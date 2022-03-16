from collections import namedtuple
from playerstars_adapters import ConsoleAdapter, PlayerAdapter
from playerstars_interactors.player.get_player_consoles import (
    GetPlayerConsolesInteractor,
    GetPlayerConsolesRequestModel,
    GetPlayerConsolesResponseModel)
from pytest import fixture
from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest


prefix = 'playerstars_interactors.player.get_player_consoles'


def test_get_player_console_request_model():
    player_id_mock = MagicMock()
    request_model = GetPlayerConsolesRequestModel(player_id_mock)
    assert request_model
    assert request_model.player_id == player_id_mock


def test_get_player_console_response_model():
    consoles_mock = MagicMock()
    response_model = GetPlayerConsolesResponseModel(consoles_mock)
    assert response_model.consoles == consoles_mock


def test_get_player_console_response_model__call():
    console_mock = MagicMock()
    consoles_mock = [console_mock]
    response_model = GetPlayerConsolesResponseModel(consoles_mock)
    assert response_model() == consoles_mock


def test_get_player_console_response_model__call_empty():
    response_model = GetPlayerConsolesResponseModel(None)
    call_result = response_model()
    assert call_result == []


Factory = namedtuple('Factory', 'interactor, mock_request, '
                                'mock_console_adapter, mock_player_adapter')


@fixture(scope='class')
def interactor_fixture(request):
    def factory(request: GetPlayerConsolesRequestModel = MagicMock(),
                console_adapter: ConsoleAdapter = MagicMock(),
                player_adapter: PlayerAdapter = MagicMock()):
        interactor = GetPlayerConsolesInteractor(
            console_adapter=console_adapter,
            player_adapter=player_adapter,
            request=request)
        return Factory(interactor, request, console_adapter, player_adapter)
    request.cls.factory = factory


@pytest.mark.usefixtures('interactor_fixture')
class TestGetPlayerConsolesInteractor(TestCase):
    def setUp(self):
        fac = TestGetPlayerConsolesInteractor.factory()
        self.interactor: GetPlayerConsolesInteractor = fac.interactor
        self.mock_console_adapter = fac.mock_console_adapter
        self.mock_player_adapter = fac.mock_player_adapter
        self.mock_request = fac.mock_request

    def tearDown(self):
        pass

    def test_init(self):
        assert self.interactor.request == self.mock_request
        assert self.interactor.console_adapter == self.mock_console_adapter
        assert self.interactor.player_adapter == self.mock_player_adapter

    def make_game_list_1(self):
        game_1 = MagicMock()
        game_1.entity_id = '1'
        game_1.name = 'game_1'
        game_1.logo_path = 'abc'
        game_1.active = True
        game_2 = MagicMock()
        game_2.entity_id = '2'
        game_2.name = 'game_2'
        game_2.logo_path = 'def'
        game_2.active = True
        game_3 = MagicMock()
        game_3.entity_id = '3'
        game_3.name = 'game_3'
        game_3.logo_path = 'ghi'
        game_3.active = True
        return [game_1, game_2, game_3]

    def make_game_list_2(self):
        game_1 = MagicMock()
        game_1.entity_id = '1'
        game_1.name = 'game_1'
        game_1.active = False
        game_1.logo_path = 'abc'
        game_2 = MagicMock()
        game_2.entity_id = '2'
        game_2.name = 'game_2'
        game_2.active = True
        game_2.logo_path = 'def'
        game_3 = MagicMock()
        game_3.entity_id = '3'
        game_3.name = 'game_3'
        game_3.active = False
        game_3.logo_path = 'ghi'
        return [game_1, game_2, game_3]

    def make_game_points_list(self):
        game_points_1 = MagicMock()
        game_points_1.game_id = '1'
        game_points_1.victories = 1
        game_points_2 = MagicMock()
        game_points_2.game_id = '3'
        game_points_2.victories = 3
        return [game_points_1, game_points_2]

    def test_format_games(self):
        format_result = self.interactor.format_games(
            games=self.make_game_list_1(),
            game_points=self.make_game_points_list())
        assert format_result == [
            {
                'entity_id': '1',
                'victories': 1,
                'logo_path': 'abc',
                'name': 'game_1'
            },
            {
                'entity_id': '3',
                'victories': 3,
                'logo_path': 'ghi',
                'name': 'game_3'
            }
        ]

    def test_format_games_inactive_game(self):
        format_result = self.interactor.format_games(
            games=self.make_game_list_2(),
            game_points=self.make_game_points_list())
        assert format_result == []

    @patch.object(GetPlayerConsolesInteractor, 'format_games',
                  return_value=[MagicMock()])
    def test_format_consoles(self, format_games_mock):
        console_mock = MagicMock()
        consoles_mock = [console_mock]
        get_by_id_mock = MagicMock()
        self.mock_console_adapter.get_by_id = get_by_id_mock
        console_list = self.interactor.format_consoles(consoles_mock)

        get_by_id_mock.assert_called_with(console_mock.console_id)
        format_games_mock.assert_called_with(get_by_id_mock().games,
                                             console_mock.game_points)
        assert console_list == [{
            'entity_id': get_by_id_mock().entity_id,
            'name': get_by_id_mock().name,
            'logo_path': get_by_id_mock().logo_path,
            'tag_name': console_mock.tag_name,
            'games': format_games_mock()
        }]

    @patch.object(GetPlayerConsolesInteractor, 'format_games', return_value=[])
    def test_format_consoles_with_console_without_games(
            self, format_games_mock):
        console_mock = MagicMock()
        consoles_mock = [console_mock]
        get_by_id_mock = MagicMock()
        self.mock_console_adapter.get_by_id = get_by_id_mock
        console_list = self.interactor.format_consoles(consoles_mock)

        get_by_id_mock.assert_called_with(console_mock.console_id)
        format_games_mock.assert_called_with(get_by_id_mock().games,
                                             console_mock.game_points)
        assert console_list == []

    @patch.object(GetPlayerConsolesInteractor, 'format_consoles')
    @patch(f'{prefix}.GetPlayerConsolesResponseModel')
    def test_run(self, response_model_mock, format_consoles_mock):
        get_by_id_mock = MagicMock()
        self.interactor.player_adapter.get_by_id = get_by_id_mock
        response = self.interactor.run()
        get_by_id_mock.assert_called_with(self.mock_request.player_id)
        format_consoles_mock.assert_called_once_with(get_by_id_mock().consoles)
        response_model_mock.assert_called_with(format_consoles_mock())
        assert response == response_model_mock()()

    @patch.object(GetPlayerConsolesInteractor, 'format_consoles')
    @patch(f'{prefix}.GetPlayerConsolesResponseModel')
    def test_run_not_player(self, response_model_mock, format_consoles_mock):
        get_by_id_mock = MagicMock(return_value=None)
        self.interactor.player_adapter.get_by_id = get_by_id_mock
        response = self.interactor.run()
        response_model_mock.assert_not_called()
        format_consoles_mock.assert_not_called()
        get_by_id_mock.assert_called()
        assert response == []
