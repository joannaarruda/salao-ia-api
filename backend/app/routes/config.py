from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional
import json
import os
import shutil

# --- CONFIGURAÇÃO DE DIRETÓRIOS ---
# Certifique-se de ter um diretório 'static/uploads' e servi-lo via FastAPI
CONFIG_FILE = "config.json" # Assumindo que este arquivo está na raiz do projeto ou em um local acessível
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- MODELO Pydantic ---

class Settings(BaseModel):
    """Modelo para as configurações do sistema (cores e logo)."""
    logo_url: str = Field("/static/images/default_logo.png", description="URL da logo.")
    primary_color: str = Field("#007bff", description="Cor primária (ex: #RRGGBB).")
    secondary_color: str = Field("#6c757d", description="Cor secundária (ex: #RRGGBB).")


# --- FUNÇÕES DE PERSISTÊNCIA (Simples I/O de JSON) ---

def get_current_config() -> Settings:
    """Carrega a configuração atual ou a padrão."""
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return Settings(**data)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir/for inválido, retorna o padrão e o cria
        default_config = Settings()
        save_config(default_config)
        return default_config

def save_config(config: Settings):
    """Salva a configuração no arquivo JSON."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.dict(), f, indent=4)

# --- DEPENDÊNCIA ADMIN (MOCK) ---
# **AVISO**: Esta é uma implementação MOCK. Substitua-a pelo seu código real.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_admin_user(token: str = Depends(oauth2_scheme)):
    """Verifica o token e se o usuário tem o role 'admin'."""
    # Sua lógica de verificação de JWT e role vai aqui. 
    # Se o usuário não for admin, lance:
    # raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem aceder.")
    return {"id": "admin_user", "role": "admin"} # Retorna um objeto mock de admin

# --- ROTAS ---

router = APIRouter(prefix="/admin/config", tags=["Admin Configuração"])

@router.get("/", response_model=Settings, summary="Obter Configuração Atual")
async def get_system_config():
    """Recupera as configurações atuais do sistema (logo e cores)."""
    return get_current_config()

@router.post("/", response_model=Settings, summary="Atualizar Configuração e Logo", status_code=status.HTTP_200_OK)
async def update_system_config(
    # Endpoint protegido por autenticação de admin
    admin_user: dict = Depends(get_current_admin_user), 
    primary_color: str = Field(..., max_length=7, pattern="^#[0-9a-fA-F]{6}$"),
    secondary_color: str = Field(..., max_length=7, pattern="^#[0-9a-fA-F]{6}$"),
    logo: Optional[UploadFile] = File(None, description="Opcional: Novo ficheiro de logo")
):
    """Atualiza as cores do sistema e, opcionalmente, faz upload de uma nova logo."""
    
    current_config = get_current_config()
    
    # 1. Processar a nova logo
    if logo:
        # Cria um nome de arquivo único e seguro
        file_extension = os.path.splitext(logo.filename)[-1].lower()
        logo_filename = f"logo_{os.urandom(8).hex()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, logo_filename)
        
        # Salva o arquivo no disco
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(logo.file, buffer)
            
            # Atualiza a URL da logo para ser servida pelo backend
            current_config.logo_url = f"/{UPLOAD_DIR}/{logo_filename}"
            
        except Exception as e:
            print(f"Erro ao salvar a logo: {e}")
            raise HTTPException(status_code=500, detail="Erro ao salvar o arquivo da logo.")
    
    # 2. Atualizar as cores
    current_config.primary_color = primary_color
    current_config.secondary_color = secondary_color
    
    # 3. Salvar as alterações
    save_config(current_config)
    
    return current_config