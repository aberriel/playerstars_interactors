from .basic_webhook_processor import (
    BasicWebhookProcessor,
    WebhookProcessorAdapters)
from playerstars_domain import Subscription


class InvoiceWebhookProcessor(BasicWebhookProcessor):
    def __init__(self,
                 webhook_json: dict,
                 adapters: WebhookProcessorAdapters):
        super(InvoiceWebhookProcessor, self).__init__(
            webhook_json=webhook_json,
            adapters=adapters)

    def run(self):
        subscription_id = self.webhook_json['resource']['subscription_code']
        subscription: Subscription = self._get_subscription_from_api(
            subscription_id)
        self._log_received_webhook(subscription.customer.code)
