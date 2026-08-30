import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:2006@localhost:3306/warranty_assistant",
)


engine_options = {"echo": os.getenv("SQL_ECHO", "false").lower() == "true"}

if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
