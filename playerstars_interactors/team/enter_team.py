from playerstars_domain import Team, Player
import logging


class EnterTeamException(Exception):
    pass


class EnterTeamRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.team_id = json_data['team_id']


class EnterTeamResponseModel:
    def __init__(self, team_id):
        self.team_id = team_id

    def __call__(self):
        return self.team_id


class EnterTeamInteractor:
    def __init__(self,
                 request: EnterTeamRequestModel,
                 player_adapter,
                 team_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def _recover_team(self, team_id):
        team: Team = self.team_adapter.get_by_id(team_id)
        team.set_adapter(self.team_adapter)
        return team

    def _recover_player(self, player_id):
        player: Player = self.player_adapter.get_by_id(player_id)
        player.set_adapter(self.player_adapter)
        return player

    def run(self):
        player: Player = self._recover_player(self.request.player_id)

        team: Team = self._recover_team(self.request.team_id)

        team.add_member(player)
        team.set_adapter(self.team_adapter)
        try:
            altered_team_id = team.save()
            response = EnterTeamResponseModel(altered_team_id)
            return response()
        except Exception as exc:
            msg = 'Erro ao salvar novo player no time: {}'.format(exc)
            self.logger.error(msg)
            raise EnterTeamException(msg)
