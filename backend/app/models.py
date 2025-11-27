"""
MODELS.PY - MODELOS COMPLETOS DO SISTEMA
=========================================
Inclui todos os modelos necessários para:
- Usuários (clientes e profissionais)
- Settings (configurações do salão)
- Agendamentos com histórico médico
- Consultas e fichas de atendimento
- Histórico de procedimentos
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ===============================================================
# ENUMS
# ===============================================================

class UserRole(str, Enum):
    """Roles de usuário"""
    ADMIN = "admin"
    CLIENTE = "cliente"
    PROFISSIONAL = "profissional"


class AppointmentStatus(str, Enum):
    """Status de agendamento"""
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    EM_ATENDIMENTO = "em_atendimento"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class ServiceType(str, Enum):
    """Tipos de serviço"""
    CORTE = "corte"
    COLORACAO = "coloracao"
    LUZES = "luzes"
    MECHAS = "mechas"
    HIDRATACAO = "hidratacao"
    RETOQUE_RAIZ = "retoque_raiz"
    MANICURE = "manicure"
    PEDICURE = "pedicure"
    UNHA_GEL = "unha_gel"
    NAIL_ART = "nail_art"


# ===============================================================
# MODELOS DE UTILIZADOR
# ===============================================================

class UserBase(BaseModel):
    """Modelo base para utilizadores"""
    email: EmailStr
    nome: str = Field(..., min_length=3)
    telefone: Optional[str] = None
    morada: Optional[str] = None
    role: UserRole = UserRole.CLIENTE


class UserCreate(UserBase):
    """Modelo para criação de utilizador"""
    senha: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Modelo para login"""
    email: EmailStr
    senha: str


class User(UserBase):
    """Modelo de utilizador para resposta API"""
    id: str
    foto_perfil: Optional[str] = None
    created_at: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# ===============================================================
# MODELOS DE AUTENTICAÇÃO (TOKEN)
# ===============================================================

class Token(BaseModel):
    """Modelo de resposta de token de acesso, incluindo o objeto do usuário."""
    access_token: str
    token_type: str
    user: User # Usa o modelo User definido acima

class TokenData(BaseModel):
    """Modelo para dados decodificados do JWT (payload)."""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    id: Optional[str] = None


# ===============================================================
# MODELOS DE SETTINGS (CONFIGURAÇÕES)
# ===============================================================

class ColorPalette(BaseModel):
    """Paleta de cores do sistema"""
    primary: str = Field(default="#6366f1", pattern="^#([A-Fa-f0-9]{6})$")
    secondary: str = Field(default="#8b5cf6", pattern="^#([A-Fa-f0-9]{6})$")
    accent: str = Field(default="#ec4899", pattern="^#([A-Fa-f0-9]{6})$")
    background: str = Field(default="#ffffff", pattern="^#([A-Fa-f0-9]{6})$")
    text: str = Field(default="#1f2937", pattern="^#([A-Fa-f0-9]{6})$")


class Settings(BaseModel):
    """Configurações do sistema"""
    salon_name: str = Field(default="Salão IA")
    logo_url: str = Field(default="/static/images/default_logo.png")
    logo_filename: Optional[str] = None
    colors: ColorPalette = Field(default_factory=ColorPalette)
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None


# ===============================================================
# MODELOS DE PROFISSIONAIS
# ===============================================================

class Professional(BaseModel):
    """Modelo para profissional"""
    id: str
    nome: str
    tipo_servico: str
    especialidades: List[str]
    is_active: bool = True

    class Config:
        from_attributes = True


# ===============================================================
# MODELOS DE FICHA MÉDICA / CONSULTA
# ===============================================================

class MedicalHistory(BaseModel):
    """Histórico médico do cliente"""
    usa_medicamentos: bool = False
    medicamentos: Optional[str] = None
    alergias: Optional[str] = None
    tratamentos_anteriores: List[str] = Field(default_factory=list)
    banho_piscina_frequente: bool = False
    observacoes_medicas: Optional[str] = None


class MedicalHistoryCreate(MedicalHistory):
    """Criação de histórico médico"""
    cliente_id: str


class MedicalHistoryResponse(MedicalHistory):
    """Resposta de histórico médico"""
    id: str
    cliente_id: str
    created_at: str
    updated_at: Optional[str] = None


# ===============================================================
# MODELOS DE TESTE DE MECHA
# ===============================================================

class StrandTest(BaseModel):
    """Teste de mecha"""
    resultado: str
    observacoes: Optional[str] = None
    recomendacao: Optional[str] = None
    produto_testado: Optional[str] = None


class StrandTestCreate(StrandTest):
    """Criação de teste de mecha"""
    cliente_id: str
    profissional_id: str


