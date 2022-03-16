from playerstars_interactors import (
    GetPlayerTournamentsInteractor, GetPlayerTournamentsRequestModel
)
from unittest.mock import MagicMock
from tests.player.player_utils import tournament, player1
from playerstars_interactors.tournament.tournament_detail_util import (
    get_winners, get_members_data, format_tournament
)
from tests.util_tests import team_1
from playerstars_domain import (
    TournamentMemberStatus, PlayerTournament, TournamentMember,
    TournamentStatus, Game, Console, DuelMemberType
)
from datetime import datetime


def get_interactor(status=None, player_id='schrubles'):
    request = GetPlayerTournamentsRequestModel(player_id, status)
    player_adapter = MagicMock()
    team_adapter = MagicMock()
    team_tournament_adapter = MagicMock()
    player_tournament_adapter = MagicMock(list_all=MagicMock())
    interactor = GetPlayerTournamentsInteractor(
        request, player_adapter, team_adapter, team_tournament_adapter,
        player_tournament_adapter, 500
    )
    return interactor


def test_get_individual_tournaments():
    interactor = get_interactor()
    tournament.is_member = MagicMock(return_value=True)
    interactor.player_tournament_adapter = MagicMock(
        list_all=MagicMock(return_value=[tournament]))
    indv_tourneys = interactor.get_individual_tournaments()
    assert indv_tourneys
    tournament.is_member.assert_called_with('schrubles')


def test_get_team_tournaments():
    tournament.is_member = MagicMock(return_value=True)

    interactor = get_interactor(
        player_id="8f547626-d1f7-49a3-ba2e-eb7a7504ad22")
    interactor.team_adapter = MagicMock(
        get_by_id=MagicMock(return_value=team_1))
    interactor.team_tournament_adapter = MagicMock(
        list_all=MagicMock(return_value=[tournament]))

    team_tourneys = interactor.get_team_tournaments()

    assert team_tourneys
    interactor.team_tournament_adapter.list_all.assert_called_once()
    assert interactor.team_adapter.get_by_id.call_count == 1
    interactor.team_adapter.get_by_id.assert_called_with(
        tournament.members[0].member_id)


def test_format_tournament():
    interactor = get_interactor()
    interactor.player_adapter = MagicMock(
        get_by_id=MagicMock(return_value=player1))
    interactor.get_members_data = MagicMock(return_value=[])
    interactor.get_winners = MagicMock(return_value=[])
    formated_tourney = format_tournament(
        tournament, DuelMemberType.PLAYER, interactor.player_adapter,
        interactor.tournament_review_time)
    assert formated_tourney


def test_get_members_data():
    interactor = get_interactor()
    member_list = get_members_data(
        tournament.members, interactor.player_adapter)
    assert member_list


def test_get_winners():
    assert not get_winners(tournament)


def test_run():
    interactor = get_interactor()
    interactor.get_individual_tournaments = MagicMock()
    interactor.get_team_tournaments = MagicMock()
    response = interactor.run()
    assert response()
    interactor.get_individual_tournaments.assert_called_once()
    interactor.get_team_tournaments.assert_called_once()


def test_flux():
    tourney_member_1 = TournamentMember(
        member_id='schrubles1234',
        status=TournamentMemberStatus.ACCEPTED
    )

    tourney_member_2 = TournamentMember(
        member_id='schrubles5678',
        status=TournamentMemberStatus.OWNER
    )

    tournament_list = [
        PlayerTournament(
            game=Game(
                name='LOL',
                entity_id='6411df96-799b-4e6d-84f6-f277cff016e7',
                logo_path='/images/lol.png'),
            console=Console(
                name='PC',
                entity_id='c5a73eaa-9c87-4c32-9a49-05125fb79387',
                logo_path='images/LOL.jpg'),
            award_first_place_perc=70,
            award_second_place_perc=20,
            award_third_place_perc=10,
            price_to_enter=30,
            member_amount=16,
            level_duration=120,
            levels_per_day=2,
            start_datetime=datetime(2020, 7, 23, 18, 34, 6, 138139),
            members=[tourney_member_1, tourney_member_2],
            status=TournamentStatus.WAITING_START,
            creation_datetime=datetime(2020, 7, 21, 18, 34, 6, 138139)
        )
    ]
    interactor = get_interactor(player_id='schrubles5678',
                                status={'status': 'oie-tchau'})
    interactor.player_tournament_adapter = MagicMock(
        list_all=MagicMock(return_value=tournament_list),
        filter=MagicMock(return_value=tournament_list))
    response = interactor.run()
    assert interactor.request.status == ['oie', 'tchau']
    assert isinstance(response(), list)
    assert len(response()) == 1
    assert response()[0]['tournament_id'] == tournament_list[0].entity_id
    assert response()[0]['tournament_status'] == 'WAITING_START'
