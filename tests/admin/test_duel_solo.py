from playerstars_interactors import \
    GetAllDuelAdminRequestModel, GetAllDuelAdminInteractor
from unittest.mock import MagicMock
from tests.util_tests import duel_list

params = {
    'playerd_id': '123',
    'sort_field': 'entity_id',
    'sort_order': 'ASC'
}


duel_adapter = MagicMock(filter=MagicMock(return_value=duel_list))


def test_duel_solo_individual():
    request = GetAllDuelAdminRequestModel(params)
    interactor = GetAllDuelAdminInteractor(
        duel_adapter=duel_adapter, request=request, duel_type='individual')
    response = interactor.run()
    assert isinstance(response, list)
    assert response == [duel_list[0].to_json(), duel_list[1].to_json()]


def test_duel_solo_time():
    request = GetAllDuelAdminRequestModel(params)
    interactor = GetAllDuelAdminInteractor(
        duel_adapter=duel_adapter, request=request, duel_type='time')
    response = interactor.run()
    assert isinstance(response, list)
    assert response == [duel_list[2].to_json()]


def test_duel_solo_full_param():
    request = GetAllDuelAdminRequestModel(params)
    interactor = GetAllDuelAdminInteractor(
        duel_adapter=duel_adapter, request=request, duel_type='individual',
        paginate=True, sort=True)
    response = interactor.run()
    assert isinstance(response[0], list)
    assert response[0] == [duel_list[0].to_json(), duel_list[1].to_json()]
    assert response[1].initial == 0
    assert response[1].final == 2
    assert response[1].total == 2
    assert response[1].unit == 'duel'
