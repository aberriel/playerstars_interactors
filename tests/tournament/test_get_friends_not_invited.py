from playerstars_interactors.tournament.get_friends_not_invited import (
    GetFriendsNotInvitedAdapters, GetFriendsNotInvitedError,
    GetFriendsNotInvitedInteractor, GetFriendsNotInvitedRequestModel,
    GetFriendsNotInvitedResponseModel
)
from playerstars_domain import \
    Console, Game, PlayerConsoles, GamePoints, Player
from tests.player.player_utils import player1, player2, console, tournament
from unittest.mock import MagicMock, patch
import pytest
import copy


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


expected_response = [{
    'entity_id': player1.entity_id,
    'name': player1.user.name,
    'photo': player1.user.profile_image,
    'nickname': player1.user.nickname,
    'tag_name': 'Leoplay4'
}, {
    'entity_id': player1.entity_id,
    'name': player1.user.name,
    'photo': player1.user.profile_image,
    'nickname': player1.user.nickname,
    'tag_name': 'Leoplay4'
}]
player_temp = copy.deepcopy(player1)
player_temp.consoles[0].console_id = '1'
console2 = Console(
    entity_id='c5a73eaa-9c87-4c32-9a49-05125fb79387',
    logo_path="/images/ss.png",
    name="Playstation 4",
    tag_name="Leoplay4",
    games=[
        Game(entity_id="6411df96-799b-4e6d-84f6-f277cff016e7",
             logo_path="images/sonic.jpg",
             name="teste",
             points=0,
             victories=0)
    ]
)
player_console = PlayerConsoles(
    console_id=console2.entity_id,
    game_points=[GamePoints(
        game_id=console2.games[0].entity_id
    )],
    tag_name=console2.tag_name
)
player_temp.consoles.append(player_console)

query_params = {
    'player_id': '123',
    'console_id': '1',
    'game_id': 'id1234'}


console_adapter_mock = MagicMock(
    get_by_id=MagicMock(return_value=console))
player_adapter_mock_1 = MagicMock(
    get_by_id=MagicMock(return_value=player_temp))
player_adapter_mock_2 = MagicMock(
    get_by_id=MagicMock(return_value=player2))
player_tournament_adapter_mock = MagicMock(
    get_by_id=MagicMock(return_value=tournament))


def get_interactor():
    request = GetFriendsNotInvitedRequestModel('player123', 'tournament123')
    adapters = GetFriendsNotInvitedAdapters(
        player_adapter=player_adapter_mock_1,
        player_tournament_adapter=player_tournament_adapter_mock,
        console_adapter=console_adapter_mock
    )
    interactor = GetFriendsNotInvitedInteractor(
        request=request,
        adapters=adapters)
    return interactor


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_players_by_console_game(boto3):
    interactor = get_interactor()
    response = interactor.filter_by_console_game(
        players_ids=['1234', '5678'],
        tournament=tournament,
        console=console
    )
    assert isinstance(response, list)
    assert isinstance(response[0], Player)
    assert isinstance(response[1], Player)


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_get_tag_name(boto3):
    interactor = get_interactor()
    response = interactor.get_tag_name(
        player=player_temp,
        console_id=player_temp.consoles[0].console_id
    )
    assert isinstance(response, str)
    assert response == 'Leoplay4'


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_format_friends(boto3):
    interactor = get_interactor()
    response = interactor.format_friends(
        players=[player_temp, player1],
        console_id='1'
    )
    assert isinstance(response, list)
    assert response == [{
        'entity_id': '1',
        'name': 'Anselmo Lira',
        'nickname': 'player1',
        'photo': 'iVBORw0KGgoAAAANSUhEUgAA',
        'tag_name': 'Leoplay4'
    }, {
        'entity_id': '1',
        'name': 'Anselmo Lira',
        'nickname': 'player1',
        'photo': 'iVBORw0KGgoAAAANSUhEUgAA',
        'tag_name': 'Leoplay4'
    }]


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_filter_already_invited(boto3):
    interactor = get_interactor()
    response = interactor.filter_already_invited(
        friends=[player_temp, player1],
        tournament=tournament
    )
    assert isinstance(response, list)
    assert len(response) == 2


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_run(boto3):
    interactor = get_interactor()
    interactor.filter_by_console_game = MagicMock()
    interactor.filter_already_invited = MagicMock()
    interactor.format_friends = MagicMock()
    response = interactor.run()
    assert isinstance(response, GetFriendsNotInvitedResponseModel)
    assert response()
    interactor.adapters.player_tournament_adapter.get_by_id.\
        assert_called_once_with(interactor.request.tournament_id)
    interactor.adapters.player_adapter.get_by_id.assert_called_with(
        interactor.request.player_id
    )
    interactor.adapters.console_adapter.get_by_id.assert_called_once_with(
        tournament.console.entity_id
    )
    interactor.filter_by_console_game.assert_called_once_with(
        players_ids=player_temp.favorites,
        console=console,
        tournament=tournament
    )
    interactor.filter_already_invited.assert_called_once_with(
        interactor.filter_by_console_game(), tournament
    )
    interactor.format_friends.assert_called_once_with(
        interactor.filter_already_invited(), tournament.console.entity_id
    )


@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_tournament_not_found(boto3):
    interactor = get_interactor()
    interactor.adapters.player_tournament_adapter.get_by_id = MagicMock(
        return_value=None
    )
    with pytest.raises(GetFriendsNotInvitedError) as excinfo:
        interactor.run()
    assert 'Tournament tournament123 not found in player tournaments' \
           in str(excinfo.value)
