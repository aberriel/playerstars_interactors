from collections import namedtuple
from playerstars_adapters import PlayerAdapter
from playerstars_interactors.notification.post_player_sns_endpoint import (
    PostPlayerSnsEndpointException,
    PostPlayerSnsEndpointInteractor,
    PostPlayerSnsEndpointRequestModel,
    PostPlayerSnsEndpointResponseModel)
from pytest import fixture, raises
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.notification.post_player_sns_endpoint'


def test_request_model():
    mock_json_data = MagicMock()
    request = PostPlayerSnsEndpointRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('player_id', 'player_id'), ('token', 'token')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_response_model():
    mock_endpoint_arn = MagicMock()
    response_model = PostPlayerSnsEndpointResponseModel(mock_endpoint_arn)
    assert response_model.endpoint_arn == mock_endpoint_arn


def test_response_model__call():
    mock_endpoint_arn = MagicMock()
    response_model = PostPlayerSnsEndpointResponseModel(mock_endpoint_arn)
    call_response = response_model()
    assert call_response == mock_endpoint_arn


Factory = namedtuple('Factory', 'interactor, mock_request, '
                                'mock_player_adapter, mock_platform_arn, '
                                'mock_aws_region')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(request: PostPlayerSnsEndpointRequestModel = MagicMock(),
                player_adapter: PlayerAdapter = MagicMock(),
                platform_arn: str = MagicMock(),
                aws_region: str = MagicMock()):
        interactor = PostPlayerSnsEndpointInteractor(
            request=request,
            player_adapter=player_adapter,
            platform_arn=platform_arn,
            aws_region=aws_region)
        return Factory(interactor, request,
                       player_adapter, platform_arn,
                       aws_region)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestPostPlayerSnsEndpoint(TestCase):
    def setUp(self):
        fac = TestPostPlayerSnsEndpoint.factory()
        self.interactor: PostPlayerSnsEndpointInteractor = fac.interactor
        self.mock_request = fac.mock_request
        self.mock_player_adapter = fac.mock_player_adapter
        self.mock_platform_arn = fac.mock_platform_arn
        self.mock_aws_region = fac.mock_aws_region

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.player_adapter == self.mock_player_adapter
        assert self.interactor.platform_arn == self.mock_platform_arn
        assert self.interactor.aws_region == self.mock_aws_region

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_player(self, mock_find_entity):
        mock_player_id = MagicMock()
        player_data = self.interactor.get_player(mock_player_id)
        mock_find_entity.assert_called_with(
            _id=mock_player_id,
            adapter_instance=self.mock_player_adapter,
            class_name='Player')
        assert player_data == mock_find_entity()

    @patch(f'{prefix}.boto3')
    def test_get_endpoint_player_data_has_endpoint(self, mock_boto):
        mock_player_data = MagicMock()
        endpoint = self.interactor.get_endpoint(mock_player_data)

        mock_boto.client.assert_called_with('sns')
        mock_boto.client().get_endpoint_attributes.assert_called_with(
            EndpointArn=mock_player_data.push_notification_data.endpoint_arn)
        assert endpoint == mock_boto.client().get_endpoint_attributes()

    @patch(f'{prefix}.boto3')
    def test_get_endpoint_player_data_has_not_endpoint(self, mock_boto):
        mock_player_data = MagicMock()
        mock_player_data.push_notification_data = None
        endpoint = self.interactor.get_endpoint(mock_player_data)

        mock_boto.client.assert_not_called()
        assert endpoint is None

    @patch(f'{prefix}.boto3')
    def test_get_endpoint_error(self, mock_boto):
        mock_player_data = MagicMock()
        mock_boto.client().get_endpoint_attributes = \
            MagicMock(side_effect=Exception('oops'))
        endpoint = self.interactor.get_endpoint(mock_player_data)
        assert endpoint is None
        mock_boto.client.assert_called_with('sns')

    @patch(f'{prefix}.boto3')
    def test_create_endpoint(self, mock_boto):
        endpoint_arn = self.interactor.create_endpoint()
        mock_boto.client.assert_called_with('sns')
        mock_boto.client().create_platform_endpoint.assert_called_with(
            PlatformApplicationArn=self.mock_platform_arn,
            Token=self.mock_request.token)
        mock_boto.client().create_platform_endpoint().\
            __getitem__.assert_called_with('EndpointArn')
        assert endpoint_arn == mock_boto.client().\
            create_platform_endpoint().__getitem__()

    @patch(f'{prefix}.boto3')
    def test_update_endpoint(self, mock_boto):
        mock_endpoint_arn = MagicMock()
        self.interactor.update_endpoint(mock_endpoint_arn)

        mock_boto.client.assert_called_with('sns')
        mock_boto.client().set_endpoint_attributes.assert_called_with(
            EndpointArn=mock_endpoint_arn,
            Attributes={
                'Token': self.mock_request.token})

    @patch(f'{prefix}.PushNotificationData')
    def test_update_player_sns_endpoint(self, mock_push_notification_data):
        mock_endpoint_arn = MagicMock()
        mock_player_data = MagicMock()
        self.interactor.update_player_sns_endpoint(
            endpoint_arn=mock_endpoint_arn,
            player_data=mock_player_data)
        mock_push_notification_data.assert_called_with(
            endpoint_arn=mock_endpoint_arn,
            device_token=self.mock_request.token)
        mock_player_data.save.assert_called()

    @patch.object(PostPlayerSnsEndpointInteractor, 'get_player')
    @patch.object(PostPlayerSnsEndpointInteractor,
                  'get_endpoint',
                  return_value=None)
    @patch.object(PostPlayerSnsEndpointInteractor, 'create_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor, 'update_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor,
                  'update_player_sns_endpoint')
    @patch(f'{prefix}.PostPlayerSnsEndpointResponseModel')
    def test_run_not_current_endpoint(self, mock_response_model,
                                      mock_update_player_sns_endpoint,
                                      mock_update_endpoint,
                                      mock_create_endpoint,
                                      mock_get_endpoint,
                                      mock_get_player):
        response = self.interactor.run()
        mock_get_player.assert_called_with(self.mock_request.player_id)
        mock_get_endpoint.assert_called_with(mock_get_player())
        mock_create_endpoint.assert_called()
        mock_update_endpoint.assert_not_called()
        mock_update_player_sns_endpoint.assert_called_with(
            endpoint_arn=mock_create_endpoint(),
            player_data=mock_get_player())
        mock_response_model.assert_called_with(mock_create_endpoint())
        assert response == mock_response_model()

    @patch.object(PostPlayerSnsEndpointInteractor, 'get_player')
    @patch.object(PostPlayerSnsEndpointInteractor, 'get_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor, 'create_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor, 'update_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor,
                  'update_player_sns_endpoint')
    @patch(f'{prefix}.PostPlayerSnsEndpointResponseModel')
    def test_run_has_current_endpoint(self, mock_response_model,
                                      mock_update_sns_endpoint,
                                      mock_update_endpoint,
                                      mock_create_endpoint,
                                      mock_get_endpoint,
                                      mock_get_player):
        response = self.interactor.run()
        mock_get_player.assert_called_with(self.mock_request.player_id)
        mock_get_endpoint.assert_called_with(mock_get_player())
        mock_create_endpoint.assert_not_called()
        mock_update_endpoint.assert_called_with(
            mock_get_player().push_notification_data.endpoint_arn)
        mock_update_sns_endpoint.assert_called_with(
            endpoint_arn=mock_get_player().
            push_notification_data.endpoint_arn,
            player_data=mock_get_player())
        mock_response_model.assert_called_with(
            mock_get_player().push_notification_data.endpoint_arn)
        assert response == mock_response_model()

    @patch.object(PostPlayerSnsEndpointInteractor,
                  'get_player',
                  side_effect=Exception('oops'))
    @patch.object(PostPlayerSnsEndpointInteractor, 'get_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor, 'create_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor, 'update_endpoint')
    @patch.object(PostPlayerSnsEndpointInteractor,
                  'update_player_sns_endpoint')
    @patch(f'{prefix}.PostPlayerSnsEndpointResponseModel')
    def test_run_error(self, mock_response_model,
                       mock_update_player_sns_endpoint,
                       mock_update_endpoint,
                       mock_create_endpoint,
                       mock_get_endpoint,
                       mock_get_player):
        with raises(PostPlayerSnsEndpointException) as exc:
            self.interactor.run()
        mock_get_player.assert_called_with(self.mock_request.player_id)
        assert 'Error during persist SNS endpoint: Exception: oops' \
            in str(exc.value)
        mock_get_endpoint.assert_not_called()
        mock_create_endpoint.assert_not_called()
        mock_update_endpoint.assert_not_called()
        mock_update_player_sns_endpoint.assert_not_called()
        mock_response_model.assert_not_called()
