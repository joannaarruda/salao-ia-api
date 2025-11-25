from fastapi import HTTPException, Depends
from app.models import UserCreate, User
from app.database import db

def register_user(user: UserCreate):
    existing_user = db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    user_data = user.dict()
    user_data["senha"] = get_password_hash(user_data["senha"])
    new_user = db.create_user(user_data)
    new_user.pop("senha", None)
    return new_user

def get_user_details(user_id: str):
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.pop("senha", None)
    return user

def get_all_users():
    return db.get_all_users()  # Assuming a method exists to get all users in the database.