from playerstars_interactors import \
    GetFriendsByConsoleGameRequestModel, GetFriendsByConsoleGameInteractor
from tests.player.player_utils import player1, player2, console
from unittest.mock import MagicMock, patch

import copy


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


expected_response = [{
    'entity_id': player1.entity_id,
    'name': player1.user.name,
    'photo': player1.user.profile_image,
    'nickname': player1.user.nickname,
    'tag_name': 'Leoplay4'
}, {
    'entity_id': player1.entity_id,
    'name': player1.user.name,
    'photo': player1.user.profile_image,
    'nickname': player1.user.nickname,
    'tag_name': 'Leoplay4'
}]
player_temp = copy.deepcopy(player1)
player_temp.consoles[0].console_id = '1'

query_params = {
    'player_id': '123',
    'console_id': '1',
    'game_id': 'id1234'}


console_adapter_mock = MagicMock(
    get_by_id=MagicMock(return_value=console))
player_adapter_mock_1 = MagicMock(
    get_by_id=MagicMock(return_value=player1))
player_adapter_mock_2 = MagicMock(
    get_by_id=MagicMock(return_value=player2))


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_players_by_console_game(boto3):
    request = GetFriendsByConsoleGameRequestModel(query_params)
    interactor = GetFriendsByConsoleGameInteractor(
        request, player_adapter_mock_1, console_adapter_mock)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == expected_response


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_players_by_console_game_empty(boto3):
    request = GetFriendsByConsoleGameRequestModel(query_params)
    interactor = GetFriendsByConsoleGameInteractor(
        request, player_adapter_mock_2, console_adapter_mock)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == []
