from playerstars_adapters import ConsoleAdapter
from playerstars_domain import Console, Game
from typing import List

import logging


class GetAllGamesAdminException(Exception):
    pass


class GetAllGamesAdminResponseModel:
    def __init__(self, game_list):
        self.game_list = game_list

    def __call__(self):
        return self.game_list


class GetAllGamesAdminInteractor:
    def __init__(self, console_adapter: ConsoleAdapter):
        self.console_adapter = console_adapter
        self.logger = logging.getLogger(__name__)

    def process_console_list_for_response(self, console_list: List[Console]):
        return [self.process_console_for_response(x) for x in console_list]

    def process_console_for_response(self, console: Console):
        return [self.format_game_for_response(console, x)
                for x in console.games]

    def format_game_for_response(self, console: Console, game: Game):
        return {
            'game_id': game.entity_id,
            'game_name': game.name,
            'game_logo_path': game.logo_path,
            'console_id': console.entity_id,
            'console_name': console.name}

    def run(self):
        try:
            all_consoles = self.console_adapter.list_all()
            game_list = self.process_console_list_for_response(all_consoles)
            response = GetAllGamesAdminResponseModel(game_list)
            return response
        except Exception as exc:
            msg = f'Error during get game list: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise GetAllGamesAdminException(msg)
