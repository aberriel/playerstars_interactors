from clapy_basic_classes import BasicValue
from collections import namedtuple
from datetime import datetime
from marshmallow import fields, post_load
from marshmallow_enum import EnumField
from playerstars_adapters import (
    ConsoleAdapter,
    NotificationAdapter,
    PlayerTournamentAdapter,
    TeamTournamentAdapter,
    ValuesAdapter)
from playerstars_domain import (Values, TournamentMember,
                                TournamentMemberStatus, TournamentStatus,
                                Console, Game, PlayerTournament,
                                TeamTournament, Notification, NotificationType,
                                Tournament, DuelMemberType as MemberType)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_domain.utils.marshmallow_helper import REQUIRED, REQUIRED_DATE
from traceback import format_exception
from typing import List, Optional

import logging
import sys


class PostTournamentRestModel(BasicValue):
    def __init__(self,
                 game_id: str,
                 console_id: str,
                 duel_type: MemberType,
                 star_amount: int,
                 start_datetime: datetime,
                 phase_duration: int,
                 phases_per_day: int,
                 member_amount: int,
                 members: List[str],
                 entity_id=None):
        self.entity_id = entity_id
        self.game_id = game_id
        self.console_id = console_id
        self.duel_type = duel_type
        self.star_amount = star_amount
        self.start_datetime = start_datetime
        self.phase_duration = phase_duration
        self.phases_per_day = phases_per_day
        self.member_amount = member_amount
        self.members = members

    class Schema(BasicValue.Schema):
        entity_id = fields.Str(required=False, allow_none=True)
        game_id = fields.Str(**REQUIRED)
        console_id = fields.Str(**REQUIRED)
        duel_type = EnumField(MemberType, **REQUIRED)
        star_amount = fields.Int(**REQUIRED)
        start_datetime = fields.AwareDateTime(**REQUIRED_DATE)
        phase_duration = fields.Int(**REQUIRED)
        phases_per_day = fields.Int(**REQUIRED)
        member_amount = fields.Int(**REQUIRED)
        members = fields.List(fields.String, required=True, allow_none=False)

        # noinspection PyUnusedLocal
        @post_load
        def on_load(self, data, many, partial):
            return PostTournamentRestModel(**data)


class PostTournamentAdapters:
    def __init__(self,
                 tournament: [PlayerTournamentAdapter,
                              TeamTournamentAdapter],
                 console: ConsoleAdapter,
                 values: ValuesAdapter,
                 notification_adapter: NotificationAdapter):
        self.tournament = tournament
        self.console = console
        self.values = values
        self.notification_adapter = notification_adapter


FailedInvite = namedtuple('FailedInvite',
                          'member, exception, message, traceback')


class FailedInviteException(BaseException):
    pass


class PostTournamentInteractor:
    def __init__(self,
                 request: PostTournamentRestModel,
                 adapters: PostTournamentAdapters,
                 player_id: str,
                 logger=None):
        self.request = request
        self.adapters = adapters
        self.player_id = player_id
        self.awards = None
        self.members = None
        self.console: [Console, None] = None
        self.game: [Game, None] = None
        self.logger = logger or logging.getLogger(__name__)

        self.failed_invites: List[FailedInvite] = []
        self.tournament: Optional[Tournament] = None

    def _get_values(self) -> Values:
        return self.adapters.values.get_by_id('1')

    def _fill_award_values(self, values):
        Awards = namedtuple('Awards', 'first, second, third')
        self.awards = Awards(
            first=values.championship_award_first_place_perc,
            second=values.championship_award_second_place_perc,
            third=values.championship_award_third_place_perc)

    @staticmethod
    def _member_factory(member_id):
        return TournamentMember(member_id=member_id,
                                status=TournamentMemberStatus.INVITED)

    def _fill_members(self):
        self.members = [self._member_factory(x) for x in self.request.members]
        self.members.append(TournamentMember(
            member_id=self.player_id,
            status=TournamentMemberStatus.OWNER))

    def _fill_console(self):
        self.console = self.adapters.console.get_by_id(self.request.console_id)

    def _fill_game(self, console):
        self.game: Game = [x for x in console.games
                           if x.entity_id == self.request.game_id][0]

    def _get_tournament_class(self):
        class_map = {
            MemberType.PLAYER: PlayerTournament,
            MemberType.TEAM: TeamTournament
        }
        return class_map[self.request.duel_type]

    def _make_response(self) -> PostTournamentRestModel:
        json_data = self.request.to_json()
        response: PostTournamentRestModel = PostTournamentRestModel.from_json(
            json_data)

        response.entity_id = self.tournament.entity_id
        return response

    def _send_invites(self):
        for member in self.members:
            self._invite_member(member)

    def _invite_member(self, member: TournamentMember):
        try:
            complement = self._format_complement()
            game_image = self.game.logo_path
            notification = Notification(
                player_id=member.member_id,
                notification_type=NotificationType.CHAMPIONSHIP_INVITE_PLAYER,
                championship_id=self.tournament.entity_id,
                notification_complement=complement,
                notification_image=game_image)
            notification.set_adapter(self.adapters.notification_adapter)
            notification.save()

        except Exception as exc:
            self.failed_invites.append(FailedInvite(member,
                                                    exc.__class__.__name__,
                                                    str(exc),
                                                    self._get_tb()))

    def _format_complement(self):
        return self.tournament.creation_datetime.strftime(
            'Inicio: %d/%m/%Y - %H:%M')

    @staticmethod
    def _get_tb():
        etype, value, traceback = sys.exc_info()
        tb = format_exception(etype, value, traceback)
        return '\n'.join(tb)

    def _failed_invites_count(self):
        return len(self.failed_invites)

    def _report_failed_invites(self):
        num_fails = self._failed_invites_count()
        if num_fails == 0:
            return

        self.logger.error(f'{num_fails} invites failed on '
                          f'tournament {self.tournament.entity_id}:')
        for failed_invite in self.failed_invites:
            msg = f'Failed invite:\t' \
                  f'member_id: {failed_invite.member.member_id}\t' \
                  f'error: {failed_invite.exception}\t' \
                  f'Message: {failed_invite.message}\t' \
                  f'Traceback: {failed_invite.traceback}'
            self.logger.error(msg)

    def run(self):
        values = self._get_values()
        self._fill_award_values(values)
        self._fill_members()
        self._fill_console()
        self._fill_game(self.console)

        tournament_class = self._get_tournament_class()

        self.tournament = tournament_class(
            game=self.game,
            console=self.console,
            award_first_place_perc=self.awards.first,
            award_second_place_perc=self.awards.second,
            award_third_place_perc=self.awards.third,
            price_to_enter=self.request.star_amount,
            member_amount=self.request.member_amount,
            level_duration=self.request.phase_duration,
            levels_per_day=self.request.phases_per_day,
            start_datetime=self.request.start_datetime,
            members=self.members,
            status=TournamentStatus.WAITING_START,
            creation_datetime=aware_now())
        self.tournament.set_adapter(self.adapters.tournament)
        self.tournament.save()
        self._send_invites()
        self._report_failed_invites()
        return self._make_response()
