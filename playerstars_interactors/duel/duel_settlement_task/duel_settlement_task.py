import logging
from abc import ABC, abstractmethod
from enum import Enum

from playerstars_adapters import (
    DuelAdapter,
    NotificationAdapter,
    PlayerAdapter,
    ValuesAdapter)
from playerstars_domain import (
    CoinType,
    Duel,
    DuelJudgeResult,
    JudgeMatrix,
    NotificationType,
    Player,
    PlayerDuelInfo,
    DuelMemberType,
    ImageValidity,
    Values)
from playerstars_interactors.duel.duel_utils import update_elo_ratings
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_interactors.utils.image_utils import check_image
from playerstars_interactors.utils.notification_utils import \
    create_notification


class ResultImageCheckStatus(Enum):
    VALID = 'valid'
    INVALID = 'invalid'
    NOT_PROVIDED = 'not_provided'


class DuelSettlementException(BaseException):
    pass


# Documentação dos cenários da finalização de duelo:
# http://bit.ly/duel_finish_uc
class DuelSettlementTask(ABC):
    challenger = None
    challenger_duel_info = None
    challenged = None
    challenged_duel_info = None

    def __init__(self,
                 duel: Duel,
                 duel_adapter: DuelAdapter,
                 notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 values_adapter: ValuesAdapter,
                 judge_matrix: str,
                 logger=None):
        self.duel = duel
        self.duel_adapter = duel_adapter
        self.notification_adapter = notification_adapter
        self.player_adapter = player_adapter
        self.values_adapter = values_adapter
        self.judge_matrix = judge_matrix
        self.logger = logger or logging.getLogger(__name__)

    @staticmethod
    def get_coin_type_name_to_notification(coin_type: CoinType):
        coin_names = {
            CoinType.GOLDEN_STAR: 'Stars Gold',
            CoinType.RED_STAR: 'Stars Red'
        }
        return coin_names[coin_type]

    def _get_member_player(self, member_id):
        return find_entity_by_id(
            _id=member_id,
            adapter_instance=self.player_adapter,
            class_name='Player')

    def send_notification(self,
                          player_id: str,
                          notification_type: NotificationType,
                          complement: str = None,
                          additional_data: str = None,
                          team_id: str = None):
        player_data = self._get_member_player(player_id)
        create_notification(
            player_data=player_data,
            notification_adapter=self.notification_adapter,
            logger_instance=self.logger,
            notification_type=notification_type,
            duel_id=self.duel.entity_id,
            team_id=team_id,
            notification_image=self.duel.game.logo_path,
            notification_complement=complement,
            additional_data=additional_data)

    def get_validator_class_name(self):
        all_values: [Values] = self.values_adapter.list_all()
        validator_maps = all_values[0].validator_maps
        print('self.duel.game.entity_id: ' + str(self.duel.game.entity_id))
        for x in validator_maps:
            print('x: ' + str(x))
            print('x.game_id: ' + str(x.game_id))
            if x.game_id == self.duel.game.entity_id:
                return x.class_name
        return None

    def compare_result_with_image(self, result, player_tag_name):
        if not result or not result.result_image:
            return ImageValidity.NOT_SENT
        validator_class_name = self.get_validator_class_name()
        return check_image(
            player_result=result,
            tag_name=player_tag_name,
            validator_class_name=validator_class_name,
            logger=self.logger)

    def get_team_captain_tag_name(self, team):
        captain = self.player_adapter.get_by_id(team.captain.player_id)
        return captain.get_tag_name(self.duel.console.entity_id)

    def process_member_result(self, duel_result, member):
        tag_name = member.get_tag_name(self.duel.console.entity_id) \
            if self.duel.member_type == DuelMemberType.PLAYER \
            else self.get_team_captain_tag_name(member)
        image_validation: ImageValidity = self.compare_result_with_image(
            duel_result, tag_name)
        self.logger.info('image validation')
        self.logger.info(image_validation)
        self.logger.info('duel result.result')
        if duel_result:
            self.logger.info(duel_result.result)
        else:
            self.logger.info('none')
        player_duel_info = PlayerDuelInfo.get_player_duel_info(
            duel_member_result=duel_result, image_validation=image_validation)

        return player_duel_info

    def process_challenger_result(self):
        challenger = self.get_challenger()
        duel_result = self.duel.challenger_duel_result
        return self.process_member_result(duel_result, challenger)

    def process_challenged_result(self):
        challenged = self.get_challenged()
        duel_result = self.duel.challenged_duel_result
        return self.process_member_result(duel_result, challenged)

    def make_duel_judge(self):
        self.challenger_duel_info = self.process_challenger_result()
        self.challenged_duel_info = self.process_challenged_result()
        jm = JudgeMatrix(self.challenger_duel_info,
                         self.challenged_duel_info,
                         self.judge_matrix)
        judge_result = jm.judge_result()
        if judge_result is None:
            value_1 = self.challenger_duel_info.report_state.value
            value_2 = self.challenged_duel_info.report_state.value
            raise DuelSettlementException(
                f'Duel Settlement Error: The result '
                f'{value_1} and '
                f'{value_2} '
                f'is impossible.')
        return judge_result

    def _finish_by_victory_player1(self):
        self.finish_by_victory(self.duel.challenger)

    def _finish_by_victory_player2(self):
        self.finish_by_victory(self.duel.challenged)

    def process_judge_result(self, judge_result: DuelJudgeResult):
        action_map = {
            DuelJudgeResult.PLAYER1_WIN: self._finish_by_victory_player1,
            DuelJudgeResult.PLAYER2_WIN: self._finish_by_victory_player2,
            DuelJudgeResult.TIED: self.do_tie_tasks,
            DuelJudgeResult.INVALIDATED: self.cancel_by_inconsistent_result
        }
        action_map[judge_result]()

    @abstractmethod
    def finish_by_victory(self, winner: str):
        pass

    @staticmethod
    def _pay_player_redstar(player: Player, value: int):
        player.red_star_balance += value
        return player

    @staticmethod
    def _pay_player_goldstar(player: Player, value: int):
        player.golden_star_balance += value
        return player

    def pay_player(self, player: Player, value: int):
        action_map = {
            CoinType.GOLDEN_STAR: self._pay_player_goldstar,
            CoinType.RED_STAR: self._pay_player_redstar
        }
        return action_map[self.duel.star_type](player, value)

    @abstractmethod
    def cancel_by_inconsistent_result(self):
        pass

    @abstractmethod
    def do_tie_tasks(self):
        pass

    @abstractmethod
    def update_winner(self, winner):
        pass

    def update_duel(self):
        self.duel.set_adapter(self.duel_adapter)
        self.duel.save()

    def _process_members_by_victory(self, winner_id):
        members_by_id = {
            self.challenger.entity_id: self.challenger,
            self.challenged.entity_id: self.challenged
        }
        loser_by_winner_id = {
            self.challenger.entity_id: self.challenged,
            self.challenged.entity_id: self.challenger
        }

        winner = members_by_id[winner_id]
        loser = loser_by_winner_id[winner_id]
        updated_winner = self.update_winner(winner)
        members_by_id[winner_id] = updated_winner
        update_elo_ratings(winner=updated_winner, loser=loser)
        return loser, winner

    @abstractmethod
    def get_challenger(self):
        pass

    @abstractmethod
    def get_challenged(self):
        pass

    @abstractmethod
    def get_member_adapter(self):
        pass

    def run(self):
        member_adapter = self.get_member_adapter()
        self.challenger = self.get_challenger()
        self.challenger.set_adapter(member_adapter)
        self.challenged = self.get_challenged()
        self.challenged.set_adapter(member_adapter)

        judge_result = self.make_duel_judge()
        self.process_judge_result(judge_result)

        return self.duel
