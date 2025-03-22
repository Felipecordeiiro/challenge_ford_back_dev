from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_part import Part
from app.schemas.part import PartDelete, PartRequest, PartResponse, PartUpdate
from app.utils.part import delete_part_by_part_name, get_all_parts_util, get_part_by_id_util, get_part_by_name_util, update_part_by_id_util

router = APIRouter(prefix="/part", tags=["part"])

@router.get("/")
def list_part(db: Session = Depends(get_db)) -> list[PartResponse]:
    """
    Lista todas as partes.
    """
    all_parts = get_all_parts_util(db)
    return [PartResponse.model_validate(part.__dict__) for part in all_parts]

@router.get("/{part_id}")
def get_part_by_id(part_id: int, db: Session = Depends(get_db)) -> PartResponse:
    """
    Obtém uma parte pelo seu ID.
    """
    part = get_part_by_id_util(part_id, db=db)
    if not part:
        raise HTTPException(status_code=404, detail="Parte não encontrada")
    return PartResponse(**part.__dict__)

@router.post("/", status_code=201)
def create_part(part: PartRequest, db: Session = Depends(get_db)) -> PartResponse:
    """
    Cria uma parte.
    """
    new_part = Part(**part.model_dump())
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return PartResponse(**new_part.__dict__)

@router.put("/{part_id}")
def update_part(part: PartUpdate, part_id: int, db: Session = Depends(get_db)) -> PartResponse:
    """
    Atualiza uma parte.
    """
    update_data = part.model_dump()
    update_data["part_id"] = part_id

    rows_updated = update_part_by_id_util(**update_data, db=db)

    if not rows_updated:
        raise HTTPException(status_code=404, detail=f"Não foi possível atualizar parte")
    
    updated_part = get_part_by_id_util(part_id, db=db)

    if not updated_part:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar parte após atualização")
    
    return PartResponse.model_validate(updated_part)

@router.delete("/{part_name}")
def delete_part(part: PartDelete, db: Session = Depends(get_db)) -> PartResponse:
    """
    Deleta uma parte.
    """
    part_to_delete = get_part_by_name_util(part.part_name, db=db)
    
    if not part_to_delete:
        raise HTTPException(status_code=404, detail=f"Parte com nome '{part.part_name}' não encontrada")

    response_data = PartResponse.model_validate(part_to_delete.__dict__)
    
    deleted_part = delete_part_by_part_name(part.part_name, db=db)
    
    if not deleted_part:
        raise HTTPException(status_code=500, detail="Falha ao excluir a parte")
    
    return response_data
