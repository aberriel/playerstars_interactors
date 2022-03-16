from playerstars_adapters import PlayerAdapter
from playerstars_domain import Player

import logging


class GetPurchaseHistoryRequestModel:
    def __init__(self, json_data):
        self.player_id = json_data['player_id']
        self.star_type = json_data.get('star_type', None)


class GetPurchaseHistoryResponseModel:
    def __init__(self, purchases: dict):
        self.purchases = purchases

    def __call__(self):
        return self.purchases


class GetPurchaseHistoryInteractor:
    def __init__(self,
                 request: GetPurchaseHistoryRequestModel,
                 player_adapter: PlayerAdapter):
        self.request = request
        self.player_adapter = player_adapter
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def filter_gold_star_durations(purchases):
        for purchase in purchases:
            if purchase['product']['star_type'] == 'gold':
                del purchase['product']['duration']
        return purchases

    @staticmethod
    def filter_by_star_type(purchases, star_type):
        if not star_type:
            return [purchase.to_json() for purchase in purchases]
        filtered_purchases = [purchase.to_json() for purchase in purchases if
                              purchase.product.star_type == star_type]
        return filtered_purchases

    def run(self):
        player: Player = self.player_adapter.get_by_id(self.request.player_id)
        if not player:
            raise BaseException(
                "Player {0} não existe".format(self.request.player_id)
            )

        purchases = player.list_purchases()
        filtered_purchases = self.filter_by_star_type(
            purchases, self.request.star_type)
        final_purchases = self.filter_gold_star_durations(filtered_purchases)
        response = GetPurchaseHistoryResponseModel(final_purchases)
        return response()
