from collections import namedtuple
from unittest import TestCase

from playerstars_adapters import PlayerAdapter
from playerstars_interactors.purchase.post_purchase_notification_by_google \
    import (PostPurchaseNotificationByGoogleException,
            PostPurchaseNotificationByGoogleInteractor,
            PostPurchaseNotificationByGoogleRequestModel,
            PostPurchaseNotificationByGoogleResponseModel)
from pytest import fixture
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.purchase.' \
         'post_purchase_notification_by_google'


def test_post_purchase_notification_by_google_request_model():
    mock_json_data = MagicMock()
    request = PostPurchaseNotificationByGoogleRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [
        ('player_id', 'player_id'),
        ('order_id', 'orderId'),
        ('product_id', 'productId'),
        ('purchase_state', 'purchaseState'),
        ('acknowledged', 'acknowledged'),
        ('auto_renewing', 'autoRenewing'),
        ('purchase_time', 'purchaseTime'),
        ('expiration_datetime', 'expirationDateTime'),
        ('purchase_token', 'purchaseToken'),
        ('package_name', 'packageName')
    ]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_post_purchase_notification_by_google_response_model():
    player_id_mock = MagicMock()
    package_name_mock = MagicMock()
    expiration_datetime_mock = MagicMock()
    response = PostPurchaseNotificationByGoogleResponseModel(
        player_id=player_id_mock,
        package_name=package_name_mock,
        expiration_datetime=expiration_datetime_mock)
    assert response.player_id == player_id_mock
    assert response.package_name == package_name_mock
    assert response.expiration_datetime == expiration_datetime_mock


@patch(f'{prefix}.datetime')
def test_post_purchase_notification_by_google_response_model__call__(
        datetime_mock):
    player_id_mock = MagicMock()
    package_name_mock = MagicMock()
    expiration_datetime_mock = MagicMock()
    response = PostPurchaseNotificationByGoogleResponseModel(
        player_id=player_id_mock,
        package_name=package_name_mock,
        expiration_datetime=expiration_datetime_mock)
    response_call = response()
    expiration_datetime_mock.isoformat.assert_called_once()
    assert response_call == {
        'player_id': player_id_mock,
        'package_name': package_name_mock,
        'expiration_datetime': expiration_datetime_mock.isoformat()}


Factory = namedtuple('Factory', 'interactor, mock_request, mock_player_adapter, ')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(request: PostPurchaseNotificationByGoogleRequestModel =
                MagicMock(),
                player_adapter: PlayerAdapter = MagicMock):
        interactor = PostPurchaseNotificationByGoogleInteractor(
            player_adapter=player_adapter,
            request=request)
        return Factory(interactor, request, player_adapter)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestPostPurchaseNotificationByGoogleInteractor(TestCase):
    def setUp(self):
        fac = TestPostPurchaseNotificationByGoogleInteractor.factory()
        self.interactor: PostPurchaseNotificationByGoogleInteractor = \
            fac.interactor
        self.mock_request = fac.mock_request
        self.mock_player_adapter = fac.mock_player_adapter

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.player_adapter == self.mock_player_adapter

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_player(self, find_entity_by_id_mock):
        player_data = self.interactor._get_player()
        find_entity_by_id_mock.assert_called_once_with(
            _id=self.mock_request.player_id,
            adapter_instance=self.mock_player_adapter,
            class_name='Player')
        assert player_data == find_entity_by_id_mock()

    @patch(f'{prefix}.datetime')
    @patch(f'{prefix}.GooglePurchase')
    def test_mount_google_purchase(self, google_purchase_mock, datetime_mock):
        google_purchase = self.interactor._mount_google_purchase()
        datetime_mock.fromisoformat.assert_called_with(
            self.mock_request.expiration_datetime)
        google_purchase_mock.assert_called_with(
            orderId=self.mock_request.order_id,
            productId=self.mock_request.product_id,
            purchaseState=self.mock_request.purchase_state,
            acknowledged=self.mock_request.acknowledged,
            autoRenewing=self.mock_request.auto_renewing,
            purchaseTime=self.mock_request.purchase_time,
            expirationDateTime=datetime_mock.fromisoformat(
                self.mock_request.expiration_datetime),
            purchaseToken=self.mock_request.purchase_token,
            packageName=self.mock_request.package_name)
        assert google_purchase == google_purchase_mock()

    def test_add_payment_log(self):
        player_mock = MagicMock()
        payment_log_mock = MagicMock()
        self.interactor.add_payment_log(player_mock, payment_log_mock)
        player_mock.add_payment_log.assert_called_once_with(payment_log_mock)
        player_mock.save.assert_called_once()

    def test_update_player_subscription(self):
        player_mock = MagicMock()
        subscription_mock = MagicMock()
        self.interactor.update_player_subscription(
            player_mock, subscription_mock)
        assert player_mock.subscription == subscription_mock
        player_mock.save.assert_called_once()

    @patch.object(PostPurchaseNotificationByGoogleInteractor, '_get_player')
    @patch.object(PostPurchaseNotificationByGoogleInteractor, '_mount_google_purchase')
    @patch.object(PostPurchaseNotificationByGoogleInteractor, 'update_player_subscription')
    @patch.object(PostPurchaseNotificationByGoogleInteractor, 'add_payment_log')
    @patch(f'{prefix}.PostPurchaseNotificationByGoogleResponseModel')
    def test_run(self, response_model_mock,
                 add_payment_log_mock,
                 update_player_subscription_mock,
                 mount_google_purchase_mock,
                 get_player_mock):
        response = self.interactor.run()
        get_player_mock.assert_called_once()
        mount_google_purchase_mock.assert_called_once()
        mount_google_purchase_mock().mount_subscription.assert_called()
        mount_google_purchase_mock().mount_payment_log.assert_called()
        update_player_subscription_mock.assert_called_with(
            player=get_player_mock(),
            subscription=mount_google_purchase_mock().mount_subscription())
        add_payment_log_mock.assert_called_with(
            player=get_player_mock(),
            payment_log=mount_google_purchase_mock().mount_payment_log())
        response_model_mock.assert_called_with(
            player_id=self.mock_request.player_id,
            package_name=mount_google_purchase_mock().packageName,
            expiration_datetime=mount_google_purchase_mock().
            expirationDateTime)
        assert response == response_model_mock()

    @patch.object(PostPurchaseNotificationByGoogleInteractor,
                  '_get_player',
                  side_effect=Exception('oops'))
    @patch.object(PostPurchaseNotificationByGoogleInteractor, '_mount_google_purchase')
    @patch.object(PostPurchaseNotificationByGoogleInteractor, 'update_player_subscription')
    @patch.object(PostPurchaseNotificationByGoogleInteractor, 'add_payment_log')
    @patch(f'{prefix}.PostPurchaseNotificationByGoogleResponseModel')
    def test_run_fails(self, response_model_mock,
                       add_payment_log_mock,
                       update_player_subscription_mock,
                       mount_google_purchase_mock,
                       get_player_mock):
        with pytest.raises(PostPurchaseNotificationByGoogleException) as exc:
            self.interactor.run()
        assert 'Error during receive payment data from Google: ' \
            'Exception: oops' in str(exc.value)
        get_player_mock.assert_called_once()
        mount_google_purchase_mock.assert_not_called()
        update_player_subscription_mock.assert_not_called()
        add_payment_log_mock.assert_not_called()
        response_model_mock.assert_not_called()
