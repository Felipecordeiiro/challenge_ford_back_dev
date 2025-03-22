from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_purchase import Purchase
from app.schemas.purchase import PurchaseDelete, PurchaseEnum, PurchaseRequest, PurchaseResponse, PurchaseUpdate
from app.utils.purchase import delete_purchase_by_id, get_all_purchase_util, get_purchase_by_id_util, get_purchases_by_purchase_date_util, get_purchases_by_purchase_type_util, update_purchase_by_id_util

router = APIRouter(prefix="/purchases", tags=["purchases"])

@router.get("/")
def list_purchases(db: Session = Depends(get_db)) -> list[PurchaseResponse]:
    """
    Lista todas as compras.
    """
    all_purchases = get_all_purchase_util(db=db)
    return [PurchaseResponse.model_validate(purchase.__dict__) for purchase in all_purchases]

@router.get("/id/{purchase_id}")
def get_purchase_by_id(purchase_id: int, db: Session = Depends(get_db)) -> PurchaseResponse:
    """
    Obtem compra pelo seu ID.
    """
    location = get_purchase_by_id_util(purchase_id, db=db)
    if not location:
        raise HTTPException(status_code=404, detail=f"Compra com id {purchase_id} não encontrada no banco de dados")
    return PurchaseResponse(**location.__dict__)

@router.get("/type/{purchase_type}")
def get_purchase_by_type(purchase_type: PurchaseEnum, db: Session = Depends(get_db)) -> list[PurchaseResponse]:
    """
    Obtem compras pelo tipo.
    """
    purchases = get_purchases_by_purchase_type_util(purchase_type, db=db)
    if not purchases:
        raise HTTPException(status_code=404, detail=f"Nenhuma compra realizada baseada no tipo {purchase_type}")
    return [PurchaseResponse.model_validate(purchase.__dict__) for purchase in purchases]

@router.get("/date/{purchase_date}")
def get_purchase_by_date(purchase_date: datetime, db: Session = Depends(get_db)) -> list[PurchaseResponse]:
    """
    Obtem compras pela data.
    """
    purchases = get_purchases_by_purchase_date_util(purchase_date, db=db)
    if not purchases:
        raise HTTPException(status_code=404, detail=f"Nenhuma compra realizada baseada no tipo {purchase_date.isoformat()}")
    return [PurchaseResponse.model_validate(purchase.__dict__) for purchase in purchases]

@router.post("/")
def create_purchase(purchase: PurchaseRequest, db: Session = Depends(get_db)) -> PurchaseResponse:
    """
    Cria uma compra.
    """
    new_purchase = Purchase(**purchase.model_dump())
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)
    return PurchaseResponse(**new_purchase.__dict__)

@router.put("/id/{purchase_id}")
def update_purchase(purchase: PurchaseUpdate, purchase_id:int, db: Session = Depends(get_db)) -> PurchaseResponse:
    """
    Atualiza uma compra.
    """
    update_data = purchase.model_dump()
    update_data["purchase_id"] = purchase_id

    rows_updated = update_purchase_by_id_util(**update_data, db=db)

    if not rows_updated:
        raise HTTPException(status_code=404, detail=f"Não foi possível atualizar compra")
    
    db.commit()
    updated_part = get_purchase_by_id(purchase_id, db=db)

    if not updated_part:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar compra após atualização")
    
    return PurchaseResponse.model_validate(updated_part.__dict__)

@router.delete("/id/{purchase_id}")
def delete_purchase(purchase: PurchaseDelete, db: Session = Depends(get_db)) -> PurchaseResponse:
    """
    Deleta uma compra.
    """
    purchase_to_delete = get_purchase_by_id_util(purchase.purchase_id, db=db)
    
    if not purchase_to_delete:
        raise HTTPException(status_code=404, detail=f"Compra com id '{purchase.purchase_id}' não encontrada")

    response_data = PurchaseResponse.model_validate(purchase_to_delete.__dict__)
    
    deleted_part = delete_purchase_by_id(purchase.purchase_id, db=db)
    
    if not deleted_part:
        raise HTTPException(status_code=500, detail="Falha ao excluir a compra")
    
    return response_data