from collections import defaultdict
from logging import getLogger
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.schemas.analytical import ProvinceAnalytics, SupplierAnalytics
from app.schemas.purchase import PurchaseEnum
from app.schemas.vehicle import PropulsionEnum
from app.utils.location import get_locations_by_province_util, get_province_by_location_province_util
from app.utils.part import get_part_by_id_util, get_parts_by_supplier_id_util
from app.utils.purchase import get_purchases_by_part_id_util, get_purchases_by_purchase_type_util
from app.utils.supplier import get_supplier_by_location_id_util, get_supplier_by_name_util
from app.utils.vehicle import get_vehicle_by_id_util, get_vehicle_by_model_util, get_vehicle_by_propulsion_util
from app.utils.warranty import get_warranties_by_part_id_util, get_warranties_by_vehicle_id_util

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = getLogger(__name__)

@router.get("/supplier_by_province/{location_province}")
def analytics_supplier_by_province(location_province:str, db: Session = Depends(get_db)) -> ProvinceAnalytics:
    """
    Obtém análises detalhadas de fornecedores por província, incluindo:
    - Total de vendas por fornecedor
    - Número de produtos fornecidos
    - Top 5 fornecedores com maior volume de vendas
    - Comparação com a média da província
    """
    
    province_exists = get_province_by_location_province_util(location_province, db=db)
    if not province_exists:
            raise HTTPException(status_code=404, detail=f"Província '{location_province}' não encontrada")
    try:
        locations = get_locations_by_province_util(location_province, db=db)
        location_ids = [loc.location_id for loc in locations]
            
        if not location_ids:
            return ProvinceAnalytics(
                province=location_province,
                total_suppliers=0,
                total_parts=0,
                total_purchases=0,
                bulk_percentage=0,
                warranty_percentage=0,
                suppliers_by_market={},
                top_suppliers=[]
            )
        
        all_suppliers = []
        
        # Para cada localização, obter todos os fornecedores
        for location_id in location_ids:
            # Esta função provavelmente retorna uma lista de fornecedores
            suppliers_at_location = get_supplier_by_location_id_util(location_id, db=db)
            
            # Se a função retornar um único fornecedor em vez de uma lista, garanta que seja uma lista
            if not isinstance(suppliers_at_location, list):
                suppliers_at_location = [suppliers_at_location]
                
            # Adicionar fornecedores desta localização à lista geral
            all_suppliers.extend(suppliers_at_location)
        
        total_suppliers = len(all_suppliers)
        all_parts = []
        all_purchases = []
        
        # Mapeamento de partes para fornecedores
        part_to_supplier = {}
        
        # Para cada fornecedor, obter peças
        for supplier in all_suppliers:
            # Obter partes deste fornecedor
            supplier_parts = get_parts_by_supplier_id_util(supplier.supplier_id, db=db)
            
            # Se a função retornar um único item em vez de uma lista, garanta que seja uma lista
            if not isinstance(supplier_parts, list):
                supplier_parts = [supplier_parts]
                
            # Adicionar à lista geral de partes
            all_parts.extend(supplier_parts)
            
            # Adicionar ao mapeamento
            for part in supplier_parts[:1]:
                part_to_supplier[part.part_id] = supplier.supplier_id
                
                # Obter compras para cada parte
                part_purchases = get_purchases_by_part_id_util(part.part_id, db=db)
                
                # Se a função retornar um único item em vez de uma lista, garanta que seja uma lista
                if not isinstance(part_purchases, list):
                    part_purchases = [part_purchases]
                    
                # Adicionar à lista geral de compras
                all_purchases.extend(part_purchases)

        bulk_count = sum(1 for p in all_purchases if p.purchase_type == PurchaseEnum.bulk)
        warranty_count = sum(1 for p in all_purchases if p.purchase_type == PurchaseEnum.warranty)
        # Análise por mercado
        market_counts = {}
        for loc in locations:
            if loc.market not in market_counts:
                market_counts[loc.market] = 0
            
            # Contar fornecedores neste mercado
            suppliers_in_loc = sum(1 for s in all_suppliers if s.location_id == loc.location_id)
            market_counts[loc.market] += suppliers_in_loc
        
        # Preparar análise para cada fornecedor
        supplier_analytics = []
        
        for supplier in all_suppliers:
            # Encontrar localização do fornecedor
            location = next((loc for loc in locations if loc.location_id == supplier.location_id), None)
            
            # Encontrar partes deste fornecedor
            supplier_parts = [part for part in all_parts if part.supplier_id == supplier.supplier_id]
            supplier_part_ids = [part.part_id for part in supplier_parts]
            
            # Encontrar compras para as partes deste fornecedor
            supplier_purchases = [p for p in all_purchases if p.part_id in supplier_part_ids]
            
            # Contagem de tipos de compra para este fornecedor
            supplier_bulk = sum(1 for p in supplier_purchases if p.purchase_type == PurchaseEnum.bulk)
            supplier_warranty = sum(1 for p in supplier_purchases if p.purchase_type == PurchaseEnum.warranty)
            
            analytics = SupplierAnalytics(
                supplier_id=supplier.supplier_id,
                supplier_name=supplier.supplier_name,
                supplier_cpf=supplier.supplier_cpf,
                location_id=supplier.location_id,
                market=location.market if location else None,
                country=location.country if location else "",
                province=location.province if location else "",
                city=location.city if location else "",
                total_parts=len(supplier_parts),
                total_purchases=len(supplier_purchases),
                bulk_purchases=supplier_bulk,
                warranty_purchases=supplier_warranty
            )
            
            supplier_analytics.append(analytics)
        
        # Ordenar fornecedores por número total de compras
        supplier_analytics.sort(key=lambda x: x.total_purchases, reverse=True)
        top_suppliers = supplier_analytics[:5] #TOP 5 Fornecedores
        
        response = ProvinceAnalytics(
            province=location_province,
            total_suppliers=total_suppliers,
            total_parts=len(all_parts),
            total_purchases=len(all_purchases),
            bulk_percentage=(bulk_count / len(all_purchases) * 100) if all_purchases else 0,
            warranty_percentage=(warranty_count / len(all_purchases) * 100) if all_purchases else 0,
            suppliers_by_market=market_counts,
            top_suppliers=top_suppliers
        )
        return response.model_dump()
        
    except Exception as e:
        logger.error(f"Erro ao analisar fornecedores na província {location_province}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar análise: {str(e)}")
    
