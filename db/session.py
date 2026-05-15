from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings

DATABASE_URL = "sqlite:///edumind.db"

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)