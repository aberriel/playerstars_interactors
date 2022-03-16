import logging
from playerstars_domain import Player, Team, Duel
from typing import List
from playerstars_adapters import (
    PlayerAdapter, TeamAdapter, DuelAdapter, ConsoleAdapter
)
from playerstars_domain import Console


class GetProfileRequestModel:
    def __init__(self,
                 player_id):
        self.player_id = player_id


class GetProfileResponseModel:
    def __init__(self, player, teams, duels, consoles):
        self.player = player
        self.teams = teams
        self.duels = duels
        self.consoles = consoles

    def __call__(self):
        return {
            'player': self.player,
            'teams': self.teams,
            'duels': self.duels,
            'consoles': self.consoles
        }


class GetProfileInteractor:
    def __init__(
            self, request, player_adapter, team_adapter, duel_adapter,
            console_adapter):
        self.request: GetProfileRequestModel = request
        self.player_adapter: PlayerAdapter = player_adapter
        self.team_adapter: TeamAdapter = team_adapter
        self.duel_adapter: DuelAdapter = duel_adapter
        self.console_adapter: ConsoleAdapter = console_adapter
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def check_if_member(team: Team, player_id):
        if team.captain.player_id == player_id:
            return True
        for member in team.members:
            if member.player_id == player_id:
                return True
        return False

    @staticmethod
    def check_if_participant(duel: Duel, player_id):
        if duel.challenger == player_id:
            return True
        if duel.challenged and duel.challenged == player_id:
            return True
        return False

    def filter_teams_by_player(
            self, all_teams: List[Team], player_id):
        player_teams = list()
        for team in all_teams:
            if self.check_if_member(team, player_id):
                player_teams.append(team.to_json())
        return player_teams

    def filter_duel_by_player(self, all_duels, player_id):
        player_duels = list()
        for duel in all_duels:
            if self.check_if_participant(duel, player_id):
                player_duels.append(duel.to_json())
        return player_duels

    @staticmethod
    def check_captain(team, player_id):
        if team['captain']['player_id'] == player_id:
            return True
        return False

    def format_team(self, teams, player_id):
        formated_teams = list()
        for team in teams:
            formated_teams.append({
                'name': team['name'],
                'image': "teste/testsa",
                'patent': 'CAPTAIN' if self.check_captain(
                    team, player_id) else 'MEMBER'
            })
        return formated_teams

    @staticmethod
    def format_duel(duels):
        formated_duels = list()
        already_added_games = list()
        for duel in duels:
            if duel['game']['entity_id'] not in already_added_games:
                already_added_games.append(duel['game']['entity_id'])
                formated_duels.append({
                    'game': duel['game']['name'],
                    'gameImage': duel['game']['logo_path']
                })
        return formated_duels

    def get_consoles_data(self, consoles):
        console_list = list()
        for item in consoles:
            console: Console = self.console_adapter.get_by_id(item.console_id)
            console_list.append({
                "entity_id": console.entity_id,
                "name": console.name,
                "logo_path": console.logo_path,
                "tag_name": item.tag_name,
                "games": console.to_json()['games']
            })
        return console_list

    def run(self):
        player: Player = self.player_adapter.get_by_id(self.request.player_id)
        player_formated = player.to_json()
        player_formated.update({"wins": 120})

        all_teams: List[Team] = self.team_adapter.list_all()
        team_list = self.filter_teams_by_player(
            all_teams, self.request.player_id)

        # team_list: List[Team] = self.team_adapter.filter(
        #     members__contains=self.request.player_id,
        #     captain_entity_id__eq=self.request.player_id)
        team_formated_list = self.format_team(
            team_list, self.request.player_id)
        all_duels: List[Duel] = self.duel_adapter.list_all()
        duel_list = self.filter_duel_by_player(
            all_duels, self.request.player_id)
        duel_formated_list = self.format_duel(duel_list)

        consoles_list = self.get_consoles_data(player.consoles)

        response = GetProfileResponseModel(
            player_formated, team_formated_list, duel_formated_list,
            consoles_list
        )
        return response()
