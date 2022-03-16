from collections import namedtuple
from datetime import datetime
from playerstars_domain import (
    CoinType,
    DuelMemberType,
    DuelStatus)
from playerstars_domain.utils.datetime_helper import aware_utc
from playerstars_interactors.duel.enter_duel import (
    EnterDuelException,
    EnterDuelInteractor,
    EnterDuelInteractorAdapters,
    EnterDuelRequestModel,
    EnterDuelResponseModel,
    NotEnoughBalanceException, InvalidStatusException)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.duel.enter_duel'


def test_enter_duel_request_model():
    mock_json_data = MagicMock()
    request = EnterDuelRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('player_id', 'player_id'),
              ('duel_id', 'duel_id'),
              ('team_id', 'team_id')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_enter_duel_response_model():
    mock_duel = MagicMock()
    response = EnterDuelResponseModel(mock_duel)
    assert response.duel_data == mock_duel


def test_enter_duel_response_model_accept_duel_datetime():
    mock_duel = MagicMock()
    response = EnterDuelResponseModel(mock_duel)
    time_start = response.accept_duel_datetime()
    mock_duel.time_start.isoformat.assert_called_once()
    assert time_start == mock_duel.time_start.isoformat()


@patch(f'{prefix}.aware_now')
def test_enter_duel_response_model_current_server_time(aware_now_mock):
    mock_duel = MagicMock()
    response = EnterDuelResponseModel(mock_duel)
    server_time = response.current_server_time()

    aware_now_mock.assert_called_once()
    aware_now_mock().isoformat.assert_called_once()
    assert server_time == aware_now_mock().isoformat()


@patch.object(EnterDuelResponseModel, 'accept_duel_datetime')
@patch.object(EnterDuelResponseModel, 'current_server_time')
def test_enter_duel_response_model__call(mock_current_server_time,
                                         mock_accept_duel_datetime):
    mock_duel = MagicMock()
    response = EnterDuelResponseModel(mock_duel)
    assert response() == {
        'duel_id': mock_duel.entity_id,
        'accepted_at': mock_accept_duel_datetime(),
        'time_to_finish': mock_duel.time_to_finish_duel,
        'current_server_time': mock_current_server_time()}


def test_enter_duel_interactor_adapters():
    mock_duel_adapter_dynamo = MagicMock()
    mock_duel_adapter_graphql = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    mock_era_adapter = MagicMock()
    mock_scheduler_adapter = MagicMock()

    adapters = EnterDuelInteractorAdapters(
        duel_adapter_dynamo=mock_duel_adapter_dynamo,
        duel_adapter_graphql=mock_duel_adapter_graphql,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter,
        era_adapter=mock_era_adapter,
        scheduler_adapter=mock_scheduler_adapter)

    assert adapters.duel_adapter_dynamo == mock_duel_adapter_dynamo
    assert adapters.duel_adapter_graphql == mock_duel_adapter_graphql
    assert adapters.notification_adapter == mock_notification_adapter
    assert adapters.player_adapter == mock_player_adapter
    assert adapters.team_adapter == mock_team_adapter


