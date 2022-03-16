from playerstars_domain import Player


class GetFriendRequestModel:
    def __init__(self, player_id, favorite_id):
        self.player_id = player_id
        self.favorite_id = favorite_id


class GetFriendResponseModel:
    def __init__(self, player: Player):
        self.player = player

    def __call__(self):
        return self.player.to_json() if self.player else None


class GetFriendInteractor:
    def __init__(self,
                 request: GetFriendRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance

    def get_favorite_from_player(self, player: Player, favorite_id):
        for entity_id in player.favorites:
            if entity_id == favorite_id:
                result = self.adapter_instance.get_by_id(entity_id)
                return result

    def run(self):
        player: Player = self.adapter_instance.get_by_id(
            self.request.player_id)
        favorite = self.get_favorite_from_player(player,
                                                 self.request.favorite_id)
        response = GetFriendResponseModel(favorite)
        return response()
