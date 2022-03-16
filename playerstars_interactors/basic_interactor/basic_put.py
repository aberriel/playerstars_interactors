import logging


class UpdateEntityException(BaseException):
    pass


class BasicPutRequestModel:
    def __init__(self, json_data):
        self.json_data = json_data


class BasicPutResponseModel:
    def __init__(self, saved_id):
        self.saved_id = saved_id

    def __call__(self):
        return self.saved_id


class BasicPutInteractor:
    def __init__(self, request: BasicPutRequestModel,
                 adapter_instance,
                 entity_class):
        self.request = request
        self.adapter_instance = adapter_instance
        self.entity_class = entity_class
        self.logger = logging.getLogger(__name__)

    def _init_entity(self):
        """
        Função que deve ser sobreescrita por classe derivada caso
        a criação da entidade com os dados do post não seja trivial

        :return: Instância da entidade.
        """
        entity = self.entity_class.from_json(self.request.json_data)
        return entity

    def run(self):
        try:
            entity = self._init_entity()
            entity.set_adapter(self.adapter_instance)
            saved_entity = entity.save()
            return BasicPutResponseModel(saved_entity)()
        except Exception as e:
            msg = 'Entity update error: {}'.format(e)
            self.logger.error(msg)
            raise UpdateEntityException(msg)
