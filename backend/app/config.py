"""
APP/CONFIG.PY - CONFIGURAÇÃO DE FEATURES
========================================
Configuração centralizada de funcionalidades habilitadas/desabilitadas
"""

from typing import Dict, Any
from pydantic import BaseModel


class FeatureFlags(BaseModel):
    """Flags de funcionalidades"""
    
    # IA e Análise Facial
    facial_analysis_enabled: bool = False  # Sistema de análise facial (Azure/Face++)
    ai_hair_suggestions_enabled: bool = True  # Sugestões de IA (demo mode)
    ai_demo_mode: bool = True  # Usar modo demo (sem APIs reais)
    
    # Google Calendar
    google_calendar_enabled: bool = False
    
    # Internacionalização
    i18n_enabled: bool = False
    
    # Teste de Mecha
    strand_test_enabled: bool = True
    strand_test_required_for_coloring: bool = False  # Tornar obrigatório para colorações
    
    # Consultas
    consultation_required_for_first_time: bool = True  # Obrigatório para primeira vez
    
    # Upload de fotos
    photo_upload_enabled: bool = True
    max_photo_size_mb: int = 5
    
    # Notificações
    email_notifications_enabled: bool = False
    sms_notifications_enabled: bool = False
    
    # Pagamentos
    online_payment_enabled: bool = False


class APICredentials(BaseModel):
    """Credenciais de APIs externas"""
    
    # Azure Face API
    azure_face_api_key: str = ""
    azure_face_endpoint: str = ""
    
    # Face++
    facepp_api_key: str = ""
    facepp_api_secret: str = ""
    
    # Google Calendar
    google_calendar_credentials_path: str = ""
    
    # Outros
    sendgrid_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""


class AppConfig:
    """Configuração principal da aplicação"""
    
    def __init__(self):
        self.features = FeatureFlags()
        self.credentials = APICredentials()
        self.app_name = "Salão IA"
        self.app_version = "2.0.0"
        self.debug_mode = True
    
    def enable_feature(self, feature_name: str):
        """Habilita uma funcionalidade"""
        if hasattr(self.features, feature_name):
            setattr(self.features, feature_name, True)
            print(f"✅ Feature '{feature_name}' habilitada")
        else:
            print(f"⚠️ Feature '{feature_name}' não existe")
    
    def disable_feature(self, feature_name: str):
        """Desabilita uma funcionalidade"""
        if hasattr(self.features, feature_name):
            setattr(self.features, feature_name, False)
            print(f"❌ Feature '{feature_name}' desabilitada")
        else:
            print(f"⚠️ Feature '{feature_name}' não existe")
    
    def set_credential(self, credential_name: str, value: str):
        """Define uma credencial"""
        if hasattr(self.credentials, credential_name):
            setattr(self.credentials, credential_name, value)
            print(f"🔑 Credencial '{credential_name}' configurada")
        else:
            print(f"⚠️ Credencial '{credential_name}' não existe")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Retorna configuração como dicionário"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "features": self.features.dict(),
            "debug_mode": self.debug_mode
        }


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def is_feature_enabled(feature_name: str) -> bool:
    """Verifica se uma feature está habilitada"""
    return getattr(config.features, feature_name, False)


def get_api_credential(credential_name: str) -> str:
    """Obtém uma credencial de API"""
    return getattr(config.credentials, credential_name, "")


def require_feature(feature_name: str):
    """Decorator para verificar se uma feature está habilitada"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not is_feature_enabled(feature_name):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=503,
                    detail=f"Funcionalidade '{feature_name}' não está habilitada"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# INSTÂNCIA GLOBAL (CRIADA AUTOMATICAMENTE)
# =============================================================================

# Cria instância global de configuração
config = AppConfig()

print("\n" + "="*70)
print("⚙️  CONFIGURAÇÃO CARREGADA")
print("="*70)
print(f"✅ Modo: {'DEMO' if config.features.ai_demo_mode else 'PRODUÇÃO'}")
print(f"✅ Análise Facial: {'Habilitada' if config.features.facial_analysis_enabled else 'Desabilitada (use modo demo)'}")
print(f"✅ Teste de Mecha: {'Habilitado' if config.features.strand_test_enabled else 'Desabilitado'}")
print(f"✅ Consulta Obrigatória: {'Sim' if config.features.consultation_required_for_first_time else 'Não'}")
print("="*70 + "\n")