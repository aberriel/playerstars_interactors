from playerstars_adapters import DuelAdapter as DuelAdapterDynamo
from playerstars_domain import Duel, DuelStatus
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_graphql_adapters import DuelAdapter as DuelAdapterGraphql
from playerstars_interactors.utils.domain_utils import find_entity_by_id
import logging


class RejectDuelException(BaseException):
    pass


class RejectDuelRequestModel:
    def __init__(self, json_data):
        self.duel_id = json_data['duel_id']


class RejectDuelResponseModel:
    def __init__(self, duel_id):
        self.duel_id = duel_id

    def __call__(self):
        return self.duel_id


class RejectDuelInteractor:
    duel = None

    def __init__(self,
                 request: RejectDuelRequestModel,
                 duel_adapter_dynamo: DuelAdapterDynamo,
                 duel_adapter_graphql: DuelAdapterGraphql):
        self.request = request
        self.duel_adapter_dynamo = duel_adapter_dynamo
        self.duel_adapter_graphql = duel_adapter_graphql
        self.logger = logging.getLogger(__name__)

    def change_status(self):
        if self.duel.status != DuelStatus.LOBBY:
            raise Exception("Player can't reject duel "
                            "because duel's status is {0}"
                            .format(self.duel.status.value))
        self.duel.set_adapter(self.duel_adapter_graphql)
        self.duel.status = DuelStatus.REJECTED
        self.duel.time_cancel = aware_now()
        save_result = self.duel.save_graphql(exec_update=True)
        return save_result

    def run(self):
        try:
            self.duel: Duel = find_entity_by_id(
                _id=self.request.duel_id,
                adapter_instance=self.duel_adapter_dynamo,
                class_name='Duel')
            duel_altered_id = self.change_status()
            response = RejectDuelResponseModel(duel_altered_id)
            return response
        except Exception as exc:
            msg = f'Error in reject duel {self.request.duel_id}: {str(exc)}'
            self.logger.error(msg)
            raise RejectDuelException(msg)
