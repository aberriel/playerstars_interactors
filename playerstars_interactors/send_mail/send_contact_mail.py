from botocore.exceptions import ClientError
from playerstars_domain import Player
from playerstars_interactors.utils.send_mail import send_email
from playerstars_mail.mail_templates import MailTemplate

import logging


class SendContactMailRequestModel:
    def __init__(self, json_data, receiver_email, player_id=None):
        self.recipients = [receiver_email]
        self.data = json_data.get('data')
        self.contact_message = json_data.get('contact_message', None)
        self.subject = json_data.get('subject')
        self.sender_name = json_data.get('sender_name', None)
        self.sender_mail = json_data.get('sender_mail', None)
        self.player_id = player_id


class SendContactMailInteractor:
    def __init__(self,
                 request: SendContactMailRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance
        self.logger = logging.getLogger(__name__)

    def get_email_data(self, player):
        player_name = self.request.sender_name
        sender = self.request.sender_mail
        player_id = None
        if player:
            player_name = player.user.name
            sender = player.user.email
            player_id = player.entity_id
        return [player_name, sender, player_id]

    def run(self):
        if not self.request.contact_message:
            raise Exception('A mensagem de contato não foi fornecida')
        try:
            player: Player = self.adapter_instance.get_by_id(
                self.request.player_id) if self.request.player_id \
                else None
            email_data = self.get_email_data(player)
            response = send_email(
                player_name=email_data[0],
                sender=email_data[1],
                player_id=email_data[2],
                template=MailTemplate.CONTACT_MESSAGE,
                recipients=self.request.recipients,
                subject=self.request.subject,
                mail_data=self.request.data,
                additional_params={
                    'contact_message': self.request.contact_message
                }
            )
            return response
        except ClientError as exc:
            msg = 'Erro ao enviar o email:' + exc.response['Error']['Message']
            self.logger.error(msg)
            raise ClientError(msg, 'erro ao enviar email de contato')
        except BaseException as exc:
            msg = 'Erro desconhecido ao enviar o email: ' + str(exc)
            self.logger.error(msg)
            raise BaseException(msg)
