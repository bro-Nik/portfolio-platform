from pathlib import Path

from app.common.email import Mailer
from app.core import settings

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / 'templates' / 'email'
FAVICON_PATH = TEMPLATE_DIR / 'favicon.png'

_mailer = Mailer(TEMPLATE_DIR, FAVICON_PATH)


class EmailService:
    @staticmethod
    def build_verification_link(token: str) -> str:
        return f'{settings.frontend_url}/login?token={token}'

    @staticmethod
    def build_password_reset_link(token: str) -> str:
        return f'{settings.frontend_url}/reset-password?token={token}'

    @staticmethod
    async def send_password_reset_confirmation_email(email: str) -> None:
        await _mailer.send(
            email,
            'Пароль был изменён',
            'reset_password_confirmation',
            {
                'email': email,
                'frontend_url': settings.frontend_url,
            },
            what='письмо подтверждения смены пароля',
        )

    @staticmethod
    async def send_verification_email(email: str, token: str) -> None:
        await _mailer.send(
            email,
            'Подтверждение регистрации',
            'verify_email',
            {
                'email': email,
                'link': EmailService.build_verification_link(token),
                'frontend_url': settings.frontend_url,
            },
            what='письмо подтверждения email',
        )

    @staticmethod
    async def send_password_reset_email(email: str, token: str) -> None:
        await _mailer.send(
            email,
            'Сброс пароля',
            'reset_password',
            {
                'email': email,
                'link': EmailService.build_password_reset_link(token),
                'frontend_url': settings.frontend_url,
            },
            what='письмо сброса пароля',
        )
