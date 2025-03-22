from datetime import datetime
from fastapi import Depends
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_purchase import Purchase
from app.schemas.purchase import PurchaseEnum

def get_all_purchase_util(db: Session = Depends(get_db)):
    return db.query(Purchase).all()

def get_purchase_by_id_util(purchase_id:int, db: Session = Depends(get_db)):
    return db.query(Purchase).filter(Purchase.purchase_id == purchase_id).first()

def get_purchases_by_purchase_type_util(purchase_type:PurchaseEnum, db: Session = Depends(get_db)):
    return db.query(Purchase).filter(Purchase.purchase_type == purchase_type).all()

def get_purchases_by_part_id_util(part_id:int, db: Session = Depends(get_db)):
    return db.query(Purchase).filter(Purchase.part_id == part_id).all()

def get_purchases_by_purchase_date_util(purchase_date:datetime, db: Session = Depends(get_db)):
    year = purchase_date.year
    month = purchase_date.month
    day = purchase_date.day
    
    # Filtrar registros onde o ano, mês e dia correspondem, independentemente da hora
    return db.query(Purchase).filter(
        extract('year', Purchase.purchase_date) == year,
        extract('month', Purchase.purchase_date) == month,
        extract('day', Purchase.purchase_date) == day
    ).all()

def update_purchase_by_id_util(purchase_type:str = None, purchase_date: datetime = None, purchase_id:int = None, db: Session = Depends(get_db)):
    update_data = {}
    
    if purchase_type is not None:
        update_data[Purchase.purchase_type] = purchase_type
    
    if not isinstance(datetime, purchase_date):
        purchase_date = datetime(purchase_date)

    if purchase_date is not None:
        update_data[Purchase.purchase_date] = purchase_date
    
    if update_data:  
        return db.query(Purchase).filter(Purchase.purchase_id == purchase_id).update(update_data)
    
    return 0

def delete_purchase_by_id(purchase_id:int, db: Session = Depends(get_db)):
    rows_deleted = db.query(Purchase).filter(Purchase.purchase_id == purchase_id).delete()
    db.commit()
    db.refresh(rows_deleted)
    return rows_deleted