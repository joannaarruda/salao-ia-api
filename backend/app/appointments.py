# app/routes/appointments.py - INTEGRADO COM SISTEMA DE ARQUIVOS

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import json
import os
from pathlib import Path

router = APIRouter()

# ==================== CONFIGURAÇÃO ====================

# Diretórios
DATA_DIR = Path("data")
EXPORTS_DIR = Path("exports/databricks")
APPOINTMENTS_FILE = DATA_DIR / "appointments.json"

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

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
    appointment_date: str
    appointment_time: str
    professional_id: Optional[str] = None
    notes: Optional[str] = ""

# ==================== FUNÇÕES AUXILIARES ====================

def load_appointments():
    """Carrega agendamentos do arquivo JSON"""
    if not APPOINTMENTS_FILE.exists():
        return []
    
    try:
        with open(APPOINTMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Erro ao carregar appointments.json: {e}")
        return []

def save_appointments(appointments):
    """Salva agendamentos no arquivo JSON"""
    try:
        with open(APPOINTMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(appointments, f, indent=2, ensure_ascii=False)
        print(f"✅ Salvo em: {APPOINTMENTS_FILE}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar appointments.json: {e}")
        return False

def export_to_databricks(appointment):
    """Exporta agendamento para pasta databricks"""
    try:
        # Criar nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"appointment_{appointment['id']}_{timestamp}.json"
        filepath = EXPORTS_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(appointment, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exportado para databricks: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Erro ao exportar para databricks: {e}")
        return False

def get_user_id_from_token(token: str = None):
    """
    Extrai user_id do token JWT
    Por enquanto retorna um ID fixo, mas você pode implementar a lógica real
    """
    # TODO: Implementar extração real do token
    return "5aaa0775-8d44-4d89-a789-59553210a0a9"

# ==================== STORAGE TEMPORÁRIO ====================

pending_bookings = {}

# ==================== ENDPOINTS ====================

@router.post("/prepare")
async def prepare_appointment(data: PrepareAppointmentRequest):
    """
    Prepara um agendamento, salvando os serviços e questionário médico.
    """
    try:
        booking_code = f"BOOK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        requires_test = any(s.requiresTest for s in data.services)
        
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

@router.post("/schedule")
async def schedule_appointment(data: ScheduleAppointmentRequest):
    """
    Agenda uma data e hora, salvando no arquivo JSON e exportando.
    """
    try:
        # Validar data
        appointment_datetime = datetime.fromisoformat(f"{data.appointment_date}T{data.appointment_time}")
        if appointment_datetime < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data e hora não podem estar no passado"
            )
        
        # Buscar booking preparado
        booking = pending_bookings.get(data.booking_code, {})
        
        # Gerar ID único
        appointment_id = str(uuid.uuid4())
        
        # Obter user_id (você pode passar no token)
        user_id = get_user_id_from_token()
        
        # Criar agendamento no formato do seu sistema
        new_appointment = {
            "id": appointment_id,
            "usuario_id": user_id,
            "profissional_id": data.professional_id or "1",  # ID do profissional (default: 1)
            "servico": ", ".join([s["name"] for s in booking.get("services", [])]),
            "data_hora": appointment_datetime.isoformat(),
            "status": "agendado",
            "created_at": datetime.now().isoformat(),
            # Dados adicionais
            "booking_code": data.booking_code,
            "services_details": booking.get("services", []),
            "total_price": booking.get("total_price", 0),
            "total_duration": booking.get("total_duration", 0),
            "medical_questionnaire": booking.get("medical_questionnaire"),
            "notes": data.notes,
            "requires_test": booking.get("requires_test", False)
        }
        
        # Carregar agendamentos existentes
        appointments = load_appointments()
        
        # Adicionar novo agendamento
        appointments.append(new_appointment)
        
        # Salvar no arquivo JSON principal
        if not save_appointments(appointments):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar agendamento"
            )
        
        # Exportar para databricks
        export_to_databricks(new_appointment)
        
        # Atualizar booking
        if data.booking_code in pending_bookings:
            pending_bookings[data.booking_code]["status"] = "scheduled"
            pending_bookings[data.booking_code]["appointment_id"] = appointment_id
        
        print(f"✅ Agendamento salvo: {appointment_id}")
        print(f"   Data: {data.appointment_date} às {data.appointment_time}")
        print(f"   Profissional: {data.professional_id or '1'}")
        print(f"   Serviço: {new_appointment['servico']}")
        
        return {
            "appointment_id": appointment_id,
            "status": "agendado",
            "appointment_datetime": appointment_datetime.isoformat(),
            "message": "Agendamento confirmado e salvo com sucesso",
            "saved_to_file": True,
            "exported_to_databricks": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao agendar: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao agendar: {str(e)}"
        )

@router.get("/list")
async def list_appointments(usuario_id: Optional[str] = None):
    """
    Lista agendamentos do arquivo JSON.
    Se usuario_id for fornecido, filtra por usuário.
    """
    try:
        appointments = load_appointments()
        
        # Filtrar por usuário se fornecido
        if usuario_id:
            appointments = [apt for apt in appointments if apt.get("usuario_id") == usuario_id]
        
        # Ordenar por data (mais recente primeiro)
        appointments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "appointments": appointments,
            "total": len(appointments)
        }
        
    except Exception as e:
        print(f"❌ Erro ao listar agendamentos: {e}")
        return {
            "appointments": [],
            "total": 0
        }

