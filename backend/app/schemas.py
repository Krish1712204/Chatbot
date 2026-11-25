"""Shapes of data going in and out of the API. FastAPI checks requests against these."""

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, field_validator


def _clean_email(value: str) -> str:
    # check_deliverability=False: only check the format, don't look up the domain online.
    try:
        return validate_email(value.strip(), check_deliverability=False).normalized.lower()
    except EmailNotValidError:
        raise ValueError("Please enter a valid email address")


class RegisterIn(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def check_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Please enter your name")
        if len(v) > 100:
            raise ValueError("Name must be 100 characters or less")
        return v

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return _clean_email(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v.encode()) > 72:  # bcrypt's limit (in bytes, so emoji count as several)
            raise ValueError("Password is too long (max 72 characters)")
        return v


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return _clean_email(v)


class UserOut(BaseModel):
    # from_attributes: allows building this from a database User object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class AuthOut(BaseModel):
    token: str
    user: UserOut
