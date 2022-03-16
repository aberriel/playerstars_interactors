from playerstars_adapters import PlayerAdapter, ConsoleAdapter
from playerstars_interactors import \
    GetRankingByConsoleGameRequestModel, GetRankingByConsoleGameInteractor
from unittest.mock import patch
from tests.player.player_utils import (
    player2, player3, player1, console, player4, player5, player6)


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


expected_response = [
    {
        "position": 1,
        "profile_image": player1.user.profile_image,
        "user_name": player1.user.nickname,
        "victories": 10,
        "is_himself": False,
        "elo_rating": 5000
    }, {
        "position": 2,
        "profile_image": player2.user.profile_image,
        "user_name": player2.user.nickname,
        "victories": 40,
        "is_himself": False,
        "elo_rating": 4000
    }, {
        "position": 3,
        "profile_image": player3.user.profile_image,
        "user_name": player3.user.nickname,
        "victories": 30,
        "is_himself": True,
        "elo_rating": 3000
    }
]

query_params = {
    'console_id': '1',
    'game_id': 'f16c9f9a-9b22-4884-b890-bcc3294e91be'
}


@patch.object(PlayerAdapter, 'list_all',
              return_value=[player1, player2, player3])
@patch.object(ConsoleAdapter, 'get_by_id', return_value=console)
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_ranking_by_console_game(boto3,
                                     get_console,
                                     list_players):
    player_adapter = PlayerAdapter('player-test', 'localhost-test')
    console_adapter = ConsoleAdapter('console-test', 'localhost-test')
    request = GetRankingByConsoleGameRequestModel(query_params, '3')
    interactor = GetRankingByConsoleGameInteractor(
        request, player_adapter, console_adapter)
    response, range_data = interactor.run()
    assert isinstance(response, list)
    assert response == expected_response
    assert range_data.initial == 0
    assert range_data.final == 3
    assert range_data.total == 3
    assert range_data.unit == 'ranking'


@patch.object(PlayerAdapter, 'list_all',
              return_value=[])
@patch.object(ConsoleAdapter, 'get_by_id', return_value=console)
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_ranking_by_console_game_empty(boto3,
                                           get_console,
                                           list_players):
    player_adapter = PlayerAdapter('player-test')
    console_adapter = ConsoleAdapter('console-test')
    request = GetRankingByConsoleGameRequestModel(query_params, '2')
    interactor = GetRankingByConsoleGameInteractor(
        request, player_adapter, console_adapter)
    response, range_data = interactor.run()
    assert isinstance(response, list)
    assert response == []
    assert range_data.initial == 0
    assert range_data.final == 0
    assert range_data.total == 0
    assert range_data.unit == 'ranking'


query_params2 = {
    'console_id': '1',
    'game_id': 'f16c9f9a-9b22-4884-b890-bcc3294e91be',
    'pagination_page': 1,
    'pagination_per_page': 2
}

expected_response1 = [
    {
        "position": 1,
        "profile_image": player1.user.profile_image,
        "user_name": player1.user.nickname,
        "victories": 10,
        "is_himself": False,
        "elo_rating": 5000
    }, {
        "position": 2,
        "profile_image": player2.user.profile_image,
        "user_name": player2.user.nickname,
        "victories": 40,
        "is_himself": False,
        "elo_rating": 4000
    }, {
        'position': 3,
        'profile_image': 'iVBORw0KGgoAAAANSUhEUgAA',
        'user_name': 'player3',
        'victories': 30,
        'is_himself': True,
        'elo_rating': 3000
    }
]


@patch.object(PlayerAdapter, 'list_all',
              return_value=[player1, player2, player3])
@patch.object(ConsoleAdapter, 'get_by_id', return_value=console)
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_ranking_page_by_console_game(boto3,
                                          get_console,
                                          list_players):
    player_adapter = PlayerAdapter('player-test')
    console_adapter = ConsoleAdapter('console-test')
    request = GetRankingByConsoleGameRequestModel(query_params2, '3')
    interactor = GetRankingByConsoleGameInteractor(
        request, player_adapter, console_adapter)
    response, range_data = interactor.run()
    assert isinstance(response, list)
    assert response == expected_response1
    assert range_data.initial == 0
    assert range_data.final == 2
    assert range_data.total == 3
    assert range_data.unit == 'ranking'


expected_response2 = [
    {
        "position": 1,
        "profile_image": player1.user.profile_image,
        "user_name": player1.user.nickname,
        "victories": 10,
        "is_himself": False,
        "elo_rating": 5000
    }, {
        "position": 2,
        "profile_image": player2.user.profile_image,
        "user_name": player2.user.nickname,
        "victories": 40,
        "is_himself": False,
        "elo_rating": 4000
    }, {
        "position": 4,
        "profile_image": player4.user.profile_image,
        "user_name": player4.user.nickname,
        "victories": 5,
        "is_himself": True,
        "elo_rating": 2000
    }
]


