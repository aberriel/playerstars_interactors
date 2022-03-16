from playerstars_domain import Player
from typing import List
import logging


class GetFriendsNotInvitedError(BaseException):
    pass


class GetFriendsNotInvitedRequestModel:
    def __init__(self, player_id, tournament_id):
        self.player_id = player_id
        self.tournament_id = tournament_id


class GetFriendsNotInvitedResponseModel:
    def __init__(self, players):
        self.players = players

    def __call__(self, *args, **kwargs):
        return self.players if self.players else []


class GetFriendsNotInvitedAdapters:
    def __init__(self,
                 player_adapter,
                 player_tournament_adapter,
                 console_adapter):
        self.player_adapter = player_adapter
        self.player_tournament_adapter = player_tournament_adapter
        self.console_adapter = console_adapter


class GetFriendsNotInvitedInteractor:
    def __init__(self, request: GetFriendsNotInvitedRequestModel,
                 adapters: GetFriendsNotInvitedAdapters):
        self.request = request
        self.adapters = adapters
        self.logger = logging.getLogger(__name__)

    def filter_by_console_game(
            self, players_ids: List[str], tournament, console):
        filtered_players = list()
        for player_id in players_ids:
            player: Player = self.adapters.player_adapter.get_by_id(player_id)
            console_list = player.console_list()
            if tournament.console.entity_id in console_list and\
                    console.find_game_by_id(tournament.game.entity_id):
                filtered_players.append(player)
        return filtered_players

    @staticmethod
    def get_tag_name(player, console_id):
        for console in player.consoles:
            if console.console_id == console_id:
                return console.tag_name

    def format_friends(self, players, console_id):
        favorite_list = list()
        for player in players:
            favorite_list.append({
                'entity_id': player.entity_id,
                'name': player.user.name,
                'photo': player.user.profile_image,
                'nickname': player.user.nickname,
                'tag_name': self.get_tag_name(player, console_id)
            })
        return favorite_list

    @staticmethod
    def filter_already_invited(friends, tournament):
        invited = [x.member_id for x in tournament.members]
        return [x for x in friends if x.entity_id not in invited]

    def run(self):
        tournament = self.adapters.player_tournament_adapter.get_by_id(
            self.request.tournament_id)
        if not tournament:
            raise GetFriendsNotInvitedError(
                f'Tournament {self.request.tournament_id} not found in'
                f' player tournaments')
        player = self.adapters.player_adapter.get_by_id(
            self.request.player_id)
        console = self.adapters.console_adapter.get_by_id(
            tournament.console.entity_id)

        filtered_friends = self.filter_by_console_game(
            players_ids=player.favorites,
            console=console,
            tournament=tournament)

        filtered_friends = self.filter_already_invited(
            filtered_friends, tournament)
        formated_friends = self.format_friends(
            filtered_friends, tournament.console.entity_id)
        response = GetFriendsNotInvitedResponseModel(formated_friends)
        return response
