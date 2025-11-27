"""
USERS.PY - ROTAS DE USUÁRIOS (LOGIN E REGISTRO)
================================================
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.models import User, UserCreate, UserLogin
from app.database import db
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

# ============================================================
# REGISTRO DE USUÁRIO
# ============================================================

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Registra novo usuário no sistema.
    
    Args:
        user: Dados do novo usuário (email, nome, senha, role)
    
    Returns:
        Dados do usuário criado (sem senha)
    """
    # Verifica se email já existe
    existing_user = db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Hash da senha
    hashed_password = get_password_hash(user.senha)
    
    # Cria usuário
    user_data = user.dict()
    user_data["senha"] = hashed_password
    
    created_user = db.create_user(user_data)
    
    return User(**created_user)


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
async def login(credentials: UserLogin):
    """
    Faz login do usuário e retorna token JWT.
    
    Args:
        credentials: Email e senha do usuário
    
    Returns:
        access_token: Token JWT para autenticação
        token_type: Tipo do token (bearer)
        user: Dados do usuário logado
    """
    # Busca usuário por email
    user = db.get_user_by_email(credentials.email)
    
    # Verifica se usuário existe
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica senha
    if not verify_password(credentials.senha, user["senha"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verifica se usuário está ativo
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Cria token de acesso (inclui email e id)
    access_token = create_access_token(data={"sub": user["email"], "id": user["id"]})
    
    # Remove senha antes de retornar
    user_data = {k: v for k, v in user.items() if k != "senha"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


# ============================================================
# OBTER USUÁRIO ATUAL
# ============================================================

@router.get("/me", response_model=User)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retorna dados do usuário autenticado.
    
    Args:
        current_user: Usuário obtido do token JWT
    
    Returns:
        Dados do usuário logado
    """
    return current_user


# ============================================================
# LISTAR TODOS OS USUÁRIOS (ADMIN)
# ============================================================

@router.get("/", response_model=list[User])
async def list_users(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Lista todos os usuários.
    Apenas administradores podem listar todos os usuários.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar usuários"
        )
    
    users = db.get_all_users()
    
    # Remove senhas
    users_without_password = [
        {k: v for k, v in user.items() if k != "senha"}
        for user in users
    ]
    
    return [User(**user) for user in users_without_password]


# ============================================================
# ATUALIZAR USUÁRIO
# ============================================================

@router.patch("/me", response_model=User)
async def update_me(
    update_data: dict,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Atualiza dados do usuário autenticado.
    
    Args:
        update_data: Dados a atualizar (nome, telefone, morada, foto_perfil)
        current_user: Usuário autenticado
    
    Returns:
        Dados do usuário atualizado
    """
    # Campos permitidos para atualização
    allowed_fields = ["nome", "telefone", "morada", "foto_perfil"]
    
    # Filtra apenas campos permitidos
    filtered_data = {
        k: v for k, v in update_data.items() 
        if k in allowed_fields
    }
    
    if not filtered_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo válido para atualizar"
        )
    
    # Atualiza usuário
    updated_user = db.update_user(current_user.id, filtered_data)
    
    return User(**updated_user)


# ============================================================
# MUDAR SENHA
# ============================================================

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Altera senha do usuário.
    
    Args:
        old_password: Senha atual
        new_password: Nova senha
        current_user: Usuário autenticado
    
    Returns:
        Mensagem de sucesso
    """
    # Busca usuário completo (com senha)
    user = db.get_user_by_email(current_user.email)
    
    # Verifica senha atual
    if not verify_password(old_password, user["senha"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta"
        )
    
    # Valida nova senha
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ter pelo menos 6 caracteres"
        )
    
    # Hash da nova senha
    new_hashed_password = get_password_hash(new_password)
    
    # Atualiza senha
    db.update_user(current_user.id, {"senha": new_hashed_password})
    
    return {"message": "Senha alterada com sucesso"}


# ============================================================
# DELETAR USUÁRIO (ADMIN)
# ============================================================

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Deleta usuário.
    Apenas administradores podem deletar usuários.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem deletar usuários"
        )
    
    # Não pode deletar a si mesmo
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode deletar sua própria conta"
        )
    
    # Busca usuário
    users = db.get_all_users()
    user = next((u for u in users if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Remove usuário
    users = [u for u in users if u["id"] != user_id]
    db._write_file("users", users)
    
    return {"message": "Usuário deletado com sucesso"}