from playerstars_domain import Player, Console
from typing import List


class GetFriendsByConsoleGameRequestModel:
    def __init__(self, query_params):
        self.player_id = query_params.get('player_id')
        self.console_id = query_params.get('console_id')
        self.game_id = query_params.get('game_id')


class GetFriendsByConsoleGameResponseModel:
    def __init__(self, players):
        self.players = players

    def __call__(self):
        return self.players if self.players else []


class GetFriendsByConsoleGameInteractor:
    def __init__(self, request: GetFriendsByConsoleGameRequestModel,
                 player_adapter, console_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.console_adapter = console_adapter

    def filter_by_console_game(self, players_ids: List[str]):
        filtered_players = list()
        console: Console = self.console_adapter.get_by_id(
            self.request.console_id)
        for player_id in players_ids:
            player: Player = self.player_adapter.get_by_id(player_id)
            console_list = player.console_list()
            if self.request.console_id in console_list and\
                    console.find_game_by_id(self.request.game_id):
                filtered_players.append(player)
        return filtered_players

    def get_tag_name(self, player):
        for console in player.consoles:
            if console.console_id == self.request.console_id:
                return console.tag_name

    def format_friends(self, players):
        favorite_list = list()
        for player in players:
            favorite_list.append({
                'entity_id': player.entity_id,
                'name': player.user.name,
                'photo': player.user.profile_image,
                'nickname': player.user.nickname,
                'tag_name': self.get_tag_name(player)
            })
        return favorite_list

    def run(self):
        player: Player = self.player_adapter.get_by_id(
            self.request.player_id)
        filtered_players = self.filter_by_console_game(player.favorites)
        formated_players = self.format_friends(filtered_players)
        response = GetFriendsByConsoleGameResponseModel(formated_players)
        return response()
