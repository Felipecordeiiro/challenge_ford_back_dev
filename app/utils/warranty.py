from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_warranty import Warranty

def get_all_warranties_util(db: Session = Depends(get_db)):
    return db.query(Warranty).all()

def get_warranty_by_id_util(claim_key:int, db: Session = Depends(get_db)):
    return db.query(Warranty).filter(Warranty.claim_key == claim_key).first()

def delete_warranty_by_id_util(claim_key:int, db: Session = Depends(get_db)):
    rows_deleted = db.query(Warranty).filter(Warranty.claim_key == claim_key).delete()
    db.commit()

    return rows_deleted

def update_warranty_by_id_util(repair_date:datetime = None, client_comment:str = None, tech_comment:str = None, classified_failured:str = None, claim_key: int = None, db: Session = Depends(get_db)):
    update_data = {}
    
    if repair_date is not None:
        update_data[Warranty.repair_date] = repair_date
    if client_comment is not None:
        update_data[Warranty.client_comment] = client_comment
    if tech_comment is not None:
        update_data[Warranty.tech_comment] = tech_comment
    if classified_failured is not None:
        update_data[Warranty.classified_failured] = classified_failured
    
    if update_data:  
        return db.query(Warranty).filter(Warranty.claim_key == claim_key).update(update_data)
    
    return 0