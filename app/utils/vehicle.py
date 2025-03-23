from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_vehicle import Vehicle
from app.schemas.vehicle import PropulsionEnum

def get_all_vehicles_util(db: Session = Depends(get_db)):
    return db.query(Vehicle).all()

def get_vehicle_by_id_util(vehicle_id:int, db: Session = Depends(get_db)):
    return db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()

def get_vehicle_by_model_util(model:str, db: Session = Depends(get_db)):
    return db.query(Vehicle).filter(Vehicle.model == model).all()

def get_vehicle_by_warranty(model:str, db: Session = Depends(get_db)):
    return db.query(Vehicle).filter(Vehicle.model == model).all()

def get_vehicle_by_propulsion_util(propulsion: PropulsionEnum, db: Session = Depends(get_db)):
    return db.query(Vehicle).filter(Vehicle.propulsion == propulsion).all()

def get_vehicle_by_year_util(year: int, db: Session = Depends(get_db)):
    return db.query(Vehicle).filter(Vehicle.year == year).all()

def delete_vehicle_by_id_util(vehicle_id:int, db: Session = Depends(get_db)):
    rows_deleted = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).delete()
    db.commit()

    return rows_deleted

def update_vehicle_by_id_util(model:str = None, prod_date:datetime = None, year:int = None, tech_comment:str = None, propulsion:PropulsionEnum = PropulsionEnum.gas, vehicle_id: int = None, db: Session = Depends(get_db)):
    update_data = {}
    
    if model is not None:
        update_data[Vehicle.model] = model
    if prod_date is not None:
        update_data[Vehicle.prod_date] = prod_date
    if year is not None:
        update_data[Vehicle.year] = year
    if propulsion is not None:
        update_data[Vehicle.propulsion] = propulsion
    
    if update_data:  
        return db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).update(update_data)
    
    return 0