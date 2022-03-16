from playerstars_adapters import TeamAdapter
from playerstars_domain import Team
from playerstars_domain.team.team import TeamStatus
from playerstars_interactors.utils.domain_utils import (
    find_entity_by_id,
    EntityNotFoundException
)

import logging


class DeleteTeamException(BaseException):
    pass


class DeleteTeamRequestModel:
    def __init__(self, json_data):
        self.team_id = json_data.get('team_id')
        self.player_id = json_data.get('player_id')


class DeleteTeamResponseModel:
    def __init__(self, deleted_id):
        self.deleted_id = deleted_id

    def __call__(self):
        return self.deleted_id


class DeleteTeamInteractor:
    team = None

    def __init__(self,
                 request: DeleteTeamRequestModel,
                 team_adapter: TeamAdapter):
        self.request = request
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def set_team_as_inactive(self):
        self.team.status = TeamStatus.INACTIVE
        self.team.set_adapter(self.team_adapter)
        self.team.save()

    def check_rights(self):
        if self.team.captain.player_id != self.request.player_id:
            raise Exception("You aren't the team's captain")

    def get_team(self):
        self.team: Team = find_entity_by_id(
            _id=self.request.team_id,
            adapter_instance=self.team_adapter,
            class_name='Team')

    def run(self):
        try:
            self.get_team()
            self.check_rights()
            self.set_team_as_inactive()
            response = DeleteTeamResponseModel(self.request.team_id)
            return response()
        except (Exception, EntityNotFoundException) as ex:
            msg = f'Error during team exclusion: {ex}'
            self.logger.error(msg)
            raise DeleteTeamException(msg)
