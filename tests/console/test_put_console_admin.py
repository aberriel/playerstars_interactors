from datetime import date
from playerstars_domain import (
    Console, Game, GamePoints,
    Player, PlayerConsoles, PlayerStatus,
    User)
from playerstars_interactors import (
    PutConsoleAdminException,
    PutConsoleAdminInteractor,
    PutConsoleAdminRequestModel)
from playerstars_interactors.utils.rights_utils import \
    AccessDeniedAdminException
from pytest import raises
from unittest.mock import MagicMock, patch


def make_game_1():
    return Game(
        entity_id='8afad7e1-c572-44a5-b46c-50be45cc0472',
        name='Need for Speed Underground 2',
        logo_path='http://s3.aws.com/images/nfsu2.jpg')


def make_game_2():
    return Game(
        entity_id='04324811-696f-4eb0-9f90-28ae17e61c28',
        name='Sonic II',
        logo_path='http://s3.aws.com/images/sonic2.jpg')


def make_games():
    return [make_game_1(), make_game_2()]


def make_console():
    return Console(
        entity_id='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        name='Playstation II',
        logo_path='http://s3.aws.com/images/ps2.jpg',
        games=make_games())


def make_player_consoles():
    game_points = [GamePoints(make_game_1().entity_id, 0),
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


def make_request_put_console():
    return {
        'player_id': '1235',
        'entity_id': 'd5404939-8b68-4d70-bd15-b7080ef7cd51',
        'name': 'Playstation II',
        'logo_path': 'http://s3.aws.com/images/ps2.jpg',
        'games': [
            {
                'entity_id': '8afad7e1-c572-44a5-b46c-50be45cc0472',
                'name': 'Need for Speed Underground 2',
                'logo_path': 'http://s3.aws.com/images/nfsu2.jpg'
            }
        ]
    }


def make_request_change_console_logo():
    return {
        'player_id': '1235',
        'entity_id': 'd5404939-8b68-4d70-bd15-b7080ef7cd51',
        'name': 'Playstation II',
        'logo_path': 'data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAA'
                     'AABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAA'
                     'ABJRU5ErkJggg==',
        'games': [
            {
                'entity_id': '8afad7e1-c572-44a5-b46c-50be45cc0472',
                'name': 'Need for Speed Underground 2',
                'logo_path': 'http://s3.aws.com/images/nfsu2.jpg'
            }
        ]
    }


def make_request_change_game_logo():
    return {
        'player_id': '1235',
        'entity_id': 'd5404939-8b68-4d70-bd15-b7080ef7cd51',
        'name': 'Playstation II',
        'logo_path': 'http://s3.aws.com/images/ps2.jpg',
        'games': [
            {
                'entity_id': '8afad7e1-c572-44a5-b46c-50be45cc0472',
                'name': 'Need for Speed Underground 2',
                'logo_path':
                    'data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAA'
                    'AABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAA'
                    'ABJRU5ErkJggg=='
            }
        ]
    }


def make_request_put_console_not_admin():
    request_data = make_request_put_console()
    request_data['player_id'] = 'dudu123'
    return request_data


console_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_console()),
    save=MagicMock(return_value='d5404939-8b68-4d70-bd15-b7080ef7cd51'))
console_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_console()),
    save=MagicMock(side_effect=Exception('oops')))
player_adapter_mock_admin = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_admin()))
player_adapter_mock_not_admin = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_player_not_admin()))


@patch('playerstars_interactors.console.put_console_admin.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/logo.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_update_entity_logo_path(client, resource, upload_photo):
    request = PutConsoleAdminRequestModel(
        json_data=make_request_put_console())
    interactor = PutConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')
    interactor.new_console = make_console()

    interactor.update_entity_logo_path(
        raw_logo_path='http://s3.aws.com/images/logo.jpg',
        unique_name='q1w2e3')
    assert upload_photo.call_count == 0

    interactor.update_entity_logo_path(
        raw_logo_path='data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAA'
                      'ABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAAB'
                      'JRU5ErkJggg==',
        unique_name='d5404939-8b68-4d70-bd15-b7080ef7cd51')
    assert upload_photo.call_count == 1
    upload_photo.assert_called_with(
        sent_image='data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABC'
                   'AYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5Er'
                   'kJggg==',
        unique_name='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        s3_bucket_name='bucket_name',
        s3_bucket_url='bucket_url')


@patch('playerstars_interactors.console.put_console_admin.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/logo.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_put_console_admin(client, resource, upload_photo):
    console_adapter_mock.save.call_count = 0
    request = PutConsoleAdminRequestModel(make_request_put_console())
    interactor = PutConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')
    interactor.run()

    console_adapter_mock.save.assert_called_once()
    assert len(interactor.new_console.games) == 1
    assert upload_photo.call_count == 0


@patch('playerstars_interactors.console.put_console_admin.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/logo.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_upload_image_new_logo_console(client, resource, upload_photo):
    console_adapter_mock.save.call_count = 0
    request = PutConsoleAdminRequestModel(make_request_change_console_logo())
    interactor = PutConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')
    interactor.run()

    console_adapter_mock.save.assert_called_once()
    assert upload_photo.call_count == 1
    assert len(interactor.new_console.games) == 1
    upload_photo.assert_called_with(
        sent_image='data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB'
                   'CAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5'
                   'ErkJggg==',
        unique_name='d5404939-8b68-4d70-bd15-b7080ef7cd51',
        s3_bucket_name='bucket_name',
        s3_bucket_url='bucket_url')


@patch('playerstars_interactors.console.put_console_admin.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/logo.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_upload_image_if_new_logo_game(client, resource, upload_photo):
    console_adapter_mock.save.call_count = 0
    request = PutConsoleAdminRequestModel(make_request_change_game_logo())
    interactor = PutConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')
    interactor.run()

    console_adapter_mock.save.assert_called_once()
    assert upload_photo.call_count == 1
    assert len(interactor.new_console.games) == 1
    upload_photo.assert_called_with(
        sent_image='data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB'
                   'CAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5'
                   'ErkJggg==',
        unique_name='8afad7e1-c572-44a5-b46c-50be45cc0472',
        s3_bucket_name='bucket_name',
        s3_bucket_url='bucket_url')


@patch('boto3.resource')
@patch('boto3.client')
def test_put_console_admin_not_admin(boto_client, boto_resource):
    request = PutConsoleAdminRequestModel(
        make_request_put_console_not_admin())
    interactor = PutConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock,
        player_adapter=player_adapter_mock_not_admin,
        s3_bucket_url='bucket_url',
        s3_bucket_name='bucket_name')
    with raises(AccessDeniedAdminException) as exc:
        interactor.run()
    assert "Error during console update: " \
           "Player dudu123 isn't admin" in str(exc.value)


@patch('playerstars_interactors.utils.upload_photos.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/logo.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_put_console_admin_raises(client, resource, upload_photo):
    request = PutConsoleAdminRequestModel(make_request_put_console())
    interactor = PutConsoleAdminInteractor(
        request=request,
        console_adapter=console_adapter_mock_raises,
        player_adapter=player_adapter_mock_admin,
        s3_bucket_name='bucket_name',
        s3_bucket_url='bucket_url')
    with raises(PutConsoleAdminException) as exc:
        interactor.run()
    assert 'Error during console update: oops' in str(exc.value)
