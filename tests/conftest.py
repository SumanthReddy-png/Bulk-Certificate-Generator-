import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.routes import get_session_factory
import app.config as config_module
import app.service as service_module


@pytest.fixture(scope="session")
def tmp_storage(tmp_path_factory):
    return str(tmp_path_factory.mktemp("storage"))


@pytest.fixture(scope="session")
def db_engine(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db") / "test.db"
    url = f"sqlite:///{db_file}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture
def client(session_factory, tmp_storage, monkeypatch):
    monkeypatch.setattr(config_module, "STORAGE_DIR", tmp_storage)
    monkeypatch.setattr(service_module, "STORAGE_DIR", tmp_storage)

    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def override_get_session_factory():
        return session_factory

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_session_factory] = override_get_session_factory

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
