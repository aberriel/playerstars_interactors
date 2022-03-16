from playerstars_interactors import (
    DeleteGameError,
    DeleteGameInteractor,
    DeleteGameRequestModel)
from tests.game.game_utils import make_console_list_from_database
from unittest.mock import MagicMock, patch

import pytest


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


adapter_mock_from_database = MagicMock(
    list_all=MagicMock(return_value=make_console_list_from_database()),
    save=MagicMock(return_value='2'))
adapter_mock_not_found = MagicMock(
    list_all=MagicMock(return_value=None),
    save=MagicMock(side_effect=Exception('oops')))
adapter_mock_error = MagicMock(
    list_all=MagicMock(return_value=make_console_list_from_database()),
    save=MagicMock(side_effect=Exception('oops')))


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_delete(boto_mock):
    request = DeleteGameRequestModel('1')
    interactor = DeleteGameInteractor(request, adapter_mock_from_database)
    result = interactor.run()
    adapter_mock_from_database.save.assert_called_once()
    assert result == '1'


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_delete_game_console_not_found(boto_mock):
    request = DeleteGameRequestModel('1')
    interactor = DeleteGameInteractor(request, adapter_mock_not_found)
    with pytest.raises(DeleteGameError) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Nenhum console encontrado'


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_delete_game_save_error(boto_mock):
    request = DeleteGameRequestModel('1')
    interactor = DeleteGameInteractor(request, adapter_mock_error)
    with pytest.raises(DeleteGameError) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Erro deletando game: oops'
