from datetime import date, datetime
from playerstars_adapters import (
    ConsoleAdapter,
    PlayerAdapter
)
from playerstars_domain import (
    Console,
    Game,
    Player,
    PlayerStatus,
    User
)
from playerstars_interactors import (
    GetConsolesAdminException,
    GetConsolesAdminInteractor,
    GetConsolesAdminRequestModel
)
from playerstars_interactors.utils.rights_utils import \
    AccessDeniedAdminException
from pytest import raises
from unittest.mock import patch


def make_game_1():
    return Game(
        entity_id='04324811-696f-4eb0-9f90-28ae17e61c28',
        name='Sonic II',
        logo_path='/images/sonic2.jpg')


def make_game_2():
    return Game(
        entity_id='8afad7e1-c572-44a5-b46c-50be45cc0472',
        name='Need for Speed Underground 2',
        logo_path='/images/nfsu2.jpg')


def make_console_1():
    game_1 = make_game_1()
    game_2 = make_game_2()
    return Console(
        entity_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        name='Playstation II',
        logo_path='/images/ps2.jpg',
        games=[game_1, game_2])


def make_console_2():
    game_1 = make_game_1
    return Console(
        entity_id='ca978ce4-fc2a-4cd2-95e2-e96db8891d8d',
        name='Mega Drive III',
        logo_path='/images/megadrive3.jpg',
        games=[game_1])


def make_console_list():
    return [make_console_1(), make_console_2()]


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
                    consoles=make_console_list(),
                    entity_id='1235',
                    is_admin=True)
    return player


def make_player_not_admin():
    user = User(name='Felipe Duarte',
                email='f.duarte@stormsec',
                date_birth=datetime(1990, 6, 5),
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
                    consoles=make_console_list(),
                    player_status=PlayerStatus.AVAILABLE,
                    is_admin=False)
    return player


# noinspection PyUnusedLocal,PyUnusedLocal
@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(ConsoleAdapter, 'list_all', return_value=make_console_list())
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.player_adapter.PlayerAdapter.get_by_id',
       return_value=make_player_admin())
@patch('boto3.resource')
def test_get_consoles_admin(boto_resource,
                            player_data,
                            create_table_player,
                            list_all_console,
                            create_table_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsolesAdminRequestModel('1235')
    interactor = GetConsolesAdminInteractor(
        console_adapter=console_adapter,
        player_adapter=player_adapter,
        request=request)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == [
        make_console_1().to_json(),
        make_console_2().to_json()
    ]


# noinspection PyUnusedLocal,PyUnusedLocal
@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(ConsoleAdapter, 'list_all', return_value=[])
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.player_adapter.PlayerAdapter.get_by_id',
       return_value=make_player_admin())
@patch('boto3.resource')
def test_get_consoles_admin_empty(boto_resource,
                                  player_data,
                                  create_table_player,
                                  list_all_empty_console,
                                  create_table_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsolesAdminRequestModel('1235')
    interactor = GetConsolesAdminInteractor(
        console_adapter=console_adapter,
        player_adapter=player_adapter,
        request=request)
    response = interactor.run()
    assert isinstance(response, list)
    assert response == []


# noinspection PyUnusedLocal,PyUnusedLocal
@patch.object(ConsoleAdapter, 'list_all', return_value=[])
@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.player_adapter.PlayerAdapter.get_by_id',
       return_value=make_player_not_admin())
@patch('boto3.resource')
def test_get_consoles_admin_not_admin(boto_resource,
                                      player_data,
                                      create_table_player,
                                      create_table_console,
                                      list_all_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsolesAdminRequestModel('pl11')
    interactor = GetConsolesAdminInteractor(
        console_adapter=console_adapter,
        player_adapter=player_adapter,
        request=request)

    with raises(AccessDeniedAdminException) as exc:
        interactor.run()
    assert "Error during recovery all consoles: " \
           "Player dudu123 isn't admin" in str(exc.value)


# noinspection PyUnusedLocal,PyUnusedLocal
@patch.object(ConsoleAdapter, 'list_all', side_effect=Exception('oops'))
@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(PlayerAdapter, '_create_table_if_dont_exists')
@patch('playerstars_adapters.player_adapter.PlayerAdapter.get_by_id',
       return_value=make_player_admin())
@patch('boto3.resource')
def test_get_consoles_admin_raises(boto_resource,
                                   player_data,
                                   create_table_player,
                                   create_table_console,
                                   list_all_console):
    console_adapter = ConsoleAdapter('console-table', 'localhost')
    player_adapter = PlayerAdapter('player-table', 'localhost')
    request = GetConsolesAdminRequestModel('1235')
    interactor = GetConsolesAdminInteractor(
        request=request,
        console_adapter=console_adapter,
        player_adapter=player_adapter)

    with raises(GetConsolesAdminException) as exc:
        interactor.run()
    assert "Error during recovery all consoles: oops" in str(exc.value)
