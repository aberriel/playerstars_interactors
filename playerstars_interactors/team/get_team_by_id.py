from playerstars_domain import Console, Team, Player, Game
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_domain.team.team import TeamStatus


class GetTeamRequestModel:
    def __init__(self, entity_id):
        self.entity_id = entity_id


class GetTeamResponseModel:
    def __init__(self, entity):
        self.entity = entity

    def __call__(self):
        return self.entity if self.entity else None


class GetTeamInteractor:
    def __init__(self,
                 request: GetTeamRequestModel,
                 team_adapter, player_adapter, console_adapter):
        self.request = request
        self.team_adapter = team_adapter
        self.player_adapter = player_adapter
        self.console_adapter = console_adapter

    def format_team(self, team: Team):
        formated_team = team.to_json()
        formated_members = list()
        for member in team.members:
            new_member = member.to_json()
            player_data: Player = find_entity_by_id(
                member.player_id, self.player_adapter, 'Player')
            new_member.update({"player_photo": player_data.user.profile_image,
                               "player_nickname": player_data.user.nickname})
            formated_members.append(new_member)
        formated_team['members'] = formated_members

        console_data: Console = find_entity_by_id(
            team.console_id, self.console_adapter, 'Console')

        game_data: Game = console_data.find_game_by_id(team.game_id)

        formated_team.update({'console_name': console_data.name,
                              'game_name': game_data.name})
        return formated_team

    def run(self):
        team: Team = self.team_adapter.get_by_id(self.request.entity_id)
        formated_team = self.format_team(team) \
            if team and team.status == TeamStatus.ACTIVE else None
        response = GetTeamResponseModel(formated_team)
        return response()
