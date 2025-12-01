"""
ROUTES/AI.PY - INTELIGÊNCIA ARTIFICIAL INTEGRADA
================================================
Sistema completo de IA com fallback para modo demo
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Annotated, Optional, List
import os

from app.database import db
from app.auth import get_current_user
from app.models import User

# Importa configuração
try:
    from app.config import config, is_feature_enabled, get_api_credential
except ImportError:
    print("⚠️ Módulo config não encontrado. Criando configuração padrão...")
    # Configuração padrão inline
    class DefaultConfig:
        class Features:
            facial_analysis_enabled = False
            ai_hair_suggestions_enabled = True
            ai_demo_mode = True
        
        class Credentials:
            azure_face_api_key = ""
            azure_face_endpoint = ""
            facepp_api_key = ""
            facepp_api_secret = ""
        
        features = Features()
        credentials = Credentials()
    
    config = DefaultConfig()
    
    def is_feature_enabled(feature_name: str) -> bool:
        return getattr(config.features, feature_name, False)
    
    def get_api_credential(credential_name: str) -> str:
        return getattr(config.credentials, credential_name, "")

# Tenta importar sistema de análise facial
FACIAL_ANALYSIS_AVAILABLE = False
try:
    if is_feature_enabled("facial_analysis_enabled"):
        from hair_style_ai import (
            analyze_face_for_hairstyle,
            FaceShape,
            SkinTone,
            HairStyleRecommender
        )
        FACIAL_ANALYSIS_AVAILABLE = True
        print("✅ Sistema de análise facial carregado")
except ImportError:
    print("⚠️ Sistema de análise facial não disponível. Usando modo demo.")
    
    # Define classes mockadas para modo demo
    from enum import Enum
    
    class FaceShape(str, Enum):
        OVAL = "oval"
        ROUND = "redondo"
        SQUARE = "quadrado"
        HEART = "coração"
        DIAMOND = "diamante"
        OBLONG = "oblongo"
    
    class SkinTone(str, Enum):
        WARM = "quente"
        COOL = "frio"
        NEUTRAL = "neutro"
    
    class HairStyleRecommender:
        @staticmethod
        def get_recommendations(face_shape, skin_tone):
            # Recomendações mockadas
            return {
                "hairstyles": [
                    "Corte em camadas médias",
                    "Bob assimétrico",
                    "Franja lateral",
                    "Long bob (lob)",
                    "Ondas suaves"
                ],
                "colors": [
                    "Castanho chocolate",
                    "Loiro mel",
                    "Ruivo acobreado",
                    "Caramelo",
                    "Balayage natural"
                ],
                "style_tips": [
                    "Procure criar volume no topo",
                    "Evite cortes muito retos",
                    "Tons quentes realçam sua pele"
                ],
                "avoid_styles": [
                    "Evite franjas pesadas",
                    "Evite volume lateral excessivo"
                ],
                "avoid_colors": [
                    "Evite tons muito frios"
                ]
            }

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_demo_recommendations(user_data: dict = None) -> dict:
    """
    Retorna recomendações demo sem usar APIs
    """
    recommender = HairStyleRecommender()
    
    # Usa formato oval e tom neutro como padrão
    face_shape = FaceShape.OVAL
    skin_tone = SkinTone.NEUTRAL
    
    recommendations = recommender.get_recommendations(face_shape, skin_tone)
    
    return {
        "modo": "demo",
        "formato_rosto": face_shape.value if hasattr(face_shape, 'value') else str(face_shape),
        "tom_pele": skin_tone.value if hasattr(skin_tone, 'value') else str(skin_tone),
        "confianca": 0.0,
        "message": "Recomendações em modo demo. Habilite análise facial para resultados personalizados.",
        "cortes_sugeridos": recommendations["hairstyles"][:5],
        "cores_sugeridas": recommendations["colors"][:5],
        "dicas_estilo": recommendations["style_tips"][:3],
        "evitar_cortes": recommendations["avoid_styles"][:2] if recommendations.get("avoid_styles") else [],
        "evitar_cores": recommendations["avoid_colors"][:2] if recommendations.get("avoid_colors") else []
    }


def analyze_photo_with_ai(file_path: str) -> dict:
    """
    Analisa foto com IA real (Azure ou Face++)
    """
    if not FACIAL_ANALYSIS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Sistema de análise facial não está configurado. Use modo demo."
        )
    
    # Obtém credenciais
    api_provider = "azure"  # ou "facepp"
    
    if api_provider == "azure":
        api_key = get_api_credential("azure_face_api_key")
        endpoint = get_api_credential("azure_face_endpoint")
        
        if not api_key or not endpoint:
            raise HTTPException(
                status_code=503,
                detail="Credenciais Azure não configuradas. Use modo demo ou configure em config.py"
            )
        
        # Analisa com Azure
        result = analyze_face_for_hairstyle(
            image_path=file_path,
            api_provider="azure",
            api_key=api_key,
            endpoint=endpoint
        )
    
    else:  # facepp
        api_key = get_api_credential("facepp_api_key")
        api_secret = get_api_credential("facepp_api_secret")
        
        if not api_key or not api_secret:
            raise HTTPException(
                status_code=503,
                detail="Credenciais Face++ não configuradas. Use modo demo ou configure em config.py"
            )
        
        result = analyze_face_for_hairstyle(
            image_path=file_path,
            api_provider="facepp",
            api_key=api_key,
            api_secret=api_secret
        )
    
    return {
        "modo": "ia_real",
        "formato_rosto": result.face_shape.value,
        "tom_pele": result.skin_tone.value,
        "confianca": result.confidence,
        "medidas": {
            "largura_rosto": result.face_width,
            "altura_rosto": result.face_height,
            "largura_testa": result.forehead_width,
            "largura_maxilar": result.jawline_width
        },
        "cortes_sugeridos": result.recommended_hairstyles,
        "cores_sugeridas": result.recommended_colors,
        "dicas_estilo": result.style_tips
    }


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status")
async def get_ai_status():
    """
    Retorna status das funcionalidades de IA
    """
    return {
        "ai_demo_mode": config.features.ai_demo_mode if hasattr(config.features, 'ai_demo_mode') else True,
        "facial_analysis_enabled": config.features.facial_analysis_enabled if hasattr(config.features, 'facial_analysis_enabled') else False,
        "facial_analysis_available": FACIAL_ANALYSIS_AVAILABLE,
        "features": {
            "recommendations": True,
            "photo_analysis": FACIAL_ANALYSIS_AVAILABLE,
            "demo_mode": config.features.ai_demo_mode if hasattr(config.features, 'ai_demo_mode') else True
        },
        "message": "Sistema de IA em modo demo" if not FACIAL_ANALYSIS_AVAILABLE else "Sistema de IA operacional"
    }


@router.post("/analyze")
async def analyze_photo(
    current_user: Annotated[User, Depends(get_current_user)],
    file: Optional[UploadFile] = File(None),
    use_profile_photo: bool = False
):
    """
    Analisa foto e retorna recomendações de cabelo.
    
    Modos:
    - Demo: Retorna recomendações genéricas
    - IA Real: Usa Azure/Face++ para análise personalizada
    """
    
    # Verifica se IA está habilitada
    ai_enabled = config.features.ai_hair_suggestions_enabled if hasattr(config.features, 'ai_hair_suggestions_enabled') else True
    
    if not ai_enabled:
        raise HTTPException(
            status_code=503,
            detail="Sistema de IA está desabilitado. Contate o administrador."
        )
    
    # Modo demo - sem análise real
    demo_mode = config.features.ai_demo_mode if hasattr(config.features, 'ai_demo_mode') else True
    
    if demo_mode or not FACIAL_ANALYSIS_AVAILABLE:
        print("🎭 Usando modo demo")
        recommendations = get_demo_recommendations()
        
        return {
            **recommendations,
            "user_id": current_user.id,
            "foto_analisada": None
        }
    
    # Modo IA real - requer foto
    file_location = None
    
    # 1. Determina qual foto usar
    if file:
        # Salva foto enviada
        file_location = os.path.join(UPLOAD_DIR, f"analysis_{current_user.id}_{file.filename}")
        try:
            contents = await file.read()
            with open(file_location, "wb") as f:
                f.write(contents)
            print(f"✅ Arquivo salvo: {file_location}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao salvar arquivo: {str(e)}"
            )
    
    elif use_profile_photo:
        # Usa foto de perfil
        db_user = db.get_user_by_id(current_user.id)
        if not db_user or not db_user.get("foto_perfil"):
            raise HTTPException(
                status_code=400,
                detail="Nenhuma foto de perfil encontrada. Envie uma foto ou faça upload do perfil."
            )
        file_location = db_user["foto_perfil"]
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma foto fornecida. Envie uma foto ou use a foto de perfil."
        )
    
    # 2. Verifica se arquivo existe
    if not os.path.exists(file_location):
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo não encontrado: {file_location}"
        )
    
    # 3. Analisa com IA
    try:
        print(f"🤖 Analisando foto com IA: {file_location}")
        analysis_result = analyze_photo_with_ai(file_location)
        
        return {
            **analysis_result,
            "user_id": current_user.id,
            "foto_analisada": file_location
        }
    
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")
        # Fallback para modo demo em caso de erro
        print("🎭 Fallback para modo demo")
        recommendations = get_demo_recommendations()
        return {
            **recommendations,
            "user_id": current_user.id,
            "foto_analisada": file_location,
            "error": str(e)
        }


@router.post("/suggestions")
async def get_ai_suggestions(
    current_user: Annotated[User, Depends(get_current_user)],
    file: Optional[UploadFile] = File(None),
    style: str = "corte moderno",
    servicos_selecionados: List[str] = []
):
    """
    Gera sugestões visuais de cabelo (imagem mockada por enquanto).
    
    Em produção, usaria um modelo generativo (DALL-E, Stable Diffusion, etc)
    """
    
    # Verifica se IA está habilitada
    ai_enabled = config.features.ai_hair_suggestions_enabled if hasattr(config.features, 'ai_hair_suggestions_enabled') else True
    
    if not ai_enabled:
        raise HTTPException(
            status_code=503,
            detail="Sugestões de IA estão desabilitadas"
        )
    
    # 1. Busca usuário
    db_user = db.get_user_by_id(current_user.id)
    
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    
    # 2. Decide qual foto usar
    file_location = None
    
    if file:
        file_location = os.path.join(UPLOAD_DIR, f"suggestion_{current_user.id}_{file.filename}")
        try:
            contents = await file.read()
            with open(file_location, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao salvar arquivo: {str(e)}"
            )
    elif db_user.get("foto_perfil"):
        file_location = db_user["foto_perfil"]
    else:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma foto fornecida ou foto de perfil não encontrada"
        )
    
    # 3. Verifica se arquivo existe
    if not os.path.exists(file_location):
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo não encontrado: {file_location}"
        )
    
    # 4. Por enquanto, apenas retorna a imagem original
    # Em produção, chamaria um modelo generativo
    with open(file_location, "rb") as f:
        image_bytes = f.read()
    
    # 5. Salva "sugestão" (por enquanto é a mesma imagem)
    output_filename = f"ai_suggestion_{current_user.id}_{os.path.basename(file_location)}"
    output_path = os.path.join(UPLOAD_DIR, output_filename)
    
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    
    return {
        "user_id": current_user.id,
        "style": style,
        "servicos": servicos_selecionados,
        "photo_ia_url": f"/static/uploads/{output_filename}",
        "message": "Sugestão gerada com sucesso! (Modo demo - em produção usaria IA generativa)",
        "note": "Esta é uma versão demo. Configure um modelo generativo para resultados reais."
    }


@router.get("/recommendations/{face_shape}/{skin_tone}")
async def get_recommendations_by_type(
    face_shape: str,
    skin_tone: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retorna recomendações para um formato de rosto e tom de pele específicos
    """
    
    try:
        # Converte strings para enums
        face_shape_enum = FaceShape[face_shape.upper().replace('Ã', 'A').replace('Ã‡', 'C')]
        skin_tone_enum = SkinTone[skin_tone.upper()]
        
        # Obtém recomendações
        recommender = HairStyleRecommender()
        recommendations = recommender.get_recommendations(face_shape_enum, skin_tone_enum)
        
        return {
            "formato_rosto": face_shape,
            "tom_pele": skin_tone,
            "cortes_recomendados": recommendations["hairstyles"],
            "cores_recomendadas": recommendations["colors"],
            "dicas": recommendations["style_tips"],
            "evitar_cortes": recommendations.get("avoid_styles", []),
            "evitar_cores": recommendations.get("avoid_colors", [])
        }
    
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail="Formato de rosto ou tom de pele inválido. "
                   "Formatos válidos: oval, round, square, heart, diamond, oblong. "
                   "Tons válidos: warm, cool, neutral"
        )


@router.get("/face-shapes")
async def get_available_face_shapes():
    """Lista todos os formatos de rosto disponíveis"""
    return {
        "face_shapes": [shape.value for shape in FaceShape],
        "descriptions": {
            "oval": "Formato equilibrado, mais longo que largo",
            "redondo": "Largura e altura similares, linhas suaves",
            "quadrado": "Mandíbula angular, testa e maxilar largos",
            "coração": "Testa larga, queixo pontiagudo",
            "diamante": "Maçãs do rosto proeminentes",
            "oblongo": "Rosto mais alongado"
        }
    }


@router.get("/skin-tones")
async def get_available_skin_tones():
    """Lista todos os tons de pele disponíveis"""
    return {
        "skin_tones": [tone.value for tone in SkinTone],
        "descriptions": {
            "quente": "Tons dourados, amarelados",
            "frio": "Tons rosados, azulados",
            "neutro": "Equilíbrio entre quente e frio"
        }
    }