from datetime import timedelta
from playerstars_adapters import (
    DuelAdapter as DuelAdapterDynamo,
    PlayerAdapter,
    TeamAdapter, AwsTaskSchedulerAdapter,
    EventReminderAssistantAdapter)
from playerstars_domain import CoinType, DuelStatus, DuelMemberType, Player
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_graphql_adapters import (
    DuelAdapter as DuelAdapterGraphql,
    NotificationAdapter)
from playerstars_interactors.duel.duel_utils import \
    send_duel_ongoing_notification
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_scheduled_task_adapter import ScheduleTask
from playerstars_interactors.utils.create_era_event import create_era

import logging


class ChallengedNotFoundException(Exception):
    pass


class NotEnoughBalanceException(Exception):
    pass


class EnterDuelException(Exception):
    pass


class EnterDuelRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data.get('player_id', None)
        self.duel_id = json_data.get('duel_id')
        self.team_id = json_data.get('team_id', None)


class EnterDuelResponseModel:
    def __init__(self, duel_data):
        self.duel_data = duel_data

    def accept_duel_datetime(self):
        return self.duel_data.time_start.isoformat()

    def current_server_time(self):
        current_time = aware_now()
        return current_time.isoformat()

    def __call__(self):
        accept_datetime = self.accept_duel_datetime()
        server_time = self.current_server_time()
        result = {
            'duel_id': self.duel_data.entity_id,
            'accepted_at': accept_datetime,
            'time_to_finish': self.duel_data.time_to_finish_duel,
            'current_server_time': server_time}
        return result


class InvalidStatusException(BaseException):
    pass


class EnterDuelInteractorAdapters:
    def __init__(self,
                 duel_adapter_dynamo: DuelAdapterDynamo,
                 duel_adapter_graphql: DuelAdapterGraphql,
                 notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter,
                 era_adapter: EventReminderAssistantAdapter,
                 scheduler_adapter: AwsTaskSchedulerAdapter):
        self.duel_adapter_dynamo = duel_adapter_dynamo
        self.duel_adapter_graphql = duel_adapter_graphql
        self.notification_adapter = notification_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.era_adapter = era_adapter
        self.scheduler_adapter = scheduler_adapter


