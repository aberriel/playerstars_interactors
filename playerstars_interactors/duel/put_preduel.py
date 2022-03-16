from datetime import timedelta
from playerstars_adapters import (
    AwsTaskSchedulerAdapter,
    ConsoleAdapter,
    DuelAdapter,
    EventReminderAssistantAdapter,
    NotificationAdapter,
    PlayerAdapter,
    PreDuelAdapter,
    TeamAdapter)
from playerstars_domain import (
    Duel, CoinType, Game, NotificationType,
    Player, PreDuel, Team)
from playerstars_domain.duel.duel import DuelMemberType, DuelStatus, DuelType
from playerstars_domain.duel.pre_duel import Status as PreDuelStatus
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_interactors.utils.message import send_message
from playerstars_interactors.utils.notification_utils import \
    create_notification
from playerstars_scheduled_task_adapter import ScheduleTask
from typing import Callable
from playerstars_interactors.utils.create_era_event import create_era
import logging


class PlayerNotFoundException(Exception):
    pass


class PutPreDuelException(Exception):
    pass


class PutPreDuelConfirmException(BaseException):
    pass


class PutPreDuelAcceptException(BaseException):
    pass


class PutPreDuelUnknowStatusException(BaseException):
    pass


class PutPreDuelRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data.get('player_id')
        self.preduel_id = json_data.get('preduel_id')
        self.status = json_data.get('status')


class PutPreDuelResponseModel:
    def __init__(self, preduel_id, ):
        self.preduel_id = preduel_id

    def __call__(self):
        return self.preduel_id


class PutPreDuelAdapters:
    def __init__(self,
                 preduel_adapter: PreDuelAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter,
                 duel_adapter: DuelAdapter,
                 console_adapter: ConsoleAdapter,
                 notification_adapter: NotificationAdapter,
                 schedule_task_adapter: ScheduleTask,
                 era_adapter: EventReminderAssistantAdapter,
                 scheduler_adapter: AwsTaskSchedulerAdapter):
        self.preduel_adapter = preduel_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.duel_adapter = duel_adapter
        self.console_adapter = console_adapter
        self.notification_adapter = notification_adapter
        self.schedule_task_adapter = schedule_task_adapter
        self.era_adapter = era_adapter
        self.scheduler_adapter = scheduler_adapter


