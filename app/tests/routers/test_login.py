from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.configs.database import get_db
from app.configs.config import configurar_banco
from app.main import app
import os

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL
os.environ['TEST_DATABASE'] = 'true'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def test_create_user():
    configurar_banco(SQLALCHEMY_DATABASE_URL)

    new_login = {
        "identifier": "felipeteste@gmail.com",
        "identifier_type": "email",
        "password": "12345678900",
    }
    new_login_copy = new_login.copy()	
    response = client.post("/login", json=new_login)
    assert response.status_code == 200
    assert response.json() == new_login_copy

def test_create_user_erro_minimum_char_identifier():
    configurar_banco(SQLALCHEMY_DATABASE_URL)

    new_login = {
        "identifier": "oi",
        "identifier_type": "username",
        "password": "12345678900",
    }
    response = client.post("/login", json=new_login)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "identifier"]

def test_create_user_erro_maximum_char_identifier():
    configurar_banco(SQLALCHEMY_DATABASE_URL)

    new_login = {
        "identifier": "felipeteste_aprovado_teste2_reprovado_teste3_aprovado@gmail.com",
        "identifier_type": "email",
        "password": "12345678900",
    }
    response = client.post("/login", json=new_login)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "identifier"]

def test_create_user_erro_minimum_char_password():
    configurar_banco(SQLALCHEMY_DATABASE_URL)

    new_login = {
        "identifier": "felipeteste@gmail.com",
        "identifier_type": "email",
        "password": "1234",
    }
    response = client.post("/login", json=new_login)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]

def test_create_user_erro_maximum_char_password():
    configurar_banco(SQLALCHEMY_DATABASE_URL)

    new_login = {
        "identifier": "felipeteste@gmail.com",
        "identifier_type": "email",
        "password": "1234567891011121314151617181920",
    }
    response = client.post("/login", json=new_login)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]