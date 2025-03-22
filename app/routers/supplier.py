from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_supplier import Supplier
from app.schemas.supplier import SupplierDelete, SupplierRequest, SupplierResponse, SupplierUpdate
from app.utils.supplier import delete_supplier_by_name, get_all_suppliers_util, get_supplier_by_cpf_util, get_supplier_by_id_util, get_supplier_by_name_util, update_supplier_by_id_util

router = APIRouter(prefix="/supplier", tags=["supplier"])

@router.get("/")
def list_supplier(db: Session = Depends(get_db)) -> list[SupplierResponse]:
    all_suppliers = get_all_suppliers_util(db)
    return [SupplierResponse.model_validate(supplier.__dict__) for supplier in all_suppliers]

@router.get("/{supplier_id}")
def get_supplier_by_id(supplier_id: int, db: Session = Depends(get_db)) -> SupplierResponse:
    """
    Obtém um fornecedor pelo seu ID.
    """
    supplier = get_supplier_by_id_util(supplier_id, db)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar o fornecedor pelo seu ID")
    return SupplierResponse.model_validate(supplier.__dict__)

@router.get("/{supplier_name}")
def get_supplier_by_name(supplier_name: str, db: Session = Depends(get_db)) -> SupplierResponse:
    """
    Obtém um fornecedor pelo seu nome.
    """
    supplier = get_supplier_by_name_util(supplier_name, db)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar o fornecedor pelo seu nome")
    return SupplierResponse.model_validate(supplier.__dict__)

@router.get("/{supplier_cpf}")
def get_supplier_by_cpf(supplier_cpf: str, db: Session = Depends(get_db)) -> SupplierResponse:
    """
    Obtém um fornecedor pelo seu cpf.
    """
    supplier = get_supplier_by_cpf_util(supplier_cpf, db)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar o fornecedor pelo seu cpf")
    return SupplierResponse.model_validate(supplier.__dict__)

@router.post("/")
def create_supplier(supplier: SupplierRequest, db: Session = Depends(get_db)) -> SupplierResponse:
    """
    Cria um fornecedor.
    """
    new_supplier = Supplier(**supplier.model_dump())
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return SupplierResponse(**new_supplier.__dict__)

@router.put("/{supplier_id}")
def update_supplier(supplier: SupplierUpdate, supplier_id: int, db: Session = Depends(get_db)) -> SupplierResponse:
    """
    Atualiza um fornecedor.
    """
    update_data = supplier.model_dump()
    update_data["supplier_id"] = supplier

    rows_updated = update_supplier_by_id_util(**update_data, db=db)

    if not rows_updated:
        raise HTTPException(status_code=404, detail=f"Não foi possível atualizar o fornecedor")
    
    updated_part = get_supplier_by_id_util(supplier_id, db=db)

    if not updated_part:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar o fornecedor após atualização")
    
    return SupplierResponse.model_validate(updated_part.__dict__)

@router.delete("/{supplier_id}")
def delete_supplier(supplier: SupplierDelete, db: Session = Depends(get_db)) -> SupplierResponse:
    """
    Deleta um fornecedor.
    """
    supplier_to_delete = get_supplier_by_name_util(supplier.supplier_name, db=db)
    
    if not supplier_to_delete:
        raise HTTPException(status_code=404, detail=f"Supplier com nome '{supplier.supplier_name}' não encontrada")

    response_data = SupplierResponse.model_validate(supplier_to_delete)
    
    deleted_part = delete_supplier_by_name(supplier.supplier_name, db=db)
    
    if not deleted_part:
        raise HTTPException(status_code=500, detail="Falha ao excluir a parte")
    
    return response_data