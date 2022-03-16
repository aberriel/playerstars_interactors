from playerstars_adapters import (
    NotificationAdapter,
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    MemberStatus, MemberType,
    NotificationType, Team, TeamMember)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.utils.notification_utils import \
    create_notification
from playerstars_interactors.utils.upload_photos import \
    upload_photo_and_return_url

import logging
import uuid


default_logger = logging.getLogger(__name__)


class SaveTeamException(BaseException):
    pass


class PostTeamRequestModel:
    def __init__(self, json_data):
        self.name = json_data.get('name')
        self.captain = json_data.get('captain')
        self.members = json_data.get('members')
        self.description = json_data.get('description', '')
        self.image_base64 = json_data.get('image_base64', None)
        self.console_id = json_data.get('console_id')
        self.game_id = json_data.get('game_id')


class PostTeamResponseModel:
    def __init__(self, saved_id):
        self.saved_id = saved_id

    def __call__(self):
        return self.saved_id


class PostTeamInteractor:
    team = None

    def __init__(self,
                 request: PostTeamRequestModel,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter,
                 notification_adapter: NotificationAdapter,
                 s3_bucket_name: str,
                 s3_bucket_url: str):
        self.request = request
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.notification_adapter = notification_adapter
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_url = s3_bucket_url
        self.logger = logging.getLogger(__name__)

    def get_member(self, member_id):
        return self.player_adapter.get_by_id(member_id)

    def _init_captain(self):
        return self._init_member(
            member_id=self.request.captain,
            member_type=MemberType.CAPTAIN,
            member_status=MemberStatus.ACCEPTED)

    def _init_member(self, member_id: str,
                     member_type: MemberType,
                     member_status: MemberStatus):
        member = self.get_member(member_id)
        if not member:
            raise Exception('Team member {0} {1} not found'
                            .format(member_type.value,
                                    self.request.captain))
        return TeamMember(
            player_id=member_id,
            member_type=member_type,
            status=member_status,
            association_date=aware_now(),
            last_status_change_datetime=aware_now())

    def mount_member_list(self, members):
        member_list = []
        unique_members = list()
        for member_id in members:
            if member_id not in unique_members:
                team_member = self._init_member(
                    member_id=member_id,
                    member_type=MemberType.MEMBER,
                    member_status=MemberStatus.INVITED)
                member_list.append(team_member)
                unique_members.append(member_id)
        return member_list

    def invite_members(self, team):
        invited_members = [x for x in team.members
                           if x.status == MemberStatus.INVITED]
        for member in invited_members:
            self.invite_member(member_data=member,
                               team=team)

    def invite_member(self, member_data, team: Team):
        player_data = self.get_member(member_data.player_id)
        create_notification(
            player_data=player_data,
            notification_adapter=self.notification_adapter,
            notification_type=NotificationType.TEAM_INVITE,
            notification_image=team.logo_path,
            notification_complement=team.name,
            team_id=team.entity_id,
            logger_instance=self.logger)

    def _upload_team_image(self, team):
        if self.request.image_base64:
            return upload_photo_and_return_url(
                sent_image=self.request.image_base64,
                unique_name=team.entity_id,
                s3_bucket_name=self.s3_bucket_name,
                s3_bucket_url=self.s3_bucket_url)
        return None

    def check_request_data(self):
        if not self.request.captain:
            raise Exception('Team leader was not provided')
        if not self.request.console_id:
            raise Exception('Team console was not provided')
        if not self.request.game_id:
            raise Exception('Team game was not provided')
        return True

    def _init_team(self):
        captain = self._init_captain()
        member_list = self.mount_member_list(self.request.members)
        team = Team(entity_id=str(uuid.uuid4()),
                    name=self.request.name,
                    captain=captain,
                    members=member_list,
                    description=self.request.description,
                    game_id=self.request.game_id,
                    console_id=self.request.console_id)
        team.logo_path = self._upload_team_image(team)
        return team

    def _save_team(self, team):
        team.set_adapter(self.team_adapter)
        return team.save()

    def run(self):
        try:
            self.check_request_data()
            team = self._init_team()
            self.invite_members(team)
            saved_id = self._save_team(team)
            return PostTeamResponseModel(saved_id)
        except Exception as e:
            msg = 'Error during team creation: {}'.format(e)
            default_logger.error(msg)
            raise SaveTeamException(msg)
