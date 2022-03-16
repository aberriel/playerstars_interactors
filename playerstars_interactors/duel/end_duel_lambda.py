from playerstars_adapters import (
    DuelAdapter as DuelAdapterDynamo,
    PlayerAdapter, TeamAdapter, ValuesAdapter)
from playerstars_domain import Duel, DuelMemberType, DuelStatus
from playerstars_graphql_adapters import (
    DuelAdapter as DuelAdapterGraphql,
    NotificationAdapter)
from playerstars_interactors.duel import (
    DuelSettlementTaskPlayer,
    DuelSettlementTaskTeam)
from playerstars_interactors.utils.domain_utils import find_entity_by_id
import logging


class EndDuelLambdaException(BaseException):
    pass


class EndDuelLambdaRequestModel:
    def __init__(self, json_data):
        self.duel_id = json_data['duel_id']


class EndDuelLambdaResponseModel:
    def __init__(self, duel_id,
                 duel_status,
                 processing_performed):
        self.duel_id = duel_id
        self.duel_status = duel_status
        self.processing_performed = processing_performed

    def __call__(self):
        return {
            'duel_id': self.duel_id,
            'duel_status': self.duel_status,
            'processing_performed': self.processing_performed}


class EndDuelLambdaInteractor:
    duel = None
    judge_matrix = None

    def __init__(self,
                 request: EndDuelLambdaRequestModel,
                 duel_adapter_dynamo: DuelAdapterDynamo,
                 duel_adapter_graphql: DuelAdapterGraphql,
                 notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter,
                 values_adapter: ValuesAdapter,
                 judge_matrix: str):
        self.request = request
        self.duel_adapter_dynamo = duel_adapter_dynamo
        self.duel_adapter_graphql = duel_adapter_graphql
        self.notification_adapter = notification_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.values_adapter = values_adapter
        self.judge_matrix = judge_matrix
        self.logger = logging.getLogger(__name__)

    def is_pending_completion(self):
        return self.duel.status == DuelStatus.DUELING

    def judge_duel(self):
        if self.duel.member_type == DuelMemberType.PLAYER:
            self.judge_duel_player()
        else:
            self.judge_duel_team()

    def judge_duel_player(self):
        duel_settlement_task = DuelSettlementTaskPlayer(
            duel=self.duel,
            duel_adapter=self.duel_adapter_graphql,
            notification_adapter=self.notification_adapter,
            player_adapter=self.player_adapter,
            values_adapter=self.values_adapter,
            judge_matrix=self.judge_matrix)
        self.duel = duel_settlement_task.run()

    def judge_duel_team(self):
        duel_settlement_task = DuelSettlementTaskTeam(
            duel=self.duel,
            duel_adapter=self.duel_adapter_graphql,
            notification_adapter=self.notification_adapter,
            player_adapter=self.player_adapter,
            team_adapter=self.team_adapter,
            values_adapter=self.values_adapter,
            judge_matrix=self.judge_matrix)
        self.duel = duel_settlement_task.run()

    def run(self):
        try:
            processing_performed = False
            self.duel: Duel = find_entity_by_id(
                _id=self.request.duel_id,
                adapter_instance=self.duel_adapter_dynamo,
                class_name='Duel')

            if self.is_pending_completion():
                self.judge_duel()
                processing_performed = True

            response = EndDuelLambdaResponseModel(
                duel_id=self.duel.entity_id,
                duel_status=self.duel.status.value,
                processing_performed=processing_performed)
            return response
        except Exception as exc:
            msg = 'Error during duel ending: {}'.format(exc)
            self.logger.error(msg)
            raise EndDuelLambdaException(msg)
