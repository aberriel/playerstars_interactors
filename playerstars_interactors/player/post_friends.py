from playerstars_domain import Player
from typing import List

import logging


class SaveFriendsException(BaseException):
    pass


class AlterFriendsRequestModel:
    def __init__(self, list_entity_id: List[str], player_id):
        self.list_entity_id = list_entity_id
        self.player_id = player_id


class AlterFriendsResponseModel:
    def __init__(self, saved_id_list):
        self.saved_id_list = saved_id_list

    def __call__(self):
        return self.saved_id_list


class AlterFriendsInteractor:
    def __init__(self,
                 request: AlterFriendsRequestModel,
                 adapter_instance,
                 option):
        self.request = request
        self.adapter_instance = adapter_instance
        self.option = option
        self.logger = logging.getLogger(__name__)

    def _alter_favorite_list(self, player):
        for item in self.request.list_entity_id:
            if self.option == 'add':
                player.add_favorite(item)
            if self.option == 'delete':
                player.remove_favorite(item)
        return player

    def run(self):
        player: Player = self.adapter_instance.\
            get_by_id(self.request.player_id)
        player.set_adapter(self.adapter_instance)
        player = self._alter_favorite_list(player, )
        try:
            update_player = player.update()
            if update_player:
                response = AlterFriendsResponseModel(player.favorites)
                return response()
        except BaseException as e:
            msg = f'Erro salvando amigo:{e}'
            self.logger.error(msg)
            raise SaveFriendsException(msg)
