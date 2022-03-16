from playerstars_interactors import (
    GetPurchaseHistoryInteractor,
    GetPurchaseHistoryRequestModel
)
from playerstars_adapters import PlayerAdapter
from playerstars_domain import Player
from unittest.mock import patch
import pytest


player_json = {
    'entity_id': '',
    'red_star_balance': 15,
    'consoles': [{
        'console_id': 'c01',
        'tag_name': 'Leoplay4',
        'game_points': [{
            "game_id": 'g01',
            'victories': 0
        }]
    }],
    "countries_regions": ["id123"],
    "states_regions": ["id123"],
    "favorites": ["ght232141-3a12-5t67-19ehdufasuu"],
    "golden_star_balance": 0,
    "star_transactions": [{
        "value": 2,
        "operation_date": "2019-08-21T13:11:07+00:00",
        "coin_type": "GOLDEN_STAR",
        "operation_type": "DEBIT",
        "source": "DUEL",
        "source_id": "68dc45c5-43eb-4351-bead-4319aba7af85"
    }],
    "purchases": [{
        "product": {
            "price": 1050,
            "star_value": "3",
            "description": "teste teste teste",
            "star_type": "red",
            "duration": 3
        },
        "purchase_type": "SUBSCRIPTION",
        "purchase_datetime": "2017-11-21T09:58:00",
        "payment": {
            "code": "schrubles123",
            "payment_datetime": "2017-11-22T09:58:00",
            "payment_type": "PAGSEGURO",
            "transactions": []
        }
    }, {
        "product": {
            "price": 999,
            "star_value": "4",
            "description": "testinhooo",
            "star_type": "gold",
            "duration": 0
        },
        "purchase_type": "GOLDEN_STAR_PURCHASE",
        "purchase_datetime": "2016-11-21T09:58:00",
        "payment": {
            "code": "schrubles123",
            "payment_datetime": "2016-11-22T09:58:00",
            "payment_type": "PAGSEGURO",
            "transactions": []
        }
    }, {
        "payment": {
            "code": "7f4f2703-14d3-42a4-858d-89bf037f5675",
            "payment_datetime": "2019-11-06T21:00:07.780761",
            "payment_type": "PAGSEGURO",
            "transactions": [
                {
                    "code": "7f4f2703-14d3-42a4-858d-89bf037f5675",
                    "status": "AWAITING_PAYMENT",
                    "transaction_datetime": "2019-11-06T21:00:07.780471"
                },
                {
                    "code": "E004334A-B2EE-408F-AF09-9E686146E28E",
                    "status": "PAID",
                    "transaction_datetime": "2019-11-06T21:00:07.780471"
                }
            ]
        },
        "product": {
            "description": "20 stars gold",
            "price": 10000,
            "star_type": "gold",
            "star_value": 20,
            "duration": 0
        },
        "purchase_datetime": "2019-11-06T21:00:07.781110",
        "purchase_type": "GOLDEN_STAR_PURCHASE"
    }],
    "user": {
        "name": "Anselmo Lira",
        "email": "playerstars@playerstars.com.br",
        "date_birth": "2018-11-11",
        "street": 'Avenida Brasil',
        "street_number": '500',
        "street_complement": 'apt 607',
        "neighborhood": 'pechinchão',
        "city": "Rio de Janeiro",
        "state": "Rio de Janeiro",
        "country": "Brasil",
        "postal_code": "22333-000",
        "phone_number": "(21) 99663-6963",
        "cpf": "123.456.789-00",
        "nickname": "anselmo.lira",
        "profile_image": "ACCBB4762CF23AA35690CC"
    },
    'points': 200,
    'terms': True,
    'player_status': 'OFFLINE'
}
player = Player.from_json(player_json)

expected_purchases = [
    {
        'payment': {
            'code': '7f4f2703-14d3-42a4-858d-89bf037f5675',
            'payment_datetime': '2019-11-06T21:00:07.780761',
            'payment_type': 'PAGSEGURO',
            'transactions': [
                {
                    'code': '7f4f2703-14d3-42a4-858d-89bf037f5675',
                    'status': 'AWAITING_PAYMENT',
                    'transaction_datetime': '2019-11-06T21:00:07.780471'
                },
                {
                    'code': 'E004334A-B2EE-408F-AF09-9E686146E28E',
                    'status': 'PAID',
                    'transaction_datetime': '2019-11-06T21:00:07.780471'
                }
            ]
        },
        'product': {
            'description': '20 stars gold',
            'price': 10000,
            'star_type': 'gold',
            'star_value': 20,
            'name': None
        },
        'purchase_datetime': '2019-11-06T21:00:07.781110',
        'purchase_type': 'GOLDEN_STAR_PURCHASE'
    },
    {
        'product': {
            'price': 1050,
            'star_value': 3,
            'description': 'teste teste teste',
            'star_type': 'red',
            'duration': 3,
            'name': None
        },
        'purchase_type': 'SUBSCRIPTION',
        'purchase_datetime': '2017-11-21T09:58:00',
        'payment': {
            'code': 'schrubles123',
            'payment_datetime': '2017-11-22T09:58:00',
            'payment_type': 'PAGSEGURO',
            'transactions': []
        }
    },
    {
        'product': {
            'price': 999,
            'star_value': 4,
            'description': 'testinhooo',
            'star_type': 'gold',
            'name': None
        },
        'purchase_type': 'GOLDEN_STAR_PURCHASE',
        'purchase_datetime': '2016-11-21T09:58:00',
        'payment': {
            'code': 'schrubles123',
            'payment_datetime': '2016-11-22T09:58:00',
            'payment_type': 'PAGSEGURO',
            'transactions': []
        }
    }
]

expected_red_purchases = [
    {
        'product': {
            'price': 1050,
            'star_value': 3,
            'description': 'teste teste teste',
            'star_type': 'red',
            'duration': 3,
            'name': None
        },
        'purchase_type': 'SUBSCRIPTION',
        'purchase_datetime': '2017-11-21T09:58:00',
        'payment': {
            'code': 'schrubles123',
            'payment_datetime': '2017-11-22T09:58:00',
            'payment_type': 'PAGSEGURO',
            'transactions': []
        }
    }
]


@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_purchase_history(resource, table, get_by_id):
    adapter = PlayerAdapter('player-test', 'localhost-test')
    request = GetPurchaseHistoryRequestModel({'player_id': 'id123'})
    interactor = GetPurchaseHistoryInteractor(request, adapter)
    response = interactor.run()
    assert response == expected_purchases


@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_red_purchase_history(resource, table, get_by_id):
    adapter = PlayerAdapter('player-test', 'localhost-test')
    request = GetPurchaseHistoryRequestModel({'player_id': 'id123',
                                              'star_type': 'red'})
    interactor = GetPurchaseHistoryInteractor(request, adapter)
    response = interactor.run()
    assert response == expected_red_purchases


@patch.object(PlayerAdapter, 'get_by_id', return_value=None)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_purchase_history_player_not_found(resource, table, get_by_id):
    adapter = PlayerAdapter('player-test', 'localhost-test')
    request = GetPurchaseHistoryRequestModel({'player_id': 'id123'})
    interactor = GetPurchaseHistoryInteractor(request, adapter)
    with pytest.raises(BaseException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Player id123 não existe'
