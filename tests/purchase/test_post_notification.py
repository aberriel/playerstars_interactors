from playerstars_adapters import PlayerAdapter, ProductAdapter
from playerstars_interactors import (
    PostNotificationRequestModel,
    PostNotificationResponseModel,
    PostNotificationInteractor,
    PagSeguroException
)
from playerstars_interactors.purchase.post_notification import (
    get_player_adapter,
    get_token,
    get_pagseguro_host,
    get_pagseguro_notifications_url,
    parse_transaction_response,
    find_player_by_reference,
    add_transaction_by_reference,
    get_product,
    add_balance_if_purchase_accepted,
    last_status_not_equals_transaction_status)
from playerstars_domain import (
    Player,
    Purchase,
    PagSeguroPaymentTransaction,
    PagSeguroStatus,
    Product,
    PagSeguroPayment,
    ProductPurchased)
from unittest.mock import patch, MagicMock
import pytest
from decouple import config
from tests.util_tests import player_json


form_urlencoded_body = b'notificationType=transaction&notificationCode=A2CDE'
request_model = PostNotificationRequestModel(form_urlencoded_body)
settings = MagicMock(
    PLAYER_TABLE_NAME='teste', DYNAMODB_URL='teste-url',
    PAGSEGURO_SANDBOX_TOKEN=config('', 'test_schrubles'),
    PAGSEGURO_TOKEN=config('', 'gluglu'),
    PAGSEGURO_SANDBOX_ENABLE=True, PAGSEGURO_EMAIL='oie@tchau.com.br',
    PRODUCT_TABLE_NAME='testeeee',
    PAGSEGURO_HOST_URL='https://ws.pagseguro.uol.com.br',
    PAGSEGURO_SANDBOX_HOST_URL='https://ws.sandbox.pagseguro.uol.com.br',
    PAGSEGURO_UPDATE_NOTIFICATION_URL='{host}/v3/transactions/notifications/'
                               '{notification_code}?email={email}&token='
                               '{token}')


def test_post_notification_request_model():
    req = PostNotificationRequestModel(form_urlencoded_body)
    assert req.code == 'A2CDE'
    assert req.type == 'transaction'


def test_post_notification_response_model():
    response = PostNotificationResponseModel('12345')
    assert response() == '12345'


@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_adapter(resource, table):
    assert get_player_adapter(settings)


@patch('playerstars_interactors.purchase.post_notification.requests.get',
       return_value=MagicMock(status_code=200))
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_make_request_200(resource, table, get):
    adapter = PlayerAdapter('test-table', 'test-db')
    interactor = PostNotificationInteractor(request_model, 'settings', adapter)
    req = interactor._make_request('gluglu')
    assert req.status_code == 200


@patch('playerstars_interactors.purchase.post_notification.requests.get',
       return_value=MagicMock(status_code=500))
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_make_request_500(resource, table, get):
    adapter = PlayerAdapter('test-table', 'test-db')
    interactor = PostNotificationInteractor(request_model, 'settings', adapter)
    with pytest.raises(PagSeguroException) as excinfo:
        interactor._make_request('gluglu')
    assert 'GET de notificação ' in str(excinfo.value)


def test_get_token():
    assert get_token(settings) == 'test_schrubles'


def test_get_pag_seguro_host():
    assert get_pagseguro_host(settings) == \
        'https://ws.sandbox.pagseguro.uol.com.br'


def test_get_pagseguro_notifications_url():
    assert get_pagseguro_notifications_url('code', settings) == \
        'https://ws.sandbox.pagseguro.uol.com.br/v3/transactions/' \
        'notifications/code?email=oie@tchau.com.br&token=test_schrubles'


def test_parse_transaction_response():
    parsed_transaction = parse_transaction_response(xml_notification_response)
    assert parsed_transaction['transaction'].code == \
        'BF13B62F-24DE-43AC-AC2B-A2EE7F974FFA'
    assert parsed_transaction['reference'] == 'puts'
    assert parsed_transaction['item_id'] == 'itemID'


def test_parse_transaction_response_raises():
    empty_xml = """<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
    <transaction></transaction>"""
    with pytest.raises(ValueError) as excinfo:
        parse_transaction_response(empty_xml)
    assert 'Erro lendo retorno' in str(excinfo.value)


@patch('boto3.resource')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_interactors.purchase.post_notification.PlayerAdapter'
       '.list_all', return_value=[Player.from_json(player_json)])
