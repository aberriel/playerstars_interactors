from playerstars_interactors import \
    GetMyTeamsByGameRequestModel, GetMyTeamsByGameInteractor
from tests.util_tests import team_list, player_1, player_2, player_3
from unittest.mock import MagicMock, patch
from playerstars_domain import Console


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


query_params = {
    'player_id': player_3.entity_id,
    'console_id': '2',
    'game_id': 'schrubles'
}
console = Console.from_json({
    "entity_id": "2",
    "games": [{
        "entity_id": "a8b7c2e4-7d89-4a24-965b-7c201e4bbe37",
        "logo_path": "0e579f8eb50a43de1c1fd2fc1d6c81a60.jpg",
        "name": "Hearthstone"
    }],
    "logo_path": "/images/sss.png",
    "name": "Blizzard"
})

console_adapter_mock = MagicMock(
    get_by_id=MagicMock(return_value=console))
player_adapter_mock_1 = MagicMock(
    get_by_id=MagicMock(return_value=player_1))
player_adapter_mock_2 = MagicMock(
    get_by_id=MagicMock(return_value=player_2))
team_adapter_mock = MagicMock(
    filter=MagicMock(return_value=team_list))


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_teams_by_game(boto3):
    request = GetMyTeamsByGameRequestModel(query_params)
    interactor = GetMyTeamsByGameInteractor(
        request=request, player_adapter=player_adapter_mock_1,
        console_adapter=console_adapter_mock, team_adapter=team_adapter_mock)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == [{
        'entity_id': 'fe5c6aea-6928-4008-a08d-f90440983dd4',
        'name': 'brazucas4',
        'nickname': 'Zyzukab',
        'photo': None,
        'tag_name': 'tag#3'
    }]


query_params2 = {
    'player_id': 'gluglu',
    'console_id': '2',
    'game_id': 'schrubles'
}


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_players_by_console_game_empty(boto3):
    request = GetMyTeamsByGameRequestModel(query_params2)
    interactor = GetMyTeamsByGameInteractor(
        request=request, player_adapter=player_adapter_mock_2,
        console_adapter=console_adapter_mock, team_adapter=team_adapter_mock)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == []
