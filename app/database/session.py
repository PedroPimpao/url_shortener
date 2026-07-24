from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

db = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=db,
    autoflush=False,
    autocommit=False,
)