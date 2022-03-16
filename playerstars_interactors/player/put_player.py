from playerstars_adapters import PlayerAdapter, ConsoleAdapter
from playerstars_domain import Player, PlayerConsoles, GamePoints, Game
from playerstars_interactors.utils.domain_utils import find_entity_by_id
from playerstars_interactors.utils.upload_photos import (
    upload_photo_and_return_url)
from datetime import datetime
import logging
from typing import List


class PutPlayerException(BaseException):
    pass


class PutPlayerRequestModel:
    def __init__(self, json_data):
        self.entity_id = json_data.get('entity_id')
        self.user = json_data.get('user', None)
        self.consoles = json_data.get('consoles', None)


class PutPlayerResponseModel:
    def __init__(self, entity_id):
        self.entity_id = entity_id

    def __call__(self):
        return self.entity_id


class PutPlayerInteractor:
    def __init__(self, request: PutPlayerRequestModel,
                 player_adapter: PlayerAdapter,
                 console_adapter: ConsoleAdapter,
                 s3_bucket_name: str,
                 s3_bucket_url: str):
        self.request: PutPlayerRequestModel = request
        self.player_adapter: PlayerAdapter = player_adapter
        self.console_adapter = console_adapter
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_url = s3_bucket_url
        self.old_player: Player = find_entity_by_id(
            _id=self.request.entity_id,
            adapter_instance=self.player_adapter,
            class_name='Player')
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def update_game_point_list(games: List[Game], old_player):
        game_point_list = list()
        for game in games:
            victories = old_player.get_game_victories_by_id(game.entity_id)
            game_point_list.append(GamePoints(
                game_id=game.entity_id,
                victories=victories or 0
            ))
        return game_point_list

    def new_console_list(self, consoles_json):
        console_list = list()
        for item in consoles_json:
            console = self.console_adapter.get_by_id(item['entity_id'])
            game_point_list = self.update_game_point_list(
                console.games, self.old_player)
            player_console = PlayerConsoles(
                console_id=console.entity_id,
                tag_name=item['tag_name'],
                game_points=game_point_list
            )
            console_list.append(player_console.to_json())
        return console_list

    def update_player(self):
        new_player = self.old_player.to_json()

        new_consoles = self.request.consoles
        if new_consoles:
            new_player['consoles'] = self.new_console_list(new_consoles)

        new_user = self.request.user
        if new_user:
            if 'profile_image' in new_user and new_user['profile_image'] \
                    and ("data:image" in new_user['profile_image']
                         or 'http' not in new_user['profile_image']):
                s3_url = upload_photo_and_return_url(
                    sent_image=new_user['profile_image'],
                    unique_name=new_player['entity_id'],
                    s3_bucket_name=self.s3_bucket_name,
                    s3_bucket_url=self.s3_bucket_url)
                new_user.update({'profile_image': s3_url})
            if '/' in new_user['date_birth']:
                date = datetime.strptime(new_user['date_birth'], '%d/%m/%Y')
                new_user['date_birth'] = date.strftime("%Y-%m-%d")
            new_player["user"] = new_user

        return Player.from_json(new_player)

    def run(self):
        try:
            updated_player = self.update_player()
            updated_player.set_adapter(self.player_adapter)
            save_result = updated_player.save()
            return PutPlayerResponseModel(save_result)()
        except BaseException as e:
            msg = f'Erro fazendo update de profile do player: ' \
                f'{self.request.entity_id}. {str(e)}'
            self.logger.error(msg)
            raise PutPlayerException(msg)
