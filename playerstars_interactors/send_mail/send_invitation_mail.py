from botocore.exceptions import ClientError
from playerstars_domain import Player
from playerstars_interactors.utils.send_mail import send_email
from playerstars_mail.mail_templates import MailTemplate

import logging


class SendInvitationMailRequestModel:
    def __init__(self, json_data, player_id):
        self.recipients = json_data['recipients']
        self.player_id = player_id


class SendInvitationMailInteractor:
    def __init__(self,
                 request: SendInvitationMailRequestModel,
                 adapter_instance, sender_email):
        self.request = request
        self.adapter_instance = adapter_instance
        self.sender_email = sender_email
        self.logger = logging.getLogger(__name__)

    def run(self):
        player: Player = self.adapter_instance.get_by_id(
            self.request.player_id)

        try:
            response = send_email(
                player_name=player.user.name,
                template=MailTemplate.FRIEND_INVITATION,
                sender=self.sender_email,
                recipients=self.request.recipients,
                subject="Encontre seus amigos no PlayerStars!",
                mail_data=''
            )
        except ClientError as exc:
            msg = 'Erro ao enviar o email:' + exc.response['Error']['Message']
            self.logger.error(msg)
        except BaseException as exc:
            msg = 'Erro desconhecido ao enviar o email: ' + str(exc)
            self.logger.error(msg)
        else:
            return response
