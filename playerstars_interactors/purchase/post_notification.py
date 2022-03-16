from urllib.parse import parse_qs
import requests
import defusedxml.ElementTree as Et
from playerstars_domain import (
    PagSeguroStatus, PagSeguroPaymentTransaction, Player)
from playerstars_adapters import PlayerAdapter, ProductAdapter


class PagSeguroException(BaseException):
    pass


class PostNotificationRequestModel:
    def __init__(self, post_body):
        data = parse_qs(post_body.decode('utf-8'))
        self.code = data['notificationCode'][0]
        self.type = data['notificationType'][0]


class PostNotificationResponseModel:
    def __init__(self, player_id):
        self.player_id = player_id

    def __call__(self):
        return self.player_id


def get_player_adapter(settings):
    return PlayerAdapter(settings.PLAYER_TABLE_NAME, settings.DYNAMODB_URL)


def get_token(settings):
    sandbox_token = settings.PAGSEGURO_SANDBOX_TOKEN
    token = settings.PAGSEGURO_TOKEN
    is_sandbox = settings.PAGSEGURO_SANDBOX_ENABLE
    return sandbox_token if is_sandbox else token


def get_pagseguro_host(settings):
    is_sandbox = settings.PAGSEGURO_SANDBOX_ENABLE
    pagseguro_url_prefix = [
        settings.PAGSEGURO_HOST_URL,
        settings.PAGSEGURO_SANDBOX_HOST_URL
    ]
    return pagseguro_url_prefix[is_sandbox]


def get_pagseguro_notifications_url(notification_code, settings):
    email = settings.PAGSEGURO_EMAIL
    token = get_token(settings)
    host = get_pagseguro_host(settings)
    notification_url = settings.PAGSEGURO_UPDATE_NOTIFICATION_URL.format(
        notification_code=notification_code,
        host=host, email=email, token=token)
    return notification_url


def create_new_transaction(code, status):
    status_enum = PagSeguroStatus.get_from_int(status)
    return PagSeguroPaymentTransaction(code=code, status=status_enum)


def parse_transaction_response(response_content):
    root = Et.fromstring(response_content)
    try:
        code = root.find('code').text
        reference = root.find('reference').text
        status = int(root.find('status').text)
        item_id = root.find('items').find('item').find('id').text
    except Exception as e:
        msg = 'Erro lendo retorno da transação: {}'.format(str(e))
        raise ValueError(msg)

    new_transaction = create_new_transaction(code, status)
    return dict(
        transaction=new_transaction,
        reference=reference,
        item_id=item_id)


def find_player_by_reference(reference, settings):
    players = get_player_adapter(settings).list_all()
    for player in players:
        for purchase in player.purchases:
            if purchase.payment.code == reference:
                return player

    raise PagSeguroException(f'Não encontrado um player que possui'
                             f' uma compra com essa referência" {reference}')


def last_status_not_equals_transaction_status(transaction, purchase):
    last_value = purchase.get_last_status().value \
        if purchase.get_last_status() else None
    if transaction.status.value != last_value:
        return True
    return False


def reference_equals_code(purchase, reference):
    return purchase.payment.code == reference


def add_transaction_by_reference(player, parsed_response):
    reference = parsed_response['reference']
    transaction = parsed_response['transaction']
    for purchase in player.purchases:
        if reference_equals_code(purchase, reference) and \
                last_status_not_equals_transaction_status(
                    transaction, purchase):
            purchase.payment.add_transaction(
                status=transaction.status,
                code=transaction.code,
                transaction_datetime=transaction.transaction_datetime)
            return True
    return False


def get_product(item_id, settings):
    adapter = ProductAdapter(
        settings.PRODUCT_TABLE_NAME, settings.DYNAMODB_URL)
    product = adapter.get_by_id(item_id)
    return product


def add_balance(player, product):
    if product.star_type == 'red':
        player.red_star_balance += product.star_value
    elif product.star_type == 'gold':
        player.golden_star_balance += product.star_value
    else:
        raise BaseException('Star Type invalido')
    return player


def add_balance_if_purchase_accepted(player, parsed_response, settings):
    if parsed_response['transaction'].status.value == 'PAID':
        product = get_product(parsed_response['item_id'], settings)
        player = add_balance(player, product)
    return player


class PostNotificationInteractor:
    def __init__(self,
                 request: PostNotificationRequestModel,
                 settings,
                 player_adapter):
        self.request = request
        self.player_adapter = player_adapter
        self.settings = settings

    def _make_request(self, url):
        response = requests.get(url=url)
        if response.status_code != 200:
            msg = f'GET de notificação para {url} falhou status code: ' \
                f'{response.status_code}' \
                f'código da notificação {self.request.code}'
            raise PagSeguroException(msg)
        return response

    def run(self):
        pagseguro_url = get_pagseguro_notifications_url(
            self.request.code, self.settings)
        response = self._make_request(pagseguro_url)
        try:
            parsed_response = parse_transaction_response(response.content)
            player: Player = find_player_by_reference(
                parsed_response['reference'], self.settings)

            transaction_added = add_transaction_by_reference(
                player, parsed_response)

            if transaction_added:
                player = add_balance_if_purchase_accepted(
                    player, parsed_response, self.settings)

            player.set_adapter(get_player_adapter(self.settings))
            player_id = player.save()
            response = PostNotificationResponseModel(player_id)
        except BaseException as e:
            msg = f"Falha ao salvar o player com a nova notificação: {str(e)}"
            raise PagSeguroException(msg)
        return response()
