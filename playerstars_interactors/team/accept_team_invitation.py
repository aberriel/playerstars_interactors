from playerstars_adapters import TeamAdapter
from playerstars_domain import Team
from playerstars_interactors.utils.domain_utils import find_entity_by_id
import logging


class AcceptTeamInvitationException(Exception):
    pass


class AcceptTeamInvitationRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.team_id = json_data['team_id']
        self.accept_invite = json_data['accept_invite']


class AcceptTeamInvitationResponseModel:
    def __init__(self, team_id):
        self.team_id = team_id

    def __call__(self):
        return self.team_id


class AcceptTeamInvitationInteractor:
    def __init__(self,
                 request: AcceptTeamInvitationRequestModel,
                 team_adapter: TeamAdapter):
        self.request = request
        self.team_adapter = team_adapter
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            team: Team = find_entity_by_id(
                _id=self.request.team_id,
                adapter_instance=self.team_adapter,
                class_name='Team')
            team.member_invite_response(
                self.request.player_id, self.request.accept_invite)

            altered_team_id = team.save()
            response = AcceptTeamInvitationResponseModel(altered_team_id)
            return response()
        except Exception as exc:
            msg = f'Error when modifying the invitation status of player: ' \
                f'{self.request.player_id}, no time: {self.request.team_id}' \
                f'. {str(exc)}'
            self.logger.error(msg)
            raise AcceptTeamInvitationException(msg)
