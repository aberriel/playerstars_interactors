from playerstars_interactors.tournament.post_tournament_start import (
    PostTournamentStartAdapters,
    PostTournamentStartInteractor, PostTournamentStartRequestModel
)
from playerstars_domain import (
    TournamentStatus, CoinType, DuelStatus, DuelType, NotificationType
)
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from playerstars_domain import DuelMemberType as MemberType
import pytz

time = datetime.now()


def get_interactor():
    mock_request = MagicMock()
    mock_adapters = MagicMock()
    return PostTournamentStartInteractor(
        request=mock_request,
        adapters=mock_adapters,
        time_to_finish=time)


def test_save_tournament():
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    interactor.save_tournament()
    interactor.tournament.set_adapter.assert_called_once_with(
        interactor.adapters.player_tournament_adapter)
    interactor.tournament.save.assert_called_once()


def test_cancel_tournament():
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    interactor.save_tournament = MagicMock()
    interactor.cancel_tournament()
    assert interactor.tournament.status == TournamentStatus.CANCELED
    interactor.save_tournament.assert_called_once()


def test_set_tournament_started():
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    interactor.save_tournament = MagicMock()
    interactor.set_tournament_started()
    assert interactor.tournament.status == TournamentStatus.PHASE1
    interactor.save_tournament.assert_called_once()


def test_get_console():
    interactor = get_interactor()
    interactor.get_console('123')
    interactor.adapters.console_adapter.get_by_id.\
        assert_called_once_with('123')


def test_get_game():
    interactor = get_interactor()
    console = MagicMock()
    interactor.get_game(console, '12324')
    console.find_game_by_id.assert_called_once_with('12324')


def test__prepare_console_to_duel():
    interactor = get_interactor()
    console_data = MagicMock()
    console = interactor._prepare_console_to_duel(console_data)
    assert console
    assert console_data.games == []


@patch('playerstars_interactors.tournament.post_tournament_start.Duel')
@patch('playerstars_interactors.tournament.post_tournament_start.datetime')
def test_create_duel(time_mock, duel_mock):
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    interactor.get_console = MagicMock()
    interactor.get_game = MagicMock()
    interactor._prepare_console_to_duel = MagicMock()
    duel = interactor.create_duel('challenger', 'challenged')
    assert duel
    duel_mock.assert_called_once_with(
        challenger='challenger',
        challenged='challenged',
        game=interactor.get_game('123'),
        console=interactor._prepare_console_to_duel(),
        star_type=CoinType.GOLDEN_STAR,
        bet_size=interactor.tournament.star_amount,
        member_type=MemberType.PLAYER,
        duel_type=DuelType.CHAMPIONSHIP,
        participants=2,
        challenger_confirmation=True,
        challenged_confirmation=True,
        challenged_accept=True,
        creation_datetime=time_mock.utcnow().replace(tzinfo=pytz.utc),
        time_start=time_mock.utcnow().replace(tzinfo=pytz.utc),
        time_to_finish_duel=interactor.time_to_finish,
        time_to_accept_invitation=1,
        status=DuelStatus.DUELING
    )


member1, member2 = MagicMock(), MagicMock()


@patch('playerstars_interactors.tournament.post_tournament_start.'
       'PostTournamentStartInteractor.send_duel_invite',
       return_value=MagicMock())
@patch('playerstars_interactors.tournament.post_tournament_start.'
       'random.shuffle', return_value=[member1, member2])
def test_create_duels(mock_shuffle, send_mock):
    duel = MagicMock()
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    interactor.tournament.members = [member1, member2]
    interactor.create_duel = MagicMock(return_value=duel)
    interactor.create_duels()
    duel.set_adapter.assert_called_once_with(interactor.adapters.duel_adapter)
    duel.save.assert_called_once()
    send_mock.assert_has_calls([
        call(member1.member_id, member2.member_id, duel),
        call(member2.member_id, member1.member_id, duel)
    ])


def test_check_accepted_members_amount():
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    interactor.tournament.member_amount = 2
    interactor.tournament.confirmed_members = 2
    assert interactor.check_accepted_members_amount()


def test_get_tournament_adapter():
    interactor = get_interactor()
    interactor.request.member_type = MemberType.PLAYER
    assert interactor.get_tournament_adapter() == \
        interactor.adapters.player_tournament_adapter


@patch('playerstars_interactors.tournament.post_tournament_start.'
       'invite_member', return_value=None)
