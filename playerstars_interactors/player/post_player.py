from datetime import datetime
from playerstars_adapters import (
    ConsoleAdapter
)
from playerstars_domain import Player, PlayerConsoles, GamePoints
from playerstars_interactors import BasicPostInteractor, BasicPostRequestModel
from playerstars_interactors.utils.upload_photos import \
    upload_photo_and_return_url


class PostPlayerInteractor(BasicPostInteractor):
    def __init__(self,
                 request: BasicPostRequestModel,
                 adapter_instance,
                 console_adapter,
                 entity_class,
                 s3_bucket_name,
                 s3_bucket_url):
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_url = s3_bucket_url
        self.console_adapter = console_adapter
        super(PostPlayerInteractor, self).__init__(
            request=request, adapter_instance=adapter_instance,
            entity_class=entity_class)

    @staticmethod
    def init_game_point_list(games):
        game_point_list = list()
        for game in games:
            game_point_list.append(GamePoints(
                game_id=game.entity_id,
                victories=game.victories or 0
            ))
        return game_point_list

    def _init_console_list(self, consoles_json):
        console_list = list()
        for item in consoles_json:
            console = self.console_adapter.get_by_id(item['entity_id'])
            game_point_list = self.init_game_point_list(console.games)
            player_console = PlayerConsoles(
                console_id=console.entity_id,
                tag_name=item['tag_name'],
                game_points=game_point_list
            )
            console_list.append(player_console.to_json())
        return console_list

    def _init_entity(self):
        data = self.request.json_data
        consoles = self._get_consoles(data)
        data['consoles'] = self._init_console_list(consoles)
        formated_date_birth = self._get_formated_date_birth(data)
        data.get('user').update({'date_birth': formated_date_birth})
        self._init_default_entity_values(data)
        entity = self.entity_class.from_json(data)
        entity.profile_image = None
        if self._have_photo(data):
            s3_url = upload_photo_and_return_url(
                sent_image=data['user']['profile_image'],
                unique_name=entity.entity_id,
                s3_bucket_name=self.s3_bucket_name,
                s3_bucket_url=self.s3_bucket_url)
            entity.profile_image = s3_url

        return entity

    @staticmethod
    def _have_photo(data):
        return ('profile_image' in data['user'].keys()
                and data['user']['profile_image'])

    def _get_consoles(self, data):
        consoles = data.get('consoles', [])
        return consoles

    @staticmethod
    def _get_formated_date_birth(data):
        date_birth = datetime.strptime(
            data.get('user', {}).get('date_birth', '1/1/2000'), '%d/%m/%Y')
        return date_birth.strftime("%Y-%m-%d")

    @staticmethod
    def _init_default_entity_values(data):
        data['player_status'] = 'OFFLINE'
        data['countries_regions'] = None
        data['star_transactions'] = None
        data['favorites'] = None
        data['states_regions'] = None
        data['red_star_balance'] = 200
        data['golden_star_balance'] = 300
        data['points'] = 200
        if 'terms' not in data:
            data['terms'] = True


class PostPlayerConsoleDataInteractor(BasicPostInteractor):
    def __init__(self, request: BasicPostRequestModel,
                 adapter_instance,
                 console_adapter: ConsoleAdapter,
                 entity_class):
        self.console_adapter = console_adapter
        super(PostPlayerConsoleDataInteractor, self).__init__(
            request=request, adapter_instance=adapter_instance,
            entity_class=entity_class)

    @staticmethod
    def init_game_point_list(games):
        game_point_list = list()
        for game in games:
            game_point_list.append(GamePoints(
                game_id=game.entity_id,
                victories=game.victories or 0
            ))
        return game_point_list

    def _init_console_list(self, consoles_json):
        console_list = list()
        for item in consoles_json:
            console = self.console_adapter.get_by_id(item['entity_id'])
            game_point_list = self.init_game_point_list(console.games)
            player_console = PlayerConsoles(
                console_id=console.entity_id,
                tag_name=item['tag_name'],
                game_points=game_point_list
            )
            console_list.append(player_console)
        return console_list

    def _init_entity(self):
        data = self.request.json_data
        player: Player = self.adapter_instance.get_by_id(data['entity_id'])
        player.consoles = self._init_console_list(data['consoles'])
        return player


class PostPlayerAcceptTermsInteractor(BasicPostInteractor):
    def _init_entity(self):
        data = self.request.json_data
        player: Player = self.adapter_instance.get_by_id(data['entity_id'])
        player.terms = True
        return player
