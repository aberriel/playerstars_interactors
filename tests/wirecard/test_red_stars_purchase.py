from collections import namedtuple
from playerstars_domain import (
    PaymentGateway,
    PaymentMethod,
    Subscription,
    SubscriptionStatus)
from playerstars_interactors import (
    GetPlanException,
    RedStarsPurchaseException,
    RedStarsPurchaseRequestModel,
    RedStarsPurchaseResponseModel)
from playerstars_interactors.wirecard.red_stars_purchase import (
    RedStarPurchaseInteractorAdapters,
    RedStarsPurchaseInteractor,
    CreateCustomerException,
    CreateSubscriptionException,
    UpdateCreditCardException,
    UpdateCustomerException)
from unittest import TestCase
from unittest.mock import MagicMock, patch
from pytest import fixture

import pytest

prefix = 'playerstars_interactors.wirecard.red_stars_purchase'


def test_redstarpurchase_requestmodel():
    mock_json_data = MagicMock()
    request = RedStarsPurchaseRequestModel(mock_json_data)

    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [
        ('plan', 'plan'),
        ('fullname', 'fullname'),
        ('cpf', 'cpf'),
        ('billing_info', 'billing_info'),
        ('address', 'address'),
        ('customer_code', 'code'),
        ('email', 'email'),
        ('birthdate', 'birthdate'),
        ('phone_number', 'phone_number'),
        ('phone_area_code', 'phone_area_code')
    ]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]

    assert len(calls) == len(fields)


def test_red_stars_purchase_response_model():
    mock_subscription = MagicMock()
    response = RedStarsPurchaseResponseModel(mock_subscription)

    assert response.subscription == mock_subscription


@patch(f'{prefix}.mount_next_invoice_as_datetime')
def test_rm__prepare_subscription_json(mock_mniad):
    mock_subscription = MagicMock()
    response = RedStarsPurchaseResponseModel(mock_subscription)

    result = response._prepare_subscription_json()

    mock_mniad.assert_called_with(response.subscription.next_invoice_date)

    expected = {
        'subscription_code': response.subscription.code,
        'wirecard_id': response.subscription.id,
        'plan_code': response.subscription.plan.code,
        'amount': response.subscription.amount,
        'subscription_status': response.subscription.status.value,
        'next_invoice': mock_mniad().isoformat()
    }

    assert result == expected


@patch.object(RedStarsPurchaseResponseModel, '_prepare_subscription_json')
def test_rm__call(mock_prepare_subscription):
    mock_subscription = MagicMock()
    response = RedStarsPurchaseResponseModel(mock_subscription)
    assert response() == mock_prepare_subscription()


def test_red_star_pruchase_interactor_adapters():
    mock_plan_adapter = MagicMock()
    mock_credit_card_adapter = MagicMock()
    mock_subscriber_adapter = MagicMock()
    mock_subscription_adapter = MagicMock()
    mock_player_adapter = MagicMock()

    adapter = RedStarPurchaseInteractorAdapters(
        plan_adapter=mock_plan_adapter,
        credit_card_adapter=mock_credit_card_adapter,
        subscriber_adapter=mock_subscriber_adapter,
        subscription_adapter=mock_subscription_adapter,
        player_adapter=mock_player_adapter)

    assert adapter.plan_adapter == mock_plan_adapter
    assert adapter.credit_card_adapter == mock_credit_card_adapter
    assert adapter.subscriber_adapter == mock_subscriber_adapter
    assert adapter.subscription_adapter == mock_subscription_adapter
    assert adapter.player_adapter == mock_player_adapter


