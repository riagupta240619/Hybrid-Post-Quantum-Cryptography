import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.core.config import Settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_db_session():
        with test_session() as session:
            yield session

    application = create_app(Settings(app_env="test", database_url="sqlite://"))
    application.dependency_overrides[get_db_session] = override_db_session

    try:
        with TestClient(application) as test_client:
            yield test_client
    finally:
        application.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()