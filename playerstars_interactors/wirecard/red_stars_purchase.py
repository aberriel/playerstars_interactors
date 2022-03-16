from .wirecard_utils import (
    mount_next_invoice_as_datetime,
    process_api_response_for_errors)
from datetime import date
from playerstars_adapters import PlayerAdapter
from playerstars_domain import (
    PaymentGateway,
    PaymentLog,
    Player,
    PlayerSubscription)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_domain.wirecard import (
    Address,
    BillingInfo,
    PaymentMethod,
    Plan,
    Subscriber,
    Subscription,
    SubscriptionStatus)
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_wirecard import (
    CreditCardAdapter,
    PlanAdapter,
    SubscriberAdapter,
    SubscriptionAdapter)
from uuid import uuid4

import logging


class RedStarsPurchaseException(BaseException):
    pass


class RedStarsPurchaseRequestModel:
    def __init__(self, json_data):
        self.plan = json_data['plan']
        self.fullname = json_data['fullname']
        self.cpf = json_data['cpf']
        self.billing_info = json_data['billing_info']
        self.address = json_data['address']
        self.customer_code = json_data['code']
        self.email = json_data['email']
        self.birthdate = json_data['birthdate']
        self.phone_number = json_data['phone_number']
        self.phone_area_code = json_data['phone_area_code']


class RedStarsPurchaseResponseModel:
    def __init__(self, subscription: Subscription):
        self.subscription = subscription

    def _prepare_subscription_json(self):
        next_invoice = mount_next_invoice_as_datetime(
            self.subscription.next_invoice_date)
        return {
            'subscription_code': self.subscription.code,
            'wirecard_id': self.subscription.id,
            'plan_code': self.subscription.plan.code,
            'amount': self.subscription.amount,
            'subscription_status': self.subscription.status.value,
            'next_invoice': next_invoice.isoformat()}

    def __call__(self):
        return self._prepare_subscription_json()


class RedStarPurchaseInteractorAdapters:
    def __init__(self,
                 plan_adapter: PlanAdapter,
                 credit_card_adapter: CreditCardAdapter,
                 subscriber_adapter: SubscriberAdapter,
                 subscription_adapter: SubscriptionAdapter,
                 player_adapter: PlayerAdapter):
        self.subscriber_adapter = subscriber_adapter
        self.credit_card_adapter = credit_card_adapter
        self.plan_adapter = plan_adapter
        self.subscription_adapter = subscription_adapter
        self.player_adapter = player_adapter


class CreateCustomerException(BaseException):
    pass


class UpdateCreditCardException(BaseException):
    pass


class UpdateCustomerException(BaseException):
    pass


class GetPlanException(BaseException):
    pass


class CreateSubscriptionException(BaseException):
    pass


