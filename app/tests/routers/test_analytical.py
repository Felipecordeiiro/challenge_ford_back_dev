from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import os

from app.configs.auth import get_current_active_user
from app.configs.database import get_db
from app.configs.config import configurar_banco
from app.main import app
from app.models.model_user import User
from app.schemas.user import IsActiveEnum

client = TestClient(app)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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

@pytest.fixture
def mock_user():
    user = User(
        user_id=1,
        user_name="felipeteste",
        email="teste@gmail.com.br",
        password="hashed_password",  # Não importa para o teste
        cpf="12345678910",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=IsActiveEnum.active,
        role="admin"
    )
    return user

# Sobrescrever a dependência para os testes
@pytest.fixture(autouse=True)
def override_dependency(mock_user):
    # Substitui a função get_current_active_user pelo mock
    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    yield
    # Limpar após os testes
    app.dependency_overrides.clear()

def test_create_location():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    new_location = {
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    }
    response = client.post("location/", json=new_location)
    data = response.json()
    assert response.status_code == 201
    assert data["market"] == "latin_america"
    assert data["country"] == "Brasil"
    assert data["province"] == "Ceará"
    assert data["city"] == "Itapajé"

def test_create_location_invalid_format_or_not_found_market():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    new_location = {
        "market": "latin america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    }
    response = client.post("location/", json=new_location)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "market"]

def test_create_supplier():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    new_supplier = {
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 1
    }
    
    response = client.post("supplier/", json=new_supplier)
    
    assert response.status_code == 200
    data = response.json()
    assert data["supplier_name"] == "felipe motos"
    assert data["supplier_cpf"] == "12345678910"
    assert data["location_id"] == 1

def test_analytics_supplier_by_province_success():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    # Locations
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Quixadá"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Sobral"
    })

    # Suppliers
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 2
    })
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 3
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678911",
        "location_id": 2
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678911",
        "location_id": 3
    })

    # Purchases
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "warranty",
        "purchase_date": "2023-03-01",
        "part_id": 2
    })

    # Parts
    client.post("/part", json={
        "part_name": "pneu",
        "last_id_purchase": 1,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "garfo",
        "last_id_purchase": 2,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "motor",
        "last_id_purchase": 3,
        "supplier_id": 3
    })

    # Warranty
    client.post("/warranty", json={
        "vehicle_id": 1,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 1,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 1,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    # Vehicles
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2023-03-01",
        "year": 2023,
        "propulsion": "eletric",
    })
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2025-01-01",
        "year": 2025,
        "propulsion": "gas",
    })
    client.post("/vehicle", json={
        "model": "Fiat",
        "prod_date": "2017-01-01",
        "year": 2019,
        "propulsion": "gas",
    })

    # Fazer requisição
    response = client.get("/analytics/supplier_by_province/Ceará")

    # Debug: imprimir resposta se houver falha
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    # Verificar resposta esperada
    assert response.status_code == 200
    data = response.json()
    assert data["province"] == "Ceará"
    assert data["total_suppliers"] == 6
    assert data["total_parts"] == 3
    assert data["total_purchases"] == 2
    assert "suppliers_by_market" in data
    assert "top_suppliers" in data

def test_analytics_supplier_by_province_not_found():
    configurar_banco(SQLALCHEMY_DATABASE_URL)    
    # Locations
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Quixadá"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Sobral"
    })
    
    # Fazer requisição
    response = client.get("/analytics/supplier_by_province/provincia")
    print(response)
    
    # Verificar resposta
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"]

# Testes para purchases_by_type
def test_analytics_by_purchase_type_success():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Quixadá"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Sobral"
    })

    # Suppliers
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 2
    })
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 3
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678911",
        "location_id": 2
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678911",
        "location_id": 3
    })

    # Parts
    client.post("/part", json={
        "part_name": "pneu",
        "last_id_purchase": 1,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "garfo",
        "last_id_purchase": 2,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "motor",
        "last_id_purchase": 3,
        "supplier_id": 3
    })

    # Purchases
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 2
    })
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-10-01",
        "part_id": 3
    })

    # Fazer requisição
    response = client.get("/analytics/purchases_by_type/bulk")
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["purchase_type"] == "bulk"
    assert data["total_count"] == 4
    assert "monthly_trend" in data
    assert "top_parts" in data
    assert "first_purchase_date" in data
    assert "last_purchase_date" in data

