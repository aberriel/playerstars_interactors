from playerstars_interactors.wirecard import (
    CustomerWebhookProcessor,
    EventNotFoundException,
    InvalidEventException,
    InvoiceWebhookProcessor,
    PaymentWebhookProcessor,
    PlanWebhookProcessor,
    SubscriptionWebhookProcessor,
    webhook_processor_factory)

import pytest


prefix = 'playerstars_interactors.wirecard.webhook_processor.' \
    'webhook_processor_factory'


def test_webhook_processor_factory():
    event_map = [
        ('customer.update', CustomerWebhookProcessor),
        ('invoice.created', InvoiceWebhookProcessor),
        ('payment.status_updated', PaymentWebhookProcessor),
        ('plan.created', PlanWebhookProcessor),
        ('subscription.status_updated', SubscriptionWebhookProcessor)]
    for event in event_map:
        processor = webhook_processor_factory(
            event_name=event[0])
        assert processor == event[1]


def test_webhook_processor_factory_key_error():
    with pytest.raises(EventNotFoundException) as exc:
        webhook_processor_factory('player.created')
    assert 'player' in str(exc.value)


def test_webhook_processor_factory_any_error():
    with pytest.raises(InvalidEventException) as exc:
        webhook_processor_factory(123)
    assert "AttributeError: 'int' object has no attribute 'split'" \
           in str(exc.value)
