from playerstars_domain import Player, Console
from typing import List


class GetPlayersByConsoleGameRequestModel:
    def __init__(self, query_params):
        self.console_id = query_params.get('console_id', None)
        self.game_id = query_params.get('game_id', None)


class GetPlayersByConsoleGameResponseModel:
    def __init__(self, players: List[Player]):
        self.players = players

    def __call__(self):
        return [x.to_json() for x in self.players]


class GetPlayersByConsoleGameInteractor:
    def __init__(self, request: GetPlayersByConsoleGameRequestModel,
                 player_adapter, console_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.console_adapter = console_adapter

    def filter_by_console_game(self, players: List[Player]):
        filtered_players = list()
        console: Console = self.console_adapter.get_by_id(
            self.request.console_id)
        for player in players:
            console_list = [x.console_id for x in player.consoles]
            if self.request.console_id in console_list and\
                    console.find_game_by_id(self.request.game_id):
                filtered_players.append(player)

        return filtered_players

    def run(self):
        players: List[Player] = self.player_adapter.list_all()
        filtered_players = self.filter_by_console_game(players)
        response = GetPlayersByConsoleGameResponseModel(filtered_players)
        return response()
