from playerstars_domain import Console
from playerstars_interactors import (
    PutGameInteractor, PutGameRequestModel, UpdateGameException)
from unittest.mock import MagicMock, patch

# noinspection PyPackageRequirements
import pytest

json_data = dict(
    entity_id="id1234",
    name='Sonic',
    logo_path='images/sonic.jpg',
    consoles=[
        {
            "entity_id": "5",
            "name": "Super Nintendo",
            "logo_path": "/images/ss.png",
            "tag_name": "nick#1"
        },
        {
            "entity_id": "4",
            "name": "Atari",
            "logo_path": "/images/aa.png",
            "tag_name": "nick#2"
        }
    ]
)

console = Console(
    name="Xbox",
    logo_path="images/xb.png",
    games=[],
    tag_name="nick01")


adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    save=MagicMock(return_value='12345'))
adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    save=MagicMock(side_effect=Exception('oops')))


# noinspection PyUnusedLocal
@patch('boto3.resource')
def test_put_game(resource):
    request = PutGameRequestModel(json_data)
    interactor = PutGameInteractor(request, adapter_mock, console)
    response = interactor.run()
    assert adapter_mock.save.call_count == 2
    assert len(response) == 2
    assert response == ['12345', '12345']


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
def test_put_game_raises(resource):
    request = PutGameRequestModel(json_data)
    interactor = PutGameInteractor(request, adapter_mock_raises, console)
    with pytest.raises(UpdateGameException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Erro salvando game:oops'
