import os

os.environ["DATABASE_URL"] = "sqlite:///./test_delete.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

engine = create_engine("sqlite:///./test_delete.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture
def seeded_db(client):
    r = client.post("/departments/", json={"name": "Company"})
    root_id = r.json()["id"]
    r = client.post("/departments/", json={"name": "IT", "parent_id": root_id})
    it_id = r.json()["id"]
    r = client.post("/departments/", json={"name": "HR", "parent_id": root_id})
    hr_id = r.json()["id"]
    r = client.post("/departments/", json={"name": "Backend", "parent_id": it_id})
    backend_id = r.json()["id"]
    client.post("/departments/", json={"name": "Frontend", "parent_id": it_id})

    client.post("/employees/", json={"full_name": "Alice", "position": "CEO", "department_id": root_id})
    client.post("/employees/", json={"full_name": "Bob", "position": "Dev", "department_id": it_id})
    client.post("/employees/", json={"full_name": "Charlie", "position": "Dev", "department_id": backend_id})
    client.post("/employees/", json={"full_name": "Diana", "position": "HR Lead", "department_id": hr_id})
    return {"root": root_id, "it": it_id, "hr": hr_id, "backend": backend_id}
