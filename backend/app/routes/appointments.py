# app/routes/appointments.py - VERSÃO MÍNIMA PARA TESTE

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import sys
from pathlib import Path

# Adicionar caminho da app para imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from databricks_export import DatabricksExporter

# ✅ SEM prefix e tags (definidos no main.py)
router = APIRouter()

# Inicializar exportador
exporter = DatabricksExporter(export_dir="exports/databricks")

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
    analysis_data: Optional[Dict[str, Any]] = None
    total_price: float
    total_duration: int
    created_at: str

class ScheduleAppointmentRequest(BaseModel):
    booking_code: str
    appointment_date: str  # ISO format: 2025-12-15
    appointment_time: str  # Format: 14:30
    professional_id: Optional[str] = None
    notes: Optional[str] = ""

# ==================== STORAGE ====================

pending_bookings = {}
scheduled_appointments = {}

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
        
        print(f"✅ Agendamento preparado: {booking_code}")
        
        return {
            "booking_code": booking_code,
            "status": "pending",
            "requires_test": requires_test,
            "message": "Agendamento preparado com sucesso"
        }
        
    except Exception as e:
        print(f"❌ Erro ao preparar agendamento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao preparar agendamento: {str(e)}"
        )

@router.get("/list")
async def list_appointments():
    """
    Lista agendamentos.
    """
    appointments = list(scheduled_appointments.values())
    
    return {
        "appointments": appointments,
        "total": len(appointments)
    }

@router.get("/health")
async def appointments_health():
    """
    Health check dos appointments.
    """
    return {
        "status": "ok",
        "pending_bookings": len(pending_bookings),
        "scheduled_appointments": len(scheduled_appointments)
    }

@router.post("/schedule")
async def schedule_appointment(data: ScheduleAppointmentRequest):
    """
    Agenda uma data e hora para um booking preparado.
    """
    try:
        # Gerar ID do agendamento
        appointment_id = f"APT-{uuid.uuid4().hex[:12].upper()}"
        
        # Validar data (não pode ser no passado)
        appointment_datetime = datetime.fromisoformat(f"{data.appointment_date}T{data.appointment_time}")
        if appointment_datetime < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data e hora não podem estar no passado"
            )
        
        # Buscar booking se existir
        booking = pending_bookings.get(data.booking_code, {})
        
        # Criar agendamento
        appointment = {
            "appointment_id": appointment_id,
            "booking_code": data.booking_code,
            "appointment_date": data.appointment_date,
            "appointment_time": data.appointment_time,
            "appointment_datetime": appointment_datetime.isoformat(),
            "professional_id": data.professional_id,
            "notes": data.notes,
            "services": booking.get("services", []),
            "medical_questionnaire": booking.get("medical_questionnaire"),
            "total_price": booking.get("total_price", 0),
            "total_duration": booking.get("total_duration", 0),
            "requires_test": booking.get("requires_test", False),
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "scheduled_at": datetime.now().isoformat()
        }
        
        # Salvar agendamento
        scheduled_appointments[appointment_id] = appointment
        
        # Atualizar status do booking
        if data.booking_code in pending_bookings:
            pending_bookings[data.booking_code]["status"] = "scheduled"
            pending_bookings[data.booking_code]["appointment_id"] = appointment_id
        
        # ✅ EXPORTAR PARA DATABRICKS
        try:
            export_path = exporter.export_appointments(
                [appointment],
                compress=True
            )
            print(f"✅ Agendamento exportado para Databricks: {export_path}")
        except Exception as e:
            print(f"⚠️ Aviso ao exportar para Databricks: {e}")
        
        print(f"✅ Agendamento confirmado: {appointment_id} para {data.appointment_date} às {data.appointment_time}")
        
        return {
            "appointment_id": appointment_id,
            "status": "scheduled",
            "appointment_datetime": appointment_datetime.isoformat(),
            "message": "Agendamento confirmado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao agendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao agendar: {str(e)}"
        )

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
    
    print(f"✅ Agendamento cancelado: {appointment_id}")
    
    return {
        "message": "Agendamento cancelado com sucesso",
        "appointment_id": appointment_id
    }

