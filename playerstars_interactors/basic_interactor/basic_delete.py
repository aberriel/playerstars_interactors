class BasicDeleteRequestModel:
    def __init__(self, entity_id):
        self.entity_id = entity_id


class BasicDeleteResponseModel:
    def __init__(self, deleted_id):
        self.deleted_id = deleted_id

    def __call__(self):
        return self.deleted_id if self.deleted_id else None


class BasicDeleteInteractor:
    def __init__(self, request: BasicDeleteRequestModel, adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance

    def run(self):
        deleted = self.adapter_instance.delete(self.request.entity_id)
        response = BasicDeleteResponseModel(deleted)
        return response()
