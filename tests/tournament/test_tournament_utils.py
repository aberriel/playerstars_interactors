from unittest.mock import MagicMock, patch, call

from playerstars_domain import NotificationType
from playerstars_interactors.tournament.tournament_utils import (
    send_invites, invite_member, get_tb,
    failed_invites_count, report_failed_invites, FailedInvite
)


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.tournament_utils.invite_member',
       return_value=None)
def test_send_invites(mock_invite_member):
    tournament = MagicMock()
    new_players = [MagicMock(), MagicMock()]
    adapter = MagicMock()
    notification_type = NotificationType.CHAMPIONSHIP_INVITE_PLAYER
    failed = send_invites(
        players=new_players,
        tournament=tournament,
        logo_path='path',
        notification_adapter=adapter,
        notification_type=notification_type)
    assert failed == []
    mock_invite_member.assert_has_calls([
        call(member=new_players[0],
             tournament=tournament,
             logo_path='path',
             notification_adapter=adapter,
             notification_type=notification_type),
        call(member=new_players[1],
             tournament=tournament,
             logo_path='path',
             notification_adapter=adapter,
             notification_type=notification_type)])


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.tournament_utils.'
       'Notification', side_effect=ValueError('Errou!'))
@patch('playerstars_interactors.tournament.tournament_utils.get_tb')
def test_send_invites_failed(mock_get_tb, mock_notification):
    tournament = MagicMock()
    new_players = [MagicMock()]
    adapter = MagicMock()
    notification_type = NotificationType.CHAMPIONSHIP_INVITE_PLAYER
    failed_invites = send_invites(
        players=new_players,
        tournament=tournament,
        logo_path='path',
        notification_adapter=adapter,
        notification_type=notification_type)
    assert failed_invites == \
        [FailedInvite(new_players[0], 'ValueError', 'Errou!', mock_get_tb())]


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.tournament_utils.'
       'Notification')
@patch('playerstars_interactors.tournament.tournament_utils.'
       'format_complement')
def test_invite_member(mock_format_complement, mock_notification):
    mock_member = MagicMock()
    tournament = MagicMock()
    adapter = MagicMock()
    failed_invites = invite_member(
        mock_member, tournament, 'path', adapter,
        NotificationType.CHAMPIONSHIP_INVITE_PLAYER)
    assert not failed_invites
    mock_format_complement.assert_called_once_with(tournament)
    mock_notification.assert_called_with(
        player_id=mock_member,
        duel_id=None,
        notification_type=NotificationType.CHAMPIONSHIP_INVITE_PLAYER,
        championship_id=tournament.entity_id,
        notification_complement=mock_format_complement(),
        notification_image='path')
    mock_notification().set_adapter.assert_called_with(adapter)
    mock_notification().save.assert_called_once()


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.tournament_utils.'
       'Notification', side_effect=ValueError('Errou!'))
@patch('playerstars_interactors.tournament.tournament_utils.get_tb')
def test_invite_member_raise(mock_get_tb, mock_notification):
    mock_member = MagicMock()
    tournament = MagicMock()
    adapter = MagicMock()
    failed_invites = invite_member(
        mock_member, tournament, 'path', adapter,
        NotificationType.CHAMPIONSHIP_INVITE_PLAYER)

    assert failed_invites == \
        FailedInvite(mock_member, 'ValueError', 'Errou!', mock_get_tb())


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.tournament_utils.'
       'failed_invites_count', return_value=1)
def test_report_failed_invites(mock_failed_invite_count):
    mock_tournament = MagicMock()
    mock_logger = MagicMock()
    mock_failed = MagicMock()

    tournament = mock_tournament
    logger = mock_logger
    failed_invites = [mock_failed]
    report_failed_invites(
        tournament_id=tournament.entity_id,
        failed_invites=failed_invites,
        logger=logger)

    mock_failed_invite_count.assert_called_once()
    mock_logger.error.assert_has_calls([
        call(f'1 invites failed on tournament {mock_tournament.entity_id}:'),
        call(f'Failed invite:\t'
             f'member_id: {mock_failed.member}\t'
             f'error: {mock_failed.exception}\t'
             f'Message: {mock_failed.message}\t'
             f'Traceback: {mock_failed.traceback}')
    ])


# noinspection PyProtectedMember
@patch('playerstars_interactors.tournament.tournament_utils.'
       'failed_invites_count',
       return_value=0)
def test_report_failed_invites_none(mock_failed_invite_count):
    mock_tournament = MagicMock()
    mock_logger = MagicMock()
    mock_failed = MagicMock()

    tournament = mock_tournament
    logger = mock_logger
    failed_invites = [mock_failed]
    assert not report_failed_invites(
        tournament_id=tournament.entity_id,
        failed_invites=failed_invites,
        logger=logger)


@patch('playerstars_interactors.tournament.tournament_utils.sys')
@patch('playerstars_interactors.tournament.tournament_utils.'
       'format_exception', return_value=['1', '2'])
def test_get_tb(mock_format_exception, mock_sys):
    mock_etype, mock_value, mock_traceback = (
        MagicMock(), MagicMock(), MagicMock())
    mock_sys.exc_info = MagicMock(return_value=(
        mock_etype, mock_value, mock_traceback))

    result = get_tb()

    mock_sys.exc_info.assert_called_once()
    mock_format_exception.assert_called_with(
        mock_etype, mock_value, mock_traceback)
    assert result == '1\n2'


def test_post_invite_new_players__failed_count():
    failed_invites = list(range(42))
    result = failed_invites_count(failed_invites)
    assert result == 42
