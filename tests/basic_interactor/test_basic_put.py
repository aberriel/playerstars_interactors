from playerstars_interactors import (
    BasicPutInteractor,
    BasicPutRequestModel,
    UpdateEntityException
)
from tests.basic_interactor.fixtures import (
    FakeAdapter,
    FakeEntity,
    make_context
)
from unittest.mock import patch

import pytest


def test_basic_put():
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    make_context(adapter)

    entity_to_update = list(fake_db.values())[0]['entity_id']
    put_data = {'entity_id': entity_to_update,
                'nome': 'outro nome',
                'idade': 42}

    request = BasicPutRequestModel(put_data)
    interactor = BasicPutInteractor(request, adapter, FakeEntity)

    interactor.run()

    assert fake_db[entity_to_update]['nome'] == 'outro nome'
    assert fake_db[entity_to_update]['idade'] == 42


# noinspection PyUnusedLocal
@patch.object(FakeAdapter, 'save', side_effect=Exception('oops'))
def test_enter_duel_without_player(save):
    fake_db = {}
    adapter = FakeAdapter(fake_db)

    post_data = {'nome': 'novo nome', 'idade': 42}

    request = BasicPutRequestModel(post_data)
    interactor = BasicPutInteractor(request, adapter, FakeEntity)
    with pytest.raises(UpdateEntityException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Entity update error: oops'
