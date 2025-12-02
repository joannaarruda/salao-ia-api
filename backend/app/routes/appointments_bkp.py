# app/routes/appointments.py - ADICIONAR ESTAS ROTAS

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/appointments", tags=["appointments"])

# ==================== MODELS ====================

class ServiceItem(BaseModel):
    id: str
    name: str
    duration: int
    price: float
    requiresTest: bool = False

class MedicalQuestionnaire(BaseModel):
    q1: str
    q1_details: Optional[str] = ""
    q2: str
    q3: str
    q3_details: Optional[str] = ""
    q4: str
    q5: str
    observations: Optional[str] = ""
    timestamp: str

class PrepareAppointmentRequest(BaseModel):
    services: List[ServiceItem]
    medical_questionnaire: Optional[MedicalQuestionnaire] = None
    analysis_data: Optional[dict] = None
    total_price: float
    total_duration: int
    created_at: str

class ScheduleAppointmentRequest(BaseModel):
    booking_code: str
    appointment_date: str  # ISO format: 2025-12-15
    appointment_time: str  # Format: 14:30
    professional_id: Optional[str] = None
    notes: Optional[str] = ""

# ==================== IN-MEMORY STORAGE (substitua por banco de dados real) ====================

pending_bookings = {}  # {booking_code: booking_data}
scheduled_appointments = {}  # {appointment_id: appointment_data}

# ==================== ENDPOINTS ====================

@router.post("/prepare")
async def prepare_appointment(data: PrepareAppointmentRequest):
    """
    Prepara um agendamento, salvando os serviços e questionário médico.
    Retorna um código de agendamento único.
    """
    try:
        # Gerar código único
        booking_code = f"BOOK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Verificar se requer teste
        requires_test = any(s.requiresTest for s in data.services)
        
        # Salvar dados
        booking_data = {
            "booking_code": booking_code,
            "services": [s.dict() for s in data.services],
            "medical_questionnaire": data.medical_questionnaire.dict() if data.medical_questionnaire else None,
            "analysis_data": data.analysis_data,
            "total_price": data.total_price,
            "total_duration": data.total_duration,
            "requires_test": requires_test,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        pending_bookings[booking_code] = booking_data
        
        return {
            "booking_code": booking_code,
            "status": "pending",
            "requires_test": requires_test,
            "message": "Agendamento preparado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao preparar agendamento: {str(e)}"
        )

@router.get("/booking/{booking_code}")
async def get_booking(booking_code: str):
    """
    Retorna os dados de um booking pelo código.
    """
    if booking_code not in pending_bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    return pending_bookings[booking_code]

@router.post("/schedule")
async def schedule_appointment(data: ScheduleAppointmentRequest):
    """
    Agenda uma data e hora para um booking preparado.
    """
    try:
        # Verificar se booking existe
        if data.booking_code not in pending_bookings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agendamento não encontrado"
            )
        
        booking = pending_bookings[data.booking_code]
        
        # Validar data (não pode ser no passado)
        appointment_datetime = datetime.fromisoformat(f"{data.appointment_date}T{data.appointment_time}")
        if appointment_datetime < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data e hora não podem estar no passado"
            )
        
        # Gerar ID do agendamento
        appointment_id = f"APT-{uuid.uuid4().hex[:12].upper()}"
        
        # Criar agendamento
        appointment = {
            "appointment_id": appointment_id,
            "booking_code": data.booking_code,
            "appointment_date": data.appointment_date,
            "appointment_time": data.appointment_time,
            "appointment_datetime": appointment_datetime.isoformat(),
            "professional_id": data.professional_id,
            "notes": data.notes,
            "services": booking["services"],
            "medical_questionnaire": booking["medical_questionnaire"],
            "total_price": booking["total_price"],
            "total_duration": booking["total_duration"],
            "requires_test": booking["requires_test"],
            "status": "scheduled",
            "created_at": booking["created_at"],
            "scheduled_at": datetime.now().isoformat()
        }
        
        # Salvar agendamento
        scheduled_appointments[appointment_id] = appointment
        
        # Atualizar status do booking
        booking["status"] = "scheduled"
        booking["appointment_id"] = appointment_id
        
        return {
            "appointment_id": appointment_id,
            "status": "scheduled",
            "appointment_datetime": appointment_datetime.isoformat(),
            "message": "Agendamento confirmado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao agendar: {str(e)}"
        )

@router.get("/list")
async def list_appointments(
    status: Optional[str] = None,
    limit: int = 10
):
    """
    Lista agendamentos.
    """
    appointments = list(scheduled_appointments.values())
    
    # Filtrar por status se fornecido
    if status:
        appointments = [a for a in appointments if a["status"] == status]
    
    # Ordenar por data (mais recentes primeiro)
    appointments.sort(key=lambda x: x["appointment_datetime"], reverse=True)
    
    # Limitar resultados
    appointments = appointments[:limit]
    
    return {
        "appointments": appointments,
        "total": len(appointments)
    }

@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str):
    """
    Retorna detalhes de um agendamento.
    """
    if appointment_id not in scheduled_appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    return scheduled_appointments[appointment_id]

@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: str):
    """
    Cancela um agendamento.
    """
    if appointment_id not in scheduled_appointments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    appointment = scheduled_appointments[appointment_id]
    appointment["status"] = "cancelled"
    appointment["cancelled_at"] = datetime.now().isoformat()
    
    return {
        "message": "Agendamento cancelado com sucesso",
        "appointment_id": appointment_id
    }

@router.get("/available-slots/{date}")
async def get_available_slots(date: str):
    """
    Retorna horários disponíveis para uma data específica.
    """
    try:
        target_date = datetime.fromisoformat(date).date()
        
        # Horários de funcionamento: 9h às 18h
        # Intervalos de 30 minutos
        all_slots = []
        current_time = datetime.combine(target_date, datetime.min.time()).replace(hour=9)
        end_time = datetime.combine(target_date, datetime.min.time()).replace(hour=18)
        
        while current_time < end_time:
            all_slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)
        
        # Verificar slots ocupados
        occupied_slots = []
        for apt in scheduled_appointments.values():
            if apt["appointment_date"] == date and apt["status"] == "scheduled":
                occupied_slots.append(apt["appointment_time"])
        
        # Filtrar slots disponíveis
        available_slots = [slot for slot in all_slots if slot not in occupied_slots]
        
        return {
            "date": date,
            "available_slots": available_slots,
            "occupied_slots": occupied_slots
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )