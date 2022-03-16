from collections import namedtuple

from playerstars_domain import DuelMemberType, DuelStatus, NotificationStatus

from playerstars_interactors.duel.cancel_duel import (
    CancelDuelException,
    CancelDuelInteractor,
    CancelDuelInteractorAdapters,
    CancelDuelRequestModel,
    CancelDuelResponseModel,
    DuelMemberNotCreatorException,
    DuelNotLobbyException)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.duel.cancel_duel'


def test_cancelduel_requestmodel():
    mock_json_data = MagicMock()
    request = CancelDuelRequestModel(mock_json_data)
    calls = {x[1][0]: x() for x in mock_json_data.mock_calls}

    fields = [('player_id', 'player_id'), ('duel_id', 'duel_id')]

    for field in fields:
        assert getattr(request, field[0]) == calls[field[1]]
    assert len(calls) == len(fields)


def test_cancelduel_responsemodel():
    duel_id_mock = MagicMock()
    notification_id_mock = MagicMock()
    cancel_datetime_mock = MagicMock()
    response = CancelDuelResponseModel(
        duel_id=duel_id_mock,
        notification_id=notification_id_mock,
        cancel_datetime=cancel_datetime_mock)

    assert response.duel_id == duel_id_mock
    assert response.notification_id == notification_id_mock
    assert response.cancel_datetime == cancel_datetime_mock


def test_responsemodel_call():
    duel_id_mock = MagicMock()
    notification_id_mock = MagicMock()
    cancel_datetime_mock = MagicMock()
    response = CancelDuelResponseModel(
        duel_id=duel_id_mock,
        notification_id=notification_id_mock,
        cancel_datetime=cancel_datetime_mock)
    assert response() == {
        'duel_id': duel_id_mock,
        'notification_id': notification_id_mock,
        'cancel_datetime': cancel_datetime_mock}


def test_cancel_duel_interactor_adapters():
    mock_duel_adapter_dynamo = MagicMock()
    mock_duel_adapter_graphql = MagicMock()
    mock_notification_adapter = MagicMock()
    mock_player_adapter = MagicMock()
    mock_team_adapter = MagicMock()

    adapters = CancelDuelInteractorAdapters(
        duel_adapter_dynamo=mock_duel_adapter_dynamo,
        duel_adapter_graphql=mock_duel_adapter_graphql,
        notification_adapter=mock_notification_adapter,
        player_adapter=mock_player_adapter,
        team_adapter=mock_team_adapter)

    assert adapters.duel_adapter_dynamo == mock_duel_adapter_dynamo
    assert adapters.duel_adapter_graphql == mock_duel_adapter_graphql
    assert adapters.notification_adapter == \
        mock_notification_adapter
    assert adapters.player_adapter == mock_player_adapter
    assert adapters.team_adapter == mock_team_adapter


