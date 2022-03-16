from playerstars_interactors import (
    BasicGetInteractor,
    BasicGetRequestModel
)
from tests.basic_interactor.fixtures import (
    FakeAdapter,
    make_context
)


def test_basic_get():
    fake_db = {}
    adapter = FakeAdapter(fake_db)
    make_context(adapter)

    entity_to_get = list(fake_db.values())[1]['entity_id']
    gotten_name = fake_db[entity_to_get]['nome']

    request = BasicGetRequestModel(entity_to_get)
    interactor = BasicGetInteractor(request, adapter)

    response = interactor.run()

    assert response['nome'] == gotten_name
