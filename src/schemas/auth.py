import uuid
import re
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from src.core.config import settings


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: uuid.UUID | None = None


class TokenType(str, Enum):
    PASSWORD_RESET = 'password_reset'
    EMAIL_VERIFICATION = 'email_verification'

    @property
    def expiry_minutes(self) -> int:
        if self is TokenType.PASSWORD_RESET:
            return settings.EMAIL_RESET_TOKEN_EXPIRE_MINUTES
        elif self is TokenType.EMAIL_VERIFICATION:
            return settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES


class NewPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=64)

    @field_validator("new_password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Password must contain at least one special character')
        return value

