from clapy_basic_classes import BasicEntity
from marshmallow import fields, post_load
from uuid import uuid4


class FakeEntity(BasicEntity):
    def __init__(self, entity_id=None, nome=None, idade=None):
        super(FakeEntity, self).__init__(entity_id)
        self.nome = nome
        self.idade = idade

    class Schema(BasicEntity.Schema):
        nome = fields.String(required=True, allow_none=False)
        idade = fields.Integer(required=True, allow_none=False)

        @post_load
        def post_load(self, data, many, partial):
            return FakeEntity(**data)


class FakeAdapter:
    def __init__(self, fake_db):
        self.fake_db = fake_db

    def save(self, object_json):
        entity_id = object_json.get('entity_id', str(uuid4()))
        object_json.update({'entity_id': entity_id})
        self.fake_db[object_json['entity_id']] = object_json

    def list_all(self):
        objects = [FakeEntity.from_json(x) for x in self.fake_db.values()]
        for obj in objects:
            obj.set_adapter(self)
        return objects

    def get_by_id(self, item_id):
        response = self.fake_db.get(item_id)
        if response is not None:
            return FakeEntity.from_json(response)

    def delete(self, entity_id):
        del self.fake_db[entity_id]
        return entity_id

    def filter(self, **params):
        objects = [FakeEntity.from_json(x) for x in self.fake_db.values()]
        result_list = list()
        for k, v in params.items():
            for obj in objects:
                if k in obj.to_json().keys():
                    if v in obj.to_json()[k]:
                        obj.set_adapter(self)
                        result_list.append(obj)
        return result_list


def make_context(adapter):
    entidades = [('fulano', 15),
                 ('siclano', 30),
                 ('beltrano', 60)]

    for nome, idade in entidades:
        fentity = FakeEntity(str(uuid4()), nome, idade)
        fentity.set_adapter(adapter)
        fentity.save()

    return entidades
