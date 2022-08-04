from fastapi import BackgroundTasks
from fastapi_mail import (FastMail,
                          MessageSchema,
                          ConnectionConfig)

from app import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USER,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_HOST,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)


def send_email(background_tasks: BackgroundTasks,
               subject: str,
               email: str,
               body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)