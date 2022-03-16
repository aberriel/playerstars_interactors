from botocore.exceptions import ClientError
from playerstars_domain import Player
from playerstars_mail.ses_mail import SesMail
from playerstars_interactors import (
    SendContactMailInteractor,
    SendContactMailRequestModel,
    SendInvitationMailInteractor,
    SendInvitationMailRequestModel,
    SendWelcomeMailInteractor,
    SendWelcomeMailRequestModel
)
from unittest.mock import MagicMock, patch

import pytest


json_data = dict(
    recipients=['teste', 'teste1'],
    data={},
    template='WELCOME_MESSAGE',
    sender='tete@teste.com.br',
    subject='TESTANDO',
    contact_message='Mensagem de teste que enviei'
)
player_json = {
    "player_status": "OFFLINE",
    "golden_star_balance": 0,
    "terms": True,
    "purchases": [
        {
            "product": {
                "price": 1050,
                "star_value": 3,
                "description": "teste",
                "star_type": "gold",
                "duration": 0
            },
            "purchase_datetime": "2017-11-21T09:58:00+00:00",
            "purchase_type": "GOLDEN_STAR_PURCHASE",
            "payment": {
                "payment_datetime": "2017-11-22T09:58:00+00:00",
                "payment_type": "PAGSEGURO",
                "code": "schrubles123"
            }
        }
    ],
    "entity_id": "acbf5816-3a14-4bf1-a0d3-19efda0151d0",
    "favorites": [
        "ght232141-3a12-5t67-19ehdufasuu"
    ],
    "states_regions": ['id123'],
    "consoles": [
        {
            "console_id": "1",
            "game_points": [
                {
                    'game_id': '11',
                    'victories': 0
                }
            ],
            "tag_name": "Leoplay4"
        }
    ],
    "user": {
        "date_birth": "2019-09-13",
        "street": 'Avenida Brasil',
        "street_number": '500',
        "street_complement": 'apt 607',
        "neighborhood": 'pechinchão',
        "name": "Dada",
        "city": "Rio de Janeiro",
        "state": "RJ",
        "nickname": "leobarnaud",
        "postal_code": "23575275",
        "cpf": "09022715043",
        "profile_image": 'asiuahdiuahsiuasia',
        "country": "Brasil",
        "phone_number": "11111111111",
        "email": "wapilejig@mail-guru.net"
    },
    "red_star_balance": 15,
    "points": 100,
    "countries_regions": ['id123'],
    "star_transactions": [
        {
            "value": 2,
            "operation_type": "DEBIT",
            "operation_date": "2019-08-21T13:11:07+00:00",
            "coin_type": "GOLDEN_STAR",
            "source": "DUEL",
            "source_id": "68dc45c5-43eb-4351-bead-4319aba7af85"
        }
    ]
}
player = Player.from_json(player_json)


player_adapter_send_email = MagicMock(
    _create_table_if_dont_exists=MagicMock(),
    get_by_id=MagicMock(return_value=player))


# noinspection PyUnusedLocal
@patch('boto3.resource')
@patch.object(SesMail, 'send_email', autospec=True)
@patch.object(SesMail, '_get_client')
def test_post_contact_email(get_client, send_email, resource):
    request = SendContactMailRequestModel(
        json_data, player, 'teste@teste.com.br')
    interactor = SendContactMailInteractor(request, player_adapter_send_email)
    interactor.run()
    send_email.assert_called_once()


# noinspection PyUnusedLocal
@patch('boto3.resource')
@patch.object(SesMail, 'send_email')
@patch.object(SesMail, '_get_client')
def test_post_contact_email_raises_by_none_contact_message(
        get_client, send_email, resource):
    mail_data = dict(
        recipients=['teste', 'teste1'],
        data={},
        template='WELCOME_MESSAGE',
        sender='tete@teste.com.br',
        subject='TESTANDO',
    )
    request = SendContactMailRequestModel(
        mail_data, 'teste@teste.com.br', player.entity_id)
    interactor = SendContactMailInteractor(request, player_adapter_send_email)
    with pytest.raises(BaseException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'A mensagem de contato não foi fornecida'


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('playerstars_mail.ses_mail.SesMail._get_client',
       side_effect=ClientError(MagicMock(), MagicMock()))
def test_post_contact_email_raises(send_email, resource):
    request = SendContactMailRequestModel(
        json_data, 'teste@teste.com.br', player.entity_id)
    interactor = SendContactMailInteractor(request, player_adapter_send_email)
    with pytest.raises(BaseException) as excinfo:
        interactor.run()
    assert str(excinfo.value)


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('playerstars_mail.ses_mail.SesMail._get_client',
       side_effect=BaseException('oops'))
def test_post_contact_email_raises_unknow(send_email, resource):
    request = SendContactMailRequestModel(
        json_data, 'teste@teste.com.br', player.entity_id)
    interactor = SendContactMailInteractor(request, player_adapter_send_email)
    with pytest.raises(BaseException) as excinfo:
        interactor.run()
    assert str(excinfo.value) == 'Erro desconhecido ao enviar o email: oops'


# noinspection PyUnusedLocal
@patch('boto3.resource')
@patch.object(SesMail, 'send_email')
@patch.object(SesMail, '_get_client')
def test_post_friend_invitation_email(get_client, send_email, resource):
    request = SendInvitationMailRequestModel(json_data, '123')
    interactor = SendInvitationMailInteractor(
        request=request,
        adapter_instance=player_adapter_send_email,
        sender_email='schrubles@stormsec.com.br')
    response = interactor.run()
    send_email.assert_called_once()
    assert response


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('playerstars_mail.ses_mail.SesMail._get_client',
       side_effect=ClientError(MagicMock(), MagicMock()))
def test_post_friend_invitation_email_raises(send_email, resource):
    request = SendInvitationMailRequestModel(json_data, player)
    interactor = SendInvitationMailInteractor(
        request=request,
        adapter_instance=player_adapter_send_email,
        sender_email='schrubles@stormsec.com.br')
    interactor.run()


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('playerstars_mail.ses_mail.SesMail._get_client',
       side_effect=BaseException('oops'))
def test_post_friend_invitation_email_raises_unknow(send_email, resource):
    request = SendInvitationMailRequestModel(json_data, player)
    interactor = SendInvitationMailInteractor(
        request=request,
        adapter_instance=player_adapter_send_email,
        sender_email='schrubles@stormsec.com.br')
    interactor.run()


# noinspection PyUnusedLocal
@patch('boto3.resource')
@patch.object(SesMail, 'send_email')
@patch.object(SesMail, '_get_client')
def test_post_welcome_email(get_client, send_email, resource):
    request = SendWelcomeMailRequestModel(json_data, player)
    interactor = SendWelcomeMailInteractor(request, player_adapter_send_email)
    interactor.run()
    send_email.assert_called_once()


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('playerstars_mail.ses_mail.SesMail._get_client',
       side_effect=ClientError(MagicMock(), MagicMock()))
def test_post_welcome_email_raises(send_email, resource):
    request = SendWelcomeMailRequestModel(json_data, player)
    interactor = SendWelcomeMailInteractor(request, player_adapter_send_email)
    interactor.run()


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
@patch('boto3.resource')
@patch('playerstars_mail.ses_mail.SesMail._get_client',
       side_effect=BaseException('oops'))
def test_post_welcome_email_raises_unknow(send_email, resource):
    request = SendWelcomeMailRequestModel(json_data, player)
    interactor = SendWelcomeMailInteractor(request, player_adapter_send_email)
    interactor.run()
