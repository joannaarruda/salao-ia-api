from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
# Assumindo que UserCreate e User estão definidos em app.models
from app.models import UserCreate, User 
from app.database import db 
from datetime import datetime
from ..auth import get_current_user


# =============================================================
# --- FUNÇÕES DE SEGURANÇA (MOCKUP) ---
# Em um projeto real, estas funções devem ser implementadas em app.security 
# para hashing seguro (ex: bcrypt) e validação de JWT.
# =============================================================
def get_password_hash(password: str) -> str:
    """Mockup: Retorna a senha hasheada. SUBSTITUA PELA LÓGICA BCYPT REAL."""
    return f"hashed_{password}_secure"

def get_current_user_id(token: str = Depends(lambda: None)) -> str:
    """
    Mockup: Função para obter o ID do usuário do token de autenticação.
    Esta função deve validar o JWT e levantar 401 se for inválido.
    """
    if token is None:
        # Se estiver usando Depends(OAuth2PasswordBearer) o token será injetado
        # Se o token não estiver presente (falha de autenticação/autorização)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou token ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Mockup para retornar um ID fixo para testes:
    # return "ID_EXTRAIDO_DO_TOKEN_VALIDO" 
    return "5aaa0775-8d44-4d89-a789-59553210a0a9" # ID de teste para sucesso no /me

# =============================================================
# --- ROTAS DE USUÁRIOS ---
# =============================================================
router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(user: UserCreate):
    """Cadastra um novo usuário e verifica se o email já existe."""
    existing_user = db.get_user_by_email(user.email)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email já cadastrado"
        )
    
    # Prepara os dados
    user_data = user.dict()
    user_data["senha"] = get_password_hash(user_data["senha"])
    user_data["created_at"] = datetime.now().isoformat()
    
    new_user = db.create_user(user_data)
    
    # Remove a senha antes de enviar para o frontend
    new_user.pop("senha", None)
    return new_user

@router.get("/me", response_model=User)
async def read_users_me(current_user_id: str = Depends(get_current_user_id)):
    """
    Retorna os detalhes do usuário logado.
    Esta é a rota que o frontend chama após um login bem-sucedido.
    """
    user = db.get_user_by_id(current_user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    # Remove a senha antes de enviar
    user.pop("senha", None)
    return user

@router.get("/", response_model=List[User], include_in_schema=False)
async def get_all_users_admin():
    """Rota de administração para listar todos os usuários (ocultada)."""
    users = db.get_all_users()
    # Remover senha de todos os usuários
    for user in users:
        user.pop("senha", None)
    return users