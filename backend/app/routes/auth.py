from fastapi import APIRouter, HTTPException, status
from app.models import UserCreate, UserLogin
from app.auth import get_password_hash, verify_password, create_access_token
from app.database import db

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    existing_user = db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    user_data = user.dict()
    user_data["senha"] = get_password_hash(user_data["senha"])
    new_user = db.create_user(user_data)
    new_user.pop("senha", None)
    return {"message": "Usuário criado com sucesso", "user": new_user}

@router.post("/login")
async def login(credentials: UserLogin):
    user = db.get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.senha, user.get("senha")):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    user_id_str = str(user.get("id"))
    access_token = create_access_token(data={"id": user_id_str})
    
    user['id'] = user_id_str
    user.pop("senha", None)
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}
