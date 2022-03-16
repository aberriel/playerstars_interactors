from unittest.mock import patch, MagicMock
from playerstars_interactors import (
    GetAllPlayerDuelByStatusInteractor,
    GetAllPlayerDuelByStatusRequestModel,
    GetAllPlayerDuelByStatusError
)
from tests.player.player_utils import (
    duel1, duel2, duel3, duel4, duel1_lobby,
    duel_status_dueling, duel5, player1
)
import pytest


duel_adapter = MagicMock(list_all=MagicMock(
    return_value=[duel1, duel2, duel3, duel1_lobby]))
player_adapter = MagicMock(get_by_id=MagicMock(return_value=player1))
team_adapter = MagicMock()


# noinspection PyUnusedLocal,PyUnusedLocal
@patch('playerstars_interactors.player.get_duels.'
       'GetAllPlayerDuelByStatusInteractor.get_opponent_nickname',
       return_value='Zyzukab')
def test_get_player_duel_by_status(mock):
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436515-d1f7-49a3-ba2e-eb7a7504ad22', 'LOBBY')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter, team_adapter, player_adapter)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == [{
        'duel_id': '66225276-03b5-487c-9b27-8e91e0fe1e12',
        'gameImage': '/images/csgo.png',
        'gameName': 'CS:GO',
        'consoleName': 'PC',
        'members': 2,
        'start_date_time': '16/12/1986 15:40:08',
        'star_type': 'RED_STAR',
        'bet': 15,
        'reward': 30,
        'winner': None,
        'matchTitle': 'Individual',
        'matchType': 'duel',
        'ranking': [],
        'opponent_type': 'player',
        'opponent_name': 'Zyzukab',
        'status': 'LOBBY',
        'opponent_team_name': None,
        'team_name': None
    }]


def test_get_player_duel_by_status_dueling():
    duel_adapter.list_all = MagicMock(
        return_value=[duel1, duel2, duel3, duel4, duel_status_dueling])
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436515-d1f7-49a3-ba2e-eb7a7504ad22', 'DUELING')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter, team_adapter, player_adapter)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == [{
        'duel_id': '66225276-03b5-487c-9b27-8e91e0fe1e12',
        'gameImage': '/images/csgo.png',
        'gameName': 'CS:GO',
        'consoleName': 'PC',
        'members': 2,
        'start_date_time': '16/12/1986 15:40:08',
        'star_type': 'RED_STAR',
        'bet': 15,
        'reward': 30,
        'winner': None,
        'matchTitle': 'Individual',
        'matchType': 'duel',
        'ranking': [],
        'opponent_type': 'player',
        'opponent_name': 'player1',
        'status': 'DUELING',
        'opponent_team_name': None,
        'team_name': None
    }]


def test_get_player_duel_by_status_not_existing():
    duel_adapter.list_all = MagicMock(return_value=[duel1, duel2, duel3])
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436515-d1f7-49a3-ba2e-eb7a7504ad22', 'DUELING')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter, team_adapter, player_adapter)
    response = interactor.run()
    assert response == list()


def test_get_player_duel_by_status_more_than_one_dueling():
    duel_adapter.list_all = MagicMock(
        return_value=[duel1, duel2, duel3, duel4, duel_status_dueling,
                      duel_status_dueling])
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436515-d1f7-49a3-ba2e-eb7a7504ad22', 'DUELING')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter, team_adapter, player_adapter)
    with pytest.raises(GetAllPlayerDuelByStatusError) as excinfo:
        interactor.run()
    assert "tem mais de um duelo " \
           "acontecendo ao mesmo tempo" in str(excinfo.value)


def test_get_player_duel_by_status_player_not_in_duel():
    duel_adapter.list_all = MagicMock(return_value=[duel1, duel2])
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436515-d1f7-49a3-ba2e-eb7a7504ad21', 'LOBBY')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter, team_adapter, player_adapter)
    response = interactor.run()
    assert response == list()


@patch('playerstars_interactors.player.get_duels.'
       'GetAllPlayerDuelByStatusInteractor.get_opponent_nickname',
       return_value='Zegzo')
