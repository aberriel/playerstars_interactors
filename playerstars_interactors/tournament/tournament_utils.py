from collections import namedtuple
from playerstars_adapters import NotificationAdapter
from playerstars_domain import Notification, Tournament, NotificationType, Duel
from traceback import format_exception

import sys

FailedInvite = namedtuple('FailedInvite',
                          'member, exception, message, traceback')


def send_invites(players,
                 tournament: Tournament,
                 logo_path: str,
                 notification_adapter: NotificationAdapter,
                 notification_type: NotificationType):
    failed_invites = list()
    for player in players:
        failed = invite_member(
            member=player,
            tournament=tournament,
            logo_path=logo_path,
            notification_adapter=notification_adapter,
            notification_type=notification_type)
        if failed:
            failed_invites.append(failed)
    return failed_invites


def invite_member(member,
                  tournament: Tournament,
                  logo_path: str,
                  notification_adapter: NotificationAdapter,
                  notification_type: NotificationType,
                  complement: str = None,
                  duel: Duel = None):
    try:
        _complement = complement or format_complement(tournament)
        notification = Notification(
            player_id=member,
            notification_type=notification_type,
            duel_id=duel.entity_id if duel else None,
            championship_id=tournament.entity_id,
            notification_complement=_complement,
            notification_image=logo_path)
        notification.set_adapter(notification_adapter)
        notification.save()

    except Exception as exc:
        return FailedInvite(
            member, exc.__class__.__name__, str(exc), get_tb())


def format_complement(tournament):
    return tournament.creation_datetime.strftime(
        'Inicio: %d/%m/%Y - %H:%M')


def get_tb():
    etype, value, traceback = sys.exc_info()
    tb = format_exception(etype, value, traceback)
    return '\n'.join(tb)


def failed_invites_count(failed_invites):
    return len(failed_invites)


def report_failed_invites(
        tournament_id, failed_invites, logger, _type='invites'):
    num_fails = failed_invites_count(failed_invites)
    if num_fails == 0:
        return

    logger.error(f'{num_fails} {_type} failed on '
                 f'tournament {tournament_id}:')
    for failed_invite in failed_invites:
        msg = f'Failed invite:\t' \
            f'member_id: {failed_invite.member}\t' \
            f'error: {failed_invite.exception}\t' \
            f'Message: {failed_invite.message}\t' \
            f'Traceback: {failed_invite.traceback}'
        logger.error(msg)
