from playerstars_domain import Team
from playerstars_interactors.utils.pagination_utils import (
    get_partial_range, get_page_list)
from typing import List
import logging


class GetTeamsRankingRequestModel:
    def __init__(self, params, playerd_id):
        self.console_id = params.get('console_id', None)
        self.game_id = params.get('game_id', None)
        self.pagination_page = int(params.get('pagination_page', 1))
        self.pagination_per_page = int(
            params.get('pagination_per_page', 10))
        self.player_id = playerd_id


class GetTeamsRankingResponseModel:
    def __init__(self, teams, range_data):
        self.teams = teams
        self.range_data = range_data

    def __call__(self):
        return self.teams, self.range_data


class GetTeamsRankingInteractor:
    def __init__(self, request: GetTeamsRankingRequestModel,
                 team_adapter):
        self.request = request
        self.team_adapter = team_adapter
        self.team_info = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def sort_key(elem):
        return elem.victories

    def order_teams(self, teams: List[Team]):
        return sorted(teams, key=self.sort_key, reverse=True)

    def format_response(self, player_id, teams: List[Team]):
        position = 1
        formated_teams = list()
        previous_team = None
        for team in teams:
            victories = team.victories
            if previous_team and victories == previous_team['victories']:
                position = previous_team['position']
            member_id_list = [x.player_id for x in team.get_active_members()]
            team_info = {
                "position": position,
                "entity_id": team.entity_id,
                "team_logo": team.logo_path,
                "team_name": team.name,
                "victories": victories,
                "is_member": player_id in member_id_list,
                "elo_rating": team.elo_rating}
            if player_id in member_id_list:
                self.team_info = team_info
            formated_teams.append(team_info)
            previous_team = team_info
            position = position + 1
        return formated_teams

    def run(self):
        self.logger.info("COMEÇANDO GET RANKING TEAM")

        teams: List[Team] = self.team_adapter.filter(
            game_id__eq=self.request.game_id)
        self.logger.info("lista de times")

        ordered_teams = self.order_teams(teams)
        self.logger.info("lista de players filtrada e ordenada")

        formated_response = self.format_response(
            self.request.player_id, ordered_teams)
        self.logger.info("resposta formatada")

        page_list = get_page_list(
            self.request.pagination_page, self.request.pagination_per_page,
            formated_response)

        range_data = get_partial_range(
            teams, self.request.pagination_page,
            self.request.pagination_per_page, 'ranking')

        response = GetTeamsRankingResponseModel(
            page_list, range_data)
        self.logger.info("response")
        return response()