# @patch('playerstars_interactors.player.get_duels.'
#        'GetAllPlayerDuelByStatusInteractor.get_winner_name',
#        return_value='Tigor')
def test_get_player_duel_by_status_dueling_and_finished(mock1):
    duel_adapter.list_all = MagicMock(
        return_value=[duel1, duel2, duel3, duel4, duel5])
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436516-d1f7-49a3-ba2e-eb7a7504ad22',
        'DUELING-FINISHED_BY_VICTORY')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter, team_adapter, player_adapter)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == [
        {
            'bet': 15,
            'consoleName': 'PC',
            'duel_id': '66225276-03b5-487c-9b27-8e91e0fe1e12',
            'gameImage': '/images/csgo.png',
            'gameName': 'CS:GO',
            'matchTitle': 'Individual',
            'matchType': 'duel',
            'members': 2,
            'opponent_name': 'Zegzo',
            'opponent_type': 'player',
            'ranking': [],
            'reward': 30,
            'star_type': 'RED_STAR',
            'start_date_time': '16/12/1986 15:40:08',
            'status': 'FINISHED_BY_VICTORY',
            'opponent_team_name': None,
            'team_name': None,
            'winner': {
                'i_am_winner': False,
                'winner_id': "56436515-d1f7-49a3-ba2e-eb7a7504ad22"
            }
        },
        {
            'bet': 90,
            'consoleName': 'PC',
            'duel_id': '55d2737c-d7ac-4084-9bcf-d42954e1938c',
            'gameImage': '/images/lol.png',
            'gameName': 'LOL',
            'matchTitle': 'Individual',
            'matchType': 'duel',
            'members': 2,
            'opponent_name': 'Zegzo',
            'opponent_type': 'player',
            'ranking': [],
            'reward': 180,
            'star_type': 'GOLDEN_STAR',
            'start_date_time': '21/02/1558 15:40:08',
            'status': 'FINISHED_BY_VICTORY',
            'opponent_team_name': None,
            'team_name': None,
            'winner': {
                'i_am_winner': True,
                'winner_id': '7e436516-d1f7-49a3-ba2e-eb7a7504ad22'
            }
        },
        {
            'bet': 90,
            'consoleName': 'PC',
            'duel_id': '65d2737c-d7ac-4084-9bcf-d42954e1938c',
            'gameImage': '/images/lol.png',
            'gameName': 'LOL',
            'matchTitle': 'Individual',
            'matchType': 'duel',
            'members': 2,
            'opponent_name': 'Zegzo',
            'opponent_type': 'player',
            'ranking': [],
            'reward': 180,
            'star_type': 'GOLDEN_STAR',
            'start_date_time': '21/02/1558 15:40:08',
            'status': 'FINISHED_BY_VICTORY',
            'opponent_team_name': None,
            'team_name': None,
            'winner': {
                'i_am_winner': True,
                'winner_id': '7e436516-d1f7-49a3-ba2e-eb7a7504ad22'
            }
        }]


def test_get_player_duel_by_status_win():
    duel_adapter.list_all = MagicMock(return_value=[duel1, duel2, duel3])
    request = GetAllPlayerDuelByStatusRequestModel(
        '7e436516-d1f7-49a3-ba2e-eb7a7504ad22', 'FINISHED_BY_VICTORY')
    interactor = GetAllPlayerDuelByStatusInteractor(
        request, duel_adapter, team_adapter, player_adapter)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == [{
        'bet': 15,
        'consoleName': 'PC',
        'duel_id': '66225276-03b5-487c-9b27-8e91e0fe1e12',
        'gameImage': '/images/csgo.png',
        'gameName': 'CS:GO',
        'matchTitle': 'Individual',
        'matchType': 'duel',
        'members': 2,
        'opponent_type': 'player',
        'opponent_name': 'player1',
        'start_date_time': '16/12/1986 15:40:08',
        'ranking': [],
        'reward': 30,
        'star_type': 'RED_STAR',
        'status': 'FINISHED_BY_VICTORY',
        'opponent_team_name': None,
        'team_name': None,
        'winner': {
            "i_am_winner": False,
            "winner_id": "56436515-d1f7-49a3-ba2e-eb7a7504ad22",
        }
    }, {
        'bet': 90,
        'consoleName': 'PC',
        'duel_id': '55d2737c-d7ac-4084-9bcf-d42954e1938c',
        'gameImage': '/images/lol.png',
        'gameName': 'LOL',
        'matchTitle': 'Individual',
        'matchType': 'duel',
        'members': 2,
        'opponent_type': 'player',
        'opponent_name': 'player1',
        'start_date_time': '21/02/1558 15:40:08',
        'ranking': [],
        'reward': 180,
        'star_type': 'GOLDEN_STAR',
        'status': 'FINISHED_BY_VICTORY',
        'opponent_team_name': None,
        'team_name': None,
        'winner': {
            "i_am_winner": True,
            "winner_id": "7e436516-d1f7-49a3-ba2e-eb7a7504ad22"
        }
    }]