def test_find_player_by_reference(list_all, table, resource):
    found_player = find_player_by_reference('schrubles1241', settings)
    with pytest.raises(PagSeguroException) as excinfo:
        find_player_by_reference('outro', settings)

    assert found_player.user.name == 'Anselmo Lira'
    assert 'Não encontrado um player que possui' in str(excinfo.value)


def response_parsed_mock():
    return {
        'transaction': PagSeguroPaymentTransaction(
            code='glub',
            status=PagSeguroStatus.get_from_int(1)),
        'reference': 'schrubles1241'
    }


def second_response_parsed_mock():
    return {
        'transaction': PagSeguroPaymentTransaction(
            code='glub',
            status=PagSeguroStatus.get_from_int(3)),
        'reference': 'schrubles1241',
        'item_id': 'id123'
    }


def response_parsed_wrong_mock():
    return {
        'transaction': PagSeguroPaymentTransaction(
            code='glub',
            status=PagSeguroStatus.get_from_int(1)),
        'reference': 'schrubles124'
    }


def test_last_status_not_equals_transaction_status():
    transaction = PagSeguroPaymentTransaction(
        code='glub',
        status=PagSeguroStatus.get_from_int(1))
    payment = PagSeguroPayment(code='glub')
    transaction1 = PagSeguroPaymentTransaction(
        code='glub',
        status=PagSeguroStatus.get_from_int(1))
    payment.transactions.append(transaction1)
    product1 = ProductPurchased(
        price=140,
        star_value=10,
        description='gluglu',
        star_type='gold',
        duration=0)
    purchase = Purchase(product=product1, payment=payment)
    assert not last_status_not_equals_transaction_status(transaction, purchase)
    assert product1.duration == 0


def test_add_transaction_by_reference():
    player = Player.from_json(player_json)
    first_player = player.to_json()
    assert add_transaction_by_reference(player, response_parsed_mock())
    assert player.to_json() != first_player
    second_player = player.to_json()
    assert not (add_transaction_by_reference(
        player, response_parsed_wrong_mock()))
    assert second_player == player.to_json()
    third_player = player.to_json()
    assert add_transaction_by_reference(player, second_response_parsed_mock())
    assert player.to_json() != third_player
    assert add_transaction_by_reference(player, second_response_parsed_mock())


product = Product.from_json({
    "description": "Produto Teste 12",
    "star_type": "red",
    "entity_id": "b999d32b-3e5a-4402-b116-78a3131bc6fa",
    "star_value": 7,
    "price": 340,
    "duration": 3
})


@patch('boto3.resource')
@patch.object(ProductAdapter, '_create_table_if_dont_exists')
@patch('playerstars_interactors.purchase.post_notification.ProductAdapter'
       '.get_by_id', return_value=product)
def test_get_product(get, table, resource):
    product_data = get_product('id123', settings)
    assert product_data.price == 340


product = Product.from_json({
    "description": "Produto Teste 12",
    "star_type": "red",
    "entity_id": "b999d32b-3e5a-4402-b116-78a3131bc6fa",
    "star_value": 90,
    "price": 340,
    "duration": 3
})


@patch('boto3.resource')
@patch.object(ProductAdapter, '_create_table_if_dont_exists')
@patch('playerstars_interactors.purchase.post_notification.ProductAdapter'
       '.get_by_id', return_value=product)
def test_add_red_if_purchase_accepted(get, table, resource):
    player = Player.from_json(player_json)
    add_balance_if_purchase_accepted(
        player, second_response_parsed_mock(), settings)
    assert player.red_star_balance == 105


product = Product.from_json({
    "description": "Produto Teste 12",
    "star_type": "gold",
    "entity_id": "b999d32b-3e5a-4402-b116-78a3131bc6fa",
    "star_value": 90,
    "price": 340,
    "duration": 0
})


@patch('boto3.resource')
@patch.object(ProductAdapter, '_create_table_if_dont_exists')
@patch('playerstars_interactors.purchase.post_notification.ProductAdapter'
       '.get_by_id', return_value=product)
def test_add_gold_if_purchase_accepted(get, table, resource):
    player = Player.from_json(player_json)
    add_balance_if_purchase_accepted(
        player, second_response_parsed_mock(), settings)
    assert player.golden_star_balance == 90


product = Product.from_json({
    "description": "Produto Teste 12",
    "star_type": "golqasadasd",
    "entity_id": "b999d32b-3e5a-4402-b116-78a3131bc6fa",
    "star_value": 90,
    "price": 340,
    "duration": 3
})


@patch('boto3.resource')
@patch.object(ProductAdapter, '_create_table_if_dont_exists')
@patch('playerstars_interactors.purchase.post_notification.ProductAdapter'
       '.get_by_id', return_value=product)
