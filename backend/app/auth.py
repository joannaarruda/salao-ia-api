import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Annotated
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# 🚨 IMPORTAÇÕES DA BASE DE DADOS E MODELOS
from .database import db
from .models import User 

# ====================================================================
# 1. CONFIGURAÇÕES
# ====================================================================

# Contexto para hashing de passwords (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "sua_chave_secreta_muito_longa_e_unica_aqui" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") 


# ====================================================================
# 2. FUNÇÕES DE HASHING
# ====================================================================

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)


# ====================================================================
# 3. FUNÇÃO PARA CRIAR TOKEN
# ====================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:

    if "id" not in data:
        raise ValueError("O payload do token deve conter a chave 'id'.")

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "sub": str(data["id"])  # id do usuário
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ====================================================================
# 4. AUTENTICAR UTILIZADOR (JSON DATABASE)
# ====================================================================

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:

    user_data = db.get_user_by_email(email)

    if not user_data:
        return None

    if not verify_password(password, user_data.get("senha", "")):
        return None

    return user_data



# ====================================================================
# 5. OBTER UTILIZADOR ATUAL PELO TOKEN (JSON)
# ====================================================================

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:

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

    # Buscar usuário no JSON
    user_data = db.get_user_by_id(user_id)

    if user_data is None:
        raise credentials_exception

    # NÃO retornar senha no objeto
    user_data.pop("senha", None)

    return User(**user_data)
