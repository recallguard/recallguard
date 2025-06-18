from __future__ import annotations

from pathlib import Path
from os import getenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def parse_language(header: str | None) -> str:
    if header and header.lower().startswith('es'):
        return 'es'
    return 'en'


def render_template(name: str, context: dict, lang: str = 'en') -> str:
    path = Path('emails') / lang / name
    if not path.exists():
        path = Path('emails') / name
    html = path.read_text()
    for key, val in context.items():
        html = html.replace(f"{{{{{key}}}}}", str(val))
    return html


def send_email(to_email: str, subject: str, template: str, context: dict, lang: str = 'en') -> None:
    html = render_template(template, context, lang)
    api_key = getenv("SENDGRID_API_KEY")
    message = Mail(
        from_email=getenv("ALERTS_FROM_EMAIL", "noreply@example.com"),
        to_emails=to_email,
        subject=subject,
        html_content=html,
    )
    if api_key:
        try:
            sg = SendGridAPIClient(api_key)
            sg.send(message)
        except Exception:
            pass
    else:
        print("send email", to_email, subject, html)
