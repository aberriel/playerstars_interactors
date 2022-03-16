import logging

from playerstars_adapters import (
    DuelAdapter,
    NotificationAdapter,
    PlayerAdapter,
    TeamAdapter,
    ValuesAdapter)
from playerstars_domain import (
    CoinType,
    ComponentResult,
    Duel,
    DuelComponentResult,
    DuelMemberType,
    DuelStatus,
    NotificationType,
    Player,
    Team)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.duel import (
    DuelSettlementTaskPlayer,
    DuelSettlementTaskTeam)
from playerstars_interactors.duel.duel_utils import (
    add_victory_on_game_on_player,
    update_elo_ratings)
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_interactors.utils.notification_utils import \
    create_notification
from playerstars_interactors.utils.report_exception import exception_str


class EndDuelException(BaseException):
    pass


class EndDuelRequestModel:
    def __init__(self, json_data):
        self.duel_id = json_data['duel_id']
        self.player_id = json_data['player_id']


class EndDuelResponseModel:
    def __init__(self, duel_data, submission_datetime):
        self.duel_data = duel_data
        self.submission_datetime = submission_datetime

    def __call__(self):
        return {
            'duel_id': self.duel_data.entity_id,
            'duel_status': self.duel_data.status.value,
            'submission_datetime':
                self.submission_datetime.isoformat()}


class LoadDuelException(BaseException):
    pass


class LoadMemberException(BaseException):
    pass


class UpdateDuelException(BaseException):
    pass


class JudgeException(BaseException):
    pass


class UploadImageException(BaseException):
    pass


class SubmitResultException(BaseException):
    pass


class EndDuelAdapters:
    def __init__(self, duel_adapter: DuelAdapter,
                 notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter,
                 values_adapter: ValuesAdapter):
        self.duel_adapter = duel_adapter
        self.notification_adapter = notification_adapter
        self.player_adapter = player_adapter
        self.team_adapter = team_adapter
        self.values_adapter = values_adapter


