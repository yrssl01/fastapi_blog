from src.utils.emails import generate_test_email, send_email
from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_active_superuser
from pydantic import EmailStr
from src.schemas.message import Message


router = APIRouter(tags=["utils"])


@router.post("/send-test-email", dependencies=[Depends(get_current_active_superuser)])
def test_email(email_to: EmailStr) -> Message:
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to, 
        subject=email_data.subject, 
        html_content=email_data.html_content
    )
    return Message(message="Test email sent")