from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.auth import get_current_user
from app.database import db
from app.models import User
import os

router = APIRouter()

# Diretório para salvar uploads
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================
# Upload de foto do usuário
# =========================
@router.post("/upload-photo")
async def upload_photo(
    user: User = Depends(get_current_user),
    file: UploadFile = File(...)
):
    """
    Endpoint para enviar a foto do usuário.
    """
    if not file:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Salva o arquivo
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Atualiza o usuário com a nova foto
    db.update_user_photo(user.id, file_location)

    return {"message": "Foto enviada com sucesso", "photo_url": file_location}
