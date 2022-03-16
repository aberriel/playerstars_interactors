from datetime import datetime
from playerstars_adapters import NotificationAdapter
from playerstars_domain import (
    Notification,
    NotificationType,
    Player)
from playerstars_domain.utils.datetime_helper import aware_now

import boto3
import json


class SendNotificationError(BaseException):
    pass


def send_push_notification(player_data: Player, notification_json: dict):
    sns_client = boto3.client('sns')
    endpoint_arn = player_data.push_notification_data.endpoint_arn
    response = sns_client.publish(TargetArn=endpoint_arn,
                                  Message=json.dumps(notification_json))
    return response['MessageId']


def check_if_can_send_push_notification(player_data: Player):
    return player_data.push_notification_data is not None \
        and player_data.push_notification_data.endpoint_arn is not None


def create_notification(
        player_data: Player,
        notification_adapter: NotificationAdapter,
        logger_instance,
        notification_type: NotificationType = NotificationType.INFORMATIVE,
        duel_id: str = None,
        team_id: str = None,
        championship_id: str = None,
        notification_image: str = None,
        notification_complement: str = None,
        additional_data: str = None,
        creation_datetime: datetime = aware_now()):
    try:
        notification = Notification(
            player_id=player_data.entity_id,
            notification_type=notification_type,
            duel_id=duel_id,
            team_id=team_id,
            championship_id=championship_id,
            notification_image=notification_image,
            notification_complement=notification_complement,
            creation_datetime=creation_datetime,
            additional_data=additional_data)
        notification.set_adapter(notification_adapter)
        notification.save()
        push_message_id = None
        if check_if_can_send_push_notification(player_data):
            push_message_id = send_push_notification(
                player_data=player_data,
                notification_json=notification.to_json())
        return push_message_id
    except BaseException as exc:
        msg = f'Error during sending notification: ' \
              f'{exc.__class__.__name__}: {exc}'
        logger_instance.error(msg)
        raise SendNotificationError(msg)