@patch.object(PlayerAdapter, 'list_all',
              return_value=[player1, player2, player3, player4])
@patch.object(ConsoleAdapter, 'get_by_id', return_value=console)
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_ranking_page_by_console_game_2(boto3,
                                            get_console,
                                            list_players):
    player_adapter = PlayerAdapter('player-test')
    console_adapter = ConsoleAdapter('console-test')
    request = GetRankingByConsoleGameRequestModel(query_params2, '4')
    interactor = GetRankingByConsoleGameInteractor(
        request, player_adapter, console_adapter)
    response, range_data = interactor.run()
    assert isinstance(response, list)
    assert response == expected_response2
    assert range_data.initial == 0
    assert range_data.final == 2
    assert range_data.total == 4
    assert range_data.unit == 'ranking'


expected_response3 = [
    {
        "position": 3,
        "profile_image": player3.user.profile_image,
        "user_name": player3.user.nickname,
        "victories": 30,
        "is_himself": False,
        "elo_rating": 3000
    }, {
        "position": 4,
        "profile_image": player4.user.profile_image,
        "user_name": player4.user.nickname,
        "victories": 5,
        "is_himself": False,
        "elo_rating": 2000
    }, {
        "position": 5,
        "profile_image": player5.user.profile_image,
        "user_name": player5.user.nickname,
        "victories": 300,
        "is_himself": True,
        "elo_rating": 1500
    }
]

query_params3 = {
    'console_id': '1',
    'game_id': 'f16c9f9a-9b22-4884-b890-bcc3294e91be',
    'pagination_page': 2,
    'pagination_per_page': 2
}


@patch.object(PlayerAdapter, 'list_all',
              return_value=[player1, player2, player3, player4, player5])
@patch.object(ConsoleAdapter, 'get_by_id', return_value=console)
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_ranking_page_by_console_game_3(boto3,
                                            get_console,
                                            list_players):
    player_adapter = PlayerAdapter('player-test', 'localhost-test')
    console_adapter = ConsoleAdapter('console-test', 'localhost-test')
    request = GetRankingByConsoleGameRequestModel(query_params3, '5')
    interactor = GetRankingByConsoleGameInteractor(
        request, player_adapter, console_adapter)
    response, range_data = interactor.run()
    assert isinstance(response, list)
    assert response == expected_response3
    assert range_data.initial == 2
    assert range_data.final == 4
    assert range_data.total == 5
    assert range_data.unit == 'ranking'


expected_response4 = [
    {
        "position": 1,
        "profile_image": player1.user.profile_image,
        "user_name": player1.user.nickname,
        "victories": 10,
        "is_himself": False,
        "elo_rating": 5000
    }, {
        "position": 2,
        "profile_image": player2.user.profile_image,
        "user_name": player2.user.nickname,
        "victories": 40,
        "is_himself": False,
        "elo_rating": 4000
    }, {
        "position": 3,
        "profile_image": player3.user.profile_image,
        "user_name": player3.user.nickname,
        "victories": 30,
        "is_himself": False,
        "elo_rating": 3000
    }, {
        "position": 4,
        "profile_image": player4.user.profile_image,
        "user_name": player4.user.nickname,
        "victories": 5,
        "is_himself": False,
        "elo_rating": 2000
    }, {
        "position": 5,
        "profile_image": player5.user.profile_image,
        "user_name": player5.user.nickname,
        "victories": 300,
        "is_himself": True,
        "elo_rating": 1500
    }, {
        "position": 5,
        "profile_image": player6.user.profile_image,
        "user_name": player6.user.nickname,
        "victories": 30,
        "is_himself": False,
        "elo_rating": 1500
    }
]

query_params4 = {
    'console_id': '1',
    'game_id': 'f16c9f9a-9b22-4884-b890-bcc3294e91be',
    'pagination_page': 1,
    'pagination_per_page': 10
}


@patch.object(PlayerAdapter, 'list_all',
              return_value=[
                  player1, player2, player3, player4, player5, player6])
@patch.object(ConsoleAdapter, 'get_by_id', return_value=console)
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_ranking_page_by_console_game_4(boto3,
                                            get_console,
                                            list_players):
    player_adapter = PlayerAdapter('player-test', 'localhost-test')
    console_adapter = ConsoleAdapter('console-test', 'localhost-test')
    request = GetRankingByConsoleGameRequestModel(query_params4, '5')
    interactor = GetRankingByConsoleGameInteractor(
        request, player_adapter, console_adapter)
    response, range_data = interactor.run()
    assert isinstance(response, list)
    assert response == expected_response4
    assert range_data.initial == 0
    assert range_data.final == 6
    assert range_data.total == 6
    assert range_data.unit == 'ranking'
