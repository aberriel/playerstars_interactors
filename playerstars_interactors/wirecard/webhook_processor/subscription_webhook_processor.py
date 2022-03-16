from .basic_webhook_processor import (
    BasicWebhookProcessor,
    WebhookProcessorAdapters)
from playerstars_domain import (
    PaymentGateway,
    Plan,
    Player,
    PlayerSubscription,
    Subscription)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.wirecard.wirecard_utils import \
    mount_next_invoice_as_datetime


class SubscriptionWebhookProcessor(BasicWebhookProcessor):
    def __init__(self,
                 webhook_json: dict,
                 adapters: WebhookProcessorAdapters):
        super(SubscriptionWebhookProcessor, self).__init__(
            webhook_json=webhook_json,
            adapters=adapters)

    def _get_status_processor(self, status: str):
        status_mapping = {
            'ACTIVE': self.is_active,
            'OVERDUE': self.do_nothing,
            'EXPIRED': self.do_nothing,
            'SUSPENDED': self.is_inactive,
            'CANCELED': self.is_inactive,
            'TRIAL': self.do_nothing}
        return status_mapping[status.upper()]

    def is_active(self):
        subscription_json = self.webhook_json['resource']
        plan_id = self.webhook_json['resource']['plan']['code']
        subscription: Subscription = Subscription.from_json(
            subscription_json)
        next_invoice_datetime = mount_next_invoice_as_datetime(
            subscription.next_invoice_date)
        plan: Plan = self._get_plan_from_api(plan_id)
        self.player.subscription = PlayerSubscription(
            expiration_date=next_invoice_datetime,
            plan_name=plan.name,
            payment_gateway=PaymentGateway.WIRECARD)
        self.player.save()

    def is_inactive(self):
        plan_id = self.webhook_json['resource']['plan']['code']
        plan: Plan = self._get_plan_from_api(plan_id)
        self.player.subscription = PlayerSubscription(
            expiration_date=aware_now(),
            plan_name=plan.name,
            payment_gateway=PaymentGateway.WIRECARD)
        self.player.save()

    def _process_status(self):
        status = self.webhook_json['resource']['status']
        self._get_status_processor(status)()

    def _process_webhook(self):
        player_id = self.webhook_json['resource']['customer']['code']
        self.player: Player = self._get_player(player_id)
        self._process_status()
        self._add_payment_log()

    def do_nothing(self):
        pass

    def run(self):
        self._process_webhook()
