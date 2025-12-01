"""
AUTH.PY - AUTENTICAÇÃO E AUTORIZAÇÃO
=====================================
Sistema de autenticação JWT
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Annotated
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Imports internos
from .database import db
from .models import User

# ====================================================================
# CONFIGURAÇÕES
# ====================================================================

# Contexto para hashing de passwords (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurações JWT
SECRET_KEY = "sua_chave_secreta_muito_longa_e_unica_aqui_mude_em_producao"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ====================================================================
# FUNÇÕES DE HASHING
# ====================================================================

def get_password_hash(password: str) -> str:
    """Cria hash de uma senha"""
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return pwd_context.verify(plain_password[:72], hashed_password)


# ====================================================================
# FUNÇÕES DE TOKEN JWT
# ====================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "sub": str(data.get("id", data.get("sub", "")))
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ====================================================================
# AUTENTICAÇÃO DE USUÁRIO
# ====================================================================

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Autentica usuário por email e senha"""
    user_data = db.get_user_by_email(email)
    
    if not user_data:
        return None
    
    # Tenta obter a senha hashada (pode estar em 'senha' ou 'hashed_password')
    hashed_password = user_data.get("senha") or user_data.get("hashed_password")
    
    if not hashed_password:
        return None
    
    if not verify_password(password, hashed_password):
        return None
    
    return user_data


# ====================================================================
# OBTER USUÁRIO ATUAL
# ====================================================================

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Obtém usuário atual a partir do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Busca usuário no banco
    user_data = db.get_user_by_id(user_id)
    
    if user_data is None:
        raise credentials_exception
    
    # Remove senha antes de retornar
    user_data.pop("senha", None)
    user_data.pop("hashed_password", None)
    
    return User(**user_data)


# ====================================================================
# VERIFICAÇÃO DE ADMIN
# ====================================================================

async def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Verifica se o usuário atual é admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Requer privilégios de administrador."
        )
    return current_user
