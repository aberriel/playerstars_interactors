import logging


class GetOpponentTeamsException(BaseException):
    pass


class GetOpponentTeamsRequestModel:
    def __init__(self, query_params):
        self.team_id = query_params.get('team_id')
        self.console_id = query_params.get('console_id')
        self.game_id = query_params.get('game_id')


class GetOpponentTeamsResponseModel:
    def __init__(self, teams):
        self.teams = teams

    def __call__(self):
        return self.teams if self.teams else []


class GetOpponentTeamsInteractor:
    def __init__(self, request: GetOpponentTeamsRequestModel,
                 player_adapter, team_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def get_tag_name(self, player):
        for console in player.consoles:
            if console.console_id == self.request.console_id:
                return console.tag_name

    def format_teams(self, teams):
        formated_list = list()
        for team in teams:
            captain = self.player_adapter.get_by_id(team.captain.player_id)
            if not captain:
                raise BaseException(f"Captain id {team.captain.player_id} "
                                    f"not found in team {team.entity_id}")
            formated_list.append({
                'entity_id': team.entity_id,
                'name': team.name,
                'photo': team.logo_path,
                'nickname': captain.user.nickname,
                'tag_name': self.get_tag_name(captain)
            })
        return formated_list

    def exclude_creating_team(self, teams):
        return [x for x in teams if x.entity_id != self.request.team_id]

    def exclude_teams_with_same_captain(self, teams):
        main_team = self.team_adapter.get_by_id(self.request.team_id)
        return [x for x in teams if
                x.captain.player_id != main_team.captain.player_id]

    def run(self):
        try:
            teams = self.team_adapter.filter(game_id__eq=self.request.game_id)
            teams = self.exclude_creating_team(teams)
            teams = self.exclude_teams_with_same_captain(teams)
            formated_teams = self.format_teams(teams)
            response = GetOpponentTeamsResponseModel(formated_teams)
            return response
        except BaseException as exc:
            msg = f'Error during recovery opponents list: {exc}'
            self.logger.error(msg)
            raise GetOpponentTeamsException(msg)
