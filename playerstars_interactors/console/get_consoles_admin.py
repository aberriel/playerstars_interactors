from playerstars_adapters import ConsoleAdapter, PlayerAdapter
from playerstars_domain import Console
from playerstars_interactors.utils.rights_utils import (
    AccessDeniedAdminException,
    check_player_is_admin
)
from typing import List

import logging


class GetConsolesAdminException(BaseException):
    pass


class GetConsolesAdminRequestModel:
    def __init__(self, player_id: str):
        self.player_id = player_id


class GetConsolesAdminResponseModel:
    def __init__(self, consoles: List[Console]):
        self.consoles = consoles

    def __call__(self):
        return [x.to_json() for x in self.consoles]


class GetConsolesAdminInteractor:
    def __init__(self,
                 request: GetConsolesAdminRequestModel,
                 console_adapter: ConsoleAdapter,
                 player_adapter: PlayerAdapter):
        self.console_adapter = console_adapter
        self.player_adapter = player_adapter
        self.request = request
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            check_player_is_admin(
                player_id=self.request.player_id,
                player_adapter=self.player_adapter)
            all_consoles = self.console_adapter.list_all()
            response = GetConsolesAdminResponseModel(all_consoles)
            return response()
        except (AccessDeniedAdminException, Exception) as exc:
            msg = "Error during recovery all consoles: {0}".format(str(exc))
            self.logger.error(msg)
            if isinstance(exc, AccessDeniedAdminException):
                raise AccessDeniedAdminException(msg)
            raise GetConsolesAdminException(msg)
