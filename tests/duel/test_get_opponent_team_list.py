from playerstars_interactors import (
    GetOpponentTeamsException,
    GetOpponentTeamsInteractor,
    GetOpponentTeamsRequestModel,
    GetOpponentTeamsResponseModel)
from pytest import raises
from tests.util_tests import team_list, team_list_with_1, player_1, player_2
from unittest.mock import MagicMock, patch


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


query_params = {
    'team_id': team_list[0].entity_id,
    'console_id': '2',
    'game_id': 'schrubles'
}

player_adapter_mock_1 = MagicMock(
    get_by_id=MagicMock(return_value=player_1))
player_adapter_mock_2 = MagicMock(
    get_by_id=MagicMock(return_value=player_2))
team_adapter_mock = MagicMock(
    filter=MagicMock(return_value=team_list))


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_teams_by_game(boto3):
    request = GetOpponentTeamsRequestModel(query_params)
    interactor = GetOpponentTeamsInteractor(
        request=request, player_adapter=player_adapter_mock_1,
        team_adapter=team_adapter_mock)
    response = interactor.run()
    assert isinstance(response, GetOpponentTeamsResponseModel)
    assert response() == [{
        'entity_id': 'fe5c6aea-6928-4008-a08d-f90440983dd2',
        'name': 'brazucas2',
        'nickname': 'Zyzukab',
        'photo': None,
        'tag_name': 'tag#3'
    }, {
        'entity_id': 'fe5c6aea-6928-4008-a08d-f90440983dd3',
        'name': 'brazucas3',
        'nickname': 'Zyzukab',
        'photo': None,
        'tag_name': 'tag#3'
    }]


team_adapter_mock2 = MagicMock(
    filter=MagicMock(return_value=[]))


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_players_by_console_game_empty(boto3):
    request = GetOpponentTeamsRequestModel(query_params)
    interactor = GetOpponentTeamsInteractor(
        request=request, player_adapter=player_adapter_mock_2,
        team_adapter=team_adapter_mock2)

    response = interactor.run()
    assert isinstance(response, GetOpponentTeamsResponseModel)
    assert response() == []


player_adapter_mock_none = MagicMock(
    get_by_id=MagicMock(return_value=None))
team_adapter_mock_error = MagicMock(
    filter=MagicMock(side_effect=BaseException('oops')))


team_adapter_mock_3 = MagicMock(
    filter=MagicMock(return_value=team_list_with_1))


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_opponents_none_captain(boto_mock):
    request = GetOpponentTeamsRequestModel(query_params)
    interactor = GetOpponentTeamsInteractor(
        request=request,
        player_adapter=player_adapter_mock_none,
        team_adapter=team_adapter_mock_3)

    with raises(GetOpponentTeamsException) as exc:
        interactor.run()
    assert 'Error during recovery opponents list: Captain id ' \
           '7e436515-d1f7-49a3-ba2e-e43a7504ad22 not found in team ' \
           'fe5c6aea-6928-4008-a08d-f90440983dd2' in str(exc.value)


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_oppoennts_team_error(boto_mock):
    request = GetOpponentTeamsRequestModel(query_params)
    interactor = GetOpponentTeamsInteractor(
        request=request,
        player_adapter=player_adapter_mock_2,
        team_adapter=team_adapter_mock_error)

    with raises(GetOpponentTeamsException) as exc:
        interactor.run()
    assert 'Error during recovery opponents list: oops' in str(exc.value)
