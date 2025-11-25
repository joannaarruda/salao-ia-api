from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated, List
from datetime import datetime, timedelta

from ..auth import get_current_user
from ..models import User, Appointment, AppointmentCreate
from ..database import db

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)

# -------------------------------------------------------------
# ROTA 1: CRIAR NOVO AGENDAMENTO
# -------------------------------------------------------------

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Appointment)
async def create_appointment(
    new_appointment: AppointmentCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Cria um novo agendamento, verificando a disponibilidade.
    O ID do utilizador é obtido a partir do token de autenticação.
    """
    
    # Validação de Data/Hora: Garante que a data/hora não é retroativa
    try:
        agendamento_dt = datetime.fromisoformat(new_appointment.data_hora)
        if agendamento_dt < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível agendar para uma data e hora que já passou."
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data e hora inválido. Use o formato ISO 8601."
        )
    
    # Verifica se já existe agendamento nesse horário
    existing = db.get_appointments_by_datetime(
        new_appointment.data_hora,
        new_appointment.profissional_id
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este horário já está ocupado. Escolha outro horário."
        )
    
    # Cria o agendamento
    appointment_data = new_appointment.dict()
    appointment_data["usuario_id"] = current_user.id
    
    created_appointment = db.create_appointment(appointment_data)
    
    return Appointment(**created_appointment)


# -------------------------------------------------------------
# ROTA 2: LISTAR AGENDAMENTOS DO USUÁRIO
# -------------------------------------------------------------

@router.get("/my", response_model=List[Appointment])
async def get_my_appointments(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retorna todos os agendamentos do usuário autenticado.
    """
    appointments = db.get_user_appointments(current_user.id)
    return [Appointment(**a) for a in appointments]


# -------------------------------------------------------------
# ROTA 3: VERIFICAR HORÁRIOS DISPONÍVEIS
# -------------------------------------------------------------

@router.get("/available")
async def get_available_times(
    profissional_id: str,
    data: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retorna os horários disponíveis para um profissional em uma data específica.
    """
    try:
        # Parse da data
        data_obj = datetime.fromisoformat(data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    
    # Horários de funcionamento (9h às 18h)
    horarios_disponiveis = []
    
    for hora in range(9, 18):
        for minuto in [0, 30]:
            horario = data_obj.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            horario_str = horario.isoformat()
            
            # Verifica se está disponível
            existing = db.get_appointments_by_datetime(horario_str, profissional_id)
            
            horarios_disponiveis.append({
                "horario": horario_str,
                "disponivel": len(existing) == 0
            })
    
    return horarios_disponiveis