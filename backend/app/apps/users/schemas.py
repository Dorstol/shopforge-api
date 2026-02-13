from typing import Annotated

from apps.core.schemas import IdSchema
from password_strength import PasswordPolicy
from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator


class UserPassword(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        policy = PasswordPolicy.from_names(
            length=8,
            uppercase=1,
            numbers=1,
            special=1,
        )

        error_list = policy.test(v)

        if not error_list:
            return v

        error_messages = []
        for error in error_list:
            error_name = error.name()
            if error_name == "length":
                error_messages.append(
                    f"Password must be at least {error.length} characters long"
                )
            elif error_name == "uppercase":
                error_messages.append(
                    f"Password must contain at least {error.count} uppercase letter(s)"
                )
            elif error_name == "numbers":
                error_messages.append(
                    f"Password must contain at least {error.count} number(s)"
                )
            elif error_name == "special":
                error_messages.append(
                    f"Password must contain at least {error.count} special character(s)"
                )
        raise ValueError("; ".join(error_messages))


class BaseUser(BaseModel):
    email: EmailStr = Field(description="User email", example="user@example.com")
    name: Annotated[
        str,
        StringConstraints(
            pattern=r"^[0-9a-zA-Zа-яА-ЯїЇяЯєЄіІґҐ_.'\- ]+$",
            min_length=2,
            max_length=32,
            strip_whitespace=True,
        ),
    ] = Field(example="JohnDoe")


class UserCreate(BaseUser, UserPassword):
    pass


class UserCreated(BaseUser, IdSchema):
    model_config = {
        "from_attributes": True,
    }
