import logging


class SaveEntityException(BaseException):
    pass


class BasicPostRequestModel:
    def __init__(self, json_data):
        self.json_data = json_data


class BasicPostResponseModel:
    def __init__(self, saved_id):
        self.saved_id = saved_id

    def __call__(self):
        return self.saved_id


class BasicPostInteractor:
    def __init__(self, request: BasicPostRequestModel,
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
        kw = self.request.json_data
        if 'entity_id' not in kw.keys():
            kw.update({'entity_id': ''})
        entity = self.entity_class.from_json(kw)
        return entity

    def run(self):
        try:
            entity = self._init_entity()
            entity.set_adapter(self.adapter_instance)
            saved_entity = entity.save()
            return BasicPostResponseModel(saved_entity)()
        except Exception as e:
            msg = 'Entity creation error: {}'.format(e)
            self.logger.error(msg)
            raise SaveEntityException(msg)
