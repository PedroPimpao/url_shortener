# controllers/auth_controller.py

from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..schemas import LoginSchema, UserSchema
from ..services.auth_service import AuthService


class AuthController:

    @staticmethod
    def create_account(
        session: Session,
        data: UserSchema
    ):

        try:

            user = AuthService.create_account(
                session,
                data.name,
                data.email,
                data.password
            )

            return {
                "message": f"Account created successfully {user.email}"
            }

        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def login(
        session: Session,
        data: LoginSchema
    ):

        user = AuthService.authenticate(
            session,
            data.email,
            data.password
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Invalid credentials"
            )

        return {
            "access_token": AuthService.create_token(user.id),
            "refresh_token": AuthService.create_token(
                user.id,
                timedelta(days=7)
            ),
            "token_type": "Bearer"
        }

    @staticmethod
    def login_form(
        session: Session,
        username: str,
        password: str
    ):

        user = AuthService.authenticate(
            session,
            username,
            password
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Invalid credentials"
            )

        return {
            "access_token": AuthService.create_token(user.id),
            "token_type": "Bearer"
        }

    @staticmethod
    def me(user):

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }

    @staticmethod
    def refresh(user):

        return {
            "access_token": AuthService.create_token(user.id),
            "token_type": "Bearer"
        }