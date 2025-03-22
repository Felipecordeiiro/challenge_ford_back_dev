from fastapi import Depends
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_location import Location

def get_all_locations_util(db: Session = Depends(get_db)):
    return db.query(Location).all()

def get_location_by_id_util(location_id:int, db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.location_id == location_id).first()

def get_locations_by_market_util(market:str, db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.market == market).all()

def get_locations_by_city_util(city:str, db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.city == city).all()

def get_locations_by_country_util(country:str, db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.country == country).all()

def get_locations_by_province_util(province:str, db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.province == province).all()

def delete_location_by_id_util(location_id:int, db: Session = Depends(get_db)):
    rows_deleted = db.query(Location).filter(Location.location_id == location_id).delete()
    db.commit()

    return rows_deleted

def update_location_by_id_util(market:str = None, country:str = None, province:str = None, city:str = None, location_id: int = None, db: Session = Depends(get_db)):
    update_data = {}
    
    if market is not None:
        update_data[Location.market] = market
    if country is not None:
        update_data[Location.country] = country
    if province is not None:
        update_data[Location.province] = province
    if city is not None:
        update_data[Location.city] = city
    
    if update_data:  
        return db.query(Location).filter(Location.location_id == location_id).update(update_data)
    
    return 0