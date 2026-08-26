from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core import settings

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / 'templates' / 'email'
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
FAVICON_PATH = TEMPLATE_DIR / 'favicon.png'


class EmailService:
    @staticmethod
    def _smtp_disabled(what: str, email: str) -> bool:
        if settings.smtp_enabled:
            return False
        logger.info('SMTP не настроен — пропускаем %s для %s', what, email)
        return True

    @staticmethod
    def build_verification_link(token: str) -> str:
        return f'{settings.frontend_url}/login?token={token}'

    @staticmethod
    def build_password_reset_link(token: str) -> str:
        return f'{settings.frontend_url}/reset-password?token={token}'

    @staticmethod
    def _render(template_name: str, context: dict) -> tuple[str, str]:
        html = jinja_env.get_template(f'{template_name}.html').render(**context)
        text = jinja_env.get_template(f'{template_name}.txt').render(**context)
        return html, text

    @staticmethod
    def _build_message(subject: str, email: str, html: str, text: str) -> MIMEMultipart:
        msg_alt = MIMEMultipart('alternative')
        msg_alt.attach(MIMEText(text, 'plain', 'utf-8'))
        msg_alt.attach(MIMEText(html, 'html', 'utf-8'))

        if FAVICON_PATH.exists():
            related = MIMEMultipart('related')
            related.attach(msg_alt)

            with open(FAVICON_PATH, 'rb') as f:
                img = MIMEImage(f.read(), _subtype='png')
            img.add_header('Content-ID', '<favicon@portfolios.app>')
            img.add_header('Content-Disposition', 'inline', filename='favicon.png')
            related.attach(img)

            msg = related
        else:
            msg = msg_alt

        msg['Subject'] = subject
        msg['From'] = settings.smtp_from_email
        msg['To'] = email
        return msg

    @staticmethod
    async def send_password_reset_confirmation_email(email: str) -> None:
        if EmailService._smtp_disabled('письмо подтверждения смены пароля', email):
            return
        html, text = EmailService._render('reset_password_confirmation', {
            'email': email,
            'frontend_url': settings.frontend_url,
        })
        msg = EmailService._build_message('Пароль был изменён', email, html, text)
        await EmailService._send(msg)

    @staticmethod
    async def send_verification_email(email: str, token: str) -> None:
        if EmailService._smtp_disabled('письмо подтверждения email', email):
            return
        html, text = EmailService._render('verify_email', {
            'email': email,
            'link': EmailService.build_verification_link(token),
            'frontend_url': settings.frontend_url,
        })
        msg = EmailService._build_message('Подтверждение регистрации', email, html, text)
        await EmailService._send(msg)

    @staticmethod
    async def send_password_reset_email(email: str, token: str) -> None:
        if EmailService._smtp_disabled('письмо сброса пароля', email):
            return
        html, text = EmailService._render('reset_password', {
            'email': email,
            'link': EmailService.build_password_reset_link(token),
            'frontend_url': settings.frontend_url,
        })
        msg = EmailService._build_message('Сброс пароля', email, html, text)
        await EmailService._send(msg)

    @staticmethod
    async def _send(msg: MIMEMultipart) -> None:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=settings.smtp_enabled,
        )
