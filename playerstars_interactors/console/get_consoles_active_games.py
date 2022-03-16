from playerstars_adapters import ConsoleAdapter
from playerstars_domain import Console, Game
from typing import List

import logging


class GetAllConsolesActiveGamesException(BaseException):
    pass


class GetAllConsolesActiveGamesResponseModel:
    def __init__(self, consoles):
        self.consoles = consoles

    def __call__(self):
        return self.consoles


class GetAllConsolesActiveGamesInteractor:
    def __init__(self, console_adapter: ConsoleAdapter):
        self.console_adapter = console_adapter
        self.logger = logging.getLogger(__name__)

    def get_all_consoles(self):
        return self.console_adapter.list_all()

    @staticmethod
    def filter_games_only_actives(game_list: List[Game]):
        return [x for x in game_list if x.active]

    def process_consoles(self, consoles: List[Console]):
        final_console_list = list()
        for console in consoles:
            active_games = self.filter_games_only_actives(console.games)
            if active_games:
                console.games = active_games
                final_console_list.append(console)
        return final_console_list

    @staticmethod
    def format_consoles(consoles: List[Console]):
        console_list = list()
        for console in consoles:
            console_list.append({
                "entity_id": console.entity_id,
                "name": console.name,
                "logo_path": console.logo_path,
                "tag_name": console.tag_name,
                "games": console.to_json()['games']
            })
        return console_list

    def run(self):
        try:
            all_consoles = self.get_all_consoles()
            processed_consoles = self.process_consoles(all_consoles)
            formated_consoles = self.format_consoles(processed_consoles)
            response = GetAllConsolesActiveGamesResponseModel(
                formated_consoles)
            return response
        except BaseException as exc:
            msg = f'Error during get all consoles active games: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise GetAllConsolesActiveGamesException(msg)
