from playerstars_adapters import ConsoleAdapter
from playerstars_domain import Console, Game
from typing import List

import logging


class GetAllConsolesExternalException(BaseException):
    pass


class GetAllConsolesExternalResponseModel:
    def __init__(self, consoles):
        self.consoles = consoles

    def __call__(self):
        return [x.to_json() for x in self.consoles]


class GetAllConsolesExternalInteractor:
    def __init__(self, console_adapter: ConsoleAdapter):
        self.console_adapter = console_adapter
        self.logger = logging.getLogger(__name__)

    def get_all_consoles(self):
        return self.console_adapter.list_all()

    def filter_games_only_actives(self, game_list: List[Game]):
        active_games = [x for x in game_list if x.active is True]
        return active_games

    def process_consoles(self, consoles: List[Console]):
        final_console_list = list()
        for console in consoles:
            processed_console = self.process_console_games(console)
            if processed_console:
                final_console_list.append(processed_console)
        return final_console_list

    def process_console_games(self, console: Console):
        filtered_games = self.filter_games_only_actives(console.games)
        if filtered_games:
            console.games = filtered_games
            return console
        return None

    def run(self):
        try:
            all_consoles = self.get_all_consoles()
            processed_consoles = self.process_consoles(all_consoles)
            response = GetAllConsolesExternalResponseModel(processed_consoles)
            return response
        except BaseException as exc:
            msg = f'Error during get all consoles to not logged users: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise GetAllConsolesExternalException(msg)
