from datetime import date
from playerstars_adapters import ConsoleAdapter, PlayerAdapter
from playerstars_domain import (
    Console,
    Game,
    GamePoints,
    Player,
    PlayerConsoles,
    PlayerStatus,
    User
)
from playerstars_interactors import (
    GetConsoleByIdAdminException,
    GetConsoleByIdAdminInteractor,
    GetConsoleByIdAdminRequestModel
)
from playerstars_interactors.utils.rights_utils import \
    AccessDeniedAdminException
from pytest import raises
from unittest.mock import patch


def make_game_1():
    return Game(
        entity_id='8afad7e1-c572-44a5-b46c-50be45cc0472',
        name='Need for Speed Underground 2',
        logo_path='/images/nfsu2.jpg')


def make_game_2():
    return Game(
        entity_id='04324811-696f-4eb0-9f90-28ae17e61c28',
        name='Sonic II',
        logo_path='/images/sonic2.jpg')


def make_games():
    return [make_game_1(), make_game_2()]


def make_console():
    return Console(
        entity_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        name='Playstation II',
        logo_path='/images/ps2.jpg',
        games=make_games())


def make_player_consoles():
    game_points = [
        GamePoints(make_game_1().entity_id, 0),
        GamePoints(make_game_2().entity_id, 0)]
    return [PlayerConsoles(make_console().entity_id, 'tag#1', game_points)]


def make_player_admin():
    user = User(name='Anselmo Lira',
                email='anselmo.lira@stormsec.com.br',
                street='Avenida Brasil',
                street_number='500',
                street_complement='apt 607',
                neighborhood='pechinchao',
                city='Hogwarts',
                date_birth=date(1986, 12, 16),
                state='Dartmoor',
                country='England',
                postal_code='634',
                phone_number='5521991996565',
                cpf='123.456.789-01',
                nickname='lira1')
    player = Player(user=user,
                    consoles=make_player_consoles(),
                    entity_id='1235',
                    is_admin=True)
    return player


def make_player_not_admin():
    user = User(name='Felipe Duarte',
                email='f.duarte@stormsec',
                date_birth=date(1990, 6, 5),
                street='Avenida Brasil',
                street_number='500',
                street_complement='apt 607',
                neighborhood='pechinchao',
                city='Rio de Janeiro',
                state='Rio de Janeiro',
                country='Brasil',
                postal_code='25520-012',
                phone_number='(21) 98144-1317',
                cpf='998.776.554-32',
                nickname='dudu123')
    player = Player(entity_id='pl11',
                    user=user,
                    consoles=make_player_consoles(),
                    player_status=PlayerStatus.AVAILABLE,
                    is_admin=False)
    return player


def make_request_model():
    return {
        'player_id': 'q1w2e3',
        'console_id': 'aqswde1'
    }


@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.console_adapter.ConsoleAdapter.get_by_id',
       return_value=make_console())
@patch('playerstars_adapters.player_adapter.PlayerAdapter.get_by_id',
       return_value=make_player_admin())
@patch('boto3.resource')
def test_get_console_by_id_admin(boto_resource,
                                 player_data,
                                 console_data,
                                 create_table_player,
                                 create_table_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsoleByIdAdminRequestModel(make_request_model())
    interactor = GetConsoleByIdAdminInteractor(
        request=request,
        player_adapter=player_adapter,
        console_adapter=console_adapter)
    response = interactor.run()
    assert response == make_console().to_json()


@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.console_adapter.ConsoleAdapter.get_by_id',
       return_value=None)
@patch('playerstars_adapters.player_adapter.PlayerAdapter.get_by_id',
       return_value=make_player_admin())
@patch('boto3.resource')
def test_get_console_by_id_admin_not_found(boto_resource,
                                           player_data,
                                           console_data_none,
                                           create_table_player,
                                           create_table_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsoleByIdAdminRequestModel(make_request_model())
    interactor = GetConsoleByIdAdminInteractor(
        request=request,
        player_adapter=player_adapter,
        console_adapter=console_adapter)
    response = interactor.run()
    assert not response


@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.player_adapter.PlayerAdapter.get_by_id',
       return_value=make_player_not_admin())
@patch('boto3.resource')
def test_get_console_by_id_admin_not_admin(boto_resource,
                                           player_data,
                                           create_table_player,
                                           create_table_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsoleByIdAdminRequestModel(make_request_model())
    interactor = GetConsoleByIdAdminInteractor(
        request=request,
        player_adapter=player_adapter,
        console_adapter=console_adapter)
    with raises(AccessDeniedAdminException) as exc:
        interactor.run()
    assert "Error during recovery console: " \
           "Player dudu123 isn't admin" in str(exc.value)


@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, 'get_by_id', side_effect=Exception('oops'))
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('boto3.resource')
def test_get_console_by_id_admin_raises(boto_resource,
                                        create_table_player,
                                        get_by_id_player,
                                        create_table_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsoleByIdAdminRequestModel(make_request_model())
    interactor = GetConsoleByIdAdminInteractor(
        request=request,
        player_adapter=player_adapter,
        console_adapter=console_adapter)
    with raises(GetConsoleByIdAdminException) as exc:
        interactor.run()
    assert "Error during recovery console: oops" in str(exc.value)
