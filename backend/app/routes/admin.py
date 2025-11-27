from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Annotated

# Usando imports relativos, como nos outros routers
from ..auth import get_current_user 
from ..database import db 

router = APIRouter(
    tags=["admin"], # Adicionando tag para documentação
)

# --- Modelos Pydantic ---

class AdminConfig(BaseModel):
    """Modelo para as configurações de tema e logo."""
    primary_color: str = Field(default="#667eea", description="Cor primária do tema (CSS).")
    secondary_color: str = Field(default="#764ba2", description="Cor secundária do tema (CSS).")
    logo_url: str = Field(default="https://placehold.co/120x30/667eea/ffffff?text=Salão+IA", description="URL da imagem do logo.")

# --- Helpers de Configuração ---

CONFIG_COLLECTION = "system_config"
CONFIG_DOC_ID = "main_config"

def get_current_admin(current_user: Annotated[dict, Depends(get_current_user)]):
    """Verifica se o usuário logado é um administrador."""
    # A verificação de role deve ser feita contra o campo 'role' 
    # que é definido no modelo User (ver models.py)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Requer privilégios de administrador."
        )
    return current_user

# --- Endpoints ---

@router.get("/config", response_model=AdminConfig)
async def get_admin_config():
    """Obtém as configurações atuais do salão."""
    config_data = db.get_document(CONFIG_COLLECTION, CONFIG_DOC_ID)
    if not config_data:
        # Retorna o modelo padrão se não houver dados salvos
        return AdminConfig()
    
    # Valida e retorna os dados
    return AdminConfig(**config_data)

@router.post("/config/save", response_model=AdminConfig)
async def save_admin_config_simple(
    config_data_model: AdminConfig, # Recebe o objeto completo com as novas cores e logo_url
    current_user: Annotated[dict, Depends(get_current_admin)] # Requer admin
):
    """Salva as configurações de tema e logo. Requer admin."""
    
    # Converte o Pydantic model para um dicionário salvável
    config_data = config_data_model.model_dump()
    
    # Salvar na base de dados
    db.update_document(CONFIG_COLLECTION, CONFIG_DOC_ID, config_data)
    
    # Retorna a configuração atualizada
    return await get_admin_config()
