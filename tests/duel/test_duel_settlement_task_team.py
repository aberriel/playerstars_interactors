from collections import namedtuple
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
    NotificationType)
from playerstars_interactors.duel import DuelSettlementTaskTeam
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.duel.duel_settlement_task.' \
         'duel_settlement_task_team'


Factory = namedtuple('Factory', 'task, mock_duel, mock_duel_adapter, '
                                'mock_notification_adapter, '
                                'mock_player_adapter, mock_team_adapter, '
                                'mock_values_adapter, '
                                'mock_judge_matrix')


@fixture(scope='class')
def task_fixture(request):
    def factory(duel: Duel = MagicMock(),
                duel_adapter: DuelAdapter = MagicMock(),
                notification_adapter: NotificationAdapter = MagicMock(),
                player_adapter: PlayerAdapter = MagicMock(),
                team_adapter: TeamAdapter = MagicMock(),
                values_adapter: ValuesAdapter = MagicMock(),
                judge_matrix: str = MagicMock()):
        task = DuelSettlementTaskTeam(
            duel=duel,
            duel_adapter=duel_adapter,
            notification_adapter=notification_adapter,
            player_adapter=player_adapter,
            team_adapter=team_adapter,
            values_adapter=values_adapter,
            judge_matrix=judge_matrix)
        return Factory(task, duel, duel_adapter, notification_adapter,
                       player_adapter, team_adapter, values_adapter,
                       judge_matrix)
    request.cls.factory = factory


