from playerstars_interactors import \
    GetPlayersByConsoleGameRequestModel, GetPlayersByConsoleGameInteractor
from tests.player.player_utils import player1, player2, player3, console
from unittest.mock import MagicMock, patch

import copy


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


expected_response = [player1.to_json(), player2.to_json()]

player3_temp = copy.deepcopy(player3)
player3_temp.consoles[0].console_id = 11

query_params = {
    'console_id': '1',
    'game_id': 'id1234'
}


console_adapter_mock = MagicMock(
    get_by_id=MagicMock(return_value=console))
player_adapter_mock = MagicMock(
    list_all=MagicMock(return_value=[player1, player2, player3_temp]))
player_adapter_mock_empty = MagicMock(
    list_all=MagicMock(return_value=[]))


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_players_by_console_game(boto3):
    request = GetPlayersByConsoleGameRequestModel(query_params)
    interactor = GetPlayersByConsoleGameInteractor(
        request, player_adapter_mock, console_adapter_mock)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == expected_response


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_players_by_console_game_empty(boto3):
    request = GetPlayersByConsoleGameRequestModel(query_params)
    interactor = GetPlayersByConsoleGameInteractor(
        request, player_adapter_mock_empty, console_adapter_mock)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == []
