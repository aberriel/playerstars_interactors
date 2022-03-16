from playerstars_domain import Game, Console
from typing import List


class GetAllGamesRequestModel:
    def __init__(self, console_id):
        self.console_id = console_id


class GetAllGamesResponseModel:
    def __init__(self, games: List[Game]):
        self.games = games

    def __call__(self):
        return [x.to_json() for x in self.games]


class GetAllGamesInteractor:
    def __init__(self,
                 request: GetAllGamesRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance

    @staticmethod
    def _get_game_list(console: Console):
        return [game for game in console.games]

    def run(self):
        console: Console = self.adapter_instance.get_by_id(
            self.request.console_id)
        if not console:
            return dict()
        games_list = self._get_game_list(console)
        response = GetAllGamesResponseModel(games_list)
        return response()
