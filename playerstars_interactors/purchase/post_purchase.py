from defusedxml import ElementTree as Et
from playerstars_domain import (
    PagSeguroPayment,
    PagSeguroPaymentTransaction,
    Player,
    ProductPurchased,
    Purchase
)
from uuid import uuid4

import logging
import requests


pagseguro_url_prefix = [
    'https://ws.pagseguro.uol.com.br',
    'https://ws.sandbox.pagseguro.uol.com.br'
]


pagseguro_url_without_ws_prefix = [
    'https://pagseguro.uol.com.br',
    'https://sandbox.pagseguro.uol.com.br'
]


class PostPurchaseException(BaseException):
    pass


class PostPurchaseRequestModel:
    def __init__(self, json_data):
        self.price = json_data['price']
        self.description = json_data['description']
        self.product_id = json_data['product_id']
        self.star_value = json_data['star_value']
        self.star_type = json_data['star_type']
        self.duration = json_data['duration']


class PostPurchaseResponseModel:
    def __init__(self, session_id, player_id, is_sandbox):
        self.session_id = session_id
        self.player_id = player_id
        self.is_sandbox = is_sandbox

    def __call__(self):

        host = pagseguro_url_without_ws_prefix[self.is_sandbox]
        url_redirect = f'{host}/v2/checkout/payment.html?code' \
            f'={self.session_id}'
        return {'url_redirect': url_redirect,
                'played_id': self.player_id}


class PostPurchaseInteractor:
    def __init__(self,
                 request: PostPurchaseRequestModel,
                 player_id,
                 adapter_class,
                 settings):
        self.request = request
        self.player_id = player_id
        self.adapter_class = adapter_class
        self.settings = settings
        self.is_sandbox = self.settings.PAGSEGURO_SANDBOX_ENABLE
        self.logger = logging.getLogger(__name__)

    def get_pagseguro_url(self, email, token):
        host = pagseguro_url_prefix[self.is_sandbox]
        return '{host}/v2/{service}?email={email}&token={token}' \
            .format(host=host,
                    service='checkout',
                    email=email,
                    token=token)

    def _get_token(self):
        sbtoken = self.settings.PAGSEGURO_SANDBOX_TOKEN
        pdtoken = self.settings.PAGSEGURO_TOKEN
        is_sandbox = self.settings.PAGSEGURO_SANDBOX_ENABLE
        return sbtoken if is_sandbox else pdtoken

    def _create_payment_data_xml(self, code, settings):
        pagseguro_xml_string = """
        <checkout>
          <currency>BRL</currency>
          <items>
            <item>
              <id>{product_id}</id>
              <description>{description}</description>
              <amount>{price}</amount>
              <quantity>1</quantity>
              <weight>1</weight>
            </item>
          </items>
          <redirectURL>{return_url}</redirectURL>
          <notificationURL>{notification_url}</notificationURL>
          <reference>{code}</reference>
          <shipping>
            <addressRequired>false</addressRequired>
          </shipping>
          <timeout>{purchase_timeout}</timeout>
          <enableRecover>false</enableRecover>
        </checkout>
        """.format(
            price=format(int(self.request.price)/100, '.2f'),
            return_url=self.settings.RETURN_URL,
            description=self.request.description,
            product_id=self.request.product_id,
            purchase_timeout=self.settings.PURCHASE_OPERATION_TIMEOUT,
            code=code,
            notification_url=settings.PLAYERSTARS_NOTIFICATION_URL
        )
        return pagseguro_xml_string

    def _add_purchase_to_player(self, player_id, code):
        player: Player = self.adapter_class.get_by_id(player_id)
        payment = PagSeguroPayment(code=code)
        transaction = PagSeguroPaymentTransaction(
            code=code)
        payment.transactions.append(transaction)
        product = ProductPurchased(
            price=self.request.price,
            star_value=self.request.star_value,
            description=self.request.description,
            star_type=self.request.star_type,
            duration=self.request.duration)
        purchase = Purchase(product=product, payment=payment)
        player.add_purchase(purchase)
        return player

    def run(self):
        headers = {
            'Content-Type': 'application/xml; charset=UTF-8'
        }
        email = self.settings.PAGSEGURO_EMAIL
        token = self._get_token()
        url = self.get_pagseguro_url(email, token)
        code = uuid4()
        xml_body = self._create_payment_data_xml(code, self.settings)
        response = requests.post(url=url, headers=headers, data=xml_body)
        if response.status_code != 200:
            self._check_known_errors(response.content)
            self.logger.error('Content on error: {}'.format(response.content))
            raise PostPurchaseException(response.content.decode('ISO-8859-1'))

        try:
            session_id = Et.fromstring(response.content).find('code').text
            player: Player = self._add_purchase_to_player(
                self.player_id, code)
            player.set_adapter(self.adapter_class)
            player_id = player.save()
            response = PostPurchaseResponseModel(
                session_id, player_id, self.is_sandbox)
        except Exception as e:
            msg = 'Erro no retorno do PagSeguro: {}'.format(e)
            raise PostPurchaseException(msg)

        return response()

    @staticmethod
    def _check_known_errors(content):
        fingerprint = 'Houve um problema e não foi possível exibir a página'
        if fingerprint.encode('iso-8859-1') in content:
            raise PostPurchaseException('O Sandbox do Pagseguro '
                                        'retornou um erro.')
