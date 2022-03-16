from collections import namedtuple
from playerstars_adapters import ConsoleAdapter
from playerstars_interactors.admin import (
    GetAllGamesAdminException,
    GetAllGamesAdminInteractor,
    GetAllGamesAdminResponseModel)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.admin.get_all_games_admin'


def test_response_model():
    game_list = MagicMock()
    response_model = GetAllGamesAdminResponseModel(game_list)
    assert response_model.game_list == game_list


def test_response_model_call():
    game_list = MagicMock()
    response_model = GetAllGamesAdminResponseModel(game_list)
    assert response_model() == game_list


Factory = namedtuple('Factory', 'interactor, mock_console_adapter')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(console_adapter: ConsoleAdapter = MagicMock()):
        interactor = GetAllGamesAdminInteractor(
            console_adapter=console_adapter)
        return Factory(interactor, console_adapter)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestCancelDuelInteractor(TestCase):
    def setUp(self):
        fac = TestCancelDuelInteractor.factory()
        self.interactor: GetAllGamesAdminInteractor = fac.interactor
        self.mock_console_adapter = fac.mock_console_adapter

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.console_adapter == self.mock_console_adapter

    def test_format_game_for_response(self):
        console_data = MagicMock()
        game_data = MagicMock()
        result = self.interactor.format_game_for_response(
            console=console_data,
            game=game_data)
        assert result == {
            'game_id': game_data.entity_id,
            'game_name': game_data.name,
            'game_logo_path': game_data.logo_path,
            'console_id': console_data.entity_id,
            'console_name': console_data.name}

    @patch.object(GetAllGamesAdminInteractor, 'format_game_for_response')
    def test_process_console_for_response(self, format_game_mock):
        game_data = MagicMock()
        console_data = MagicMock()
        console_data.games = [game_data]
        result = self.interactor.process_console_for_response(console_data)
        assert result == [format_game_mock()]
        format_game_mock.assert_called()

    @patch.object(GetAllGamesAdminInteractor, 'format_game_for_response')
    def test_process_console_for_response_not_games(self, format_game_mock):
        console_data = MagicMock()
        console_data.games = []
        result = self.interactor.process_console_for_response(console_data)
        assert result == []
        format_game_mock.assert_not_called()

    @patch.object(GetAllGamesAdminInteractor, 'process_console_for_response')
    def test_process_console_list_for_response(self, process_console_mock):
        console_data = MagicMock()
        console_list = [console_data]
        result = self.interactor.process_console_list_for_response(console_list)
        assert result == [process_console_mock()]
        process_console_mock.assert_called()

    @patch.object(GetAllGamesAdminInteractor, 'process_console_for_response')
    def test_process_console_list_for_response_list_empty(
            self, process_console_mock):
        result = self.interactor.process_console_list_for_response([])
        assert result == []
        process_console_mock.assert_not_called()

    @patch.object(GetAllGamesAdminInteractor, 'process_console_list_for_response')
    @patch(f'{prefix}.GetAllGamesAdminResponseModel')
    def test_run(self, response_model_mock, process_console_list_mock):
        response = self.interactor.run()
        self.mock_console_adapter.list_all.assert_called_once()
        process_console_list_mock.assert_called_once_with(
            self.mock_console_adapter.list_all())
        response_model_mock.assert_called_with(process_console_list_mock())
        assert response == response_model_mock()

    @patch(f'{prefix}.GetAllGamesAdminResponseModel')
    @patch.object(GetAllGamesAdminInteractor,
                  'process_console_list_for_response',
                  side_effect=Exception('oops'))
    def test_run_error(self, process_console_list_mock, response_model_mock):
        with pytest.raises(GetAllGamesAdminException) as exc:
            self.interactor.run()
        assert 'Error during get game list: Exception: oops' in str(exc.value)
        response_model_mock.assert_not_called()
