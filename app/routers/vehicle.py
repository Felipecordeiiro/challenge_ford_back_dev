from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.model_vehicle import Vehicle
from app.schemas.vehicle import VehicleDelete, VehicleRequest, VehicleResponse, VehicleUpdate
from app.utils.vehicle import delete_vehicle_by_id_util, get_all_vehicles_util, get_vehicle_by_id_util, get_vehicle_by_model_util, get_vehicle_by_propulsion_util, get_vehicle_by_year_util, update_vehicle_by_id_util

router = APIRouter(prefix="/vehicle", tags=["vehicle"])

@router.get("/")
def list_vehicle(db: Session = Depends(get_db)) -> list[VehicleResponse]:
    """
    Lista todos os veículos do banco de dados.
    """
    all_vehicles = get_all_vehicles_util(db=db)
    return [VehicleResponse.model_validate(vehicle.__dict__) for vehicle in all_vehicles]

@router.get("/id/{vehicle_id}")
def get_vehicle_by_id(vehicle_id:str, db: Session = Depends(get_db)) -> VehicleResponse:
    """
    Obtém um veículo pelo seu ID.
    """
    vehicle = get_vehicle_by_id_util(vehicle_id, db=db)
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Nenhum carro encontrada com esse id '{vehicle_id}'")
    return VehicleResponse.model_validate(vehicle.__dict__)

@router.get("/model/{vehicle_model}")
def get_vehicle_by_model(vehicle_model:str, db: Session = Depends(get_db)) -> list[VehicleResponse]:
    """
    Lista todos os veículos baseado no modelo do veículo.
    """
    vehicles = get_vehicle_by_model_util(vehicle_model, db=db)
    if not vehicles:
        raise HTTPException(status_code=404, detail=f"Nenhum carro encontrada desse modelo '{vehicle_model}'")
    return [VehicleResponse.model_validate(vehicle.__dict__) for vehicle in vehicles]

@router.get("/propulsion/{vehicle_propulsion}")
def get_vehicle_by_propulsion(vehicle_propulsion:str, db: Session = Depends(get_db)) -> list[VehicleResponse]:
    """
    Lista todos os veículos baseado na propulsão do veículo.
    """
    vehicles = get_vehicle_by_propulsion_util(vehicle_propulsion, db=db)
    if not vehicles:
        raise HTTPException(status_code=404, detail=f"Nenhum carro encontrado com esse tipo de propulsão '{vehicle_propulsion}'")
    return [VehicleResponse.model_validate(vehicle.__dict__) for vehicle in vehicles]

@router.get("/year/{vehicle_year}")
def get_vehicle_by_year(vehicle_year:int, db: Session = Depends(get_db)) -> list[VehicleResponse]:
    vehicles = get_vehicle_by_year_util(vehicle_year, db=db)
    if not vehicles:
        raise HTTPException(status_code=404, detail=f"Nenhum carro encontrado nesse ano '{vehicle_year}'")
    return [VehicleResponse.model_validate(vehicle.__dict__) for vehicle in vehicles]

@router.post("/")
def create_vehicle(vehicle: VehicleRequest, db: Session = Depends(get_db)) -> VehicleResponse:
    """
    Cria um veículo.
    """
    new_vehicle = Vehicle(**vehicle.model_dump())
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return VehicleResponse(**new_vehicle.__dict__)

@router.put("/id/{vehicle_id}")
def update_vehicle(vehicle: VehicleUpdate, vehicle_id: int, db: Session = Depends(get_db)) -> VehicleResponse:
    """
    Atualiza um veículo.
    """
    update_data = vehicle.model_dump()
    update_data["vehicle_id"] = vehicle_id
    rows_updated = update_vehicle_by_id_util(**update_data, db=db)

    if not rows_updated:
        raise HTTPException(status_code=404, detail=f"Não foi possível atualizar o veículo")
    
    db.commit()
    updated_vehicle = get_vehicle_by_id_util(vehicle_id, db=db)

    if not updated_vehicle:
        raise HTTPException(status_code=404, detail=f"Não foi possível encontrar o veículo após atualização")
    
    return VehicleResponse.model_validate(updated_vehicle.__dict__)

@router.delete("/id/{vehicle_id}")
def delete_vehicle(vehicle: VehicleDelete, db: Session = Depends(get_db)) -> VehicleResponse:
    """
    Deleta um veículo.
    """
    vehicle_to_delete = get_vehicle_by_id_util(vehicle.vehicle_id, db=db)
    
    if not vehicle_to_delete:
        raise HTTPException(status_code=404, detail=f"Veículo com o id '{vehicle.vehicle_id}' não encontrada")
    
    response_data = VehicleResponse.model_validate(vehicle_to_delete.__dict__)

    deleted_vehicle = delete_vehicle_by_id_util(vehicle.vehicle_id, db=db)

    if not deleted_vehicle:
        raise HTTPException(status_code=500, detail="Falha ao excluir a veículo")
    
    return response_data