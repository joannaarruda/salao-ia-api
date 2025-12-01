"""
ROUTES/ATTENDANCE.PY - FICHAS DE ATENDIMENTO
============================================
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from typing import Annotated, List
import os
import uuid

from app.auth import get_current_user
from app.models import (
    User, AttendanceRecordCreate, AttendanceRecordResponse,
    StrandTestCreate, StrandTestResponse
)
from app.database import db

router = APIRouter()

UPLOAD_DIR = "static/attendance"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =============================================================
# FICHAS DE ATENDIMENTO
# =============================================================

@router.post("/records", response_model=AttendanceRecordResponse)
async def create_attendance_record(
    record: AttendanceRecordCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Cria ficha de atendimento (profissional)"""
    
    if current_user.role != "profissional":
        raise HTTPException(
            status_code=403,
            detail="Apenas profissionais podem criar fichas de atendimento"
        )
    
    # Verifica se o agendamento existe e pertence ao profissional
    appointments = db.get_all_appointments()
    appointment = next((a for a in appointments if a["id"] == record.appointment_id), None)
    
    if not appointment or appointment["profissional_id"] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Agendamento inválido ou não pertence a você"
        )
    
    record_data = record.model_dump()
    record_data["profissional_id"] = current_user.id
    
    created = db.create_attendance_record(record_data)
    
    # Atualiza status do agendamento para concluído
    db.update_appointment_status(record.appointment_id, "concluido", current_user.id)
    
    return AttendanceRecordResponse(**created)


@router.get("/records/client/{cliente_id}")
async def get_client_attendance_records(
    cliente_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Lista fichas de atendimento do cliente"""
    
    if current_user.role not in ["profissional", "admin"] and current_user.id != cliente_id:
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para ver fichas de outros clientes"
        )
    
    records = db.get_attendance_records_by_client(cliente_id)
    
    return [AttendanceRecordResponse(**r) for r in records]


@router.get("/records/my")
async def get_my_attendance_records(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Lista minhas fichas de atendimento"""
    
    records = db.get_attendance_records_by_client(current_user.id)
    
    return [AttendanceRecordResponse(**r) for r in records]


@router.patch("/records/{record_id}")
async def update_attendance_record(
    record_id: str,
    update_data: dict,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Atualiza ficha de atendimento (adicionar feedback do cliente)"""
    
    records = db.get_attendance_records_by_client(current_user.id)
    record = next((r for r in records if r["id"] == record_id), None)
    
    if not record:
        raise HTTPException(
            status_code=404,
            detail="Ficha não encontrada"
        )
    
    # Cliente pode adicionar feedback
    if current_user.id == record["cliente_id"]:
        allowed_fields = ["feedback"]
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        if not filtered_data:
            raise HTTPException(
                status_code=400,
                detail="Cliente só pode atualizar feedback"
            )
        update_data = filtered_data
    # Profissional pode atualizar tudo
    elif current_user.role != "profissional" or record["profissional_id"] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para atualizar esta ficha"
        )
    
    updated = db.update_attendance_record(record_id, update_data)
    
    return AttendanceRecordResponse(**updated)


# =============================================================
# UPLOAD DE FOTOS
# =============================================================

@router.post("/records/{record_id}/photos")
async def upload_attendance_photos(
    record_id: str,
    tipo: str,  # "antes" ou "depois"
    current_user: Annotated[User, Depends(get_current_user)],
    files: List[UploadFile] = File(...)
):
    """
    Upload de fotos do atendimento (profissional)
    
    Args:
        record_id: ID da ficha de atendimento
        tipo: "antes" ou "depois"
        files: Lista de arquivos para upload
    """
    
    if current_user.role != "profissional":
        raise HTTPException(
            status_code=403,
            detail="Apenas profissionais podem fazer upload de fotos"
        )
    
    # Busca ficha
    records = db._read_file("attendance_records")
    record = next((r for r in records if r["id"] == record_id), None)
    
    if not record or record["profissional_id"] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Sem permissão para esta ficha"
        )
    
    # Salva fotos
    photo_urls = []
    for file in files:
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(await file.read())
        
        photo_urls.append(f"/{UPLOAD_DIR}/{filename}")
    
    # Atualiza ficha
    if "procedimento" not in record:
        record["procedimento"] = {"fotos_antes": [], "fotos_depois": []}
    
    if tipo == "antes":
        if "fotos_antes" not in record["procedimento"]:
            record["procedimento"]["fotos_antes"] = []
        record["procedimento"]["fotos_antes"].extend(photo_urls)
    else:
        if "fotos_depois" not in record["procedimento"]:
            record["procedimento"]["fotos_depois"] = []
        record["procedimento"]["fotos_depois"].extend(photo_urls)
    
    db.update_attendance_record(record_id, record)
    
    return {"message": "Fotos enviadas com sucesso", "urls": photo_urls}


# =============================================================
# TESTES DE MECHA
# =============================================================

@router.post("/strand-tests", response_model=StrandTestResponse)
async def create_strand_test(
    test: StrandTestCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Registra teste de mecha (profissional)"""
    
    if current_user.role != "profissional":
        raise HTTPException(
            status_code=403,
            detail="Apenas profissionais podem registrar testes de mecha"
        )
    
    test_data = test.model_dump()
    test_data["profissional_id"] = current_user.id
    
    created = db.create_strand_test(test_data)
    
    return StrandTestResponse(**created)


@router.get("/strand-tests/client/{cliente_id}")
async def get_client_strand_tests(
    cliente_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Lista testes de mecha do cliente"""
    
    if current_user.role not in ["profissional", "admin"] and current_user.id != cliente_id:
        raise HTTPException(
            status_code=403,
            detail="Sem permissão"
        )
    
    tests = db.get_strand_tests_by_client(cliente_id)
    
    return [StrandTestResponse(**t) for t in tests]


@router.get("/strand-tests/my")
async def get_my_strand_tests(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Lista meus testes de mecha"""
    
    tests = db.get_strand_tests_by_client(current_user.id)
    
    return [StrandTestResponse(**t) for t in tests]
