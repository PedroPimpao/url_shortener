from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import User
from ..security import bcrypt_context


class InvalidCurrentCredentialsError(Exception):
    pass


class EmailAlreadyInUseError(Exception):
    pass


class UnchangedUserDataError(Exception):
    pass


class UserService:
    @staticmethod
    def update_name(user: User, new_name: str, session: Session):
        if user.name == new_name:
            raise UnchangedUserDataError("O novo nome deve ser diferente do nome atual")

        user.name = new_name
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def update_email(
        user: User,
        current_email: str,
        new_email: str,
        password: str,
        session: Session,
    ):
        if (
            user.email.lower() != current_email
            or not bcrypt_context.verify(password, user.password)
        ):
            raise InvalidCurrentCredentialsError("Credenciais atuais inválidas")

        existing_user = (
            session.query(User)
            .filter(func.lower(User.email) == new_email)
            .first()
        )
        if existing_user:
            raise EmailAlreadyInUseError("Email já cadastrado")

        user.email = new_email
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise EmailAlreadyInUseError("Email já cadastrado") from error

        session.refresh(user)
        return user

    @staticmethod
    def update_password(
        user: User,
        email: str,
        current_password: str,
        new_password: str,
        session: Session,
    ):
        if (
            user.email.lower() != email
            or not bcrypt_context.verify(current_password, user.password)
        ):
            raise InvalidCurrentCredentialsError("Credenciais atuais inválidas")

        if bcrypt_context.verify(new_password, user.password):
            raise UnchangedUserDataError("A nova senha deve ser diferente da senha atual")

        user.password = bcrypt_context.hash(new_password)
        session.commit()
        return user
