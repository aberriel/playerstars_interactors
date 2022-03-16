import pytest
from unittest.mock import patch
from tests.basic_interactor.fixtures import (
    FakeAdapter,
    FakeEntity,
    make_context
)
from playerstars_interactors import (
    BasicPostInteractor,
    BasicPostRequestModel,
    SaveEntityException
)


def test_basic_post():
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    make_context(adapter)

    post_data = {'nome': 'novo nome', 'idade': 42}

    request = BasicPostRequestModel(post_data)
    interactor = BasicPostInteractor(request, adapter, FakeEntity)

    assert len(fake_db) == 3

    interactor.run()

    assert len(fake_db) == 4
    assert 'novo nome' in [x['nome'] for x in fake_db.values()]


# noinspection PyUnusedLocal
@patch.object(FakeAdapter, 'save', side_effect=Exception('oops'))
def test_basic_post_raises(save):
    fake_db = {}
    adapter = FakeAdapter(fake_db)

    post_data = {'nome': 'novo nome', 'idade': 42}

    request = BasicPostRequestModel(post_data)
    interactor = BasicPostInteractor(request, adapter, FakeEntity)
    with pytest.raises(SaveEntityException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Entity creation error: oops'
