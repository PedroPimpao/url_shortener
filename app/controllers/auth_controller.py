from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import User
from ..services.auth_service import (
    AuthService,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidPasswordResetError,
)

class AuthController:
    @staticmethod
    def create_account(
        name: str,
        email: str,
        password: str,
        session: Session,
    ):
        try:
            return AuthService.create_account(
                name=name,
                email=email,
                password=password,
                session=session,
            )
        except EmailAlreadyExistsError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @staticmethod
    def login(
        email: str,
        password: str,
        session: Session,
    ):
        try:
            return AuthService.login(
                email=email,
                password=password,
                session=session,
            )
        except InvalidCredentialsError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error

    @staticmethod
    def login_form(
        email: str,
        password: str,
        session: Session,
    ):
        try:
            return AuthService.login_form(
                email=email,
                password=password,
                session=session,
            )
        except InvalidCredentialsError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error

    @staticmethod
    def refresh_token(user_id: str):
        return AuthService.refresh_token(user_id=user_id)

    @staticmethod
    def get_user_info(user: User):
        return AuthService.get_user_info(user=user)

    @staticmethod
    def request_password_reset(email: str, session: Session):
        return AuthService.request_password_reset(email=email, session=session)

    @staticmethod
    def verify_password_reset_otp(email: str, otp: str, session: Session):
        try:
            return AuthService.verify_password_reset_otp(
                email=email,
                otp=otp,
                session=session,
            )
        except InvalidPasswordResetError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @staticmethod
    def complete_password_reset(
        reset_token: str,
        new_password: str,
        session: Session,
    ):
        try:
            AuthService.complete_password_reset(
                reset_token=reset_token,
                new_password=new_password,
                session=session,
            )
        except InvalidPasswordResetError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