@router.get("/purchases_by_type/{purchase_type}")
def analytics_by_purchase_type(purchase_type: PurchaseEnum, db: Session = Depends(get_db)) -> dict:
    """
    Obtém estatísticas de compras por tipo (bulk, warranty)
    """
    
    purchases = get_purchases_by_purchase_type_util(purchase_type, db=db)
    if not purchases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail={
                "purchase_type": purchase_type.value, 
                "total_count": 0, 
                "message": f"Nenhuma compra do tipo {purchase_type.value} encontrada"
            }
        )
    try:
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/vehicle_model/{vehicle_model}")
def analytics_by_vehicle_model(vehicle_model: str, db: Session = Depends(get_db)) -> dict:
    """
    Obtém estatísticas baseado no modelo do veículo
    """
    vehicles = get_vehicle_by_model_util(vehicle_model, db=db)

    if not vehicles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f" 'vehicle_model': {vehicle_model}, 'total_count': 0, 'message': f'Nenhum modelo {vehicle_model} de carro encontrado'"
            )
    try:
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
            warranties = get_warranties_by_vehicle_id_util(vehicle.vehicle_id, db=db)
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar estatísticas: {str(e)}"
        )
    
@router.get("/propulsion_type/{propulsion_type}")
def analytics_part_by_propulsion_type(propulsion_type: PropulsionEnum, db: Session = Depends(get_db)) -> dict:
    """
    Obtém a quantidade de peças vendidas baseado na propulsão do veículo
    """
    
    vehicles = get_vehicle_by_propulsion_util(propulsion_type, db=db)
    if not vehicles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f" 'propulsion_type_vehicle': {propulsion_type.value}, 'total_count': 0, 'message': f'Nenhum tipo de propulsão {propulsion_type.value} de carro encontrado'"
            )
    try:
        # Inicializa dicionários para estatísticas
        part_stats = defaultdict(lambda: {"count": 0, "vehicles": 0, "models": set()})
        model_count = defaultdict(int)
        total_parts = 0
        
        # Para cada veículo, busca as garantias relacionadas e compila estatísticas de peças
        for vehicle in vehicles:
            model_count[vehicle.model] += 1
            
            # Obtém as garantias associadas ao veículo
            warranties = get_warranties_by_vehicle_id_util(vehicle.vehicle_id, db=db)
            
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
            part = get_part_by_id_util(part_id, db=db)
            part_name = part.part_name if part else f"Peça ID {part_id}"
            
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar estatísticas por tipo de propulsão: {str(e)}"
        )

