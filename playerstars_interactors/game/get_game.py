from playerstars_domain import Console, Game
from typing import List


class GetGameRequestModel:
    def __init__(self, entity_id):
        self.entity_id = entity_id


class GetGameResponseModel:
    def __init__(self, game: Game):
        self.game = game

    def __call__(self):
        return self.game.to_json() if self.game else None


class GetGameInteractor:
    def __init__(self,
                 request: GetGameRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance

    def get_game_from_console_list(self, console_list):
        for console in console_list:
            for game in console.games:
                if game.entity_id == self.request.entity_id:
                    return game

    def run(self):
        console_list: List[Console] = self.adapter_instance.list_all()
        game = self.get_game_from_console_list(console_list)
        response = GetGameResponseModel(game)
        return response()
