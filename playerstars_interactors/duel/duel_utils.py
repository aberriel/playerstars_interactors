from playerstars_adapters import NotificationAdapter
from playerstars_domain import (
    Duel,
    DuelMemberType,
    GamePoints,
    Notification,
    NotificationType,
    Player,
    Team)
from playerstars_domain.player.elo import Elo
from playerstars_interactors.notification.notification_utils import \
    SaveNotificationException


def send_notification(duel_data: Duel,
                      player_id: str,
                      notification_type: NotificationType,
                      notification_adapter: NotificationAdapter,
                      logger_instance,
                      complement: str = None,
                      team_id: str = None):
    try:
        notification = Notification(
            player_id=player_id,
            notification_type=notification_type,
            duel_id=duel_data.entity_id,
            team_id=team_id,
            notification_complement=complement,
            notification_image=duel_data.game.logo_path)
        notification.set_adapter(notification_adapter)
        notification.save()
        return notification
    except Exception as exc:
        msg = 'Error during notification save: {}'.format(exc)
        logger_instance.error(msg)
        raise SaveNotificationException(msg)


def send_duel_ongoing_notification(
        duel: Duel,
        challenger,
        challenged,
        notification_adapter: NotificationAdapter,
        logger_instance):
    if duel.member_type == DuelMemberType.PLAYER:
        send_duel_ongoing_notification_player(
            duel=duel,
            challenger=challenger,
            challenged=challenged,
            notification_adapter=notification_adapter,
            logger_instance=logger_instance)
    else:
        send_duel_ongoing_notification_team(
            duel=duel,
            challenger=challenger,
            challenged=challenged,
            notification_adapter=notification_adapter,
            logger_instance=logger_instance)


def send_duel_ongoing_notification_player(
        duel: Duel,
        challenger: Player,
        challenged: Player,
        notification_adapter: NotificationAdapter,
        logger_instance):
    send_notification(
        duel_data=duel,
        player_id=duel.challenger,
        notification_type=NotificationType.DUEL_ONGOING,
        notification_adapter=notification_adapter,
        logger_instance=logger_instance,
        complement=challenged.user.nickname)
    send_notification(
        duel_data=duel,
        player_id=duel.challenged,
        notification_type=NotificationType.DUEL_ONGOING,
        notification_adapter=notification_adapter,
        logger_instance=logger_instance,
        complement=challenger.user.nickname)


def send_duel_ongoing_notification_team(
        duel: Duel,
        challenger: Team,
        challenged: Team,
        notification_adapter: NotificationAdapter,
        logger_instance):
    send_notification(
        duel_data=duel,
        player_id=challenger.captain.player_id,
        notification_type=NotificationType.DUEL_ONGOING,
        notification_adapter=notification_adapter,
        logger_instance=logger_instance,
        complement=challenged.name,
        team_id=duel.challenger)
    send_notification(
        duel_data=duel,
        player_id=challenged.captain.player_id,
        notification_type=NotificationType.DUEL_ONGOING,
        notification_adapter=notification_adapter,
        logger_instance=logger_instance,
        complement=challenger.name,
        team_id=duel.challenged)


def add_victory_on_game_on_player(player: Player, duel_data: Duel):
    player_console = \
        next((x for x in player.consoles
              if x.console_id == duel_data.console.entity_id), None)
    if not player_console:
        raise Exception("Player {0} doesn't have console {1}"
                        .format(player.user.nickname,
                                duel_data.console.name))

    game_points = \
        next((x for x in player_console.game_points
              if x.game_id == duel_data.game.entity_id), None)
    if not game_points:
        game_points = GamePoints(
            game_id=duel_data.game.entity_id,
            victories=0)
    game_points.victories = game_points.victories + 1

    game_points_list = [x for x in player_console.game_points
                        if x.game_id != duel_data.game.entity_id]
    game_points_list.append(game_points)
    player_console.game_points = game_points_list

    player_console_list = [x for x in player.consoles
                           if x.console_id != duel_data.console.entity_id]
    player_console_list.append(player_console)
    player.consoles = player_console_list

    return player


def update_elo_ratings(winner, loser):
    elo = Elo()
    elo.set_ratings(
        winner_rating=winner.elo_rating,
        loser_rating=loser.elo_rating)
    elo.update_ratings()
    persist_elo_ratings(
        winner=winner,
        winner_rating=elo.winner_rating,
        loser=loser,
        loser_rating=elo.loser_rating)


def persist_elo_ratings(winner, winner_rating, loser, loser_rating):
    winner.elo_rating = winner_rating
    winner.save()
    loser.elo_rating = loser_rating
    loser.save()
