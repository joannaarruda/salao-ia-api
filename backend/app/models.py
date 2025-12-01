"""
MODELS.PY - MODELOS PYDANTIC ATUALIZADOS
========================================
Modelos com suporte completo a:
- Análise facial com IA
- Teste de mecha obrigatório
- Serviços detalhados
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================
# ENUMS
# ============================================================

class UserRole(str, Enum):
    """Roles de usuário"""
    CLIENTE = "cliente"
    PROFISSIONAL = "profissional"
    ADMIN = "admin"


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
    HIDRATACAO = "hidratacao"
    RETOQUE_RAIZ = "retoque_raiz"
    MANICURE = "manicure"
    PEDICURE = "pedicure"
    TRATAMENTO = "tratamento"
    DESCOLORACAO = "descoloracao"
    ALISAMENTO = "alisamento"
    PERMANENTE = "permanente"


# ============================================================
# MODELOS DE USUÁRIO
# ============================================================

class UserBase(BaseModel):
    """Base de usuário"""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefone: Optional[str] = None
    morada: Optional[str] = None


class UserCreate(UserBase):
    """Criação de usuário"""
    senha: str = Field(..., min_length=6)
    role: Optional[UserRole] = UserRole.CLIENTE


class UserLogin(BaseModel):
    """Login de usuário"""
    email: EmailStr
    senha: str


class User(UserBase):
    """Usuário completo (resposta)"""
    id: str
    role: UserRole = UserRole.CLIENTE
    foto_perfil: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================
# MODELOS DE TOKEN
# ============================================================

class Token(BaseModel):
    """Token de autenticação"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None


class TokenData(BaseModel):
    """Dados do token"""
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None


# ============================================================
# MODELOS DE PROFISSIONAL
# ============================================================

class Professional(BaseModel):
    """Profissional"""
    id: str
    nome: str
    tipo_servico: str
    especialidades: List[str] = []
    is_active: bool = True

    class Config:
        from_attributes = True


# ============================================================
# MODELOS DE SERVIÇO
# ============================================================

class Servico(BaseModel):
    """Serviço individual"""
    tipo: str
    descricao: Optional[str] = None
    duracao_estimada: int = Field(default=60, ge=15, le=480)
    preco: Optional[float] = None
    requer_teste_mecha: bool = False  # ✅ NOVO: Para colorações/químicas
    produtos_utilizados: List[str] = []  # ✅ NOVO: Lista de produtos


class ServicoCreate(BaseModel):
    """Criação de serviço"""
    tipo: str
    descricao: Optional[str] = None
    duracao_estimada: int = 60
    requer_teste_mecha: bool = False
    produtos_utilizados: List[str] = []


# ============================================================
# MODELOS DE ANÁLISE FACIAL (NOVO)
# ============================================================

class FacialAnalysisRequest(BaseModel):
    """Requisição de análise facial"""
    usar_foto_perfil: bool = False
    retornar_recomendacoes: bool = True


class FacialAnalysisResponse(BaseModel):
    """Resposta da análise facial"""
    modo: str  # "demo" ou "ia_real"
    formato_rosto: str
    tom_pele: str
    confianca: float
    cortes_sugeridos: List[str]
    cores_sugeridas: List[str]
    dicas_estilo: List[str]
    evitar_cortes: List[str] = []
    evitar_cores: List[str] = []
    message: Optional[str] = None


# ============================================================
# MODELOS DE AGENDAMENTO
# ============================================================

class AppointmentBase(BaseModel):
    """Base de agendamento"""
    profissional_id: str
    data_hora: str  # ISO 8601 format
    servicos: List[Servico]
    observacoes: Optional[str] = None
    usar_ia: bool = False  # ✅ Usar análise de IA
    preferencias_ia: Optional[str] = None
    requer_consulta: bool = False  # ✅ Consulta prévia
    requer_teste_mecha: bool = False  # ✅ NOVO: Teste de mecha necessário


class AppointmentCreate(AppointmentBase):
    """Criação de agendamento"""
    pass


class Appointment(AppointmentBase):
    """Agendamento completo"""
    id: str
    cliente_id: str
    status: AppointmentStatus = AppointmentStatus.PENDENTE
    created_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    completed_at: Optional[str] = None
    google_calendar_event_id: Optional[str] = None
    teste_mecha_realizado: bool = False  # ✅ NOVO
    teste_mecha_aprovado: Optional[bool] = None  # ✅ NOVO
    teste_mecha_data: Optional[str] = None  # ✅ NOVO

    class Config:
        from_attributes = True


# ============================================================
# MODELOS DE DISPONIBILIDADE
# ============================================================

class TimeSlot(BaseModel):
    """Slot de horário"""
    horario: str
    disponivel: bool
    profissional_id: str
    duracao_disponivel: int = 0