@pytest.mark.usefixtures('task_fixture')
class TestDuelSettlementTaskTeam(TestCase):
    def setUp(self):
        fac = TestDuelSettlementTaskTeam.factory()
        self.task: DuelSettlementTaskTeam = fac.task
        self.mock_duel = fac.mock_duel
        self.mock_duel_adapter = fac.mock_duel_adapter
        self.mock_notification_adapter = fac.mock_notification_adapter
        self.mock_player_adapter = fac.mock_player_adapter
        self.mock_team_adapter = fac.mock_team_adapter
        self.mock_values_adapter = fac.mock_values_adapter
        self.mock_judge_matrix = fac.mock_judge_matrix

    def tearDown(self):
        pass

    def test_init(self):
        assert self.task.duel == self.mock_duel
        assert self.task.duel_adapter == self.mock_duel_adapter
        assert self.task.notification_adapter == self.mock_notification_adapter
        assert self.task.player_adapter == self.mock_player_adapter
        assert self.task.team_adapter == self.mock_team_adapter
        assert self.task.values_adapter == self.mock_values_adapter
        assert self.task.judge_matrix == self.mock_judge_matrix

    def test_get_challenger(self):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        result = self.task.get_challenger()
        self.mock_team_adapter.get_by_id.assert_called_with(
            mock_duel.challenger)
        assert result == self.mock_team_adapter.get_by_id()

    def test_get_challenged(self):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        result = self.task.get_challenged()
        self.mock_team_adapter.get_by_id.assert_called_with(
            mock_duel.challenged)
        assert result == self.mock_team_adapter.get_by_id()

    @patch.object(DuelSettlementTaskTeam, 'add_victory_on_game')
    @patch.object(DuelSettlementTaskTeam, '_get_player_by_id')
    @patch.object(DuelSettlementTaskTeam, 'pay_player')
    def test_update_winner(self, mock_pay_player,
                           mock_get_player_by_id,
                           mock_add_bictory_on_game):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_winner = MagicMock()
        result = self.task.update_winner(mock_winner)

        mock_add_bictory_on_game.assert_called_with(mock_winner)
        mock_get_player_by_id.assert_called_with(
            mock_add_bictory_on_game().captain.player_id)
        mock_pay_player.assert_called_with(mock_get_player_by_id(),
                                           mock_duel.total_reward)
        mock_pay_player().save.assert_called()
        mock_add_bictory_on_game().save.assert_called()
        assert result == mock_add_bictory_on_game()

    @patch(f'{prefix}.find_entity_by_id')
    def test__get_player_by_id(self, mock_find_entity_by_id):
        mock_player_id = MagicMock()
        result = self.task._get_player_by_id(mock_player_id)
        mock_find_entity_by_id.assert_called_with(
            _id=mock_player_id,
            adapter_instance=self.mock_player_adapter,
            class_name='Player')
        assert result == mock_find_entity_by_id()

    @patch.object(DuelSettlementTaskTeam, '_get_player_by_id')
    def test__get_captain(self, mock_get_player_by_id):
        mock_team = MagicMock()
        result = self.task._get_captain(mock_team)
        mock_get_player_by_id.assert_called_with(mock_team.captain.player_id)
        assert result == mock_get_player_by_id()

    def test_add_victory_on_game(self):
        mock_duel_member = MagicMock()
        mock_duel_member.victories = 1
        result = self.task.add_victory_on_game(mock_duel_member)
        assert result.victories == 2

    def test_mount_additional_notification_data(self):
        mock_challenger_duel_info = MagicMock()
        self.task.challenger_duel_info = mock_challenger_duel_info
        mock_challenged_duel_info = MagicMock()
        self.task.challenged_duel_info = mock_challenged_duel_info
        result = self.task.mount_additional_notification_data()

        assert result == {
            'challenger_result_info':
                mock_challenger_duel_info.report_state.value,
            'challenged_result_info':
                mock_challenged_duel_info.report_state.value}

    @patch.object(DuelSettlementTaskTeam, 'mount_additional_notification_data')
    @patch.object(DuelSettlementTaskTeam, '_pay_members')
    @patch.object(DuelSettlementTaskTeam, '_notify_members')
    @patch.object(DuelSettlementTaskTeam, '_cancel_duel')
    def test_cancel_by_inconsistent_result__golden(
            self, mock_cancel_duel,
            mock_notify_members,
            mock_pay_members,
            mock_mount_additional_notification_data):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.GOLDEN_STAR
        self.task.duel = mock_duel
        self.task.cancel_by_inconsistent_result()

        mock_pay_members.assert_called()
        mock_notify_members.assert_called_with(
            notification_type=NotificationType.DUEL_FINISHED_CONFLICT,
            additional_data=str(mock_mount_additional_notification_data()))

    @patch.object(DuelSettlementTaskTeam, 'mount_additional_notification_data')
    @patch.object(DuelSettlementTaskTeam, '_pay_members')
    @patch.object(DuelSettlementTaskTeam, '_notify_members')
    @patch.object(DuelSettlementTaskTeam, '_cancel_duel')
    def test_cancel_by_inconsistent_result__red(
            self, mock_cancel_duel,
            mock_notify_members,
            mock_pay_members,
            mock_mount_additional_notification_data):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.RED_STAR
        self.task.duel = mock_duel
        self.task.cancel_by_inconsistent_result()

        mock_pay_members.assert_not_called()
        mock_notify_members.assert_called_with(
            notification_type=NotificationType.DUEL_FINISHED_CONFLICT,
            additional_data=str(mock_mount_additional_notification_data()))

    @patch(f'{prefix}.aware_now')
    @patch.object(DuelSettlementTaskTeam, 'update_duel')
    def test__cancel_duel(self, mock_update_duel, mock_aware_now):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._cancel_duel()

        assert self.task.duel.status == \
            DuelStatus.CANCELED_BY_INCONSISTENT_RESULT
        assert self.task.duel.time_finish == mock_aware_now()
        mock_update_duel.assert_called()

    @patch(f'{prefix}.aware_now')
    @patch.object(DuelSettlementTaskTeam, 'update_duel')
    def test__tie_duel(self, mock_update_duel, mock_aware_now):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._tie_duel()

        assert self.task.duel.status == DuelStatus.FINISHED_BY_TIE
        assert self.task.duel.time_finish == mock_aware_now()
        mock_update_duel.assert_called()

    @patch.object(DuelSettlementTaskTeam, '_notify_challenger')
    @patch.object(DuelSettlementTaskTeam, '_notify_challenged')
    def test__notify_members(self, mock_notify_challenged,
                             mock_notify_challenger):
        mock_notification_type = MagicMock()
        mock_complement = MagicMock()
        mock_additional_data = MagicMock()
        self.task._notify_members(mock_notification_type,
                                  mock_complement,
                                  mock_additional_data)

        mock_notify_challenger.assert_called_with(
            mock_notification_type, mock_complement, mock_additional_data)
        mock_notify_challenged.assert_called_with(
            mock_notification_type, mock_complement, mock_additional_data)

    @patch.object(DuelSettlementTaskTeam, '_pay_challenger')
    @patch.object(DuelSettlementTaskTeam, '_pay_challenged')
    def test__pay_members(self, mock_pay_challenged, mock_pay_challenger):
        self.task._pay_members()
        mock_pay_challenger.assert_called()
        mock_pay_challenged.assert_called()

    @patch.object(DuelSettlementTaskTeam, 'send_notification')
    def test__notify_challenged(self, mock_send_notification):
        mock_challenged = MagicMock()
        self.task.challenged = mock_challenged

        mock_notification_type = MagicMock()
        mock_complement = MagicMock()
        mock_additional_data = MagicMock()
        self.task._notify_challenged(
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data)

        mock_send_notification.assert_called_with(
            player_id=mock_challenged.captain.player_id,
            team_id=mock_challenged.entity_id,
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data)

    @patch.object(DuelSettlementTaskTeam, 'send_notification')
    def test__notify_challenger(self, mock_send_notification):
        mock_challenger = MagicMock()
        self.task.challenger = mock_challenger

        mock_notification_type = MagicMock()
        mock_complement = MagicMock()
        mock_additional_data = MagicMock()
        self.task._notify_challenger(
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data)

        mock_send_notification.assert_called_with(
            player_id=mock_challenger.captain.player_id,
            team_id=mock_challenger.entity_id,
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data)

    @patch.object(DuelSettlementTaskTeam, '_get_captain')
    @patch.object(DuelSettlementTaskTeam, 'pay_player')
    def test__pay_challenged(self, mock_pay_player, mock_get_captain):
        mock_challenged = MagicMock()
        self.task.challenged = mock_challenged
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._pay_challenged()

        mock_get_captain.assert_called_with(mock_challenged)
        mock_pay_player.assert_called_with(
            mock_get_captain(), mock_duel.bet_size)
        mock_pay_player().save.assert_called()

    @patch.object(DuelSettlementTaskTeam, '_get_captain')
    @patch.object(DuelSettlementTaskTeam, 'pay_player')
    def test__pay_challenger(self, mock_pay_player, mock_get_captain):
        mock_challenger = MagicMock()
        self.task.challenger = mock_challenger
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._pay_challenger()

        mock_get_captain.assert_called_with(mock_challenger)
        mock_pay_player.assert_called_with(mock_get_captain(),
                                           mock_duel.bet_size)
        mock_pay_player().save.assert_called()

    @patch.object(DuelSettlementTaskTeam, '_pay_members')
    @patch.object(DuelSettlementTaskTeam, '_notify_members')
    @patch.object(DuelSettlementTaskTeam, '_tie_duel')
    def test_do_tie_tasks__golden(self, mock_tie_duel,
                                  mock_notify_members,
                                  mock_pay_members):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.GOLDEN_STAR
        self.task.duel = mock_duel
        self.task.do_tie_tasks()

        mock_pay_members.assert_called()
        mock_notify_members.assert_called_with(NotificationType.DUEL_TIED)
        mock_tie_duel.assert_called()

    @patch.object(DuelSettlementTaskTeam, '_pay_members')
    @patch.object(DuelSettlementTaskTeam, '_notify_members')
    @patch.object(DuelSettlementTaskTeam, '_tie_duel')
    def test_do_tie_tasks__red(self, mock_tie_duel,
                               mock_notify_members,
                               mock_pay_members):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.RED_STAR
        self.task.duel = mock_duel
        self.task.do_tie_tasks()

        mock_pay_members.assert_not_called()
        mock_notify_members.assert_called_with(NotificationType.DUEL_TIED)
        mock_tie_duel.assert_called()

    @patch.object(DuelSettlementTaskTeam,
                  '_process_members_by_victory',
                  return_value=(MagicMock(), MagicMock()))
    @patch.object(DuelSettlementTaskTeam, '_update_duel_by_victory')
    @patch.object(DuelSettlementTaskTeam, '_notify_members_by_victory')
    def test_finish_by_victory(self, mock_notify_members_by_victory,
                               mock_update_duel_by_victory,
                               mock_process_members_by_victory):
        mock_winner_id = MagicMock()
        self.task.finish_by_victory(mock_winner_id)
        mock_process_members_by_victory.assert_called_with(mock_winner_id)
        mock_update_duel_by_victory.assert_called_with(mock_winner_id)
        mock_notify_members_by_victory.assert_called_with(
            mock_process_members_by_victory()[0],
            mock_process_members_by_victory()[1])

    @patch.object(DuelSettlementTaskTeam, '_notify_winner')
    @patch.object(DuelSettlementTaskTeam, '_notify_loser')
    def test__notify_members_by_victory(self, mock_notify_loser,
                                        mock_notify_winner):
        mock_loser = MagicMock()
        mock_winner = MagicMock()
        self.task._notify_members_by_victory(mock_loser, mock_winner)

        mock_notify_loser.assert_called_with(mock_loser, mock_winner)
        mock_notify_winner.assert_called_with(mock_winner)

    @patch.object(DuelSettlementTaskTeam, 'send_notification')
    def test__notify_loser(self, mock_send_notification):
        mock_loser = MagicMock()
        mock_winner = MagicMock()
        self.task._notify_loser(mock_loser, mock_winner)
        mock_send_notification.assert_called_with(
            player_id=mock_loser.captain.player_id,
            team_id=mock_loser.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            complement=mock_winner.name)

    @patch.object(DuelSettlementTaskTeam, 'send_notification')
    @patch.object(DuelSettlementTaskTeam, 'get_coin_type_name_to_notification')
    def test__notify_winner(self, mock_get_coin_type_name_to_notification,
                            mock_send_notification):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_winner = MagicMock()
        self.task._notify_winner(mock_winner)

        mock_get_coin_type_name_to_notification.assert_called_with(
            mock_duel.star_type)
        mock_complement = f'{mock_duel.total_reward} ' \
                          f'{mock_get_coin_type_name_to_notification()}'
        mock_send_notification.assert_called_with(
            player_id=mock_winner.captain.player_id,
            team_id=mock_winner.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            complement=mock_complement)

    @patch(f'{prefix}.aware_now')
    @patch.object(DuelSettlementTaskTeam, 'update_duel')
    def test__update_duel_by_victory(self, mock_update_duel,
                                     mock_aware_now):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_winner_id = MagicMock()
        self.task._update_duel_by_victory(mock_winner_id)

        mock_aware_now.assert_called()
        mock_update_duel.assert_called()
        assert self.task.duel.status == DuelStatus.FINISHED_BY_VICTORY
        assert self.task.duel.winner == mock_winner_id
        assert self.task.duel.time_finish == mock_aware_now()

    def test_get_member_adapter(self):
        result = self.task.get_member_adapter()
        assert result == self.mock_team_adapter
