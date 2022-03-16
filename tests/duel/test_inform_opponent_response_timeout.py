from collections import namedtuple
from playerstars_domain import DuelMemberType, DuelStatus
from playerstars_interactors import (
    DuelMemberNotCreatorException,
    InformOpponentResponseTimeoutException,
    InformOpponentResponseTimeoutInteractor,
    InformOpponentResponseTimeoutInteractorAdapters,
    InformOpponentResponseTimeoutRequestModel,
    InformOpponentResponseTimeoutResponseModel)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch


import pytest


prefix = 'playerstars_interactors.duel.inform_opponent_response_timeout'


def test_inform_opponent_timeout_request_model():
    mock_json_data = MagicMock()
    request = InformOpponentResponseTimeoutRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('player_id', 'player_id'), ('duel_id', 'duel_id')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_inform_opponent_timeout_response_model():
    duel_mock = MagicMock()
    response = InformOpponentResponseTimeoutResponseModel(duel_mock)
    assert response.duel_id == duel_mock.entity_id
    assert response.cancelation_datetime == duel_mock.time_finish


def test_inform_opponent_timeout_response_model_call():
    duel_mock = MagicMock()
    response = InformOpponentResponseTimeoutResponseModel(duel_mock)
    response_call = response()
    assert response_call == {
        'duel_id': response.duel_id,
        'cancelation_datetime': response.cancelation_datetime.isoformat()}


def test_inform_opponent_timeout_response_interactor_adapters():
    mock_duel_adapter_dynamo = MagicMock()
    mock_duel_adapter_graphql = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()
    adapters = InformOpponentResponseTimeoutInteractorAdapters(
        duel_adapter_dynamo=mock_duel_adapter_dynamo,
        duel_adapter_graphql=mock_duel_adapter_graphql,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter)

    assert adapters.duel_adapter_dynamo == mock_duel_adapter_dynamo
    assert adapters.duel_adapter_graphql == mock_duel_adapter_graphql
    assert adapters.player_adapter == mock_player_adapter
    assert adapters.team_adapter == mock_team_adapter


