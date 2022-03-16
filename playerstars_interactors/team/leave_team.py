from playerstars_adapters import TeamAdapter
from playerstars_domain import Team
from playerstars_interactors.utils.domain_utils import find_entity_by_id

import logging


class LeaveTeamException(BaseException):
    pass


class LeaveTeamRequestModel:
    def __init__(self,
                 json_data: dict):
        self.team_id = json_data.get('team_id')
        self.player_id = json_data.get('player_id')


class LeaveTeamResponseModel:
    def __init__(self, team_id):
        self.team_id = team_id

    def __call__(self):
        return self.team_id


class LeaveTeamInteractor:
    team = None

    def __init__(self,
                 request: LeaveTeamRequestModel,
                 team_adapter: TeamAdapter):
        self.request = request
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def get_team(self):
        self.team: Team = find_entity_by_id(
            _id=self.request.team_id,
            adapter_instance=self.team_adapter,
            class_name='Team')

    def run(self):
        try:
            self.get_team()
            if self.team.captain.player_id != self.request.player_id:
                self.team.leave_team(self.request.player_id)
                self.team.save()
            else:
                self.team.delete()
            response = LeaveTeamResponseModel(self.team.entity_id)
            return response()
        except Exception as exc:
            msg = 'Error during leave team: {0}'.format(exc)
            self.logger.error(msg)
            raise LeaveTeamException(msg)
