from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core import settings


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / 'templates' / 'email'
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
FAVICON_PATH = TEMPLATE_DIR / 'favicon.png'


class EmailService:
    @staticmethod
    def build_verification_link(token: str) -> str:
        return f'{settings.frontend_url}/login?token={token}'

    @staticmethod
    def build_password_reset_link(token: str) -> str:
        return f'{settings.frontend_url}/reset-password?token={token}'

    @staticmethod
    async def send_password_reset_confirmation_email(email: str) -> None:
        subject = 'Пароль был изменён'
        context = {
            'email': email,
            'frontend_url': settings.frontend_url,
        }

        html = jinja_env.get_template('reset_password_confirmation.html').render(**context)
        text = jinja_env.get_template('reset_password_confirmation.txt').render(**context)

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

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=bool(settings.smtp_host not in ('', 'mailpit', 'localhost')),
        )

    @staticmethod
    async def send_verification_email(email: str, token: str) -> None:
        link = EmailService.build_verification_link(token)
        subject = 'Подтверждение регистрации'
        context = {
            'email': email,
            'link': link,
            'frontend_url': settings.frontend_url,
        }

        html = jinja_env.get_template('verify_email.html').render(**context)
        text = jinja_env.get_template('verify_email.txt').render(**context)

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

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=bool(settings.smtp_host not in ('', 'mailpit', 'localhost')),
        )

    @staticmethod
    async def send_password_reset_email(email: str, token: str) -> None:
        link = EmailService.build_password_reset_link(token)
        subject = 'Сброс пароля'
        context = {
            'email': email,
            'link': link,
            'frontend_url': settings.frontend_url,
        }

        html = jinja_env.get_template('reset_password.html').render(**context)
        text = jinja_env.get_template('reset_password.txt').render(**context)

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

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=bool(settings.smtp_host not in ('', 'mailpit', 'localhost')),
        )
