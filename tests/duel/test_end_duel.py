from collections import namedtuple
from itertools import product
from playerstars_domain import (DuelStatus,
                                CoinType,
                                DuelMemberType,
                                ComponentResult,
                                DuelComponentResult,
                                NotificationType)
from playerstars_interactors import (
    EndDuelAdapters,
    EndDuelInteractor,
    EndDuelRequestModel,
    EndDuelResponseModel)
from playerstars_interactors.duel.end_duel import (
    EndDuelException,
    JudgeException,
    LoadDuelException,
    LoadMemberException,
    UpdateDuelException)
from pytest import fixture, raises
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.duel.end_duel'


def test_end_duel_request_model():
    mock_json_data = MagicMock()
    request = EndDuelRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('duel_id', 'duel_id'), ('player_id', 'player_id')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_response_model():
    mock_duel_data = MagicMock()
    mock_submission_datetime = MagicMock()
    response = EndDuelResponseModel(
        duel_data=mock_duel_data,
        submission_datetime=mock_submission_datetime)

    assert response.duel_data == mock_duel_data
    assert response.submission_datetime == mock_submission_datetime


def test_response_model__call():
    mock_duel_data = MagicMock()
    mock_submission_datetime = MagicMock()
    response = EndDuelResponseModel(
        duel_data=mock_duel_data,
        submission_datetime=mock_submission_datetime)
    call_result = response()

    assert call_result == {
        'duel_id': mock_duel_data.entity_id,
        'duel_status': mock_duel_data.status.value,
        'submission_datetime': mock_submission_datetime.isoformat()
    }


def test_adapters():
    mock_duel_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_values_adapter = MagicMock()
    adapters = EndDuelAdapters(
        duel_adapter=mock_duel_adapter,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        values_adapter=mock_values_adapter)

    assert adapters.duel_adapter == mock_duel_adapter
    assert adapters.notification_adapter == mock_notification_adapter
    assert adapters.player_adapter == mock_player_adapter
    assert adapters.team_adapter == mock_team_adapter
    assert adapters.values_adapter == mock_values_adapter


Factory = namedtuple('Factory', 'interactor, mock_request, '
                                'mock_s3_bucket_name, mock_s3_bucket_url, '
                                'mock_adapters, mock_judge_matrix')


@fixture(scope='class')
def end_duel_interactor(request):
    def interactor_factory(request=MagicMock(),
                           s3_bucket_name=MagicMock(),
                           s3_bucket_url=MagicMock(),
                           adapters=MagicMock(),
                           judge_matrix=MagicMock()):
        interactor = EndDuelInteractor(
            request=request,
            s3_bucket_name=s3_bucket_name,
            s3_bucket_url=s3_bucket_url,
            adapters=adapters,
            judge_matrix=judge_matrix)

        return Factory(interactor, request, s3_bucket_name, s3_bucket_url,
                       adapters, judge_matrix)

    request.cls.factory = interactor_factory


