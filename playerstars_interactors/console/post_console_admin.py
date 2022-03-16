from playerstars_adapters import (
    ConsoleAdapter,
    PlayerAdapter)
from playerstars_domain import Console, Game
from playerstars_interactors.utils.domain_utils import EntityNotFoundException
from playerstars_interactors.utils.rights_utils import (
    AccessDeniedAdminException,
    check_player_is_admin)
from playerstars_interactors.utils.upload_photos import (
    upload_photo_and_return_url)
from uuid import uuid4

import logging


class PostConsoleAdminException(BaseException):
    pass


class PostConsoleAdminRequestModel:
    def __init__(self, json_data: dict):
        self.player_id = json_data['player_id']
        self.name = json_data['name']
        self.logo = json_data['logo_path'] \
            if 'logo_path' in json_data else None
        self.games = json_data['games'] if 'games' in json_data else []


class PostConsoleAdminResponseModel:
    def __init__(self, console_id):
        self.console_id = console_id

    def __call__(self):
        return self.console_id


class PostConsoleAdminInteractor:
    console_data = None

    def __init__(self,
                 request: PostConsoleAdminRequestModel,
                 console_adapter: ConsoleAdapter,
                 player_adapter: PlayerAdapter,
                 s3_bucket_url: str,
                 s3_bucket_name: str):
        self.request = request
        self.console_adapter = console_adapter
        self.player_adapter = player_adapter
        self.s3_bucket_url = s3_bucket_url
        self.s3_bucket_name = s3_bucket_name
        self.logger = logging.getLogger(__name__)

    def check_console(self):
        all_consoles = self.console_adapter.list_all()
        same_console = next((x for x in all_consoles
                             if x.name == self.request.name),
                            None)
        if same_console:
            raise Exception('Exists a console with same name and has id {0}'.
                            format(same_console.entity_id))

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

    def mount_console(self):
        raw_game_list = self.request.games
        entity_id = str(uuid4())
        game_list = []
        for raw_game in raw_game_list:
            game_data = self.mount_game(raw_game)
            game_list.append(game_data)

        logo_path = self.update_entity_logo_path(
            raw_logo_path=self.request.logo,
            unique_name=entity_id)

        self.console_data = Console(
            entity_id=entity_id,
            name=self.request.name,
            logo_path=logo_path,
            games=game_list)
        self.console_data.set_adapter(self.console_adapter)

    def mount_game(self, game_data: dict):
        entity_id = game_data['entity_id'] \
            if 'entity_id' in game_data else str(uuid4())
        logo_path = self.update_entity_logo_path(
            raw_logo_path=game_data['logo_path']
            if 'logo_path' in game_data else None,
            unique_name=entity_id)
        return Game(
            entity_id=entity_id,
            name=game_data['name'],
            logo_path=logo_path)

    def run(self):
        try:
            check_player_is_admin(self.request.player_id, self.player_adapter)
            self.check_console()
            self.mount_console()
            console_id = self.console_data.save()
            response = PostConsoleAdminResponseModel(console_id)
            return response()
        except (AccessDeniedAdminException,
                EntityNotFoundException,
                Exception) as exc:
            msg = 'Error during console creation: {0}'.format(str(exc))
            self.logger.error(msg)
            if isinstance(exc, AccessDeniedAdminException):
                raise AccessDeniedAdminException(msg)
            raise PostConsoleAdminException(msg)
