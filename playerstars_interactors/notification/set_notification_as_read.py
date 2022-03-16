from playerstars_adapters import \
    NotificationAdapter as NotificationAdapterDynamo
from playerstars_domain import Notification, NotificationStatus
from playerstars_graphql_adapters import \
    NotificationAdapter as NotificationAdapterGraphql
from playerstars_interactors.utils.domain_utils import find_entity_by_id

import logging


class SetNotificationAsReadRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.notification_id = json_data['notification_id']


class SetNotificationAsReadResponseModel:
    def __init__(self, notification_id):
        self.notification_id = notification_id

    def __call__(self):
        return self.notification_id


class SetNotificationAsReadException(BaseException):
    pass


class SetNotificationAsReadInteractor:
    notification = None

    def __init__(self,
                 request: SetNotificationAsReadRequestModel,
                 notification_adapter_dynamo: NotificationAdapterDynamo,
                 notification_adapter_graphql: NotificationAdapterGraphql):
        self.request = request
        self.notification_adapter_dynamo = notification_adapter_dynamo
        self.notification_adapter_graphql = notification_adapter_graphql
        self.logger = logging.getLogger(__name__)

    def get_notification(self):
        self.notification: Notification = find_entity_by_id(
            _id=self.request.notification_id,
            adapter_instance=self.notification_adapter_dynamo,
            class_name='Notification')

    def check_notification(self):
        if self.notification.status in (NotificationStatus.CLOSED,
                                        NotificationStatus.DELETED):
            raise Exception("It can't to close notification because it "
                            "is on status {0}"
                            .format(self.notification.status.value))
        return True

    def set_notification_read(self):
        self.notification.set_adapter(self.notification_adapter_graphql)
        self.notification.status = NotificationStatus.CLOSED
        return self.notification.save_graphql(exec_update=True)

    def run(self):
        try:
            self.get_notification()
            self.check_notification()
            update_result = self.set_notification_read()
            response = SetNotificationAsReadResponseModel(update_result)
            return response()
        except Exception as exc:
            msg = "Error during notification close: {0}".format(str(exc))
            self.logger.error(msg)
            raise SetNotificationAsReadException(msg)
