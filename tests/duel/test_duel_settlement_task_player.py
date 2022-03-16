from collections import namedtuple
from playerstars_adapters import (
    DuelAdapter,
    NotificationAdapter,
    PlayerAdapter,
    ValuesAdapter)
from playerstars_domain import (
    CoinType,
    Duel,
    DuelJudgeResult,
    DuelMemberType,
    DuelStatus,
    GamePoints,
    ImageValidity,
    NotificationType,
    PlayerConsoles)
from playerstars_interactors.duel import (
    DuelSettlementException,
    DuelSettlementTaskPlayer)
from pytest import fixture
from unittest import TestCase
from unittest.mock import call, MagicMock, patch

import pytest


prefix = 'playerstars_interactors.duel.duel_settlement_task.' \
         'duel_settlement_task_player'
prefix_super_class = 'playerstars_interactors.duel.' \
                     'duel_settlement_task.duel_settlement_task'


Factory = namedtuple('Factory', 'task, mock_duel, mock_duel_adapter, '
                                'mock_notification_adapter, '
                                'mock_player_adapter, mock_values_adapter, '
                                'mock_judge_matrix')


def mount_game_points():
    return GamePoints(
        game_id='game123',
        victories=1)


@fixture(scope='class')
def task_fixture(request):
    def factory(duel: Duel = MagicMock(),
                duel_adapter: DuelAdapter = MagicMock(),
                notification_adapter: NotificationAdapter = MagicMock(),
                player_adapter: PlayerAdapter = MagicMock(),
                values_adapter: ValuesAdapter = MagicMock(),
                judge_matrix: str = MagicMock()):
        task = DuelSettlementTaskPlayer(
            duel=duel,
            duel_adapter=duel_adapter,
            notification_adapter=notification_adapter,
            player_adapter=player_adapter,
            values_adapter=values_adapter,
            judge_matrix=judge_matrix)
        return Factory(task, duel, duel_adapter, notification_adapter,
                       player_adapter, values_adapter, judge_matrix)
    request.cls.factory = factory


