from collections import namedtuple
from datetime import datetime
from playerstars_domain import (
    CoinType,
    DuelMemberType,
    DuelStatus,
    DuelType,
    NotificationType,
    Player,
    Team,
    User)
from playerstars_domain.duel.pre_duel import Status as PreDuelStatus
from playerstars_interactors.duel.put_preduel import (
    PutPreDuelAcceptException,
    PutPreDuelAdapters,
    PutPreDuelConfirmException,
    PutPreDuelException,
    PutPreDuelInteractor,
    PutPreDuelRequestModel,
    PutPreDuelResponseModel,
    PutPreDuelUnknowStatusException)
from pytest import fixture, raises
from unittest import TestCase
from unittest.mock import call, MagicMock, patch

import pytest


prefix = 'playerstars_interactors.duel.put_preduel'


def test_request_model():
    mock_json_data = MagicMock()
    request = PutPreDuelRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('player_id', 'player_id'),
              ('preduel_id', 'preduel_id'),
              ('status', 'status')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_response_model():
    mock_preduel_id = MagicMock()
    response = PutPreDuelResponseModel(mock_preduel_id)
    assert response.preduel_id == mock_preduel_id


def test_response_model__call():
    mock_preduel_id = MagicMock()
    response = PutPreDuelResponseModel(mock_preduel_id)
    response_call = response()
    assert response_call == mock_preduel_id


def test_adapters():
    mock_preduel_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_duel_adapter = MagicMock()
    mock_console_adapter = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_schedule_task_adapter = MagicMock()
    mock_era_adapter = MagicMock()
    mock_scheduler_adapter = MagicMock()
    adapters = PutPreDuelAdapters(
        preduel_adapter=mock_preduel_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        duel_adapter=mock_duel_adapter,
        console_adapter=mock_console_adapter,
        notification_adapter=mock_notification_adapter,
        schedule_task_adapter=mock_schedule_task_adapter,
        era_adapter=mock_era_adapter,
        scheduler_adapter=mock_scheduler_adapter)

    assert adapters.preduel_adapter == mock_preduel_adapter
    assert adapters.player_adapter == mock_player_adapter
    assert adapters.team_adapter == mock_team_adapter
    assert adapters.duel_adapter == mock_duel_adapter
    assert adapters.console_adapter == mock_console_adapter
    assert adapters.notification_adapter == mock_notification_adapter
    assert adapters.schedule_task_adapter == mock_schedule_task_adapter
    assert adapters.era_adapter == mock_era_adapter
    assert adapters.scheduler_adapter == mock_scheduler_adapter


Factory = namedtuple('Factory', 'interactor, mock_request, mock_adapters, '
                                'mock_time_to_finish, '
                                'mock_era_finish_duel_url')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(request: PutPreDuelRequestModel = MagicMock(),
                adapters: PutPreDuelAdapters = MagicMock(),
                time_to_finish: int = MagicMock(),
                era_finish_duel_url: str = MagicMock()):
        interactor = PutPreDuelInteractor(
            request=request,
            adapters=adapters,
            time_to_finish=time_to_finish,
            era_finish_duel_url=era_finish_duel_url)
        return Factory(interactor, request, adapters,
                       time_to_finish, era_finish_duel_url)
    request.cls.factory = factory


def make_preduel_accepted_2():
    mock_preduel = MagicMock()
    mock_preduel.status = PreDuelStatus.ACCEPTED_2
    return mock_preduel


def make_preduel_golden_star():
    mock_preduel = MagicMock()
    mock_preduel.status = PreDuelStatus.ACCEPTED_2
    mock_preduel.star_type = CoinType.GOLDEN_STAR
    return mock_preduel


def make_team(mock_captain_id):
    mock_team = MagicMock()
    mock_team.captain.player_id = mock_captain_id
    return mock_team


