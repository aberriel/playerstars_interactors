from playerstars_adapters import (
    NotificationAdapter
)
from playerstars_domain import (
    Notification
)
from playerstars_domain.notification.notification import NotificationStatus
from typing import List
from operator import itemgetter


class GetAppNotificationByUserRequestModel:
    def __init__(self, entity_id, status):
        self.player_id = entity_id
        self.status = status


class GetAppNotificationByUserResponseModel:
    def __init__(self, entities: List[Notification]):
        self.entities: List[Notification] = entities

    @staticmethod
    def ordered_notifications(notifications):
        json_notifications = [x.to_json() for x in notifications]
        return sorted(
            json_notifications,
            key=itemgetter('creation_datetime'),
            reverse=True)

    def __call__(self):
        return self.ordered_notifications(self.entities)


class GetAppNotificationByUserInteractor:
    def __init__(self,
                 request: GetAppNotificationByUserRequestModel,
                 adapter_instance: NotificationAdapter):
        self.request = request
        self.adapter_instance = adapter_instance

    @staticmethod
    def filter_by_status(notification_list, status):
        return [x for x in notification_list
                if x.status == NotificationStatus(status)]

    def run(self):
        notification_list: List[Notification] = \
            self.adapter_instance.filter(
            player_id__eq=self.request.player_id)
        if self.request.status:
            notification_list = self.filter_by_status(
                notification_list, self.request.status)
        response = GetAppNotificationByUserResponseModel(notification_list)
        return response()