Factory = namedtuple('Factory', 'interactor, mock_adapters, mock_request')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(adapters: CancelDuelInteractorAdapters = MagicMock(),
                request: CancelDuelRequestModel = MagicMock()):
        interactor = CancelDuelInteractor(adapters=adapters, request=request)
        return Factory(interactor, adapters, request)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestCancelDuelInteractor(TestCase):
    def setUp(self):
        fac = TestCancelDuelInteractor.factory()
        self.interactor: CancelDuelInteractor = fac.interactor
        self.mock_adapters = fac.mock_adapters
        self.mock_request = fac.mock_request

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.adapters == self.mock_adapters

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_player(self, find_entity_mock):
        id_mock = MagicMock()
        player = self.interactor.get_player(id_mock)
        find_entity_mock.assert_called_once_with(
            _id=id_mock,
            adapter_instance=self.mock_adapters.player_adapter,
            class_name='Player')
        assert player == find_entity_mock()

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_team(self, find_entity_mock):
        id_mock = MagicMock()
        team = self.interactor.get_team(id_mock)
        find_entity_mock.assert_called_once_with(
            _id=id_mock,
            adapter_instance=self.mock_adapters.team_adapter,
            class_name='Team')
        assert team == find_entity_mock()

    @patch(f'{prefix}.find_entity_by_id')
    def test_get_duel(self, find_entity_mock):
        duel = self.interactor.get_duel()
        find_entity_mock.assert_called_once_with(
            _id=self.mock_request.duel_id,
            adapter_instance=self.mock_adapters.duel_adapter_dynamo,
            class_name='Duel')
        assert duel == find_entity_mock()

    def test_check_if_player_can_cancel_duel_player(self):
        challenger_id_mock = MagicMock()
        self.interactor.player_request = MagicMock()
        self.interactor.player_request.entity_id = challenger_id_mock
        self.interactor.duel = MagicMock()
        self.interactor.duel.challenger = challenger_id_mock
        check_result = self.interactor.check_if_player_can_cancel_duel_player()
        assert check_result

    def test_check_if_player_can_cancel_duel_player_error(self):
        self.interactor.player_request = MagicMock()
        self.interactor.player_request.user.nickname = 'Anselmo'
        self.interactor.duel = MagicMock()

        with pytest.raises(DuelMemberNotCreatorException) as exc:
            self.interactor.check_if_player_can_cancel_duel_player()
        assert "Player Anselmo can't cancel duel because isn't duel creator" \
            in str(exc.value)

    @patch.object(CancelDuelInteractor, 'get_team')
    def test_check_if_player_can_cancel_duel_team(self, get_team_mock):
        player_id_mock = MagicMock()
        get_team_mock().captain.player_id = player_id_mock
        self.mock_request.player_id = player_id_mock
        self.interactor.duel = MagicMock()
        check_result = self.interactor.check_if_player_can_cancel_duel_team()
        get_team_mock.assert_called_with(self.interactor.duel.challenger)
        assert check_result

    @patch.object(CancelDuelInteractor, 'get_team')
    def test_check_if_player_can_cancel_duel_team_error(self, get_team_mock):
        self.interactor.player_request = MagicMock()
        self.interactor.player_request.user.nickname = 'Anselmo'
        self.interactor.duel = MagicMock()

        with pytest.raises(DuelMemberNotCreatorException) as exc:
            self.interactor.check_if_player_can_cancel_duel_team()
        assert "Player Anselmo can't cancel duel because isn't " \
            "captain of challenger" in str(exc.value)

    @patch.object(CancelDuelInteractor, 'check_if_player_can_cancel_duel_player')
    @patch.object(CancelDuelInteractor, 'check_if_player_can_cancel_duel_team')
    def test_check_if_player_can_cancel_duel__player(
            self, check_cancel_duel_team_mock, check_cancel_duel_player_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.PLAYER
        check_result = self.interactor.check_if_player_can_cancel_duel()

        assert check_result == check_cancel_duel_player_mock()
        check_cancel_duel_player_mock.assert_called()
        check_cancel_duel_team_mock.assert_not_called()

    @patch.object(CancelDuelInteractor, 'check_if_player_can_cancel_duel_player')
    @patch.object(CancelDuelInteractor, 'check_if_player_can_cancel_duel_team')
    def test_check_if_player_can_cancel_duel__team(
            self, check_cancel_duel_team_mock, check_cancel_duel_player_mock):
        self.interactor.duel = MagicMock()
        self.interactor.duel.member_type = DuelMemberType.TEAM
        check_result = self.interactor.check_if_player_can_cancel_duel()

        assert check_result == check_cancel_duel_team_mock()
        check_cancel_duel_player_mock.assert_not_called()
        check_cancel_duel_team_mock.assert_called()

    @patch(f'{prefix}.datetime')
    def test_delete_duel(self, mock_datetime):
        self.interactor.duel = MagicMock()
        self.interactor.duel.status = DuelStatus.LOBBY
        delete_result = self.interactor.delete_duel()

        self.interactor.duel.set_adapter.assert_called_with(
            self.mock_adapters.duel_adapter_graphql)
        assert self.interactor.duel.status == DuelStatus.DELETED
        mock_datetime.utcnow.assert_called()
        assert self.interactor.duel.time_cancel == mock_datetime.utcnow()
        self.interactor.duel.save_graphql.assert_called_with(exec_update=True)
        assert delete_result == self.interactor.duel.save_graphql()

    def test_delete_duel_error(self):
        self.interactor.duel = MagicMock()
        self.interactor.duel.duel_status = DuelStatus.DUELING
        with pytest.raises(DuelNotLobbyException) as exc:
            self.interactor.delete_duel()
        assert "Duel can't to cancel because it isn't on state LOBBY" in str(exc.value)

    @patch.object(CancelDuelInteractor, 'get_notification_by_duel')
    def test_delete_notification(self, get_notification_mock):
        delete_result = self.interactor.delete_notification()
        get_notification_mock().save.assert_called()
        get_notification_mock().status == NotificationStatus.DELETED
        get_notification_mock().set_adapter.assert_called_with(
            self.mock_adapters.notification_adapter)
        assert delete_result == get_notification_mock().save()

    @patch.object(CancelDuelInteractor, 'get_notification_by_duel', return_value=None)
    def test_delete_notification_none(self, get_notification_mock):
        delete_result = self.interactor.delete_notification()
        assert delete_result is None

    @patch.object(CancelDuelInteractor, 'get_duel')
    @patch.object(CancelDuelInteractor, 'get_player')
    @patch.object(CancelDuelInteractor, 'check_if_player_can_cancel_duel')
    @patch.object(CancelDuelInteractor, 'delete_duel')
    @patch.object(CancelDuelInteractor, 'delete_notification')
    @patch(f'{prefix}.CancelDuelResponseModel')
    def test_run(self, mock_response_model,
                 mock_delete_notification,
                 mock_delete_duel,
                 mock_check_player_cancel,
                 mock_get_player,
                 mock_get_duel):
        cancel_result = self.interactor.run()
        mock_get_duel.assert_called_once()
        mock_get_player.assert_called_once_with(self.mock_request.player_id)
        mock_check_player_cancel.assert_called_once()
        mock_delete_duel.assert_called_once()
        mock_delete_notification.assert_called_once()
        mock_response_model.assert_called_with(
            duel_id=mock_delete_duel(),
            notification_id=mock_delete_notification(),
            cancel_datetime=mock_get_duel().time_cancel.isoformat())
        assert cancel_result == mock_response_model()

    @patch.object(CancelDuelInteractor, 'get_duel', side_effect=Exception('oops'))
    def test_run_error(self, mock_get_duel):
        with pytest.raises(CancelDuelException) as exc:
            self.interactor.run()
        assert 'Error during cancel duel: Exception: oops' in str(exc.value)

    def test_get_notification_by_duel(self):
        duel_id_mock = MagicMock()
        self.mock_request.duel_id = duel_id_mock

        notification_1 = MagicMock()
        notification_1.duel_id = duel_id_mock
        notification_1.status = NotificationStatus.CREATED
        notification_2 = MagicMock()
        notification_3 = MagicMock()
        notification_3.duel_id = duel_id_mock
        notification_3.status = NotificationStatus.DELETED

        notification_list = [notification_1, notification_2, notification_3]
        self.mock_adapters.notification_adapter_dynamo.list_all = \
            MagicMock(return_value=notification_list)

        self.interactor.get_notification_by_duel()

        self.mock_adapters.notification_adapter.list_all.\
            assert_called()
