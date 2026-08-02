# routes/auth_route.py

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..controllers.auth_controller import AuthController
from ..dependencies import get_session
from ..models import User
from ..schemas import LoginSchema, UserSchema

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@auth_router.get("/")
async def home():
    """
    Auth Home Route
    """
    return {"message": "Home Auth Route"}


@auth_router.post("/create-account")
async def create_account(
    user: UserSchema,
    session: Session = Depends(get_session)
):
    """
    Create Account Route
    """
    return AuthController.create_account(
        session,
        user
    )


@auth_router.post("/login")
async def login(
    login: LoginSchema,
    session: Session = Depends(get_session)
):
    """
    Login Route
    """
    return AuthController.login(
        session,
        login
    )


@auth_router.post("/login-form")
async def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Login Form Route
    """
    return AuthController.login_form(
        session,
        form.username,
        form.password
    )


@auth_router.get("/refresh-token")
async def refresh_token(
    user: User = Depends()
):
    """
    Refresh Token Route
    """
    return AuthController.refresh(user)


@auth_router.get("/me")
async def me(
    user: User = Depends()
):
    """
    User Info Route
    """
    return AuthController.me(user)