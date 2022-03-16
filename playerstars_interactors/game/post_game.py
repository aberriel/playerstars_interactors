from playerstars_domain import Game, Console
from typing import List

import logging


class SaveGameException(BaseException):
    pass


class PostGameRequestModel:
    def __init__(self, json_data: dict):
        self.name = json_data['name']
        self.logo_path = json_data['logo_path']
        self.consoles = json_data['consoles']


class PostGameResponseModel:
    def __init__(self, saved_id):
        self.saved_id = saved_id

    def __call__(self):
        return self.saved_id


class PostGameInteractor:
    def __init__(self,
                 request: PostGameRequestModel,
                 adapter_instance,
                 entity_class):
        self.request = request
        self.adapter_instance = adapter_instance
        self.entity_class = entity_class
        self.logger = logging.getLogger(__name__)

    def _init_game(self):
        game = Game(name=self.request.name,
                    logo_path=self.request.logo_path)
        return game

    def _init_consoles(self):
        consoles = list()
        game: Game = self._init_game()
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
                    PostGameResponseModel(updated_console)())
            except Exception as e:
                msg = f'Erro salvando game:{e}'
                self.logger.error(msg)
                raise SaveGameException(msg)
        return response_list
