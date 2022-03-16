from playerstars_interactors.purchase.post_purchase import (
    PostPurchaseException,
    PostPurchaseInteractor,
    PostPurchaseRequestModel
)
from playerstars_adapters import PlayerAdapter
from tests.util_tests import Settings
from playerstars_domain import Player, User
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest

user = User(
    name='Pablinho',
    email='menoti@hotmail.com',
    date_birth=datetime.strptime("18/11/1991", "%d/%m/%Y"),
    street='Avenida Brasil',
    street_number='500',
    street_complement='apt 607',
    neighborhood='pechinchão',
    city='Rio de Janeiro',
    state='Rio de Janeiro',
    country='Brasil',
    postal_code='90210',
    phone_number='5555-4321',
    nickname='zyzukab',
    cpf='123.456.789-01'
)


player = Player(
    user=user,
    consoles=[],
    favorites=[],
    red_star_balance=321,
    golden_star_balance=987,
    entity_id='id123')

xml_response = """<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<checkout>
    <code>C13F573B2727DBFCC4024FB16EDEE423</code>
    <date>2019-01-16T17:26:08.000-02:00</date>
</checkout>
"""


# noinspection PyUnusedLocal
@patch('playerstars_interactors.purchase.post_purchase.requests.post',
       return_value=MagicMock(status_code=200,
                              content=xml_response.encode('iso8859-1')))
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_post_purchase(resource, table, get_by_id, post):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = PostPurchaseRequestModel({
        'price': 10,
        'description': 'teste',
        'product_id': 'id1234',
        'star_value': 5,
        'star_type': 'red',
        'duration': 1
    })
    interactor = PostPurchaseInteractor(
        request=request, player_id='id123',
        adapter_class=adapter, settings=Settings)
    response = interactor.run()
    assert response == {
        'url_redirect': 'https://sandbox.pagseguro.uol.com.br/v2/checkout/'
                        'payment.html?code=C13F573B2727DBFCC4024FB16EDEE423',
        'played_id': 'id123'
    }


xml_error_response = """<?xml version="1.0" encoding="ISO-8859-1"
standalone="yes"?>
<errors>
    <error>
        <code>Error Code</code>
        <message>Error Description</message>
    </error>
</errors>"""


# noinspection PyUnusedLocal
@patch('playerstars_interactors.purchase.post_purchase.requests.post',
       return_value=MagicMock(status_code=400,
                              content=xml_error_response.encode('iso8859-1')))
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_post_purchase_pagseguro_error(resource, table, get_by_id, post):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = PostPurchaseRequestModel({
        'price': 10,
        'description': 'teste',
        'product_id': 'id1234',
        'star_value': 5,
        'star_type': 'red',
        'duration': 1
    })
    interactor = PostPurchaseInteractor(request, 'idteste', adapter, Settings)
    with pytest.raises(PostPurchaseException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == xml_error_response


xml_content_error_response = """<?xml version="1.0" encoding="ISO-8859-1"
 standalone="yes"?>
<checkout>
    <date>2019-01-16T17:26:08.000-02:00</date>
</checkout>
"""


# noinspection PyUnusedLocal
@patch('playerstars_interactors.purchase.post_purchase.requests.post',
       return_value=MagicMock(
           status_code=200,
           content=xml_content_error_response.encode('iso8859-1')))
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_post_purchase_pagseguro_200_error(resource, table, get_by_id, post):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = PostPurchaseRequestModel({
        'price': 10,
        'description': 'teste',
        'product_id': 'id1234',
        'star_value': 5,
        'star_type': 'red',
        'duration': 1
    })
    interactor = PostPurchaseInteractor(request, 'idteste', adapter, Settings)
    with pytest.raises(PostPurchaseException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == "Erro no retorno do PagSeguro: " \
                                 "'NoneType' object has no attribute 'text'"


xml_known_error_response = """<?xml version="1.0" encoding="ISO-8859-1"
standalone="yes"?>
<errors>
    <error>
        <code>Error Code</code>
        <message>Houve um problema e não foi possível exibir a página</message>
    </error>
</errors>"""


# noinspection PyUnusedLocal
@patch('playerstars_interactors.purchase.post_purchase.requests.post',
       return_value=MagicMock(
           status_code=400,
           content=xml_known_error_response.encode('iso8859-1')))
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_post_purchase_pagseguro_known_error(
        resource, table, get_by_id, post):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = PostPurchaseRequestModel({
        'price': 10,
        'description': 'teste',
        'product_id': 'id1234',
        'star_value': 5,
        'star_type': 'red',
        'duration': 1
    })
    interactor = PostPurchaseInteractor(request, 'idteste', adapter, Settings)
    with pytest.raises(PostPurchaseException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == "O Sandbox do Pagseguro retornou um erro."


# noinspection PyUnusedLocal
@patch('playerstars_interactors.purchase.post_purchase.requests.post',
       return_value=MagicMock(status_code=200, content=xml_response.encode('iso8859-1')))
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_post_purchase_gold(resource, table, get_by_id, post):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = PostPurchaseRequestModel({
        'price': 10,
        'description': 'teste',
        'product_id': 'id1234',
        'star_value': 5,
        'star_type': 'gold',
        'duration': 0
    })
    interactor = PostPurchaseInteractor(
        request=request, player_id='id123',
        adapter_class=adapter, settings=Settings)
    player123 = interactor._add_purchase_to_player('schrubles', 'glubglub')
    assert player123.purchases[1].product.duration == 0
    response = interactor.run()
    assert response == {
        'url_redirect': 'https://sandbox.pagseguro.uol.com.br/v2/checkout/'
                        'payment.html?code=C13F573B2727DBFCC4024FB16EDEE423',
        'played_id': 'id123'
    }
