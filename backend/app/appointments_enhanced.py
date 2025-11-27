"""
APPOINTMENTS.PY - ROTAS DE AGENDAMENTO COM GOOGLE CALENDAR E I18N
==================================================================
Versão atualizada com integração do Google Calendar e suporte a idiomas
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Header
from typing import Annotated, List, Optional
from datetime import datetime, timedelta

from app.auth import get_current_user
from app.models import (
    User, Appointment, AppointmentCreate, AppointmentStatus,
    TimeSlot, AvailabilityResponse, ProfessionalSchedule
)
from app.database import db
from app.google_calendar import (
    GoogleCalendarIntegration,
    sync_appointment_to_calendar,
    update_appointment_in_calendar,
    cancel_appointment_in_calendar
)
from app.i18n import Language, get_translation, translator

router = APIRouter()

# Inicializa integração com Google Calendar
calendar_integration = GoogleCalendarIntegration()

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_language_from_header(accept_language: Optional[str] = Header(None)) -> Language:
    """
    Extrai o idioma preferido do header Accept-Language
    
    Args:
        accept_language: Header HTTP Accept-Language
    
    Returns:
        Idioma detectado
    """
    if not accept_language:
        return Language.PT
    
    # Parse do header (ex: "pt-PT,pt;q=0.9,en;q=0.8")
    langs = accept_language.lower().split(',')
    
    for lang in langs:
        lang_code = lang.split(';')[0].strip()[:2]
        
        if lang_code == 'pt':
            return Language.PT
        elif lang_code == 'en':
            return Language.EN
        elif lang_code == 'it':
            return Language.IT
        elif lang_code == 'es':
            return Language.ES
    
    return Language.PT


def _check_time_conflicts(profissional_id: str, data_hora: datetime, duracao: int) -> Optional[str]:
    """Verifica conflitos de horário"""
    data_str = data_hora.date().isoformat()
    agendamentos = db.get_professional_appointments(profissional_id, data_str)
    
    fim_novo = data_hora + timedelta(minutes=duracao)
    
    for apt in agendamentos:
        if apt.get("status") in ["cancelado"]:
            continue
        
        apt_inicio = datetime.fromisoformat(apt["data_hora"])
        apt_duracao = sum(s.get("duracao_estimada", 60) for s in apt.get("servicos", []))
        apt_fim = apt_inicio + timedelta(minutes=apt_duracao)
        
        if not (fim_novo <= apt_inicio or data_hora >= apt_fim):
            return f"{apt_inicio.strftime('%H:%M')} - {apt_fim.strftime('%H:%M')}"
    
    return None


# ============================================================
# CRIAR AGENDAMENTO COM GOOGLE CALENDAR
# ============================================================

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Appointment)
async def create_appointment(
    new_appointment: AppointmentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    accept_language: Optional[str] = Header(None),
    sync_calendar: bool = Query(True, description="Sincronizar com Google Calendar")
):
    """
    Cria novo agendamento com opção de sincronizar com Google Calendar
    
    Funcionalidades:
    - Suporta múltiplos serviços
    - Opção de usar IA ou não
    - Sincronização automática com Google Calendar
    - Suporte a múltiplos idiomas
    """
    
    # Define idioma
    language = get_language_from_header(accept_language)
    translator.set_language(language)
    
    # Validação de data/hora
    try:
        agendamento_dt = datetime.fromisoformat(new_appointment.data_hora)
        if agendamento_dt < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.get("error_past_datetime")
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translator.get("error_invalid_datetime")
        )
    
    # Calcula duração total
    duracao_total = sum(servico.duracao_estimada for servico in new_appointment.servicos)
    
    # Verifica conflitos
    conflitos = _check_time_conflicts(
        new_appointment.profissional_id,
        agendamento_dt,
        duracao_total
    )
    
    if conflitos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{translator.get('error_time_conflict')} {conflitos}"
        )
    
    # Cria agendamento
    appointment_data = new_appointment.dict()
    appointment_data["cliente_id"] = current_user.id
    appointment_data["status"] = "pendente"
    
    created_appointment = db.create_appointment(appointment_data)
    
    # Sincroniza com Google Calendar se solicitado
    google_calendar_event_id = None
    if sync_calendar:
        try:
            # Busca dados do profissional e cliente
            professional = db.get_professional_by_id(new_appointment.profissional_id)
            
            if professional and current_user.email:
                google_calendar_event_id = sync_appointment_to_calendar(
                    appointment=created_appointment,
                    professional_name=professional['nome'],
                    client_name=current_user.nome,
                    client_email=current_user.email,
                    calendar_integration=calendar_integration
                )
                
                if google_calendar_event_id:
                    # Atualiza agendamento com ID do evento do Google
                    created_appointment["google_calendar_event_id"] = google_calendar_event_id
                    db._write_file("appointments", db.get_all_appointments())
                    print(f"✅ Agendamento sincronizado com Google Calendar: {google_calendar_event_id}")
        except Exception as e:
            print(f"⚠️ Erro ao sincronizar com Google Calendar: {e}")
            # Não falha o agendamento se a sincronização falhar
    
    # Cria consulta se solicitada
    if new_appointment.requer_consulta:
        consulta_data = {
            "cliente_id": current_user.id,
            "profissional_id": new_appointment.profissional_id,
            "agendamento_id": created_appointment["id"],
            "objetivo": f"{translator.get('consultation')} - {', '.join([s.tipo for s in new_appointment.servicos])}",
            "estado_atual_cabelo": "",
            "desejos_cliente": new_appointment.observacoes or "",
            "requer_teste_mecha": new_appointment.requer_teste_mecha
        }
        db.create_consultation(consulta_data)
    
    return Appointment(**created_appointment)


# ============================================================
# ATUALIZAR STATUS COM GOOGLE CALENDAR
# ============================================================

@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    new_status: AppointmentStatus,
    current_user: Annotated[User, Depends(get_current_user)],
    accept_language: Optional[str] = Header(None),
    update_calendar: bool = Query(True, description="Atualizar Google Calendar")
):
    """
    Atualiza status do agendamento e sincroniza com Google Calendar
    """
    # Define idioma
    language = get_language_from_header(accept_language)
    translator.set_language(language)
    
    # Busca agendamento
    appointments = db.get_all_appointments()
    appointment = next((a for a in appointments if a["id"] == appointment_id), None)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=translator.get("error_appointment_not_found")
        )
    
    # Verifica permissões
    is_professional = current_user.role == "profissional" and appointment["profissional_id"] == current_user.id
    is_client = current_user.role == "cliente" and appointment["cliente_id"] == current_user.id
    is_admin = current_user.role == "admin"
    
    if not (is_professional or is_client or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translator.get("error_no_permission")
        )
    
    # Clientes só podem cancelar
    if is_client and new_status not in ["cancelado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translator.get("error_client_can_only_cancel")
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
            detail=translator.get("error_update_failed")
        )
    
    # Atualiza Google Calendar
    if update_calendar and updated.get("google_calendar_event_id"):
        try:
            if new_status == "cancelado":
                # Cancela evento no Google Calendar
                cancel_appointment_in_calendar(
                    updated["google_calendar_event_id"],
                    calendar_integration
                )
                print(f"✅ Evento cancelado no Google Calendar")
            else:
                # Atualiza evento
                professional = db.get_professional_by_id(updated["profissional_id"])
                client = db.get_user_by_id(updated["cliente_id"])
                
                if professional and client:
                    update_appointment_in_calendar(
                        appointment=updated,
                        google_calendar_event_id=updated["google_calendar_event_id"],
                        professional_name=professional['nome'],
                        client_name=client['nome'],
                        calendar_integration=calendar_integration
                    )
                    print(f"✅ Evento atualizado no Google Calendar")
        except Exception as e:
            print(f"⚠️ Erro ao atualizar Google Calendar: {e}")
    
    return {
        "message": translator.get("success_status_updated"),
        "appointment": Appointment(**updated)
    }


# ============================================================
# LISTAR AGENDAMENTOS (COM TRADUÇÃO)
# ============================================================

@router.get("/my", response_model=List[Appointment])
async def get_my_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    status: Optional[AppointmentStatus] = None,
    accept_language: Optional[str] = Header(None)
):
    """Lista agendamentos do usuário logado"""
    language = get_language_from_header(accept_language)
    translator.set_language(language)
    
    appointments = db.get_user_appointments(current_user.id)
    
    if status:
        appointments = [a for a in appointments if a.get("status") == status]
    
    return [Appointment(**a) for a in appointments]


@router.get("/professional", response_model=List[Appointment])
async def get_professional_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    data: Optional[str] = Query(None, description="Data no formato YYYY-MM-DD"),
    status: Optional[AppointmentStatus] = None,
    accept_language: Optional[str] = Header(None)
):
    """Lista agendamentos do profissional"""
    language = get_language_from_header(accept_language)
    translator.set_language(language)
    
    if current_user.role not in ["profissional", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translator.get("error_only_professionals")
        )
    
    appointments = db.get_professional_appointments(current_user.id, data)
    
    if status:
        appointments = [a for a in appointments if a.get("status") == status]
    
    return [Appointment(**a) for a in appointments]


@router.get("/available", response_model=AvailabilityResponse)
async def get_available_times(
    profissional_id: str,
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
    duracao: int = Query(60, description="Duração em minutos"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    accept_language: Optional[str] = Header(None)
):
    """Retorna horários disponíveis"""
    language = get_language_from_header(accept_language)
    translator.set_language(language)
    
    try:
        data_obj = datetime.fromisoformat(data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translator.get("error_invalid_date")
        )
    
    horarios = []
    
    for hora in range(9, 19):
        for minuto in [0, 30]:
            horario = data_obj.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            horario_str = horario.isoformat()
            
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


# ============================================================
# ENDPOINT DE TRADUÇÃO
# ============================================================

@router.get("/translations")
async def get_translations(
    language: Language = Query(Language.PT, description="Idioma desejado")
):
    """
    Retorna todas as traduções para um idioma específico
    
    Use este endpoint no frontend para carregar traduções
    """
    return {
        "language": language,
        "translations": translator.get_all(language)
    }
