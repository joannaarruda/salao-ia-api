"""
APPOINTMENTS.PY - ROTAS DE AGENDAMENTO EXPANDIDAS
==================================================
Inclui:
- Agendamentos com múltiplos serviços
- Com ou sem IA
- Confirmação por profissional
- Consultas e testes de mecha
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Annotated, List, Optional
from datetime import datetime, timedelta

from app.auth import get_current_user
from app.models import (
    User, Appointment, AppointmentCreate, AppointmentStatus,
    TimeSlot, AvailabilityResponse, ProfessionalSchedule
)
from app.database import db

router = APIRouter()

# =============================================================
# CRIAR AGENDAMENTO
# =============================================================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Appointment)
async def create_appointment(
    new_appointment: AppointmentCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Cria novo agendamento com múltiplos serviços.
    
    Funcionalidades:
    - Suporta múltiplos serviços
    - Opção de usar IA ou não
    - Opção de solicitar consulta prévia
    - Opção de solicitar teste de mecha
    """
    
    # Validação de data/hora
    try:
        agendamento_dt = datetime.fromisoformat(new_appointment.data_hora)
        if agendamento_dt < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível agendar para data/hora passada."
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use ISO 8601."
        )
    
    # Calcula duração total dos serviços
    duracao_total = sum(servico.duracao_estimada for servico in new_appointment.servicos)
    
    # Verifica disponibilidade considerando a duração
    conflitos = _check_time_conflicts(
        new_appointment.profissional_id,
        agendamento_dt,
        duracao_total
    )
    
    if conflitos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflito de horário. Profissional já tem agendamento das {conflitos}"
        )
    
    # Cria agendamento
    appointment_data = new_appointment.dict()
    appointment_data["cliente_id"] = current_user.id
    appointment_data["status"] = "pendente"
    
    created_appointment = db.create_appointment(appointment_data)
    
    # Se requer consulta, cria automaticamente
    if new_appointment.requer_consulta:
        consulta_data = {
            "cliente_id": current_user.id,
            "profissional_id": new_appointment.profissional_id,
            "agendamento_id": created_appointment["id"],
            "objetivo": f"Consulta para {', '.join([s.tipo for s in new_appointment.servicos])}",
            "estado_atual_cabelo": "",
            "desejos_cliente": new_appointment.observacoes or "",
            "requer_teste_mecha": new_appointment.requer_teste_mecha
        }
        db.create_consultation(consulta_data)
    
    return Appointment(**created_appointment)


def _check_time_conflicts(profissional_id: str, data_hora: datetime, duracao: int) -> Optional[str]:
    """Verifica conflitos de horário considerando duração"""
    data_str = data_hora.date().isoformat()
    agendamentos = db.get_professional_appointments(profissional_id, data_str)
    
    fim_novo = data_hora + timedelta(minutes=duracao)
    
    for apt in agendamentos:
        if apt.get("status") in ["cancelado"]:
            continue
        
        apt_inicio = datetime.fromisoformat(apt["data_hora"])
        apt_duracao = sum(s.get("duracao_estimada", 60) for s in apt.get("servicos", []))
        apt_fim = apt_inicio + timedelta(minutes=apt_duracao)
        
        # Verifica sobreposição
        if not (fim_novo <= apt_inicio or data_hora >= apt_fim):
            return f"{apt_inicio.strftime('%H:%M')} - {apt_fim.strftime('%H:%M')}"
    
    return None


# =============================================================
# LISTAR AGENDAMENTOS
# =============================================================

@router.get("/my", response_model=List[Appointment])
async def get_my_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    status: Optional[AppointmentStatus] = None
):
    """Lista agendamentos do usuário logado"""
    appointments = db.get_user_appointments(current_user.id)
    
    if status:
        appointments = [a for a in appointments if a.get("status") == status]
    
    return [Appointment(**a) for a in appointments]


