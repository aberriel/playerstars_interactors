from .duel_settlement_task import DuelSettlementTask
from playerstars_adapters import (
    DuelAdapter,
    NotificationAdapter,
    PlayerAdapter,
    TeamAdapter,
    ValuesAdapter)
from playerstars_domain import (
    CoinType,
    Duel,
    DuelStatus,
    NotificationType,
    Player, Team)
from playerstars_domain.utils.datetime_helper import aware_now
from playerstars_interactors.utils.domain_utils import find_entity_by_id
import logging


class DuelSettlementTaskTeam(DuelSettlementTask):
    def __init__(self,
                 duel: Duel,
                 duel_adapter: DuelAdapter,
                 notification_adapter: NotificationAdapter,
                 player_adapter: PlayerAdapter,
                 team_adapter: TeamAdapter,
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
        self.team_adapter = team_adapter

    def get_challenger(self):
        return self.team_adapter.get_by_id(self.duel.challenger)

    def get_challenged(self):
        return self.team_adapter.get_by_id(self.duel.challenged)

    def update_winner(self, winner):
        winner = self.add_victory_on_game(winner)
        player_captain = self._get_player_by_id(winner.captain.player_id)
        updated_captain = self.pay_player(player_captain,
                                          self.duel.total_reward)
        updated_captain.save()
        winner.save()
        return winner

    def _get_player_by_id(self, player_id):
        player_captain = find_entity_by_id(
            _id=player_id,
            adapter_instance=self.player_adapter,
            class_name='Player')
        return player_captain

    def _get_captain(self, team: Team):
        return self._get_player_by_id(team.captain.player_id)

    @staticmethod
    def add_victory_on_game(duel_member):
        duel_member.victories += 1
        return duel_member

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
            additional_data=str(self.mount_additional_notification_data()))
        self._cancel_duel()

    def _cancel_duel(self):
        self.duel.status = DuelStatus.CANCELED_BY_INCONSISTENT_RESULT
        self.duel.time_finish = aware_now()
        self.update_duel()

    # TODO: Por que o empate não grava o time_finish como o cancelamento?
    def _tie_duel(self):
        self.duel.status = DuelStatus.FINISHED_BY_TIE
        self.duel.time_finish = aware_now()
        self.update_duel()

    def _notify_members(
            self, notification_type, complement=None, additional_data=None):
        self._notify_challenger(notification_type, complement, additional_data)
        self._notify_challenged(notification_type, complement, additional_data)

    def _pay_members(self):
        self._pay_challenger()
        self._pay_challenged()

    def _notify_challenged(self, notification_type: NotificationType,
                           complement: str = None,
                           additional_data: str = None):
        self.send_notification(
            player_id=self.challenged.captain.player_id,
            team_id=self.challenged.entity_id,
            notification_type=notification_type,
            complement=complement,
            additional_data=additional_data)

    def _notify_challenger(self, notification_type: NotificationType,
                           complement: str = None,
                           additional_data: str = None):
        self.send_notification(
            player_id=self.challenger.captain.player_id,
            team_id=self.challenger.entity_id,
            notification_type=notification_type,
            complement=complement,
            additional_data=additional_data)

    def _pay_challenged(self):
        captain_data: Player = self._get_captain(self.challenged)
        captain_data = self.pay_player(captain_data, self.duel.bet_size)
        captain_data.save()

    def _pay_challenger(self):
        captain_data: Player = self._get_captain(self.challenger)
        captain_data = self.pay_player(captain_data, self.duel.bet_size)
        captain_data.save()

    def do_tie_tasks(self):
        if self.duel.star_type == CoinType.GOLDEN_STAR:
            self._pay_members()
        self._notify_members(NotificationType.DUEL_TIED)
        self._tie_duel()

    def finish_by_victory(self, winner_id: str):
        loser, winner = self._process_members_by_victory(winner_id)
        self._update_duel_by_victory(winner_id)
        self._notify_members_by_victory(loser, winner)

    def _notify_members_by_victory(self, loser, winner):
        self._notify_winner(winner)
        self._notify_loser(loser, winner)

    def _notify_loser(self, loser, winner):
        loser_notification_complement = winner.name
        self.send_notification(
            player_id=loser.captain.player_id,
            team_id=loser.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            complement=loser_notification_complement)

    def _notify_winner(self, winner):
        winner_notification_complement = \
            f'{self.duel.total_reward} ' \
            f'{self.get_coin_type_name_to_notification(self.duel.star_type)}'
        self.send_notification(
            player_id=winner.captain.player_id,
            team_id=winner.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            complement=winner_notification_complement)

    def _update_duel_by_victory(self, winner_id):
        self.duel.status = DuelStatus.FINISHED_BY_VICTORY
        self.duel.winner = winner_id
        self.duel.time_finish = aware_now()
        self.update_duel()

    def get_member_adapter(self):
        return self.team_adapter
