from playerstars_domain import Console
import logging


class DeleteGameError(Exception):
    pass


class DeleteGameRequestModel:
    def __init__(self, entity_id):
        self.entity_id = entity_id


class DeleteGameResponseModel:
    def __init__(self, deleted_id):
        self.deleted_id = deleted_id

    def __call__(self):
        return self.deleted_id if self.deleted_id else None


class DeleteGameInteractor:
    def __init__(self,
                 request: DeleteGameRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance
        self.logger = logging.getLogger(__name__)

    def _find_game_in_console(self, consoles):
        for console in consoles:
            list_game_ids = [game.entity_id for game in console.games]
            if self.request.entity_id in list_game_ids:
                return console

    def _delete_game(self, console: Console):
        new_games = list()
        for game in console.games:
            if self.request.entity_id != game.entity_id:
                new_games.append(game)
        return Console(
            entity_id=console.entity_id,
            name=console.name,
            games=new_games,
            logo_path=console.logo_path,
            tag_name=console.tag_name
        )

    def run(self):
        consoles = self.adapter_instance.list_all()
        if not consoles:
            raise DeleteGameError('Nenhum console encontrado')
        console: Console = self._find_game_in_console(consoles)
        new_console: Console = self._delete_game(console)
        new_console.set_adapter(self.adapter_instance)
        try:
            new_console.save()
            deleted_id = self.request.entity_id
            response = DeleteGameResponseModel(deleted_id)
            return response()
        except Exception as ex:
            msg = f'Erro deletando game: {ex}'
            self.logger.error(msg)
            raise DeleteGameError(msg)
