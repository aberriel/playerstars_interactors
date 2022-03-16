from playerstars_domain import Team
from typing import List


class GetMyTeamsByGameRequestModel:
    def __init__(self, query_params):
        self.player_id = query_params.get('player_id')
        self.console_id = query_params.get('console_id')
        self.game_id = query_params.get('game_id')


class GetMyTeamsByGameResponseModel:
    def __init__(self, teams):
        self.teams = teams

    def __call__(self):
        return self.teams if self.teams else []


class GetMyTeamsByGameInteractor:
    def __init__(self, request: GetMyTeamsByGameRequestModel,
                 player_adapter, team_adapter, console_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.console_adapter = console_adapter

    def filter_by_player(self, teams: List[Team]):
        filtered_teams = list()
        for team in teams:
            if self.request.player_id in team.captain.player_id:
                filtered_teams.append(team)
        return filtered_teams

    def get_tag_name(self, player):
        for console in player.consoles:
            if console.console_id == self.request.console_id:
                return console.tag_name

    def format_teams(self, teams):
        formated_list = list()
        for team in teams:
            captain = self.player_adapter.get_by_id(team.captain.player_id)
            formated_list.append({
                'entity_id': team.entity_id,
                'name': team.name,
                'photo': team.logo_path,
                'nickname': captain.user.nickname,
                'tag_name': self.get_tag_name(captain)
            })
        return formated_list

    def run(self):
        teams = self.team_adapter.filter(game_id__eq=self.request.game_id)
        teams_with_player = self.filter_by_player(teams)
        formated_teams = self.format_teams(teams_with_player)
        response = GetMyTeamsByGameResponseModel(formated_teams)
        return response()