@router.get("/professional", response_model=List[Appointment])
async def get_professional_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    data: Optional[str] = Query(None, description="Data no formato YYYY-MM-DD"),
    status: Optional[AppointmentStatus] = None
):
    """
    Lista agendamentos do profissional.
    Apenas usuários com role 'profissional' ou 'admin' podem acessar.
    """
    if current_user.role not in ["profissional", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas profissionais."
        )
    
    appointments = db.get_professional_appointments(current_user.id, data)
    
    if status:
        appointments = [a for a in appointments if a.get("status") == status]
    
    return [Appointment(**a) for a in appointments]


@router.get("/professional/schedule", response_model=ProfessionalSchedule)
async def get_professional_schedule(
    current_user: Annotated[User, Depends(get_current_user)],
    data: str = Query(..., description="Data no formato YYYY-MM-DD")
):
    """
    Retorna agenda completa do profissional para uma data específica.
    Inclui agendamentos e horários disponíveis.
    """
    if current_user.role not in ["profissional", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas profissionais."
        )
    
    appointments = db.get_professional_appointments(current_user.id, data)
    
    # Gera horários disponíveis
    horarios_disponiveis = []
    data_obj = datetime.fromisoformat(data)
    
    for hora in range(9, 19):
        for minuto in [0, 30]:
            horario = data_obj.replace(hour=hora, minute=minuto)
            horario_str = horario.isoformat()
            
            conflito = _check_time_conflicts(current_user.id, horario, 30)
            if not conflito:
                horarios_disponiveis.append(horario_str)
    
    return ProfessionalSchedule(
        profissional_id=current_user.id,
        data=data,
        agendamentos=[Appointment(**a) for a in appointments],
        horarios_disponiveis=horarios_disponiveis,
        total_agendamentos=len(appointments)
    )


# =============================================================
# CONFIRMAR/ATUALIZAR AGENDAMENTO
# =============================================================

@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    new_status: AppointmentStatus,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Atualiza status do agendamento.
    Profissionais podem confirmar/cancelar seus agendamentos.
    Clientes podem cancelar seus próprios agendamentos.
    """
    # Busca agendamento
    appointments = db.get_all_appointments()
    appointment = next((a for a in appointments if a["id"] == appointment_id), None)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Verifica permissões
    is_professional = current_user.role == "profissional" and appointment["profissional_id"] == current_user.id
    is_client = current_user.role == "cliente" and appointment["cliente_id"] == current_user.id
    is_admin = current_user.role == "admin"
    
    if not (is_professional or is_client or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para alterar este agendamento"
        )
    
    # Clientes só podem cancelar
    if is_client and new_status not in ["cancelado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clientes só podem cancelar agendamentos"
        )
    
    # Atualiza status
    updated = db.update_appointment_status(
        appointment_id,
        new_status,
        current_user.id if is_professional else None
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar agendamento"
        )
    
    return {
        "message": "Status atualizado com sucesso",
        "appointment": Appointment(**updated)
    }


# =============================================================
# VERIFICAR DISPONIBILIDADE
# =============================================================

@router.get("/available", response_model=AvailabilityResponse)
async def get_available_times(
    profissional_id: str,
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
    duracao: int = Query(60, description="Duração em minutos"),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Retorna horários disponíveis para um profissional em uma data.
    Considera a duração do serviço para evitar conflitos.
    """
    try:
        data_obj = datetime.fromisoformat(data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    
    # Horário de funcionamento: 9h às 18h30
    horarios = []
    
    for hora in range(9, 19):
        for minuto in [0, 30]:
            horario = data_obj.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            horario_str = horario.isoformat()
            
            # Verifica se há conflito
            conflito = _check_time_conflicts(profissional_id, horario, duracao)
            disponivel = conflito is None
            
            horarios.append(TimeSlot(
                horario=horario_str,
                disponivel=disponivel,
                profissional_id=profissional_id,
                duracao_disponivel=duracao if disponivel else 0
            ))
    
    return AvailabilityResponse(
        data=data,
        profissional_id=profissional_id,
        horarios=horarios
    )
