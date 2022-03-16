from playerstars_domain import DuelMemberType as MemberType
from playerstars_domain import (
    Tournament, Duel, DuelType, DuelStatus,
    CoinType, TournamentStatus, NotificationType, TournamentPhase)
from playerstars_interactors.tournament.tournament_utils import (
    send_invites, report_failed_invites, invite_member
)
from datetime import datetime
from typing import List
import logging
import random
import pytz


class PostTournamentStartError(BaseException):
    pass


class PostTournamentStartRequestModel:
    def __init__(self, player_id, member_type,
                 data, team_id=None):
        self.player_id = player_id
        self.member_type: MemberType = member_type
        self.tournament_id = data.get('tournament_id')
        self.team_id = team_id


class PostTournamentStartResponseModel:
    def __init__(self, tournament):
        self.tournament = tournament

    def __call__(self, *args, **kwargs):
        return self.tournament.to_json() if self.tournament else None


class PostTournamentStartAdapters:
    def __init__(self,
                 player_adapter,
                 team_adapter,
                 player_tournament_adapter,
                 team_tournament_adapter,
                 console_adapter,
                 duel_adapter,
                 notificationgql_adapter):
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.player_tournament_adapter = player_tournament_adapter
        self.team_tournament_adapter = team_tournament_adapter
        self.console_adapter = console_adapter
        self.duel_adapter = duel_adapter
        self.notificationgql_adapter = notificationgql_adapter


class PostTournamentStartInteractor:
    def __init__(self, request: PostTournamentStartRequestModel,
                 adapters: PostTournamentStartAdapters,
                 time_to_finish, logger=None):
        self.request = request
        self.adapters = adapters
        self.time_to_finish = time_to_finish
        self.tournament = None
        self.duel_list: List[str] = list()
        self.logger = logger or logging.getLogger(__name__)

    def save_tournament(self):
        self.tournament.set_adapter(self.adapters.player_tournament_adapter)
        self.tournament.save()

    def cancel_tournament(self):
        self.tournament.status = TournamentStatus.CANCELED
        self.save_tournament()

    def set_tournament_started(self):
        self.tournament.status = TournamentStatus.PHASE1
        self.save_tournament()

    def create_phase_one(self):
        phase_one = TournamentPhase(
            duels=self.duel_list,
            phase=TournamentStatus.PHASE1,
            start_datetime=datetime.utcnow().replace(tzinfo=pytz.utc)
        )
        self.tournament.phases.append(phase_one)

    def get_console(self, console_id):
        return self.adapters.console_adapter.get_by_id(console_id)

    @staticmethod
    def get_game(console, game_id):
        return console.find_game_by_id(game_id)

    @staticmethod
    def _prepare_console_to_duel(console_data):
        console_data.games = []
        return console_data

    def create_duel(self, challenger, challenged):
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        console = self.get_console(self.tournament.console.entity_id)
        game = self.get_game(console, self.tournament.game.entity_id)
        return Duel(
            challenger=challenger,
            challenged=challenged,
            game=game,
            console=self._prepare_console_to_duel(console),
            star_type=CoinType.GOLDEN_STAR,
            bet_size=self.tournament.star_amount,
            member_type=MemberType.PLAYER,
            duel_type=DuelType.CHAMPIONSHIP,
            participants=2,
            challenger_confirmation=True,
            challenged_confirmation=True,
            challenged_accept=True,
            creation_datetime=now,
            time_start=now,
            time_to_finish_duel=self.time_to_finish,
            time_to_accept_invitation=1,
            status=DuelStatus.DUELING
        )

    def create_duels(self):
        members = self.tournament.members
        random.shuffle(members)
        for x in range(0, int(len(members)/2)):
            challenger = members[x].member_id
            challenged = members[len(members)-1-x].member_id
            duel = self.create_duel(challenger, challenged)
            duel.set_adapter(self.adapters.duel_adapter)
            duel.save()
            self.duel_list.append(duel.entity_id)
            self.send_duel_invite(challenger, challenged, duel)
            self.send_duel_invite(challenged, challenger, duel)

    def check_accepted_members_amount(self):
        return True if self.tournament.member_amount == \
                       self.tournament.confirmed_members else False

    def get_tournament_adapter(self):
        adapter_map = {
            MemberType.PLAYER: self.adapters.player_tournament_adapter,
            MemberType.TEAM: self.adapters.team_tournament_adapter
        }

        return adapter_map[self.request.member_type]

    def send_duel_invite(self, member1, member2, duel):
        adversary = self.adapters.player_adapter.get_by_id(member2)
        failed = invite_member(
            member=member1,
            notification_type=NotificationType.DUEL_INVITE,
            duel=duel,
            tournament=self.tournament,
            notification_adapter=self.adapters.notificationgql_adapter,
            complement=adversary.user.nickname,
            logo_path=self.tournament.game.logo_path
        )
        if failed:
            report_failed_invites(
                tournament_id=self.tournament.entity_id,
                failed_invites=[failed],
                logger=self.logger,
                _type='duel invites')

    def send_cancel_notifications(self):
        failed_notifications = send_invites(
            players=self.tournament.members,
            tournament=self.tournament,
            logo_path=self.tournament.game.logo_path,
            notification_adapter=self.adapters.notificationgql_adapter,
            notification_type=NotificationType.CHAMPIONSHIP_CANCEL
        )
        report_failed_invites(
            tournament_id=self.tournament.entity_id,
            failed_invites=failed_notifications,
            logger=self.logger,
            _type='cancel notifications'
        )

    def run(self):
        tournament_adapter = self.get_tournament_adapter()
        self.tournament: Tournament = tournament_adapter.get_by_id(
            self.request.tournament_id)

        if self.check_accepted_members_amount():
            self.create_duels()
            self.create_phase_one()
            self.set_tournament_started()
        else:
            self.cancel_tournament()
            self.send_cancel_notifications()

        response = PostTournamentStartResponseModel(self.tournament)
        return response
