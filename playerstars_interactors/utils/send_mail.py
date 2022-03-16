from datetime import datetime
from playerstars_mail.mail_templates import MailTemplate
from playerstars_mail.ses_mail import SesMail


def send_email(player_name,
               template,
               sender,
               recipients,
               subject,
               mail_data,
               player_id=None,
               additional_params=None):
    email_time = datetime.utcnow()

    message_template = template.value
    if template == MailTemplate.CONTACT_MESSAGE:
        # Neste caso, terei que pegar a mensagem deixada pelo usuário
        message = str(message_template).format(
            user_name=player_name,
            datetime=str(email_time),
            contact_subject=subject,
            contact_message=additional_params['contact_message'])
        subject = f"Contato do usuário {player_name}. Id: {player_id}."

    elif template == MailTemplate.FRIEND_INVITATION:
        message = str(message_template).format(
            user_name=player_name)
    else:
        message = str(message_template).format(
            user_name=player_name,
            datetime=str(email_time))
    ses_mail = SesMail(sender=sender,
                       recipients=recipients,
                       subject=subject,
                       body_html=message,
                       data=mail_data)
    return ses_mail.send_email()