@router.get("/available-slots/{date}")
async def get_available_slots(date: str):
    """
    Retorna horários disponíveis para uma data específica.
    """
    try:
        target_date = datetime.fromisoformat(date).date()
        
        # Horários de funcionamento: 9h às 18h, intervalos de 30min
        all_slots = []
        current_time = datetime.combine(target_date, datetime.min.time()).replace(hour=9)
        end_time = datetime.combine(target_date, datetime.min.time()).replace(hour=18)
        
        while current_time < end_time:
            all_slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)
        
        # Carregar agendamentos
        appointments = load_appointments()
        
        # Verificar slots ocupados nesta data
        occupied_slots = []
        for apt in appointments:
            try:
                apt_datetime = datetime.fromisoformat(apt["data_hora"])
                if apt_datetime.date() == target_date and apt["status"] == "agendado":
                    occupied_slots.append(apt_datetime.strftime("%H:%M"))
            except:
                continue
        
        # Filtrar disponíveis
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
    Cancela um agendamento no arquivo JSON.
    """
    try:
        appointments = load_appointments()
        
        # Encontrar agendamento
        found = False
        for apt in appointments:
            if apt["id"] == appointment_id:
                apt["status"] = "cancelado"
                apt["cancelled_at"] = datetime.now().isoformat()
                found = True
                break
        
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agendamento não encontrado"
            )
        
        # Salvar
        save_appointments(appointments)
        
        print(f"✅ Agendamento cancelado: {appointment_id}")
        
        return {
            "message": "Agendamento cancelado com sucesso",
            "appointment_id": appointment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao cancelar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cancelar: {str(e)}"
        )

@router.get("/health")
async def appointments_health():
    """
    Health check com estatísticas.
    """
    appointments = load_appointments()
    
    total = len(appointments)
    agendados = len([a for a in appointments if a.get("status") == "agendado"])
    cancelados = len([a for a in appointments if a.get("status") == "cancelado"])
    
    return {
        "status": "ok",
        "total_appointments": total,
        "agendados": agendados,
        "cancelados": cancelados,
        "pending_bookings": len(pending_bookings),
        "files": {
            "appointments_json": str(APPOINTMENTS_FILE),
            "exists": APPOINTMENTS_FILE.exists(),
            "exports_dir": str(EXPORTS_DIR),
            "exports_count": len(list(EXPORTS_DIR.glob("*.json"))) if EXPORTS_DIR.exists() else 0
        }
    }

@router.get("/export-all")
async def export_all_to_databricks():
    """
    Exporta todos os agendamentos para databricks.
    """
    try:
        appointments = load_appointments()
        exported = 0
        
        for apt in appointments:
            if export_to_databricks(apt):
                exported += 1
        
        return {
            "message": f"Exportados {exported} de {len(appointments)} agendamentos",
            "exported": exported,
            "total": len(appointments)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao exportar: {str(e)}"
        )