class RedStarsPurchaseInteractor:
    player: Player = None
    plan: Plan = None

    def __init__(self,
                 adapters: RedStarPurchaseInteractorAdapters,
                 request: RedStarsPurchaseRequestModel):
        self.adapters = adapters
        self.request = request
        self.logger = logging.getLogger(__name__)
        self.customer = self._mount_customer_object()

    def _get_birthdate_components(self):
        birthdate = date.fromisoformat(self.request.birthdate)
        return {
            'birthdate_day': birthdate.day,
            'birthdate_month': str(birthdate.month),
            'birthdate_year': birthdate.year}

    def _mount_customer_object(self):
        address = Address.from_json(self.request.address)
        billing_info = BillingInfo.from_json(self.request.billing_info)
        birthdate = self._get_birthdate_components()
        customer = Subscriber(
            code=self.request.customer_code,
            email=self.request.email,
            fullname=self.request.fullname,
            cpf=self.request.cpf,
            phone_area_code=self.request.phone_area_code,
            phone_number=self.request.phone_number,
            address=address,
            billing_info=billing_info,
            birthdate_day=birthdate['birthdate_day'],
            birthdate_month=birthdate['birthdate_month'],
            birthdate_year=birthdate['birthdate_year'])
        return customer

    def mount_plan_object(self):
        plan = Plan(code=self.plan.code, amount=self.plan.amount)
        return plan

    @staticmethod
    def _make_subscription_code():
        return str(uuid4())

    def mount_subscription_object(self):
        subscription = Subscription(
            code=self._make_subscription_code(),
            amount=self.request.plan['amount'],
            customer=self.customer,
            plan=self.mount_plan_object(),
            payment_method=PaymentMethod.CREDIT_CARD)
        return subscription

    def get_customer_from_api(self):
        customer_code = self.request.customer_code
        customer_from_api = self.adapters.subscriber_adapter.get_by_id(
            customer_code)
        return customer_from_api

    def create_customer(self):
        create_result = self.adapters.subscriber_adapter.save(self.customer)
        self.add_payment_log(create_result)
        if create_result['status_code'] != 201:
            raise CreateCustomerException(process_api_response_for_errors(
                create_result))
        return create_result['content']

    def update_customer_and_creditcard(self):
        self._update_customer()
        self._update_creditcard()

    def _update_creditcard(self):
        credit_card_update = self.adapters.credit_card_adapter.save(
            self.customer.billing_info)
        self.add_payment_log(credit_card_update)
        if credit_card_update['status_code'] != 200:
            error_msg = process_api_response_for_errors(credit_card_update)
            raise UpdateCreditCardException(error_msg)

    def _update_customer(self):
        update_result = self.adapters.subscriber_adapter.save(
            self.customer,
            exec_update=True)
        self.add_payment_log(update_result)
        if update_result['status_code'] != 200:
            raise UpdateCustomerException(process_api_response_for_errors(
                update_result))

    def create_or_update_customer(self):
        customer_api = self.get_customer_from_api()
        if customer_api is None:
            self.create_customer()
        else:
            self.update_customer_and_creditcard()

    def get_plan(self):
        plan_code = self.request.plan['code']
        plan = self.adapters.plan_adapter.get_by_id(plan_code)
        if not plan:
            raise GetPlanException(f'Plan {plan_code} does not exist')
        return plan

    def prepare_subscription_to_create(self):
        subscription = self.mount_subscription_object()
        subscription.amount = self.plan.amount
        return subscription

    def create_subscription(self, subscription):
        create_result = self.adapters.subscription_adapter.save(subscription)
        self.add_payment_log(create_result)
        if create_result['status_code'] != 201:
            raise CreateSubscriptionException(
                process_api_response_for_errors(create_result))
        return create_result['content']

    def get_player(self):
        return find_entity_by_id(
            _id=self.request.customer_code,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

    def update_player_subscription(self, created_subscription: Subscription):
        next_invoice = mount_next_invoice_as_datetime(
            created_subscription.next_invoice_date)
        player_subscription = PlayerSubscription(
            expiration_date=next_invoice,
            payment_gateway=PaymentGateway.WIRECARD,
            plan_name=created_subscription.plan.name)
        self.player.subscription = player_subscription
        self.player.save()

    def add_payment_log(self, api_response):
        payment_log = PaymentLog(
            transaction_date=aware_now(),
            payment_gateway=PaymentGateway.WIRECARD,
            raw_sent_data=str(api_response['raw_sent_data']),
            raw_received_data=str(api_response['raw_received_data']))
        self.player.add_payment_log(payment_log)
        self.player.save()

    @staticmethod
    def _is_active_subscription(subscription):
        return subscription.status == SubscriptionStatus.ACTIVE

    def run(self):
        try:
            self.player = self.get_player()
            self.plan = self.get_plan()
            self.create_or_update_customer()
            subscription = self.prepare_subscription_to_create()
            subscription_created = self.create_subscription(subscription)

            if self._is_active_subscription(subscription_created):
                self.update_player_subscription(subscription_created)

            response = RedStarsPurchaseResponseModel(subscription_created)
            return response
        except BaseException as exc:
            msg = f'Error during red stars ' \
                  f'payment: {exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise RedStarsPurchaseException(msg)
