from playerstars_domain import \
    Player, StarTransaction, SourceOperationType, OperationType, CoinType
import logging


class SaveConvertedStarsException(Exception):
    pass


class SaveConvertedStarsRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.gold_stars = json_data['gold_stars']
        self.red_stars = json_data['red_stars']


class SaveConvertedStarsResponseModel:
    def __init__(self, saved_player):
        self.saved_player = saved_player

    def __call__(self):
        return self.saved_player


class SaveConvertedStarsInteractor:
    def __init__(self,
                 request: SaveConvertedStarsRequestModel,
                 player_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.logger = logging.getLogger(__name__)

    def execute_operations(self, player):
        gold_debit = StarTransaction(
            self.request.gold_stars, 'Convert Stars',
            source=SourceOperationType.FINANCIAL_TRANSACTION)
        red_credit = StarTransaction(
            self.request.red_stars, 'Convert Stars', OperationType.CREDIT,
            CoinType.RED_STAR, SourceOperationType.FINANCIAL_TRANSACTION)

        player.add_star_transaction(gold_debit)
        player.add_star_transaction(red_credit)
        return player

    def run(self):
        try:
            player: Player = self.player_adapter.get_by_id(
                self.request.player_id)
            player = self.execute_operations(player)
            player.set_adapter(self.player_adapter)
            player_id = player.save()
            response = SaveConvertedStarsResponseModel(player_id)
            return response()
        except Exception as exc:
            msg = 'Erro ao salvar novo saldo de stars: {}'.format(exc)
            self.logger.error(msg)
            raise SaveConvertedStarsException(msg)
