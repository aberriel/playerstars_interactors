from .duel_settlement_task import DuelSettlementTask
from playerstars_adapters import PlayerAdapter, ValuesAdapter, DuelAdapter
from playerstars_domain import (
    CoinType,
    Duel,
    DuelStatus,
    GamePoints,
    NotificationType)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_graphql_adapters import NotificationAdapter
import logging


class DuelSettlementTaskPlayer(DuelSettlementTask):
    def __init__(self,
                 duel: Duel,
                 player_adapter: PlayerAdapter,
                 duel_adapter: DuelAdapter,
                 notification_adapter: NotificationAdapter,
                 values_adapter: ValuesAdapter,
                 judge_matrix: str):
        logger_instance = logging.getLogger(__name__)
        super().__init__(
            duel=duel,
            duel_adapter=duel_adapter,
            notification_adapter=notification_adapter,
            player_adapter=player_adapter,
            values_adapter=values_adapter,
            judge_matrix=judge_matrix,
            logger=logger_instance)

    def get_challenger(self):
        return self.player_adapter.get_by_id(self.duel.challenger)

    def get_challenged(self):
        return self.player_adapter.get_by_id(self.duel.challenged)

    def update_winner(self, winner):
        winner = self.add_victory_on_game(winner)
        winner = self.pay_player(winner, self.duel.total_reward)
        winner.save()
        return winner

    def _get_player_console(self, duel_member):
        try:
            return [x for x in duel_member.consoles
                    if x.console_id == self.duel.console.entity_id][0]
        except IndexError:
            raise Exception("Player {0} doesn't have console {1}"
                            .format(duel_member.user.nickname,
                                    self.duel.console.name))

    def _get_game_points(self, player_console):
        try:
            return [x for x in player_console.game_points
                    if x.game_id == self.duel.game.entity_id][0]
        except IndexError:
            return GamePoints(game_id=self.duel.game.entity_id, victories=0)

    def add_victory_on_game(self, duel_member):
        player_console = self._get_player_console(duel_member)
        game_points = self._get_game_points(player_console)
        game_points.victories = game_points.victories + 1

        game_points_list = self._get_game_points_list(player_console)
        game_points_list.append(game_points)

        player_console.game_points = game_points_list

        player_console_list = self._get_player_console_list(duel_member)
        player_console_list.append(player_console)
        duel_member.consoles = player_console_list

        return duel_member

    def _get_player_console_list(self, duel_member):
        player_console_list = [x for x in duel_member.consoles
                               if x.console_id != self.duel.console.entity_id]
        return player_console_list

    def _get_game_points_list(self, player_console):
        game_points_list = [x for x in player_console.game_points
                            if x.game_id != self.duel.game.entity_id]
        return game_points_list

    def mount_additional_notification_data(self):
        return {
            'challenger_result_info':
                self.challenger_duel_info.report_state.value,
            'challenged_result_info':
                self.challenged_duel_info.report_state.value}

    def cancel_by_inconsistent_result(self):
        if self.duel.star_type == CoinType.GOLDEN_STAR:
            self._pay_members()
        self._notify_members(
            notification_type=NotificationType.DUEL_FINISHED_CONFLICT,
            additional_data=self.mount_additional_notification_data())
        self._cancel_duel()

    def _cancel_duel(self):
        self.duel.status = DuelStatus.CANCELED_BY_INCONSISTENT_RESULT
        self.duel.time_finish = aware_now()
        self.update_duel()

    def _notify_challenged(self, notification_type: NotificationType,
                           complement: str = None,
                           additional_data: str = None):
        self.send_notification(
            player_id=self.challenged.entity_id,
            notification_type=notification_type,
            complement=complement,
            additional_data=additional_data)

    def _notify_challenger(self, notification_type: NotificationType,
                           complement: str = None,
                           additional_data: str = None):
        self.send_notification(
            player_id=self.challenger.entity_id,
            notification_type=notification_type,
            complement=complement,
            additional_data=additional_data)

    def _pay_challenged(self):
        self.challenged = self.pay_player(self.challenged, self.duel.bet_size)
        self.challenged.save()

    def _pay_challenger(self):
        self.challenger = self.pay_player(self.challenger, self.duel.bet_size)
        self.challenger.save()

    def do_tie_tasks(self):
        self.duel.status = DuelStatus.FINISHED_BY_TIE
        self.duel.time_finish = aware_now()
        if self.duel.star_type == CoinType.GOLDEN_STAR:
            self._pay_members()
        self._notify_members(NotificationType.DUEL_TIED)
        self.update_duel()

    def _pay_members(self):
        self._pay_challenger()
        self._pay_challenged()

    def _notify_members(
            self, notification_type, complement=None, additional_data=None):
        self._notify_challenger(
            notification_type, complement, additional_data)
        self._notify_challenged(
            notification_type, complement, additional_data)

    def finish_by_victory(self, winner_id: str):
        loser, winner = self._process_members_by_victory(winner_id)
        self._update_duel_by_victory(winner_id)
        self._notify_members_by_victory(loser, winner)

    def _notify_members_by_victory(self, loser, winner):
        self._notify_winner(winner)
        self._notify_loser(loser, winner)

    def _update_duel_by_victory(self, winner_id):
        self.duel.status = DuelStatus.FINISHED_BY_VICTORY
        self.duel.time_finish = aware_now()
        self.duel.winner = winner_id
        self.update_duel()

    def _notify_loser(self, loser, winner):
        loser_notification_complement = winner.user.nickname
        self.send_notification(
            player_id=loser.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            complement=loser_notification_complement)

    def _notify_winner(self, winner):
        winner_notification_complement = \
            f'{self.duel.total_reward} ' \
            f'{self.get_coin_type_name_to_notification(self.duel.star_type)}'
        self.send_notification(
            player_id=winner.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            complement=winner_notification_complement)

    def get_member_adapter(self):
        return self.player_adapter
