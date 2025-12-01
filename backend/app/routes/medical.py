"""
ROUTES/MEDICAL.PY - ROTAS DE HISTÓRICO MÉDICO E CONSULTAS
=========================================================
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.auth import get_current_user
from app.models import (
    User, MedicalHistoryCreate, MedicalHistoryResponse,
    ConsultationCreate, ConsultationResponse
)
from app.database import db

router = APIRouter()


# =============================================================
# HISTÓRICO MÉDICO
# =============================================================

@router.post("/history", response_model=MedicalHistoryResponse)
async def create_medical_history(
    history: MedicalHistoryCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Cria ou atualiza histórico médico do cliente"""
    
    # Verifica se já existe
    existing = db.get_medical_history_by_client(current_user.id)
    
    if existing:
        # Atualiza existente
        updated = db.update_medical_history(current_user.id, history.model_dump())
        return MedicalHistoryResponse(**updated)
    
    # Cria novo
    history_data = history.model_dump()
    history_data["cliente_id"] = current_user.id
    created = db.create_medical_history(history_data)
    
    return MedicalHistoryResponse(**created)


@router.get("/history", response_model=MedicalHistoryResponse)
async def get_my_medical_history(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Obtém histórico médico do cliente"""
    
    history = db.get_medical_history_by_client(current_user.id)
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail="Histórico médico não encontrado. Por favor, preencha seu histórico."
        )
    
    return MedicalHistoryResponse(**history)


@router.get("/history/{cliente_id}", response_model=MedicalHistoryResponse)
async def get_client_medical_history(
    cliente_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Obtém histórico médico de um cliente específico.
    Apenas profissionais e admins podem acessar.
    """
    
    if current_user.role not in ["profissional", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas profissionais podem ver histórico de outros clientes."
        )
    
    history = db.get_medical_history_by_client(cliente_id)
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail="Histórico médico não encontrado"
        )
    
    return MedicalHistoryResponse(**history)


# =============================================================
# CONSULTAS
# =============================================================

@router.post("/consultations", response_model=ConsultationResponse)
async def create_consultation(
    consultation: ConsultationCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Cria consulta (apenas profissionais)"""
    
    if current_user.role != "profissional":
        raise HTTPException(
            status_code=403,
            detail="Apenas profissionais podem criar consultas"
        )
    
    consultation_data = consultation.model_dump()
    consultation_data["profissional_id"] = current_user.id
    
    created = db.create_consultation(consultation_data)
    
    return ConsultationResponse(**created)


@router.get("/consultations/client/{cliente_id}")
async def get_client_consultations(
    cliente_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Lista consultas do cliente (profissional ou próprio cliente)"""
    
    if current_user.role not in ["profissional", "admin"] and current_user.id != cliente_id:
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para ver consultas de outros clientes"
        )
    
    consultations = db.get_consultations_by_client(cliente_id)
    
    return [ConsultationResponse(**c) for c in consultations]


@router.get("/consultations/my")
async def get_my_consultations(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Lista minhas consultas"""
    
    consultations = db.get_consultations_by_client(current_user.id)
    
    return [ConsultationResponse(**c) for c in consultations]
