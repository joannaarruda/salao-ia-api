from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.database import db
from app.auth import get_current_user
from app.models import User
from app.ai.hair_style import edit_hair_style
import os

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/suggestions")
async def get_ai_suggestions(
    user: User = Depends(get_current_user),
    file: UploadFile = File(None),
    style: str = "corte curto loiro"
):
    """
    Gera uma imagem de sugestão de cabelo usando IA.
    Aceita um novo arquivo ou usa a foto de perfil existente.
    """
    # 1. Busca o usuário atualizado no DB
    db_user = db.get_user_by_id(user.id)
    
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # 2. Decide qual foto usar
    file_location = None
    
    if file:
        # Se enviou um novo arquivo, salva temporariamente
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_location, "wb") as f:
                f.write(await file.read())
            print(f"✅ Arquivo salvo em: {file_location}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
            
    elif db_user.get("foto_perfil"):
        # Usa a foto de perfil existente
        file_location = db_user["foto_perfil"].replace("\\", "/")
        print(f"✅ Usando foto de perfil: {file_location}")
    else:
        raise HTTPException(status_code=400, detail="Nenhuma foto fornecida ou foto de perfil não encontrada")

    # 3. Verifica se o arquivo realmente existe
    if not os.path.exists(file_location):
        raise HTTPException(
            status_code=404, 
            detail=f"Arquivo não encontrado no caminho: {file_location}"
        )

    # 4. Chama a função de IA
    try:
        print(f"🤖 Processando imagem com IA: {file_location}")
        modified_image_bytes = edit_hair_style(file_location, style)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")

    # 5. Salva a imagem gerada com nome único
    original_filename = os.path.basename(file_location)
    output_filename = f"ai_{user.id}_{original_filename}"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    
    try:
        with open(output_path, "wb") as f:
            f.write(modified_image_bytes)
        print(f"✅ Imagem IA salva em: {output_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar resultado: {str(e)}")

    # 6. Retorna o caminho da imagem gerada (não atualiza a foto de perfil)
    return {
        "user_id": user.id,
        "photo_ia_url": f"/static/uploads/{output_filename}",
        "message": "Sugestão gerada com sucesso!"
    }


@router.post("/analyze")
async def analyze_photo(
    user: User = Depends(get_current_user)
):
    """
    Analisa a foto de perfil do usuário e retorna sugestões.
    """
    # 1. Busca usuário
    db_user = db.get_user_by_id(user.id)
    
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # 2. Verifica se tem foto de perfil
    if not db_user.get("foto_perfil"):
        raise HTTPException(status_code=400, detail="Nenhuma foto de perfil encontrada. Faça upload primeiro.")
    
    file_location = db_user["foto_perfil"].replace("\\", "/")
    
    # 3. Verifica se o arquivo existe
    if not os.path.exists(file_location):
        raise HTTPException(
            status_code=404,
            detail=f"Foto de perfil não encontrada no servidor: {file_location}"
        )
    
    # 4. Aqui você pode implementar análise real com IA
    # Por enquanto, retorna sugestões mockadas
    return {
        "cortes_sugeridos": [
            "Corte em camadas médias",
            "Bob assimétrico",
            "Franja lateral"
        ],
        "cores_sugeridas": [
            "Castanho chocolate",
            "Loiro mel",
            "Ruivo acobreado"
        ],
        "estilos_recomendados": [
            "Ondas suaves",
            "Liso elegante",
            "Cacheado natural"
        ],
        "cores_esmalte": [
            "Vermelho clássico",
            "Nude rosado",
            "Azul marinho"
        ],
        "foto_analisada": file_location
    }