class EndDuelInteractor:
    duel = None
    challenger = None
    challenged = None
    submission_datetime = None

    def __init__(self, request: EndDuelRequestModel,
                 s3_bucket_name: str,
                 s3_bucket_url: str,
                 adapters: EndDuelAdapters,
                 judge_matrix: str):
        self.request = request
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_url = s3_bucket_url
        self.adapters = adapters
        self.judge_matrix = judge_matrix
        self.submission_datetime = aware_now()
        self.logger = logging.getLogger(__name__)

    def _can_end(self):
        if self.duel.status == DuelStatus.FINISHED_ONE_SIDE:
            return True
        if self.duel.status == DuelStatus.DUELING:
            self.duel.status = DuelStatus.FINISHED_ONE_SIDE
            self.duel.set_adapter(self.adapters.duel_adapter)
            self.duel.save()
            return False
        else:
            raise Exception("Unable to end duel because "
                            "it's on state " + self.duel.status.value)

    @staticmethod
    def duel_ready_to_finish(duel: Duel):
        check_result = all([
            duel.challenger_duel_result is not None,
            duel.challenged_duel_result is not None,
            duel.status != DuelStatus.FINISHED_BY_RESIGN])
        return check_result

    @staticmethod
    def get_coin_type_name_to_notification(coin_type: CoinType):
        return 'Stars Gold' \
            if coin_type == CoinType.GOLDEN_STAR else 'Stars Red'

    def _get_adapter(self):
        if self.duel.member_type == DuelMemberType.TEAM:
            return self.adapters.team_adapter
        return self.adapters.player_adapter

    def get_player_data(self, player_id):
        return find_entity_by_id(
            _id=player_id,
            adapter_instance=self.adapters.player_adapter,
            class_name='Player')

    def get_member_player(self, member_data):
        if isinstance(member_data, Player):
            return member_data
        return self.get_player_data(member_data.captain.player_id)

    def get_challenger(self):
        adapter = self._get_adapter()
        challenger_data = adapter.get_by_id(self.duel.challenger)
        return challenger_data

    def get_challenged(self):
        adapter = self._get_adapter()
        challenged_data = adapter.get_by_id(self.duel.challenged)
        return challenged_data

    def judge_duel(self):
        if self.duel.member_type == DuelMemberType.PLAYER:
            self.judge_duel_player()
        else:
            self.judge_duel_team()

    def judge_duel_player(self):
        duel_settlement_task = DuelSettlementTaskPlayer(
            duel=self.duel,
            duel_adapter=self.adapters.duel_adapter,
            notification_adapter=self.adapters.notification_adapter,
            player_adapter=self.adapters.player_adapter,
            values_adapter=self.adapters.values_adapter,
            judge_matrix=self.judge_matrix)
        self.duel = duel_settlement_task.run()

    def judge_duel_team(self):
        duel_settlement_task = DuelSettlementTaskTeam(
            duel=self.duel,
            duel_adapter=self.adapters.duel_adapter,
            notification_adapter=self.adapters.notification_adapter,
            player_adapter=self.adapters.player_adapter,
            team_adapter=self.adapters.team_adapter,
            values_adapter=self.adapters.values_adapter,
            judge_matrix=self.judge_matrix)
        self.duel = duel_settlement_task.run()

    def _check_resignation(self):
        if self._is_resignation():
            self.resignation_proceed()

    def _is_resignation(self):
        return ComponentResult.RESIGNED in [
            self.duel.challenged_duel_result.result,
            self.duel.challenger_duel_result.result]

    def resignation_proceed(self):
        member_loser, member_winner = self._select_wo_winner()

        if self.duel.member_type == DuelMemberType.PLAYER:
            self.resignation_proceed_player(member_winner, member_loser)
        else:
            self.resignation_proceed_team(member_winner, member_loser)

        self.finish_duel_by_resignation(member_winner)

    def _has_challenger_result(self) -> bool:
        return self.duel.challenger_duel_result is not None

    def _do_challenger_resigned(self):
        if self._has_challenger_result():
            result = self.duel.challenger_duel_result.result
            return result == ComponentResult.RESIGNED
        else:
            return False

    def _select_wo_winner(self):
        if self._do_challenger_resigned():
            member_winner = self.challenged
            member_loser = self.challenger
        else:
            member_winner = self.challenger
            member_loser = self.challenged
        return member_loser, member_winner

    def _set_victory_to_challenger(self):
        self.duel.challenger_duel_result = self._make_victory_response()

    def _set_victory_to_challenged(self):
        self.duel.challenged_duel_result = self._make_victory_response()

    def finish_duel_by_resignation(self, member_winner):
        map_set_victory = {
            self.duel.challenger: self._set_victory_to_challenger,
            self.duel.challenged: self._set_victory_to_challenged
        }
        map_set_victory[member_winner.entity_id]()

        self.duel.winner = member_winner.entity_id
        self.duel.status = DuelStatus.FINISHED_BY_RESIGN
        self.duel.time_finish = self.submission_datetime
        self._update_duel()

    def _make_victory_response(self):
        victory_response = DuelComponentResult(
            result=ComponentResult.WINNER,
            submission_datetime=self.submission_datetime)
        return victory_response

    def resignation_proceed_player(self, winner_player, loser_player):
        winner_player = self._process_winner(loser_player, winner_player)

        self._set_winner_to_challenger_or_challenged(winner_player)

        winner_complement = self._make_winner_notification_complement()
        loser_complement = winner_player.user.nickname

        self._notify_winner(winner_complement, winner_player)
        self._notify_loser(loser_complement, loser_player)

    def _notify_loser(self, loser_complement, loser_player):
        create_notification(
            player_data=loser_player,
            notification_adapter=self.adapters.notification_adapter,
            duel_id=self.duel.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            notification_complement=loser_complement,
            notification_image=self.duel.game.logo_path,
            logger_instance=self.logger)

    def _notify_winner(self, winner_complement, winner_player):
        create_notification(
            player_data=winner_player,
            notification_adapter=self.adapters.notification_adapter,
            logger_instance=self.logger,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            duel_id=self.duel.entity_id,
            notification_image=self.duel.game.logo_path,
            notification_complement=winner_complement)

    def _make_winner_notification_complement(self):
        winner_notification_complement = '{0} {1}'.format(
            self.duel.total_reward,
            self.get_coin_type_name_to_notification(self.duel.star_type))
        return winner_notification_complement

    def _set_winner_to_challenger_or_challenged(self, winner_player):
        if winner_player.entity_id == self.challenger.entity_id:
            self.challenger = winner_player
        else:
            self.challenged = winner_player

    def _process_winner(self, loser_player, winner_player):
        winner_player = self.pay_player(winner_player)
        winner_player = add_victory_on_game_on_player(
            player=winner_player,
            duel_data=self.duel)
        winner_player.save()
        update_elo_ratings(winner=winner_player, loser=loser_player)
        return winner_player

    def resignation_proceed_team(self, winner_team, loser_team):
        winner_player = self._process_winner_team(loser_team, winner_team)

        self._set_winner_to_challenger_or_challenged(winner_team)

        winner_complement = self._make_winner_notification_complement()
        loser_complement = loser_team.name

        self._notify_winner_team(winner_team, winner_complement, winner_player)
        self._notify_loser_team(loser_team, loser_complement)

    def _notify_loser_team(self, loser_team, loser_notification_complement):
        team_player = self.get_member_player(loser_team)
        create_notification(
            player_data=team_player,
            duel_id=self.duel.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            notification_complement=loser_notification_complement,
            notification_adapter=self.adapters.notification_adapter,
            logger_instance=self.logger,
            notification_image=self.duel.game.logo_path)

    def _notify_winner_team(self,
                            winner_team,
                            winner_notification_complement,
                            winner_player):
        create_notification(
            player_data=winner_player,
            notification_adapter=self.adapters.notification_adapter,
            logger_instance=self.logger,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            duel_id=self.duel.entity_id,
            team_id=winner_team.entity_id,
            notification_image=self.duel.game.logo_path,
            notification_complement=winner_notification_complement)

    def _process_winner_team(self, loser_team, winner_team):
        winner_player = self.get_member_player(winner_team)
        updated_captain = self.pay_player(winner_player)
        updated_captain.save()
        update_elo_ratings(winner=winner_team, loser=loser_team)
        return winner_player

    def pay_victory_team(self, winner_team: Team):
        player_id = winner_team.captain.player_id
        player_data: Player = self.adapters.player_adapter.get_by_id(player_id)
        player_data.set_adapter(self.adapters.player_adapter)
        player_data = self.pay_player(player_data)
        player_data.save()
        return player_data

    def pay_player(self, player_data: Player):
        if self.duel.star_type == CoinType.GOLDEN_STAR:
            return self.pay_player_golden(player_data)
        return self.pay_player_red(player_data)

    def pay_player_golden(self, player_data: Player):
        player_data.golden_star_balance += self.duel.total_reward
        return player_data

    def pay_player_red(self, player_data: Player):
        player_data.red_star_balance += self.duel.total_reward
        return player_data

    def _judge_duel(self):
        try:
            self.judge_duel()
        except Exception as e:
            msg = f'Error judging duel: {exception_str(e)}'
            raise JudgeException(msg)

    def _update_duel(self):
        try:
            self.duel.set_adapter(self.adapters.duel_adapter)
            self.duel.save()
        except Exception as e:
            msg = f'Error updating duel: {exception_str(e)}'
            raise UpdateDuelException(msg)

    def _load_members(self):
        self._load_challenger()
        self._load_challenged()

    def _load_member(self, fn_get, target_field):
        try:
            setattr(self, target_field, fn_get())
            getattr(self, target_field).set_adapter(self._get_adapter())
        except Exception as e:
            msg = f'Error loading {target_field}: {exception_str(e)}'
            raise LoadMemberException(msg)

    def _load_challenged(self):
        self._load_member(self.get_challenged, 'challenged')

    def _load_challenger(self):
        self._load_member(self.get_challenger, 'challenger')

    def _load_duel(self):
        try:
            self.duel: Duel = find_entity_by_id(
                _id=self.request.duel_id,
                adapter_instance=self.adapters.duel_adapter,
                class_name='Duel')
            self.duel.set_adapter(self.adapters.duel_adapter)
        except Exception as e:
            msg = f'Error loading duel id: "{self.request.duel_id}": ' \
                  f'{exception_str(e)}'
            raise LoadDuelException(msg)

    def run(self):
        try:
            self._load_duel()
            if self._can_end():
                self._load_members()
                self._check_resignation()
                if self.duel_ready_to_finish(self.duel):
                    self._judge_duel()

            response = EndDuelResponseModel(self.duel,
                                            self.submission_datetime)
            return response
        except Exception as exc:
            msg = f'Error during duel ending: ' \
                  f'{self.request.duel_id} - {exc.__class__.__name__}({exc})'
            self.logger.error(msg)
            raise EndDuelException(msg)
