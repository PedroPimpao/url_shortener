from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import settings
from ..models import User
from ..security import bcrypt_context
from ..utils.password_reset import (
    generate_otp,
    generate_reset_token,
    hash_otp,
    hash_reset_token,
    otp_matches,
)
class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidPasswordResetError(Exception):
    pass


class AuthService:
    @staticmethod
    def create_token(
        user_id: str,
        token_duration=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    ):
        expire_date = datetime.now(timezone.utc) + token_duration
        payload = {
            "sub": str(user_id),
            "exp": expire_date,
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            settings.ALGORITHM,
        )

    @staticmethod
    def authenticate(
        email: str,
        password: str,
        session: Session,
    ):
        user = session.query(User).filter(User.email == email).first()

        if not user or not bcrypt_context.verify(password, user.password):
            raise InvalidCredentialsError("Credenciais inválidas")

        return user

    @staticmethod
    def create_account(
        name: str,
        email: str,
        password: str,
        session: Session,
    ):
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            raise EmailAlreadyExistsError("Email já cadastrado")

        user = User(
            name=name,
            email=email,
            password=bcrypt_context.hash(password),
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    @staticmethod
    def login(
        email: str,
        password: str,
        session: Session,
    ):
        user = AuthService.authenticate(
            email=email,
            password=password,
            session=session,
        )

        return {
            "access_token": AuthService.create_token(user.id),
            "refresh_token": AuthService.create_token(
                user.id,
                timedelta(days=7),
            ),
            "token_type": "Bearer",
        }

    @staticmethod
    def login_form(
        email: str,
        password: str,
        session: Session,
    ):
        user = AuthService.authenticate(
            email=email,
            password=password,
            session=session,
        )

        return {
            "access_token": AuthService.create_token(user.id),
            "token_type": "Bearer",
        }

    @staticmethod
    def refresh_token(user_id: str):
        return AuthService.create_token(user_id=user_id)

    @staticmethod
    def get_user_info(user: User):
        return user

    @staticmethod
    def _clear_password_reset(user: User) -> None:
        user.password_reset_otp = None
        user.password_reset_expires = None
        user.password_reset_attempts = 0
        user.password_reset_token = None
        user.password_reset_token_expires = None

    @staticmethod
    def request_password_reset(email: str, session: Session) -> str:
        otp = generate_otp()
        user = (
            session.query(User)
            .filter(func.lower(User.email) == email)
            .with_for_update()
            .first()
        )
        if not user:
            return otp

        AuthService._clear_password_reset(user)
        user.password_reset_otp = hash_otp(otp)
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.PASSWORD_RESET_OTP_EXPIRE_MINUTES
        )
        session.commit()
        return otp

    @staticmethod
    def verify_password_reset_otp(
        email: str,
        otp: str,
        session: Session,
    ) -> str:
        user = (
            session.query(User)
            .filter(func.lower(User.email) == email)
            .with_for_update()
            .first()
        )
        now = datetime.now(timezone.utc)
        invalid = (
            not user
            or not user.password_reset_otp
            or not user.password_reset_expires
            or user.password_reset_expires <= now
            or user.password_reset_attempts >= settings.PASSWORD_RESET_MAX_ATTEMPTS
        )
        if invalid:
            if user and user.password_reset_otp:
                AuthService._clear_password_reset(user)
                session.commit()
            raise InvalidPasswordResetError("Código inválido ou expirado")

        if not otp_matches(otp, user.password_reset_otp):
            user.password_reset_attempts += 1
            if user.password_reset_attempts >= settings.PASSWORD_RESET_MAX_ATTEMPTS:
                AuthService._clear_password_reset(user)
            session.commit()
            raise InvalidPasswordResetError("Código inválido ou expirado")

        reset_token = generate_reset_token()
        user.password_reset_otp = None
        user.password_reset_expires = None
        user.password_reset_attempts = 0
        user.password_reset_token = hash_reset_token(reset_token)
        user.password_reset_token_expires = now + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )
        session.commit()
        return reset_token

    @staticmethod
    def complete_password_reset(
        reset_token: str,
        new_password: str,
        session: Session,
    ) -> None:
        token_hash = hash_reset_token(reset_token)
        user = (
            session.query(User)
            .filter(User.password_reset_token == token_hash)
            .with_for_update()
            .first()
        )
        now = datetime.now(timezone.utc)
        if (
            not user
            or not user.password_reset_token_expires
            or user.password_reset_token_expires <= now
        ):
            if user:
                AuthService._clear_password_reset(user)
                session.commit()
            raise InvalidPasswordResetError("Autorização inválida ou expirada")

        if bcrypt_context.verify(new_password, user.password):
            raise InvalidPasswordResetError("A nova senha deve ser diferente da senha atual")

        user.password = bcrypt_context.hash(new_password)
        AuthService._clear_password_reset(user)
        session.commit()
