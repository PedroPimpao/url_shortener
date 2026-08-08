import smtplib
from email.message import EmailMessage

from ..config import settings


class EmailDeliveryError(Exception):
    pass


class EmailService:
    @staticmethod
    def send_password_reset_otp(recipient: str, otp: str) -> None:
        if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
            raise EmailDeliveryError("Serviço de email indisponível")

        message = EmailMessage()
        message["Subject"] = "Código para recuperação de senha"
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = recipient
        message.set_content(
            f"Seu código de recuperação é {otp}. "
            f"Ele expira em {settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES} minutos."
        )

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                if settings.SMTP_USE_TLS:
                    smtp.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            raise EmailDeliveryError("Serviço de email indisponível") from error
