"""
AI.PY MINIMALISTA - MODO DEMO GARANTIDO
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Annotated, Optional
import os

from app.database import db
from app.auth import get_current_user
from app.models import User

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =============================================================================
# FUNÇÕES DE RECOMENDAÇÃO (MOCKADAS - MODO DEMO)
# =============================================================================

def get_demo_recommendations():
    """Retorna recomendações fixas em modo demo"""
    return {
        "modo": "demo",
        "formato_rosto": "oval",
        "tom_pele": "neutro",
        "confianca": 0.0,
        "message": "Recomendações em modo demo. Habilite análise facial para resultados personalizados.",
        "cortes_sugeridos": [
            "Corte em camadas médias",
            "Bob assimétrico",
            "Franja lateral",
            "Long bob (lob)",
            "Ondas suaves"
        ],
        "cores_sugeridas": [
            "Castanho chocolate",
            "Loiro mel",
            "Ruivo acobreado",
            "Caramelo",
            "Balayage natural"
        ],
        "dicas_estilo": [
            "Procure criar volume no topo",
            "Evite cortes muito retos",
            "Tons quentes realçam sua pele"
        ]
    }


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status")
async def get_ai_status():
    """Retorna status do sistema de IA"""
    return {
        "ai_demo_mode": True,
        "facial_analysis_enabled": False,
        "facial_analysis_available": False,
        "features": {
            "recommendations": True,
            "photo_analysis": False,
            "demo_mode": True
        },
        "message": "Sistema de IA em modo demo"
    }


@router.post("/analyze")
async def analyze_photo(
    current_user: Annotated[User, Depends(get_current_user)],
    file: Optional[UploadFile] = File(None),
    use_profile_photo: bool = False
):
    """
    Analisa foto e retorna recomendações (MODO DEMO)
    """
    
    print("🎭 Analisando foto em modo demo")
    
    # Salva a foto se foi enviada
    if file:
        file_location = os.path.join(UPLOAD_DIR, f"analysis_{current_user.id}_{file.filename}")
        try:
            contents = await file.read()
            with open(file_location, "wb") as f:
                f.write(contents)
            print(f"✅ Arquivo salvo: {file_location}")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    # Retorna recomendações demo
    recommendations = get_demo_recommendations()
    
    return {
        **recommendations,
        "user_id": current_user.id,
        "foto_analisada": file.filename if file else None
    }


@router.post("/suggestions")
async def get_ai_suggestions(
    current_user: Annotated[User, Depends(get_current_user)],
    file: Optional[UploadFile] = File(None)
):
    """
    Gera sugestões visuais (mockado)
    """
    
    if file:
        file_location = os.path.join(UPLOAD_DIR, f"suggestion_{current_user.id}_{file.filename}")
        contents = await file.read()
        with open(file_location, "wb") as f:
            f.write(contents)
        
        return {
            "user_id": current_user.id,
            "photo_ia_url": f"/static/uploads/suggestion_{current_user.id}_{file.filename}",
            "message": "Sugestão gerada! (Modo demo)",
            "note": "Em produção, usaria IA generativa para criar visualização"
        }
    
    raise HTTPException(status_code=400, detail="Nenhuma foto fornecida")


@router.get("/recommendations/{face_shape}/{skin_tone}")
async def get_recommendations_by_type(
    face_shape: str,
    skin_tone: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retorna recomendações por formato e tom específicos
    """
    
    # Recomendações por formato
    recommendations = {
        "oval": {
            "cuts": ["Praticamente qualquer estilo", "Long bob", "Franja lateral", "Pixie cut"],
            "colors": ["Qualquer tonalidade funciona bem"]
        },
        "redondo": {
            "cuts": ["Camadas longas", "Franja lateral assimétrica", "Long bob angular"],
            "colors": ["Tons que criem contraste"]
        },
        "quadrado": {
            "cuts": ["Ondas suaves", "Long bob ondulado", "Camadas no queixo"],
            "colors": ["Tons suaves"]
        }
    }
    
    # Pega as recomendações ou usa padrão
    format_recs = recommendations.get(face_shape.lower(), recommendations["oval"])
    
    return {
        "formato_rosto": face_shape,
        "tom_pele": skin_tone,
        "cortes_recomendados": format_recs["cuts"],
        "cores_recomendadas": format_recs["colors"],
        "dicas": ["Consulte um profissional", "Considere sua rotina", "Experimente gradualmente"]
    }


@router.get("/face-shapes")
async def get_available_face_shapes():
    """Lista formatos de rosto"""
    return {
        "face_shapes": ["oval", "redondo", "quadrado", "coração", "diamante", "oblongo"],
        "descriptions": {
            "oval": "Formato equilibrado",
            "redondo": "Largura e altura similares",
            "quadrado": "Mandíbula angular",
            "coração": "Testa larga, queixo pontiagudo",
            "diamante": "Maçãs proeminentes",
            "oblongo": "Rosto alongado"
        }
    }


@router.get("/skin-tones")
async def get_available_skin_tones():
    """Lista tons de pele"""
    return {
        "skin_tones": ["quente", "frio", "neutro"],
        "descriptions": {
            "quente": "Tons dourados, amarelados",
            "frio": "Tons rosados, azulados",
            "neutro": "Equilíbrio entre quente e frio"
        }
    }