Factory = namedtuple('Factory', 'interactor, mock_adapters, mock_request, '
                                'mock_mco')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(adapters: RedStarPurchaseInteractorAdapters = MagicMock(),
                request: RedStarsPurchaseRequestModel = MagicMock()):
        with patch.object(RedStarsPurchaseInteractor,
                          '_mount_customer_object') as mock_mco:
            interactor = RedStarsPurchaseInteractor(adapters, request)
        return Factory(interactor, adapters, request, mock_mco)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestRedStarsPurchaseInteractor(TestCase):
    def setUp(self):
        fac = TestRedStarsPurchaseInteractor.factory()
        self.interactor: RedStarsPurchaseInteractor = fac.interactor
        self.mock_adapters = fac.mock_adapters
        self.mock_request = fac.mock_request
        self.mock_mco = fac.mock_mco

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.adapters == self.mock_adapters
        assert self.interactor.customer == self.mock_mco()

    @patch(f'{prefix}.date')
    def test__get_birthdate_components(self, date_mock):
        birthdate = self.interactor._get_birthdate_components()
        date_mock.fromisoformat.assert_called_once_with(
            self.mock_request.birthdate)
        assert birthdate == {
            'birthdate_day': date_mock.fromisoformat().day,
            'birthdate_month': str(date_mock.fromisoformat().month),
            'birthdate_year': date_mock.fromisoformat().year}

    @patch(f'{prefix}.Address')
    @patch(f'{prefix}.BillingInfo')
    @patch(f'{prefix}.Subscriber')
    @patch.object(RedStarsPurchaseInteractor,
                  '_get_birthdate_components')
    def test__mount_customer_object(self,
                                    get_birthdate_components_mock,
                                    mock_subscriber,
                                    mock_billing_info,
                                    mock_address):
        result = self.interactor._mount_customer_object()
        mock_address.from_json.assert_called_with(self.mock_request.address)
        mock_billing_info.from_json.assert_called_with(
            self.mock_request.billing_info)
        mock_subscriber.assert_called_with(
            code=self.mock_request.customer_code,
            email=self.mock_request.email,
            fullname=self.mock_request.fullname,
            cpf=self.mock_request.cpf,
            phone_area_code=self.mock_request.phone_area_code,
            phone_number=self.mock_request.phone_number,
            address=mock_address.from_json(),
            billing_info=mock_billing_info.from_json(),
            birthdate_day=get_birthdate_components_mock()
            .__getitem__('birthdate_day'),
            birthdate_month=get_birthdate_components_mock()
            .__getitem__('birthdate_month'),
            birthdate_year=get_birthdate_components_mock()
            .__getitem__('birthdate_year'))

        assert result == mock_subscriber()

    @patch(f'{prefix}.Plan')
    def test_mount_plan_object(self, mock_plan):
        self.interactor.plan = MagicMock()
        result = self.interactor.mount_plan_object()

        mock_plan.assert_called_with(
            code=self.interactor.plan.code,
            amount=self.interactor.plan.amount)

        assert result == mock_plan()

    @patch(f'{prefix}.Subscription')
    @patch.object(RedStarsPurchaseInteractor, '_make_subscription_code')
    @patch.object(RedStarsPurchaseInteractor, 'mount_plan_object')
    def test_mount_subscription_object(self,
                                       mock_mount_plan_object,
                                       mock_make_subs_code,
                                       mock_subscription):
        result = self.interactor.mount_subscription_object()

        self.mock_request.plan.__getitem__.assert_called_with('amount')

        mock_subscription.assert_called_with(
            code=mock_make_subs_code(),
            amount=self.mock_request.plan.__getitem__(),
            customer=self.interactor.customer,
            plan=mock_mount_plan_object(),
            payment_method=PaymentMethod.CREDIT_CARD)

        assert result == mock_subscription()

    @patch(f'{prefix}.uuid4')
    def test_make_subscription_code(self, mock_uuid):
        subscription_code = self.interactor._make_subscription_code()
        mock_uuid.assert_called_once()
        assert subscription_code == str(mock_uuid())

    def test_get_customer_from_api(self):
        customer = self.interactor.get_customer_from_api()
        self.mock_adapters.subscriber_adapter.\
            get_by_id.assert_called_with(self.mock_request.customer_code)
        assert customer == self.mock_adapters.subscriber_adapter.get_by_id()

    def test_get_plan(self):
        plan = self.interactor.get_plan()
        self.mock_request.plan.__getitem__.assert_called_with('code')
        self.mock_adapters.plan_adapter.get_by_id.assert_called_once_with(
            self.mock_request.plan.__getitem__())
        assert plan == self.mock_adapters.plan_adapter.get_by_id()

    def test_get_plan_error(self):
        self.mock_adapters.plan_adapter.get_by_id = \
            MagicMock(return_value=None)
        self.mock_request.plan.__getitem__ = MagicMock(return_value='123')
        with pytest.raises(GetPlanException) as exc:
            self.interactor.get_plan()
        self.mock_request.plan.__getitem__.assert_called_with('code')
        self.mock_adapters.plan_adapter.get_by_id.assert_called_once_with(
            self.mock_request.plan.__getitem__())
        assert 'Plan 123 does not exist' in str(exc.value)

    @patch.object(RedStarsPurchaseInteractor,
                  'get_customer_from_api',
                  return_value=None)
    @patch.object(RedStarsPurchaseInteractor, 'create_customer')
    @patch.object(RedStarsPurchaseInteractor,
                  'update_customer_and_creditcard')
    def test_create_or_update_customer_create(self, update_customer_mock,
                                              create_customer_mock,
                                              get_customer_mock):
        self.interactor.create_or_update_customer()
        get_customer_mock.assert_called_once()
        create_customer_mock.assert_called_once()
        update_customer_mock.assert_not_called()

    @patch.object(RedStarsPurchaseInteractor,
                  'get_customer_from_api',
                  return_value='123')
    @patch.object(RedStarsPurchaseInteractor, 'create_customer')
    @patch.object(RedStarsPurchaseInteractor,
                  'update_customer_and_creditcard')
    def test_create_or_update_customer_update(self, update_customer_mock,
                                              create_customer_mock,
                                              get_customer_mock):
        self.interactor.create_or_update_customer()
        get_customer_mock.assert_called_once()
        create_customer_mock.assert_not_called()
        update_customer_mock.assert_called_once()

    @patch.object(RedStarsPurchaseInteractor, 'mount_subscription_object')
    def test_prepare_subscription_to_create(self, mount_subscription_mock):
        self.interactor.plan = MagicMock()
        subscription = self.interactor.prepare_subscription_to_create()
        mount_subscription_mock.assert_called_once()
        assert subscription.amount == self.interactor.plan.amount

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_player(self, find_entity_mock):
        player = self.interactor.get_player()
        find_entity_mock.assert_called_with(
            _id=self.mock_request.customer_code,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        assert player == find_entity_mock()

    @patch.object(RedStarsPurchaseInteractor, '_update_customer')
    @patch.object(RedStarsPurchaseInteractor, '_update_creditcard')
    def test_update_customer_and_creditcard(self, update_creditcard_mock,
                                            update_customer_mock):
        self.interactor.update_customer_and_creditcard()
        update_customer_mock.assert_called_once()
        update_creditcard_mock.assert_called_once()

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.PaymentLog')
    def test_add_payment_log(self, payment_log_mock, aware_now_mock):
        self.interactor.player = MagicMock()
        api_response = {
            'raw_sent_data': '123',
            'raw_received_data': '456'}
        self.interactor.add_payment_log(api_response)
        payment_log_mock.assert_called_with(
            transaction_date=aware_now_mock(),
            payment_gateway=PaymentGateway.WIRECARD,
            raw_sent_data=api_response['raw_sent_data'],
            raw_received_data=api_response['raw_received_data'])
        self.interactor.player.add_payment_log.assert_called_once_with(
            payment_log_mock())
        self.interactor.player.save.assert_called_once()

    @patch(f'{prefix}.PlayerSubscription')
    @patch(f'{prefix}.mount_next_invoice_as_datetime')
    def test_update_player_subscription(self,
                                        mount_next_invoice_mock,
                                        player_subscription_mock):
        self.interactor.player = MagicMock()
        plan = MagicMock()
        subscription = Subscription(
            code='1234',
            amount=100,
            plan=plan,
            status=SubscriptionStatus.ACTIVE)
        self.interactor.update_player_subscription(subscription)
        self.interactor.player.save.assert_called_once()
        player_subscription_mock.assert_called_once_with(
            expiration_date=mount_next_invoice_mock(),
            payment_gateway=PaymentGateway.WIRECARD,
            plan_name=plan.name)
        assert self.interactor.player.subscription == \
            player_subscription_mock()

    def test_is_active_subscription(self):
        plan = MagicMock()
        subscription = Subscription(
            code='1234',
            amount=100,
            plan=plan,
            status=SubscriptionStatus.ACTIVE)
        result = self.interactor._is_active_subscription(subscription)
        assert result

    @patch.object(RedStarsPurchaseInteractor, 'get_player')
    @patch.object(RedStarsPurchaseInteractor, 'get_plan')
    @patch.object(RedStarsPurchaseInteractor, 'create_or_update_customer')
    @patch.object(RedStarsPurchaseInteractor,
                  'prepare_subscription_to_create')
    @patch.object(RedStarsPurchaseInteractor, 'create_subscription')
    @patch.object(RedStarsPurchaseInteractor,
                  '_is_active_subscription',
                  return_value=True)
    @patch.object(RedStarsPurchaseInteractor, 'update_player_subscription')
    @patch(f'{prefix}.RedStarsPurchaseResponseModel')
    def test_run_active_subscription(self,
                                     response_model_mock,
                                     update_player_subscription_mock,
                                     is_active_subscription_mock,
                                     create_subscription_mock,
                                     prepare_subscription_mock,
                                     create_or_update_customer_mock,
                                     get_plan_mock,
                                     get_player_mock):
        response = self.interactor.run()
        get_player_mock.assert_called_once()
        get_plan_mock.assert_called_once()
        create_or_update_customer_mock.assert_called_once()
        prepare_subscription_mock.assert_called_once()
        create_subscription_mock.assert_called_once_with(
            prepare_subscription_mock())
        is_active_subscription_mock.assert_called_once_with(
            create_subscription_mock())
        update_player_subscription_mock.assert_called_once_with(
            create_subscription_mock())
        response_model_mock.assert_called_with(create_subscription_mock())
        assert response == response_model_mock()

    @patch.object(RedStarsPurchaseInteractor, 'get_player')
    @patch.object(RedStarsPurchaseInteractor, 'get_plan')
    @patch.object(RedStarsPurchaseInteractor, 'create_or_update_customer')
    @patch.object(RedStarsPurchaseInteractor,
                  'prepare_subscription_to_create')
    @patch.object(RedStarsPurchaseInteractor, 'create_subscription')
    @patch.object(RedStarsPurchaseInteractor,
                  '_is_active_subscription',
                  return_value=False)
    @patch.object(RedStarsPurchaseInteractor, 'update_player_subscription')
    @patch(f'{prefix}.RedStarsPurchaseResponseModel')
    def test_run_inactive_subscription(self,
                                       response_model_mock,
                                       update_player_subscription_mock,
                                       is_active_subscription_mock,
                                       create_subscription_mock,
                                       prepare_subscription_mock,
                                       create_or_update_customer_mock,
                                       get_plan_mock,
                                       get_player_mock):
        response = self.interactor.run()
        get_player_mock.assert_called_once()
        get_plan_mock.assert_called_once()
        create_or_update_customer_mock.assert_called_once()
        prepare_subscription_mock.assert_called_once()
        create_subscription_mock.assert_called_once_with(
            prepare_subscription_mock())
        is_active_subscription_mock.assert_called_once_with(
            create_subscription_mock())
        update_player_subscription_mock.assert_not_called()
        response_model_mock.assert_called_with(create_subscription_mock())
        assert response == response_model_mock()

    @patch.object(RedStarsPurchaseInteractor,
                  'get_player',
                  side_effect=Exception('oops'))
    def test_run_fails(self, get_player_mock):
        with pytest.raises(RedStarsPurchaseException) as exc:
            self.interactor.run()
        assert 'Error during red stars payment: Exception: oops' \
               in str(exc.value)

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    def test_create_customer_success(self, add_log_mock):
        self.mock_adapters.subscriber_adapter.save = \
            MagicMock(return_value={
                'status_code': 201,
                'content': 'Sou eu'})
        customer_created = self.interactor.create_customer()
        add_log_mock.assert_called_once_with(
            self.mock_adapters.subscriber_adapter.save())
        assert customer_created == 'Sou eu'

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    @patch('playerstars_interactors.wirecard.red_stars_purchase.'
           'process_api_response_for_errors')
    def test_create_customer_fails(self, process_api_response_mock,
                                   add_log_mock):
        self.mock_adapters.subscriber_adapter.save = \
            MagicMock(return_value={
                'status_code': 500,
                'content': 'Sou eu'})
        with pytest.raises(CreateCustomerException) as excinfo:
            self.interactor.create_customer()
        assert str(excinfo.value) == str(process_api_response_mock())

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    def test_update_credit_card(self, add_log_mock):
        self.mock_adapters.credit_card_adapter.save = \
            MagicMock(return_value={
                'status_code': 200,
                'content': 'Sou eu'})
        self.interactor._update_creditcard()
        add_log_mock.assert_called_once_with(
            self.mock_adapters.credit_card_adapter.save())

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    @patch('playerstars_interactors.wirecard.red_stars_purchase.'
           'process_api_response_for_errors')
    def test_update_credit_card_fails(self, process_api_response_mock,
                                      add_log_mock):
        self.mock_adapters.credit_card_adapter.save = \
            MagicMock(return_value={
                'status_code': 500,
                'content': 'Sou eu'})
        with pytest.raises(UpdateCreditCardException) as excinfo:
            self.interactor._update_creditcard()
        assert str(excinfo.value) == str(process_api_response_mock())

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    def test_create_subscription_success(self, add_log_mock):
        self.mock_adapters.subscription_adapter.save = \
            MagicMock(return_value={
                'status_code': 201,
                'content': 'Sou eu'})
        subscription = MagicMock()
        create_result = self.interactor.create_subscription(subscription)
        add_log_mock.assert_called_once_with(
            self.mock_adapters.subscription_adapter.save())
        assert create_result == 'Sou eu'

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    @patch('playerstars_interactors.wirecard.red_stars_purchase.'
           'process_api_response_for_errors')
    def test_create_subscription_fails(self, process_api_response_mock,
                                       add_log_mock):
        self.mock_adapters.subscription_adapter.save = \
            MagicMock(return_value={
                'status_code': 500,
                'content': 'Sou eu'})
        subscription = MagicMock()
        with pytest.raises(CreateSubscriptionException) as excinfo:
            self.interactor.create_subscription(subscription)
        assert str(excinfo.value) == str(process_api_response_mock())

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    def test_update_customer(self, add_log_mock):
        self.mock_adapters.subscriber_adapter.save = \
            MagicMock(return_value={
                'status_code': 200,
                'content': 'Sou eu'})
        self.interactor._update_customer()
        add_log_mock.assert_called_once_with(
            self.mock_adapters.subscriber_adapter.save())

    @patch.object(RedStarsPurchaseInteractor, 'add_payment_log')
    @patch('playerstars_interactors.wirecard.red_stars_purchase.'
           'process_api_response_for_errors')
    def test_update_customer_fails(self, process_api_response_mock,
                                   add_log_mock):
        self.mock_adapters.subscriber_adapter.save = \
            MagicMock(return_value={
                'status_code': 500,
                'content': 'Sou eu'})
        with pytest.raises(UpdateCustomerException) as excinfo:
            self.interactor._update_customer()
        assert str(excinfo.value) == str(process_api_response_mock())
