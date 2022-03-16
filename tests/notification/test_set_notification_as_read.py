from playerstars_domain import Notification, NotificationStatus
from playerstars_interactors import (
    SetNotificationAsReadException,
    SetNotificationAsReadInteractor,
    SetNotificationAsReadRequestModel)
from pytest import raises
from unittest.mock import MagicMock, patch


def make_request():
    return {
        'player_id': 'player123',
        'notification_id': 'notification123'
    }


def make_notification_sent():
    return Notification(
        entity_id='notification123',
        player_id='player123',
        status=NotificationStatus.SENT,
        duel_id='duel123')


def make_notification_closed():
    notification_data = make_notification_sent()
    notification_data.status = NotificationStatus.CLOSED
    return notification_data


def make_notification_deleted():
    notification_data = make_notification_sent()
    notification_data.status = NotificationStatus.DELETED
    return notification_data


notification_adapter_mock_sent = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_notification_sent()),
    save=MagicMock(return_value='notification123'))
notification_adapter_mock_closed = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_notification_closed()))
notification_adapter_mock_deleted = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_notification_deleted()))
notification_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_notification_sent()),
    save=MagicMock(side_effect=Exception('oops')))


@patch('boto3.resource')
@patch('boto3.client')
def test_get_notification(client, resource):
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_sent,
        notification_adapter_graphql=notification_adapter_mock_sent)

    interactor.get_notification()
    assert interactor.notification
    assert isinstance(interactor.notification, Notification)


@patch('boto3.resource')
def test_check_notification(resource):
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_sent,
        notification_adapter_graphql=notification_adapter_mock_sent)
    interactor.notification = make_notification_sent()

    check_result = interactor.check_notification()
    assert check_result
    assert isinstance(check_result, bool)


@patch('boto3.resource')
def test_check_notification_closed(resource):
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_closed,
        notification_adapter_graphql=notification_adapter_mock_closed)
    interactor.notification = make_notification_closed()

    with raises(Exception) as exc:
        interactor.check_notification()
    assert "It can't to close notification because " \
           "it is on status CLOSED" in str(exc.value)


@patch('boto3.resource')
def test_check_notification_deleted(resource):
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_deleted,
        notification_adapter_graphql=notification_adapter_mock_deleted)
    interactor.notification = make_notification_deleted()

    with raises(Exception) as exc:
        interactor.check_notification()
    assert "It can't to close notification because " \
           "it is on status DELETED" in str(exc.value)


@patch('boto3.resource')
@patch('boto3.client')
def test_update_notification(client, resource):
    notification_adapter_mock_sent.save.call_count = 0
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_sent,
        notification_adapter_graphql=notification_adapter_mock_sent)
    interactor.notification = make_notification_sent()
    save_result = interactor.set_notification_read()

    assert save_result == 'notification123'
    notification_adapter_mock_sent.save.assert_called_once()


@patch('boto3.resource')
@patch('boto3.client')
def test_set_notification_as_read(client, resource):
    notification_adapter_mock_sent.get_by_id.call_count = 0
    notification_adapter_mock_sent.save.call_count = 0
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_sent,
        notification_adapter_graphql=notification_adapter_mock_sent)
    response = interactor.run()

    assert response
    assert isinstance(response, str)
    assert response == 'notification123'
    notification_adapter_mock_sent.save.assert_called_once()
    notification_adapter_mock_sent.get_by_id.assert_called_once()


@patch('boto3.resource')
@patch('boto3.client')
def test_set_notification_as_read_raises(client, resource):
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_raises,
        notification_adapter_graphql=notification_adapter_mock_raises)

    with raises(SetNotificationAsReadException) as exc:
        interactor.run()
    assert "Error during notification close: oops" in str(exc.value)


@patch('boto3.resource')
@patch('boto3.client')
def test_set_notification_as_read_closed(client, resource):
    notification_adapter_mock_closed.get_by_id.call_count = 0
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_closed,
        notification_adapter_graphql=notification_adapter_mock_closed)

    with raises(SetNotificationAsReadException) as exc:
        interactor.run()
    notification_adapter_mock_closed.get_by_id.assert_called_once()
    assert "Error during notification close: It can't to close " \
           "notification because it is on status CLOSED" in str(exc.value)


@patch('boto3.resource')
@patch('boto3.client')
def test_set_notification_as_read_deleted(client, resource):
    notification_adapter_mock_deleted.get_by_id.call_count = 0
    request = SetNotificationAsReadRequestModel(make_request())
    interactor = SetNotificationAsReadInteractor(
        request=request,
        notification_adapter_dynamo=notification_adapter_mock_deleted,
        notification_adapter_graphql=notification_adapter_mock_sent)

    with raises(SetNotificationAsReadException) as exc:
        interactor.run()
    notification_adapter_mock_deleted.get_by_id.assert_called_once()
    assert "Error during notification close: It can't to close " \
           "notification because it is on status DELETED" in str(exc.value)
