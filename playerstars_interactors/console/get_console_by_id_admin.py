from playerstars_adapters import (
    ConsoleAdapter,
    PlayerAdapter)
from playerstars_interactors.utils.domain_utils import EntityNotFoundException
from playerstars_interactors.utils.rights_utils import (
    AccessDeniedAdminException,
    check_player_is_admin)

import logging


class GetConsoleByIdAdminException(BaseException):
    pass


class GetConsoleByIdAdminRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.console_id = json_data['console_id']


class GetConsoleByIdAdminResponseModel:
    def __init__(self, console_data):
        self.console_data = console_data

    def __call__(self):
        if not self.console_data:
            return None
        return self.console_data.to_json()


class GetConsoleByIdAdminInteractor:
    def __init__(self,
                 request: GetConsoleByIdAdminRequestModel,
                 player_adapter: PlayerAdapter,
                 console_adapter: ConsoleAdapter):
        self.request = request
        self.console_adapter = console_adapter
        self.player_adapter = player_adapter
        self.logger = logging.getLogger(__name__)

    def get_console(self):
        return self.console_adapter.get_by_id(self.request.console_id)

    def run(self):
        try:
            check_player_is_admin(
                player_id=self.request.player_id,
                player_adapter=self.player_adapter)
            console = self.get_console()
            response = GetConsoleByIdAdminResponseModel(console)
            return response()
        except (AccessDeniedAdminException,
                EntityNotFoundException,
                Exception) as exc:
            msg = 'Error during recovery console: {0}'.format(str(exc))
            self.logger.error(msg)
            if isinstance(exc, AccessDeniedAdminException):
                raise AccessDeniedAdminException(msg)
            raise GetConsoleByIdAdminException(msg)
