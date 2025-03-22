
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_warranty import Warranty
from app.schemas.warranty import WarrantyDelete, WarrantyRequest, WarrantyResponse, WarrantyUpdate
from app.utils.warranty import delete_warranty_by_id_util, get_all_warranties_util, get_warranty_by_id_util, update_warranty_by_id_util

router = APIRouter(prefix="/warranty", tags=["warranty"])

@router.get("/")
def list_warranties(db: Session = Depends(get_db)) -> list[WarrantyResponse]:
    """
    Lista todas as garantias.
    """
    all_warranties = get_all_warranties_util(db=db)
    return [WarrantyResponse.model_validate(warranty) for warranty in all_warranties]

@router.get("/{warranty_id}")
def get_warranties_by_id(claim_key:str, db: Session = Depends(get_db)) -> WarrantyResponse:
    """
    Obtém garantia pelo seu ID.
    """
    warranty = get_warranty_by_id_util(claim_key, db=db)
    if not warranty:
        raise HTTPException(status_code=404, detail=f"Nenhuma localização encontrada para o mercado '{market}'")
    return WarrantyResponse(**warranty.__dict__)

@router.post("/")
def create_warranty(warranty: WarrantyRequest,  db: Session = Depends(get_db)) -> WarrantyResponse:
    """
    Cria uma nova garantia.
    """
    new_warranty = Warranty(**warranty.model_dump())
    db.add(new_warranty)
    db.commit()
    db.refresh(new_warranty)
    return WarrantyResponse(**new_warranty.__dict__)

@router.put("/{warranty_id}")
def update_warranty(warranty: WarrantyUpdate, claim_key: int, db: Session = Depends(get_db)) -> WarrantyResponse:
    """
    Atualiza uma garantia.
    """
    update_data = warranty.model_dump()
    update_data["claim_key"] = claim_key
    rows_updated = update_warranty_by_id_util(**update_data, db=db)

    if not rows_updated:
        raise HTTPException(status_code=404, detail=f"Não foi possível atualizar a garantia")
    
    db.commit()
    updated_location = get_warranty_by_id_util(claim_key, db=db)

    if not updated_location:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar garantia após atualização")
    
    return WarrantyResponse.model_validate(updated_location)

@router.delete("/{warranty_id}")
def delete_warranty(warranty: WarrantyDelete, claim_key:int, db: Session = Depends(get_db)) -> WarrantyResponse:
    """
    Deleta uma garantia.
    """
    warranty_to_delete = get_warranty_by_id_util(claim_key, db=db)
    
    if not warranty_to_delete:
        raise HTTPException(status_code=404, detail=f"Garantia com esse id '{warranty_to_delete.claim_key}' não encontrada")
    
    response_data = WarrantyResponse.model_validate(warranty_to_delete)

    deleted_location = delete_warranty_by_id_util(warranty.claim_key, db=db)

    if not deleted_location:
        raise HTTPException(status_code=500, detail="Falha ao excluir a garantia")
    
    return response_data