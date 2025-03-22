from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_location import Location
from app.schemas.location import LocationDelete, LocationRequest, LocationResponse, LocationUpdate
from app.utils.location import delete_location_by_id_util, get_all_locations_util, get_location_by_id_util, get_locations_by_country_util, get_locations_by_market_util, get_locations_by_city_util, get_locations_by_province_util, update_location_by_id_util

router = APIRouter(prefix="/location", tags=["location"])

@router.get("/")
def list_location(db: Session = Depends(get_db)) -> list[LocationResponse]: 
    """
    Lista todas as localizações.
    """
    all_locations = get_all_locations_util(db)
    return [LocationResponse.model_validate(location.__dict__) for location in all_locations]

@router.get("/id/{location_id}")
def get_location_by_id(location_id: int, db: Session = Depends(get_db)) -> LocationResponse:
    """
    Obtém uma localização pelo seu ID.
    """
    location = get_location_by_id_util(location_id, db)
    if not location:
        raise HTTPException(status_code=404, detail="Localização não encontrada")
    return LocationResponse(**location.__dict__)

@router.get("/market/{market}")
def get_location_by_market(market: str, db: Session = Depends(get_db)) -> list[LocationResponse]:
    """
    Obtém localizações a partir do nome do mercado.
    """
    locations = get_locations_by_market_util(market, db)
    if not locations:
        raise HTTPException(status_code=404, detail=f"Nenhuma localização encontrada para o mercado '{market}'")
    return [LocationResponse.model_validate(location.__dict__) for location in locations]

@router.get("/country/{country}")
def get_location_by_country(country: str, db: Session = Depends(get_db)) -> list[LocationResponse]:
    """
    Obtém localizações pelo nome do país.
    """
    locations = get_locations_by_country_util(country, db)
    if not locations:
        raise HTTPException(status_code=404, detail=f"Nenhuma localização encontrada para o país '{country}'")
    return [LocationResponse.model_validate(location.__dict__) for location in locations]

@router.get("/province/{province}")
def get_location_by_province(province: str, db: Session = Depends(get_db)) -> list[LocationResponse]:
    """
    Obtém localizações pelo nome da província.
    """
    locations = get_locations_by_province_util(province, db)
    if not locations:
        raise HTTPException(status_code=404, detail=f"Nenhuma localização encontrada para o país '{province}'")
    return [LocationResponse.model_validate(location.__dict__) for location in locations]

@router.get("/city/{city}")
def get_location_by_city(city: str, db: Session = Depends(get_db)) -> list[LocationResponse]:
    """
    Obtém localizações pelo nome da cidade.
    """
    locations = get_locations_by_city_util(city, db)
    if not locations:
        raise HTTPException(status_code=404, detail=f"Nenhuma localização encontrada para a cidade '{city}'")
    return [LocationResponse.model_validate(location.__dict__) for location in locations]

@router.post("/", status_code=201)
def create_location(location: LocationRequest, db: Session = Depends(get_db)) -> LocationResponse:
    """
    Cria uma localização.
    """
    new_location = Location(
        **location.model_dump()    
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return LocationResponse( **new_location.__dict__ )

@router.put("/id/{location_id}")
def update_location(location: LocationUpdate, location_id: int, db: Session = Depends(get_db)) -> LocationResponse:
    """
    Atualiza uma localização.
    """
    # Converter o modelo Pydantic para um dicionário e filtrar strings vazias
    update_data = location.model_dump()            
    update_data["location_id"] = location_id
    rows_updated = update_location_by_id_util(**update_data, db=db)

    if not rows_updated:
        raise HTTPException(status_code=404, detail=f"Não foi possível atualizar localização {rows_updated}")
    
    db.commit()
    updated_location = get_location_by_id_util(location_id, db=db)

    if not updated_location:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar localização após atualização")
    
    return LocationResponse.model_validate(updated_location.__dict__)

@router.delete("/id/{location_id}")
def delete_location(location: LocationDelete, db: Session = Depends(get_db)) -> LocationResponse:
    """
    Deleta uma localização.
    """
    location_to_delete = get_location_by_id_util(location.location_id, db=db)
    
    if not location_to_delete:
        raise HTTPException(status_code=404, detail=f"Localização com esse id '{location.location_id}' não encontrada")
    
    response_data = LocationResponse.model_validate(location_to_delete.__dict__)

    deleted_location = delete_location_by_id_util(location.location_id, db=db)

    if not deleted_location:
        raise HTTPException(status_code=500, detail="Falha ao excluir a localização")
    
    return response_data