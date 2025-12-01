"""
ROUTES/MEDIA.PY - UPLOAD DE MÍDIA
=================================
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Annotated
import os

from app.auth import get_current_user
from app.database import db
from app.models import User

router = APIRouter()

# Diretório para salvar uploads
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-photo")
async def upload_photo(
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...)
):
    """Endpoint para enviar a foto do usuário"""
    
    if not file:
        raise HTTPException(
            status_code=400,
            detail="Nenhum arquivo enviado"
        )
    
    # Validar tamanho (5MB máximo)
    max_size = 5 * 1024 * 1024
    contents = await file.read()
    
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Arquivo muito grande. Máximo 5MB."
        )
    
    # Validar formato
    allowed_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Formato inválido. Use PNG, JPG ou JPEG."
        )
    
    # Gerar nome único
    import uuid
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_extension}"
    file_location = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Salvar arquivo
    with open(file_location, "wb") as f:
        f.write(contents)
    
    # Atualizar usuário com a nova foto
    db.update_user_photo(current_user.id, file_location)
    
    return {
        "message": "Foto enviada com sucesso",
        "photo_url": f"/{file_location}"
    }


@router.delete("/photo")
async def delete_photo(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Remove a foto de perfil do usuário"""
    
    # Busca usuário para obter o caminho da foto
    user = db.get_user_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    
    foto_perfil = user.get("foto_perfil")
    
    if foto_perfil and os.path.exists(foto_perfil):
        os.remove(foto_perfil)
    
    # Atualiza usuário removendo a foto
    db.update_user(current_user.id, {"foto_perfil": None})
    
    return {"message": "Foto removida com sucesso"}
