"""
ROUTES/ADMIN.PY - ROTAS DE ADMINISTRAÇÃO
========================================
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Annotated

from app.auth import get_current_user
from app.database import db

router = APIRouter()


# =============================================================
# MODELOS
# =============================================================

class AdminConfig(BaseModel):
    """Modelo para as configurações de tema e logo"""
    primary_color: str = Field(default="#667eea", description="Cor primária do tema (CSS).")
    secondary_color: str = Field(default="#764ba2", description="Cor secundária do tema (CSS).")
    logo_url: str = Field(default="https://placehold.co/120x30/667eea/ffffff?text=Salão+IA", description="URL da imagem do logo.")


# =============================================================
# HELPERS
# =============================================================

CONFIG_COLLECTION = "system_config"
CONFIG_DOC_ID = "main_config"


def get_current_admin(current_user: Annotated[dict, Depends(get_current_user)]):
    """Verifica se o usuário logado é um administrador"""
    
    # Aceita tanto objeto User quanto dict
    role = getattr(current_user, 'role', None) or current_user.get("role")
    
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer privilégios de administrador."
        )
    return current_user


# =============================================================
# ENDPOINTS
# =============================================================

@router.get("/config", response_model=AdminConfig)
async def get_admin_config():
    """Obtém as configurações atuais do salão"""
    
    config_data = db.get_document(CONFIG_COLLECTION, CONFIG_DOC_ID)
    
    if not config_data:
        # Retorna o modelo padrão se não houver dados salvos
        return AdminConfig()
    
    return AdminConfig(**config_data)


@router.post("/config/save", response_model=AdminConfig)
async def save_admin_config_simple(
    config_data_model: AdminConfig,
    current_user: Annotated[dict, Depends(get_current_admin)]
):
    """Salva as configurações de tema e logo. Requer admin."""
    
    # Converte o Pydantic model para um dicionário salvável
    config_data = config_data_model.model_dump()
    
    # Salvar na base de dados
    db.update_document(CONFIG_COLLECTION, CONFIG_DOC_ID, config_data)
    
    # Retorna a configuração atualizada
    return await get_admin_config()


@router.get("/stats")
async def get_admin_stats(
    current_user: Annotated[dict, Depends(get_current_admin)]
):
    """Retorna estatísticas básicas do sistema (apenas admin)"""
    
    users = db.get_all_users()
    appointments = db.get_all_appointments()
    professionals = db.get_all_professionals()
    
    return {
        "total_users": len(users),
        "total_appointments": len(appointments),
        "total_professionals": len(professionals),
        "appointments_by_status": {
            "pendente": len([a for a in appointments if a.get("status") == "pendente"]),
            "confirmado": len([a for a in appointments if a.get("status") == "confirmado"]),
            "concluido": len([a for a in appointments if a.get("status") == "concluido"]),
            "cancelado": len([a for a in appointments if a.get("status") == "cancelado"])
        },
        "users_by_role": {
            "cliente": len([u for u in users if u.get("role") == "cliente"]),
            "profissional": len([u for u in users if u.get("role") == "profissional"]),
            "admin": len([u for u in users if u.get("role") == "admin"])
        }
    }