@pytest.mark.usefixtures('interactor_fixture')
class TestPutPreDuelInteractor(TestCase):
    def setUp(self):
        fac = TestPutPreDuelInteractor.factory()
        self.interactor: PutPreDuelInteractor = fac.interactor
        self.mock_request = fac.mock_request
        self.mock_adapters = fac.mock_adapters
        self.mock_time_to_finish = fac.mock_time_to_finish
        self.mock_era_finish_duel_url = fac.mock_era_finish_duel_url

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.adapters == self.mock_adapters
        assert self.interactor.time_to_finish == self.mock_time_to_finish
        assert self.interactor.era_finish_duel_url == \
            self.mock_era_finish_duel_url

    @patch.object(PutPreDuelInteractor, 'get_duel_member_player')
    @patch.object(PutPreDuelInteractor, 'get_duel_member_team')
    def test__get_duel_member__as_player(
            self, mock_get_duel_member_team, mock_get_duel_member_player):
        mock_duel_member_id = MagicMock()
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.PLAYER
        self.interactor.duel = mock_duel
        duel_member = self.interactor._get_duel_member(mock_duel_member_id)

        mock_get_duel_member_team.assert_not_called()
        mock_get_duel_member_player.assert_called_with(mock_duel_member_id)
        assert duel_member == mock_get_duel_member_player()

    @patch.object(PutPreDuelInteractor, 'get_duel_member_player')
    @patch.object(PutPreDuelInteractor, 'get_duel_member_team')
    def test__get_duel_member__as_team(
            self, mock_get_duel_member_team, mock_get_duel_member_player):
        mock_duel_member_id = MagicMock()
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.TEAM
        self.interactor.duel = mock_duel
        duel_member = self.interactor._get_duel_member(mock_duel_member_id)

        mock_get_duel_member_team.assert_called_with(mock_duel_member_id)
        mock_get_duel_member_player.assert_not_called()
        assert duel_member == mock_get_duel_member_team()

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_duel_member_player(self, mock_find_entity_by_id):
        mock_member_id = MagicMock()
        member = self.interactor.get_duel_member_player(mock_member_id)
        mock_find_entity_by_id.assert_called_with(
            _id=mock_member_id,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        assert member == mock_find_entity_by_id()

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_duel_member_team(self, mock_find_entity_by_id):
        mock_member_id = MagicMock()
        member = self.interactor.get_duel_member_team(mock_member_id)
        mock_find_entity_by_id.assert_called_with(
            _id=mock_member_id,
            adapter_instance=self.mock_adapters.team_adapter,
            class_name='Team')
        assert member == mock_find_entity_by_id()

    def test_check_participants__player(self):
        mock_pre_duel = MagicMock()
        mock_pre_duel.duel_type = DuelMemberType.PLAYER
        mock_pre_duel.challenger = '1'
        mock_pre_duel.challenged = '2'
        self.mock_request.player_id = '1'
        check_result = self.interactor.check_participants(mock_pre_duel)

        self.mock_adapters.team_adapter.get_by_id.assert_not_called()
        assert check_result is True

    def test_check_participants__team(self):
        mock_pre_duel = MagicMock()
        mock_pre_duel.duel_type = DuelMemberType.TEAM
        mock_pre_duel.challenger = '1'
        mock_team = MagicMock()
        mock_team.captain.player_id = '1'
        self.mock_adapters.team_adapter.get_by_id = \
            MagicMock(return_value=mock_team)
        self.mock_request.player_id = '1'
        check_result = self.interactor.check_participants(mock_pre_duel)

        assert self.mock_adapters.team_adapter.get_by_id.call_count == 2
        assert check_result is True

    def test_check_participants__player_id_not_in_participants(self):
        mock_pre_duel = MagicMock()
        mock_pre_duel.duel_type = DuelMemberType.PLAYER
        mock_pre_duel.challenger = '1'
        mock_pre_duel.challenged = '2'
        self.mock_request.player_id = '3'
        with raises(PutPreDuelException) as exc:
            self.interactor.check_participants(mock_pre_duel)
        assert 'Player 3 is not a participant in this preduel' \
            in str(exc.value)

    @patch.object(PutPreDuelInteractor, 'warn_other_participant')
    def test_confirm__status_confirm(self, mock_warn_other_participant):
        mock_pre_duel = MagicMock()
        mock_pre_duel.status = PreDuelStatus.CONFIRM
        result = self.interactor.confirm(mock_pre_duel)

        assert result.status == PreDuelStatus.CONFIRMED_1
        assert result.ack is False
        mock_warn_other_participant.assert_called_with(mock_pre_duel)
        assert result == mock_pre_duel

    @patch.object(PutPreDuelInteractor, 'warn_other_participant')
    def test_confirm__status_confirmed_1(self, mock_warn_other_participant):
        mock_pre_duel = MagicMock()
        mock_pre_duel.status = PreDuelStatus.CONFIRMED_1
        result = self.interactor.confirm(mock_pre_duel)

        assert result.status == PreDuelStatus.CONFIRMED_2
        mock_warn_other_participant.assert_called_with(mock_pre_duel)
        assert result == mock_pre_duel

    @patch.object(PutPreDuelInteractor, 'warn_other_participant')
    def test_confirm__raises(self, mock_warn_other_participant):
        mock_pre_duel = MagicMock()
        mock_pre_duel.status = PreDuelStatus.AWAITING
        with raises(PutPreDuelConfirmException) as exc:
            self.interactor.confirm(mock_pre_duel)
        assert 'Trying to confirm a preduel that has ' \
            'Status.AWAITING status is not possible' in str(exc.value)
        mock_warn_other_participant.assert_not_called()

    @patch.object(PutPreDuelInteractor, 'warn_other_participant')
    def test_accept__status_confirmed_2(self, mock_warn_other_participant):
        mock_pre_duel = MagicMock()
        mock_pre_duel.status = PreDuelStatus.CONFIRMED_2
        result = self.interactor.accept(mock_pre_duel)

        assert result.status == PreDuelStatus.ACCEPTED_1
        assert result.ack is False
        mock_warn_other_participant.assert_called_with(mock_pre_duel)
        assert result == mock_pre_duel

    @patch.object(PutPreDuelInteractor, 'warn_other_participant')
    def test_accept__status_accepted_1(self, mock_warn_other_participant):
        mock_pre_duel = MagicMock()
        mock_pre_duel.status = PreDuelStatus.ACCEPTED_1
        result = self.interactor.accept(mock_pre_duel)

        assert result.status == PreDuelStatus.ACCEPTED_2
        mock_warn_other_participant.assert_called_with(mock_pre_duel)
        assert result == mock_pre_duel

    @patch.object(PutPreDuelInteractor, 'warn_other_participant')
    def test_accept__raises(self, mock_warn_other_participant):
        mock_pre_duel = MagicMock()
        mock_pre_duel.status = PreDuelStatus.AWAITING
        with raises(PutPreDuelAcceptException) as exc:
            self.interactor.accept(mock_pre_duel)
        assert f'Trying to accept a preduel that has Status.AWAITING ' \
            f'status is not possible' in str(exc.value)

    @patch.object(PutPreDuelInteractor, 'warn_other_participant')
    def test_ack_true(self, mock_warn_other_participant):
        mock_pre_duel = MagicMock()
        result = self.interactor.ack_true(mock_pre_duel)
        assert result.ack is True
        mock_warn_other_participant.assert_called_with(mock_pre_duel)

    @patch(f'{prefix}.send_message')
    @patch.object(PutPreDuelInteractor,
                  'get_participant_to_warn',
                  return_value='a')
    def test_warn_other_participant(self, mock_get_participant_to_warn,
                                    mock_send_message):
        mock_pre_duel = MagicMock()
        mock_pre_duel.entity_id = '1'
        mock_pre_duel.status = PreDuelStatus.ACCEPTED_1.value
        self.interactor.warn_other_participant(mock_pre_duel)
        mock_get_participant_to_warn.assert_called_with(mock_pre_duel)
        mock_send_message.assert_called_with(
            msg=f'a do duel 1 marcou o duelo como ACCEPTED_1',
            queue_name=mock_get_participant_to_warn())

    @patch.object(PutPreDuelInteractor, 'get_other_captain_id')
    def test_get_participant_to_warn__player_challenger(
            self, mock_get_other_captain_id):
        mock_challenged = MagicMock()
        self.mock_request.player_id = mock_challenged
        mock_pre_duel = MagicMock()
        mock_pre_duel.duel_type = DuelMemberType.PLAYER
        mock_pre_duel.challenged = mock_challenged
        result = self.interactor.get_participant_to_warn(mock_pre_duel)

        mock_get_other_captain_id.assert_not_called()
        assert result == mock_pre_duel.challenger

    @patch.object(PutPreDuelInteractor, 'get_other_captain_id')
    def test_get_participant_to_warn__player_challenged(
            self, mock_get_other_captain_id):
        mock_challenger = MagicMock()
        self.mock_request.player_id = mock_challenger
        mock_pre_duel = MagicMock()
        mock_pre_duel.duel_type = DuelMemberType.PLAYER
        mock_pre_duel.challenger = mock_challenger
        result = self.interactor.get_participant_to_warn(mock_pre_duel)

        mock_get_other_captain_id.assert_not_called()
        assert result == mock_pre_duel.challenged

    @patch.object(PutPreDuelInteractor, 'get_other_captain_id')
    def test_get_participant_to_warn__team(
            self, mock_get_other_captain_id):
        mock_pre_duel = MagicMock()
        mock_pre_duel.duel_type = DuelMemberType.TEAM
        result = self.interactor.get_participant_to_warn(mock_pre_duel)

        mock_get_other_captain_id.assert_called_with(mock_pre_duel)
        assert result == mock_get_other_captain_id()

    @patch.object(PutPreDuelInteractor, 'warn_refuse')
    def test_refuse(self, mock_warn_refuse):
        mock_pre_duel = MagicMock()
        mock_pre_duel.challenged = None
        result = self.interactor.refuse(mock_pre_duel)

        mock_warn_refuse.assert_not_called()
        assert result.status == PreDuelStatus.REFUSED
        assert result == mock_pre_duel

    @patch.object(PutPreDuelInteractor, 'warn_refuse')
    def test_refuse__warn(self, mock_warn_refuse):
        mock_pre_duel = MagicMock()
        result = self.interactor.refuse(mock_pre_duel)
        mock_warn_refuse.assert_called_with(mock_pre_duel)
        assert result.status == PreDuelStatus.REFUSED
        assert result == mock_pre_duel

    @patch(f'{prefix}.send_message')
    @patch.object(PutPreDuelInteractor,
                  'get_participant_to_warn',
                  return_value='a')
    def test_warn_refuse(self, mock_get_participant_to_warn,
                         mock_send_message):
        mock_pre_duel = MagicMock()
        mock_pre_duel.entity_id = '1'
        self.interactor.warn_refuse(mock_pre_duel)
        mock_get_participant_to_warn.assert_called_with(mock_pre_duel)
        mock_send_message.assert_called_with(
            msg=f'a recusou o duel 1',
            queue_name=mock_get_participant_to_warn())

    @patch(f'{prefix}.Callable')
    @patch.object(PutPreDuelInteractor, 'confirm')
    @patch.object(PutPreDuelInteractor, 'accept')
    @patch.object(PutPreDuelInteractor, 'ack_true')
    @patch.object(PutPreDuelInteractor, 'refuse')
    def test_resolve_status_confirm(self, mock_refuse,
                                    mock_ack_true,
                                    mock_accept,
                                    mock_confirm,
                                    mock_callable):
        self.mock_request.status = 'confirm'
        mock_pre_duel = MagicMock()
        result = self.interactor.resolve_status(mock_pre_duel)

        mock_confirm.assert_called_with(mock_pre_duel)
        mock_accept.assert_not_called()
        mock_ack_true.assert_not_called()
        mock_refuse.assert_not_called()
        assert result == mock_confirm()

    @patch(f'{prefix}.Callable')
    @patch.object(PutPreDuelInteractor, 'confirm')
    @patch.object(PutPreDuelInteractor, 'accept')
    @patch.object(PutPreDuelInteractor, 'ack_true')
    @patch.object(PutPreDuelInteractor, 'refuse')
    def test_resolve_status_accepted(self, mock_refuse,
                                     mock_ack_true,
                                     mock_accept,
                                     mock_confirm,
                                     mock_callable):
        self.mock_request.status = 'accepted'
        mock_pre_duel = MagicMock()
        result = self.interactor.resolve_status(mock_pre_duel)

        mock_confirm.assert_not_called()
        mock_accept.assert_called_with(mock_pre_duel)
        mock_ack_true.assert_not_called()
        mock_refuse.assert_not_called()
        assert result == mock_accept()

    @patch(f'{prefix}.Callable')
    @patch.object(PutPreDuelInteractor, 'confirm')
    @patch.object(PutPreDuelInteractor, 'accept')
    @patch.object(PutPreDuelInteractor, 'ack_true')
    @patch.object(PutPreDuelInteractor, 'refuse')
    def test_resolve_status_ack(self, mock_refuse,
                                mock_ack_true,
                                mock_accept,
                                mock_confirm,
                                mock_callable):
        self.mock_request.status = 'ack'
        mock_pre_duel = MagicMock()
        result = self.interactor.resolve_status(mock_pre_duel)

        mock_confirm.assert_not_called()
        mock_accept.assert_not_called()
        mock_ack_true.assert_called_with(mock_pre_duel)
        mock_refuse.assert_not_called()
        assert result == mock_ack_true()

    @patch(f'{prefix}.Callable')
    @patch.object(PutPreDuelInteractor, 'confirm')
    @patch.object(PutPreDuelInteractor, 'accept')
    @patch.object(PutPreDuelInteractor, 'ack_true')
    @patch.object(PutPreDuelInteractor, 'refuse')
    def test_resolve_status_refuse(self, mock_refuse,
                                   mock_ack_true,
                                   mock_accept,
                                   mock_confirm,
                                   mock_callable):
        self.mock_request.status = 'refuse'
        mock_pre_duel = MagicMock()
        result = self.interactor.resolve_status(mock_pre_duel)

        mock_confirm.assert_not_called()
        mock_accept.assert_not_called()
        mock_ack_true.assert_not_called()
        mock_refuse.assert_called_with(mock_pre_duel)
        assert result == mock_refuse()

    @patch(f'{prefix}.Callable')
    @patch.object(PutPreDuelInteractor, 'confirm')
    @patch.object(PutPreDuelInteractor, 'accept')
    @patch.object(PutPreDuelInteractor, 'ack_true')
    @patch.object(PutPreDuelInteractor, 'refuse')
    def test_resolve_status_error(self, mock_refuse,
                                  mock_ack_true,
                                  mock_accept,
                                  mock_confirm,
                                  mock_callable):
        self.mock_request.status = 'other'
        mock_pre_duel = MagicMock()
        with raises(PutPreDuelUnknowStatusException) as exc:
            self.interactor.resolve_status(mock_pre_duel)
        assert 'Status de atualização de preduel inválido' in str(exc.value)
        mock_confirm.assert_not_called()
        mock_accept.assert_not_called()
        mock_ack_true.assert_not_called()
        mock_refuse.assert_not_called()

    def test_get_console(self):
        mock_console_id = MagicMock()
        console_data = self.interactor.get_console(mock_console_id)
        self.mock_adapters.console_adapter.get_by_id.assert_called_with(
            mock_console_id)
        assert console_data == self.mock_adapters.console_adapter.get_by_id()

    def test_get_game(self):
        mock_console = MagicMock()
        mock_game_id = MagicMock()
        game_data = self.interactor.get_game(
            console=mock_console,
            game_id=mock_game_id)

        mock_console.find_game_by_id.assert_called_with(mock_game_id)
        assert game_data.tutorial is None
        assert game_data == mock_console.find_game_by_id()

    def test__prepare_console_to_duel(self):
        mock_console = MagicMock()
        console_data = self.interactor._prepare_console_to_duel(mock_console)
        assert console_data.games == []

    @patch(f'{prefix}.aware_now')
    @patch(f'{prefix}.Duel')
    @patch.object(PutPreDuelInteractor, 'get_console')
    @patch.object(PutPreDuelInteractor, 'get_game')
    @patch.object(PutPreDuelInteractor, '_prepare_console_to_duel')
    def test_create_duel(self, mock_prepare_console_to_duel,
                         mock_get_game,
                         mock_get_console,
                         mock_duel,
                         mock_aware_now):
        mock_preduel = MagicMock()
        duel = self.interactor.create_duel(mock_preduel)

        mock_get_console.assert_called_with(mock_preduel.console_entity_id)
        mock_get_game.assert_called_with(
            console=mock_get_console(),
            game_id=mock_preduel.game_entity_id)
        mock_aware_now.assert_called()
        mock_prepare_console_to_duel.assert_called_with(mock_get_console())
        mock_duel.assert_called_with(
            challenger=mock_preduel.challenger,
            challenged=mock_preduel.challenged,
            game=mock_get_game(),
            console=mock_prepare_console_to_duel(),
            star_type=mock_preduel.star_type,
            bet_size=mock_preduel.star_amount,
            member_type=mock_preduel.duel_type,
            duel_type=DuelType.INDIVIDUAL,
            participants=2,
            challenger_confirmation=True,
            challenged_confirmation=True,
            challenged_accept=True,
            creation_datetime=mock_aware_now(),
            time_start=mock_aware_now(),
            time_to_finish_duel=self.interactor.time_to_finish,
            time_to_accept_invitation=1,
            status=DuelStatus.DUELING)
        assert duel == mock_duel()

    def test_get_player_balance__golden_star(self):
        mock_player = MagicMock()
        mock_star_type = CoinType.GOLDEN_STAR
        balance = self.interactor.get_player_balance(
            mock_player, mock_star_type)
        assert balance == mock_player.golden_star_balance

    def test_get_player_balance__red_star(self):
        mock_player = MagicMock()
        mock_star_type = CoinType.RED_STAR
        balance = self.interactor.get_player_balance(
            mock_player, mock_star_type)
        assert balance == mock_player.red_star_balance

    def test_set_player_balance__golden_star(self):
        mock_player = MagicMock()
        mock_star_balance = CoinType.GOLDEN_STAR
        mock_new_balance = MagicMock()
        mock_golden_balance = MagicMock()
        mock_player.golden_star_balance = mock_golden_balance
        mock_red_balance = MagicMock()
        mock_player.red_star_balance = mock_red_balance
        updated_player = self.interactor.set_player_balance(
            mock_player, mock_star_balance, mock_new_balance)

        assert updated_player == mock_player
        assert updated_player.golden_star_balance == mock_new_balance
        assert updated_player.red_star_balance == mock_red_balance

    def test_set_player_balance__red_star(self):
        mock_player = MagicMock()
        mock_star_balance = CoinType.RED_STAR
        mock_new_balance = MagicMock()
        mock_golden_balance = MagicMock()
        mock_player.golden_star_balance = mock_golden_balance
        mock_red_balance = MagicMock()
        mock_player.red_star_balance = mock_red_balance
        updated_player = self.interactor.set_player_balance(
            mock_player, mock_star_balance, mock_new_balance)

        assert updated_player == mock_player
        assert updated_player.golden_star_balance == mock_golden_balance
        assert updated_player.red_star_balance == mock_new_balance

    @patch.object(PutPreDuelInteractor,
                  'get_player_balance',
                  return_value=30)
    @patch.object(PutPreDuelInteractor, 'set_player_balance')
    def test_pay_player(self, mock_set_player_balance,
                        mock_get_player_balance):
        mock_bet_size = 5
        mock_entity_id = MagicMock()
        mock_star_type = MagicMock()
        self.interactor.pay_player(
            entity_id=mock_entity_id,
            bet_size=mock_bet_size,
            star_type=mock_star_type)

        self.mock_adapters.player_adapter.get_by_id.assert_called_with(
            mock_entity_id)
        mock_get_player_balance.assert_called_with(
            self.mock_adapters.player_adapter.get_by_id(), mock_star_type)
        mock_set_player_balance.assert_called_with(
            player=self.mock_adapters.player_adapter.get_by_id(),
            star_type=mock_star_type,
            new_balance=mock_get_player_balance() - mock_bet_size)
        mock_set_player_balance().set_adapter.assert_called_with(
            self.mock_adapters.player_adapter)
        mock_set_player_balance().save.assert_called()

    @patch.object(PutPreDuelInteractor,
                  'get_player_balance',
                  return_value=5)
    @patch.object(PutPreDuelInteractor, 'set_player_balance')
    def test_pay_player_error(self, mock_set_player_balance,
                              mock_get_player_balance):
        mock_bet_size = 10
        mock_entity_id = MagicMock()
        mock_star_type = MagicMock()

        mock_player = MagicMock()
        mock_player.entity_id = 'a'
        self.mock_adapters.player_adapter.get_by_id = \
            MagicMock(return_value=mock_player)
        with raises(ValueError) as exc:
            self.interactor.pay_player(
                entity_id=mock_entity_id,
                bet_size=mock_bet_size,
                star_type=mock_star_type)

        assert "Player a doesn't have enough stars" in str(exc.value)

    @patch.object(PutPreDuelInteractor, 'pay_player')
    def test_pay_team(self, mock_pay_player):
        mock_entity_id = MagicMock()
        mock_bet_size = MagicMock()
        mock_star_type = MagicMock()
        self.interactor.pay_team(
            entity_id=mock_entity_id,
            bet_size=mock_bet_size,
            star_type=mock_star_type)

        self.mock_adapters.team_adapter.get_by_id.assert_called_with(
            mock_entity_id)
        self.mock_adapters.player_adapter.get_by_id.assert_called_with(
            self.mock_adapters.team_adapter.get_by_id().captain.player_id)
        mock_pay_player.assert_called_with(
            entity_id=self.mock_adapters.player_adapter.get_by_id().entity_id,
            bet_size=mock_bet_size,
            star_type=mock_star_type)

    @patch(f'{prefix}.Callable')
    @patch.object(PutPreDuelInteractor, 'pay_player')
    @patch.object(PutPreDuelInteractor, 'pay_team')
    def test_pay_duel__player(self, mock_pay_team,
                              mock_pay_player,
                              mock_callable):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.PLAYER
        self.interactor.pay_duel(mock_duel)
        assert mock_pay_player.call_count == 2
        mock_pay_team.assert_not_called()

    @patch(f'{prefix}.Callable')
    @patch.object(PutPreDuelInteractor, 'pay_player')
    @patch.object(PutPreDuelInteractor, 'pay_team')
    def test_pay_duel__team(self, mock_pay_team,
                            mock_pay_player,
                            mock_callable):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.TEAM
        self.interactor.pay_duel(mock_duel)
        assert mock_pay_team.call_count == 2
        mock_pay_player.assert_not_called()

    @patch(f'{prefix}.aware_now',
           return_value=datetime(2020, 12, 1, 0, 0, 0))
    def test_calculate_finish_datetime(self, mock_aware_now):
        self.interactor.time_to_finish = 15
        result = self.interactor.calculate_finish_datetime()
        mock_aware_now.assert_called()
        assert result == datetime(2020, 12, 1, 0, 15, 0)

    @patch(f'{prefix}.create_era')
    @patch.object(PutPreDuelInteractor, 'calculate_finish_datetime')
    def test_create_finish_task(self, mock_calculate_finish_datetime,
                                mock_create_era):
        mock_era_url = MagicMock()
        self.interactor.era_finish_duel_url = mock_era_url
        mock_duel_id = MagicMock()
        self.interactor.create_finish_task(mock_duel_id)
        mock_calculate_finish_datetime.assert_called()
        mock_create_era.assert_called_with(
            duel_id=mock_duel_id,
            event_time=mock_calculate_finish_datetime(),
            era_finish_duel_url=mock_era_url,
            persist_adapter=self.mock_adapters.era_adapter,
            scheduler_adapter=self.mock_adapters.scheduler_adapter)

    def test_update_preduel(self):
        mock_preduel = MagicMock()
        self.interactor.update_preduel(mock_preduel)
        mock_preduel.set_adapter.assert_called_with(
            self.mock_adapters.preduel_adapter)
        mock_preduel.save.assert_called()

    def test_update_duel(self):
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        self.interactor.update_duel()

        mock_duel.set_adapter.assert_called_with(
            self.mock_adapters.duel_adapter)
        mock_duel.save.assert_called()

    @patch.object(PutPreDuelInteractor, 'get_duel_member_player')
    def test__get_member_player__player(self, mock_get_duel_member_player):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.PLAYER
        self.interactor.duel = mock_duel
        mock_member_data = MagicMock()
        member = self.interactor._get_member_player(mock_member_data)
        mock_get_duel_member_player.assert_not_called()
        assert member == mock_member_data

    @patch.object(PutPreDuelInteractor, 'get_duel_member_player')
    def test__get_member_player__team(self, mock_get_duel_member_player):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.TEAM
        self.interactor.duel = mock_duel
        mock_member_data = MagicMock()
        member = self.interactor._get_member_player(mock_member_data)

        mock_get_duel_member_player.assert_called_with(
            mock_member_data.captain.player_id)
        assert member == mock_get_duel_member_player()

    def test__get_team_id__player(self):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.PLAYER
        self.interactor.duel = mock_duel
        mock_member_data = MagicMock()
        team_id = self.interactor._get_team_id(mock_member_data)
        assert team_id is None

    def test__get_team_id__team(self):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.TEAM
        self.interactor.duel = mock_duel
        mock_member_data = MagicMock()
        team_id = self.interactor._get_team_id(mock_member_data)
        assert team_id == mock_member_data.entity_id

    def test__get_member_name__player(self):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.PLAYER
        self.interactor.duel = mock_duel
        mock_member_data = Player(
            user=User(
                name='Anselmo',
                email='anselmo.lira@stormgroup.com.br',
                nickname='anselmo.lira',
                street=MagicMock(),
                street_number=MagicMock(),
                street_complement=MagicMock(),
                neighborhood=MagicMock(),
                city=MagicMock(),
                state=MagicMock(),
                country=MagicMock(),
                postal_code=MagicMock(),
                cpf=MagicMock(),
                date_birth=MagicMock(),
                phone_number=MagicMock()))
        member_name = self.interactor._get_member_name(mock_member_data)
        assert member_name == mock_member_data.user.nickname

    def test__get_member_name__team(self):
        mock_duel = MagicMock()
        mock_duel.member_type = DuelMemberType.TEAM
        self.interactor.duel = mock_duel
        mock_member_data = Team(
            name='Cariocas',
            captain=MagicMock())
        member_name = self.interactor._get_member_name(mock_member_data)
        assert member_name == mock_member_data.name

    @patch.object(PutPreDuelInteractor, '_get_duel_member')
    @patch.object(PutPreDuelInteractor, 'notify_member')
    def test_notify_members(self, mock_notify_member, mock_get_duel_member):
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        self.interactor.notify_members()

        get_duel_member_calls = [call(mock_duel.challenger),
                                 call(mock_duel.challenged)]
        mock_get_duel_member.assert_has_calls(get_duel_member_calls)
        mock_notify_member.assert_called()

    @patch(f'{prefix}.create_notification')
    @patch.object(PutPreDuelInteractor, '_get_member_player')
    @patch.object(PutPreDuelInteractor, '_get_member_name')
    @patch.object(PutPreDuelInteractor, '_get_team_id')
    def test_notify_member(self, mock_get_team_id,
                           mock_get_member_name,
                           mock_get_member_player,
                           mock_create_notification):
        mock_member_1 = MagicMock()
        mock_member_2 = MagicMock()
        mock_duel = MagicMock()
        self.interactor.duel = mock_duel
        self.interactor.notify_member(mock_member_1, mock_member_2)

        mock_get_member_player.assert_called_with(mock_member_1)
        mock_get_member_name.assert_called_with(mock_member_2)
        mock_get_team_id.assert_called_with(mock_member_1)
        mock_create_notification.assert_called_with(
            player_data=mock_get_member_player(),
            notification_adapter=self.mock_adapters.notification_adapter,
            notification_type=NotificationType.DUEL_ONGOING,
            notification_complement=mock_get_member_name(),
            duel_id=mock_duel.entity_id,
            team_id=mock_get_team_id(),
            notification_image=mock_duel.game.logo_path,
            logger_instance=self.interactor.logger)

    @patch(f'{prefix}.PutPreDuelResponseModel')
    @patch.object(PutPreDuelInteractor, '_get_preduel')
    @patch.object(PutPreDuelInteractor, 'check_participants')
    @patch.object(PutPreDuelInteractor,
                  'resolve_status',
                  return_value=make_preduel_accepted_2())
    @patch.object(PutPreDuelInteractor, 'update_preduel')
    @patch.object(PutPreDuelInteractor, 'create_duel')
    @patch.object(PutPreDuelInteractor, 'pay_duel')
    @patch.object(PutPreDuelInteractor, 'create_finish_task')
    @patch.object(PutPreDuelInteractor, 'update_duel')
    @patch.object(PutPreDuelInteractor, 'notify_members')
    def test_run(self, mock_notify_members,
                 mock_update_duel,
                 mock_create_finish_task,
                 mock_pay_duel,
                 mock_create_duel,
                 mock_update_preduel,
                 mock_resolve_status,
                 mock_check_participants,
                 mock_get_preduel,
                 mock_response_model):
        response = self.interactor.run()
        mock_get_preduel.assert_called()
        mock_check_participants.assert_called_with(mock_get_preduel())
        mock_resolve_status.assert_called_with(mock_get_preduel())
        mock_update_preduel.assert_called()
        mock_create_duel.assert_called_with(mock_resolve_status())
        mock_pay_duel.assert_not_called()
        mock_create_finish_task.assert_called_with(
            mock_create_duel().entity_id)
        mock_update_duel.assert_called()
        mock_notify_members.assert_called()
        mock_response_model.assert_called_with(mock_create_duel().entity_id)
        assert response == mock_response_model()

    @patch(f'{prefix}.PutPreDuelResponseModel')
    @patch.object(PutPreDuelInteractor, '_get_preduel')
    @patch.object(PutPreDuelInteractor, 'check_participants')
    @patch.object(PutPreDuelInteractor, 'resolve_status')
    @patch.object(PutPreDuelInteractor, 'update_preduel')
    @patch.object(PutPreDuelInteractor, 'create_duel')
    @patch.object(PutPreDuelInteractor, 'pay_duel')
    @patch.object(PutPreDuelInteractor, 'create_finish_task')
    @patch.object(PutPreDuelInteractor, 'update_duel')
    @patch.object(PutPreDuelInteractor, 'notify_members')
    def test_run__status_not_accepted_2(self, mock_notify_members,
                                        mock_update_duel,
                                        mock_create_finish_task,
                                        mock_pay_duel,
                                        mock_create_duel,
                                        mock_update_preduel,
                                        mock_resolve_status,
                                        mock_check_participants,
                                        mock_get_preduel,
                                        mock_response_model):
        response = self.interactor.run()
        mock_get_preduel.assert_called()
        mock_check_participants.assert_called_with(mock_get_preduel())
        mock_resolve_status.assert_called_with(mock_get_preduel())
        mock_update_preduel.assert_called_with(mock_resolve_status())
        mock_create_duel.assert_not_called()
        mock_pay_duel.assert_not_called()
        mock_create_finish_task.assert_not_called()
        mock_update_duel.assert_not_called()
        mock_notify_members.assert_not_called()
        mock_response_model.assert_called_with(
            mock_resolve_status().entity_id)
        assert response == mock_response_model()

    @patch(f'{prefix}.PutPreDuelResponseModel')
    @patch.object(PutPreDuelInteractor, '_get_preduel')
    @patch.object(PutPreDuelInteractor, 'check_participants')
    @patch.object(PutPreDuelInteractor,
                  'resolve_status',
                  return_value=make_preduel_golden_star())
    @patch.object(PutPreDuelInteractor, 'update_preduel')
    @patch.object(PutPreDuelInteractor, 'create_duel')
    @patch.object(PutPreDuelInteractor, 'pay_duel')
    @patch.object(PutPreDuelInteractor, 'create_finish_task')
    @patch.object(PutPreDuelInteractor, 'update_duel')
    @patch.object(PutPreDuelInteractor, 'notify_members')
    def test_run__golden_star(self, mock_notify_members,
                              mock_update_duel,
                              mock_create_finish_task,
                              mock_pay_duel,
                              mock_create_duel,
                              mock_update_preduel,
                              mock_resolve_status,
                              mock_check_participants,
                              mock_get_preduel,
                              mock_response_model):
        response = self.interactor.run()
        mock_get_preduel.assert_called()
        mock_check_participants.assert_called_with(mock_get_preduel())
        mock_resolve_status.assert_called_with(mock_get_preduel())
        mock_update_preduel.assert_called_with(mock_resolve_status())
        mock_create_duel.assert_called_with(mock_resolve_status())
        mock_pay_duel.assert_called_with(mock_create_duel())
        mock_create_finish_task.assert_called_with(
            mock_create_duel().entity_id)
        mock_update_duel.assert_called()
        mock_notify_members.assert_called()
        mock_response_model.assert_called_with(mock_create_duel().entity_id)
        assert response == mock_response_model()

    @patch(f'{prefix}.PutPreDuelResponseModel')
    @patch.object(PutPreDuelInteractor,
                  '_get_preduel',
                  side_effect=Exception('oops'))
    @patch.object(PutPreDuelInteractor, 'check_participants')
    @patch.object(PutPreDuelInteractor, 'resolve_status')
    @patch.object(PutPreDuelInteractor, 'update_preduel')
    @patch.object(PutPreDuelInteractor, 'create_duel')
    @patch.object(PutPreDuelInteractor, 'pay_duel')
    @patch.object(PutPreDuelInteractor, 'create_finish_task')
    @patch.object(PutPreDuelInteractor, 'update_duel')
    @patch.object(PutPreDuelInteractor, 'notify_members')
    def test_run__raises(self, mock_notify_members,
                         mock_update_duel,
                         mock_create_finish_task,
                         mock_pay_duel,
                         mock_create_duel,
                         mock_update_preduel,
                         mock_resolve_status,
                         mock_check_participants,
                         mock_get_preduel,
                         mock_response_model):
        with raises(PutPreDuelException) as exc:
            self.interactor.run()
        assert 'Error during preduel update: Exception: oops' \
            in str(exc.value)
        mock_get_preduel.assert_called()
        mock_check_participants.assert_not_called()
        mock_resolve_status.assert_not_called()
        mock_update_preduel.assert_not_called()
        mock_create_duel.assert_not_called()
        mock_pay_duel.assert_not_called()
        mock_create_finish_task.assert_not_called()
        mock_update_duel.assert_not_called()
        mock_notify_members.assert_not_called()
        mock_response_model.assert_not_called()

    @patch(f'{prefix}.find_entity_by_id')
    def test__get_preduel(self, mock_find_entity_by_id):
        mock_preduel_id = MagicMock()
        self.mock_request.preduel_id = mock_preduel_id
        preduel = self.interactor._get_preduel()
        mock_find_entity_by_id.assert_called_with(
            _id=mock_preduel_id,
            adapter_instance=self.mock_adapters.preduel_adapter,
            class_name='PreDuel')
        assert preduel == mock_find_entity_by_id()

    def test_get_other_captain_id(self):
        mock_player_id = MagicMock()
        self.mock_request.player_id = mock_player_id
        self.mock_adapters.team_adapter.get_by_id = \
            MagicMock(return_value=make_team(mock_player_id))
        mock_preduel = MagicMock()
        result = self.interactor.get_other_captain_id(mock_preduel)

        self.mock_adapters.team_adapter.get_by_id.assert_called()
        assert result == self.mock_adapters.team_adapter.get_by_id()\
            .captain.player_id

    def test_get_other_captain_id__captain_not_player_id(self):
        mock_preduel = MagicMock()
        self.mock_request.player_id = MagicMock()
        result = self.interactor.get_other_captain_id(mock_preduel)

        self.mock_adapters.team_adapter.get_by_id.assert_called()
        assert result == self.mock_adapters.team_adapter.get_by_id()\
            .captain.player_id
