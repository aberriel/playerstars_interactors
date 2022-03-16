from datetime import datetime
from playerstars_adapters import PlayerAdapter
from playerstars_domain import (
    GooglePurchase,
    PaymentLog,
    Player,
    PlayerSubscription)
from playerstars_interactors.utils.domain_utils import find_entity_by_id

import logging


class PostPurchaseNotificationByGoogleException(BaseException):
    pass


class PostPurchaseNotificationByGoogleRequestModel:
    def __init__(self, json_data: dict):
        self.player_id = json_data['player_id']
        self.order_id = json_data['orderId']
        self.product_id = json_data['productId']
        self.purchase_state = json_data['purchaseState']
        self.acknowledged = json_data['acknowledged']
        self.auto_renewing = json_data['autoRenewing']
        self.purchase_time = json_data['purchaseTime']
        self.expiration_datetime = json_data['expirationDateTime']
        self.purchase_token = json_data['purchaseToken']
        self.package_name = json_data['packageName']


class PostPurchaseNotificationByGoogleResponseModel:
    def __init__(self, player_id: str,
                 package_name: str,
                 expiration_datetime: datetime):
        self.player_id = player_id
        self.package_name = package_name
        self.expiration_datetime = expiration_datetime

    def __call__(self):
        return {
            'player_id': self.player_id,
            'package_name': self.package_name,
            'expiration_datetime': self.expiration_datetime.isoformat()}


class PostPurchaseNotificationByGoogleInteractor:
    def __init__(self,
                 request: PostPurchaseNotificationByGoogleRequestModel,
                 player_adapter: PlayerAdapter):
        self.request = request
        self.player_adapter = player_adapter
        self.logger = logging.getLogger(__name__)

    def _get_player(self):
        return find_entity_by_id(
            _id=self.request.player_id,
            adapter_instance=self.player_adapter,
            class_name='Player')

    def _mount_google_purchase(self):
        return GooglePurchase(
            orderId=self.request.order_id,
            productId=self.request.product_id,
            purchaseState=self.request.purchase_state,
            acknowledged=self.request.acknowledged,
            autoRenewing=self.request.auto_renewing,
            purchaseTime=self.request.purchase_time,
            expirationDateTime=datetime.fromisoformat(
                self.request.expiration_datetime),
            purchaseToken=self.request.purchase_token,
            packageName=self.request.package_name)

    def add_payment_log(self, player: Player, payment_log: PaymentLog):
        player.add_payment_log(payment_log)
        player.save()

    def update_player_subscription(self,
                                   player: Player,
                                   subscription: PlayerSubscription):
        player.subscription = subscription
        player.save()

    def run(self):
        try:
            player: Player = self._get_player()
            purchase_data = self._mount_google_purchase()
            self.update_player_subscription(
                player=player,
                subscription=purchase_data.mount_subscription())
            self.add_payment_log(
                player=player,
                payment_log=purchase_data.mount_payment_log())
            response = PostPurchaseNotificationByGoogleResponseModel(
                player_id=self.request.player_id,
                package_name=purchase_data.packageName,
                expiration_datetime=purchase_data.expirationDateTime)
            return response
        except Exception as exc:
            msg = f'Error during receive payment data from Google: ' \
                  f'{exc.__class__.__name__}: {exc}'
            self.logger.error(msg)
            raise PostPurchaseNotificationByGoogleException(msg)
