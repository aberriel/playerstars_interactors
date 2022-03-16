from playerstars_interactors.basic_interactor.basic_post import \
    BasicPostInteractor


class PostAppNotificationInteractor(BasicPostInteractor):
    def _init_entity(self):
        return self.entity_class.from_json(self.request.json_data)
