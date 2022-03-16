from playerstars_adapters import PlayerAdapter
from playerstars_interactors.utils.domain_utils import (
    EntityNotFoundException,
    find_entity_by_id
)
from tests.util_tests import (
    make_player_data
)
from unittest.mock import patch

import pytest


# noinspection PyUnusedLocal,PyUnusedLocal
@patch.object(PlayerAdapter, 'get_by_id', autospec=True)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
@patch('playerstars_adapters.player_adapter.'
       'BasicDynamodbAdapter.get_by_id',
       return_value=make_player_data())
def test_find_entity(player_data,
                     boto_resource,
                     create_table_player,
                     get_by_id):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    find_entity_by_id('123', player_adapter, 'Player')
    get_by_id.assert_called_once_with('123')


# noinspection PyUnusedLocal,PyUnusedLocal
@patch.object(PlayerAdapter, 'get_by_id', return_value=None)
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_find_entity_by_id_not_found(
        boto_resource, create_table_player, get_by_id):
    player_adapter = PlayerAdapter('player-table', 'localhost')
    with pytest.raises(EntityNotFoundException) as exc:
        find_entity_by_id('123', player_adapter, 'Player')
    get_by_id.assert_called_once_with('123')
    assert 'Player 123 not found' in str(exc.value)
