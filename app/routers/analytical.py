from fastapi import APIRouter

from app.schemas.purchase import PurchaseEnum
from app.schemas.vehicle import PropulsionEnum

router = APIRouter(prefix="/analytics", tags=["analytics"])

"""
Crie endpoints para gerar dados analíticos, exemplos abaixo, sinta-se livre:
Total de vendas por supplier / parte.
Número de garantias emitidas por supplier / modelo.
Valor médio das transações por tipo (compra/garantia) ou por modelo.
"""

@router.get("/{supplier_name}/{location_province}")
def analitycs_supplier_by_province(supplier_name:str, location_province:str) -> dict:
    """
    Obtém o total de vendas de fornecedor por parte
    """

@router.get("/{purchase_type}")
def analitycs_mean_transactions_by_purchase_type(purchase_type: PurchaseEnum) -> dict:
    """
    Obtém o valor médio das transações por tipo (compra, garantia)
    """
    if purchase_type == PurchaseEnum.bulk:
        print("lala")
    elif purchase_type == PurchaseEnum.warranty:
        print("lala")

@router.get("/{vehicle_model}")
def analitycs_mean_transactions_by_vehicle_model(vehicle_model: str) -> dict:
    """
    Obtém o valor médio das transações pelo modelo do veículo
    """

@router.get("/{part_name}/{propulsion_type}")
def analitycs_part_by_propulsion_type(propulsion_type: PropulsionEnum) -> dict:
    """
    Obtém a quantidade de peças vendidas baseado na propulsão do veículo
    """
    if propulsion_type == PurchaseEnum.bulk:
        print("lala")
    elif propulsion_type == PurchaseEnum.warranty:
        print("lala")

@router.get("/{supplier_name}/{part_name}")
def analitycs_supplier_by_part(supplier_name: str, part_name: str) -> dict:
    return {
        {
            "id": 1,
            "name": supplier_name,
            "address": "123 Supplier St",
            "city": "Supplier City",
            "state": "Supplier State",
            "zip": "12345"
        },
        {
            part_name
        }
    }