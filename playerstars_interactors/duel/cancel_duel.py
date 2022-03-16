from datetime import datetime
from playerstars_adapters import (
    DuelAdapter as DuelAdapterDynamo,
    NotificationAdapter,
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    Duel,F
    DuelMemberType,
    DuelStatus,
    Notification,
    NotificationStatus,
    Team)
from playerstars_graphql_adapters import DuelAdapter as DuelAdapterGraphql
from playerstars_interactors.utils.domain_utils import (
    EntityNotFoundException,F
    find_entity_by_id)
from typing import List

import logging


class DuelNotLobbyException(BaseException):
    pass


class DuelMemberNotCreatorException(BaseException):
    pass


class CancelDuelException(BaseException):
    pass


class CancelDuelRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.duel_id = json_data['duel_id']


class CancelDuelResponseModel:
    def __init__(self, duel_id: str,
                 notification_id: str,
                 cancel_datetime: datetime):
        self.duel_id = duel_id
        self.notification_id = notification_id
        self.cancel_datetime = cancel_datetime

    def __call__(self):
        return {
            'duel_id': self.duel_id,
            'notification_id': self.notification_id,
            'cancel_datetime': self.cancel_datetime}


class CancelDuelInteractorAdapters:
    def __init__(self, duel_adapter_dynamo: DuelAdapterDynamo,
                 duel_adapter_graphql: DuelAdapterGraphql,
                 notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter):
        self.duel_adapter_dynamo = duel_adapter_dynamo
        self.duel_adapter_graphql = duel_adapter_graphql
        self.notification_adapter = notification_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter


class CancelDuelInteractor:
    duel = None
    player_request = None

    def __init__(self,
                 request: CancelDuelRequestModel,
                 adapters: CancelDuelInteractorAdapters):
        self.request = request
        self.adapters = adapters
        self.logger = logging.getLogger(__name__)

    def get_player(self, player_id):
        return find_entity_by_id(
            _id=player_id,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

    def get_duel(self):
        duel_data: Duel = find_entity_by_id(
            _id=self.request.duel_id,
            adapter_instance=self.adapters.duel_adapter_dynamo,
            class_name='Duel')
        return duel_data

    def get_team(self, team_id: str):
        return find_entity_by_id(
            _id=team_id,
            adapter_instance=self.adapters.team_adapter,
            class_name='Team')

    def get_notification_by_duel(self):
        all_notifications: List[Notification] = \
            self.adapters.notification_adapter.list_all()
        duel_invite_notification = \
            next((x for x in all_notifications
                  if x.duel_id == self.request.duel_id
                  and x.status != NotificationStatus.DELETED),
                 None)
        return duel_invite_notification

    def delete_notification(self):
        notification_to_delete = self.get_notification_by_duel()
        if notification_to_delete:
            notification_to_delete.set_adapter(
                self.adapters.notification_adapter)
            notification_to_delete.status = NotificationStatus.DELETED
            return notification_to_delete.save()
        return None

    def delete_duel(self):
        if self.duel.status != DuelStatus.LOBBY:
            raise DuelNotLobbyException(
                "Duel can't to cancel because it isn't on state LOBBY")

        self.duel.set_adapter(self.adapters.duel_adapter_graphql)
        self.duel.status = DuelStatus.DELETED
        self.duel.time_cancel = datetime.utcnow()
        save_result = self.duel.save_graphql(exec_update=True)
        return save_result

    def check_if_player_can_cancel_duel(self):
        if self.duel.member_type == DuelMemberType.PLAYER:
            return self.check_if_player_can_cancel_duel_player()
        return self.check_if_player_can_cancel_duel_team()

    def check_if_player_can_cancel_duel_player(self):
        if self.duel.challenger != self.player_request.entity_id:
            raise DuelMemberNotCreatorException(
                f"Player {self.player_request.user.nickname} "
                f"can't cancel duel because isn't duel creator")
        return True

    def check_if_player_can_cancel_duel_team(self):
        team_data: Team = self.get_team(self.duel.challenger)
        if self.request.player_id != team_data.captain.player_id:
            raise DuelMemberNotCreatorException(
                f"Player {self.player_request.user.nickname} "
                f"can't cancel duel because isn't captain of challenger")
        return True

    def run(self):
        try:
            self.duel: Duel = self.get_duel()
            self.player_request = self.get_player(self.request.player_id)
            self.check_if_player_can_cancel_duel()
            save_duel_result = self.delete_duel()
            save_notification_result = self.delete_notification()
            response = CancelDuelResponseModel(
                duel_id=save_duel_result,
                notification_id=save_notification_result,
                cancel_datetime=self.duel.time_cancel.isoformat())
            return response
        except (Exception, EntityNotFoundException) as exc:
            msg = f'Error during cancel duel: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise CancelDuelException(msg)
