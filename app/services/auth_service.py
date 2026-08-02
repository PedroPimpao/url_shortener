from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..models import User
from ..security import bcrypt_context


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
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
