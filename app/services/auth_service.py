# services/auth_service.py

from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..models import User
from ..security import bcrypt_context


class AuthService:

    @staticmethod
    def create_token(
        user_id: str,
        token_duration=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    ):
        expire_date = datetime.now(timezone.utc) + token_duration

        payload = {
            "sub": str(user_id),
            "exp": expire_date
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            settings.ALGORITHM
        )

    @staticmethod
    def authenticate(
        session: Session,
        email: str,
        password: str
    ):

        user = session.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not bcrypt_context.verify(password, user.password):
            return None

        return user

    @staticmethod
    def create_account(
        session: Session,
        name: str,
        email: str,
        password: str
    ):

        existing = session.query(User).filter(User.email == email).first()

        if existing:
            raise ValueError("Email already exists")

        hashed = bcrypt_context.hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user