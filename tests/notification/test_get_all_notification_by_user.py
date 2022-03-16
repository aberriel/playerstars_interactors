from unittest.mock import patch
from playerstars_adapters import NotificationAdapter
from playerstars_domain import Notification
from playerstars_interactors import (
    GetAppNotificationByUserRequestModel,
    GetAppNotificationByUserInteractor)


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


notification1 = Notification.from_json({
    "player_id": "12341",
    "entity_id": "notification1",
    "duel_id": "222222",
    "status": "CREATED",
    "creation_datetime": "2016-11-01T19:49:00",
    "notification_type": "INFORMATIVE"
})

notification2 = Notification.from_json({
    "player_id": "12341",
    "entity_id": "notification2",
    "duel_id": "222222111",
    "status": "CREATED",
    "creation_datetime": "2017-11-01T19:49:00",
    "notification_type": "INFORMATIVE"
})

notification3 = Notification.from_json({
    "player_id": "12341",
    "entity_id": "notification3",
    "duel_id": "22222211342342111",
    "status": "CLOSED",
    "creation_datetime": "2018-11-01T19:49:00",
    "notification_type": "INFORMATIVE"
})

notification4 = Notification.from_json({
    "player_id": "12341",
    "entity_id": "notification4",
    "duel_id": "1q2w3e",
    "status": "CREATED",
    "creation_datetime": "2019-11-30T20:45:55",
    "notification_type": "DUEL_INVITE",
    "notification_image": "/images/fifa19.png",
    "notification_complement": "aabbcc"
})

notification5 = Notification.from_json({
    "player_id": "12341",
    "entity_id": "notification5",
    "duel_id": "1q2w3e",
    "status": "CREATED",
    "creation_datetime": "2016-11-01T20:45:55",
    "notification_type": "DUEL_INVITE",
    "notification_image": "/images/fifa19.png",
    "notification_complement": "aabbcc"
})

notification4_response = {
    "player_id": "12341",
    "entity_id": "notification4",
    "duel_id": "1q2w3e",
    "status": "CREATED",
    "creation_datetime": "2019-11-30T20:45:55",
    "notification_type": "DUEL_INVITE",
    "challenger_nickname": "aabbcc",
    "game_logo_path": "/images/fifa19.png"
}

expected_response = [notification4.to_json(),
                     notification3.to_json(),
                     notification2.to_json(),
                     notification5.to_json(),
                     notification1.to_json()]


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
@patch.object(NotificationAdapter, 'filter',
              return_value=[notification1, notification2, notification3,
                            notification4, notification5])
def test_get_all_player_notifications(filter_notification, boto_mock):
    adapter_instance = NotificationAdapter('dyamo-table', 'localhost-teste')
    request = GetAppNotificationByUserRequestModel('12341', None)
    interactor = GetAppNotificationByUserInteractor(
        request=request,
        adapter_instance=adapter_instance)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == expected_response


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
@patch.object(NotificationAdapter, 'list_all',
              return_value=[])
def test_get_all_player_notifications_has_none(list_all_notifications,
                                               boto_mock):
    adapter_instance = NotificationAdapter('dynamo-table', 'localhost-teste')
    request = GetAppNotificationByUserRequestModel('12341', None)
    interactor = GetAppNotificationByUserInteractor(
        request=request,
        adapter_instance=adapter_instance)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == []


# noinspection PyUnusedLocal,PyUnusedLocal
@patch(f'{prefix_dynamodb_adapter}.boto3')
@patch.object(NotificationAdapter, 'filter',
              return_value=[notification1,
                            notification2,
                            notification3,
                            notification4])
def test_get_by_player_and_status_notifications(filter_notification,
                                                boto_mock):
    adapter_instance = NotificationAdapter('dynamo-table', 'localhost-teste')
    request = GetAppNotificationByUserRequestModel('12341', "CLOSED")
    interactor = GetAppNotificationByUserInteractor(
        request=request,
        adapter_instance=adapter_instance)
    result = interactor.run()
    assert isinstance(result, list)
    assert result == [notification3.to_json()]