@router.get("/part_by_suppliers/{supplier_name}")
def analytics_supplier_by_part(supplier_name: str, db: Session = Depends(get_db)) -> dict:
    """
    Obtém análise detalhada das peças fornecidas por um determinado fornecedor,
    incluindo estatísticas de falhas, uso em diferentes modelos de veículos e tendências.
    """
    supplier = get_supplier_by_name_util(supplier_name, db=db)

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fornecedor '{supplier_name}' não encontrado"
        )
    try:
        parts = get_parts_by_supplier_id_util(supplier.supplier_id, db=db)
        if not parts:
            return {
                "supplier": {
                    "supplier_id": supplier.supplier_id,
                    "name": supplier.supplier_name,
                },
                "total_parts": 0,
                "message": "Nenhuma peça encontrada para este fornecedor",
                "parts_analysis": []
            }
        # Inicializa análise de peças
        parts_analysis = []
        
        for part in parts:
            # Busca garantias relacionadas a esta peça
            warranties = get_warranties_by_part_id_util(part.part_id, db=db)
            
            # Agrupa por modelo de veículo e tipo de propulsão
            model_stats = defaultdict(int)
            propulsion_stats = defaultdict(int)
            failure_classifications = defaultdict(int)
            vehicle_years = defaultdict(int)
            
            # Coleta IDs únicos de veículos para calcular taxa de falha
            unique_vehicles = set()
            
            for warranty in warranties:
                # Obtém informações do veículo
                vehicle = get_vehicle_by_id_util(warranty.vehicle_id, db=db)
                if vehicle:
                    model_stats[vehicle.model] += 1
                    propulsion_stats[vehicle.propulsion] += 1
                    vehicle_years[vehicle.year] += 1
                    unique_vehicles.add(vehicle.vehicle_id)
                
                # Estatísticas de classificação de falhas
                failure_classifications[warranty.classified_failured] += 1
            
            # Calcula tempo médio até falha (em dias)
            avg_time_to_failure = 0
            if warranties:
                total_days = 0
                count = 0
                for warranty in warranties:
                    vehicle = get_vehicle_by_id_util(warranty.vehicle_id, db=db)
                    if vehicle:
                        days_to_failure = (warranty.repair_date - vehicle.prod_date).days
                        if days_to_failure > 0:  # Previne valores negativos
                            total_days += days_to_failure
                            count += 1
                
                if count > 0:
                    avg_time_to_failure = total_days / count
            
            # Formata estatísticas para incluir na análise
            formatted_model_stats = [
                {"model": model, "count": count, "percentage": round((count / len(warranties)) * 100, 2)}
                for model, count in sorted(model_stats.items(), key=lambda x: x[1], reverse=True)
            ]
            
            formatted_propulsion_stats = [
                {"type": prop_type, "count": count, "percentage": round((count / len(warranties)) * 100, 2)}
                for prop_type, count in sorted(propulsion_stats.items(), key=lambda x: x[1], reverse=True)
            ]
            
            formatted_failure_stats = [
                {"classification": classification, "count": count, "percentage": round((count / len(warranties)) * 100, 2)}
                for classification, count in sorted(failure_classifications.items(), key=lambda x: x[1], reverse=True)
            ]
            
            # Agrega anos por faixa para identificar tendências
            year_ranges = defaultdict(int)
            for year, count in vehicle_years.items():
                range_start = (year // 5) * 5  # Agrupa em faixas de 5 anos
                range_key = f"{range_start}-{range_start+4}"
                year_ranges[range_key] += count
                
            formatted_year_stats = [
                {"range": year_range, "count": count, "percentage": round((count / len(warranties)) * 100, 2)}
                for year_range, count in sorted(year_ranges.items())
            ]
            
            # Adiciona análise desta peça ao resultado
            parts_analysis.append({
                "part_id": part.part_id,
                "name": part.part_name,
                "warranty_stats": {
                    "total_claims": len(warranties),
                    "affected_vehicles": len(unique_vehicles),
                    "avg_time_to_failure_days": round(avg_time_to_failure, 1),
                    "failure_classifications": formatted_failure_stats
                },
                "vehicle_stats": {
                    "models": formatted_model_stats,
                    "propulsion_types": formatted_propulsion_stats,
                    "year_distribution": formatted_year_stats
                }
            })
        
        # Ordena as peças por número de reclamações (decrescente)
        parts_analysis.sort(key=lambda x: x["warranty_stats"]["total_claims"], reverse=True)
        
        # Retorna a análise completa
        return {
            "supplier": {
                "supplier_id": supplier.supplier_id,
                "name": supplier.supplier_name,
                "cpf": supplier.supplier_cpf if hasattr(supplier, "supplier_cpf") else "",
            },
            "total_parts": len(parts),
            "parts_with_warranty_claims": sum(1 for p in parts_analysis if p["warranty_stats"]["total_claims"] > 0),
            "parts_analysis": parts_analysis
        }
    except Exception as e:
        # Captura outras exceções e retorna uma resposta de erro
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar estatísticas de peças por fornecedor: {str(e)}"
        )