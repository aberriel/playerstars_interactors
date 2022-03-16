from playerstars_interactors.utils.notification_utils import (
    check_if_can_send_push_notification,
    create_notification,
    send_push_notification,
    SendNotificationError)
from pytest import raises
from unittest.mock import MagicMock, patch


prefix = 'playerstars_interactors.utils.notification_utils'


@patch(f'{prefix}.boto3')
@patch(f'{prefix}.json')
def test_send_push_notification(mock_json, mock_boto):
    mock_player_data = MagicMock()
    mock_notification_json = MagicMock()
    result = send_push_notification(
        player_data=mock_player_data,
        notification_json=mock_notification_json)
    mock_boto.client.assert_called_with('sns')
    mock_json.dumps.assert_called_with(mock_notification_json)
    mock_boto.client().publish.assert_called_with(
        TargetArn=mock_player_data.push_notification_data.endpoint_arn,
        Message=mock_json.dumps())
    mock_boto.client().publish().__getitem__.assert_called_with('MessageId')
    assert result == mock_boto.client().publish().__getitem__()


def test_check_if_can_send_push_notification__push_data_none():
    mock_player_data = MagicMock()
    mock_player_data.push_notification_data = None
    check_result = check_if_can_send_push_notification(mock_player_data)
    assert check_result is False


def test_check_if_can_send_push_notification__endpoint_arn_none():
    mock_player_data = MagicMock()
    mock_player_data.push_notification_data = MagicMock()
    mock_player_data.push_notification_data.endpoint_arn = None
    check_result = check_if_can_send_push_notification(mock_player_data)
    assert check_result is False


def test_check_if_can_send_push_notification():
    mock_player_data = MagicMock()
    check_result = check_if_can_send_push_notification(mock_player_data)
    assert check_result is True


@patch(f'{prefix}.Notification')
@patch(f'{prefix}.send_push_notification')
@patch(f'{prefix}.check_if_can_send_push_notification',
       return_value=True)
def test_create_notification(mock_check_can_send_push_notification,
                             mock_send_push_notification,
                             mock_notification):
    mock_player_data = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_notification_type = MagicMock()
    mock_duel_id = MagicMock()
    mock_team_id = MagicMock()
    mock_championship_id = MagicMock()
    mock_notification_image = MagicMock()
    mock_notification_complement = MagicMock()
    mock_logger_instance = MagicMock()
    mock_additional_data = MagicMock()
    mock_creation_datetime = MagicMock()
    result = create_notification(
        player_data=mock_player_data,
        notification_adapter=mock_notification_adapter,
        notification_type=mock_notification_type,
        duel_id=mock_duel_id,
        team_id=mock_team_id,
        championship_id=mock_championship_id,
        notification_image=mock_notification_image,
        notification_complement=mock_notification_complement,
        additional_data=mock_additional_data,
        logger_instance=mock_logger_instance,
        creation_datetime=mock_creation_datetime)

    mock_notification.assert_called_with(
        player_id=mock_player_data.entity_id,
        notification_type=mock_notification_type,
        duel_id=mock_duel_id,
        team_id=mock_team_id,
        championship_id=mock_championship_id,
        notification_image=mock_notification_image,
        notification_complement=mock_notification_complement,
        additional_data=mock_additional_data,
        creation_datetime=mock_creation_datetime)
    mock_notification().set_adapter.assert_called_with(
        mock_notification_adapter)
    mock_notification().save.assert_called()
    mock_check_can_send_push_notification.assert_called_with(mock_player_data)
    mock_send_push_notification.assert_called_with(
        player_data=mock_player_data,
        notification_json=mock_notification().to_json())
    mock_notification().to_json.assert_called()
    assert result == mock_send_push_notification()


@patch(f'{prefix}.Notification')
@patch(f'{prefix}.send_push_notification')
@patch(f'{prefix}.check_if_can_send_push_notification',
       return_value=False)
def test_create_notification_check_can_send_push_false(
        mock_check_can_send_push_notification,
        mock_send_push_notification,
        mock_notification):
    mock_player_data = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_notification_type = MagicMock()
    mock_duel_id = MagicMock()
    mock_team_id = MagicMock()
    mock_championship_id = MagicMock()
    mock_notification_image = MagicMock()
    mock_notification_complement = MagicMock()
    mock_logger_instance = MagicMock()
    mock_additional_data = MagicMock()
    mock_creation_datetime = MagicMock()
    result = create_notification(
        player_data=mock_player_data,
        notification_adapter=mock_notification_adapter,
        notification_type=mock_notification_type,
        duel_id=mock_duel_id,
        team_id=mock_team_id,
        championship_id=mock_championship_id,
        notification_image=mock_notification_image,
        notification_complement=mock_notification_complement,
        additional_data=mock_additional_data,
        logger_instance=mock_logger_instance,
        creation_datetime=mock_creation_datetime)

    mock_notification.assert_called_with(
        player_id=mock_player_data.entity_id,
        notification_type=mock_notification_type,
        duel_id=mock_duel_id,
        team_id=mock_team_id,
        championship_id=mock_championship_id,
        notification_image=mock_notification_image,
        notification_complement=mock_notification_complement,
        additional_data=mock_additional_data,
        creation_datetime=mock_creation_datetime)
    mock_notification().set_adapter.assert_called_with(
        mock_notification_adapter)
    mock_notification().save.assert_called()
    mock_check_can_send_push_notification.assert_called_with(mock_player_data)
    mock_send_push_notification.assert_not_called()
    mock_notification().to_json.assert_not_called()
    assert result is None


@patch(f'{prefix}.Notification', side_effect=Exception('oops'))
@patch(f'{prefix}.send_push_notification')
def test_create_notification_error(mock_send_push_notification,
                                   mock_notification):
    mock_player_data = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_notification_type = MagicMock()
    mock_duel_id = MagicMock()
    mock_team_id = MagicMock()
    mock_championship_id = MagicMock()
    mock_notification_image = MagicMock()
    mock_notification_complement = MagicMock()
    mock_logger_instance = MagicMock()
    mock_creation_datetime = MagicMock()
    mock_additional_data = MagicMock()
    with raises(SendNotificationError) as exc:
        create_notification(
            player_data=mock_player_data,
            notification_adapter=mock_notification_adapter,
            notification_type=mock_notification_type,
            duel_id=mock_duel_id,
            team_id=mock_team_id,
            championship_id=mock_championship_id,
            notification_image=mock_notification_image,
            notification_complement=mock_notification_complement,
            logger_instance=mock_logger_instance,
            additional_data=mock_additional_data,
            creation_datetime=mock_creation_datetime)

    assert f'Error during sending notification: Exception: oops' \
        in str(exc.value)
    mock_notification.assert_called_with(
        player_id=mock_player_data.entity_id,
        notification_type=mock_notification_type,
        duel_id=mock_duel_id,
        team_id=mock_team_id,
        championship_id=mock_championship_id,
        notification_image=mock_notification_image,
        notification_complement=mock_notification_complement,
        additional_data=mock_additional_data,
        creation_datetime=mock_creation_datetime)
    mock_send_push_notification.assert_not_called()
    mock_logger_instance.error.assert_called()
