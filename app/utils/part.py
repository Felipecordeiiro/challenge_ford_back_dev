from fastapi import Depends
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_part import Part

def get_all_parts_util(db: Session = Depends(get_db)):
    return db.query(Part).all()

def get_part_by_id_util(part_id:int, db: Session = Depends(get_db)):
    return db.query(Part).filter(Part.part_id == part_id).first()

def get_part_by_name_util(part_name:str, db: Session = Depends(get_db)):
    return db.query(Part).filter(Part.part_name == part_name).first()

def update_part_by_id_util(part_name:str = None, part_id: int = None, db: Session = Depends(get_db)):
    update_data = {}
    
    if part_name is not None:
        update_data[Part.part_name] = part_name
    
    if update_data:  
        return db.query(Part).filter(Part.part_id == part_id).update(update_data)
    
    return 0

def delete_part_by_part_name(part_name:str, db: Session = Depends(get_db)):
    rows_deleted = db.query(Part).filter(Part.part_name == part_name).delete()
    db.commit()
    return rows_deleted