@pytest.mark.usefixtures('task_fixture')
class TestDuelSettlementTaskPlayer(TestCase):
    def setUp(self):
        fac = TestDuelSettlementTaskPlayer.factory()
        self.task: DuelSettlementTaskPlayer = fac.task
        self.mock_duel = fac.mock_duel
        self.mock_duel_adapter = fac.mock_duel_adapter
        self.mock_notification_adapter = fac.mock_notification_adapter
        self.mock_player_adapter = fac.mock_player_adapter
        self.mock_values_adapter = fac.mock_values_adapter
        self.mock_judge_matrix = fac.mock_judge_matrix

    def tearDown(self):
        pass

    def test_init(self):
        assert self.task.duel == self.mock_duel
        assert self.task.duel_adapter == self.mock_duel_adapter
        assert self.task.notification_adapter == \
            self.mock_notification_adapter
        assert self.task.player_adapter == self.mock_player_adapter
        assert self.task.values_adapter == self.mock_values_adapter
        assert self.task.judge_matrix == self.mock_judge_matrix

    def test_get_coin_type_name_to_notification__golden(self):
        mock_coin_type = CoinType.GOLDEN_STAR
        result = self.task.get_coin_type_name_to_notification(mock_coin_type)
        assert result == 'Stars Gold'

    def test_get_coin_type_name_to_notification__red(self):
        mock_coin_type = CoinType.RED_STAR
        result = self.task.get_coin_type_name_to_notification(mock_coin_type)
        assert result == 'Stars Red'

    @patch(f'{prefix_super_class}.find_entity_by_id')
    def test__get_member_player(self, mock_find_entity_by_id):
        mock_member_id = MagicMock()
        result = self.task._get_member_player(mock_member_id)
        mock_find_entity_by_id.assert_called_with(
            _id=mock_member_id,
            adapter_instance=self.mock_player_adapter,
            class_name='Player')
        assert result == mock_find_entity_by_id()

    @patch.object(DuelSettlementTaskPlayer, '_get_member_player')
    @patch(f'{prefix_super_class}.create_notification')
    def test_send_notification(self, mock_create_notification,
                               mock_get_member_player):
        mock_player_id = MagicMock()
        mock_notification_type = MagicMock()
        mock_complement = MagicMock()
        mock_additional_data = MagicMock()
        mock_team_id = MagicMock()
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task.send_notification(
            player_id=mock_player_id,
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data,
            team_id=mock_team_id)

        mock_get_member_player.assert_called_with(mock_player_id)
        mock_create_notification.assert_called_with(
            player_data=mock_get_member_player(),
            notification_adapter=self.mock_notification_adapter,
            logger_instance=self.task.logger,
            notification_type=mock_notification_type,
            duel_id=mock_duel.entity_id,
            team_id=mock_team_id,
            notification_image=mock_duel.game.logo_path,
            notification_complement=mock_complement,
            additional_data=mock_additional_data)

    def test_get_validator_class_name(self):
        mock_duel = MagicMock()
        mock_duel.game.entity_id = '1'
        self.task.duel = mock_duel

        mock_value = MagicMock()
        mock_validator_map = MagicMock()
        mock_validator_map.game_id = '1'
        mock_value.validator_maps = [mock_validator_map]
        self.mock_values_adapter.list_all = \
            MagicMock(return_value=[mock_value])

        result = self.task.get_validator_class_name()

        self.mock_values_adapter.list_all.assert_called()
        assert result == mock_validator_map.class_name

    def test_get_validator_class_name__none(self):
        result = self.task.get_validator_class_name()
        assert result is None
        self.mock_values_adapter.list_all.assert_called()

    @patch.object(DuelSettlementTaskPlayer, 'get_validator_class_name')
    @patch(f'{prefix_super_class}.check_image')
    def test_compare_result_with_image(
            self, mock_check_image, mock_get_validator_class_name):
        mock_result = MagicMock()
        mock_player_tag_name = MagicMock()
        result = self.task.compare_result_with_image(
            result=mock_result,
            player_tag_name=mock_player_tag_name)

        mock_get_validator_class_name.assert_called()
        mock_check_image.assert_called_with(
            player_result=mock_result,
            tag_name=mock_player_tag_name,
            validator_class_name=mock_get_validator_class_name(),
            logger=self.task.logger)
        assert result == mock_check_image()

    @patch.object(DuelSettlementTaskPlayer, 'get_validator_class_name')
    @patch(f'{prefix_super_class}.check_image')
    def test_compare_result_with_image__not_result(
            self, mock_check_image, mock_get_validator_class_name):
        mock_result = None
        mock_player_tag_name = MagicMock()
        result = self.task.compare_result_with_image(
            result=mock_result,
            player_tag_name=mock_player_tag_name)
        assert result == ImageValidity.NOT_SENT

        mock_get_validator_class_name.assert_not_called()
        mock_check_image.assert_not_called()

    def test_get_team_captain_tag_name(self):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_team = MagicMock()
        result = self.task.get_team_captain_tag_name(mock_team)
        self.mock_player_adapter.get_by_id.assert_called_with(
            mock_team.captain.player_id)
        self.mock_player_adapter.get_by_id().get_tag_name.assert_called_with(
            mock_duel.console.entity_id)
        assert result == self.mock_player_adapter.get_by_id().get_tag_name()

    @patch(f'{prefix_super_class}.PlayerDuelInfo')
    @patch.object(DuelSettlementTaskPlayer, 'get_team_captain_tag_name')
    @patch.object(DuelSettlementTaskPlayer, 'compare_result_with_image')
    def test_process_member_result__duel_player(
            self, mock_compare_result_with_image,
            mock_get_team_captain_tag_name,
            mock_player_duel_info):
        self.task.logger = MagicMock()
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.PLAYER
        self.task.duel = mock_duel

        mock_duel_result = MagicMock()
        mock_member = MagicMock()
        result = self.task.process_member_result(
            duel_result=mock_duel_result,
            member=mock_member)

        logger_info_calls = [call('image validation'),
                             call(mock_compare_result_with_image()),
                             call('duel result.result'),
                             call(mock_duel_result.result)]
        self.task.logger.info.assert_has_calls(logger_info_calls)

        mock_member.get_tag_name.assert_called()
        mock_get_team_captain_tag_name.assert_not_called()
        mock_compare_result_with_image.assert_called()
        mock_player_duel_info.get_player_duel_info.assert_called_with(
            duel_member_result=mock_duel_result,
            image_validation=mock_compare_result_with_image())
        assert result == mock_player_duel_info.get_player_duel_info()

    @patch(f'{prefix_super_class}.PlayerDuelInfo')
    @patch.object(DuelSettlementTaskPlayer, 'get_team_captain_tag_name')
    @patch.object(DuelSettlementTaskPlayer, 'compare_result_with_image')
    def test_process_member_result__duel_team(
            self, mock_compare_result_with_image,
            mock_get_team_captain_tag_name,
            mock_player_duel_info):
        self.task.logger = MagicMock()
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.TEAM
        self.task.duel = mock_duel

        mock_duel_result = MagicMock()
        mock_member = MagicMock()
        result = self.task.process_member_result(
            duel_result=mock_duel_result,
            member=mock_member)

        logger_info_calls = [call('image validation'),
                             call(mock_compare_result_with_image()),
                             call('duel result.result'),
                             call(mock_duel_result.result)]
        self.task.logger.info.assert_has_calls(logger_info_calls)

        mock_member.get_tag_name.assert_not_called()
        mock_get_team_captain_tag_name.assert_called_with(mock_member)
        mock_compare_result_with_image.assert_called()
        mock_player_duel_info.get_player_duel_info.assert_called_with(
            duel_member_result=mock_duel_result,
            image_validation=mock_compare_result_with_image())
        assert result == mock_player_duel_info.get_player_duel_info()

    @patch(f'{prefix_super_class}.PlayerDuelInfo')
    @patch.object(DuelSettlementTaskPlayer, 'get_team_captain_tag_name')
    @patch.object(DuelSettlementTaskPlayer, 'compare_result_with_image')
    def test_process_member_result__duel_result_none(
            self, mock_compare_result_with_image,
            mock_get_team_captain_tag_name,
            mock_player_duel_info):
        self.task.logger = MagicMock()
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.PLAYER
        self.task.duel = mock_duel

        mock_duel_result = None
        mock_member = MagicMock()
        result = self.task.process_member_result(
            duel_result=mock_duel_result,
            member=mock_member)

        logger_info_calls = [call('image validation'),
                             call(mock_compare_result_with_image()),
                             call('duel result.result'),
                             call('none')]
        self.task.logger.info.assert_has_calls(logger_info_calls)

        mock_member.get_tag_name.assert_called()
        mock_get_team_captain_tag_name.assert_not_called()
        mock_compare_result_with_image.assert_called()
        mock_player_duel_info.get_player_duel_info.assert_called_with(
            duel_member_result=mock_duel_result,
            image_validation=mock_compare_result_with_image())
        assert result == mock_player_duel_info.get_player_duel_info()

    @patch.object(DuelSettlementTaskPlayer, 'get_challenger')
    @patch.object(DuelSettlementTaskPlayer, 'process_member_result')
    def test_process_challenger_result(
            self, mock_process_member_result, mock_get_challenger):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        result = self.task.process_challenger_result()
        mock_get_challenger.assert_called()
        mock_process_member_result.assert_called_with(
            mock_duel.challenger_duel_result, mock_get_challenger())
        assert result == mock_process_member_result()

    @patch.object(DuelSettlementTaskPlayer, 'get_challenged')
    @patch.object(DuelSettlementTaskPlayer, 'process_member_result')
    def test_process_challenged_result(
            self, mock_process_member_result, mock_get_challenged):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        result = self.task.process_challenged_result()
        mock_get_challenged.assert_called()
        mock_process_member_result.assert_called_with(
            mock_duel.challenged_duel_result, mock_get_challenged())
        assert result == mock_process_member_result()

    @patch(f'{prefix_super_class}.JudgeMatrix')
    @patch.object(DuelSettlementTaskPlayer, 'process_challenger_result')
    @patch.object(DuelSettlementTaskPlayer, 'process_challenged_result')
    def test_make_duel_judge(self, mock_process_challenged_result,
                             mock_process_challenger_result,
                             mock_judge_matrix):
        mock_judge_matrix_raw = MagicMock()
        self.task.judge_matrix = mock_judge_matrix_raw
        result = self.task.make_duel_judge()
        mock_process_challenger_result.assert_called()
        mock_process_challenged_result.assert_called()
        mock_judge_matrix.assert_called_with(
            mock_process_challenger_result(),
            mock_process_challenged_result(),
            mock_judge_matrix_raw)
        mock_judge_matrix().judge_result.assert_called()
        assert result == mock_judge_matrix().judge_result()

    @patch(f'{prefix_super_class}.JudgeMatrix.judge_result',
           return_value=None)
    @patch.object(DuelSettlementTaskPlayer, 'process_challenger_result')
    @patch.object(DuelSettlementTaskPlayer, 'process_challenged_result')
    def test_make_duel_judge__judge_result_none(
            self, mock_process_challenged_result,
            mock_process_challenger_result,
            mock_judge_matrix):
        with pytest.raises(DuelSettlementException) as exc:
            self.task.make_duel_judge()
        assert f'Duel Settlement Error: The result ' \
               f'{mock_process_challenger_result().report_state.value} and ' \
               f'{mock_process_challenged_result().report_state.value} ' \
               f'is impossible.' in str(exc.value)

    @patch.object(DuelSettlementTaskPlayer, 'finish_by_victory')
    def test__finish_by_victory_player1(self, mock_finish_by_victory):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._finish_by_victory_player1()
        mock_finish_by_victory.assert_called_with(mock_duel.challenger)

    @patch.object(DuelSettlementTaskPlayer, 'finish_by_victory')
    def test__finish_by_victory_player2(self, mock_finish_by_victory):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._finish_by_victory_player2()
        mock_finish_by_victory.assert_called_with(mock_duel.challenged)

    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player1')
    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player2')
    @patch.object(DuelSettlementTaskPlayer, 'do_tie_tasks')
    @patch.object(DuelSettlementTaskPlayer, 'cancel_by_inconsistent_result')
    def test_process_judge_result__player1_win(
            self, mock_cancel, mock_tie, mock_victory_2, mock_victory_1):
        mock_judge_result = DuelJudgeResult.PLAYER1_WIN
        self.task.process_judge_result(mock_judge_result)

        mock_victory_1.assert_called()
        mock_victory_2.assert_not_called()
        mock_tie.assert_not_called()
        mock_cancel.assert_not_called()

    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player1')
    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player2')
    @patch.object(DuelSettlementTaskPlayer, 'do_tie_tasks')
    @patch.object(DuelSettlementTaskPlayer, 'cancel_by_inconsistent_result')
    def test_process_judge_result__player2_win(
            self, mock_cancel, mock_tie, mock_victory_2, mock_victory_1):
        mock_judge_result = DuelJudgeResult.PLAYER2_WIN
        self.task.process_judge_result(mock_judge_result)

        mock_victory_1.assert_not_called()
        mock_victory_2.assert_called()
        mock_tie.assert_not_called()
        mock_cancel.assert_not_called()

    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player1')
    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player2')
    @patch.object(DuelSettlementTaskPlayer, 'do_tie_tasks')
    @patch.object(DuelSettlementTaskPlayer, 'cancel_by_inconsistent_result')
    def test_process_judge_result__tied(
            self, mock_cancel, mock_tie, mock_victory_2, mock_victory_1):
        mock_judge_result = DuelJudgeResult.TIED
        self.task.process_judge_result(mock_judge_result)

        mock_victory_1.assert_not_called()
        mock_victory_2.assert_not_called()
        mock_tie.assert_called()
        mock_cancel.assert_not_called()

    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player1')
    @patch.object(DuelSettlementTaskPlayer, '_finish_by_victory_player2')
    @patch.object(DuelSettlementTaskPlayer, 'do_tie_tasks')
    @patch.object(DuelSettlementTaskPlayer, 'cancel_by_inconsistent_result')
    def test_process_judge_result__invalidated(
            self, mock_cancel, mock_tie, mock_victory_2, mock_victory_1):
        mock_judge_result = DuelJudgeResult.INVALIDATED
        self.task.process_judge_result(mock_judge_result)

        mock_victory_1.assert_not_called()
        mock_victory_2.assert_not_called()
        mock_tie.assert_not_called()
        mock_cancel.assert_called()

    def test__pay_player_redstar(self):
        mock_player = MagicMock()
        mock_player.red_star_balance = 1
        mock_player.golden_star_balance = 1
        mock_value = 2
        result = self.task._pay_player_redstar(mock_player, mock_value)

        assert result.red_star_balance == 3
        assert result.golden_star_balance == 1

    def test__pay_player_goldstar(self):
        mock_player = MagicMock()
        mock_player.red_star_balance = 1
        mock_player.golden_star_balance = 1
        mock_value = 2
        result = self.task._pay_player_goldstar(mock_player, mock_value)

        assert result.red_star_balance == 1
        assert result.golden_star_balance == 3

    @patch.object(DuelSettlementTaskPlayer, '_pay_player_goldstar')
    @patch.object(DuelSettlementTaskPlayer, '_pay_player_redstar')
    def test_pay_player__golden(self, mock_pay_red, mock_pay_golden):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.GOLDEN_STAR
        self.task.duel = mock_duel
        mock_player = MagicMock()
        mock_value = MagicMock()
        result = self.task.pay_player(mock_player, mock_value)

        mock_pay_red.assert_not_called()
        mock_pay_golden.assert_called_with(mock_player, mock_value)
        assert result == mock_pay_golden()

    @patch.object(DuelSettlementTaskPlayer, '_pay_player_goldstar')
    @patch.object(DuelSettlementTaskPlayer, '_pay_player_redstar')
    def test_pay_player__red(self, mock_pay_red, mock_pay_golden):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.RED_STAR
        self.task.duel = mock_duel
        mock_player = MagicMock()
        mock_value = MagicMock()
        result = self.task.pay_player(mock_player, mock_value)

        mock_pay_red.assert_called_with(mock_player, mock_value)
        mock_pay_golden.assert_not_called()
        assert result == mock_pay_red()

    def test_update_duel(self):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task.update_duel()
        mock_duel.set_adapter.assert_called_with(self.mock_duel_adapter)
        mock_duel.save.assert_called()

    @patch(f'{prefix_super_class}.update_elo_ratings')
    @patch.object(DuelSettlementTaskPlayer, 'update_winner')
    def test__process_members_by_victory__winner_challenger(
            self, mock_update_winner, mock_update_elo_ratings):
        mock_winner_id = MagicMock()
        mock_challenger = MagicMock()
        mock_challenger.entity_id = mock_winner_id
        self.task.challenger = mock_challenger
        mock_challenged = MagicMock()
        self.task.challenged = mock_challenged
        loser, winner = self.task._process_members_by_victory(mock_winner_id)

        mock_update_winner.assert_called_with(mock_challenger)
        mock_update_elo_ratings.assert_called_with(
            winner=mock_update_winner(),
            loser=mock_challenged)
        assert loser == mock_challenged
        assert winner == mock_challenger

    @patch(f'{prefix_super_class}.update_elo_ratings')
    @patch.object(DuelSettlementTaskPlayer, 'update_winner')
    def test__process_members_by_victory__winner_challenged(
            self, mock_update_winner, mock_update_elo_ratings):
        mock_winner_id = MagicMock()
        mock_challenger = MagicMock()
        self.task.challenger = mock_challenger
        mock_challenged = MagicMock()
        mock_challenged.entity_id = mock_winner_id
        self.task.challenged = mock_challenged
        loser, winner = self.task._process_members_by_victory(mock_winner_id)

        mock_update_winner.assert_called_with(mock_challenged)
        mock_update_elo_ratings.assert_called_with(
            winner=mock_update_winner(),
            loser=mock_challenger)
        assert loser == mock_challenger
        assert winner == mock_challenged

    @patch.object(DuelSettlementTaskPlayer, 'get_member_adapter')
    @patch.object(DuelSettlementTaskPlayer, 'get_challenger')
    @patch.object(DuelSettlementTaskPlayer, 'get_challenged')
    @patch.object(DuelSettlementTaskPlayer, 'make_duel_judge')
    @patch.object(DuelSettlementTaskPlayer, 'process_judge_result')
    def test_run(self, mock_process_judge_result,
                 mock_make_duel_judge,
                 mock_get_challenged,
                 mock_get_challenger,
                 mock_get_member_adapter):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        result = self.task.run()

        mock_get_member_adapter.assert_called()
        mock_get_challenger.assert_called()
        mock_get_challenger().set_adapter.assert_called_with(
            mock_get_member_adapter())
        mock_get_challenged.assert_called()
        mock_get_challenged().set_adapter.assert_called_with(
            mock_get_member_adapter())
        mock_make_duel_judge.assert_called()
        mock_process_judge_result.assert_called_with(
            mock_make_duel_judge())
        assert result == mock_duel

    def test_get_challenger(self):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        result = self.task.get_challenger()
        self.mock_player_adapter.get_by_id.assert_called_with(
            mock_duel.challenger)
        assert result == self.mock_player_adapter.get_by_id()

    def test_get_challenged(self):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        result = self.task.get_challenged()
        self.mock_player_adapter.get_by_id.assert_called_with(
            mock_duel.challenged)
        assert result == self.mock_player_adapter.get_by_id()

    @patch.object(DuelSettlementTaskPlayer, 'add_victory_on_game')
    @patch.object(DuelSettlementTaskPlayer, 'pay_player')
    def test_update_winner(self, mock_pay_player, mock_add_victory_on_game):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_winner = MagicMock()
        result = self.task.update_winner(mock_winner)

        mock_add_victory_on_game.assert_called_with(mock_winner)
        mock_pay_player.assert_called_with(mock_add_victory_on_game(),
                                           mock_duel.total_reward)
        mock_pay_player().save.assert_called()
        assert result == mock_pay_player()

    def test__get_player_console(self):
        mock_duel = MagicMock()
        mock_duel.console.entity_id = '1'
        self.task.duel = mock_duel

        mock_duel_member_console = MagicMock()
        mock_duel_member_console.console_id = '1'
        mock_duel_member = MagicMock()
        mock_duel_member.consoles = [mock_duel_member_console]

        result = self.task._get_player_console(mock_duel_member)
        assert result == mock_duel_member_console

    def test__get_player_console__error(self):
        mock_duel_member = MagicMock()
        mock_duel_member.user.nickname = 'a'
        mock_duel = MagicMock()
        mock_duel.console.name = 'b'
        self.task.duel = mock_duel

        with pytest.raises(Exception) as exc:
            self.task._get_player_console(mock_duel_member)
        assert "Player a doesn't have console b" in str(exc.value)

    @patch(f'{prefix}.GamePoints')
    def test__get_game_points(self, mock_game_points_obj):
        mock_player_console = MagicMock()
        mock_duel = MagicMock()
        mock_duel.game.entity_id = '1'
        self.task.duel = mock_duel

        mock_game_point = MagicMock()
        mock_game_point.game_id = '1'
        mock_player_console.game_points = [mock_game_point]

        result = self.task._get_game_points(mock_player_console)
        assert result == mock_game_point
        mock_game_points_obj.assert_not_called

    @patch(f'{prefix}.GamePoints')
    def test__get_game_points__error(self, mock_game_points_obj):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_player_console = MagicMock()
        result = self.task._get_game_points(mock_player_console)
        mock_game_points_obj.assert_called_with(
            game_id=mock_duel.game.entity_id,
            victories=0)
        assert result == mock_game_points_obj()

    @patch.object(DuelSettlementTaskPlayer, '_get_player_console')
    @patch.object(DuelSettlementTaskPlayer, '_get_game_points',
                  return_value=mount_game_points())
    @patch.object(DuelSettlementTaskPlayer, '_get_game_points_list',
                  return_value=[mount_game_points()])
    @patch.object(DuelSettlementTaskPlayer, '_get_player_console_list')
    def test_add_victory_on_game(self, mock_get_player_console_list,
                                 mock_get_game_points_list,
                                 mock_get_game_points,
                                 mock_get_player_console):
        mock_duel_member = MagicMock()
        result = self.task.add_victory_on_game(mock_duel_member)

        mock_get_player_console.assert_called_with(mock_duel_member)
        mock_get_game_points.assert_called_with(mock_get_player_console())
        mock_get_game_points_list.assert_called_with(
            mock_get_player_console())
        mock_get_player_console_list.assert_called_with(mock_duel_member)
        assert result == mock_duel_member
        assert result.consoles == mock_get_player_console_list()

    def test__get_player_console_list(self):
        mock_console = MagicMock()
        mock_console.console_id = '1'
        mock_duel = MagicMock()
        mock_duel.console.entity_id = '1'
        self.task.duel = mock_duel
        mock_duel_member = MagicMock()
        mock_duel_member.consoles = [mock_console]
        result = self.task._get_player_console_list(mock_duel_member)
        assert result == []

    def test__get_game_points_list(self):
        game_points = GamePoints(
            game_id='game123',
            victories=1)
        player_consoles = PlayerConsoles(
            console_id='console123',
            tag_name='tag',
            game_points=[game_points])
        mock_duel = MagicMock()
        mock_duel.game.entity_id = game_points.game_id
        self.task.duel = mock_duel

        result = self.task._get_game_points_list(player_consoles)
        assert result == []

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

    @patch.object(DuelSettlementTaskPlayer, '_pay_members')
    @patch.object(DuelSettlementTaskPlayer, '_notify_members')
    @patch.object(DuelSettlementTaskPlayer, '_cancel_duel')
    @patch.object(DuelSettlementTaskPlayer,
                  'mount_additional_notification_data')
    def test_cancel_by_inconsistent_result(
            self, mock_mount_additional_notification_data,
            mock_cancel_duel,
            mock_notify_members,
            mock_pay_members):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.RED_STAR
        self.task.duel = mock_duel
        self.task.cancel_by_inconsistent_result()

        mock_pay_members.assert_not_called()
        mock_mount_additional_notification_data.assert_called()
        mock_notify_members.assert_called_with(
            notification_type=NotificationType.DUEL_FINISHED_CONFLICT,
            additional_data=mock_mount_additional_notification_data())
        mock_cancel_duel.assert_called()

    @patch.object(DuelSettlementTaskPlayer, '_pay_members')
    @patch.object(DuelSettlementTaskPlayer, '_notify_members')
    @patch.object(DuelSettlementTaskPlayer, '_cancel_duel')
    @patch.object(DuelSettlementTaskPlayer,
                  'mount_additional_notification_data')
    def test_cancel_by_inconsistent_result__golden_star(
            self, mock_mount_additional_notification_data,
            mock_cancel_duel,
            mock_notify_members,
            mock_pay_members):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.GOLDEN_STAR
        self.task.duel = mock_duel
        self.task.cancel_by_inconsistent_result()

        mock_pay_members.assert_called()
        mock_mount_additional_notification_data.assert_called()
        mock_notify_members.assert_called_with(
            notification_type=NotificationType.DUEL_FINISHED_CONFLICT,
            additional_data=mock_mount_additional_notification_data())
        mock_cancel_duel.assert_called()

    @patch(f'{prefix}.aware_now')
    @patch.object(DuelSettlementTaskPlayer, 'update_duel')
    def test__cancel_duel(self, mock_update_duel, mock_aware_now):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._cancel_duel()

        mock_aware_now.assert_called()
        mock_update_duel.assert_called()
        assert self.task.duel.time_finish == mock_aware_now()
        assert self.task.duel.status == \
            DuelStatus.CANCELED_BY_INCONSISTENT_RESULT

    @patch.object(DuelSettlementTaskPlayer, 'send_notification')
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
            player_id=mock_challenged.entity_id,
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data)

    @patch.object(DuelSettlementTaskPlayer, 'send_notification')
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
            player_id=mock_challenger.entity_id,
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data)

    @patch.object(DuelSettlementTaskPlayer, 'pay_player')
    def test__pay_challenged(self, mock_pay_player):
        mock_challenged = MagicMock()
        self.task.challenged = mock_challenged
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._pay_challenged()

        mock_pay_player.assert_called_with(mock_challenged,
                                           mock_duel.bet_size)
        mock_pay_player().save.assert_called()

    @patch.object(DuelSettlementTaskPlayer, 'pay_player')
    def test__pay_challenger(self, mock_pay_player):
        mock_challenger = MagicMock()
        self.task.challenger = mock_challenger
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        self.task._pay_challenger()

        mock_pay_player.assert_called_with(mock_challenger,
                                           mock_duel.bet_size)
        mock_pay_player().save.assert_called()

    @patch(f'{prefix}.aware_now')
    @patch.object(DuelSettlementTaskPlayer, '_pay_members')
    @patch.object(DuelSettlementTaskPlayer, '_notify_members')
    @patch.object(DuelSettlementTaskPlayer, 'update_duel')
    def test_do_tie_tasks_red(self, mock_update_duel,
                              mock_notify_members,
                              mock_pay_members,
                              mock_aware_now):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.RED_STAR
        self.task.duel = mock_duel
        self.task.do_tie_tasks()

        mock_aware_now.assert_called()
        mock_pay_members.assert_not_called()
        mock_notify_members.assert_called_with(NotificationType.DUEL_TIED)
        mock_update_duel.assert_called()

    @patch(f'{prefix}.aware_now')
    @patch.object(DuelSettlementTaskPlayer, '_pay_members')
    @patch.object(DuelSettlementTaskPlayer, '_notify_members')
    @patch.object(DuelSettlementTaskPlayer, 'update_duel')
    def test_do_tie_tasks_golden(self, mock_update_duel,
                                 mock_notify_members,
                                 mock_pay_members,
                                 mock_aware_now):
        mock_duel = MagicMock()
        mock_duel.star_type = CoinType.GOLDEN_STAR
        self.task.duel = mock_duel
        self.task.do_tie_tasks()

        mock_aware_now.assert_called()
        mock_pay_members.assert_called()
        mock_notify_members.assert_called_with(NotificationType.DUEL_TIED)
        mock_update_duel.assert_called()

    @patch.object(DuelSettlementTaskPlayer, '_pay_challenger')
    @patch.object(DuelSettlementTaskPlayer, '_pay_challenged')
    def test__pay_members(self, mock_pay_challenged, mock_pay_challenger):
        self.task._pay_members()
        mock_pay_challenger.assert_called()
        mock_pay_challenged.assert_called()

    @patch.object(DuelSettlementTaskPlayer, '_notify_challenger')
    @patch.object(DuelSettlementTaskPlayer, '_notify_challenged')
    def test__notify_members(self, mock_notify_challenged,
                             mock_notify_challenger):
        mock_notification_type = MagicMock()
        mock_complement = MagicMock()
        mock_additional_data = MagicMock()
        self.task._notify_members(
            notification_type=mock_notification_type,
            complement=mock_complement,
            additional_data=mock_additional_data)

        mock_notify_challenger.assert_called_with(
            mock_notification_type, mock_complement, mock_additional_data)
        mock_notify_challenged.assert_called_with(
            mock_notification_type, mock_complement, mock_additional_data)

    @patch.object(DuelSettlementTaskPlayer,
                  '_process_members_by_victory',
                  return_value=(MagicMock(), MagicMock()))
    @patch.object(DuelSettlementTaskPlayer, '_update_duel_by_victory')
    @patch.object(DuelSettlementTaskPlayer, '_notify_members_by_victory')
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

    @patch.object(DuelSettlementTaskPlayer, '_notify_winner')
    @patch.object(DuelSettlementTaskPlayer, '_notify_loser')
    def test__notify_members_by_victory(self, mock_notify_loser,
                                        mock_notify_winner):
        mock_loser = MagicMock()
        mock_winner = MagicMock()
        self.task._notify_members_by_victory(mock_loser, mock_winner)
        mock_notify_winner.assert_called_with(mock_winner)
        mock_notify_loser.assert_called_with(mock_loser, mock_winner)

    @patch(f'{prefix}.aware_now')
    @patch.object(DuelSettlementTaskPlayer, 'update_duel')
    def test__update_duel_by_victory(self, mock_update_duel, mock_aware_now):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_winner_id = MagicMock()
        self.task._update_duel_by_victory(mock_winner_id)

        mock_aware_now.assert_called()
        mock_update_duel.assert_called()
        assert self.task.duel.status == DuelStatus.FINISHED_BY_VICTORY
        assert self.task.duel.time_finish == mock_aware_now()
        assert self.task.duel.winner == mock_winner_id

    @patch.object(DuelSettlementTaskPlayer, 'send_notification')
    def test__notify_loser(self, mock_send_notification):
        mock_loser = MagicMock()
        mock_winner = MagicMock()
        self.task._notify_loser(mock_loser, mock_winner)
        mock_send_notification.assert_called_with(
            player_id=mock_loser.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            complement=mock_winner.user.nickname)

    @patch.object(DuelSettlementTaskPlayer,
                  'get_coin_type_name_to_notification')
    @patch.object(DuelSettlementTaskPlayer, 'send_notification')
    def test__notify_winner(self, mock_send_notification,
                            mock_get_coint_type_name_to_notification):
        mock_duel = MagicMock()
        self.task.duel = mock_duel
        mock_winner = MagicMock()
        self.task._notify_winner(mock_winner)
        mock_get_coint_type_name_to_notification.assert_called_with(
            mock_duel.star_type)

        mock_complement = f'{mock_duel.total_reward} ' \
                          f'{mock_get_coint_type_name_to_notification()}'
        mock_send_notification.assert_called_with(
            player_id=mock_winner.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            complement=mock_complement)

    def test_get_member_adapter(self):
        result = self.task.get_member_adapter()
        assert result == self.mock_player_adapter
