from collections import namedtuple
from playerstars_adapters import ConsoleAdapter
from playerstars_interactors.console.get_all_consoles_external import (
    GetAllConsolesExternalException,
    GetAllConsolesExternalInteractor,
    GetAllConsolesExternalResponseModel)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.console.get_all_consoles_external'


def test_response_model():
    consoles_mock = MagicMock()
    response = GetAllConsolesExternalResponseModel(consoles_mock)
    assert response
    assert response.consoles == consoles_mock


def test_response_model__call():
    console_mock = MagicMock()
    consoles_mock = [console_mock]
    response = GetAllConsolesExternalResponseModel(consoles_mock)
    call_result = response()

    assert call_result == [console_mock.to_json()]
    console_mock.to_json.assert_called()


Factory = namedtuple('Factory', 'interactor, mock_console_adapter')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(console_adapter: ConsoleAdapter = MagicMock()):
        interactor = GetAllConsolesExternalInteractor(
            console_adapter=console_adapter)
        return Factory(interactor, console_adapter)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestGetAllConsolesExternalInteractor(TestCase):
    def setUp(self):
        fac = TestGetAllConsolesExternalInteractor.factory()
        self.interactor: GetAllConsolesExternalInteractor = fac.interactor
        self.mock_console_adapter = fac.mock_console_adapter

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.console_adapter == self.mock_console_adapter

    def test_get_all_consoles(self):
        all_consoles = self.interactor.get_all_consoles()
        assert all_consoles == self.mock_console_adapter.list_all()
        self.mock_console_adapter.list_all.assert_called()

    def test_filter_games_only_actives(self):
        game_1_mock = MagicMock()
        game_1_mock.active = True
        game_2_mock = MagicMock()
        game_2_mock.active = False
        game_list = [game_1_mock, game_2_mock]
        filtered_game_list = \
            self.interactor.filter_games_only_actives(game_list)
        assert isinstance(filtered_game_list, list)
        assert filtered_game_list == [game_1_mock]

    def test_filter_games_only_actives_empty(self):
        game_1_mock = MagicMock()
        game_1_mock.active = False
        game_2_mock = MagicMock()
        game_2_mock.active = False
        game_list = [game_1_mock, game_2_mock]
        filtered_game_list = \
            self.interactor.filter_games_only_actives(game_list)
        assert isinstance(filtered_game_list, list)
        assert filtered_game_list == []

    @patch.object(GetAllConsolesExternalInteractor, 'process_console_games')
    def test_process_consoles(self, mock_process_console_games):
        console_mock = MagicMock()
        consoles_mock = [console_mock]
        processed_consoles = self.interactor.process_consoles(consoles_mock)
        mock_process_console_games.assert_called_with(console_mock)
        assert processed_consoles == [mock_process_console_games()]

    @patch.object(GetAllConsolesExternalInteractor,
                  'process_console_games',
                  return_value=None)
    def test_process_consoles_empty(self, mock_process_console_games):
        console_mock = MagicMock()
        consoles_mock = [console_mock]
        processed_consoles = self.interactor.process_consoles(consoles_mock)
        mock_process_console_games.assert_called_with(console_mock)
        assert processed_consoles == []

    @patch.object(GetAllConsolesExternalInteractor,
                  'filter_games_only_actives')
    def test_process_console_games(self, mock_filter_games_only_actives):
        console_mock = MagicMock()
        games_mock = MagicMock()
        console_mock.games = games_mock
        processed_console = self.interactor.process_console_games(console_mock)
        mock_filter_games_only_actives.assert_called_with(games_mock)
        assert processed_console == console_mock
        assert processed_console.games == mock_filter_games_only_actives()

    @patch.object(GetAllConsolesExternalInteractor,
                  'filter_games_only_actives',
                  return_value=None)
    def test_process_console_games_without_games(
            self, mock_filter_games_only_actives):
        console_mock = MagicMock()
        processed_console = self.interactor.process_console_games(console_mock)
        mock_filter_games_only_actives.assert_called_with(console_mock.games)
        assert processed_console is None

    @patch.object(GetAllConsolesExternalInteractor, 'get_all_consoles')
    @patch.object(GetAllConsolesExternalInteractor, 'process_consoles')
    @patch(f'{prefix}.GetAllConsolesExternalResponseModel')
    def test_run(self, response_model_mock,
                 process_consoles_mock,
                 get_all_consoles_mock):
        response = self.interactor.run()
        get_all_consoles_mock.assert_called()
        process_consoles_mock.assert_called_with(get_all_consoles_mock())
        response_model_mock.assert_called_with(process_consoles_mock())
        assert response == response_model_mock()

    @patch.object(GetAllConsolesExternalInteractor,
                  'get_all_consoles',
                  side_effect=Exception('oops'))
    @patch.object(GetAllConsolesExternalInteractor, 'process_consoles')
    @patch(f'{prefix}.GetAllConsolesExternalResponseModel')
    def test_run_with_error(self, response_model_mock,
                            process_consoles_mock,
                            get_all_consoles_mock):
        with pytest.raises(GetAllConsolesExternalException) as exc:
            self.interactor.run()
        assert 'Error during get all consoles to ' \
            'not logged users: Exception: oops' in str(exc.value)
        response_model_mock.assert_not_called()
        process_consoles_mock.assert_not_called()
        get_all_consoles_mock.assert_called()
