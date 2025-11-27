from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Annotated, Optional
from app.models import Professional
from app.database import db

router = APIRouter()

@router.get("/", response_model=List[Professional])
async def list_professionals(
    tipo_servico: Annotated[Optional[str], Query(description="Filtrar por tipo de serviço")] = None,
):
    """
    Lista todos os profissionais. Pode ser filtrada pelo tipo de serviço.
    ROTA PÚBLICA - não requer autenticação
    """
    if tipo_servico:
        professionals_data = db.get_professionals_by_type(tipo_servico.lower())
    else:
        professionals_data = db.get_all_professionals()
    
    return [Professional(**p) for p in professionals_data]

@router.get("/{professional_id}", response_model=Professional)
async def get_professional(professional_id: str):
    """Buscar profissional por ID"""
    professional = db.get_professional_by_id(professional_id)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado"
        )
    return professional
