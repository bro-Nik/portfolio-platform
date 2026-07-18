from app.core.taskiq import broker
from app.modules.auth.services.email import EmailService


@broker.task(task_name='send_verification_email')
async def send_verification_email(email: str, token: str) -> None:
    await EmailService.send_verification_email(email, token)


@broker.task(task_name='send_password_reset_email')
async def send_password_reset_email(email: str, token: str) -> None:
    await EmailService.send_password_reset_email(email, token)


@broker.task(task_name='send_password_reset_confirmation_email')
async def send_password_reset_confirmation_email(email: str) -> None:
    await EmailService.send_password_reset_confirmation_email(email)
