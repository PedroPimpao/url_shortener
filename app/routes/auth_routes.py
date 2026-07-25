from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..dependencies import get_session
from ..models import User
from ..schemas import UserSchema, LoginSchema

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from ..config import settings
from ..security import bcrypt_context

auth_router = APIRouter(prefix='/auth', tags=['auth'])

def create_token(user_id, token_duration=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)):
    expire_date = datetime.now(timezone.utc) + token_duration
    dic_info = { "sub": str(user_id), "exp": expire_date }
    encoded_jwt = jwt.encode(dic_info, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt

def auth_user(email, password, session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user

@auth_router.get('/')
async def home():
    """
    Rota padrão de autenticação
    """
    return { "message": "Home Auth Route" }

@auth_router.post('/create-account')
async def create_account(userSchema: UserSchema, session: Session = Depends(get_session)):
    """
    Rota de criação de conta
    """
    user = session.query(User).filter(User.email == userSchema.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already exists")
    else:
        hashed_password = bcrypt_context.hash(userSchema.password)
        new_user = User(name=userSchema.name, email=userSchema.email, password=hashed_password)
        session.add(new_user)
        session.commit()
        return {"message": f"Account created successfully {new_user.email}"}

@auth_router.post('/login')
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)):
    """
    Rota de Login
    """
    user = auth_user(login_schema.email, login_schema.password, session)
    if not user: 
        raise HTTPException(status_code=404, detail="Invalid credentials")
    else: 
        access_token = create_token(user_id=user.id)
        refresh_token = create_token(user_id=user.id, token_duration=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
    
@auth_router.post('/login-form')
async def login_form(formData: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Rota de Login de teste
    """
    user = auth_user(formData.username, formData.password, session)
    if not user: 
        raise HTTPException(status_code=404, detail="Invalid credentials")
    else: 
        access_token = create_token(user_id=user.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

@auth_router.get('/refresh-token')
async def user_refresh_token(user: User = Depends()):
    access_token = create_token(user_id=user.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }

