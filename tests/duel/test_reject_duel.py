from datetime import datetime
from playerstars_domain import (
    CoinType,
    Console,
    Duel,
    DuelMemberType,
    DuelStatus,
    DuelType,
    Game)
from playerstars_interactors import (
    RejectDuelException,
    RejectDuelInteractor,
    RejectDuelRequestModel,
    RejectDuelResponseModel)
from unittest.mock import MagicMock, patch
import pytest


request = RejectDuelRequestModel({
    'duel_id': 'duel123'
})


def make_duel_data():
    duel = Duel(
        bet_size=200,
        challenged='ecc4a0c8-329a-41e9-a069-a76fc27abb69',
        challenger='2423e622-621b-4162-89c9-4e9e22d259d1',
        console=Console(entity_id='abec7b9a-a410-4cc0-bdf1-1ac8e763c8aa',
                        logo_path='/teste/atari.png',
                        name='Atari'),
        entity_id='duel123',
        game=Game(entity_id='3a793ed7-3558-4dc1-a310-676dc49d81fb',
                  logo_path='images/sonic.jpg',
                  name='Sonic'),
        participants=2,
        star_type=CoinType.GOLDEN_STAR,
        status=DuelStatus.LOBBY,
        time_start=datetime(2019, 11, 4, 20, 47, 0, 320655),
        creation_datetime=datetime(2019, 11, 4, 20, 45, 15, 12345),
        total_reward=400,
        duel_type=DuelType.INDIVIDUAL,
        member_type=DuelMemberType.PLAYER,
        time_to_finish_duel=300,
        time_to_accept_invitation=5)
    return duel


duel_adapter_mock = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_duel_data()),
    save=MagicMock(return_value='duel123'))


@patch('boto3.resource')
@patch('boto3.client')
def test_reject_duel(boto_client, boto_resource):
    duel_adapter_mock.save.call_count = 0
    interactor = RejectDuelInteractor(
        request=request,
        duel_adapter_dynamo=duel_adapter_mock,
        duel_adapter_graphql=duel_adapter_mock)

    response = interactor.run()
    duel_adapter_mock.save.assert_called_once()
    assert response
    assert isinstance(response, RejectDuelResponseModel)
    assert response() == 'duel123'


duel_adapter_raises = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_duel_data()),
    save=MagicMock(side_effect=Exception('oops')))


@patch('boto3.resource')
@patch('boto3.client')
def test_reject_duel_raises(boto3, resource):
    interactor = RejectDuelInteractor(
        request=request,
        duel_adapter_dynamo=duel_adapter_raises,
        duel_adapter_graphql=duel_adapter_raises)
    with pytest.raises(RejectDuelException) as excinfo:
        interactor.run()
    assert 'Error in reject duel duel123: oops' in str(excinfo.value)


def make_duel_accepted():
    duel_data = make_duel_data()
    duel_data.status = DuelStatus.DUELING
    return duel_data


duel_adapter_accepted = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=make_duel_accepted()))


@patch('boto3.resource')
@patch('boto3.client')
def test_reject_duel_status_error(client, resource):
    interactor = RejectDuelInteractor(
        request=request,
        duel_adapter_dynamo=duel_adapter_accepted,
        duel_adapter_graphql=duel_adapter_accepted)
    with pytest.raises(RejectDuelException) as exc:
        interactor.run()
    assert "Error in reject duel duel123: Player can't reject duel " \
           "because duel's status is DUELING" in str(exc.value)