class StrandTestResponse(StrandTest):
    """Resposta de teste de mecha"""
    id: str
    cliente_id: str
    profissional_id: str
    created_at: str


# ===============================================================
# MODELOS DE AGENDAMENTO
# ===============================================================

class ServiceItem(BaseModel):
    """Item de serviço individual"""
    tipo: ServiceType
    descricao: Optional[str] = None
    duracao_estimada: int = 60
    preco: Optional[float] = None


class AppointmentBase(BaseModel):
    """Modelo base para agendamento"""
    profissional_id: str
    data_hora: str
    servicos: List[ServiceItem] = Field(..., min_items=1)
    usar_ia: bool = False
    preferencias_ia: Optional[str] = None
    observacoes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Criação de agendamento"""
    requer_consulta: bool = False
    requer_teste_mecha: bool = False


class Appointment(AppointmentBase):
    """Modelo completo de agendamento"""
    id: str
    cliente_id: str
    status: AppointmentStatus = AppointmentStatus.PENDENTE
    created_at: str
    confirmed_at: Optional[str] = None
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True


# ===============================================================
# MODELOS DE ATENDIMENTO / FICHA DE PROCEDIMENTO
# ===============================================================

class ProcedureRecord(BaseModel):
    """Registro de procedimento realizado"""
    produtos_utilizados: List[str] = Field(default_factory=list)
    tecnicas_aplicadas: List[str] = Field(default_factory=list)
    tempo_processamento: Optional[int] = None
    observacoes_tecnicas: Optional[str] = None
    fotos_antes: List[str] = Field(default_factory=list)
    fotos_depois: List[str] = Field(default_factory=list)
    pode_publicar_fotos: bool = False


class ClientFeedback(BaseModel):
    """Feedback do cliente"""
    satisfacao: int = Field(..., ge=1, le=5)
    gostou_resultado: bool = True
    gostou_atendimento: bool = True
    observacoes_cliente: Optional[str] = None
    reacao_alergica: bool = False
    detalhes_reacao: Optional[str] = None


class AttendanceRecord(BaseModel):
    """Ficha completa de atendimento"""
    appointment_id: str
    cliente_id: str
    profissional_id: str
    procedimento: ProcedureRecord
    feedback: Optional[ClientFeedback] = None
    proxima_recomendacao: Optional[str] = None
    cronograma_tratamento: Optional[List[str]] = None


class AttendanceRecordCreate(AttendanceRecord):
    """Criação de ficha de atendimento"""
    pass


class AttendanceRecordResponse(AttendanceRecord):
    """Resposta de ficha de atendimento"""
    id: str
    created_at: str
    updated_at: Optional[str] = None


# ===============================================================
# MODELOS DE HISTÓRICO DO CLIENTE
# ===============================================================

class ClientHistory(BaseModel):
    """Histórico completo do cliente"""
    cliente_id: str
    agendamentos: List[Appointment] = Field(default_factory=list)
    atendimentos: List[AttendanceRecordResponse] = Field(default_factory=list)
    testes_mecha: List[StrandTestResponse] = Field(default_factory=list)
    historico_medico: Optional[MedicalHistoryResponse] = None
    observacoes_gerais: List[str] = Field(default_factory=list)


# ===============================================================
# MODELOS DE CONSULTA PROFISSIONAL
# ===============================================================

class Consultation(BaseModel):
    """Consulta inicial"""
    cliente_id: str
    profissional_id: str
    objetivo: str
    estado_atual_cabelo: str
    desejos_cliente: str
    historico_resumido: Optional[str] = None
    recomendacoes: Optional[str] = None
    requer_teste_mecha: bool = False


class ConsultationCreate(Consultation):
    """Criação de consulta"""
    pass


class ConsultationResponse(Consultation):
    """Resposta de consulta"""
    id: str
    created_at: str
    agendamento_id: Optional[str] = None


# ===============================================================
# MODELOS DE AGENDA DO PROFISSIONAL
# ===============================================================

class ProfessionalSchedule(BaseModel):
    """Agenda do profissional"""
    profissional_id: str
    data: str
    agendamentos: List[Appointment] = Field(default_factory=list)
    horarios_disponiveis: List[str] = Field(default_factory=list)
    total_agendamentos: int = 0


# ===============================================================
# MODELOS DE DISPONIBILIDADE
# ===============================================================

class TimeSlot(BaseModel):
    """Slot de horário"""
    horario: str
    disponivel: bool
    profissional_id: str
    duracao_disponivel: int = 60


class AvailabilityResponse(BaseModel):
    """Resposta de disponibilidade"""
    data: str
    profissional_id: str
    horarios: List[TimeSlot]