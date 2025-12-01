"""
ROUTES/AUTH.PY - ROTAS DE AUTENTICAÇÃO
======================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta

from app.models import User, Token, UserCreate
from app.database import db
from app.auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Cria um novo usuário cliente"""
    
    # Verifica se email já existe
    if db.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registado"
        )
    
    # Hash da senha
    hashed_password = get_password_hash(user_data.senha)
    
    # Cria usuário
    new_user = user_data.model_dump()
    new_user["senha"] = hashed_password
    new_user["role"] = "cliente"  # Role padrão
    
    created_user = db.create_user(new_user)
    
    # Remove senha antes de retornar
    created_user.pop("senha", None)
    
    return User(**created_user)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Autentica o usuário usando Form Data (username/email e password)
    """
    # Busca usuário
    db_user = db.get_user_by_email(form_data.username)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Verifique seu email e senha.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Autentica
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Verifique seu email e senha.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={
            "sub": user["id"],
            "email": user["email"],
            "role": user.get("role", "cliente"),
            "id": user["id"]
        },
        expires_delta=access_token_expires,
    )
    
    # Remove senha do usuário antes de retornar
    user_response = {k: v for k, v in user.items() if k != "senha"}
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )
