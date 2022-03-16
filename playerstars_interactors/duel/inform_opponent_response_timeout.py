from playerstars_adapters import (
    DuelAdapter as DuelAdapterDynamo,
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    Duel,
    DuelMemberType,
    DuelStatus,
    Team)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_graphql_adapters import DuelAdapter as DuelAdapterGraphql
from playerstars_interactors.duel.cancel_duel import \
    DuelMemberNotCreatorException
from playerstars_interactors.utils.domain_utils import (
    EntityNotFoundException,
    find_entity_by_id)
import logging


class InformOpponentResponseTimeoutException(BaseException):
    pass


class InformOpponentResponseTimeoutRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.duel_id = json_data['duel_id']


class InformOpponentResponseTimeoutResponseModel:
    def __init__(self, duel_data: Duel):
        self.duel_id = duel_data.entity_id
        self.cancelation_datetime = duel_data.time_finish

    def __call__(self):
        return {
            'duel_id': self.duel_id,
            'cancelation_datetime': self.cancelation_datetime.isoformat()}


class InformOpponentResponseTimeoutInteractorAdapters:
    def __init__(self,
                 duel_adapter_dynamo: DuelAdapterDynamo,
                 duel_adapter_graphql: DuelAdapterGraphql,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter):
        self.duel_adapter_dynamo = duel_adapter_dynamo
        self.duel_adapter_graphql = duel_adapter_graphql
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter


class InformOpponentResponseTimeoutInteractor:
    duel = None
    player_data = None

    def __init__(self, request: InformOpponentResponseTimeoutRequestModel,
                 adapters: InformOpponentResponseTimeoutInteractorAdapters):
        self.request = request
        self.adapters = adapters
        self.logger = logging.getLogger(__name__)

    def get_duel(self):
        duel: Duel = find_entity_by_id(
            _id=self.request.duel_id,
            adapter_instance=self.adapters.duel_adapter_dynamo,
            class_name='Duel')
        return duel

    def get_team_data(self):
        return find_entity_by_id(
            _id=self.duel.challenger,
            adapter_instance=self.adapters.team_adapter,
            class_name='Team')

    def get_player_data(self, player_id):
        return find_entity_by_id(
            _id=player_id,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

    def check_duel_owner(self):
        if self.duel.member_type == DuelMemberType.PLAYER:
            return self.check_duel_owner_player()
        return self.check_duel_owner_team()

    def check_duel_owner_player(self):
        if self.duel.challenger != self.request.player_id:
            raise DuelMemberNotCreatorException(
                f"Player {self.player_data.user.nickname} "
                f"isn't the duel's owner")
        return True

    def check_duel_owner_team(self):
        team_owner: Team = self.get_team_data()
        if team_owner.captain.player_id != self.request.player_id:
            raise DuelMemberNotCreatorException(
                f"Player {self.player_data.user.nickname} isn't "
                f"the captain of the team {team_owner.name}")
        return True

    def set_duel_timeout_status(self):
        self.duel.set_adapter(self.adapters.duel_adapter_graphql)
        self.duel.status = DuelStatus.CANCELED_BY_TIMEOUT
        self.duel.time_finish = aware_now()
        self.duel.save_graphql(exec_update=True)

    def run(self):
        try:
            self.duel = self.get_duel()
            self.player_data = self.get_player_data(self.request.player_id)
            self.check_duel_owner()
            self.set_duel_timeout_status()
            response = InformOpponentResponseTimeoutResponseModel(self.duel)
            return response
        except (Exception, EntityNotFoundException) as exc:
            msg = f'Error during define duel timeout status: ' \
                  f'{exc.__class__.__name__}: {str(exc)}'
            self.logger.error(msg)
            raise InformOpponentResponseTimeoutException(msg)
