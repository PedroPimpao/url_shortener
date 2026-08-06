from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..controllers.user_controller import UserController
from ..dependencies import get_session, verify_token
from ..models import User
from ..schemas import UpdateEmailSchema, UpdateNameSchema, UpdatePasswordSchema


user_router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(verify_token)],
)


@user_router.patch("/update-name")
async def update_name(
    name_schema: UpdateNameSchema,
    session: Session = Depends(get_session),
    user: User = Depends(verify_token),
):
    updated_user = UserController.update_name(
        user=user,
        new_name=name_schema.new_name,
        session=session,
    )
    return {
        "message": "Nome atualizado com sucesso",
        "name": updated_user.name,
    }


@user_router.patch("/update-email")
async def update_email(
    email_schema: UpdateEmailSchema,
    session: Session = Depends(get_session),
    user: User = Depends(verify_token),
):
    updated_user = UserController.update_email(
        user=user,
        current_email=email_schema.current_email,
        new_email=email_schema.new_email,
        password=email_schema.password,
        session=session,
    )
    return {
        "message": "Email atualizado com sucesso",
        "email": updated_user.email,
    }


@user_router.patch("/update-password")
async def update_password(
    password_schema: UpdatePasswordSchema,
    session: Session = Depends(get_session),
    user: User = Depends(verify_token),
):
    UserController.update_password(
        user=user,
        email=password_schema.email,
        current_password=password_schema.current_password,
        new_password=password_schema.new_password,
        session=session,
    )
    return {"message": "Senha atualizada com sucesso"}
