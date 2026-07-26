from collections.abc import Generator
from sqlalchemy.orm import Session
from .database.session import SessionLocal
from fastapi import Depends, HTTPException
from .security import oauth2_schema
from jose import jwt, JWTError
from .config import settings
from .models import User

def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        dic_info = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        userID = str(dic_info.get('sub'))
    except JWTError:
        raise HTTPException(status_code=401, detail="Access Denied")
    user = session.query(User).filter(User.id == userID).first()
    if not user:
        raise HTTPException(status_code=401, detail="Access Denied")
    return user

