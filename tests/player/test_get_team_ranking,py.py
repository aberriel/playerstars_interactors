from playerstars_interactors import (
    GetTeamsRankingRequestModel, GetTeamsRankingInteractor
)
from unittest.mock import MagicMock
from tests.util_tests import team_list


params = {
    'game_id': 'f16c9f9a-9b22-4884-b890-bcc3294e91be'
}
team_adapter = MagicMock(filter=MagicMock(return_value=team_list))


def test_get_team_ranking():
    request = GetTeamsRankingRequestModel(
        params=params, playerd_id='q1w2e3abc')
    interactor = GetTeamsRankingInteractor(request, team_adapter)
    data, range_data = interactor.run()
    assert range_data.initial == 0
    assert range_data.final == 4
    assert range_data.total == 4
    assert range_data.unit == 'ranking'
    assert data == [{
        'entity_id': 'fe5c6aea-6928-4008-a08d-f90440983dd3',
        'is_member': False,
        'position': 1,
        'team_logo': None,
        'team_name': 'brazucas3',
        'victories': 3,
        'elo_rating': 1500
    }, {
        'entity_id': 'fe5c6aea-6928-4008-a08d-f90440983dd4',
        'is_member': True,
        'position': 1,
        'team_logo': None,
        'team_name': 'brazucas4',
        'victories': 3,
        'elo_rating': 1500
    }, {
        'entity_id': 'fe5c6aea-6928-4008-a08d-f90440983dd4',
        'is_member': False,
        'position': 2,
        'team_logo': None,
        'team_name': 'brazucas1',
        'victories': 0,
        'elo_rating': 1500
    }, {
        'entity_id': 'fe5c6aea-6928-4008-a08d-f90440983dd2',
        'is_member': False,
        'position': 2,
        'team_logo': None,
        'team_name': 'brazucas2',
        'victories': 0,
        'elo_rating': 1500
    }]
