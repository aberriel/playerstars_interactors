from playerstars_interactors.tournament.post_invite_answer import (
    PostInviteAnswerError, PostInviteAnswerInteractor,
    PostInviteAnswerRequestModel, PostInviteAnswerAdapters
)
from playerstars_domain import DuelMemberType as MemberType
from playerstars_domain import TournamentMemberStatus
from unittest.mock import MagicMock
from tests.util_tests import player_1, team_1
import pytest
from tests.player.player_utils import tournament


def get_interactor():
    request = PostInviteAnswerRequestModel(
        player_id='schrubles1234',
        team_id='team1234',
        member_type=MemberType.PLAYER,
        data=dict(tournament_id="tournament1234"),
        answer="ACCEPT"
    )
    adapters = PostInviteAnswerAdapters(
        player_adapter=MagicMock(),
        team_adapter=MagicMock(),
        player_tournament_adapter=MagicMock(),
        team_tournament_adapter=MagicMock()
    )
    interactor = PostInviteAnswerInteractor(
        request=request,
        adapters=adapters
    )
    return interactor


def test_get_player():
    interactor = get_interactor()
    player = interactor.get_player('1234')
    assert player
    interactor.adapters.player_adapter.get_by_id.\
        assert_called_once_with('1234')


def test_get_team():
    interactor = get_interactor()
    team = interactor.get_team('1234')
    assert team
    interactor.adapters.team_adapter.get_by_id.\
        assert_called_once_with('1234')


def test_subtract_player_stars():
    interactor = get_interactor()
    interactor.subtract_player_stars(player_1, 20)
    assert player_1.golden_star_balance == 80


def test_check_player_stars():
    interactor = get_interactor()
    interactor.get_player = MagicMock(return_value=player_1)
    interactor.subtract_player_stars = MagicMock()
    assert not interactor.check_player_stars(15)
    interactor.get_player.assert_called_once_with('schrubles1234')
    interactor.subtract_player_stars.assert_called_once_with(player_1, 15)


def test_check_player_stars_raises():
    interactor = get_interactor()
    interactor.get_player = MagicMock(return_value=player_1)
    interactor.subtract_player_stars = MagicMock()
    with pytest.raises(PostInviteAnswerError) as excinfo:
        interactor.check_player_stars(15000)
    assert "Player cannot accept invite with less stars than the price" \
           in str(excinfo.value)


def test_check_team_stars():
    interactor = get_interactor()
    interactor.get_team = MagicMock(return_value=team_1)
    interactor.get_player = MagicMock(return_value=player_1)
    interactor.subtract_player_stars = MagicMock()
    assert not interactor.check_team_stars(15)
    interactor.get_player.assert_called_once_with(
        '8f547626-d1f7-49a3-ba2e-eb7a7504ad22')
    interactor.get_team.assert_called_once_with('team1234')
    interactor.subtract_player_stars.assert_called_once_with(player_1, 15)


def test_check_team_stars_raises():
    interactor = get_interactor()
    interactor.get_player = MagicMock(return_value=player_1)
    interactor.get_player = MagicMock(return_value=player_1)
    interactor.subtract_player_stars = MagicMock()
    with pytest.raises(PostInviteAnswerError) as excinfo:
        interactor.check_team_stars(15000)
    assert "Team cannot accept invite when the captain has less stars" \
           " than the price is" in str(excinfo.value)


def test_check_stars():
    interactor = get_interactor()
    interactor.check_player_stars = MagicMock()
    assert not interactor.check_stars(145)
    interactor.check_player_stars.assert_called_once_with(145)


def test_check_answer():
    interactor = get_interactor()
    assert interactor.check_answer()
    interactor.request.answer = False
    assert not interactor.check_answer()


def test_refuse_invite():
    interactor = get_interactor()
    assert not interactor.refuse_invite(tournament)
    assert len([x for x in tournament.members
                if x.status == TournamentMemberStatus.REJECTED]) == 1


def test_accept_invite():
    interactor = get_interactor()
    assert not interactor.accept_invite(tournament)
    assert len([x for x in tournament.members
                if x.status == TournamentMemberStatus.REJECTED]) == 0


def test_run():
    interactor = get_interactor()
    interactor.adapters.player_tournament_adapter = MagicMock(
        get_by_id=MagicMock(return_value=tournament))
    interactor.check_answer = MagicMock()
    interactor.check_stars = MagicMock()
    interactor.accept_invite = MagicMock()
    response = interactor.run()
    assert response
    interactor.check_answer.assert_called_once()
    interactor.check_stars.assert_called_once_with(
        tournament.price_to_enter)
    interactor.accept_invite.assert_called_once_with(tournament)
    interactor.adapters.player_tournament_adapter.save.assert_called_once()
    assert isinstance(response(), dict)


def test_run_refuse():
    interactor = get_interactor()
    interactor.request.answer = 'REJECT'
    interactor.adapters.player_tournament_adapter = MagicMock(
        get_by_id=MagicMock(return_value=tournament))
    interactor.check_answer = MagicMock(return_value=False)
    interactor.check_stars = MagicMock()
    interactor.refuse_invite = MagicMock()
    response = interactor.run()
    assert response
    interactor.check_answer.assert_called_once()
    interactor.refuse_invite.assert_called_once_with(tournament)
    interactor.adapters.player_tournament_adapter.save.assert_called_once()
    assert isinstance(response(), dict)
