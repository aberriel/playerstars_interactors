from playerstars_interactors.wirecard.webhook_processor import \
    WebhookProcessorAdapters
from playerstars_interactors.wirecard.webhook_processor. \
    webhook_processor_factory import webhook_processor_factory, \
    EventNotFoundException, InvalidEventException

import logging


class ReceiveWebhookException(BaseException):
    pass


class ReceiveWebhookResponseModel:
    def __call__(self):
        return {
            'status': 'ok'}


class ReceiveWebhookInteractor:
    def __init__(self,
                 webhook_json: dict,
                 adapters: WebhookProcessorAdapters):
        self.webhook_json = webhook_json
        self.adapters = adapters
        self.logger = logging.getLogger(__name__)

    def _process_webhook(self, event_name):
        processor_cls = webhook_processor_factory(event_name)
        processor = processor_cls(
            webhook_json=self.webhook_json,
            adapters=self.adapters)
        processor.run()

    def run(self):
        try:
            event_name = self.webhook_json['event']
            self._process_webhook(event_name)
            response = ReceiveWebhookResponseModel()
            return response
        except EventNotFoundException as e:
            msg = f'Event not found processing webhook: {e}'
            self.logger.error(msg)
            raise ReceiveWebhookException(msg)
        except InvalidEventException as e:
            msg = f'Invalid event processing webhook: {e}'
            self.logger.error(msg)
            raise ReceiveWebhookException(msg)
        except BaseException as e:
            msg = f'Any error processing webhook: {e}'
            self.logger.error(msg)
            raise ReceiveWebhookException(msg)
