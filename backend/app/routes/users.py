"""
ROUTES/USERS.PY - ROTAS DE USUÁRIOS
===================================
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated, List

from app.models import User, UserCreate
from app.database import db
from app.auth import get_current_user, get_password_hash, verify_password

router = APIRouter()


@router.get("/me", response_model=User)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Retorna dados do usuário autenticado"""
    return current_user


@router.get("/", response_model=List[User])
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


@router.patch("/me", response_model=User)
async def update_me(
    update_data: dict,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Atualiza dados do usuário autenticado"""
    
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
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar usuário"
        )
    
    # Remove senha
    updated_user.pop("senha", None)
    
    return User(**updated_user)


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Altera senha do usuário"""
    
    # Busca usuário completo (com senha)
    user = db.get_user_by_email(current_user.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verifica senha atual
    if not verify_password(old_password, user.get("senha", "")):
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
    user = db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Remove usuário
    users = db.get_all_users()
    users = [u for u in users if u["id"] != user_id]
    db._write_file("users", users)
    
    return {"message": "Usuário deletado com sucesso"}
