from playerstars_adapters import NotificationAdapter
from playerstars_domain import Notification, NotificationType, Player
from playerstars_interactors.duel.duel_utils import (
    add_victory_on_game_on_player,
    persist_elo_ratings,
    send_notification,
    update_elo_ratings)
from playerstars_interactors.notification.notification_utils import \
    SaveNotificationException
from pytest import raises
from tests.duel.duel_utils import (
    make_console_2,
    make_duel_player_in_progress_golden,
    make_game_3,
    make_player_1,
    make_player_1_without_game_points)
from unittest.mock import patch, MagicMock

import logging


prefix = 'playerstars_interactors.duel.duel_utils'


@patch.object(NotificationAdapter, 'save', return_value='notification123')
@patch('boto3.resource')
@patch('boto3.client')
def test_send_notification(boto_client,
                           boto_resource,
                           save_notification):
    notification_adapter = NotificationAdapter(
        'notification_table', 'endpoint')

    duel_data = make_duel_player_in_progress_golden()
    logger = logging.getLogger(__name__)

    result = send_notification(
        duel_data=duel_data,
        player_id='player123',
        notification_type=NotificationType.INFORMATIVE,
        notification_adapter=notification_adapter,
        complement='qualquer_coisa',
        logger_instance=logger)

    assert result
    assert isinstance(result, Notification)
    save_notification.assert_called_once()

    assert result.player_id == 'player123'
    assert result.notification_type == NotificationType.INFORMATIVE
    assert result.notification_complement == 'qualquer_coisa'
    assert result.duel_id == 'f13eb50c'


@patch.object(NotificationAdapter, 'save', side_effect=Exception('oops'))
@patch('boto3.resource')
@patch('boto3.client')
def test_send_notification_error(boto_client,
                                 boto_resource,
                                 save_notification):
    notification_adapter = NotificationAdapter(
        'notification-table', 'endpoint')

    duel_data = make_duel_player_in_progress_golden()
    logger = logging.getLogger(__name__)

    with raises(SaveNotificationException) as exc:
        send_notification(
            duel_data=duel_data,
            player_id='player123',
            notification_type=NotificationType.INFORMATIVE,
            notification_adapter=notification_adapter,
            complement='qualquer_coisa',
            logger_instance=logger)
    assert 'Error during notification save: oops' in str(exc.value)


def test_add_victory_on_game_on_player():
    duel_data = make_duel_player_in_progress_golden()
    player_data = make_player_1()

    assert player_data.consoles
    assert len(player_data.consoles) == 1
    console_data_1 = player_data.consoles[0]
    assert console_data_1
    assert console_data_1.game_points
    assert len(console_data_1.game_points) == 2

    game_points_data_1 = None
    for gamepoints_1 in console_data_1.game_points:
        if gamepoints_1.game_id == duel_data.game.entity_id:
            game_points_data_1 = gamepoints_1
    assert game_points_data_1
    assert game_points_data_1.victories == 0

    add_result = add_victory_on_game_on_player(player_data, duel_data)
    assert add_result
    assert isinstance(add_result, Player)
    assert add_result.consoles
    assert len(add_result.consoles) == 1
    console_data_2 = add_result.consoles[0]
    assert console_data_2
    assert console_data_2.game_points
    assert len(console_data_2.game_points) == 2

    game_points_data_2 = None
    for gamepoints_2 in console_data_2.game_points:
        if gamepoints_2.game_id == duel_data.game.entity_id:
            game_points_data_2 = gamepoints_2
    assert game_points_data_2
    assert game_points_data_2.victories == 1

    total_victories = add_result.get_game_victories_by_id(
        duel_data.game.entity_id)
    assert total_victories
    assert isinstance(total_victories, int)
    assert total_victories == 1


def test_add_victory_on_game_on_player_without_game():
    duel_data = make_duel_player_in_progress_golden()
    player_data = make_player_1_without_game_points()

    assert player_data.consoles
    assert len(player_data.consoles) == 1
    console_data_1 = player_data.consoles[0]
    assert len(console_data_1.game_points) == 0

    add_result = add_victory_on_game_on_player(player_data, duel_data)
    assert add_result
    assert isinstance(add_result, Player)
    assert add_result.consoles
    assert len(add_result.consoles) == 1
    console_data_2 = add_result.consoles[0]
    assert console_data_2.game_points
    assert len(console_data_2.game_points) == 1
    game_points_data = console_data_2.game_points[0]
    assert game_points_data.victories == 1


def make_duel_data_to_add_victory_error_test():
    duel_data = make_duel_player_in_progress_golden()
    duel_data.game = make_game_3()
    duel_data.console = make_console_2()
    return duel_data


def test_add_victory_on_game_on_player_without_console():
    console_2 = make_console_2()
    duel_data = make_duel_data_to_add_victory_error_test()
    player_data = make_player_1()

    with raises(Exception) as exc:
        add_victory_on_game_on_player(player_data, duel_data)
    assert "Player zyzukab doesn't have console {0}".format(console_2.name) \
           in str(exc.value)


@patch(f'{prefix}.Elo')
@patch(f'{prefix}.persist_elo_ratings')
def test_update_elo_ratings(persist_elo_ratings_mock, elo_mock):
    winner_mock = MagicMock()
    loser_mock = MagicMock()
    elo_mock().winner_rating = MagicMock()
    elo_mock().loser_rating = MagicMock()
    update_elo_ratings(winner_mock, loser_mock)

    elo_mock.assert_called()
    elo_mock().set_ratings.assert_called_with(
        winner_rating=winner_mock.elo_rating,
        loser_rating=loser_mock.elo_rating)
    elo_mock().update_ratings.assert_called_once()
    persist_elo_ratings_mock.assert_called_once_with(
        winner=winner_mock,
        winner_rating=elo_mock().winner_rating,
        loser=loser_mock,
        loser_rating=elo_mock().loser_rating)


def test_persist_elo_ratings():
    winner_mock = MagicMock()
    winner_rating_mock = MagicMock()
    loser_mock = MagicMock()
    loser_rating_mock = MagicMock()
    persist_elo_ratings(winner_mock,
                        winner_rating_mock,
                        loser_mock,
                        loser_rating_mock)

    winner_mock.save.assert_called_once()
    assert winner_mock.elo_rating == winner_rating_mock
    loser_mock.save.assert_called_once()
    assert loser_mock.elo_rating == loser_rating_mock
