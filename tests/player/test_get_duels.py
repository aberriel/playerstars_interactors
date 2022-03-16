from playerstars_interactors import \
    GetAllPlayerDuelByStatusInteractor, GetAllPlayerDuelByStatusRequestModel
from tests.player.player_utils import duel1, duel2, duel3, duel4
from unittest.mock import MagicMock, patch
from tests.util_tests import \
    make_duel_team_golden, make_duel_team_red, team_get_duels, player_2
from playerstars_domain import DuelStatus
from datetime import datetime


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


expected_response = [
    {
        'duel_id': '325c47c4-1cc0-49c7-8b85-a35f032cbf25',
        'gameImage': '/images/lol.png',
        'gameName': 'LOL',
        'consoleName': 'PC',
        'members': 2,
        'start_date_time': '10/01/2020 15:40:08',
        'star_type': 'GOLDEN_STAR',
        'bet': 7,
        'reward': 14,
        'winner': None,
        'matchTitle': 'Individual',
        'matchType': 'duel',
        'ranking': [],
        'opponent_type': 'player',
        'status': 'CANCELED_BY_INCONSISTENT_RESULT',
        'opponent_name': 'Zyzukab',
        'opponent_team_name': None,
        'team_name': None
    },
    {
        'duel_id': '66225276-03b5-487c-9b27-8e91e0fe1e12',
        'gameImage': '/images/csgo.png',
        'gameName': 'CS:GO',
        'consoleName': 'PC',
        'members': 2,
        'start_date_time': '16/12/1986 15:40:08',
        'star_type': 'RED_STAR',
        'bet': 15,
        'reward': 30,
        'winner': {
            'i_am_winner': False,
            'winner_id': '56436515-d1f7-49a3-ba2e-eb7a7504ad22',
        },
        'matchTitle': 'Individual',
        'matchType': 'duel',
        'ranking': [],
        'opponent_type': 'player',
        'status': 'FINISHED_BY_VICTORY',
        'opponent_name': 'Zyzukab',
        'opponent_team_name': None,
        'team_name': None
    }, {
        "duel_id": "f13eb50c",
        "gameImage": "http://s3.aws.com/nfs.jpg",
        "gameName": "Need for Speed",
        "consoleName": "Xbox One",
        "members": 2,
        "start_date_time": "16/12/1986 15:40:08",
        "star_type": "GOLDEN_STAR",
        "bet": 3,
        "reward": 6,
        "winner": None,
        "matchTitle": "Entre Times",
        "matchType": "duel",
        "ranking": [],
        "opponent_type": "team",
        "status": "FINISHED_BY_VICTORY",
        'opponent_name': None,
        'opponent_team_name': 'brazucas4',
        'team_name': 'brazucas4'
    }, {
        "duel_id": "f13eb50c",
        "gameImage": "http://s3.aws.com/nfs.jpg",
        "gameName": "Need for Speed",
        "consoleName": "Xbox One",
        "members": 2,
        "start_date_time": "16/12/1986 15:40:08",
        "star_type": "RED_STAR",
        "bet": 3,
        "reward": 6,
        "winner": None,
        "matchTitle": "Entre Times",
        "matchType": "duel",
        "ranking": [],
        "opponent_type": "team",
        "status": "FINISHED_BY_VICTORY",
        'opponent_name': None,
        'opponent_team_name': 'brazucas4',
        'team_name': 'brazucas4'
    }, {
        'duel_id': '55d2737c-d7ac-4084-9bcf-d42954e1938c',
        'gameImage': '/images/lol.png',
        'gameName': 'LOL',
        'consoleName': 'PC',
        'members': 2,
        'start_date_time': '21/02/1558 15:40:08',
        'star_type': 'GOLDEN_STAR',
        'bet': 90,
        'reward': 180,
        'winner': {
            'i_am_winner': True,
            'winner_id': '7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
        },
        'matchTitle': 'Individual',
        'matchType': 'duel',
        'ranking': [],
        'opponent_type': 'player',
        'status': 'FINISHED_BY_VICTORY',
        'opponent_name': 'Zyzukab',
        'opponent_team_name': None,
        'team_name': None
    }
]

duel_team_gold = make_duel_team_golden()
duel_team_gold.status = DuelStatus.FINISHED_BY_VICTORY
duel_team_gold.time_start = datetime(1986, 12, 16, 15, 40, 8)
duel_team_red = make_duel_team_red()
duel_team_red.status = DuelStatus.FINISHED_BY_VICTORY
duel_team_red.time_start = datetime(1986, 12, 16, 15, 40, 8)
duel_adapter_mock = MagicMock(
    list_all=MagicMock(return_value=[
        duel1, duel2, duel3, duel4, duel_team_gold, duel_team_red]))

duel_adapter_mock_empty = MagicMock(
    list_all=MagicMock(return_value=[]))
team_adater_mock = MagicMock(get_by_id=MagicMock(return_value=team_get_duels))
player_adapter_mock = MagicMock(get_by_id=MagicMock(return_value=player_2))


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_all_player_duels(boto_mock):
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436516-d1f7-49a3-ba2e-eb7a7504ad22')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter_mock, team_adater_mock, player_adapter_mock)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == expected_response


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_all_player_duels_has_no_duel(boto_mock):
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436516-d1f7-49a3-ba2e-eb7a7504ad22')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter_mock_empty,
        team_adater_mock, player_adapter_mock)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == []
