from .basic_webhook_processor import (
    BasicWebhookProcessor,
    WebhookProcessorAdapters)


class CustomerWebhookProcessor(BasicWebhookProcessor):
    def __init__(self,
                 webhook_json: dict,
                 adapters: WebhookProcessorAdapters):
        super(CustomerWebhookProcessor, self).__init__(
            webhook_json=webhook_json,
            adapters=adapters)

    def run(self):
        player_id = self.webhook_json['resource']['code']
        self._log_received_webhook(player_id)
