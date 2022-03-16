from playerstars_interactors import (
    BasicDeleteInteractor,
    BasicDeleteRequestModel
)
from tests.basic_interactor.fixtures import (
    FakeAdapter,
    make_context
)


def test_basic_delete():
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    make_context(adapter)

    entity_to_delete = list(fake_db.values())[0]['entity_id']
    deleted_name = fake_db[entity_to_delete]['nome']

    request = BasicDeleteRequestModel(entity_to_delete)
    interactor = BasicDeleteInteractor(request, adapter)

    assert len(fake_db) == 3

    response = interactor.run()

    assert len(fake_db) == 2
    assert deleted_name not in [x['nome'] for x in fake_db.values()]
    assert response == entity_to_delete
