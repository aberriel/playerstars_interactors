from collections import namedtuple
from playerstars_interactors.wirecard import (
    PaymentWebhookProcessor,
    WebhookProcessorAdapters)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


Factory = namedtuple('Factory',
                     'processor, mock_adapters, mock_webhook_json, ')


@fixture(scope='class')
def processor_fixture(request):
    def factory(adapters: WebhookProcessorAdapters = MagicMock(),
                webhook_json: dict = MagicMock()):
        processor = PaymentWebhookProcessor(
            adapters=adapters,
            webhook_json=webhook_json)
        return Factory(processor, adapters, webhook_json)
    request.cls.factory = factory


@pytest.mark.usefixtures('processor_fixture')
class TestPaymentWebhookProcessor(TestCase):
    def setUp(self):
        fac = TestPaymentWebhookProcessor.factory()
        self.processor: PaymentWebhookProcessor = fac.processor
        self.mock_adapters = fac.mock_adapters
        self.mock_webhook_json = fac.mock_webhook_json

    def tearDown(self):
        pass

    def test_init(self):
        assert self.processor.adapters == self.mock_adapters
        assert self.processor.webhook_json == self.mock_webhook_json

    @patch.object(PaymentWebhookProcessor, '_get_subscription_from_api')
    @patch.object(PaymentWebhookProcessor, '_get_player')
    @patch.object(PaymentWebhookProcessor, '_get_plan_from_api')
    @patch.object(PaymentWebhookProcessor, '_add_payment_log')
    @patch.object(PaymentWebhookProcessor, '_log_received_webhook')
    def test_run(self, log_received_webhook_mock,
                 add_payment_log_mock,
                 get_plan_from_api_mock,
                 get_player_mock,
                 get_subscription_from_api_mock):
        self.processor.run()
        self.mock_webhook_json.__getitem__().__getitem__.assert_called_once()
        get_subscription_from_api_mock.assert_called_once_with(
            self.mock_webhook_json.__getitem__().__getitem__())
        log_received_webhook_mock.assert_called_once_with(
            get_subscription_from_api_mock().customer.code)
        get_plan_from_api_mock.assert_not_called()
        get_player_mock.assert_not_called()
        add_payment_log_mock.assert_not_called()