class AvailabilityResponse(BaseModel):
    """Resposta de disponibilidade"""
    data: str
    profissional_id: str
    horarios: List[TimeSlot]


class ProfessionalSchedule(BaseModel):
    """Agenda do profissional"""
    profissional_id: str
    data: str
    agendamentos: List[Appointment]
    horarios_disponiveis: List[str]
    total_agendamentos: int


# ============================================================
# MODELOS DE HISTÃ"RICO MÉDICO
# ============================================================

class MedicalHistoryBase(BaseModel):
    """Base de histórico médico"""
    alergias: List[str] = []
    medicamentos_em_uso: List[str] = []
    tratamentos_anteriores: List[str] = []
    quimica_recente: bool = False
    data_ultima_quimica: Optional[str] = None
    tipo_ultima_quimica: Optional[str] = None
    problemas_couro_cabeludo: List[str] = []
    gravidez_ou_amamentacao: bool = False
    banho_piscina_frequente: bool = False
    observacoes: Optional[str] = None


class MedicalHistoryCreate(MedicalHistoryBase):
    """Criação de histórico médico"""
    pass


class MedicalHistory(MedicalHistoryBase):
    """Histórico médico completo"""
    id: str
    cliente_id: str
    created_at: Optional[str] = None
    data_atualizacao: Optional[str] = None

    class Config:
        from_attributes = True


class MedicalHistoryResponse(MedicalHistory):
    """Resposta de histórico médico"""
    pass


# ============================================================
# MODELOS DE CONSULTA
# ============================================================

class ConsultationBase(BaseModel):
    """Base de consulta"""
    cliente_id: str
    objetivo: str
    estado_atual_cabelo: Optional[str] = None
    desejos_cliente: Optional[str] = None
    requer_teste_mecha: bool = False


class ConsultationCreate(ConsultationBase):
    """Criação de consulta"""
    pass


class Consultation(ConsultationBase):
    """Consulta completa"""
    id: str
    profissional_id: str
    agendamento_id: Optional[str] = None
    created_at: Optional[str] = None
    resultado: Optional[str] = None

    class Config:
        from_attributes = True


class ConsultationResponse(Consultation):
    """Resposta de consulta"""
    pass


# ============================================================
# MODELOS DE TESTE DE MECHA (ATUALIZADO)
# ============================================================

class StrandTestBase(BaseModel):
    """Base de teste de mecha"""
    cliente_id: str
    produto_testado: str
    area_teste: str = "nuca"
    tempo_exposicao: int  # minutos
    resultado: Optional[str] = None
    aprovado: Optional[bool] = None
    observacoes: Optional[str] = None
    reacao_alergica: bool = False  # ✅ NOVO
    fotos_teste: List[str] = []  # ✅ NOVO


class StrandTestCreate(StrandTestBase):
    """Criação de teste de mecha"""
    pass


class StrandTest(StrandTestBase):
    """Teste de mecha completo"""
    id: str
    profissional_id: str
    agendamento_id: Optional[str] = None  # ✅ NOVO: Vincula ao agendamento
    created_at: Optional[str] = None
    data_validade: Optional[str] = None  # Normalmente 6 meses

    class Config:
        from_attributes = True


class StrandTestResponse(StrandTest):
    """Resposta de teste de mecha"""
    pass


# ============================================================
# MODELOS DE FICHA DE ATENDIMENTO
# ============================================================

class ProcedimentoDetalhe(BaseModel):
    """Detalhes do procedimento"""
    produtos_utilizados: List[str] = []
    tecnicas_aplicadas: List[str] = []
    tempo_processamento: Optional[int] = None
    observacoes_tecnicas: Optional[str] = None
    fotos_antes: List[str] = []
    fotos_depois: List[str] = []
    pode_publicar_fotos: bool = False


class FeedbackCliente(BaseModel):
    """Feedback do cliente"""
    satisfacao: Optional[int] = Field(None, ge=1, le=5)
    gostou_resultado: Optional[bool] = None
    comentario: Optional[str] = None
    reacao_alergica: bool = False
    data_feedback: Optional[str] = None


class AttendanceRecordBase(BaseModel):
    """Base de ficha de atendimento"""
    appointment_id: str
    cliente_id: str
    procedimento: ProcedimentoDetalhe
    proxima_recomendacao: Optional[str] = None
    cronograma_tratamento: Optional[str] = None


class AttendanceRecordCreate(AttendanceRecordBase):
    """Criação de ficha de atendimento"""
    pass


class AttendanceRecord(AttendanceRecordBase):
    """Ficha de atendimento completa"""
    id: str
    profissional_id: str
    created_at: Optional[str] = None
    feedback: Optional[FeedbackCliente] = None

    class Config:
        from_attributes = True


class AttendanceRecordResponse(AttendanceRecord):
    """Resposta de ficha de atendimento"""
    pass