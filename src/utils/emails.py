from pathlib import Path
from dataclasses import dataclass
from typing import Any

import emails
import jwt
from jinja2 import Template
from src.core.config import settings
from src.logger import logger


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
        *,
        email_to: str,
        subject: str = "",
        html_content: str = ""
):
    assert settings.emails_enabled, "Email variables are not configured"
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={
            "project_name": project_name,
            "email": email_to
        }
    )
    return EmailData(html_content=html_content, subject=subject)
    

def generate_password_reset_email(email_to: str, email: str, token: str):
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"127.0.0.1:8000/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": project_name,
            "username": email,
            "email": email_to,
            "valid_minutes": settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES,
            "link": link
        }
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_verification_email(email_to: str, email: str, token: str):
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Verify your email"
    link = f"127.0.0.1:8000/verify-email?token={token}"
    html_content = render_email_template(
        template_name="verify_email.html",
        context={
            "project_name": project_name,
            "username": email,
            "email": email_to,
            "valid_minutes": settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
            "link": link
        }
    )
    return EmailData(html_content=html_content, subject=subject)