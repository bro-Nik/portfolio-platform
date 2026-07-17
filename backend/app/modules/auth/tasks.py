from app.core.taskiq import broker
from app.modules.auth.services.email import EmailService


@broker.task(task_name='send_verification_email')
async def send_verification_email(email: str, token: str) -> None:
    await EmailService.send_verification_email(email, token)
