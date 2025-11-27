# app/routes/auth_utils.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt, JWTError

# Imports internos
# Importa o objeto 'settings' que você corrigiu no passo anterior
from ..config import settings
from ..models import UserRole 

# Inicialização de contextos
# Configura o contexto de hash para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===============================================================
# FUNÇÕES DE HASH DE SENHA
# ===============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Cria o hash de uma senha."""
    return pwd_context.hash(password)

# ===============================================================
# FUNÇÕES DE TOKEN JWT
# ===============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um JSON Web Token (JWT) de acesso."""
    to_encode = data.copy()
    
    # Define a expiração do token
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "sub": "access_token"})
    
    # Codifica o token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

# ===============================================================
# FUNÇÃO DE AUTENTICAÇÃO DE USUÁRIO
# ===============================================================

def authenticate_user(db_user: dict, password: str) -> Optional[dict]:
    """
    Verifica se o hash da senha armazenada corresponde à senha fornecida.
    """
    # 1. Verifica o hash:
    # 🚨 CORREÇÃO AQUI: Procura por 'hashed_password' (padrão) OU 'senha' (o que está no seu JSON)
    hashed_password = db_user.get("hashed_password") or db_user.get("senha")
    
    if not hashed_password:
        return None # Utilizador sem hash de senha no DB

    # 2. Verifica a senha
    if not verify_password(password, hashed_password):
        return None # Senha incorreta

    # 3. Retorna o objeto do utilizador (removendo a senha/hash)
    user_data = db_user.copy()
    user_data.pop("senha", None) # Remove a chave "senha"
    user_data.pop("hashed_password", None) # Remove a chave "hashed_password" (se existir)
    return user_data