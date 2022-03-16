from collections import namedtuple
from playerstars_adapters import ConsoleAdapter
from playerstars_interactors.console.get_consoles_active_games import (
    GetAllConsolesActiveGamesException,
    GetAllConsolesActiveGamesResponseModel,
    GetAllConsolesActiveGamesInteractor)
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest


prefix = 'playerstars_interactors.console.get_consoles_active_games'


def test_response_model():
    consoles_mock = MagicMock()
    response = GetAllConsolesActiveGamesResponseModel(consoles_mock)
    assert response
    assert response.consoles == consoles_mock


def test_response_model__call():
    console_mock = MagicMock()
    consoles_mock = [console_mock]
    response = GetAllConsolesActiveGamesResponseModel(consoles_mock)
    call_result = response()

    assert call_result == [console_mock]


Factory = namedtuple('Factory', 'interactor, mock_console_adapter')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(console_adapter: ConsoleAdapter = MagicMock()):
        interactor = GetAllConsolesActiveGamesInteractor(
            console_adapter=console_adapter)
        return Factory(interactor, console_adapter)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestGetAllConsolesActiveGamesInteractor(TestCase):
    def setUp(self):
        fac = TestGetAllConsolesActiveGamesInteractor.factory()
        self.interactor: GetAllConsolesActiveGamesInteractor = fac.interactor
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
        assert not filtered_game_list

    @patch.object(GetAllConsolesActiveGamesInteractor,
                  'filter_games_only_actives')
    def test_process_consoles(self, mock_filter_games):
        console_mock = MagicMock()
        consoles_mock = [console_mock]
        processed_consoles = self.interactor.process_consoles(consoles_mock)
        console_mock.games = mock_filter_games(console_mock.games)
        result = console_mock
        assert processed_consoles == [result]

    def test_process_consoles_empty(self):
        console_mock = MagicMock()
        consoles_mock = [console_mock]
        processed_consoles = self.interactor.process_consoles(consoles_mock)
        assert processed_consoles == []

    @patch.object(GetAllConsolesActiveGamesInteractor, 'get_all_consoles')
    @patch.object(GetAllConsolesActiveGamesInteractor, 'process_consoles')
    @patch.object(GetAllConsolesActiveGamesInteractor, 'format_consoles')
    @patch(f'{prefix}.GetAllConsolesActiveGamesResponseModel')
    def test_run(self, response_model_mock,
                 format_consoles_mock,
                 process_consoles_mock,
                 get_all_consoles_mock):
        response = self.interactor.run()
        get_all_consoles_mock.assert_called()
        process_consoles_mock.assert_called_with(get_all_consoles_mock())
        response_model_mock.assert_called_with(format_consoles_mock())
        assert response == response_model_mock()

    @patch.object(GetAllConsolesActiveGamesInteractor,
                  'get_all_consoles',
                  side_effect=Exception('oops'))
    @patch.object(GetAllConsolesActiveGamesInteractor, 'process_consoles')
    @patch(f'{prefix}.GetAllConsolesActiveGamesResponseModel')
    def test_run_with_error(self, response_model_mock,
                            process_consoles_mock,
                            get_all_consoles_mock):
        with pytest.raises(GetAllConsolesActiveGamesException) as exc:
            self.interactor.run()
        assert 'Error during get all consoles active games: Exception:' \
               ' oops' in str(exc.value)
        response_model_mock.assert_not_called()
        process_consoles_mock.assert_not_called()
        get_all_consoles_mock.assert_called()

    def test_format_consoles(self):
        console_mock = MagicMock()
        consoles_mock = [console_mock]
        formated_consoles = self.interactor.format_consoles(consoles_mock)
        assert formated_consoles == [{
            "entity_id": console_mock.entity_id,
            "name": console_mock.name,
            "logo_path": console_mock.logo_path,
            "tag_name": console_mock.tag_name,
            "games": console_mock.to_json()['games']
        }]
