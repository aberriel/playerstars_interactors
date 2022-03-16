from playerstars_adapters import ConsoleAdapter, PlayerAdapter
from playerstars_domain import Player, Console
import logging


class GetPlayerConsolesRequestModel:
    def __init__(self, player_id):
        self.player_id = player_id


class GetPlayerConsolesResponseModel:
    def __init__(self, consoles):
        self.consoles = consoles

    def __call__(self):
        return self.consoles if self.consoles else list()


class GetPlayerConsolesInteractor:
    def __init__(self,
                 request: GetPlayerConsolesRequestModel,
                 console_adapter: ConsoleAdapter,
                 player_adapter: PlayerAdapter,
                 logger=None):
        self.request = request
        self.console_adapter = console_adapter
        self.player_adapter = player_adapter
        self.logger = logger or logging.getLogger(__name__)

    @staticmethod
    def format_games(games, game_points):
        game_list = list()
        for item in game_points:
            for game in games:
                if item.game_id == game.entity_id and game.active is True:
                    game_list.append({
                        "entity_id": game.entity_id,
                        "victories": item.victories,
                        "logo_path": game.logo_path,
                        "name": game.name
                    })
        return game_list

    def format_consoles(self, consoles):
        console_list = list()
        for item in consoles:
            console: Console = self.console_adapter.get_by_id(
                item.console_id)
            self.logger.info(f'Console encontrado: {console.name}, '
                             f'id: {console.entity_id},'
                             f'console games: {console.games}')
            console_dict = {
                "entity_id": console.entity_id,
                "name": console.name,
                "logo_path": console.logo_path,
                "tag_name": item.tag_name,
                "games": self.format_games(console.games, item.game_points)
            }
            if len(console_dict['games']) > 0:
                console_list.append(console_dict)
        return console_list

    def run(self):
        player: Player = self.player_adapter.get_by_id(
            self.request.player_id)
        if not player:
            self.logger.info(f"Player não encontrado")
            return list()
        self.logger.info(f"Player encontrado: {player.user.nickname}")
        self.logger.info(f"Consoles: {player.consoles}")
        formated_consoles = self.format_consoles(player.consoles)
        self.logger.info(f"formated consoles: {formated_consoles}")
        response = GetPlayerConsolesResponseModel(formated_consoles)
        return response()
