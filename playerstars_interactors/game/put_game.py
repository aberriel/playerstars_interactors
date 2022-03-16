from playerstars_domain.game import Game
from playerstars_domain.console import Console
from typing import List

import logging

default_logger = logging.getLogger(__name__)


class UpdateGameException(BaseException):
    pass


class PutGameRequestModel:
    def __init__(self, json_data: dict):
        self.name = json_data['name']
        self.entity_id = json_data['entity_id']
        self.logo_path = json_data['logo_path']
        self.consoles = json_data['consoles']


class PutGameResponseModel:
    def __init__(self, updated_id):
        self.updated_id = updated_id

    def __call__(self):
        return self.updated_id


class PutGameInteractor:
    def __init__(self,
                 request: PutGameRequestModel,
                 adapter_instance,
                 entity_class):
        self.request = request
        self.adapter_instance = adapter_instance
        self.entity_class = entity_class
        self.logger = logging.getLogger(__name__)

    def _init_game(self):
        game = Game(
            entity_id=self.request.entity_id,
            name=self.request.name,
            logo_path=self.request.logo_path)
        return game

    def _init_consoles(self):
        game: Game = self._init_game()
        consoles = list()
        for request_console in self.request.consoles:
            console = Console(
                entity_id=request_console['entity_id'],
                name=request_console['name'],
                logo_path=request_console['logo_path'],
                tag_name=request_console['tag_name'],
                games=request_console['games'] if 'games' in request_console
                else []
            )
            console.games.append(game)
            consoles.append(console)
        return consoles

    def run(self):
        consoles: List[Console] = self._init_consoles()
        response_list = list()
        for console in consoles:
            console.set_adapter(self.adapter_instance)
            try:
                updated_console = console.update()
                response_list.append(
                    PutGameResponseModel(updated_console)())
            except Exception as e:
                msg = f'Erro salvando game:{e}'
                default_logger.error(msg)
                raise UpdateGameException(msg)
        return response_list
