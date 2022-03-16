from playerstars_adapters import (
    NotificationAdapter,
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    MemberStatus,
    MemberType,
    NotificationType,
    Team,
    TeamMember)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_interactors.utils.notification_utils import \
    create_notification
from playerstars_interactors.utils.upload_photos import \
    upload_photo_and_return_url
from typing import List
import logging


class UpdateTeamException(BaseException):
    pass


class DuplicateMemberException(BaseException):
    pass


class PutTeamRequestModel:
    def __init__(self, json_data):
        self.entity_id = json_data.get("entity_id")
        self.name = json_data.get("name", None)
        self.members: List[str] = json_data.get('members', [])
        self.console_id: str = json_data.get('console_id', None)
        self.description = json_data.get('description', None)
        self.image_base64 = json_data.get('image_base64', '')
        self.game_id = json_data.get('game_id', None)


class PutTeamResponseModel:
    def __init__(self,
                 saved_id: str):
        self.saved_id = saved_id

    def __call__(self):
        return self.saved_id


class PutTeamAdapters:
    def __init__(self, notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter):
        self.notification_adapter = notification_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter


class PutTeamInteractor:
    saved_team = None

    def __init__(self,
                 request: PutTeamRequestModel,
                 adapters: PutTeamAdapters,
                 s3_bucket_name: str,
                 s3_bucket_url: str):
        self.request = request
        self.adapters = adapters
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_url = s3_bucket_url
        self.logger = logging.getLogger(__name__)

    def get_saved_team(self):
        return find_entity_by_id(
            _id=self.request.entity_id,
            adapter_instance=self.adapters.team_adapter,
            class_name='Team')

    def find_member_old_team(self, member_id: str):
        member_obj = None
        if self.saved_team.captain.player_id == member_id:
            raise UpdateTeamException(f'Member {member_id} is team leader')
        else:
            for member in self.saved_team.members:
                if member.player_id == member_id:
                    member_obj = member
        return member_obj

    def get_member(self, member_id):
        return find_entity_by_id(
            _id=member_id,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

    def mount_member_list(self, members: List[str]):
        member_list = list()
        unique_members = list()
        for member_id in members:
            if member_id not in unique_members:
                member_obj = self.get_member(member_id)
                if not member_obj:
                    raise Exception(f'Player {member_id} not found')

                association_date = aware_now()
                status = MemberStatus.INVITED

                saved_member = self.find_member_old_team(member_id)

                if saved_member:
                    association_date = saved_member.association_date
                    status = saved_member.status

                team_member = TeamMember(
                    player_id=member_obj.entity_id,
                    association_date=association_date,
                    member_type=MemberType.MEMBER,
                    status=status)
                unique_members.append(member_id)
                member_list.append(team_member)
        return member_list

    def invite_new_members(self, team: Team):
        old_members = self.saved_team.members
        old_members_id_list = [x.player_id for x in old_members]
        for member in team.members:
            if member.player_id not in old_members_id_list:
                self.invite_new_member(
                    member_id=member.player_id,
                    team=team)

    def invite_new_member(self, member_id: str, team: Team):
        member_obj = self.get_member(member_id)
        create_notification(
            player_data=member_obj,
            notification_adapter=self.adapters.notification_adapter,
            notification_type=NotificationType.TEAM_INVITE,
            team_id=team.entity_id,
            notification_image=team.logo_path,
            notification_complement=team.name,
            logger_instance=self.logger)

    def init_team(self, old_team: Team):
        member_list = self.mount_member_list(self.request.members)
        logo_path = None
        if self.request.image_base64:
            logo_path = upload_photo_and_return_url(
                sent_image=self.request.image_base64,
                unique_name=self.request.entity_id,
                s3_bucket_name=self.s3_bucket_name,
                s3_bucket_url=self.s3_bucket_url)
        team = Team(
            name=self.request.name or old_team.name,
            captain=old_team.captain,
            members=member_list,
            console_id=self.request.console_id or old_team.console_id,
            entity_id=self.request.entity_id,
            description=self.request.description or old_team.description,
            game_id=self.request.game_id or old_team.game_id,
            logo_path=logo_path or old_team.logo_path
        )
        self.invite_new_members(team)
        return team

    def check_member_list_duplicates(self):
        for elem in self.request.members:
            if self.request.members.count(elem) > 1:
                msg = f'Member {elem} has more than on entry.'
                raise DuplicateMemberException(msg)

    def persist_team(self, team: Team):
        team.set_adapter(self.adapters.team_adapter)
        team.save()

    def run(self):
        try:
            self.saved_team = self.get_saved_team()
            self.check_member_list_duplicates()
            team = self.init_team(self.saved_team)
            self.persist_team(team)
            return PutTeamResponseModel(team.entity_id)
        except Exception as e:
            msg = f'Team update error: {e}'
            self.logger.error(msg)
            raise UpdateTeamException(msg)
