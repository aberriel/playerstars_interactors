import copy
from collections import namedtuple
from unittest.mock import MagicMock, patch

from playerstars_adapters import ConsoleAdapter
from playerstars_domain import Player
from pytest import fixture

from playerstars_interactors import (
    BasicPostRequestModel,
    PostPlayerConsoleDataInteractor,
    PostPlayerAcceptTermsInteractor, PostPlayerInteractor)
from tests.player.player_utils import post_data, console_data

console_adapter = MagicMock(
    get_by_id=MagicMock(return_value=console_data))

post_data_temp = copy.deepcopy(post_data)
del post_data_temp['consoles']
post_data_temp['user']['date_birth'] = '1997-11-11'

player_adapter_post_player = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=Player.from_json(post_data_temp)))


@patch('playerstars_interactors.utils.upload_photos.boto3')
@patch.object(ConsoleAdapter, '_create_table_if_dont_exists')
@patch.object(ConsoleAdapter, 'get_by_id',
              return_value=console_data)
@patch('boto3.resource')
def test_post_console_data_player(boto_resource,
                                  get_by_id_console,
                                  create_table_console,
                                  boto3):
    console_adapter = ConsoleAdapter("table-test", "localhost-test")
    post_data_console = {
        "entity_id": '1',
        "consoles": [{
            "entity_id": '1',
            "tag_name": "Leoplay4"
        }]

    }
    request = BasicPostRequestModel(post_data_console)
    interactor = PostPlayerConsoleDataInteractor(
        request, player_adapter_post_player, console_adapter, Player)
    player = interactor._init_entity()
    assert player.to_json()['consoles'] == [{
        "console_id": '1',
        "tag_name": "Leoplay4",
        "game_points": [{
            "game_id": '123',
            "victories": 0,
            "elo_rating": 1500
        }]
    }]


post_data_temp = copy.deepcopy(post_data)
post_data_temp['user']['date_birth'] = '1997-11-11'


@patch('playerstars_interactors.utils.upload_photos.boto3')
@patch('boto3.resource')
def test_post_accept_terms_player(boto_resource, boto3):
    post_data = {
        "entity_id": "id123",
        "terms": True}
    request = BasicPostRequestModel(post_data)
    interactor = PostPlayerAcceptTermsInteractor(
        request=request,
        adapter_instance=player_adapter_post_player,
        entity_class=Player)
    player = interactor._init_entity()
    assert player.terms


@fixture
def interactor_factory():
    def factory(mock_request=MagicMock(),
                mock_adapter=MagicMock(),
                mock_console_adapter=MagicMock(),
                mock_entity_class=MagicMock(),
                mock_bucket_name=MagicMock(),
                mock_bucket_url=MagicMock()):
        Mocks = namedtuple('Mocks', ['request',
                                     'adapter',
                                     'console_adapter',
                                     'entity_class',
                                     'bucket_name',
                                     'bucket_url'])
        interactor = PostPlayerInteractor(
            request=mock_request,
            adapter_instance=mock_adapter,
            console_adapter=mock_console_adapter,
            entity_class=mock_entity_class,
            s3_bucket_name=mock_bucket_name,
            s3_bucket_url=mock_bucket_url)
        return interactor, Mocks(mock_request,
                                 mock_adapter,
                                 mock_console_adapter,
                                 mock_entity_class,
                                 mock_bucket_name,
                                 mock_bucket_url)

    return factory


def test_post_player_interactor_instance(interactor_factory):
    interactor, mocks = interactor_factory()

    assert interactor.s3_bucket_name == mocks.bucket_name
    assert interactor.s3_bucket_url == mocks.bucket_url
    assert interactor.console_adapter == mocks.console_adapter
    assert interactor.request == mocks.request
    assert interactor.adapter_instance == mocks.adapter
    assert interactor.entity_class == mocks.entity_class


def test_init_game_point_list(interactor_factory):
    interactor, mocks = interactor_factory()

    games = [MagicMock(entity_id='1', victories=42),
             MagicMock(entity_id='2', victories=17)]
    result = interactor.init_game_point_list(games)

    assert result[0].game_id == '1'
    assert result[0].victories == 42
    assert result[1].game_id == '2'
    assert result[1].victories == 17