@router.post("/professional/create")
async def create_appointment_as_professional(data: Dict[str, Any]):
    """
    Permite que um profissional crie agendamento para um cliente.
    
    Esperado:
    {
        "client_name": "Nome do Cliente",
        "client_email": "email@example.com",
        "client_phone": "912345678",
        "appointment_date": "2025-12-15",
        "appointment_time": "14:30",
        "professional_id": "prof-123",
        "professional_name": "Nome do Profissional",
        "services": [{"id": "...", "name": "...", "price": 25, "duration": 60}],
        "notes": "Observações opcionais"
    }
    """
    try:
        # Gerar IDs únicos
        appointment_id = f"APT-{uuid.uuid4().hex[:12].upper()}"
        booking_code = f"BOOK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Validar data
        appointment_datetime = datetime.fromisoformat(f"{data.get('appointment_date')}T{data.get('appointment_time')}")
        if appointment_datetime < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data e hora não podem estar no passado"
            )
        
        # Criar agendamento
        appointment = {
            "appointment_id": appointment_id,
            "booking_code": booking_code,
            "appointment_date": data.get("appointment_date"),
            "appointment_time": data.get("appointment_time"),
            "appointment_datetime": appointment_datetime.isoformat(),
            "professional_id": data.get("professional_id"),
            "professional_name": data.get("professional_name"),
            "client_name": data.get("client_name"),
            "client_email": data.get("client_email"),
            "client_phone": data.get("client_phone"),
            "notes": data.get("notes", ""),
            "services": data.get("services", []),
            "total_price": sum(s.get("price", 0) for s in data.get("services", [])),
            "total_duration": sum(s.get("duration", 0) for s in data.get("services", [])),
            "status": "scheduled",
            "created_by": "professional",
            "created_at": datetime.now().isoformat(),
            "scheduled_at": datetime.now().isoformat()
        }
        
        # Salvar agendamento
        scheduled_appointments[appointment_id] = appointment
        
        # ✅ EXPORTAR PARA DATABRICKS
        try:
            export_path = exporter.export_appointments(
                [appointment],
                compress=True
            )
            print(f"✅ Agendamento criado por profissional exportado para Databricks: {export_path}")
        except Exception as e:
            print(f"⚠️ Aviso ao exportar para Databricks: {e}")
        
        print(f"✅ Agendamento criado por profissional: {appointment_id} para {data.get('appointment_date')} às {data.get('appointment_time')}")
        
        return {
            "appointment_id": appointment_id,
            "booking_code": booking_code,
            "status": "scheduled",
            "appointment_datetime": appointment_datetime.isoformat(),
            "message": "Agendamento criado com sucesso pelo profissional"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao criar agendamento como profissional: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar agendamento: {str(e)}"
        )

@router.post("/export-completed")
async def export_completed_appointment(data: Dict[str, Any]):
    """
    Exporta agendamento concluído para Databricks.
    Pode ser chamado diretamente após conclusão do atendimento.
    
    Dados esperados:
    {
        "booking_code": "...",
        "status": "completed",
        "completed_at": "...",
        "strand_test_result": {  // opcional
            "result": "positivo|negativo|adiado",
            "observations": "...",
            "tested_at": "..."
        }
    }
    """
    try:
        # ✅ EXPORTAR PARA DATABRICKS
        export_path = exporter.export_appointments(
            [data],
            compress=True
        )
        print(f"✅ Agendamento concluído exportado para Databricks: {export_path}")
        
        return {
            "status": "exported",
            "export_path": export_path,
            "message": "Agendamento concluído exportado com sucesso"
        }
        
    except Exception as e:
        print(f"⚠️ Aviso ao exportar para Databricks: {e}")
        # Não interromper o fluxo se a exportação falhar
        return {
            "status": "warning",
            "message": f"Agendamento concluído mas exportação teve aviso: {str(e)}"
        }