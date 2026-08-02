from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..controllers.auth_controller import AuthController
from ..dependencies import get_session, verify_token
from ..models import User
from ..schemas import LoginSchema, UserSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/")
async def home():
    """Rota padrão de autenticação."""
    return {"message": "Home Auth Route"}


@auth_router.post("/create-account")
async def create_account(
    user_schema: UserSchema,
    session: Session = Depends(get_session),
):
    """Rota de criação de conta."""
    user = AuthController.create_account(
        name=user_schema.name,
        email=user_schema.email,
        password=user_schema.password,
        session=session,
    )

    return {
        "message": "Conta criada com sucesso",
        "email": user.email,
    }


@auth_router.post("/login")
async def login(
    login_schema: LoginSchema,
    session: Session = Depends(get_session),
):
    """Rota de login."""
    tokens = AuthController.login(
        email=login_schema.email,
        password=login_schema.password,
        session=session,
    )

    return tokens


@auth_router.post("/login-form")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Rota de login compatível com o fluxo OAuth2 do Swagger."""
    tokens = AuthController.login_form(
        email=form_data.username,
        password=form_data.password,
        session=session,
    )

    return tokens


@auth_router.get("/refresh-token")
async def refresh_token(user: User = Depends(verify_token)):
    """Rota de renovação do token de acesso."""
    access_token = AuthController.refresh_token(user_id=user.id)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }


@auth_router.get("/me")
async def user_info(user: User = Depends(verify_token)):
    """Rota de consulta do usuário autenticado."""
    current_user = AuthController.get_user_info(user=user)

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }
