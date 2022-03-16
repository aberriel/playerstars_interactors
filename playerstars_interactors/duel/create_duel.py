from builtins import isinstance
from playerstars_adapters import (
    DuelAdapter,
    NotificationAdapter,
    PlayerAdapter,
    TeamAdapter)
from playerstars_domain import (
    CoinType, Console, Duel, DuelMemberType, DuelType, Game,
    NotificationType, Player, Team)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.utils.domain_utils import (
    find_entity_by_id)
from playerstars_interactors.utils.notification_utils import (
    create_notification)

import logging
import uuid


class PlayerNotFoundException(Exception):
    pass


class CreateDuelException(Exception):
    pass


class CreateDuelRequestModel:
    def __init__(self, json_data):
        self.member_type = json_data.get('member_type')
        self.challenger = json_data.get('challenger')
        self.challenger_team = json_data.get('challenger_team', None)
        self.challenged = json_data.get('challenged')
        self.console = json_data.get('console')
        self.game = json_data.get('game')
        self.bet_size = json_data.get('bet_size')
        self.star_type = CoinType(json_data.get('star_type'))
        self.duel_type = json_data.get('duel_type')


class CreateDuelResponseModel:
    def __init__(self, duel_data: Duel):
        self.duel_data = duel_data

    @property
    def current_server_time(self):
        current_time = aware_now()
        current_server_time_str = current_time.isoformat()
        return current_server_time_str

    def __call__(self):
        duel_creation_dt_str = \
            self.duel_data.creation_datetime.isoformat()
        return {
            'duel_id': self.duel_data.entity_id,
            'created_at': duel_creation_dt_str,
            'accept_time':
                self.duel_data.time_to_accept_invitation,
            'time_to_finish': self.duel_data.time_to_finish_duel,
            'current_server_time': self.current_server_time}


class CreateDuelInteractor:
    challenger = None
    challenged = None
    duel = None

    def __init__(self,
                 request: CreateDuelRequestModel,
                 duel_adapter: DuelAdapter,
                 notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter,
                 time_to_finish: int,
                 accept_time: int):
        self.request = request
        self.duel_adapter = duel_adapter
        self.notification_adapter = notification_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.time_to_finish = time_to_finish
        self.accept_time = accept_time
        self.logger = logging.getLogger(__name__)

    def get_challenger(self):
        challenger_id = self.request.challenger_team \
            if self.request.challenger_team else self.request.challenger
        return self._get_participant(challenger_id)

    def get_challenged(self):
        return self._get_participant(self.request.challenged)

    def _get_participant(self, participant_id):
        member_type = DuelMemberType(self.request.member_type)
        adapter = self.player_adapter \
            if member_type == DuelMemberType.PLAYER \
            else self.team_adapter
        class_name = 'Player' \
            if member_type == DuelMemberType.PLAYER \
            else 'Team'
        return find_entity_by_id(
            _id=participant_id,
            adapter_instance=adapter,
            class_name=class_name)

    def _get_captain(self, captain_id):
        return find_entity_by_id(
            _id=captain_id, adapter_instance=self.player_adapter,
            class_name='Player')

    def get_paying_player(self):
        if isinstance(self.challenger, Player):
            return self.challenger
        return self._get_captain(self.challenger.captain.player_id)

    def check_balance(self):
        if self.request.star_type == CoinType.GOLDEN_STAR:
            self.check_balance_golden_star()
        else:
            self.check_balance_red_star()

    def check_balance_golden_star(self):
        paying_player: Player = self.get_paying_player()
        if paying_player.golden_star_balance < self.request.bet_size:
            raise CreateDuelException(
                "Player {0} doesn't have enought golden star"
                .format(paying_player.user.nickname))

    def check_balance_red_star(self):
        paying_player = self.get_paying_player()
        if paying_player.red_star_balance < self.request.bet_size:
            raise CreateDuelException(
                "Player {0} doesn't have enought red star"
                .format(paying_player.user.nickname))

    def check_team_member_on_opponent(self):
        player = self._get_captain(self.challenger.captain.player_id)
        player_as_opponent_captain = \
            self.challenged.captain.player_id == player.entity_id
        player_as_opponent_member = \
            next((x for x in self.challenged.members
                  if x.player_id == player.entity_id),
                 None)

        if player_as_opponent_captain or player_as_opponent_member:
            raise Exception('{0} captain cannot be in both teams'
                            .format(self.challenger.name))

    def _init_console(self):
        return Console(
            entity_id=self.request.console['entity_id'],
            name=self.request.console['name'],
            logo_path=self.request.console['logo_path'])

    def _init_game(self):
        return Game(
            entity_id=self.request.game['entity_id'],
            name=self.request.game['name'],
            logo_path=self.request.game['logo_path'])

    def _init_duel(self, game, console):
        creation_datetime = aware_now()
        time_accepting_duel = self.accept_time
        return Duel(
            entity_id=str(uuid.uuid4()),
            challenger=self.request.challenger_team
            if self.request.challenger_team else self.request.challenger,
            challenged=self.request.challenged,
            challenged_accept=False,
            game=game,
            console=console,
            star_type=self.request.star_type,
            bet_size=self.request.bet_size,
            challenged_confirmation=False,
            challenger_confirmation=False,
            participants=2,
            time_start=None,
            creation_datetime=creation_datetime,
            member_type=DuelMemberType(self.request.member_type),
            duel_type=DuelType(self.request.duel_type),
            time_to_finish_duel=self.time_to_finish,
            time_to_accept_invitation=time_accepting_duel)

    def _get_member_player(self, member):
        return member if isinstance(member, Player) \
            else self._get_captain(member.captain.player_id)

    def _get_member_team_id(self, member):
        return member.entity_id \
            if isinstance(member, Team) else None

    def invite_member(self):
        notification_datetime = aware_now()

        challenger_player: Player = self._get_member_player(self.challenger)
        challenged_player: Player = self._get_member_player(self.challenged)
        notification_complement = challenger_player.user.nickname
        team_id = self._get_member_team_id(self.challenged)
        message_id = create_notification(
            player_data=challenged_player,
            notification_adapter=self.notification_adapter,
            notification_type=NotificationType.DUEL_INVITE,
            duel_id=self.duel.entity_id,
            team_id=team_id,
            notification_image=self.duel.game.logo_path,
            notification_complement=notification_complement,
            creation_datetime=notification_datetime,
            logger_instance=self.logger
        )
        self.duel.time_send_invitation = aware_now()
        return message_id

    def run(self):
        try:
            self.challenger = self.get_challenger()
            self.challenged = self.get_challenged()
            self.check_balance()

            if self.request.member_type == DuelMemberType.TEAM.value:
                self.check_team_member_on_opponent()

            console: Console = self._init_console()
            game: Game = self._init_game()
            self.duel: Duel = self._init_duel(
                game=game,
                console=console)
            self.invite_member()

            self.duel.set_adapter(self.duel_adapter)
            self.duel.save()
            response = CreateDuelResponseModel(self.duel)
            return response
        except Exception as exc:
            msg = 'Error during duel creation: {}'.format(exc)
            raise CreateDuelException(msg)
