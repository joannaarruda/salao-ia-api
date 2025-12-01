"""
ROUTES/APPOINTMENTS.PY - ROTAS DE AGENDAMENTOS
===============================================
Sistema completo de agendamentos com:
- Múltiplos serviços
- Com ou sem IA
- Confirmação por profissional
- Validação de histórico médico
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Annotated, List, Optional
from datetime import datetime, timedelta

from app.auth import get_current_user
from app.models import (
    User, Appointment, AppointmentCreate, AppointmentStatus,
    TimeSlot, AvailabilityResponse, ProfessionalSchedule, Servico
)
from app.database import db

router = APIRouter()


# =============================================================
# FUNÇÕES AUXILIARES
# =============================================================

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


def _verificar_historico_medico_obrigatorio(servicos: list, user_id: str):
    """
    Verifica se os serviços requerem histórico médico e se está preenchido.
    """
    # Serviços que exigem histórico médico
    servicos_quimicos = ["coloracao", "descoloracao", "alisamento", "permanente", "hidratacao_quimica"]
    
    # Verifica se algum serviço é químico
    requer_historico = any(
        servico.tipo.lower() in servicos_quimicos 
        for servico in servicos
    )
    
    if not requer_historico:
        return  # Não requer histórico médico
    
    # Busca histórico médico do cliente
    historico = db.get_medical_history_by_client(user_id)
    
    if not historico:
        servicos_afetados = [s.tipo for s in servicos if s.tipo.lower() in servicos_quimicos]
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "message": "Histórico médico obrigatório para este serviço",
                "redirect": "/medical/history",
                "servicos_afetados": servicos_afetados,
                "motivo": "Serviços químicos requerem avaliação de alergias e condições de saúde"
            }
        )
    
    # Verifica se histórico está atualizado (< 6 meses)
    data_historico = datetime.fromisoformat(historico.get("data_atualizacao", historico.get("created_at", "")))
    if datetime.now() - data_historico > timedelta(days=180):
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "message": "Histórico médico desatualizado",
                "redirect": "/medical/history",
                "ultima_atualizacao": historico.get("data_atualizacao"),
                "motivo": "Por segurança, atualize seu histórico médico a cada 6 meses"
            }
        )


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
    - Validação de histórico médico para serviços químicos
    """
    
    # Validação de histórico médico (se necessário)
    _verificar_historico_medico_obrigatorio(new_appointment.servicos, current_user.id)
    
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
    appointment_data = new_appointment.model_dump()
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


# =============================================================
# LISTAR AGENDAMENTOS
# =============================================================

@router.get("/my", response_model=List[Appointment])
async def get_my_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: Optional[str] = Query(None, alias="status")
):
    """Lista agendamentos do usuário logado"""
    appointments = db.get_user_appointments(current_user.id)
    
    if status_filter:
        appointments = [a for a in appointments if a.get("status") == status_filter]
    
    return [Appointment(**a) for a in appointments]


@router.get("/professional", response_model=List[Appointment])
async def get_professional_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    data: Optional[str] = Query(None, description="Data no formato YYYY-MM-DD"),
    status_filter: Optional[str] = Query(None, alias="status")
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
    
    if status_filter:
        appointments = [a for a in appointments if a.get("status") == status_filter]
    
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
# CONFIRMAR/ATUALIZAR STATUS
# =============================================================

@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    new_status: AppointmentStatus,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Atualiza status do agendamento.
    - Profissionais podem confirmar/cancelar seus agendamentos.
    - Clientes podem cancelar seus próprios agendamentos.
    """
    # Busca agendamento
    appointment = db.get_appointment_by_id(appointment_id)
    
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
    if is_client and new_status not in [AppointmentStatus.CANCELADO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clientes só podem cancelar agendamentos"
        )
    
    # Atualiza status
    updated = db.update_appointment_status(
        appointment_id,
        new_status.value,
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


# =============================================================
# CANCELAR AGENDAMENTO
# =============================================================

@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    motivo: Optional[str] = None
):
    """
    Cancela um agendamento.
    """
    # Busca agendamento
    appointment = db.get_appointment_by_id(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Verifica permissões
    is_owner = appointment["cliente_id"] == current_user.id
    is_professional = current_user.role == "profissional"
    is_admin = current_user.role == "admin"
    
    if not (is_owner or is_professional or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para cancelar este agendamento"
        )
    
    # Não permitir cancelamento de agendamentos concluídos
    if appointment["status"] == "concluido":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar agendamentos já concluídos"
        )
    
    # Atualiza status
    update_data = {
        "status": "cancelado",
        "cancelado_em": datetime.now().isoformat(),
        "cancelado_por": current_user.id,
        "motivo_cancelamento": motivo or "Não informado"
    }
    
    db.update_appointment(appointment_id, update_data)
    
    return {
        "message": "Agendamento cancelado com sucesso",
        "appointment_id": appointment_id,
        "status": "cancelado"
    }
