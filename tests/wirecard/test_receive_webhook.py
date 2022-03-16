from collections import namedtuple
from playerstars_interactors.wirecard import (
    EventNotFoundException,
    InvalidEventException,
    ReceiveWebhookException,
    ReceiveWebhookInteractor,
    ReceiveWebhookResponseModel,
    WebhookProcessorAdapters)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.wirecard.receive_webhook'


def test_receive_webhook_response_model():
    response = ReceiveWebhookResponseModel()
    assert response


def test_rm__call():
    response = ReceiveWebhookResponseModel()
    assert response() == {
        'status': 'ok'}


def test_webhook_processor_adapters():
    mock_plan_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_subscription_adapter = MagicMock()

    adapters = WebhookProcessorAdapters(
        player_adapter=mock_player_adapter,
        subscription_adapter=mock_subscription_adapter,
        plan_adapter=mock_plan_adapter)

    assert adapters.plan_adapter == mock_plan_adapter
    assert adapters.player_adapter == mock_player_adapter
    assert adapters.subscription_adapter == mock_subscription_adapter


Factory = namedtuple('Factory',
                     'interactor, mock_adapters, mock_webhook_json, ')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(adapters: WebhookProcessorAdapters = MagicMock(),
                webhook_json: dict() = MagicMock()):
        interactor = ReceiveWebhookInteractor(
            webhook_json=webhook_json,
            adapters=adapters)
        return Factory(interactor, adapters, webhook_json)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestReceiveWebhookInteractor(TestCase):
    def setUp(self):
        fac = TestReceiveWebhookInteractor.factory()
        self.interactor: ReceiveWebhookInteractor = fac.interactor
        self.mock_adapters = fac.mock_adapters
        self.mock_webhook_json = fac.mock_webhook_json

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.adapters == self.mock_adapters
        assert self.interactor.webhook_json == self.mock_webhook_json

    @patch(f'{prefix}.webhook_processor_factory')
    def test_process_webhook(self, webhook_processor_mock):
        self.interactor._process_webhook('event')
        webhook_processor_mock.assert_called_with('event')
        webhook_processor_mock().assert_called_with(
            webhook_json=self.mock_webhook_json,
            adapters=self.mock_adapters)
        webhook_processor_mock()().run.assert_called_once()

    @patch(f'{prefix}.ReceiveWebhookResponseModel')
    @patch.object(ReceiveWebhookInteractor, '_process_webhook')
    def test_run(self, process_webhook_mock, response_model_mock):
        response = self.interactor.run()
        self.mock_webhook_json.__getitem__.assert_called_with('event')
        process_webhook_mock.assert_called_with(self.mock_webhook_json.__getitem__())
        response_model_mock.assert_called_once()
        assert response == response_model_mock()

    @patch(f'{prefix}.ReceiveWebhookResponseModel')
    @patch.object(ReceiveWebhookInteractor,
                  '_process_webhook',
                  side_effect=EventNotFoundException('oops'))
    def test_event_not_found_error(self,
                                   process_webhook_mock,
                                   response_model_mock):
        with pytest.raises(ReceiveWebhookException) as exc:
            self.interactor.run()
        self.mock_webhook_json.__getitem__.assert_called_with('event')
        process_webhook_mock.assert_called_with(self.mock_webhook_json.__getitem__())
        assert 'Event not found processing webhook: oops' in str(exc.value)

    @patch(f'{prefix}.ReceiveWebhookResponseModel')
    @patch.object(ReceiveWebhookInteractor,
                  '_process_webhook',
                  side_effect=InvalidEventException('oops'))
    def test_invalid_event_error(self,
                                 process_webhook_mock,
                                 response_model_mock):
        with pytest.raises(ReceiveWebhookException) as exc:
            self.interactor.run()
        self.mock_webhook_json.__getitem__.assert_called_with('event')
        process_webhook_mock.assert_called_with(
            self.mock_webhook_json.__getitem__())
        assert 'Invalid event processing webhook: oops' in str(exc.value)

    @patch(f'{prefix}.ReceiveWebhookResponseModel')
    @patch.object(ReceiveWebhookInteractor,
                  '_process_webhook',
                  side_effect=Exception('oops'))
    def test_any_error(self, process_webhook_mock, response_model_mock):
        with pytest.raises(ReceiveWebhookException) as exc:
            self.interactor.run()
        self.mock_webhook_json.__getitem__.assert_called_with('event')
        process_webhook_mock.assert_called_with(self.mock_webhook_json.__getitem__())
        assert 'Any error processing webhook: oops' in str(exc.value)
