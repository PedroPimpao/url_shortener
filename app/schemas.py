import re

from pydantic import BaseModel, Field, field_validator, model_validator


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_and_validate_email(email: str) -> str:
    normalized_email = email.strip().lower()
    if len(normalized_email) > 255 or not EMAIL_PATTERN.fullmatch(normalized_email):
        raise ValueError("Email inválido")
    return normalized_email

class UserSchema(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
            from_attributes = True


class PasswordResetRequestSchema(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        return normalize_and_validate_email(email)


class PasswordResetVerifySchema(PasswordResetRequestSchema):
    otp: str = Field(pattern=r"^\d{6}$")


class PasswordResetCompleteSchema(BaseModel):
    reset_token: str = Field(min_length=32, max_length=255)
    new_password: str = Field(min_length=8, max_length=72)
    new_password_confirmation: str = Field(min_length=8, max_length=72)

    @field_validator("new_password", "new_password_confirmation")
    @classmethod
    def validate_bcrypt_length(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("A senha deve possuir no máximo 72 bytes")
        return password

    @model_validator(mode="after")
    def validate_password_confirmation(self):
        if self.new_password != self.new_password_confirmation:
            raise ValueError("A confirmação da nova senha não confere")
        return self

class URLSchema(BaseModel):
    original_url: str

    class Config:
            from_attributes = True

class UpdateTitleSchema(BaseModel):
    title: str

    class Config:
        from_attributes = True


class UpdateNameSchema(BaseModel):
    new_name: str = Field(min_length=2, max_length=120)

    @field_validator("new_name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        normalized_name = " ".join(name.split())
        if len(normalized_name) < 2:
            raise ValueError("Nome deve possuir ao menos 2 caracteres")
        return normalized_name


class UpdateEmailSchema(BaseModel):
    current_email: str
    new_email: str
    password: str = Field(min_length=1)

    @field_validator("current_email", "new_email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        return normalize_and_validate_email(email)

    @model_validator(mode="after")
    def validate_email_change(self):
        if self.current_email == self.new_email:
            raise ValueError("O novo email deve ser diferente do email atual")
        return self


class UpdatePasswordSchema(BaseModel):
    email: str
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=72)
    new_password_confirmation: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        return normalize_and_validate_email(email)

    @field_validator("new_password", "new_password_confirmation")
    @classmethod
    def validate_bcrypt_length(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("A senha deve possuir no máximo 72 bytes")
        return password

    @model_validator(mode="after")
    def validate_password_change(self):
        if self.new_password != self.new_password_confirmation:
            raise ValueError("A confirmação da nova senha não confere")
        if self.current_password == self.new_password:
            raise ValueError("A nova senha deve ser diferente da senha atual")
        return self

# class URLAccessSchema(BaseModel):
#     short_code: str

#     class Config:
#         from_attributes = True
