import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import text

load_dotenv(".env.test")

os.environ.update(
    {
        "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
        "REDIS_URL": os.environ["TEST_REDIS_URL"],
        "LOCAL_DEV": os.environ.get("TEST_LOCAL_DEV", "1"),
    }
)

from app.database import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
