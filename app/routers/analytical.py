from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.schemas.purchase import PurchaseEnum
from app.schemas.vehicle import PropulsionEnum
from app.utils.location import get_locations_by_province_util
from app.utils.part import get_part_by_id_util
from app.utils.purchase import get_purchases_by_purchase_type_util
from app.utils.supplier import get_supplier_by_location_id_util
from app.utils.vehicle import get_vehicle_by_model_util, get_vehicle_by_propulsion_util
from app.utils.warranty import get_warranties_by_vehicle_id

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/supplier_by_province/{location_province}")
def analytics_supplier_by_province(location_province:str, db: Session = Depends(get_db)) -> dict:
    """
    Obtém o total de vendas de fornecedores por província
    """
    locations = get_locations_by_province_util(location_province, db=db)
    suppliers = get_supplier_by_location_id_util(locations[0].location_id, db=db)

@router.get("/purchases_by_type/{purchase_type}")
def analytics_by_purchase_type(purchase_type: PurchaseEnum, db: Session = Depends(get_db)) -> dict:
    """
    Obtém estatísticas de compras por tipo (bulk, warranty)
    """
    try:
        purchases = get_purchases_by_purchase_type_util(purchase_type, db=db)
        if not purchases:
            raise HTTPException(
                status_code=404, 
                detail=f" 'purchase_type': {purchase_type.value}, 'total_count': 0, 'message': f'Nenhuma compra do tipo {purchase_type.value} encontrada'"
                )
        # Agrupa por mês para análise de tendência
        monthly_data = defaultdict(int)
        parts_count = defaultdict(int)

        for purchase in purchases:
            month_year = purchase.purchase_date.strftime("%Y-%m")
            monthly_data[month_year] += 1
            
            # Contabiliza quais peças são mais compradas por tipo
            parts_count[purchase.part_id] += 1

        # Obtém detalhes das top 5 peças mais compradas
        top_parts = []
        for part_id, count in sorted(parts_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            part = get_part_by_id_util(part_id, db)
            if part:
                top_parts.append({
                    "part_id": part.part_id,
                    "part_name": part.part_name,
                    "count": count
                })
        
        return {
            "purchase_type": purchase_type,
            "total_count": len(purchases),
            "monthly_trend": [
                {"month": k, "count": v} for k, v in sorted(monthly_data.items())
            ],
            "top_parts": top_parts,
            "first_purchase_date": min(p.purchase_date for p in purchases),
            "last_purchase_date": max(p.purchase_date for p in purchases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vehicle_model/{vehicle_model}")
def analytics_by_vehicle_model(vehicle_model: str, db: Session = Depends(get_db)) -> dict:
    """
    Obtém estatísticas baseado no modelo do veículo
    """
    try:
        vehicles = get_vehicle_by_model_util(vehicle_model, db=db)

        if not vehicles:
            raise HTTPException(
                status_code=404, 
                detail=f" 'vehicle_model': {vehicle_model}, 'total_count': 0, 'message': f'Nenhum modelo {vehicle_model} de carro encontrado'"
                )

        parts_count = defaultdict(int)
        propulsion_count = defaultdict(int)
        total_warranty_claims = 0
        years_count = defaultdict(int)

        for vehicle in vehicles:
            # Contagem por tipo de propulsão
            propulsion_count[vehicle.propulsion] += 1
            
            # Contagem por ano
            years_count[vehicle.year] += 1
            
            # Obtém garantias relacionadas a este veículo
            warranties = get_warranties_by_vehicle_id(vehicle.vehicle_id, db=db)
            total_warranty_claims += len(warranties)
            
            # Conta ocorrências de peças em garantias
            for warranty in warranties:
                parts_count[warranty.part_id] += 1
        top_parts = []
        if parts_count:
            # Ordena as peças por contagem (decrescente)
            sorted_parts = sorted(parts_count.items(), key=lambda x: x[1], reverse=True)
            
            # Obtém os detalhes das 5 peças mais comuns
            for part_id, count in sorted_parts[:5]:
                part = get_part_by_id_util(part_id, db=db)
                part_name = part.part_name if part else f"Peça ID {part_id}"
                top_parts.append({
                    "part_id": part_id,
                    "name": part_name,
                    "count": count,
                    "percentage": round((count / total_warranty_claims) * 100, 2) if total_warranty_claims > 0 else 0
                })
        
        # Prepara os dados de propulsão para o retorno
        propulsion_stats = [
            {"type": prop_type, "count": count, "percentage": round((count / len(vehicles)) * 100, 2)}
            for prop_type, count in propulsion_count.items()
        ]
        
        # Prepara os dados de anos para o retorno
        year_stats = [
            {"year": year, "count": count, "percentage": round((count / len(vehicles)) * 100, 2)}
            for year, count in years_count.items()
        ]
        
        # Retorna as estatísticas compiladas
        return {
            "vehicle_model": vehicle_model,
            "total_count": len(vehicles),
            "propulsion_stats": propulsion_stats,
            "year_distribution": year_stats,
            "warranty_stats": {
                "total_claims": total_warranty_claims,
                "claims_per_vehicle": round(total_warranty_claims / len(vehicles), 2) if vehicles else 0,
                "top_failing_parts": top_parts
            }
        }
    
    except Exception as e:
        # Captura outras exceções e retorna uma resposta de erro
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar estatísticas: {str(e)}"
        )
    
@router.get("/propulsion_type/{propulsion_type}")
def analytics_part_by_propulsion_type(propulsion_type: PropulsionEnum, db: Session = Depends(get_db)) -> dict:
    """
    Obtém a quantidade de peças vendidas baseado na propulsão do veículo
    """
    try:
        vehicles = get_vehicle_by_propulsion_util(propulsion_type, db)
        if not vehicles:
            raise HTTPException(
                status_code=404, 
                detail=f" 'propulsion_type_vehicle': {propulsion_type}, 'total_count': 0, 'message': f'Nenhum tipo de propulsão {propulsion_type} de carro encontrado'"
                )
        # Inicializa dicionários para estatísticas
        part_stats = defaultdict(lambda: {"count": 0, "vehicles": 0, "models": set()})
        model_count = defaultdict(int)
        total_parts = 0
        
        # Para cada veículo, busca as garantias relacionadas e compila estatísticas de peças
        for vehicle in vehicles:
            model_count[vehicle.model] += 1
            
            # Obtém as garantias associadas ao veículo
            warranties = get_warranties_by_vehicle_id(vehicle.vehicle_id, db=db)
            
            # Rastreia quais veículos têm problemas com quais peças
            vehicle_parts = set()
            
            for warranty in warranties:
                part_id = warranty.part_id
                total_parts += 1
                part_stats[part_id]["count"] += 1
                part_stats[part_id]["models"].add(vehicle.model)
                
                if part_id not in vehicle_parts:
                    vehicle_parts.add(part_id)
                    part_stats[part_id]["vehicles"] += 1
            
        # Formata as estatísticas de peças para o retorno
        formatted_part_stats = []
        for part_id, stats in part_stats.items():
            # Busca informações da peça no banco de dados
            part = get_part_by_id_util(part_id)
            part_name = part.name if part else f"Peça ID {part_id}"
            
            formatted_part_stats.append({
                "part_id": part_id,
                "name": part_name,
                "count": stats["count"],
                "vehicles_affected": stats["vehicles"],
                "percentage_of_vehicles": round((stats["vehicles"] / len(vehicles)) * 100, 2),
                "models_affected": list(stats["models"]),
                "average_per_affected_vehicle": round(stats["count"] / stats["vehicles"], 2) if stats["vehicles"] > 0 else 0
            })
        
        # Ordena as estatísticas de peças pela contagem (decrescente)
        formatted_part_stats.sort(key=lambda x: x["count"], reverse=True)
        
        # Prepara as estatísticas de modelos para o retorno
        model_stats = [
            {"model": model, "count": count, "percentage": round((count / len(vehicles)) * 100, 2)}
            for model, count in model_count.items()
        ]
        
        # Retorna as estatísticas compiladas
        return {
            "propulsion_type": propulsion_type,
            "total_vehicles": len(vehicles),
            "total_parts_replaced": total_parts,
            "average_parts_per_vehicle": round(total_parts / len(vehicles), 2) if vehicles else 0,
            "model_distribution": model_stats,
            "part_stats": formatted_part_stats
        }
        
    except Exception as e:
        # Captura outras exceções e retorna uma resposta de erro
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar estatísticas por tipo de propulsão: {str(e)}"
        )

@router.get("/part_by_suppliers/{supplier_name}")
def analytics_supplier_by_part(supplier_name: str, db: Session = Depends(get_db)) -> dict:
    """
    Obtém análise detalhada das peças fornecidas por um determinado fornecedor,
    incluindo estatísticas de falhas, uso em diferentes modelos de veículos e tendências.
    """
    try:
        supplier = get_supplier_by_location_id_util