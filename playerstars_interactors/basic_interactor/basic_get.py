from clapy_basic_classes import BasicEntity


class BasicGetRequestModel:
    def __init__(self, entity_id):
        self.entity_id = entity_id


class BasicGetResponseModel:
    def __init__(self, entity: BasicEntity):
        self.entity = entity

    def __call__(self):
        return self.entity.to_json() if self.entity else None


class BasicGetInteractor:
    def __init__(self,
                 request: BasicGetRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance

    def run(self):
        entity = self.adapter_instance.get_by_id(self.request.entity_id)
        response = BasicGetResponseModel(entity)
        return response()
