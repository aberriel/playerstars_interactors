from playerstars_interactors.basic_interactor.basic_put import \
    BasicPutInteractor


class PutPlayerIsAdminInteractor(BasicPutInteractor):
    def _init_entity(self):
        player = self.adapter_instance.get_by_id(
            self.request.json_data['entity_id'])
        if self.request.json_data['is_admin']:
            player.is_admin = True
        if not self.request.json_data['is_admin']:
            player.is_admin = False
        if self.request.json_data['is_blocked']:
            player.is_blocked = True
        if not self.request.json_data['is_blocked']:
            player.is_blocked = False
        return player
