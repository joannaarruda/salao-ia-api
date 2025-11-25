from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import AppointmentCreate, Appointment
from app.database import db

router = APIRouter()

@router.post("/", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment."""
    existing_appointments = db.get_appointments_by_datetime(
        appointment.data_hora.isoformat(),
        appointment.profissional_id
    )
    
    if existing_appointments:
        raise HTTPException(
            status_code=400,
            detail="Appointment time is already booked."
        )
    
    new_appointment = db.create_appointment(appointment.dict())
    return new_appointment

@router.get("/", response_model=List[Appointment])
async def get_appointments(user_id: str):
    """Get all appointments for a user."""
    appointments = db.get_user_appointments(user_id)
    return appointments