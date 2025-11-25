from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict

def validate_email(email: str) -> EmailStr:
    """Validar formato de email"""
    return EmailStr.validate(email)

def validate_user_data(user_data: Dict[str, Any]) -> None:
    """Validar dados do usuário"""
    if len(user_data.get("nome", "")) < 3:
        raise ValueError("O nome deve ter pelo menos 3 caracteres.")
    if not validate_email(user_data.get("email", "")):
        raise ValueError("Email inválido.")
    if len(user_data.get("senha", "")) < 6:
        raise ValueError("A senha deve ter pelo menos 6 caracteres.")

def validate_appointment_data(appointment_data: Dict[str, Any]) -> None:
    """Validar dados do agendamento"""
    if not isinstance(appointment_data.get("data_hora"), str):
        raise ValueError("A data e hora devem ser uma string.")
    if not isinstance(appointment_data.get("usuario_id"), str):
        raise ValueError("O ID do usuário deve ser uma string.")
    if not isinstance(appointment_data.get("profissional_id"), str):
        raise ValueError("O ID do profissional deve ser uma string.")