class PutPreDuelInteractor:
    duel = None

    def __init__(self,
                 request: PutPreDuelRequestModel,
                 adapters: PutPreDuelAdapters,
                 time_to_finish: int,
                 era_finish_duel_url):
        self.request = request
        self.adapters = adapters
        self.time_to_finish = time_to_finish
        self.era_finish_duel_url = era_finish_duel_url
        self.logger = logging.getLogger(__name__)

    def _get_duel_member(self, duel_member_id):
        get_map = {
            DuelMemberType.PLAYER: self.get_duel_member_player,
            DuelMemberType.TEAM: self.get_duel_member_team}
        return get_map[self.duel.member_type](duel_member_id)

    def get_duel_member_player(self, member_id):
        return find_entity_by_id(
            _id=member_id,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

    def get_duel_member_team(self, member_id):
        return find_entity_by_id(
            _id=member_id,
            adapter_instance=self.adapters.team_adapter,
            class_name='Team')

    def check_participants(self, preduel: PreDuel):
        participants = []
        if preduel.duel_type == DuelMemberType.PLAYER:
            participants = [preduel.challenger, preduel.challenged]

        if preduel.duel_type == DuelMemberType.TEAM:
            team_1 = self.adapters.team_adapter.get_by_id(
                preduel.challenger)
            team_2 = self.adapters.team_adapter.get_by_id(
                preduel.challenged)
            participants = [team_1.captain.player_id,
                            team_2.captain.player_id]
        if self.request.player_id not in participants:
            msg = f'Player {self.request.player_id} is not a participant' \
                  f' in this preduel'
            raise PutPreDuelException(msg)
        return True

    def confirm(self, preduel: PreDuel) -> PreDuel:
        if preduel.status == PreDuelStatus.CONFIRM:
            preduel.status = PreDuelStatus.CONFIRMED_1
            preduel.ack = False
            self.warn_other_participant(preduel)
            return preduel
        if preduel.status == PreDuelStatus.CONFIRMED_1:
            preduel.status = PreDuelStatus.CONFIRMED_2
            self.warn_other_participant(preduel)
            return preduel
        else:
            msg = f'Trying to confirm a preduel that has {preduel.status} ' \
                  f'status is not possible'
            raise PutPreDuelConfirmException(msg)

    def accept(self, preduel: PreDuel) -> PreDuel:
        if preduel.status == PreDuelStatus.CONFIRMED_2:
            preduel.status = PreDuelStatus.ACCEPTED_1
            preduel.ack = False
            self.warn_other_participant(preduel)
            return preduel
        if preduel.status == PreDuelStatus.ACCEPTED_1:
            preduel.status = PreDuelStatus.ACCEPTED_2
            self.warn_other_participant(preduel)
            return preduel
        else:
            msg = f'Trying to accept a preduel that has {preduel.status} ' \
                  f'status is not possible'
            raise PutPreDuelAcceptException(msg)

    def ack_true(self, preduel: PreDuel) -> PreDuel:
        preduel.ack = True
        self.warn_other_participant(preduel)
        return preduel

    def warn_other_participant(self, preduel):
        # Avisar primeiro participante a enviar confirmação
        # ou accept que o segundo enviou
        participant = self.get_participant_to_warn(preduel)
        message_response = send_message(
            msg=f'{participant} do duel {preduel.entity_id} '
            f'marcou o duelo como {preduel.status}',
            queue_name=participant)
        self.logger.info(message_response)

    def get_participant_to_warn(self, preduel):
        if preduel.duel_type == DuelMemberType.PLAYER:
            return preduel.challenger \
                if self.request.player_id == preduel.challenged \
                else preduel.challenged
        return self.get_other_captain_id(preduel)

    def get_other_captain_id(self, preduel):
        team = self.adapters.team_adapter.get_by_id(preduel.challenger)
        if self.request.player_id != team.captain.player_id:
            return team.captain.player_id
        other_team = self.adapters.team_adapter.get_by_id(preduel.challenged)
        return other_team.captain.player_id

    def refuse(self, preduel: PreDuel) -> PreDuel:
        preduel.status = PreDuelStatus.REFUSED
        if preduel.challenged:
            self.warn_refuse(preduel)
        return preduel

    def warn_refuse(self, preduel):
        # Avisar ao outro participante que o preduel foi recusado
        participant = self.get_participant_to_warn(preduel)
        message_response = send_message(
            msg=f'{participant} recusou o duel '
            f'{preduel.entity_id}',
            queue_name=participant)
        self.logger.info(message_response)

    def resolve_status(self, preduel):
        sign = Callable[[PreDuel], PreDuel]
        status_func = {
            'confirm': self.confirm,
            'accepted': self.accept,
            'ack': self.ack_true,
            'refuse': self.refuse
        }
        if self.request.status not in status_func:
            msg = 'Status de atualização de preduel inválido'
            raise PutPreDuelUnknowStatusException(msg)

        action: sign = status_func[self.request.status]
        preduel = action(preduel)
        return preduel

    def get_console(self, console_id):
        return self.adapters.console_adapter.get_by_id(console_id)

    @staticmethod
    def get_game(console, game_id):
        game: Game = console.find_game_by_id(game_id)
        game.tutorial = None
        return game

    @staticmethod
    def _prepare_console_to_duel(console_data):
        console_data.games = []
        return console_data

    def create_duel(self, preduel: PreDuel):
        now = aware_now()
        console = self.get_console(preduel.console_entity_id)
        game = self.get_game(
            console=console,
            game_id=preduel.game_entity_id)
        return Duel(
            challenger=preduel.challenger,
            challenged=preduel.challenged,
            game=game,
            console=self._prepare_console_to_duel(console),
            star_type=preduel.star_type,
            bet_size=preduel.star_amount,
            member_type=preduel.duel_type,
            duel_type=DuelType.INDIVIDUAL,
            participants=2,
            challenger_confirmation=True,
            challenged_confirmation=True,
            challenged_accept=True,
            creation_datetime=now,
            time_start=now,
            time_to_finish_duel=self.time_to_finish,
            time_to_accept_invitation=1,
            status=DuelStatus.DUELING)

    @staticmethod
    def get_player_balance(player, star_type):
        if star_type == CoinType.GOLDEN_STAR:
            return player.golden_star_balance
        return player.red_star_balance

    @staticmethod
    def set_player_balance(player, star_type, new_balance):
        if star_type == CoinType.GOLDEN_STAR:
            player.golden_star_balance = new_balance
        else:
            player.red_star_balance = new_balance
        return player

    def pay_player(self,
                   entity_id: str,
                   bet_size: int,
                   star_type: CoinType) -> None:
        player: Player = self.adapters.player_adapter.get_by_id(entity_id)
        new_balance = self.get_player_balance(player, star_type) - bet_size
        if new_balance < 0:
            msg = f"Player {player.entity_id} doesn't have enough stars"
            raise ValueError(msg)
        player = self.set_player_balance(
            player=player,
            star_type=star_type,
            new_balance=new_balance)
        player.set_adapter(self.adapters.player_adapter)
        player.save()

    def pay_team(self,
                 entity_id: str,
                 bet_size: int,
                 star_type: CoinType) -> None:
        team: Team = self.adapters.team_adapter.get_by_id(entity_id)
        captain: Player = self.adapters.player_adapter.get_by_id(
            team.captain.player_id)
        self.pay_player(
            entity_id=captain.entity_id,
            bet_size=bet_size,
            star_type=star_type)

    def pay_duel(self, duel):
        sign = Callable[[str, int, CoinType], None]
        pay_funcs = {
            DuelMemberType.PLAYER: self.pay_player,
            DuelMemberType.TEAM: self.pay_team}

        pay_func: sign = pay_funcs[duel.member_type]
        pay_func(duel.challenger, duel.bet_size, duel.star_type)
        pay_func(duel.challenged, duel.bet_size, duel.star_type)

    def calculate_finish_datetime(self):
        request_datetime = aware_now()
        finish_datetime = request_datetime + timedelta(
            minutes=int(self.time_to_finish))
        return finish_datetime

    def create_finish_task(self, duel_id):
        finish_datetime = self.calculate_finish_datetime()
        create_era(duel_id=duel_id,
                   event_time=finish_datetime,
                   era_finish_duel_url=self.era_finish_duel_url,
                   persist_adapter=self.adapters.era_adapter,
                   scheduler_adapter=self.adapters.scheduler_adapter)
        return

    def update_preduel(self, preduel):
        preduel.set_adapter(self.adapters.preduel_adapter)
        preduel.save()

    def update_duel(self):
        self.duel.set_adapter(self.adapters.duel_adapter)
        self.duel.save()

    def _get_member_player(self, member_data):
        if self.duel.member_type == DuelMemberType.TEAM:
            return self.get_duel_member_player(member_data.captain.player_id)
        return member_data

    def _get_team_id(self, member_data):
        get_map = {
            DuelMemberType.PLAYER: None,
            DuelMemberType.TEAM: member_data.entity_id}
        return get_map[self.duel.member_type]

    def _get_member_name(self, member_data):
        if self.duel.member_type == DuelMemberType.TEAM:
            return member_data.name
        return member_data.user.nickname

    def notify_members(self):
        challenger = self._get_duel_member(self.duel.challenger)
        challenged = self._get_duel_member(self.duel.challenged)
        self.notify_member(challenger, challenged)
        self.notify_member(challenged, challenger)

    def notify_member(self, member_1, member_2):
        create_notification(
            player_data=self._get_member_player(member_1),
            notification_adapter=self.adapters.notification_adapter,
            notification_type=NotificationType.DUEL_ONGOING,
            notification_complement=self._get_member_name(member_2),
            duel_id=self.duel.entity_id,
            team_id=self._get_team_id(member_1),
            notification_image=self.duel.game.logo_path,
            logger_instance=self.logger)

    def run(self):
        try:
            preduel = self._get_preduel()
            self.check_participants(preduel)
            preduel = self.resolve_status(preduel)
            self.update_preduel(preduel)

            if preduel.status != PreDuelStatus.ACCEPTED_2:
                return PutPreDuelResponseModel(preduel.entity_id)

            self.duel = self.create_duel(preduel)
            preduel.duel_id = self.duel.entity_id
            self.update_preduel(preduel)

            if preduel.star_type == CoinType.GOLDEN_STAR:
                self.pay_duel(self.duel)
            self.create_finish_task(self.duel.entity_id)
            self.update_duel()
            self.notify_members()
            response = PutPreDuelResponseModel(self.duel.entity_id)
            return response
        except BaseException as exc:
            msg = f'Error during preduel update: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise PutPreDuelException(msg)

    def _get_preduel(self):
        return find_entity_by_id(
            _id=self.request.preduel_id,
            adapter_instance=self.adapters.preduel_adapter,
            class_name='PreDuel')
