import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def get_engine():
    """
    Create and return a SQLAlchemy engine for the Cart2Insights database.
    """

    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DATABASE")

    required_settings = {
        "POSTGRES_HOST": db_host,
        "POSTGRES_PORT": db_port,
        "POSTGRES_USER": db_user,
        "POSTGRES_PASSWORD": db_password,
        "POSTGRES_DATABASE": db_name,
    }

    missing_settings = [
        name
        for name, value in required_settings.items()
        if not value
    ]

    if missing_settings:
        raise ValueError(
            "Missing database settings in .env: "
            + ", ".join(missing_settings)
        )

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name,
    )

    return create_engine(database_url)