def test_add_balance_if_purchase_accepted_raises(get, table, resource):
    player = Player.from_json(player_json)
    with pytest.raises(BaseException) as excinfo:
        add_balance_if_purchase_accepted(
            player, second_response_parsed_mock(), settings)
    assert 'Star Type invalido' in str(excinfo.value)


@patch('boto3.resource')
@patch.object(ProductAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_interactors.purchase.post_notification.'
       'get_pagseguro_notifications_url')
@patch('playerstars_interactors.purchase.post_notification.'
       'find_player_by_reference')
@patch('playerstars_interactors.purchase.post_notification.'
       'PostNotificationInteractor._make_request')
@patch('playerstars_interactors.purchase.post_notification.'
       'parse_transaction_response')
@patch('playerstars_interactors.purchase.post_notification.'
       'add_transaction_by_reference')
@patch('playerstars_interactors.purchase.post_notification.'
       'add_balance_if_purchase_accepted')
def test_post_notification_interactor(m, m1, m2, m3, m4, m5, m6, m7, m8):
    interactor = PostNotificationInteractor(request_model, settings, 'frufru')
    response = interactor.run()
    assert response


@patch('boto3.resource')
@patch.object(ProductAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_interactors.purchase.post_notification.'
       'get_pagseguro_notifications_url')
@patch('playerstars_interactors.purchase.post_notification.'
       'PostNotificationInteractor._make_request')
@patch('playerstars_interactors.purchase.post_notification.'
       'parse_transaction_response')
@patch('playerstars_interactors.purchase.post_notification.'
       'add_transaction_by_reference')
@patch('playerstars_interactors.purchase.post_notification.'
       'add_balance_if_purchase_accepted')
def test_post_notification_interactor_raises(m, m1, m2, m3, m4, m5, m6, m7):
    interactor = PostNotificationInteractor(request_model, settings, 'frufru')
    with pytest.raises(BaseException) as excinfo:
        interactor.run()
    assert 'Falha ao salvar o player com a nova' in str(excinfo.value)


xml_notification_response = """<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<transaction>
    <date>2019-10-03T14:47:44.000-03:00</date>
    <code>BF13B62F-24DE-43AC-AC2B-A2EE7F974FFA</code>
    <reference>puts</reference>
    <type>1</type>
    <status>3</status>
    <lastEventDate>2019-10-03T14:52:40.000-03:00</lastEventDate>
    <paymentMethod>
        <type>1</type>
        <code>101</code>
    </paymentMethod>
    <grossAmount>20.00</grossAmount>
    <discountAmount>0.00</discountAmount>
    <creditorFees>
        <installmentFeeAmount>0.00</installmentFeeAmount>
        <intermediationRateAmount>0.40</intermediationRateAmount>
        <intermediationFeeAmount>1.00</intermediationFeeAmount>
    </creditorFees>
    <netAmount>18.60</netAmount>
    <extraAmount>0.00</extraAmount>
    <escrowEndDate>2019-10-03T14:52:40.000-03:00</escrowEndDate>
    <installmentCount>1</installmentCount>
    <itemCount>1</itemCount>
    <items>
        <item>
            <id>itemID</id>
            <description>Doacao Bolao ABBR</description>
            <quantity>1</quantity>
            <amount>20.00</amount>
        </item>
    </items>
    <sender>
        <name>asdfg gggg</name>
        <email>nickolas@sandbox.pagseguro.com.br</email>
        <phone>
            <areaCode>21</areaCode>
            <number>973724872</number>
        </phone>
        <documents>
            <document>
                <type>CPF</type>
                <value>12345678909</value>
            </document>
        </documents>
    </sender>
    <shipping>
        <address>
            <street>RUA ESCRITOR ELIE WIESEL</street>
            <number>123</number>
            <complement>489</complement>
            <district>Recreio dos Bandeirantes</district>
            <city>RIO DE JANEIRO</city>
            <state>RJ</state>
            <country>BRA</country>
            <postalCode>22790672</postalCode>
        </address>
        <type>3</type>
        <cost>0.00</cost>
    </shipping>
    <gatewaySystem>
        <type>cielo</type>
        <nsu>0</nsu>
        <tid>0</tid>
        <establishmentCode>1056784170</establishmentCode>
        <acquirerName>CIELO</acquirerName>
    </gatewaySystem>
    <primaryReceiver>
        <publicKey>PUB4C8D7D1D87A54B31883949BDCEA7CD59</publicKey>
    </primaryReceiver>
</transaction>"""
