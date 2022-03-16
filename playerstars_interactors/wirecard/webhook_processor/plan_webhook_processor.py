from .basic_webhook_processor import (
    BasicWebhookProcessor,
    WebhookProcessorAdapters)


class PlanWebhookProcessor(BasicWebhookProcessor):
    def __init__(self, webhook_json: dict,
                 adapters: WebhookProcessorAdapters):
        super(PlanWebhookProcessor, self).__init__(
            webhook_json=webhook_json,
            adapters=adapters)

    def run(self):
        pass
