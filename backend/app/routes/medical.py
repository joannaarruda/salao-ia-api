"""
MEDICAL.PY - ROTAS DE HISTÓRICO MÉDICO E CONSULTAS
===================================================
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from app.auth import get_current_user
from app.models import (
    User, MedicalHistory, MedicalHistoryCreate, MedicalHistoryResponse,
    Consultation, ConsultationCreate, ConsultationResponse
)
from app.database import db

router = APIRouter()

# HISTÓRICO MÉDICO

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
        updated = db.update_medical_history(current_user.id, history.dict())
        return MedicalHistoryResponse(**updated)
    
    # Cria novo
    history_data = history.dict()
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
        raise HTTPException(404, "Histórico médico não encontrado")
    
    return MedicalHistoryResponse(**history)

# CONSULTAS

@router.post("/consultations", response_model=ConsultationResponse)
async def create_consultation(
    consultation: ConsultationCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Cria consulta (apenas profissionais)"""
    if current_user.role != "profissional":
        raise HTTPException(403, "Apenas profissionais")
    
    consultation_data = consultation.dict()
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
        raise HTTPException(403, "Sem permissão")
    
    consultations = db.get_consultations_by_client(cliente_id)
    return [ConsultationResponse(**c) for c in consultations]