def test_analytics_by_purchase_type_invalid_format_or_not_found():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    # Fazer requisição
    response = client.get("/analytics/purchases_by_type/teste")
    
    error_detail = response.json()["detail"][0]
    assert response.status_code == 422
    assert "Input should be" in error_detail["msg"]

# Testes para vehicle_model
def test_analytics_by_vehicle_model_success():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Quixadá"
    })

    # Suppliers
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 2
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678911",
        "location_id": 2
    })
    
    # Purchases
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "warranty",
        "purchase_date": "2023-03-01",
        "part_id": 2
    })

    # Parts
    client.post("/part", json={
        "part_name": "pneu",
        "last_id_purchase": 1,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "garfo",
        "last_id_purchase": 2,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "motor",
        "last_id_purchase": 3,
        "supplier_id": 3
    })

    # Warranty
    client.post("/warranty", json={
        "vehicle_id": 1,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 2,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 2,
        "repair_date": "2023-10-01",
        "client_comment": "Clientes teste 2",
        "tech_comment": "Equipe de TI teste 2",
        "part_id": 2,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 3,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 3",
        "tech_comment": "Equipe de TI teste 3",
        "part_id": 3,
        "classified_failured": "falha na bateria",
        "location_id": 3,
        "purchase_id": 3
    })
    # Vehicles
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2023-03-01",
        "year": 2023,
        "propulsion": "eletric",
    })
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2025-01-01",
        "year": 2025,
        "propulsion": "gas",
    })
    client.post("/vehicle", json={
        "model": "Fiat",
        "prod_date": "2017-01-01",
        "year": 2019,
        "propulsion": "gas",
    })

    # Fazer requisição
    response = client.get("/analytics/vehicle_model/Audi")
    data = response.json()

    # Verificar resposta
    assert response.status_code == 200
    assert data["vehicle_model"] == "Audi"
    assert data["total_count"] == 2
    assert "propulsion_stats" in data
    assert "year_distribution" in data
    assert "warranty_stats" in data

def test_analytics_by_vehicle_model_not_found():
    # Vehicles
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2023-03-01",
        "year": 2023,
        "propulsion": "eletric",
    })
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2025-01-01",
        "year": 2025,
        "propulsion": "gas",
    })
    client.post("/vehicle", json={
        "model": "Fiat",
        "prod_date": "2017-01-01",
        "year": 2019,
        "propulsion": "gas",
    })

    # Fazer requisição
    response = client.get("/analytics/vehicle_model/Gol")
    
    # Verificar resposta
    assert response.status_code == 404
    assert "Nenhum modelo" in response.json()["detail"]

# Testes para propulsion_type
def test_analytics_part_by_propulsion_type_success():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    # Vehicles
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2023-03-01",
        "year": 2023,
        "propulsion": "eletric",
    })
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2025-01-01",
        "year": 2025,
        "propulsion": "gas",
    })
    client.post("/vehicle", json={
        "model": "Fiat",
        "prod_date": "2017-01-01",
        "year": 2019,
        "propulsion": "gas",
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Quixadá"
    })

    # Suppliers
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 2
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678911",
        "location_id": 2
    })

    # Parts
    client.post("/part", json={
        "part_name": "pneu",
        "last_id_purchase": 1,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "garfo",
        "last_id_purchase": 2,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "motor",
        "last_id_purchase": 3,
        "supplier_id": 3
    })
    
    # Purchases
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "warranty",
        "purchase_date": "2023-03-01",
        "part_id": 2
    })

    # Warranty
    client.post("/warranty", json={
        "vehicle_id": 1,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 2,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 2,
        "repair_date": "2023-10-01",
        "client_comment": "Clientes teste 2",
        "tech_comment": "Equipe de TI teste 2",
        "part_id": 2,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 3,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 3",
        "tech_comment": "Equipe de TI teste 3",
        "part_id": 3,
        "classified_failured": "falha na bateria",
        "location_id": 3,
        "purchase_id": 3
    })

    # Fazer requisição
    response = client.get("/analytics/propulsion_type/eletric")
    
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["propulsion_type"] == "eletric"
    assert data["total_vehicles"] == 1
    assert "total_parts_replaced" in data
    assert "model_distribution" in data
    assert "part_stats" in data

