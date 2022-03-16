from playerstars_adapters import PlayerAdapter
from playerstars_domain import Player
from playerstars_interactors.player.post_friends import (
    AlterFriendsRequestModel,
    AlterFriendsInteractor,
    SaveFriendsException)
from tests.player.player_utils import data_post_friends
from unittest.mock import patch

import pytest

list_entity_id = ['001']

player = Player.from_json(data_post_friends)


# noinspection PyUnusedLocal
@patch.object(PlayerAdapter, 'save', return_value=['001'])
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch('boto3.resource')
def test_post_friends(resource, get_by_id, createtable, save):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = AlterFriendsRequestModel(list_entity_id, 'player_id_005')
    interactor = AlterFriendsInteractor(request, adapter, 'add')
    response = interactor.run()
    # verificando se favoritos contem a lista de id
    result = all(elem in response for elem in list_entity_id)
    assert result
    assert response == list_entity_id


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch.object(PlayerAdapter, 'save', side_effect=Exception('oops'))
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch('boto3.resource')
def test_post_friends_raises(resource, get_by_id, createtable, save):
    adapter = PlayerAdapter('console-table', 'localhost')
    request = AlterFriendsRequestModel(list_entity_id, 'player_id_004')
    interactor = AlterFriendsInteractor(request, adapter, Player)
    with pytest.raises(SaveFriendsException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Erro salvando amigo:oops'


player = Player.from_json(data_post_friends)
player.favorites = ['001']


# noinspection PyUnusedLocal
@patch.object(PlayerAdapter, 'save', return_value=list_entity_id)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', return_value=player)
@patch('boto3.resource')
def test_delete_friends(resource, get_by_id, createtable, save):
    adapter = PlayerAdapter('player-table', 'localhost')
    request = AlterFriendsRequestModel(list_entity_id, 'player_id_005')
    interactor = AlterFriendsInteractor(request, adapter, 'delete')
    response = interactor.run()
    result = not all(elem in response for elem in list_entity_id)
    assert result
    assert response == []
