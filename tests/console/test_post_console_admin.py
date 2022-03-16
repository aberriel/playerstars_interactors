from datetime import date
from playerstars_domain import (
    Console, Game, GamePoints, Player,
    PlayerConsoles, PlayerStatus, User)
from playerstars_interactors import (
    PostConsoleAdminException,
    PostConsoleAdminInteractor,
    PostConsoleAdminRequestModel)
from playerstars_interactors.utils.rights_utils import \
    AccessDeniedAdminException
from pytest import raises
from unittest.mock import MagicMock, Mock, patch


def make_game_1():
    return Game(
        entity_id='351c0f7e-9180-47a5-8ca3-0a654161697f',
        name='Sonic The Hedgehog',
        logo_path='http://s3.aws.com/sonic.jpg'
    )


def make_game_2():
    return Game(
        entity_id='9204912c-30f9-4c37-b025-a4c06338985c',
        name='Alex Kidd',
        logo_path='http://s3.aws.com/alexkidd.jog'
    )


def make_game_3():
    return Game(
        entity_id='753a64bc-6879-4e9a-b10d-48e0bb04d9c5',
        name='Super Mario',
        logo_path='http://s3.aws.com/mario.jpg'
    )


def make_console_1():
    game_list = [make_game_1(), make_game_2(), make_game_3()]
    return Console(
        entity_id='f77f1160-1470-4ce0-a77c-dc9058bb6f15',
        name='Mega Drive',
        logo_path='http://s3.aws.com/megadrive.jpg',
        games=game_list
    )


def make_console_2():
    game_list = [make_game_1(), make_game_2(), make_game_3()]
    return Console(
        entity_id='2610633a-b252-41e9-b579-a49af8d500ed',
        name='Super Nintendo',
        logo_path='http://s3.aws.com/supernintendo.jpg',
        games=game_list
    )


def make_console_list():
    return [make_console_1(), make_console_2()]


def make_player_console_list():
    game_points_list = [
        GamePoints(make_game_1(), 0),
        GamePoints(make_game_2(), 0),
        GamePoints(make_game_3(), 0)]
    return [
        PlayerConsoles(
            console_id=make_console_1().entity_id,
            tag_name='tag#1',
            game_points=game_points_list),
        PlayerConsoles(
            console_id=make_console_2().entity_id,
            tag_name='tag#2',
            game_points=game_points_list)]


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
                    consoles=make_player_console_list(),
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
                    consoles=make_player_console_list(),
                    player_status=PlayerStatus.AVAILABLE,
                    is_admin=False)
    return player


def make_request():
    return {
        'player_id': '1235',
        'name': 'Playestation 4',
        'logo_path': 'data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAA'
                     'AABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAA'
                     'ABJRU5ErkJggg==',
        'games': [
            {
                'entity_id': '351c0f7e-9180-47a5-8ca3-0a654161697f',
                'name': 'Sonic The Hedgehog',
                'logo_path': 'http://s3.aws.com/sonic.jpg'
            },
            {
                'entity_id': '9204912c-30f9-4c37-b025-a4c06338985c',
                'name': 'Alex Kidd',
                'logo_path': 'http://s3.aws.com/alexkidd.jog'
            },
            {
                'entity_id': '753a64bc-6879-4e9a-b10d-48e0bb04d9c5',
                'name': 'Super Mario',
                'logo_path': 'http://s3.aws.com/mario.jpg'
            }
        ]
    }


def make_request_same_name():
    request = make_request()
    request['name'] = 'Mega Drive'
    return request


def make_request_not_admin():
    request = make_request()
    request['player_id'] = 'pl11'
    return request


console_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    list_all=MagicMock(return_value=make_console_list()),
    save=MagicMock(return_value='83c596b1-8366-4fbc-978c-3d629dfac7ea'))
console_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    list_all=MagicMock(return_value=make_console_list()),
    save=MagicMock(side_effect=Exception('oops')))
player_adapter_mock_admin = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_admin()))
player_adapter_mock_not_admin = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_not_admin()))


@patch('playerstars_interactors.console.post_console_admin.uuid4')
@patch('boto3.resource')
@patch('boto3.client')
def test_post_console_admin(boto_client, boto_resource, uuid_mock):
    uuid_mock.utcnow = Mock(
        return_value='83c596b1-8366-4fbc-978c-3d629dfac7ea')
    console_adapter_mock.save.call_count = 0
    request = PostConsoleAdminRequestModel(make_request())
    interactor = PostConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')
    response = interactor.run()

    console_adapter_mock.save.assert_called_once()
    assert response == '83c596b1-8366-4fbc-978c-3d629dfac7ea'


@patch('playerstars_interactors.console.post_console_admin.uuid4')
@patch('boto3.resource')
@patch('boto3.client')
def test_post_console_same_name(boto_client, boto_resource, uuid_mock):
    uuid_mock.utcnow = Mock(
        return_value='83c596b1-8366-4fbc-978c-3d629dfac7ea')
    request = PostConsoleAdminRequestModel(make_request_same_name())
    interactor = PostConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')

    with raises(PostConsoleAdminException) as exc:
        interactor.run()
    assert 'Error during console creation: ' \
           'Exists a console with same name and ' \
           'has id f77f1160-1470-4ce0-a77c-dc9058bb6f15' in str(exc.value)


@patch('playerstars_interactors.console.post_console_admin.uuid4')
@patch('boto3.resource')
@patch('boto3.client')
def test_post_console_not_admin(boto_client, boto_resource, uuid_mock):
    uuid_mock.utcnow = Mock(
        return_value='83c596b1-8366-4fbc-978c-3d629dfac7ea')
    request = PostConsoleAdminRequestModel(make_request_not_admin())
    interactor = PostConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_not_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')

    with raises(AccessDeniedAdminException) as exc:
        interactor.run()
    assert "Error during console creation: " \
           "Player dudu123 isn't admin" in str(exc.value)


@patch('playerstars_interactors.console.post_console_admin.uuid4')
@patch('boto3.resource')
@patch('boto3.client')
def test_post_console_raises(boto_client, boto_resource, uuid_mock):
    uuid_mock.utcnow = Mock(
        return_value='83c596b1-8366-4fbc-978c-3d629dfac7ea')
    request = PostConsoleAdminRequestModel(make_request())
    interactor = PostConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock_raises,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')

    with raises(PostConsoleAdminException) as exc:
        interactor.run()
    assert 'Error during console creation: oops' in str(exc.value)
