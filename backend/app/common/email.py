"""Общая отправка писем для всех модулей.

Каждый модуль держит свои Jinja-шаблоны; мейлер — только транспорт и рендер.
Правило слоёв: код, переиспользуемый двумя и более модулями, живёт в common/.
"""

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core import settings

logger = logging.getLogger(__name__)


class Mailer:
    def __init__(self, template_dir: Path, favicon_path: Path | None = None) -> None:
        self._env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)
        self._favicon_path = favicon_path

    def _smtp_disabled(self, what: str, email: str) -> bool:
        if settings.smtp_enabled:
            return False
        logger.info('SMTP не настроен — пропускаем %s для %s', what, email)
        return True

    def _render(self, template_name: str, context: dict) -> tuple[str, str]:
        html = self._env.get_template(f'{template_name}.html').render(**context)
        text = self._env.get_template(f'{template_name}.txt').render(**context)
        return html, text

    def _build_message(self, subject: str, email: str, html: str, text: str) -> MIMEMultipart:
        msg_alt = MIMEMultipart('alternative')
        msg_alt.attach(MIMEText(text, 'plain', 'utf-8'))
        msg_alt.attach(MIMEText(html, 'html', 'utf-8'))

        if self._favicon_path is not None and self._favicon_path.exists():
            related = MIMEMultipart('related')
            related.attach(msg_alt)

            with self._favicon_path.open('rb') as f:
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

    async def send(self, email: str, subject: str, template_name: str, context: dict, *, what: str) -> None:
        """Отрендерить шаблон и отправить письмо; без SMTP — залогировать и пропустить."""
        if self._smtp_disabled(what, email):
            return
        html, text = self._render(template_name, context)
        msg = self._build_message(subject, email, html, text)
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=settings.smtp_enabled,
        )
