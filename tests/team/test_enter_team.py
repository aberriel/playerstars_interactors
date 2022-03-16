from datetime import datetime
from playerstars_domain import (
    Player, User, Team, PlayerConsoles
)
from playerstars_interactors import (
    EnterTeamException,
    EnterTeamInteractor,
    EnterTeamRequestModel
)
from tests.util_tests import team_json
from unittest.mock import MagicMock, patch

import pytest


request = EnterTeamRequestModel({
    'player_id': 'idplayer12345',
    'team_id': 'idduel123'
})


user = User(
    name='Pablinho',
    email='menoti@hotmail.com',
    date_birth=datetime.strptime("01/01/1987", "%d/%m/%Y"),
    street='Avenida Brasil',
    street_number='500',
    street_complement='apt 607',
    neighborhood='pechinchão',
    city='Rio de Janeiro',
    state='Rio de Janeiro',
    country='Brasil',
    postal_code='90210',
    phone_number='5555-4321',
    nickname='zyzukab',
    cpf='123.456.789-01'
)


player = Player(
    user=user,
    consoles=[PlayerConsoles.from_json({
        "console_id": "a03be321-622c-4908-826c-2522f71a355e",
        "game_points": [{
            "game_id": "f16c9f9a-9b22-4884-b890-bcc3294e91be",
            "victories": 100
        }],
        "tag_name": "zyzukab"
    })],
    favorites=[],
    red_star_balance=321,
    golden_star_balance=987,
    entity_id='idplayer1234')


team = Team.from_json(team_json)


player_adapter_enter_team = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player))
team_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=team),
    save=MagicMock(return_value='team123'))
team_adapter_mock_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=team),
    save=MagicMock(side_effect=Exception('oops')))


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('boto3.client')
def test_enter_team_raises(boto_client, boto_resource):
    interactor = EnterTeamInteractor(
        request=request,
        player_adapter=player_adapter_enter_team,
        team_adapter=team_adapter_mock_raises)
    with pytest.raises(EnterTeamException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Erro ao salvar novo player no time: oops'


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('boto3.client')
def test_enter_team(boto_client, boto_resource):
    interactor = EnterTeamInteractor(
        request=request,
        player_adapter=player_adapter_enter_team,
        team_adapter=team_adapter_mock)
    interactor.run()
    team_adapter_mock.save.assert_called_once()
