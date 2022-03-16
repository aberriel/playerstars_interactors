from playerstars_domain import Player, Console
from playerstars_interactors.utils.pagination_utils import (
    get_partial_range, get_page_list)
from typing import List
import logging


class GetRankingByConsoleGameRequestModel:
    def __init__(self, query_params, playerd_id):
        self.console_id = query_params.get('console_id', None)
        self.game_id = query_params.get('game_id', None)
        self.pagination_page = int(query_params.get('pagination_page', 1))
        self.pagination_per_page = int(
            query_params.get('pagination_per_page', 10))
        self.player_id = playerd_id


class GetRankingByConsoleGameResponseModel:
    def __init__(self, players, range_data):
        self.players = players
        self.range_data = range_data

    def __call__(self):
        return self.players, self.range_data


class GetRankingByConsoleGameInteractor:
    def __init__(self, request: GetRankingByConsoleGameRequestModel,
                 player_adapter, console_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.console_adapter = console_adapter
        self.player_info = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

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

    def sort_key(self, elem):
        return elem.get_game_elo_rating_by_id(self.request.game_id)

    def order_by_ranking(self, players: List[Player]):
        return sorted(players, key=self.sort_key, reverse=True)

    def format_response(self, player_id, players: List[Player]):
        position = 1
        users = list()
        previous_player = None
        for player in players:
            victories = player.get_game_victories_by_id(self.request.game_id)
            elo_rating = player.get_game_elo_rating_by_id(self.request.game_id)
            if previous_player and elo_rating == previous_player['elo_rating']:
                new_position = previous_player['position']
            else:
                new_position = position
            player_info = {
                "position": new_position,
                "profile_image": player.user.profile_image,
                "user_name": player.user.nickname,
                "victories": victories,
                "is_himself": player.entity_id == player_id,
                "elo_rating": elo_rating}
            if player.entity_id == player_id:
                self.player_info = player_info
            users.append(player_info)
            previous_player = player_info
            position = position + 1
        return users

    def add_player_to_page_if_not_there(self, page_list):
        found = False
        for item in page_list:
            if item['is_himself']:
                found = True
        if not found and self.player_info and page_list[0]['position'] and\
                self.player_info['position'] < page_list[0]['position']:
            page_list.insert(0, self.player_info)
        if not found and self.player_info and page_list[-1]['position'] and\
                self.player_info['position'] > page_list[-1]['position']:
            page_list.append(self.player_info)
        return page_list

    def run(self):
        self.logger.info("COMEÇANDO GET RANKING")

        players: List[Player] = self.player_adapter.list_all()
        self.logger.info("lista de players")

        filtered_players = self.filter_by_console_game(players)
        self.logger.info("lista de players filtrada")
        for player in filtered_players:
            self.logger.info("player: " + str(player.to_json()))
            self.logger.info("player game points: " + str(
                player.get_game_victories_by_id(self.request.game_id)))
        ordered_players = self.order_by_ranking(filtered_players)
        self.logger.info("lista de players filtrada e ordenada")

        formated_response = self.format_response(
            self.request.player_id, ordered_players)
        self.logger.info("resposta formatada")

        page_list = get_page_list(
            self.request.pagination_page, self.request.pagination_per_page,
            formated_response)

        page_list_with_player = self.add_player_to_page_if_not_there(
            page_list)

        range_data = get_partial_range(
            filtered_players, self.request.pagination_page,
            self.request.pagination_per_page, 'ranking')

        response = GetRankingByConsoleGameResponseModel(
            page_list_with_player, range_data)
        self.logger.info("response")
        return response()
