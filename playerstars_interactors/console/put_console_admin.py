from playerstars_adapters import (
    ConsoleAdapter,
    PlayerAdapter)
from playerstars_domain import (
    Console,
    Game)
from playerstars_interactors.utils.domain_utils import (
    EntityNotFoundException,
    find_entity_by_id)
from playerstars_interactors.utils.rights_utils import (
    AccessDeniedAdminException,
    check_player_is_admin)
from playerstars_interactors.utils.upload_photos import (
    upload_photo_and_return_url)
from uuid import uuid4

import logging


class PutConsoleAdminException(BaseException):
    pass


class PutConsoleAdminRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.console_id = json_data['entity_id']
        self.name = json_data['name']
        self.logo_path = json_data['logo_path'] \
            if 'logo_path' in json_data else None
        self.games = json_data['games'] if 'games' in json_data else []


class PutConsoleAdminResponseModel:
    def __init__(self, console_data):
        self.console_data: Console = console_data

    def __call__(self):
        return self.console_data.to_json()


class PutConsoleAdminInteractor:
    new_console = None

    def __init__(self,
                 request: PutConsoleAdminRequestModel,
                 console_adapter: ConsoleAdapter,
                 player_adapter: PlayerAdapter,
                 s3_bucket_name: str,
                 s3_bucket_url: str):
        self.request = request
        self.console_adapter = console_adapter
        self.player_adapter = player_adapter
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_url = s3_bucket_url
        self.logger = logging.getLogger(__name__)

    def update_entity_logo_path(self, raw_logo_path, unique_name):
        logo_path = None
        if raw_logo_path and \
                ("data:image" in raw_logo_path
                 or 'http' not in raw_logo_path):
            logo_path = upload_photo_and_return_url(
                sent_image=raw_logo_path,
                unique_name=unique_name,
                s3_bucket_name=self.s3_bucket_name,
                s3_bucket_url=self.s3_bucket_url)
        elif raw_logo_path:
            logo_path = raw_logo_path
        return logo_path

    def update_console(self):
        self.new_console.name = self.request.name
        self.new_console.logo_path = \
            self.update_entity_logo_path(
                raw_logo_path=self.request.logo_path,
                unique_name=self.new_console.entity_id)

        game_list = []
        if self.request.games:
            for game_dict in self.request.games:
                game_data = self.update_game(game_dict)
                game_list.append(game_data)
        self.new_console.games = game_list \
            if game_list else self.new_console.games

    def update_game(self, game_json):
        game_id = game_json['entity_id'] or str(uuid4())
        logo_path = self.update_entity_logo_path(
            raw_logo_path=game_json['logo_path'],
            unique_name=game_id)
        game: Game = Game(
            name=game_json['name'],
            entity_id=game_id,
            logo_path=logo_path)
        return game

    def run(self):
        try:
            check_player_is_admin(
                player_id=self.request.player_id,
                player_adapter=self.player_adapter)
            self.new_console: Console = find_entity_by_id(
                _id=self.request.console_id,
                adapter_instance=self.console_adapter,
                class_name='Console')
            self.update_console()
            self.new_console.save()
            response = PutConsoleAdminResponseModel(self.new_console)
            return response()
        except (AccessDeniedAdminException,
                EntityNotFoundException,
                Exception) as exc:
            msg = 'Error during console update: {0}'.format(str(exc))
            self.logger.error(msg)
            if isinstance(exc, AccessDeniedAdminException):
                raise AccessDeniedAdminException(msg)
            raise PutConsoleAdminException(msg)
