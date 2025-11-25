from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models import Professional
from app.database import db

router = APIRouter()

@router.get("/", response_model=List[Professional])
async def get_professionals():
    """Listar todos os profissionais"""
    professionals = db.get_all_professionals()
    return professionals

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