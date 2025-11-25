from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ===============================================================
# MODELOS DE UTILIZADOR
# ===============================================================

class UserBase(BaseModel):
    """Modelo base para utilizadores, usado em inputs e outputs."""
    email: EmailStr
    nome: Optional[str] = None
    
class UserCreate(UserBase):
    """Modelo para criação de utilizador (Registo). Requer senha."""
    senha: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Modelo para login de utilizador."""
    email: EmailStr
    senha: str
    
class User(UserBase):
    """Modelo de utilizador para resposta API."""
    id: str = Field(..., description="ID do utilizador (UUID string)")
    foto_perfil: Optional[str] = Field(None, description="URL pública da foto de perfil")
    created_at: Optional[str] = None

    class Config:
        # Permite mapear dados de dics para o modelo (como os do JSONDatabase)
        # O 'id' deve ser compatível com str, o que os UUIDs são.
        from_attributes = True

# Modelo auxiliar, se precisar de guardar na BD
class UserInDB(User):
    """Modelo de utilizador com a senha hasheada (uso interno)."""
    senha: str


# ===============================================================
# MODELOS DE PROFISSIONAIS
# ===============================================================

class Professional(BaseModel):
    """Modelo para um profissional de serviço."""
    id: str = Field(..., description="ID do profissional (UUID string)")
    nome: str
    tipo_servico: str = Field(..., description="Ex: 'cabelo', 'unha', 'estética'")
    especialidades: List[str]
    
    class Config:
        from_attributes = True


# ===============================================================
# MODELOS DE AGENDAMENTO
# ===============================================================

class AppointmentBase(BaseModel):
    """Modelo base para agendamentos."""
    profissional_id: str = Field(..., description="ID do profissional agendado (UUID string)")
    servico: str = Field(..., description="Nome do serviço (Ex: 'Corte Feminino', 'Manicure')")
    data_hora: str = Field(..., description="Data e hora do agendamento (formato ISO 8601 ou similar)")

class AppointmentCreate(AppointmentBase):
    """Modelo para a criação de um novo agendamento por um utilizador."""
    # O utilizador ID é obtido via token e não é enviado no payload.
    pass

class Appointment(AppointmentBase):
    """Modelo completo de agendamento para resposta API."""
    id: str = Field(..., description="ID do agendamento (UUID string)")
    usuario_id: str = Field(..., description="ID do utilizador que agendou (UUID string)")
    status: str = Field("agendado", description="Estado do agendamento")
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True