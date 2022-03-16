from playerstars_domain import Player
from playerstars_interactors import \
    SaveConvertedStarsInteractor, SaveConvertedStarsRequestModel, \
    SaveConvertedStarsException
from tests.util_tests import player_json
from unittest.mock import MagicMock, patch

import pytest


request_json = {
    'player_id': 'a677d189-e420-4928-ac1b-51cdea9d6296',
    'gold_stars': 20,
    'red_stars': 250
}
player: Player = Player.from_json(player_json)
player.golden_star_balance = 1000


player_adapter_mock_1 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player),
    save=MagicMock(return_value=player.entity_id))


"""
@patch('boto3.resource')
def test_post_converted_stars(resource):
    request = SaveConvertedStarsRequestModel(request_json)
    interactor = SaveConvertedStarsInteractor(request, player_adapter_mock_1)
    response = interactor.run()
    assert response
"""


player2 = Player.from_json(player_json)
player2.golden_star_balance = 200


player_adapter_mock_2 = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player2),
    save=MagicMock(return_value=player2.entity_id))


"""
@patch('boto3.resource')
def test_post_converted_stars_operations(resource):
    request = SaveConvertedStarsRequestModel(request_json)
    interactor = SaveConvertedStarsInteractor(request, player_adapter_mock_2)
    response = interactor.execute_operations(player2)
    assert response.golden_star_balance == 180
    assert response.red_star_balance == 265
"""


player_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player),
    save=MagicMock(side_effect=Exception('oops')))


@patch('boto3.resource')
def test_post_converted_stars_raises(resource):
    request = SaveConvertedStarsRequestModel(request_json)
    interactor = SaveConvertedStarsInteractor(request,
                                              player_adapter_mock_raises)
    with pytest.raises(SaveConvertedStarsException) as excinfo:
        interactor.run()
    assert 'Erro ao salvar novo saldo de stars' in str(excinfo.value)
