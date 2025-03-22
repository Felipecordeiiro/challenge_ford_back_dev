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

configurar_banco(SQLALCHEMY_DATABASE_URL)

def test_create_user():
    new_user = {
        "user_id": 1,
        "user_name": "Teste",
        "cpf": "12345678900",
        "email": "test@gmail.com",
        "password": "lalala",
        "created_at": "2021-07-01T00:00:00",
        "updated_at": "2021-07-01T00:00:00",
        "is_active": 1,
        "role": "user"
    }
    new_user_copy = new_user.copy()	
    response = client.post("/register", json=new_user)
    assert response.status_code == 200
    assert response.json() == new_user_copy

def test_create_user_erro_minimum_char_user_name():
    new_user = {
        "user_id": 1,
        "user_name": "oi",
        "cpf": "12345678900",
        "email": "test@gmail.com",
        "password": "lalala",
        "created_at": "2021-07-01T00:00:00",
        "updated_at": "2021-07-01T00:00:00",
        "is_active": 1,
        "role": "user"
    }
    response = client.post("/register", json=new_user)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "user_name"]

def test_create_user_erro_maximum_char_user_name():
    new_user = {
        "user_id": 1,
        "user_name": "a1sd3a1d5asd1as56d1as56d1as651d6as51ds65ad1a6s51d65as1da65s1ds5a6d1a",
        "cpf": "12345678900",
        "email": "test@gmail.com",
        "password": "lalala",
        "created_at": "2021-07-01T00:00:00",
        "updated_at": "2021-07-01T00:00:00",
        "is_active": 1,
        "role": "user"
    }
    response = client.post("/register", json=new_user)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "user_name"]

def test_create_user_erro_minimum_char_password():
    new_user = {
        "user_id": 1,
        "user_name": "Teste",
        "cpf": "12345678900",
        "email": "test@gmail.com",
        "password": "12345",
        "created_at": "2021-07-01T00:00:00",
        "updated_at": "2021-07-01T00:00:00",
        "is_active": 1,
        "role": "user"
    }
    response = client.post("/register", json=new_user)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]

def test_create_user_erro_maximum_char_password():
    new_user = {
        "user_id": 1,
        "user_name": "Teste",
        "cpf": "12345678900",
        "email": "test@gmail.com",
        "password": "123456789101112131415161718192021",
        "created_at": "2021-07-01T00:00:00",
        "updated_at": "2021-07-01T00:00:00",
        "is_active": 1,
        "role": "user"
    }
    response = client.post("/register", json=new_user)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]

def test_create_user_erro_minimum_char_cpf():
    new_user = {
        "user_id": 1,
        "user_name": "Teste",
        "cpf": "123456789",
        "email": "test@gmail.com",
        "password": "123456",
        "created_at": "2021-07-01T00:00:00",
        "updated_at": "2021-07-01T00:00:00",
        "is_active": 1,
        "role": "user"
    }
    response = client.post("/register", json=new_user)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "cpf"]

def test_create_user_erro_maximum_char_cpf():
    new_user = {
        "user_id": 1,
        "user_name": "Teste",
        "cpf": "123456789101112131415161718192021",
        "email": "test@gmail.com",
        "password": "123456",
        "created_at": "2021-07-01T00:00:00",
        "updated_at": "2021-07-01T00:00:00",
        "is_active": 1,
        "role": "user"
    }
    response = client.post("/register", json=new_user)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "cpf"]