@patch('playerstars_interactors.tournament.post_tournament_start.'
       'report_failed_invites')
def test_send_duel_invite(mock_report, mock_invite):
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    member1, member2, duel = MagicMock(), MagicMock(), MagicMock()
    interactor.send_duel_invite(member1, member2, duel)
    adversary = interactor.adapters.player_adapter.get_by_id()
    mock_invite.assert_called_once_with(
        member=member1,
        notification_type=NotificationType.DUEL_INVITE,
        duel=duel,
        tournament=interactor.tournament,
        notification_adapter=interactor.adapters.notificationgql_adapter,
        complement=adversary.user.nickname,
        logo_path=interactor.tournament.game.logo_path
    )


@patch('playerstars_interactors.tournament.post_tournament_start.'
       'invite_member', return_value='123')
@patch('playerstars_interactors.tournament.post_tournament_start.'
       'report_failed_invites')
def test_send_duel_invite_failed(mock_report, mock_invite):
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    member1, member2, duel = MagicMock(), MagicMock(), MagicMock()
    interactor.send_duel_invite(member1, member2, duel)
    adversary = interactor.adapters.player_adapter.get_by_id()
    mock_invite.assert_called_once_with(
        member=member1,
        notification_type=NotificationType.DUEL_INVITE,
        duel=duel,
        tournament=interactor.tournament,
        notification_adapter=interactor.adapters.notificationgql_adapter,
        complement=adversary.user.nickname,
        logo_path=interactor.tournament.game.logo_path
    )
    mock_report.assert_called_once_with(
        tournament_id=interactor.tournament.entity_id,
        failed_invites=['123'],
        logger=interactor.logger,
        _type='duel invites'
    )


@patch('playerstars_interactors.tournament.post_tournament_start.'
       'send_invites', return_value=['123', '456'])
@patch('playerstars_interactors.tournament.post_tournament_start.'
       'report_failed_invites')
def test_send_cancel_notification(mock_report, mock_invite):
    interactor = get_interactor()
    interactor.tournament = MagicMock()
    interactor.send_cancel_notifications()
    mock_invite.assert_called_once_with(
        players=interactor.tournament.members,
        tournament=interactor.tournament,
        notification_adapter=interactor.adapters.notificationgql_adapter,
        logo_path=interactor.tournament.game.logo_path,
        notification_type=NotificationType.CHAMPIONSHIP_CANCEL
    )
    mock_report.assert_called_once_with(
        tournament_id=interactor.tournament.entity_id,
        failed_invites=['123', '456'],
        logger=interactor.logger,
        _type='cancel notifications'
    )


def test_run_sufficient_members():
    interactor = get_interactor()
    interactor.get_tournament_adapter = MagicMock()
    interactor.check_accepted_members_amount = MagicMock()
    interactor.create_duels = MagicMock()
    interactor.set_tournament_started = MagicMock()
    interactor.cancel_tournament = MagicMock()
    interactor.send_cancel_notifications = MagicMock()
    response = interactor.run()
    assert response
    interactor.get_tournament_adapter.assert_called_once()
    interactor.check_accepted_members_amount.assert_called_once()
    interactor.create_duels.assert_called_once()
    interactor.set_tournament_started.assert_called_once()
    assert interactor.cancel_tournament.call_count == 0
    assert interactor.send_cancel_notifications.call_count == 0


def test_run_insufficient_members():
    interactor = get_interactor()
    interactor.get_tournament_adapter = MagicMock()
    interactor.check_accepted_members_amount = MagicMock(return_value=False)
    interactor.create_duels = MagicMock()
    interactor.set_tournament_started = MagicMock()
    interactor.cancel_tournament = MagicMock()
    interactor.send_cancel_notifications = MagicMock()
    response = interactor.run()
    assert response()
    interactor.get_tournament_adapter.assert_called_once()
    interactor.check_accepted_members_amount.assert_called_once()
    assert interactor.create_duels.call_count == 0
    assert interactor.set_tournament_started.call_count == 0
    interactor.cancel_tournament.assert_called_once()
    interactor.send_cancel_notifications.assert_called_once()


def test_models():
    request = PostTournamentStartRequestModel(
        player_id='schrubles',
        member_type=MemberType.PLAYER,
        data=dict(tournament_id='123')
    )
    assert request
    adapters = PostTournamentStartAdapters(
        MagicMock(), MagicMock(), MagicMock(), MagicMock(),
        MagicMock(), MagicMock(), MagicMock()
    )
    assert adapters
