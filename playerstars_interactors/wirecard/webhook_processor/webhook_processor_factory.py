from playerstars_interactors.wirecard.webhook_processor import (
    CustomerWebhookProcessor,
    InvoiceWebhookProcessor,
    PaymentWebhookProcessor,
    PlanWebhookProcessor,
    SubscriptionWebhookProcessor)


class EventNotFoundException(BaseException):
    pass


class InvalidEventException(BaseException):
    pass


def webhook_processor_factory(event_name):
    map_processors = {
        'customer': CustomerWebhookProcessor,
        'invoice': InvoiceWebhookProcessor,
        'payment': PaymentWebhookProcessor,
        'plan': PlanWebhookProcessor,
        'subscription': SubscriptionWebhookProcessor}
    try:
        event_name_part = event_name.split('.')[0]
        processor = map_processors[event_name_part]
        return processor
    except KeyError as e:
        raise EventNotFoundException(e)
    except Exception as e:
        raise InvalidEventException(f'{e.__class__.__name__}: {e}')
