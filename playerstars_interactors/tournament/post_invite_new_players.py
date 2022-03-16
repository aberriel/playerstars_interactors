from playerstars_domain import (
    DuelMemberType as MemberType, TournamentMember,
    TournamentMemberStatus, NotificationType
)
from playerstars_interactors.tournament.tournament_utils import (
    send_invites, report_failed_invites
)
import logging


class PostInviteNewPlayersError(BaseException):
    pass


class PostInviteNewPlayersRequestModel:
    def __init__(self, player_id, member_type,
                 data, team_id=None):
        self.player_id = player_id
        self.member_type: MemberType = member_type
        self.tournament_id = data.get('tournament_id')
        self.new_players = data.get('new_players')
        self.team_id = team_id


class PostInviteNewPlayersResponseModel:
    def __init__(self, tournament):
        self.tournament = tournament

    def __call__(self, *args, **kwargs):
        return self.tournament.to_json() if self.tournament else None


class PostInviteNewPlayersAdapters:
    def __init__(self,
                 player_adapter,
                 team_adapter,
                 player_tournament_adapter,
                 team_tournament_adapter,
                 notification_gql):
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.player_tournament_adapter = player_tournament_adapter
        self.team_tournament_adapter = team_tournament_adapter
        self.notification_gql = notification_gql


class PostInviteNewPlayersInteractor:
    def __init__(self, request: PostInviteNewPlayersRequestModel,
                 adapters: PostInviteNewPlayersAdapters, logger=None):
        self.request = request
        self.adapters = adapters
        self.logger = logger or logging.getLogger(__name__)

    def add_new_members(self, tournament):
        for new_player in self.request.new_players:
            tournament.members.append(TournamentMember(
                member_id=new_player,
                status=TournamentMemberStatus.INVITED
            ))
        return tournament

    def get_tournament_adapter(self):
        adapter_map = {
            MemberType.PLAYER: self.adapters.player_tournament_adapter,
            MemberType.TEAM: self.adapters.team_tournament_adapter
        }

        return adapter_map[self.request.member_type]

    def run(self):
        tournament_adapter = self.get_tournament_adapter()
        tournament = tournament_adapter.get_by_id(self.request.tournament_id)

        tournament = self.add_new_members(tournament)

        tournament.set_adapter(tournament_adapter)
        tournament.save()
        failed_invites = send_invites(
            players=self.request.new_players,
            tournament=tournament,
            logo_path=tournament.game.logo_path,
            notification_adapter=self.adapters.notification_gql,
            notification_type=NotificationType.CHAMPIONSHIP_INVITE_PLAYER)
        report_failed_invites(
            tournament_id=tournament.entity_id,
            failed_invites=failed_invites,
            logger=self.logger)
        response = PostInviteNewPlayersResponseModel(tournament)
        return response
