from playerstars_domain import Player


class GetAllFriendsRequestModel:
    def __init__(self, player_id):
        self.player_id = player_id


class GetAllFriendsResponseModel:
    def __init__(self, favorites):
        self.favorites = favorites

    def __call__(self):
        return self.favorites if self.favorites else list()


class GetAllFriendsInteractor:
    def __init__(self,
                 request: GetAllFriendsRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance

    def format_favorites(self, favorites):
        favorite_list = list()
        for item in favorites:
            player: Player = self.adapter_instance.get_by_id(item)
            favorite_list.append({
                'entity_id': player.entity_id,
                'name': player.user.name,
                'photo': player.user.profile_image,
                'nickname': player.user.nickname
            })
        return favorite_list

    def run(self):
        player: Player = self.adapter_instance.get_by_id(
            self.request.player_id)
        if not player:
            return list()
        formated_favorites = self.format_favorites(player.favorites)
        response = GetAllFriendsResponseModel(formated_favorites)
        return response()
