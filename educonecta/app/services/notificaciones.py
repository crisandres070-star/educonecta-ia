from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

from app.config import get_settings

settings = get_settings()


def enviar_email(destinatario: str, asunto: str, contenido: str) -> None:
    client = SendGridAPIClient(settings.sendgrid_api_key)
    message = Mail(
        from_email="notificaciones@educonecta.cl",
        to_emails=destinatario,
        subject=asunto,
        plain_text_content=contenido,
    )
    client.send(message)


def enviar_whatsapp(destinatario: str, mensaje: str, from_number: str) -> None:
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    client.messages.create(
        from_=f"whatsapp:{from_number}",
        to=f"whatsapp:{destinatario}",
        body=mensaje,
    )
