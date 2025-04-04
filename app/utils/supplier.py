from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_supplier import Supplier

def get_all_suppliers_util(db: Session = Depends(get_db)):
    return db.query(Supplier).all()

def get_supplier_by_id_util(supplier_id:int, db: Session = Depends(get_db)):
    return db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

def get_supplier_by_location_id_util(location_id:int, db: Session = Depends(get_db)):
    return db.query(Supplier).filter(Supplier.location_id == location_id).all()

def get_supplier_by_name_util(supplier_name:str, db: Session = Depends(get_db)):
    return db.query(Supplier).filter(Supplier.supplier_name == supplier_name).first()

def get_supplier_by_cpf_util(supplier_cpf:str, db: Session = Depends(get_db)):
    return db.query(Supplier).filter(Supplier.supplier_cpf == supplier_cpf).first()

def update_supplier_by_id_util(supplier_name:str = None, supplier_cpf: str = None, location_id: int = None, supplier_id:int = None, db: Session = Depends(get_db)):
    update_data = {}
    
    if supplier_name is not None:
        update_data[Supplier.supplier_name] = supplier_name
    
    if supplier_cpf is not None:
        update_data[Supplier.supplier_cpf] = supplier_cpf

    if location_id is not None:
        update_data[Supplier.location_id] = location_id

    
    if update_data:  
        return db.query(Supplier).filter(Supplier.supplier_id == supplier_id).update(update_data)
    
    return 0

def delete_supplier_by_name(supplier_name:int, db: Session = Depends(get_db)):
    rows_deleted = db.query(Supplier).filter(Supplier.supplier_name == supplier_name).delete()
    db.commit()
    return rows_deleted