class EnterDuelInteractor:
    challenger = None
    challenged = None
    duel = None
    request_datetime = None

    def __init__(self,
                 request: EnterDuelRequestModel,
                 adapters: EnterDuelInteractorAdapters,
                 time_to_finish_duel: int,
                 time_to_accept_invitation: int,
                 era_finish_duel_url,
                 schedule_task_adapter: ScheduleTask):
        self.request = request
        self.adapters = adapters
        self.schedule_task_adapter = schedule_task_adapter
        self.time_to_finish_duel = time_to_finish_duel
        self.time_to_accept_invitation = time_to_accept_invitation
        self.era_finish_duel_url = era_finish_duel_url
        self.logger = logging.getLogger(__name__)

        self.request_datetime = aware_now()

    def _get_class_name_adapter(self):
        if self.duel.member_type == DuelMemberType.PLAYER:
            return 'Player', self.adapters.player_adapter
        elif self.duel.member_type == DuelMemberType.TEAM:
            return 'Team', self.adapters.team_adapter

    def _get_member_adapter(self):
        return self.adapters.team_adapter if \
            self.duel.member_type == DuelMemberType.TEAM \
            else self.adapters.player_adapter

    def _get_duel(self):
        return find_entity_by_id(
            _id=self.request.duel_id,
            adapter_instance=self.adapters.duel_adapter_dynamo,
            class_name='Duel')

    def _get_challenger(self, challenger_id):
        class_name, adapter = self._get_class_name_adapter()
        return find_entity_by_id(
            _id=challenger_id,
            adapter_instance=adapter,
            class_name=class_name)

    def _get_challenged(self, challenged_id):
        class_name, adapter = self._get_class_name_adapter()
        return find_entity_by_id(
            _id=challenged_id,
            adapter_instance=adapter,
            class_name=class_name)

    def calculate_finish_datetime(self):
        finish_datetime = \
            self.request_datetime + timedelta(
                minutes=int(self.time_to_finish_duel))
        return finish_datetime

    def schedule_finish_task(self):
        finish_datetime = self.calculate_finish_datetime()
        create_era(self.request.duel_id, finish_datetime,
                   self.era_finish_duel_url,
                   self.adapters.era_adapter,
                   self.adapters.scheduler_adapter)
        return

    def update_duel_status(self):
        self.duel.status = DuelStatus.DUELING
        self.duel.time_start = aware_now()

    def _add_challenged(self):
        self.duel.challenged = self.challenged.entity_id
        self.duel.challenged_accept = True

    @staticmethod
    def pay_player_red_star(player, value, team=None):
        updated_balance = player.red_star_balance - value
        if updated_balance < 0:
            error_msg = f"Player {player.user.nickname} don't have " \
                        f"enough red stars"
            if team:
                error_msg = f"Captain {player.user.nickname} of team " \
                            f"{team.name} don't have enough red stars"

            raise NotEnoughBalanceException(error_msg)
        player.red_star_balance = updated_balance
        return player

    @staticmethod
    def pay_player_golden_star(player, value, team=None):
        updated_balance = player.golden_star_balance - value
        if updated_balance < 0:
            error_msg = f"Player {player.user.nickname} don't have enough" \
                        f" golden stars"
            if team:
                error_msg = f"Captain {player.user.nickname} of team " \
                            f"{team.name} don't have enough golden stars"
            raise NotEnoughBalanceException(error_msg)
        player.golden_star_balance = updated_balance
        return player

    def check_time_limit_to_accept_invitation(self):
        notification_datetime = self.duel.time_send_invitation
        time_limit = notification_datetime + timedelta(
            minutes=int(self.time_to_accept_invitation))
        if time_limit < self.request_datetime:
            error_msg = f"You can't accept duel after the limit: " \
                f"{time_limit.isoformat()}"
            raise EnterDuelException(error_msg)
        return True

    def pay_team(self, team):
        team_captain = find_entity_by_id(
            _id=team.captain.player_id,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

        if self.duel.star_type == CoinType.GOLDEN_STAR:
            updated_captain = self.pay_player_golden_star(
                player=team_captain, value=self.duel.bet_size)
        else:
            updated_captain = self.pay_player_red_star(
                player=team_captain, value=self.duel.bet_size)

        updated_captain.save()
        team.captain.player = updated_captain
        return team

    def pay_player(self, player: Player):
        if self.duel.star_type == CoinType.GOLDEN_STAR:
            updated_player = self.pay_player_golden_star(
                player=player, value=self.duel.bet_size)
        else:
            updated_player = self.pay_player_red_star(
                player=player, value=self.duel.bet_size)
        return updated_player

    def pay_duel_player(self):
        self.logger.debug('_pay_duel_player -> '
                          'Pagando a aposta do challenger')
        updated_challenger = self.pay_player(self.challenger)
        updated_challenger.save()
        self.challenger = updated_challenger

        self.logger.debug('_pay_duel_player -> '
                          'Pagando a aposta do challenged')
        updated_challenged = self.pay_player(self.challenged)
        updated_challenged.save()
        self.challenged = updated_challenged

    def pay_duel_team(self):
        self.logger.debug('_pay_duel_team -> '
                          'Pagando a aposta do challenger')
        updated_challenger = self.pay_team(self.challenger)
        updated_challenger.save()

        self.logger.debug('_pay_duel_team -> '
                          'Pagando a aposta do challenged')
        updated_challenged = self.pay_team(self.challenged)
        updated_challenged.save()

    def _pay_duel(self):
        if self.duel.member_type == DuelMemberType.PLAYER:
            self.pay_duel_player()
        else:
            self.pay_duel_team()

    def run(self):
        try:
            self.duel = self._get_duel()
            self._check_duel_status()
            self.duel.set_adapter(self.adapters.duel_adapter_dynamo)
            self.check_time_limit_to_accept_invitation()

            member_adapter = self._get_member_adapter()

            self.challenger = self._get_challenger(self.duel.challenger)
            self.challenger.set_adapter(member_adapter)

            self.challenged = self._get_challenged(self.duel.challenged)
            self.challenged.set_adapter(member_adapter)

            self._add_challenged()

            self._pay_duel()
            self.update_duel_status()
            self.schedule_finish_task()
            send_duel_ongoing_notification(
                duel=self.duel,
                challenger=self.challenger,
                challenged=self.challenged,
                notification_adapter=self.adapters.notification_adapter,
                logger_instance=self.logger)
            self.duel.set_adapter(self.adapters.duel_adapter_graphql)
            self.duel.save_graphql(exec_update=True)
            response = EnterDuelResponseModel(self.duel)
            return response
        except (BaseException, Exception, EnterDuelException) as exc:
            msg = f'Error during update duel: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise EnterDuelException(msg)

    def _check_duel_status(self):
        if self.duel.status != DuelStatus.LOBBY:
            msg = f'Invalid duel state: {self.duel.status.value}'
            raise InvalidStatusException(msg)
        return True
