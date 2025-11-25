from fastapi import APIRouter, status, Depends, Query
from typing import List, Annotated, Optional

from ..auth import get_current_user
from ..models import Professional, User
from ..database import db

router = APIRouter(
    prefix="/professionals",
    tags=["professionals"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[Professional])
async def list_professionals(
    tipo_servico: Annotated[Optional[str], Query(description="Filtrar por tipo de serviço (ex: cabelo, unha)")] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Retorna a lista de todos os profissionais. Pode ser filtrada pelo tipo de serviço.
    """
    if tipo_servico:
        professionals_data = db.get_professionals_by_type(tipo_servico.lower())
    else:
        professionals_data = db.get_all_professionals()
    
    return [Professional(**p) for p in professionals_data]