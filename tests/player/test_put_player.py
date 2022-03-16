from playerstars_domain import Player
from playerstars_interactors import \
    PutPlayerException, PutPlayerInteractor, PutPlayerRequestModel
from tests.util_tests import player_json
from unittest.mock import MagicMock, patch
from tests.player.player_utils import console_data

import pytest


player = Player.from_json(player_json)
player2 = Player.from_json(player_json)
request_json = {
    'entity_id': player.entity_id,
    'user': {
        "name": "Anselmo Lira",
        "email": "playerstars@playerstars.com.br",
        "date_birth": "2018-11-11",
        "street": 'Avenida Brasil',
        "street_number": '500',
        "street_complement": 'apt 607',
        "neighborhood": 'pechinchão',
        "city": "Rio de Janeiro",
        "state": "Rio de Janeiro",
        "country": "Brasil",
        "postal_code": "22333-000",
        "phone_number": "(21) 99663-6963",
        "cpf": "123.456.789-00",
        "nickname": "anselmo.lira",
        "profile_image": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAA"
                         "AEAAAABCAYAAAAfFcSJAAAA"
                         "DUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    }
}


player_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player),
    save=MagicMock(autospec=True, return_value=player.entity_id))
player_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player2),
    save=MagicMock(side_effect=Exception('oops')))

console_adapter = MagicMock(
    get_by_id=MagicMock(return_value=console_data))


@patch('playerstars_interactors.utils.upload_photos.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/profile.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_update_profile(boto_client, boto_resource, upload_photo_mock):
    player_adapter_mock.save.call_count = 0
    request = PutPlayerRequestModel(request_json)
    interactor = PutPlayerInteractor(
        request=request,
        player_adapter=player_adapter_mock,
        console_adapter=console_adapter,
        s3_bucket_name='bucket_name',
        s3_bucket_url='bucket_url')
    response = interactor.run()
    player_adapter_mock.save.assert_called_once()

    assert interactor.old_player.entity_id == player.entity_id
    assert response == player.entity_id


request_json2 = {
    "entity_id": player.entity_id,
    "user": {
        "name": "Anselmo Lira",
        "email": "playerstars@playerstars.com.br",
        "date_birth": "2018-11-11",
        "street": 'Avenida Brasil',
        "street_number": '500',
        "street_complement": 'apt 607',
        "neighborhood": 'pechinchão',
        "city": "Rio de Janeiro",
        "state": "Rio de Janeiro",
        "country": "Brasil",
        "postal_code": "22333-000",
        "phone_number": "(21) 99663-6963",
        "cpf": "123.456.789-00",
        "nickname": "anselmo.lira",
        "profile_image": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAA"
                         "AEAAAABCAYAAAAfFcSJAAAA"
                         "DUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    },
    "consoles": [
        {
            "entity_id": "69974eb6-1ebb-422c-92ab-aaa72e88f3a0",
            "tag_name": "anselmo01"
        },
        {
            "entity_id": "c7b0e8b6-44c9-457d-84c9-32f6c985f9d3",
            "tag_name": "007"
        },
        {
            "entity_id": "111111",
            "tag_name": "Leoplay4"
        }
    ]
}


@patch('playerstars_interactors.utils.upload_photos.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/profile.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_update_profile_with_consoles(client, resource, upload_photo_mock):
    player_adapter_mock.save.call_count = 0
    update_profile_request = PutPlayerRequestModel(request_json2)
    interactor = PutPlayerInteractor(
        request=update_profile_request,
        player_adapter=player_adapter_mock,
        console_adapter=console_adapter,
        s3_bucket_name='bucket_name',
        s3_bucket_url='bucket_url')
    response = interactor.run()

    player_adapter_mock.save.assert_called_once()
    assert response == player.entity_id


request_json3 = {
    'entity_id': player.entity_id,
    'user': {
        "name": "Anselmão",
        "email": "playerstars@playerstars.com.br",
        "date_birth": "11/11/2019",
        "street": 'Avenida Brasil',
        "street_number": '500',
        "street_complement": 'apt 607',
        "neighborhood": 'pechinchão',
        "city": "Rio de Janeiro",
        "state": "Rio de Janeiro",
        "country": "Brasil",
        "postal_code": "22333-000",
        "phone_number": "(21) 99663-6963",
        "cpf": "123.456.789-00",
        "nickname": "anselmo.lira",
        "profile_image": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAA"
                         "AEAAAABCAYAAAAfFcSJAAAA"
                         "DUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    }
}


@patch('playerstars_interactors.utils.upload_photos.'
       'upload_photo_and_return_url',
       return_value='http://bucket_url/profile.jpg')
@patch('boto3.resource')
@patch('boto3.client')
def test_update_profile_raises(client, resource, upload_photo_mock):
    request = PutPlayerRequestModel(request_json3)
    interactor = PutPlayerInteractor(
        request=request,
        player_adapter=player_adapter_mock_raises,
        console_adapter=console_adapter,
        s3_bucket_name='bucket_name',
        s3_bucket_url='bucket_url')
    with pytest.raises(PutPlayerException) as excinfo:
        interactor.run()
    assert 'Erro fazendo update de profile do player' \
           in str(excinfo.value)
