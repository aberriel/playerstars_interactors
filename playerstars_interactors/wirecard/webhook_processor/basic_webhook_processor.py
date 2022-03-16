from playerstars_adapters import PlayerAdapter
from playerstars_domain import PaymentLog, PaymentGateway, Player
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.wirecard.red_stars_purchase import \
    GetPlanException
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_wirecard import SubscriptionAdapter, PlanAdapter


class UnknowSubscriptionException(BaseException):
    pass


class WebhookProcessorAdapters:
    def __init__(self,
                 player_adapter: PlayerAdapter,
                 subscription_adapter: SubscriptionAdapter,
                 plan_adapter: PlanAdapter):
        self.player_adapter = player_adapter
        self.subscription_adapter = subscription_adapter
        self.plan_adapter = plan_adapter


class BasicWebhookProcessor:
    player = None

    def __init__(self,
                 webhook_json: dict,
                 adapters: WebhookProcessorAdapters):
        self.webhook_json = webhook_json
        self.adapters = adapters

    def _get_subscription_from_api(self, subscription_code):
        subscription = self.adapters.subscription_adapter.get_by_id(
            subscription_code)
        if not subscription:
            raise UnknowSubscriptionException(
                f'Subscription {subscription_code} not found')
        return subscription

    def _get_player(self, player_id):
        return find_entity_by_id(
            _id=player_id,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

    def _get_plan_from_api(self, plan_code):
        plan = self.adapters.plan_adapter.get_by_id(plan_code)
        if not plan:
            raise GetPlanException(f'Plan {plan_code} does not exist')
        return plan

    def _add_payment_log(self):
        payment_log = PaymentLog(
            transaction_date=aware_now(),
            payment_gateway=PaymentGateway.WIRECARD,
            raw_sent_data=None,
            raw_received_data=str(self.webhook_json))
        self.player.add_payment_log(payment_log)
        self.player.save()

    def _log_received_webhook(self, player_id):
        self.player: Player = self._get_player(player_id)
        self._add_payment_log()

    def run(self):
        pass
