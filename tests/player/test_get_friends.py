from datetime import date
from playerstars_adapters import PlayerAdapter
from playerstars_domain import (
    GamePoints,
    Player,
    PlayerConsoles,
    PlayerStatus, User)
from playerstars_interactors.player.get_all_friends import (
    GetAllFriendsRequestModel,
    GetAllFriendsInteractor)
from playerstars_interactors.player.get_friend import (
    GetFriendRequestModel,
    GetFriendInteractor)
from unittest.mock import patch


user_data = User(name='Anselmo Lira',
                 email='playerstars@playerstars.com.br',
                 date_birth=date(1986, 12, 16),
                 street='Avenida Brasil',
                 street_number='500',
                 street_complement='apt 607',
                 neighborhood='pechinchão',
                 city='Rio de Janeiro',
                 state='Rio de Janeiro',
                 country='Brasil',
                 postal_code='22333-000',
                 phone_number='(21) 99663-6963',
                 cpf='123.456.789-00',
                 nickname='anselmo.lira',
                 profile_image='ACCBB4762CF23AA35690CC')


player = Player(
    user=user_data,
    favorites=['001', 'player_id_001'],
    player_status=PlayerStatus.OFFLINE,
    red_star_balance=123,
    golden_star_balance=4321,
    consoles=[
        PlayerConsoles(
            console_id='1',
            tag_name='tag#1',
            game_points=[
                GamePoints(
                    game_id='11',
                    victories=0)]
        ),
        PlayerConsoles(
            console_id='11',
            tag_name='tag#2',
            game_points=[
                GamePoints(
                    game_id='11',
                    victories=0
                )]
        )
    ],
    states_regions=[],
    countries_regions=[],
    entity_id="player_id_005",
    star_transactions=[],
    points=40,
    terms=True)

favorite_player = Player(
    user=user_data,
    favorites=[],
    terms=True,
    player_status=PlayerStatus.OFFLINE,
    red_star_balance=123,
    golden_star_balance=4321,
    consoles=[],
    states_regions=[],
    countries_regions=[],
    entity_id="player_id_001")


# noinspection PyUnusedLocal
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch('boto3.resource')
def test_get_all_friends_by_player_id(resource, get_by_id, createtable):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = GetAllFriendsRequestModel(player.entity_id)
    interactor = GetAllFriendsInteractor(request, adapter)
    response = interactor.run()
    assert response == [{
        'entity_id': 'player_id_005',
        'name': 'Anselmo Lira',
        'photo': 'ACCBB4762CF23AA35690CC',
        'nickname': 'anselmo.lira'
    }, {
        'entity_id': 'player_id_005',
        'name': 'Anselmo Lira',
        'photo': 'ACCBB4762CF23AA35690CC',
        'nickname': 'anselmo.lira'
    }]


# noinspection PyUnusedLocal
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=[])
@patch('boto3.resource')
def test_get_all_friends_is_empty(resource, get_by_id, createtable):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = GetAllFriendsRequestModel('00000')
    interactor = GetAllFriendsInteractor(request, adapter)
    response = interactor.run()
    assert response == []


# noinspection PyUnusedLocal
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(GetFriendInteractor,
              'get_favorite_from_player',
              return_value=favorite_player)
@patch('boto3.resource')
def test_get_favorite_by_id_form_player_by_id(
        resource, get_favorite, get_by_id, createtable):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = GetFriendRequestModel(player.entity_id,
                                    favorite_player.entity_id)
    interactor = GetFriendInteractor(request, adapter)
    response = interactor.run()
    assert response == favorite_player.to_json()


# noinspection PyUnusedLocal
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch.object(GetFriendInteractor, 'get_favorite_from_player',
              return_value=None)
@patch('boto3.resource')
def test_get_favorite_by_id_not_found(
        resource, get_favorite, get_by_id, createtable):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = GetFriendRequestModel('000', favorite_player.entity_id)
    interactor = GetFriendInteractor(request, adapter)
    response = interactor.run()
    assert response is None


# noinspection PyUnusedLocal
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=favorite_player)
@patch('boto3.resource')
def test_get_favorite_from_player(resource, get_by_id, createtable):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = GetFriendRequestModel(
        player.entity_id,
        favorite_player.entity_id)
    interactor = GetFriendInteractor(request, adapter)
    response = interactor.get_favorite_from_player(
        player,
        favorite_player.entity_id)
    assert response == favorite_player
