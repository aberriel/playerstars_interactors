from botocore.exceptions import ClientError
from playerstars_domain import Player
from playerstars_interactors.utils.send_mail import send_email
from playerstars_mail.mail_templates import MailTemplate

import logging


class SendWelcomeMailRequestModel:
    def __init__(self, json_data, player_id):
        self.recipients = json_data['recipients']
        self.data = json_data['data']
        self.sender = json_data['sender']
        self.subject = json_data['subject']
        self.player_id = player_id


class SendWelcomeMailInteractor:
    def __init__(self,
                 request: SendWelcomeMailRequestModel,
                 adapter_instance):
        self.request = request
        self.adapter_instance = adapter_instance
        self.logger = logging.getLogger(__name__)

    def run(self):
        player: Player = self.adapter_instance.get_by_id(
            self.request.player_id)

        try:
            response = send_email(
                player_name=player.user.name,
                template=MailTemplate.WELCOME_MESSAGE,
                sender=self.request.sender,
                recipients=self.request.recipients,
                subject=self.request.subject,
                mail_data=self.request.data
            )
        except ClientError as exc:
            msg = 'Erro ao enviar o email:' + exc.response['Error']['Message']
            self.logger.error(msg)
        except BaseException as exc:
            msg = 'Erro desconhecido ao enviar o email: ' + str(exc)
            self.logger.error(msg)
        else:
            return response
