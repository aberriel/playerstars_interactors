from playerstars_domain import Player
from playerstars_interactors import \
    PutPlayerIsAdminInteractor, BasicPutRequestModel
from tests.util_tests import player_json
from unittest.mock import MagicMock, patch


prefix_dynamodb_adapter = 'clapy_dynamodb_adapter.basic_dynamodb_adapter'


json_data = {
    'entity_id': '1234',
    'is_admin': True,
    'is_blocked': True}


player = Player.from_json(player_json)


player_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player))


@patch('boto3.resource')
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_put_is_admin(boto, resource):
    request = BasicPutRequestModel(json_data)
    interactor = \
        PutPlayerIsAdminInteractor(request, player_adapter_mock, Player)
    player2 = interactor._init_entity()
    assert player2
    assert player2.is_admin
    assert player2.is_blocked is True


json_data2 = {
    'entity_id': '1234',
    'is_admin': False,
    'is_blocked': False
}

player.is_admin = True
player.is_blocked = True


@patch('boto3.resource')
@patch(f'{prefix_dynamodb_adapter}.boto3')
def test_put_is_admin_to_false(boto, resource):
    assert player.is_admin
    request = BasicPutRequestModel(json_data2)
    interactor = \
        PutPlayerIsAdminInteractor(request, player_adapter_mock, Player)
    player2 = interactor._init_entity()
    assert player2
    assert not player2.is_admin
    assert not player2.is_blocked