@pytest.mark.usefixtures('end_duel_interactor')
class TestEndDuel(TestCase):
    def setUp(self):
        fac = TestEndDuel.factory()
        self.interactor: EndDuelInteractor = fac.interactor
        self.mock_request = fac.mock_request
        self.mock_s3_bucket_name = fac.mock_s3_bucket_name
        self.mock_s3_bucket_url = fac.mock_s3_bucket_url
        self.mock_adapters = fac.mock_adapters
        self.mock_judge_matrix = fac.mock_judge_matrix

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.s3_bucket_name == self.mock_s3_bucket_name
        assert self.interactor.s3_bucket_url == self.mock_s3_bucket_url
        assert self.interactor.adapters == self.mock_adapters
        assert self.interactor.judge_matrix == self.mock_judge_matrix

    def test__can_end(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(status=DuelStatus.DUELING)
        result = interactor._can_end()
        self.assertEqual(interactor.duel.status, DuelStatus.FINISHED_ONE_SIDE)
        interactor.duel.save.assert_called_once()
        self.assertFalse(result)
        interactor.duel = MagicMock(status=DuelStatus.FINISHED_ONE_SIDE)
        result = interactor._can_end()
        self.assertTrue(result)

    def test__can_end_exception(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(status=DuelStatus.FINISHED_BY_RESIGN)
        with raises(Exception) as excinfo:
            interactor._can_end()

        self.assertEqual(str(excinfo.value),
                         "Unable to end duel because it's on state FINISHED_BY_RESIGN")

    def test_duel_ready_to_finish(self):
        mock_duel = MagicMock()
        result = EndDuelInteractor.duel_ready_to_finish(mock_duel)
        self.assertTrue(result)

    def test_duel_ready_to_finish_false(self):
        chalengers = [None, True]
        chalengeds = [None, True]
        statuses = [DuelStatus.DUELING, DuelStatus.FINISHED_BY_RESIGN]
        all_combs = list(product(chalengers, chalengeds, statuses))
        all_combs.remove((True, True, DuelStatus.DUELING))

        for chalenger, chalenged, status in all_combs:
            mock_duel = MagicMock(challenger_duel_result=chalenger,
                                  challenged_duel_result=chalenged,
                                  status=status)
            result = EndDuelInteractor.duel_ready_to_finish(mock_duel)
            self.assertFalse(result)

    def test_get_coin_type_name_to_notification_gold(self):
        result = EndDuelInteractor.get_coin_type_name_to_notification(
            CoinType.GOLDEN_STAR)
        self.assertEqual(result, 'Stars Gold')

    def test_get_coin_type_name_to_notification_red(self):
        result = EndDuelInteractor.get_coin_type_name_to_notification(
            CoinType.RED_STAR)
        self.assertEqual(result, 'Stars Red')

    def test__get_adapter_player(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(member_type=DuelMemberType.PLAYER)
        result = interactor._get_adapter()
        self.assertEqual(result, self.mock_adapters.player_adapter)

    def test__get_adapter_team(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(member_type=DuelMemberType.TEAM)
        result = interactor._get_adapter()
        self.assertEqual(result, self.mock_adapters.team_adapter)

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_player_data(self, mock_entity_by_id):
        interactor: EndDuelInteractor = self.factory().interactor

        mock_player_id = MagicMock()
        result = interactor.get_player_data(mock_player_id)

        mock_entity_by_id.assert_called_with(
            _id=mock_player_id,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        self.assertEqual(result, mock_entity_by_id())

    @patch(f'{prefix}.isinstance', return_value=True)
    def test_get_member_player(self, mock_is_instance):
        interactor: EndDuelInteractor = self.factory().interactor
        mock_member_data = MagicMock()
        result = interactor.get_member_player(mock_member_data)
        self.assertEqual(result, mock_member_data)

    @patch.object(EndDuelInteractor, 'get_player_data')
    def test_get_member_player_not_player(self, mock_get_player_data):
        interactor: EndDuelInteractor = self.factory().interactor
        mock_member_data = MagicMock()
        result = interactor.get_member_player(mock_member_data)
        mock_get_player_data.assert_called_with(mock_member_data.captain.player_id)
        self.assertEqual(result, mock_get_player_data())

    @patch.object(EndDuelInteractor, '_get_adapter')
    def test_get_challenger(self, mock_get_adapter):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock()
        result = interactor.get_challenger()
        mock_get_adapter.assert_called_once()
        mock_get_adapter().get_by_id.assert_called_with(interactor.duel.challenger)
        self.assertEqual(result, mock_get_adapter().get_by_id())

    @patch.object(EndDuelInteractor, '_get_adapter')
    def test_get_challenged(self, mock_get_adapter):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock()
        result = interactor.get_challenged()
        mock_get_adapter.assert_called_once()
        mock_get_adapter().get_by_id.assert_called_with(interactor.duel.challenged)
        self.assertEqual(result, mock_get_adapter().get_by_id())

    @patch.object(EndDuelInteractor, 'judge_duel_player')
    def test_judge_duel_p(self, mock_judge_duel_player):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(member_type=DuelMemberType.PLAYER)
        interactor.judge_duel()
        mock_judge_duel_player.assert_called_once()

    @patch.object(EndDuelInteractor, 'judge_duel_team')
    def test_judge_duel_t(self, mock_judge_duel_team):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(member_type=DuelMemberType.TEAM)
        interactor.judge_duel()
        mock_judge_duel_team.assert_called_once()

    @patch(f'{prefix}.DuelSettlementTaskPlayer')
    def test_judge_duel_player(self, mock_duel_settlement_task_player):
        mock_duel = MagicMock()
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = mock_duel
        interactor.judge_duel_player()

        mock_duel_settlement_task_player.assert_called_with(
            duel=mock_duel,
            duel_adapter=self.mock_adapters.duel_adapter,
            notification_adapter=self.mock_adapters.notification_adapter,
            player_adapter=self.mock_adapters.player_adapter,
            values_adapter=self.mock_adapters.values_adapter,
            judge_matrix=self.mock_judge_matrix)

    @patch(f'{prefix}.DuelSettlementTaskTeam')
    def test_judge_duel_team(self, mock_duel_settlement_task_team):
        mock_duel = MagicMock()
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = mock_duel
        interactor.judge_duel_team()

        mock_duel_settlement_task_team.assert_called_with(
            duel=mock_duel,
            duel_adapter=self.mock_adapters.duel_adapter,
            notification_adapter=self.mock_adapters.notification_adapter,
            player_adapter=self.mock_adapters.player_adapter,
            team_adapter=self.mock_adapters.team_adapter,
            values_adapter=self.mock_adapters.values_adapter,
            judge_matrix=self.mock_judge_matrix)

    @patch.object(EndDuelInteractor, 'resignation_proceed')
    def test__check_resignation(self, mock_resignation_proceed):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock()
        interactor._check_resignation()
        mock_resignation_proceed.assert_not_called()

    @patch.object(EndDuelInteractor, 'resignation_proceed')
    def test__check_resignation_proceed(self, mock_resignation_proceed):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(
            challenged_duel_result=MagicMock(result=ComponentResult.RESIGNED))
        interactor._check_resignation()

        mock_resignation_proceed.assert_called_once()

    @patch.object(EndDuelInteractor, 'finish_duel_by_resignation')
    @patch.object(EndDuelInteractor, 'resignation_proceed_player')
    @patch.object(EndDuelInteractor, 'resignation_proceed_team')
    def test_resignation_proceed(self,
                                 mock_resignation_proceed_team,
                                 mock_resignation_proceed_player,
                                 mock_finish_duel_by_resignation):

        mock_challenger = MagicMock()
        mock_challenged = MagicMock()

        TestSample = namedtuple('TestSample', 'msww_return_value, member_type')
        member_types = [DuelMemberType.PLAYER, DuelMemberType.TEAM]
        selecteds = [
            (mock_challenger, mock_challenged),
            (mock_challenged, mock_challenger)
        ]
        pairs = product(selecteds, member_types)
        test_samples = [TestSample(x[0], x[1]) for x in pairs]

        for ts in test_samples:
            with patch.object(EndDuelInteractor, '_select_wo_winner') as msww:
                self._do_test_resignation_proceed(
                    mock_finish_duel_by_resignation,
                    mock_resignation_proceed_player, msww, ts)

    def _do_test_resignation_proceed(self,
                                     mock_finish_duel_by_resignation,
                                     mock_resignation_proceed_player,
                                     mock_select_wo_winner,
                                     ts):
        mock_select_wo_winner.return_value = ts.msww_return_value
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(member_type=ts.member_type)
        interactor.resignation_proceed()
        mock_select_wo_winner.assert_called_once()
        mock_resignation_proceed_player.assert_called_with(
            ts.msww_return_value[1], ts.msww_return_value[0])
        mock_finish_duel_by_resignation.assert_called_with(ts.msww_return_value[1])

    def test_has_challenger_result(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(challenger_duel_result=MagicMock())
        result = interactor._has_challenger_result()
        self.assertTrue(result)

    def test_has_challenger_result_false(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(challenger_duel_result=None)
        result = interactor._has_challenger_result()
        self.assertFalse(result)

    @patch.object(EndDuelInteractor, '_has_challenger_result', return_value=True)
    def test_do_challenger_resign(self, mock_has_challenger_result):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(
            challenger_duel_result=MagicMock(result=ComponentResult.RESIGNED))
        result = interactor._do_challenger_resigned()

        self.assertTrue(result)

    @patch.object(EndDuelInteractor, '_has_challenger_result', return_value=False)
    def test_do_challenger_resign_false(self, mock_has_challenger_result):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(challenger_duel_result=MagicMock(result=ComponentResult.RESIGNED))
        result = interactor._do_challenger_resigned()
        self.assertFalse(result)

    @patch.object(EndDuelInteractor, '_do_challenger_resigned', return_value=True)
    def test_select_wo_winner_challenger(self, mock_dcr):
        interactor: EndDuelInteractor = self.factory().interactor
        result = interactor._select_wo_winner()
        self.assertEqual(result, (interactor.challenger, interactor.challenged))

    @patch.object(EndDuelInteractor, '_do_challenger_resigned', return_value=False)
    def test_select_wo_winner_challenged(self, mock_dcr):
        interactor: EndDuelInteractor = self.factory().interactor
        result = interactor._select_wo_winner()
        self.assertEqual(result, (interactor.challenged, interactor.challenger))

    @patch.object(EndDuelInteractor, '_update_duel')
    @patch.object(EndDuelInteractor, '_make_victory_response')
    def test_finish_duel_by_resignation(self,
                                        mock_make_victory_response,
                                        mock_update_duel):
        mock_duel = MagicMock(challenger=MagicMock(), challenged=MagicMock())
        mock_duel_cases = [MagicMock(entity_id=mock_duel.challenger),
                           MagicMock(entity_id=mock_duel.challenged)]

        for mock_winner_data in mock_duel_cases:
            mock_update_duel.reset_mock()
            mock_make_victory_response.reset_mock()
            self._do_test_finish_duel_by_resignation(
                mock_make_victory_response,
                mock_update_duel,
                mock_duel,
                mock_winner_data)

    def _do_test_finish_duel_by_resignation(self,
                                            mock_make_victory_response,
                                            mock_update_duel,
                                            mock_duel,
                                            mock_winner_data):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = mock_duel

        interactor.finish_duel_by_resignation(mock_winner_data)

        mock_make_victory_response.assert_called_once()
        self.assertEqual(interactor.duel.challenger_duel_result,
                         mock_make_victory_response())
        self.assertEqual(interactor.duel.winner, mock_winner_data.entity_id)
        self.assertEqual(interactor.duel.status, DuelStatus.FINISHED_BY_RESIGN)
        self.assertEqual(interactor.duel.time_finish, interactor.submission_datetime)
        mock_update_duel.assert_called_once()

    def test_make_victory_response(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.submission_datetime = MagicMock()
        result = interactor._make_victory_response()

        expected = DuelComponentResult(
            result=ComponentResult.WINNER,
            submission_datetime=interactor.submission_datetime)

        self.assertEqual(result, expected)

    @patch.object(EndDuelInteractor, '_process_winner')
    @patch.object(EndDuelInteractor, '_set_winner_to_challenger_or_challenged')
    @patch.object(EndDuelInteractor, '_make_winner_notification_complement')
    @patch.object(EndDuelInteractor, '_notify_winner')
    @patch.object(EndDuelInteractor, '_notify_loser')
    def test_resignation_proceed_player(self,
                                        mock_notify_loser,
                                        mock_notify_winner,
                                        mock_make_win_not_comp,
                                        mock_set_winner_ger_or_ged,
                                        mock_process_winner):
        interactor: EndDuelInteractor = self.factory().interactor
        mock_winner_player = MagicMock()
        mock_loser_player = MagicMock()
        interactor.resignation_proceed_player(mock_winner_player, mock_loser_player)

        mock_process_winner.accert_called_with(mock_winner_player, mock_loser_player)
        mock_winner = mock_process_winner()
        mock_set_winner_ger_or_ged.assert_called_with(mock_winner)

        mock_make_win_not_comp.assert_called_once()
        mock_winner_comp = mock_make_win_not_comp()
        mock_notify_winner.assert_called_with(mock_winner_comp, mock_winner)
        mock_notify_loser.assert_called_with(mock_winner.user.nickname, mock_loser_player)

    @patch(f'{prefix}.create_notification')
    def test_notify_winner(self, mock_create_notification):
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        mock_complement = MagicMock()
        mock_winner_player = MagicMock()
        self.interactor._notify_winner(mock_complement, mock_winner_player)

        mock_create_notification.assert_called_with(
            player_data=mock_winner_player,
            notification_adapter=self.mock_adapters.notification_adapter,
            logger_instance=self.interactor.logger,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            duel_id=mock_duel.entity_id,
            notification_image=mock_duel.game.logo_path,
            notification_complement=mock_complement)

    @patch(f'{prefix}.create_notification')
    def test_notify_loser(self, mock_create_notification):
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        mock_loser_comp = MagicMock()
        mock_loser_player = MagicMock()
        self.interactor._notify_loser(mock_loser_comp, mock_loser_player)

        mock_create_notification.assert_called_with(
            player_data=mock_loser_player,
            notification_adapter=self.mock_adapters.notification_adapter,
            duel_id=mock_duel.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            notification_complement=mock_loser_comp,
            notification_image=mock_duel.game.logo_path,
            logger_instance=self.interactor.logger)

    @patch.object(EndDuelInteractor, 'get_coin_type_name_to_notification')
    def test_make_winner_notification_complement(self, mock_gctntn):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.duel = MagicMock(total_reward=42)
        result = interactor._make_winner_notification_complement()
        self.assertEqual(result, f'42 {mock_gctntn()}')

    def test_set_winner_to_challenger_or_challenged(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.challenger = MagicMock(entity_id=42)
        mock_winner_player = MagicMock(entity_id=42)
        interactor._set_winner_to_challenger_or_challenged(mock_winner_player)
        self.assertEqual(interactor.challenger, mock_winner_player)

    def test_set_winner_to_challenger_or_challenged_alt(self):
        interactor: EndDuelInteractor = self.factory().interactor
        interactor.challenger = MagicMock(entity_id=42)
        interactor.challenged = MagicMock(entity_id=17)
        mock_winner_player = MagicMock(entity_id=17)
        interactor._set_winner_to_challenger_or_challenged(mock_winner_player)
        self.assertEqual(interactor.challenged, mock_winner_player)

    @patch.object(EndDuelInteractor, 'pay_player')
    @patch(f'{prefix}.add_victory_on_game_on_player')
    @patch(f'{prefix}.update_elo_ratings')
    def test_process_winner(self, mock_update_elo, mock_add_victory, mock_pay_player):
        interactor: EndDuelInteractor = self.factory().interactor
        mock_loser_player = MagicMock()
        mock_winner_player = MagicMock()
        result = interactor._process_winner(mock_loser_player, mock_winner_player)

        mock_pay_player.assert_called_with(mock_winner_player)
        mock_add_victory.assert_called_with(player=mock_pay_player(), duel_data=interactor.duel)
        mock_add_victory().save.assert_called_once()
        mock_update_elo.assert_called_with(winner=mock_add_victory(), loser=mock_loser_player)

        self.assertEqual(result, mock_add_victory())

    @patch.object(EndDuelInteractor, '_process_winner_team')
    @patch.object(EndDuelInteractor, '_set_winner_to_challenger_or_challenged')
    @patch.object(EndDuelInteractor, '_make_winner_notification_complement')
    @patch.object(EndDuelInteractor, '_notify_winner_team')
    @patch.object(EndDuelInteractor, '_notify_loser_team')
    def test_resignation_proceed_team(self,
                                      mock_notify_loser_team,
                                      mock_notify_winner_team,
                                      mock_mwnc,
                                      mock_swtcoc,
                                      mock_process_winner_team):
        interactor: EndDuelInteractor = self.factory().interactor
        mock_winner_team = MagicMock()
        mock_loser_team = MagicMock()
        interactor.resignation_proceed_team(mock_winner_team, mock_loser_team)
        mock_process_winner_team.assert_called_with(mock_loser_team, mock_winner_team)
        mock_swtcoc.assert_called_with(mock_winner_team)
        mock_mwnc.assert_called_once()
        mock_notify_winner_team.assert_called_with(
            mock_winner_team,
            mock_mwnc(),
            mock_process_winner_team())
        mock_notify_loser_team.assert_called_with(mock_loser_team, mock_loser_team.name)

    @patch(f'{prefix}.create_notification')
    def test_notify_winner_team(self, mock_create_notification):
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        mock_complement = MagicMock()
        mock_winner_team = MagicMock()
        mock_winner_player = MagicMock()
        self.interactor._notify_winner_team(mock_winner_team, mock_complement, mock_winner_player)
        mock_create_notification.assert_called_with(
            player_data=mock_winner_player,
            notification_adapter=self.mock_adapters.notification_adapter,
            logger_instance=self.interactor.logger,
            notification_type=NotificationType.DUEL_FINISHED_WINNER,
            duel_id=mock_duel.entity_id,
            team_id=mock_winner_team.entity_id,
            notification_image=mock_duel.game.logo_path,
            notification_complement=mock_complement)

    @patch.object(EndDuelInteractor, 'get_member_player')
    @patch(f'{prefix}.create_notification')
    def test_notify_loser_team(self, mock_create_notification, mock_get_member_player):
        mock_loser_comp = MagicMock()
        mock_loser_team = MagicMock()
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        self.interactor._notify_loser_team(mock_loser_team, mock_loser_comp)

        mock_get_member_player.assert_called_with(mock_loser_team)
        mock_create_notification.assert_called_with(
            player_data=mock_get_member_player(),
            duel_id=mock_duel.entity_id,
            notification_type=NotificationType.DUEL_FINISHED_LOSER,
            notification_complement=mock_loser_comp,
            notification_adapter=self.mock_adapters.notification_adapter,
            logger_instance=self.interactor.logger,
            notification_image=mock_duel.game.logo_path)

    @patch(f'{prefix}.update_elo_ratings')
    @patch.object(EndDuelInteractor, 'pay_player')
    @patch.object(EndDuelInteractor, 'get_member_player')
    def test_process_winner_team(self,
                                 mock_get_member_player,
                                 mock_pay_player,
                                 mock_update_elo_ratings):
        interactor: EndDuelInteractor = self.factory().interactor
        mock_loser_team = MagicMock()
        mock_winner_team = MagicMock()
        result = interactor._process_winner_team(mock_loser_team, mock_winner_team)

        mock_get_member_player.assert_called_with(mock_winner_team)
        mock_pay_player.assert_called_with(mock_get_member_player())
        mock_pay_player().save.assert_called_once()
        mock_update_elo_ratings.assert_called_with(
            winner=mock_winner_team,
            loser=mock_loser_team)

        self.assertEqual(result, mock_get_member_player())

    @patch.object(EndDuelInteractor, 'pay_player')
    def test_pay_victory_team(self, mock_pay_player):
        mock_winner_team = MagicMock()
        result = self.interactor.pay_victory_team(mock_winner_team)

        self.mock_adapters.player_adapter.get_by_id.assert_called_with(
            mock_winner_team.captain.player_id)
        mock_player_data = self.mock_adapters.player_adapter.get_by_id()
        mock_player_data.set_adapter.assert_called_with(self.mock_adapters.player_adapter)
        mock_pay_player.assert_called_with(mock_player_data)
        mock_player_data = mock_pay_player()
        mock_player_data.save.assert_called_once()

        self.assertEqual(result, mock_player_data)

    @patch.object(EndDuelInteractor, 'pay_player_golden')
    def test_pay_player_goldcase(self, mock_pay_player_golden):
        self.interactor.duel = MagicMock(star_type=CoinType.GOLDEN_STAR)
        mock_player = MagicMock()
        self.interactor.pay_player(mock_player)
        mock_pay_player_golden.assert_called_with(mock_player)

    @patch.object(EndDuelInteractor, 'pay_player_red')
    def test_pay_player_redcase(self, mock_pay_player_red):
        self.interactor.duel = MagicMock(star_type=CoinType.RED_STAR)
        mock_player = MagicMock()
        self.interactor.pay_player(mock_player)
        mock_pay_player_red.assert_called_with(mock_player)

    def test_pay_player_golden(self):
        mock_player = MagicMock(golden_star_balance=17)
        self.interactor.duel = MagicMock(total_reward=13)
        result = self.interactor.pay_player_golden(mock_player)
        self.assertEqual(result.golden_star_balance, 30)

    def test_pay_player_red(self):
        mock_player = MagicMock(red_star_balance=17)
        self.interactor.duel = MagicMock(total_reward=13)
        result = self.interactor.pay_player_red(mock_player)
        self.assertEqual(result.red_star_balance, 30)

    @patch.object(EndDuelInteractor, 'judge_duel')
    def test__judge_duel(self, mock_jd):
        self.interactor._judge_duel()
        mock_jd.assert_called_once()

    @patch.object(EndDuelInteractor, 'judge_duel', side_effect=ValueError('Oops!'))
    def test__judge_duel_exception(self, mock_jd):
        with raises(JudgeException) as exc_info:
            self.interactor._judge_duel()
        self.assertEqual(str(exc_info.value), 'Error judging duel: ValueError(Oops!)')

    def test__update_duel(self):
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        self.interactor._update_duel()
        mock_duel.set_adapter.assert_called_with(self.mock_adapters.duel_adapter)
        mock_duel.save.assert_called_once()

    def test__update_duel_exception(self):
        mock_duel = MagicMock()
        mock_duel.set_adapter = MagicMock(side_effect=ValueError('Oops!'))
        self.interactor.duel = mock_duel
        with raises(UpdateDuelException) as exc_info:
            self.interactor._update_duel()
        self.assertEqual(str(exc_info.value), 'Error updating duel: ValueError(Oops!)')

    @patch.object(EndDuelInteractor, '_load_challenger')
    @patch.object(EndDuelInteractor, '_load_challenged')
    def test__load_members(self, m1, m2):
        self.interactor._load_members()
        m1.assert_called_once()
        m2.assert_called_once()

    @patch(f'{prefix}.setattr')
    @patch(f'{prefix}.getattr')
    @patch.object(EndDuelInteractor, '_get_adapter')
    def test__load_member(self, mock_get_adapter, mock_getattr, mock_setattr):
        mock_fnget = MagicMock()
        mock_target_field = MagicMock()
        self.interactor._load_member(mock_fnget, mock_target_field)
        mock_fnget.assert_called_once()
        mock_setattr.assert_called_with(self.interactor, mock_target_field, mock_fnget())
        mock_getattr.assert_called_with(self.interactor, mock_target_field)
        mock_get_adapter.assert_called_once()
        mock_getattr().set_adapter.assert_called_with(mock_get_adapter())

    @patch(f'{prefix}.setattr', side_effect=ValueError('Oops!'))
    def test__load_member_exception(self, mock_setattr):
        mock_fnget = MagicMock()
        mock_field = MagicMock()
        with raises(LoadMemberException) as exc_info:
            self.interactor._load_member(mock_fnget, mock_field)

        self.assertEqual(str(exc_info.value), f'Error loading {mock_field}: '
                                              f'ValueError(Oops!)')

    @patch.object(EndDuelInteractor, '_load_member')
    def test_load_challenged(self, mock_load_member):
        self.interactor._load_challenged()
        mock_load_member.assert_called_with(self.interactor.get_challenged, 'challenged')

    @patch.object(EndDuelInteractor, '_load_member')
    def test_load_challenger(self, mock_load_member):
        self.interactor._load_challenger()
        mock_load_member.assert_called_with(self.interactor.get_challenger, 'challenger')

    @patch(f'{prefix}.find_entity_by_id')
    def test__load_duel(self, mock_find_entity_by_id):
        self.interactor._load_duel()
        mock_find_entity_by_id.assert_called_with(
            _id=self.mock_request.duel_id,
            adapter_instance=self.mock_adapters.duel_adapter,
            class_name='Duel')
        mock_find_entity_by_id().set_adapter.assert_called_with(
            self.mock_adapters.duel_adapter)

    @patch(f'{prefix}.find_entity_by_id', side_effect=ValueError('Oops!'))
    def test__load_duel_except(self, mock_find_entity_by_id):
        with raises(LoadDuelException) as excinfo:
            self.interactor._load_duel()

        self.assertEqual(str(excinfo.value),
                         f'Error loading duel id: '
                         f'"{self.mock_request.duel_id}": '
                         f'ValueError(Oops!)')

    @patch.object(EndDuelInteractor, '_load_duel')
    @patch.object(EndDuelInteractor, '_can_end')
    @patch.object(EndDuelInteractor, '_load_members')
    @patch.object(EndDuelInteractor, '_check_resignation')
    @patch.object(EndDuelInteractor, 'duel_ready_to_finish')
    @patch.object(EndDuelInteractor, '_judge_duel')
    @patch(f'{prefix}.EndDuelResponseModel')
    def test_run(self,
                 mock_end_duel_response_model,
                 mock_judge_duel,
                 mock_duel_ready_to_finish,
                 mock_check_resignation,
                 mock_load_members,
                 mock_can_end,
                 mock_load_duel):
        result = self.interactor.run()

        mock_load_duel.assert_called_once()
        mock_can_end.assert_called_once()
        mock_load_members.assert_called_once()
        mock_check_resignation.assert_called_once()
        mock_duel_ready_to_finish.assert_called_once()
        mock_judge_duel.assert_called_once()
        mock_end_duel_response_model.assert_called_with(
            self.interactor.duel,
            self.interactor.submission_datetime)

        self.assertEqual(result, mock_end_duel_response_model())

    @patch.object(EndDuelInteractor, '_load_duel', side_effect=ValueError('Oops'))
    def test_run_exception(self, mock_load_duel):
        with raises(EndDuelException) as exc_info:
            self.interactor.run()
        self.assertEqual(str(exc_info.value),
                         f'Error during duel ending: '
                         f'{self.mock_request.duel_id} - '
                         f'ValueError(Oops)')
