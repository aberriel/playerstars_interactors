from playerstars_interactors import \
    BasicGetAllInteractor, BasicGetAllRequestModel, BasicGetAllResponseModel
from tests.basic_interactor.fixtures import (
    FakeAdapter, FakeEntity, make_context)
from unittest.mock import patch
from uuid import uuid4


def test_basic_getall():
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    entidades = make_context(adapter)
    paginate = False
    range_data = None
    interactor = BasicGetAllInteractor(
        adapter_instance=adapter, request=None, paginate=paginate)
    resultado = interactor.run()
    assert len(resultado) == 3
    assert resultado[0]['nome'] in [x[0] for x in entidades]
    assert not range_data


query_params = {
    'pagination_page': 1,
    'pagination_per_page': 2,
    'sort_order': 'DESC',
    'sort_field': 'nome'
}


def test_basic_getall_paginated_and_sorted():
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    entidades = make_context(adapter)
    request = BasicGetAllRequestModel(query_params)
    interactor = BasicGetAllInteractor(
        adapter_instance=adapter, request=request, paginate=True, sort=True)
    resultado, range_data = interactor.run()
    assert len(resultado) == 2
    assert resultado[0]['nome'] in [x[0] for x in entidades]
    assert range_data.initial == 0
    assert range_data.final == 2
    assert range_data.total == 3
    assert range_data.unit == 'ranking'


params = {
    'param': '{"nome": "siclano"}'
}

params_with_pagination = {
    'param': '{"nome": "siclano"}',
    'pagination_page': '1',
    'pagination_per_page': '2'
}


@patch.object(BasicGetAllInteractor, 'paginate_entity',
              return_value=[('siclano', 30)])
def test_basic_getall_filter_without_pagination(paginate_mock):
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    entidades = make_context(adapter)
    request = BasicGetAllRequestModel(params)
    interactor = BasicGetAllInteractor(
        adapter_instance=adapter, request=request)
    resultado = interactor.run()
    assert len(resultado) == 1
    assert resultado[0]['nome'] in [x[0] for x in entidades]
    assert paginate_mock.call_count == 0


@patch.object(BasicGetAllInteractor, 'paginate_entity',
              return_value=BasicGetAllResponseModel(
                  [FakeEntity(str(uuid4()), 'siclano', 10)]))
def test_basic_getall_filter_with_pagination(paginate_mock):
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    entidades = make_context(adapter)
    request = BasicGetAllRequestModel(params_with_pagination)
    interactor = BasicGetAllInteractor(
        adapter_instance=adapter, request=request, paginate=True)
    resultado = interactor.run()
    assert len(resultado) == 1
    assert resultado[0]['nome'] in [x[0] for x in entidades]
    paginate_mock.assert_called_once()
