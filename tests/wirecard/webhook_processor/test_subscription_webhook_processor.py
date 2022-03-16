from collections import namedtuple

from playerstars_domain import PaymentGateway

from playerstars_interactors.wirecard import (
    SubscriptionWebhookProcessor,
    WebhookProcessorAdapters)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.wirecard.webhook_processor.' \
    'subscription_webhook_processor'


Factory = namedtuple('Factory',
                     'processor, mock_adapters, mock_webhook_json, ')


@fixture(scope='class')
def processor_fixture(request):
    def factory(adapters: WebhookProcessorAdapters = MagicMock(),
                webhook_json: dict = MagicMock()):
        processor = SubscriptionWebhookProcessor(
            adapters=adapters,
            webhook_json=webhook_json)
        return Factory(processor, adapters, webhook_json)
    request.cls.factory = factory


@pytest.mark.usefixtures('processor_fixture')
class TestPlanWebhookProcessor(TestCase):
    def setUp(self):
        fac = TestPlanWebhookProcessor.factory()
        self.processor: SubscriptionWebhookProcessor = fac.processor
        self.mock_adapters = fac.mock_adapters
        self.mock_webhook_json = fac.mock_webhook_json

    def tearDown(self):
        pass

    def test_init(self):
        assert self.processor.adapters == self.mock_adapters
        assert self.processor.webhook_json == self.mock_webhook_json

    @patch.object(SubscriptionWebhookProcessor, 'is_active')
    @patch.object(SubscriptionWebhookProcessor, 'do_nothing')
    @patch.object(SubscriptionWebhookProcessor, 'is_inactive')
    def test_get_status_processor(self,
                                  is_inactive_mock,
                                  do_nothing_mock,
                                  is_active_mock):
        status_types = [
            ('ACTIVE', is_active_mock),
            ('OVERDUE', do_nothing_mock),
            ('EXPIRED', do_nothing_mock),
            ('SUSPENDED', is_inactive_mock),
            ('CANCELED', is_inactive_mock),
            ('TRIAL', do_nothing_mock)]
        for status_type in status_types:
            process_result = self.processor._get_status_processor(
                status_type[0])
            assert process_result == status_type[1]

    @patch(f'{prefix}.Plan')
    @patch(f'{prefix}.PlayerSubscription')
    @patch(f'{prefix}.Subscription')
    @patch(f'{prefix}.mount_next_invoice_as_datetime')
    @patch.object(SubscriptionWebhookProcessor, '_get_plan_from_api')
    def test_is_active(self,
                       get_plan_from_api_mock,
                       mount_next_invoice_mock,
                       subscription_mock,
                       player_subscription_mock,
                       plan_mock):
        self.processor.player = MagicMock()
        self.processor.is_active()
        self.mock_webhook_json.__getitem__().__getitem__().__getitem__.\
            assert_called_with('code')
        subscription_mock.from_json.assert_called_with(
            self.mock_webhook_json.__getitem__())
        mount_next_invoice_mock.assert_called_with(
            subscription_mock.from_json().next_invoice_date)
        get_plan_from_api_mock.assert_called_once_with(
            self.mock_webhook_json.__getitem__().__getitem__().__getitem__())
        player_subscription_mock.assert_called_with(
            expiration_date=mount_next_invoice_mock(),
            plan_name=get_plan_from_api_mock().name,
            payment_gateway=PaymentGateway.WIRECARD)
        self.processor.player.save.assert_called_once()

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.PlayerSubscription')
    @patch.object(SubscriptionWebhookProcessor, '_get_plan_from_api')
    def test_is_inactive(self,
                         get_plan_from_api_mock,
                         player_subscription_mock,
                         aware_now_mock):
        self.processor.player = MagicMock()
        self.processor.is_inactive()
        self.mock_webhook_json.__getitem__.assert_called_with('resource')
        self.mock_webhook_json.__getitem__().__getitem__().__getitem__.\
            assert_called_with('code')
        get_plan_from_api_mock.assert_called_once_with(
            self.mock_webhook_json.__getitem__().__getitem__().__getitem__())
        aware_now_mock.assert_called_once()
        player_subscription_mock.assert_called_once_with(
            expiration_date=aware_now_mock(),
            plan_name=get_plan_from_api_mock().name,
            payment_gateway=PaymentGateway.WIRECARD)
        self.processor.player.save.assert_called_once()

    @patch.object(SubscriptionWebhookProcessor, '_get_plan_from_api')
    @patch(f'{prefix}.PlayerSubscription')
    def test_do_nothing(self,
                        player_subscription_mock,
                        get_plan_from_api_mock):
        self.processor.player = MagicMock()
        self.processor.do_nothing()
        self.processor.player.save.assert_not_called()
        player_subscription_mock.assert_not_called()
        get_plan_from_api_mock.assert_not_called()

    @patch.object(SubscriptionWebhookProcessor, '_get_status_processor')
    def test_process_status(self, get_status_processor_mock):
        self.processor._process_status()
        self.mock_webhook_json.__getitem__().__getitem__.\
            assert_called_with('status')
        get_status_processor_mock.assert_called_with(
            self.mock_webhook_json.__getitem__().__getitem__())
        get_status_processor_mock().assert_called_once()

    @patch.object(SubscriptionWebhookProcessor, '_get_player')
    @patch.object(SubscriptionWebhookProcessor, '_process_status')
    @patch.object(SubscriptionWebhookProcessor, '_add_payment_log')
    def test_process_webhook(self,
                             add_payment_log_mock,
                             process_status_mock,
                             get_player_mock):
        self.processor._process_webhook()
        self.mock_webhook_json.__getitem__().__getitem__().__getitem__.\
            assert_called_with('code')
        get_player_mock.assert_called_once_with(
            self.mock_webhook_json.__getitem__().__getitem__().__getitem__())
        process_status_mock.assert_called_once()
        add_payment_log_mock.assert_called_once()

    @patch.object(SubscriptionWebhookProcessor, '_process_webhook')
    def test_run(self, process_webhook_mock):
        self.processor.run()
        process_webhook_mock.assert_called_once()