Factory = namedtuple(
    'Factory', 'interactor, mock_adapters, mock_request, '
               'mock_time_to_finish_duel, mock_time_to_accept_invitation, '
               'mock_schedule_task_adapter')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(adapters: EnterDuelInteractorAdapters = MagicMock(),
                request: EnterDuelRequestModel = MagicMock(),
                time_to_finish_duel: int = 200,
                time_to_accept_invitation: int = 10,
                schedule_task_adapter=MagicMock()):
        interactor = EnterDuelInteractor(
            adapters=adapters,
            request=request,
            time_to_finish_duel=time_to_finish_duel,
            time_to_accept_invitation=time_to_accept_invitation,
            schedule_task_adapter=schedule_task_adapter,
            era_finish_duel_url='test/era')
        return Factory(interactor, adapters, request,
                       time_to_finish_duel,
                       time_to_accept_invitation,
                       schedule_task_adapter)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestEnterDuelInteractor(TestCase):
    def setUp(self):
        fac = TestEnterDuelInteractor.factory()
        self.interactor: EnterDuelInteractor = fac.interactor
        self.mock_adapters = fac.mock_adapters
        self.mock_request = fac.mock_request
        self.mock_time_to_finish_duel = fac.mock_time_to_finish_duel
        self.mock_time_to_accept_invitation = \
            fac.mock_time_to_accept_invitation
        self.mock_schedule_task_adapter = fac.mock_schedule_task_adapter

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.adapters == self.mock_adapters
        assert self.interactor.time_to_finish_duel == \
            self.mock_time_to_finish_duel
        assert self.interactor.time_to_accept_invitation == \
            self.mock_time_to_accept_invitation
        assert self.interactor.schedule_task_adapter == \
            self.mock_schedule_task_adapter

    def test_get_class_name_adapter_player(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.PLAYER
        class_name, adapter = self.interactor._get_class_name_adapter()
        assert class_name == 'Player'
        assert adapter == self.mock_adapters.player_adapter

    def test_get_class_name_adapter_team(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.TEAM
        class_name, adapter = self.interactor._get_class_name_adapter()
        assert class_name == 'Team'
        assert adapter == self.mock_adapters.team_adapter

    def test_get_member_adapter_player(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.PLAYER
        adapter = self.interactor._get_member_adapter()
        assert adapter == self.mock_adapters.player_adapter

    def test_get_member_adapter_team(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.TEAM
        adapter = self.interactor._get_member_adapter()
        assert adapter == self.mock_adapters.team_adapter

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_duel(self, find_entity_by_id_mock):
        duel = self.interactor._get_duel()
        find_entity_by_id_mock.assert_called_with(
            _id=self.mock_request.duel_id,
            adapter_instance=self.mock_adapters.duel_adapter_dynamo,
            class_name='Duel')
        assert duel == find_entity_by_id_mock()

    @patch.object(EnterDuelInteractor, '_get_class_name_adapter',
                  return_value=[MagicMock(), MagicMock()])
    @patch(f'{prefix}.find_entity_by_id')
    def test_get_challenger(self, find_entity_by_id_mock,
                            get_class_name_adapter_mock):
        member_id = MagicMock()
        challenger = self.interactor._get_challenger(member_id)
        get_class_name_adapter_mock.assert_called()
        find_entity_by_id_mock.assert_called_with(
            _id=member_id,
            adapter_instance=get_class_name_adapter_mock()[1],
            class_name=get_class_name_adapter_mock()[0])
        assert challenger == find_entity_by_id_mock()

    @patch.object(EnterDuelInteractor, '_get_class_name_adapter',
                  return_value=[MagicMock(), MagicMock()])
    @patch(f'{prefix}.find_entity_by_id')
    def test_get_challenged(self, find_entity_by_id_mock,
                            get_class_name_adapter_mock):
        member_id = MagicMock()
        challenged = self.interactor._get_challenged(member_id)
        get_class_name_adapter_mock.assert_called()
        find_entity_by_id_mock.assert_called_with(
            _id=member_id,
            adapter_instance=get_class_name_adapter_mock()[1],
            class_name=get_class_name_adapter_mock()[0])
        assert challenged == find_entity_by_id_mock()

    def test_calculate_finish_datetime(self):
        self.interactor.request_datetime = datetime(2020, 10, 5, 12, 0, 0)
        self.interactor.time_to_finish_duel = 120
        finish_datetime = self.interactor.calculate_finish_datetime()
        assert finish_datetime == datetime(2020, 10, 5, 14, 0, 0)

    @patch.object(EnterDuelInteractor, 'calculate_finish_datetime')
    @patch('playerstars_interactors.duel.enter_duel.create_era')
    def test_schedule_finish_task(self, era, calculate_finish_datetime_mock):
        self.interactor.schedule_finish_task()
        calculate_finish_datetime_mock.assert_called_once()
        era.assert_called_once_with(
            self.interactor.request.duel_id,
            calculate_finish_datetime_mock(),
            self.interactor.era_finish_duel_url,
            self.interactor.adapters.era_adapter,
            self.interactor.adapters.scheduler_adapter
        )

    @patch(f'{prefix}.aware_now')
    def test_update_duel_status(self, aware_now_mock):
        self.interactor.duel = MagicMock()
        self.interactor.update_duel_status()
        aware_now_mock.assert_called_once()
        assert self.interactor.duel.status == DuelStatus.DUELING
        assert self.interactor.duel.time_start == aware_now_mock()

    def test_add_challenged(self):
        self.interactor.duel = MagicMock()
        self.interactor.challenged = MagicMock()
        self.interactor._add_challenged()
        assert self.interactor.duel.challenged == \
            self.interactor.challenged.entity_id
        assert self.interactor.duel.challenged_accept is True

    def test_pay_player_red_star(self):
        player_mock = MagicMock()
        player_mock.red_star_balance = 5
        player_mock.golden_star_balance = 5
        updated_player = self.interactor.pay_player_red_star(player_mock, 2)
        assert updated_player.red_star_balance == 3
        assert updated_player.golden_star_balance == 5

    def test_pay_player_red_star_error_individual(self):
        player_mock = MagicMock()
        player_mock.user.nickname = 'Anselmo'
        player_mock.red_star_balance = 5

        with pytest.raises(NotEnoughBalanceException) as exc:
            self.interactor.pay_player_red_star(player_mock, 7)
        assert "Player Anselmo don't have enough red stars" \
            in str(exc.value)

    def test_pay_player_red_star_error_team(self):
        player_mock = MagicMock()
        player_mock.user.nickname = 'Anselmo'
        player_mock.red_star_balance = 5
        team_mock = MagicMock()
        team_mock.name = 'Stormianos'

        with pytest.raises(NotEnoughBalanceException) as exc:
            self.interactor.pay_player_red_star(player_mock, 7, team_mock)
        assert "Captain Anselmo of team Stormianos don't have " \
            "enough red stars" in str(exc.value)

    def test_pay_player_golden_star(self):
        player_mock = MagicMock()
        player_mock.red_star_balance = 5
        player_mock.golden_star_balance = 5
        updated_player = self.interactor.pay_player_golden_star(
            player_mock, 2)
        assert updated_player.golden_star_balance == 3
        assert updated_player.red_star_balance == 5

    def test_pay_player_golden_star_error_individual(self):
        player_mock = MagicMock()
        player_mock.user.nickname = 'Anselmo'
        player_mock.red_star_balance = 5
        player_mock.golden_star_balance = 5

        with pytest.raises(NotEnoughBalanceException) as exc:
            self.interactor.pay_player_golden_star(player_mock, 7)
        assert "Player Anselmo don't have enough golden stars" in str(
            exc.value)

    def test_pay_player_golden_star_error_team(self):
        player_mock = MagicMock()
        player_mock.user.nickname = 'Anselmo'
        player_mock.red_star_balance = 5
        player_mock.golden_star_balance = 5
        team_mock = MagicMock()
        team_mock.name = 'Stormianos'

        with pytest.raises(NotEnoughBalanceException) as exc:
            self.interactor.pay_player_golden_star(
                player_mock, 7, team_mock)
        assert "Captain Anselmo of team Stormianos don't have " \
            "enough golden stars" in str(exc.value)

    def test_check_time_limit_to_accept_invitation(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.time_send_invitation = \
            aware_utc(datetime(2020, 10, 5, 12, 0, 0))
        self.interactor.time_to_accept_invitation = 10
        self.interactor.request_datetime = \
            aware_utc(datetime(2020, 10, 5, 12, 3, 0))
        check_result = self.interactor.check_time_limit_to_accept_invitation()
        assert check_result is True

    def test_check_time_limit_to_accept_invitation_error(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.time_send_invitation = \
            aware_utc(datetime(2020, 10, 5, 12, 0, 0))
        self.interactor.time_to_accept_invitation = 10
        self.interactor.request_datetime = \
            aware_utc(datetime(2020, 10, 5, 12, 30, 0))

        with pytest.raises(EnterDuelException) as exc:
            self.interactor.check_time_limit_to_accept_invitation()
        assert "You can't accept duel after the limit: " \
               "2020-10-05T12:10:00+00:00" in str(exc.value)

    @patch(f'{prefix}.find_entity_by_id')
    @patch.object(EnterDuelInteractor, 'pay_player_golden_star')
    @patch.object(EnterDuelInteractor, 'pay_player_red_star')
    def test_pay_team_golden(self, pay_player_red_mock,
                             pay_player_golden_mock,
                             find_entity_by_id_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.star_type = CoinType.GOLDEN_STAR
        team_mock = MagicMock()
        updated_team = self.interactor.pay_team(team_mock)

        find_entity_by_id_mock.assert_called_with(
            _id=team_mock.captain.player_id,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        pay_player_golden_mock.assert_called_with(
            player=find_entity_by_id_mock(),
            value=self.interactor.duel.bet_size)
        pay_player_red_mock.assert_not_called()
        pay_player_golden_mock().save.assert_called()
        assert updated_team.captain.player == pay_player_golden_mock()

    @patch(f'{prefix}.find_entity_by_id')
    @patch.object(EnterDuelInteractor, 'pay_player_golden_star')
    @patch.object(EnterDuelInteractor, 'pay_player_red_star')
    def test_pay_team_red(self, pay_player_red_mock,
                          pay_player_golden_mock,
                          find_entity_by_id_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.star_type = CoinType.RED_STAR
        team_mock = MagicMock()
        updated_team = self.interactor.pay_team(team_mock)

        find_entity_by_id_mock.assert_called_with(
            _id=team_mock.captain.player_id,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        pay_player_red_mock.assert_called_with(
            player=find_entity_by_id_mock(),
            value=self.interactor.duel.bet_size)
        pay_player_golden_mock.assert_not_called()
        pay_player_red_mock().save.assert_called()
        assert updated_team.captain.player == pay_player_red_mock()

    @patch.object(EnterDuelInteractor, 'pay_player_golden_star')
    @patch.object(EnterDuelInteractor, 'pay_player_red_star')
    def test_pay_player_golden(self, pay_player_red_mock,
                               pay_player_golden_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.star_type = CoinType.GOLDEN_STAR
        player_mock = MagicMock()
        updated_player = self.interactor.pay_player(player_mock)

        pay_player_golden_mock.assert_called_with(
            player=player_mock,
            value=self.interactor.duel.bet_size)
        pay_player_red_mock.assert_not_called()
        assert updated_player == pay_player_golden_mock()

    @patch.object(EnterDuelInteractor, 'pay_player_golden_star')
    @patch.object(EnterDuelInteractor, 'pay_player_red_star')
    def test_pay_player_red(self, pay_player_red_mock,
                            pay_player_golden_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.star_type = CoinType.RED_STAR
        player_mock = MagicMock()
        updated_player = self.interactor.pay_player(player_mock)

        pay_player_red_mock.assert_called_with(
            player=player_mock,
            value=self.interactor.duel.bet_size)
        pay_player_golden_mock.assert_not_called()
        assert updated_player == pay_player_red_mock()

    @patch.object(EnterDuelInteractor, 'pay_player')
    def test_pay_duel_player(self, pay_player_mock):
        self.interactor.pay_duel_player()
        assert pay_player_mock.call_count == 2
        assert pay_player_mock().save.call_count == 2
        assert self.interactor.challenger == pay_player_mock()
        assert self.interactor.challenged == pay_player_mock()

    @patch.object(EnterDuelInteractor, 'pay_team')
    def test_pay_duel_team(self, pay_team_mock):
        self.interactor.pay_duel_team()
        assert pay_team_mock.call_count == 2
        assert pay_team_mock().save.call_count == 2

    @patch.object(EnterDuelInteractor, 'pay_duel_player')
    @patch.object(EnterDuelInteractor, 'pay_duel_team')
    def test__pay_duel__member_as_player(self, pay_duel_team_mock,
                                         pay_duel_player_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.PLAYER
        self.interactor._pay_duel()
        pay_duel_player_mock.assert_called()
        pay_duel_team_mock.assert_not_called()

    @patch.object(EnterDuelInteractor, 'pay_duel_player')
    @patch.object(EnterDuelInteractor, 'pay_duel_team')
    def test__pay_duel__member_as_team(self, pay_duel_team_mock,
                                       pay_duel_player_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.TEAM
        self.interactor._pay_duel()
        pay_duel_player_mock.assert_not_called()
        pay_duel_team_mock.assert_called()

    @patch.object(EnterDuelInteractor, '_get_duel')
    @patch.object(EnterDuelInteractor, '_check_duel_status')
    @patch.object(EnterDuelInteractor,
                  'check_time_limit_to_accept_invitation')
    @patch.object(EnterDuelInteractor, '_get_member_adapter')
    @patch.object(EnterDuelInteractor, '_get_challenger')
    @patch.object(EnterDuelInteractor, '_get_challenged')
    @patch.object(EnterDuelInteractor, '_add_challenged')
    @patch.object(EnterDuelInteractor, '_pay_duel')
    @patch.object(EnterDuelInteractor, 'update_duel_status')
    @patch.object(EnterDuelInteractor, 'schedule_finish_task')
    @patch(f'{prefix}.send_duel_ongoing_notification')
    @patch(f'{prefix}.EnterDuelResponseModel')
    def test_run(self, response_model_mock,
                 send_duel_ongoing_notification_mock,
                 schedule_finish_task_mock,
                 update_duel_status_mock,
                 pay_duel_mock,
                 add_challenged_mock,
                 get_challenged_mock,
                 get_challenger_mock,
                 get_member_adapter_mock,
                 check_time_limit_to_accept_invitation_mock,
                 check_duel_status_mock,
                 get_duel_mock):
        response = self.interactor.run()
        get_duel_mock.assert_called_once()
        check_duel_status_mock.assert_called_once()
        check_time_limit_to_accept_invitation_mock.assert_called_once()

        get_member_adapter_mock.assert_called()
        get_challenger_mock.assert_called_with(get_duel_mock().challenger)
        get_challenged_mock.assert_called_with(get_duel_mock().challenged)
        get_challenger_mock().set_adapter.assert_called_with(
            get_member_adapter_mock())
        get_challenged_mock().set_adapter.assert_called_with(
            get_member_adapter_mock())
        add_challenged_mock.assert_called_once()

        pay_duel_mock.assert_called_once()
        update_duel_status_mock.assert_called_once()
        schedule_finish_task_mock.assert_called_once()
        send_duel_ongoing_notification_mock.assert_called_once_with(
            duel=get_duel_mock(),
            challenger=get_challenger_mock(),
            challenged=get_challenged_mock(),
            notification_adapter=self.mock_adapters.notification_adapter,
            logger_instance=self.interactor.logger)

        get_duel_mock().save_graphql.assert_called_with(exec_update=True)
        response_model_mock.assert_called_with(get_duel_mock())
        assert response == response_model_mock()

    @patch.object(EnterDuelInteractor, '_get_duel',
                  side_effect=Exception('oops'))
    def test_run_error(self, get_duel_mock):
        with pytest.raises(EnterDuelException) as exc:
            self.interactor.run()
        assert 'Error during update duel: Exception: oops' in str(exc.value)

    def test__check_duel_status(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.status = DuelStatus.LOBBY
        check_result = self.interactor._check_duel_status()
        assert check_result is True

    def test__check_duel_status_not_lobby(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.status = DuelStatus.DUELING

        with pytest.raises(InvalidStatusException) as exc:
            self.interactor._check_duel_status()
        assert 'Invalid duel state: DUELING' in str(exc.value)
