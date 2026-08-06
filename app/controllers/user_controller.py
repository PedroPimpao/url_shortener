from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import User
from ..services.user_service import (
    EmailAlreadyInUseError,
    InvalidCurrentCredentialsError,
    UnchangedUserDataError,
    UserService,
)


class UserController:
    @staticmethod
    def update_name(user: User, new_name: str, session: Session):
        try:
            return UserService.update_name(user, new_name, session)
        except UnchangedUserDataError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @staticmethod
    def update_email(
        user: User,
        current_email: str,
        new_email: str,
        password: str,
        session: Session,
    ):
        try:
            return UserService.update_email(
                user, current_email, new_email, password, session
            )
        except InvalidCurrentCredentialsError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error
        except EmailAlreadyInUseError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @staticmethod
    def update_password(
        user: User,
        email: str,
        current_password: str,
        new_password: str,
        session: Session,
    ):
        try:
            return UserService.update_password(
                user, email, current_password, new_password, session
            )
        except InvalidCurrentCredentialsError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error
        except UnchangedUserDataError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