@patch.object(PostPlayerInteractor, 'init_game_point_list')
@patch('playerstars_interactors.player.post_player.PlayerConsoles')
def test__init_console_list(mock_player_consoles,
                            mock_init_game_point_list,
                            interactor_factory):
    interactor, mocks = interactor_factory()

    mock_id = MagicMock()
    mock_tag = MagicMock()
    mock_consoles_json = [dict(entity_id=mock_id, tag_name=mock_tag)]
    result = interactor._init_console_list(mock_consoles_json)

    mocks.console_adapter.get_by_id.assert_called_with(mock_id)
    mock_console = mocks.console_adapter.get_by_id()
    mock_init_game_point_list.assert_called_with(mock_console.games)
    mock_player_consoles.assert_called_with(
        console_id=mock_console.entity_id,
        tag_name=mock_tag,
        game_points=mock_init_game_point_list())
    assert result == [mock_player_consoles().to_json()]


def test_init_default_entity_values():
    data = {}
    PostPlayerInteractor._init_default_entity_values(data)

    assert data['player_status'] == 'OFFLINE'
    assert data['countries_regions'] is None
    assert data['star_transactions'] is None
    assert data['favorites'] is None
    assert data['states_regions'] is None
    assert data['red_star_balance'] == 200
    assert data['golden_star_balance'] == 300
    assert data['points'] == 200
    assert data['terms']


def test_get_consoles(interactor_factory):
    interactor, mocks = interactor_factory()

    mock_data = MagicMock()
    result = interactor._get_consoles(mock_data)

    mock_data.get.assert_called_with('consoles', [])
    assert result == mock_data.get()


def test_have_photo():
    mock_data = dict(user=dict(profile_image='asdf'))
    result = PostPlayerInteractor._have_photo(mock_data)
    assert result


@patch.object(PostPlayerInteractor, '_init_console_list')
@patch.object(PostPlayerInteractor, '_init_default_entity_values')
@patch.object(PostPlayerInteractor, '_get_formated_date_birth')
@patch.object(PostPlayerInteractor, '_get_consoles')
@patch.object(PostPlayerInteractor, '_have_photo')
@patch('playerstars_interactors.player.post_player'
       '.upload_photo_and_return_url')
def test_init_entity(mock_upload_photo,
                     mock_have_photo,
                     mock_get_consoles,
                     mock_get_formated_date_birth,
                     mock_init_default_entity_values,
                     mock_init_console_list,
                     interactor_factory):
    interactor, mocks = interactor_factory()

    result = interactor._init_entity()

    mock_data = mocks.request.json_data

    mock_get_consoles.assert_called_with(mock_data)
    mock_init_console_list.assert_called_with(mock_get_consoles())
    mock_get_formated_date_birth.assert_called_with(mock_data)
    mock_data.get.assert_called_once()
    mock_data.get().update.assert_called_with({
        'date_birth': mock_get_formated_date_birth()})
    mock_init_default_entity_values.assert_called_with(mock_data)
    mocks.entity_class.from_json.assert_called_with(mock_data)

    mock_entity = mocks.entity_class.from_json()

    mock_have_photo.assert_called_with(mock_data)
    mock_upload_photo.assert_called_with(
        sent_image=mock_data.__getitem__().__getitem__(),
        unique_name=mock_entity.entity_id,
        s3_bucket_name=mocks.bucket_name,
        s3_bucket_url=mocks.bucket_url)

    assert mock_entity.profile_image == mock_upload_photo()

    assert result == mock_entity


def test_get_formated_birth_date():
    mock_data = dict(user=dict(date_birth='19/07/1971'))
    result = PostPlayerInteractor._get_formated_date_birth(mock_data)

    assert result == '1971-07-19'


def test_get_formated_birth_date_no_datebirth():
    mock_data = dict(user=dict())
    result = PostPlayerInteractor._get_formated_date_birth(mock_data)

    assert result == '2000-01-01'


def test_get_formated_birth_date_no_user():
    mock_data = dict()
    result = PostPlayerInteractor._get_formated_date_birth(mock_data)

    assert result == '2000-01-01'
