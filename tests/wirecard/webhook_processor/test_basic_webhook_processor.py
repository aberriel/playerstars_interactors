from collections import namedtuple
from playerstars_domain import PaymentGateway
from playerstars_interactors.wirecard import (
    BasicWebhookProcessor,
    GetPlanException,
    UnknowSubscriptionException,
    WebhookProcessorAdapters)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.wirecard.webhook_processor.' \
         'basic_webhook_processor'


def test_webhook_processor_adapters():
    mock_player_adapter = MagicMock()
    mock_plan_adapter = MagicMock()
    mock_subscription_adapter = MagicMock()

    adapter = WebhookProcessorAdapters(
        plan_adapter=mock_plan_adapter,
        player_adapter=mock_player_adapter,
        subscription_adapter=mock_subscription_adapter)

    assert adapter.plan_adapter == mock_plan_adapter
    assert adapter.player_adapter == mock_player_adapter
    assert adapter.subscription_adapter == mock_subscription_adapter


Factory = namedtuple('Factory',
                     'processor, mock_adapters, mock_webhook_json, ')


@fixture(scope='class')
def processor_fixture(request):
    def factory(adapters: WebhookProcessorAdapters = MagicMock(),
                webhook_json: dict = MagicMock()):
        processor = BasicWebhookProcessor(
            adapters=adapters,
            webhook_json=webhook_json)
        return Factory(processor, adapters, webhook_json)
    request.cls.factory = factory


@pytest.mark.usefixtures('processor_fixture')
class TestBasicWebhookProcessor(TestCase):
    def setUp(self):
        fac = TestBasicWebhookProcessor.factory()
        self.processor: BasicWebhookProcessor = fac.processor
        self.mock_adapters = fac.mock_adapters
        self.mock_webhook_json = fac.mock_webhook_json

    def tearDown(self):
        pass

    def test_init(self):
        assert self.processor.adapters == self.mock_adapters
        assert self.processor.webhook_json == self.mock_webhook_json

    def test_get_subscription_from_api(self):
        subscription = self.processor._get_subscription_from_api('123')
        self.mock_adapters.subscription_adapter.\
            get_by_id.assert_called_once_with('123')
        assert subscription == self.mock_adapters.\
            subscription_adapter.get_by_id()

    def test_get_subscription_from_api_fails(self):
        self.mock_adapters.subscription_adapter.get_by_id = \
            MagicMock(return_value=None)
        with pytest.raises(UnknowSubscriptionException) as exc:
            self.processor._get_subscription_from_api('123')
        self.mock_adapters.subscription_adapter.\
            get_by_id.assert_called_once_with('123')
        assert 'Subscription 123 not found' in str(exc.value)

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_player(self, find_entity_mock):
        player = self.processor._get_player('123')
        find_entity_mock.assert_called_once_with(
            _id='123',
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        assert player == find_entity_mock()

    def test_get_plan_from_api(self):
        plan = self.processor._get_plan_from_api('123')
        self.mock_adapters.plan_adapter.\
            get_by_id.assert_called_once_with('123')
        assert plan == self.mock_adapters.plan_adapter.get_by_id()

    def test_get_plan_from_api_fails(self):
        self.mock_adapters.plan_adapter.get_by_id = \
            MagicMock(return_value=None)
        with pytest.raises(GetPlanException) as exc:
            self.processor._get_plan_from_api('123')
        self.mock_adapters.plan_adapter.\
            get_by_id.assert_called_once_with('123')
        assert 'Plan 123 does not exist' in str(exc.value)

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.PaymentLog')
    def test_add_payment_log(self, payment_log_mock, aware_now_mock):
        self.processor.player = MagicMock()
        self.processor._add_payment_log()
        payment_log_mock.assert_called_with(
            transaction_date=aware_now_mock(),
            payment_gateway=PaymentGateway.WIRECARD,
            raw_sent_data=None,
            raw_received_data=str(self.mock_webhook_json))
        self.processor.player.save.assert_called_once()

    @patch.object(BasicWebhookProcessor, '_get_player')
    @patch.object(BasicWebhookProcessor, '_add_payment_log')
    def test_log_received_webhook(self,
                                  add_payment_log_mock,
                                  get_player_mock):
        self.processor._log_received_webhook('123')
        get_player_mock.assert_called_once_with('123')
        add_payment_log_mock.assert_called_once()
        assert self.processor.player == get_player_mock()

    @patch.object(BasicWebhookProcessor, '_get_subscription_from_api')
    @patch.object(BasicWebhookProcessor, '_get_player')
    @patch.object(BasicWebhookProcessor, '_get_plan_from_api')
    @patch.object(BasicWebhookProcessor, '_add_payment_log')
    @patch.object(BasicWebhookProcessor, '_log_received_webhook')
    def test_run(self, log_received_webhook_mock,
                 add_payment_log_mock,
                 get_plan_from_api_mock,
                 get_player_mock,
                 get_subscription_from_api_mock):
        self.processor.run()
        log_received_webhook_mock.assert_not_called()
        add_payment_log_mock.assert_not_called()
        get_plan_from_api_mock.assert_not_called()
        get_player_mock.assert_not_called()
        get_subscription_from_api_mock.assert_not_called()