def test_analytics_part_by_propulsion_type_invalid_format_or_not_found():
    # Fazer requisição
    response = client.get("/analytics/propulsion_type/hydrogen")
    
    error_detail = response.json()["detail"][0]
    assert response.status_code == 422
    assert "Input should be" in error_detail["msg"]

# Testes para part_by_suppliers
def test_analytics_supplier_by_part_success():
    configurar_banco(SQLALCHEMY_DATABASE_URL)
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Itapajé"
    })
    client.post("location/", json={
        "market": "latin_america",
        "country": "Brasil",
        "province": "Ceará",
        "city": "Quixadá"
    })

    # Suppliers
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe motos",
        "supplier_cpf": "12345678910",
        "location_id": 2
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678910",
        "location_id": 1
    })
    client.post("/supplier", json={
        "supplier_name": "felipe viagens",
        "supplier_cpf": "12345678911",
        "location_id": 2
    })
    
    # Purchases
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "bulk",
        "purchase_date": "2023-03-01",
        "part_id": 1
    })
    client.post("/purchases", json={
        "purchase_type": "warranty",
        "purchase_date": "2023-03-01",
        "part_id": 2
    })

    # Parts
    client.post("/part", json={
        "part_name": "pneu",
        "last_id_purchase": 1,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "garfo",
        "last_id_purchase": 2,
        "supplier_id": 1
    })
    client.post("/part", json={
        "part_name": "motor",
        "last_id_purchase": 3,
        "supplier_id": 3
    })

    # Warranty
    client.post("/warranty", json={
        "vehicle_id": 1,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 2,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 1",
        "tech_comment": "Equipe de TI teste 1",
        "part_id": 1,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 2,
        "repair_date": "2023-10-01",
        "client_comment": "Clientes teste 2",
        "tech_comment": "Equipe de TI teste 2",
        "part_id": 2,
        "classified_failured": "falha na bateria",
        "location_id": 1,
        "purchase_id": 1
    })
    client.post("/warranty", json={
        "vehicle_id": 3,
        "repair_date": "2023-03-01",
        "client_comment": "Clientes teste 3",
        "tech_comment": "Equipe de TI teste 3",
        "part_id": 3,
        "classified_failured": "falha na bateria",
        "location_id": 3,
        "purchase_id": 3
    })
    # Vehicles
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2023-03-01",
        "year": 2023,
        "propulsion": "eletric",
    })
    client.post("/vehicle", json={
        "model": "Audi",
        "prod_date": "2025-01-01",
        "year": 2025,
        "propulsion": "gas",
    })
    client.post("/vehicle", json={
        "model": "Fiat",
        "prod_date": "2017-01-01",
        "year": 2019,
        "propulsion": "gas",
    })

    # Fazer requisição
    response = client.get("/analytics/part_by_suppliers/felipe motos")
    print(response.json())
    # Verificar resposta
    assert response.status_code == 200
    data = response.json()
    assert data["supplier"]["name"] == "felipe motos"
    assert data["total_parts"] == 2
    assert "parts_analysis" in data
    assert len(data["parts_analysis"]) == 2
    assert "warranty_stats" in data["parts_analysis"][0]
    assert "vehicle_stats" in data["parts_analysis"][0]

def test_analytics_supplier_by_part_not_found():
    # Fazer requisição
    response = client.get("/analytics/part_by_suppliers/Fornecedor")
    
    # Verificar resposta
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]