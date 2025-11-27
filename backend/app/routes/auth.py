from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta

# Importações do seu projeto
from ..models import User, Token, UserCreate
from ..database import db
from ..config import settings
from .auth_utils import authenticate_user, create_access_token, get_password_hash
from ..models import Token # O modelo de resposta

# Necessário para o corpo do pedido (Form Data)
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Cria um novo usuário cliente."""
    
    if db.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email já registado")
        
    hashed_password = get_password_hash(user_data.senha)
    
    new_user = user_data.model_dump()
    new_user["senha"] = hashed_password
    new_user["role"] = "cliente" # Define o role padrão
    
    created_user = db.create_user(new_user)
    
    return User(**created_user)
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Autentica o usuário usando Form Data (username/email e password).
    """
    # 1. BUSCAR O UTILIZADOR NO DB (o username aqui é o email)
    # 🚨 NOTA: Assumimos que db.get_user_by_email(email) existe e retorna o objeto do usuário (com o hash da senha)
    db_user = db.get_user_by_email(form_data.username) 

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Verifique seu email e senha.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 2. AUTENTICAR O UTILIZADOR (PASSANDO APENAS O OBJETO DO UTILIZADOR E A SENHA)
    # AGORA APENAS 2 ARGUMENTOS SÃO PASSADOS
    user = authenticate_user(db_user, form_data.password) # <-- CORRIGIDO
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Verifique seu email e senha.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. CRIAR O TOKEN
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"], "id": user["id"]},
        expires_delta=access_token_expires,
    )
    
    # 4. RETORNAR O TOKEN E O OBJETO DO UTILIZADOR
    return Token(access_token=access_token, token_type="bearer", user=user)