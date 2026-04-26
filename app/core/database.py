from os import getenv
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


load_dotenv()


def _build_database_url() -> str:
    database_url = getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = getenv("POSTGRES_USER", "postgres")
    password = getenv("POSTGRES_PASSWORD", "postgres")
    host = getenv("POSTGRES_HOST", "localhost")
    port = getenv("POSTGRES_PORT", "5432")
    database = getenv("POSTGRES_DB", "paraiba_hotdog_db")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


DATABASE_URL = _build_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()