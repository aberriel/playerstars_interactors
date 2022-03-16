from playerstars_interactors import (
    GetAllGamesInteractor,
    GetGameRequestModel,
    GetGameInteractor,
    GetAllGamesRequestModel)
from tests.game.game_utils import (
    make_console_by_id,
    make_console_list_from_database,
    make_console_no_games,
    make_game_data,
    make_game_get_all_result)
from unittest.mock import MagicMock, patch


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


adapter_mock_from_db = MagicMock(
    get_by_id=MagicMock(return_value=make_console_by_id()),
    list_all=MagicMock(return_value=make_console_list_from_database()))
adapter_mock_none = MagicMock(
    get_by_id=MagicMock(return_value=None))
adapter_mock_no_games = MagicMock(
    get_by_id=MagicMock(return_value=make_console_no_games()))


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_all_games_by_console(boto_mock):
    request = GetAllGamesRequestModel('id1234')
    interactor = GetAllGamesInteractor(request, adapter_mock_from_db)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == make_game_get_all_result()


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_game_by_id(boto_mock):
    request = GetGameRequestModel('1')
    interactor = GetGameInteractor(request, adapter_mock_from_db)
    result = interactor.run()
    assert result == make_game_data()


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_game_not_found(boto_mock):
    request = GetGameRequestModel('99')
    interactor = GetGameInteractor(request, adapter_mock_from_db)
    result = interactor.run()
    assert result is None


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_all_empty(boto_mock):
    request = GetAllGamesRequestModel('id1234')
    interactor = GetAllGamesInteractor(request, adapter_mock_none)
    result = interactor.run()
    assert result == {}


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_all_none_found(boto_mock):
    request = GetAllGamesRequestModel('id1234')
    interactor = GetAllGamesInteractor(request, adapter_mock_no_games)
    result = interactor.run()
    assert result == []