Factory = namedtuple('Factory', 'interactor, mock_adapters, mock_request')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(adapters: InformOpponentResponseTimeoutInteractorAdapters =
                MagicMock(),
                request: InformOpponentResponseTimeoutRequestModel =
                MagicMock()):
        interactor = InformOpponentResponseTimeoutInteractor(
            adapters=adapters,
            request=request)
        return Factory(interactor, adapters, request)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestInformOpponentResponseTimeoutInteractor(TestCase):
    def setUp(self):
        fac = TestInformOpponentResponseTimeoutInteractor.factory()
        self.interactor: InformOpponentResponseTimeoutInteractor = \
            fac.interactor
        self.mock_adapters = fac.mock_adapters
        self.mock_request = fac.mock_request

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.adapters == self.mock_adapters

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_duel(self, find_entity_by_id_mock):
        duel = self.interactor.get_duel()
        find_entity_by_id_mock.assert_called_with(
            _id=self.mock_request.duel_id,
            adapter_instance=self.mock_adapters.duel_adapter_dynamo,
            class_name='Duel')
        assert duel == find_entity_by_id_mock()

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_team_data(self, find_entity_by_id_mock):
        self.interactor.duel = MagicMock()
        team = self.interactor.get_team_data()
        find_entity_by_id_mock.assert_called_with(
            _id=self.interactor.duel.challenger,
            adapter_instance=self.mock_adapters.team_adapter,
            class_name='Team')
        assert team == find_entity_by_id_mock()

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_player_data(self, find_entity_by_id_mock):
        player_id = MagicMock()
        player = self.interactor.get_player_data(player_id)
        find_entity_by_id_mock.assert_called_with(
            _id=player_id,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        assert player == find_entity_by_id_mock()

    @patch.object(InformOpponentResponseTimeoutInteractor,
                  'check_duel_owner_player')
    @patch.object(InformOpponentResponseTimeoutInteractor,
                  'check_duel_owner_team')
    def test_check_duel_owner_caseplayer(self,
                                         check_duel_owner_team_mock,
                                         check_duel_owner_player_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.PLAYER
        check_result = self.interactor.check_duel_owner()
        check_duel_owner_team_mock.assert_not_called()
        check_duel_owner_player_mock.assert_called()
        assert check_result == check_duel_owner_player_mock()

    @patch.object(InformOpponentResponseTimeoutInteractor,
                  'check_duel_owner_player')
    @patch.object(InformOpponentResponseTimeoutInteractor,
                  'check_duel_owner_team')
    def test_check_duel_owner_caseteam(self,
                                       check_duel_owner_team_mock,
                                       check_duel_owner_player_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.TEAM
        check_result = self.interactor.check_duel_owner()
        check_duel_owner_team_mock.assert_called_once()
        check_duel_owner_player_mock.assert_not_called()
        assert check_result == check_duel_owner_team_mock()

    def test_check_duel_owner_player(self):
        player_id_mock = MagicMock()
        self.mock_request.player_id = player_id_mock
        self.interactor.duel = MagicMock()
        self.interactor.duel.challenger = player_id_mock
        check_result = self.interactor.check_duel_owner_player()
        assert check_result is True

    def test_check_duel_owner_player_error(self):
        self.interactor.player_data = MagicMock()
        self.interactor.player_data.user.nickname = 'Anselmo'
        self.interactor.duel = MagicMock()

        with pytest.raises(DuelMemberNotCreatorException) as exc:
            self.interactor.check_duel_owner_player()
        assert "Player Anselmo isn't the duel's owner" in str(exc.value)

    @patch.object(InformOpponentResponseTimeoutInteractor, 'get_team_data')
    def test_check_duel_owner_team(self, get_team_data_mock):
        player_id_mock = MagicMock()
        get_team_data_mock().captain.player_id = player_id_mock
        self.mock_request.player_id = player_id_mock
        check_result = self.interactor.check_duel_owner_team()
        assert check_result is True

    @patch.object(InformOpponentResponseTimeoutInteractor, 'get_team_data')
    def test_check_duel_owner_team_error(self, get_team_data_mock):
        get_team_data_mock().name = 'Stormianos'
        self.interactor.player_data = MagicMock()
        self.interactor.player_data.user.nickname = 'Anselmo'

        with pytest.raises(DuelMemberNotCreatorException) as exc:
            self.interactor.check_duel_owner_team()
        assert "Player Anselmo isn't the captain of the team Stormianos" \
            in str(exc.value)

    @patch(f'{prefix}.aware_now')
    def test_set_duel_timeout_status(self, aware_now_mock):
        self.interactor.duel = MagicMock()
        self.interactor.set_duel_timeout_status()

        aware_now_mock.assert_called_once()
        self.interactor.duel.set_adapter.assert_called_with(
            self.mock_adapters.duel_adapter_graphql)
        self.interactor.duel.save_graphql.assert_called_with(
            exec_update=True)
        assert self.interactor.duel.status == DuelStatus.CANCELED_BY_TIMEOUT
        assert self.interactor.duel.time_finish == aware_now_mock()

    @patch(f'{prefix}.InformOpponentResponseTimeoutResponseModel')
    @patch.object(InformOpponentResponseTimeoutInteractor,
                  'set_duel_timeout_status')
    @patch.object(InformOpponentResponseTimeoutInteractor,
                  'check_duel_owner')
    @patch.object(InformOpponentResponseTimeoutInteractor, 'get_player_data')
    @patch.object(InformOpponentResponseTimeoutInteractor, 'get_duel')
    def test_run(self, get_duel_mock,
                 get_player_data_mock,
                 check_duel_owner_mock,
                 set_duel_timeout_status_mock,
                 response_model_mock):
        response = self.interactor.run()
        get_duel_mock.assert_called_once()
        get_player_data_mock.assert_called_once_with(
            self.mock_request.player_id)
        check_duel_owner_mock.assert_called_once()
        set_duel_timeout_status_mock.assert_called_once()
        assert self.interactor.duel == get_duel_mock()
        response_model_mock.assert_called_once_with(get_duel_mock())
        assert response == response_model_mock()

    @patch.object(InformOpponentResponseTimeoutInteractor, 'get_duel',
                  side_effect=Exception('oops'))
    def test_run_error(self, get_duel_mock):
        with pytest.raises(InformOpponentResponseTimeoutException) as exc:
            self.interactor.run()
        assert 'Error during define duel timeout status: Exception: oops' \
            in str(exc.value)
        get_duel_mock.assert_called_once()
