"""
AI/HAIR_STYLE_AI.PY - ANÁLISE FACIAL COM IA E RECOMENDAÇÃO DE CABELO
======================================================================
Sistema completo de análise facial usando APIs gratuitas (Azure Face API ou Face++)
para recomendar cortes e cores de cabelo baseado em:
- Formato do rosto (oval, redondo, quadrado, coração, diamante, oblongo)
- Tom de pele (quente, frio, neutro)
- Características faciais
"""

import os
import base64
import json
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class FaceShape(Enum):
    """Tipos de formato de rosto"""
    OVAL = "oval"
    ROUND = "redondo"
    SQUARE = "quadrado"
    HEART = "coração"
    DIAMOND = "diamante"
    OBLONG = "oblongo"


class SkinTone(Enum):
    """Tons de pele"""
    WARM = "quente"
    COOL = "frio"
    NEUTRAL = "neutro"


@dataclass
class FaceAnalysis:
    """Resultado da análise facial"""
    face_shape: FaceShape
    skin_tone: SkinTone
    face_width: float
    face_height: float
    jawline_width: float
    forehead_width: float
    cheekbone_width: float
    confidence: float
    recommended_hairstyles: List[str]
    recommended_colors: List[str]
    style_tips: List[str]


class HairStyleRecommender:
    """Sistema de recomendação de cabelo baseado em análise facial"""
    
    # Dicionário de recomendações de corte por formato de rosto
    HAIRSTYLE_RECOMMENDATIONS = {
        FaceShape.OVAL: {
            "styles": [
                "Praticamente qualquer estilo funciona bem!",
                "Long bob (lob) com camadas",
                "Franja lateral",
                "Cabelo médio com ondas",
                "Pixie cut",
                "Rabo de cavalo alto"
            ],
            "avoid": ["Evite franjas muito pesadas que escondam a testa"],
            "tips": [
                "Seu formato oval é o mais versátil",
                "Experimente diferentes comprimentos",
                "Pode usar cabelo preso ou solto"
            ]
        },
        FaceShape.ROUND: {
            "styles": [
                "Corte em camadas longas (alonga o rosto)",
                "Franja lateral assimétrica",
                "Long bob (lob) angular",
                "Cabelo com volume no topo",
                "Ondas verticais",
                "Corte assimétrico"
            ],
            "avoid": [
                "Evite franjas retas horizontais",
                "Evite cortes muito curtos na altura do queixo",
                "Evite volume nas laterais"
            ],
            "tips": [
                "Procure criar altura e verticalidade",
                "Use cortes que alonguem o rosto",
                "Franjas laterais são suas amigas"
            ]
        },
        FaceShape.SQUARE: {
            "styles": [
                "Ondas suaves e românticas",
                "Long bob ondulado",
                "Camadas que começam no queixo",
                "Franja lateral longa",
                "Cabelo médio com movimento",
                "Corte em camadas texturizadas"
            ],
            "avoid": [
                "Evite cortes muito retos e geométricos",
                "Evite franjas horizontais pesadas",
                "Evite cabelo liso muito reto"
            ],
            "tips": [
                "Suavize os ângulos com ondas e camadas",
                "Volume nas laterais ajuda a equilibrar",
                "Evite cortes que enfatizem a mandíbula"
            ]
        },
        FaceShape.HEART: {
            "styles": [
                "Corte na altura do queixo (chin-length bob)",
                "Ondas na altura do queixo",
                "Franja lateral ou cortina",
                "Cabelo médio com camadas",
                "Volume na parte inferior",
                "Pixie cut com volume lateral"
            ],
            "avoid": [
                "Evite muito volume no topo",
                "Evite cabelo muito curto nas laterais",
                "Evite topete volumoso"
            ],
            "tips": [
                "Equilibre a testa larga com volume embaixo",
                "Frangas laterais ajudam a suavizar a testa",
                "Procure largura na altura do queixo"
            ]
        },
        FaceShape.DIAMOND: {
            "styles": [
                "Franja lateral ou cortina",
                "Bob texturizado",
                "Ondas volumosas",
                "Cabelo médio com camadas",
                "Volume nas laterais (na testa e queixo)",
                "Cortes que adicionem largura nas têmporas"
            ],
            "avoid": [
                "Evite muito volume nas maçãs do rosto",
                "Evite cabelo muito liso e puxado para trás",
                "Evite cortes que enfatizem as maçãs"
            ],
            "tips": [
                "Balance a largura das maçãs do rosto",
                "Adicione volume na testa e no queixo",
                "Franjas laterais são ideais"
            ]
        },
        FaceShape.OBLONG: {
            "styles": [
                "Franja que encurte o rosto",
                "Bob na altura do queixo",
                "Ondas horizontais",
                "Cabelo médio com camadas",
                "Volume nas laterais",
                "Corte shag (desfiado)"
            ],
            "avoid": [
                "Evite cabelo muito longo e liso",
                "Evite muito volume no topo",
                "Evite cabelo puxado para trás"
            ],
            "tips": [
                "Use franjas para encurtar o rosto",
                "Volume lateral é seu amigo",
                "Evite alongar ainda mais o rosto"
            ]
        }
    }
    
    # Recomendações de cores por tom de pele
    COLOR_RECOMMENDATIONS = {
        SkinTone.WARM: {
            "colors": [
                "Castanho dourado",
                "Mel",
                "Caramelo",
                "Loiro dourado",
                "Chocolate quente",
                "Ruivo cobre",
                "Mogno quente"
            ],
            "avoid": ["Tons muito frios ou acinzentados", "Loiro platinado"],
            "tips": [
                "Tons quentes e dourados realçam sua pele",
                "Considere mechas em tons mel ou caramelo",
                "Ruivos quentes ficam lindos em tons quentes"
            ]
        },
        SkinTone.COOL: {
            "colors": [
                "Castanho frio",
                "Loiro platinado",
                "Loiro cinza",
                "Preto azulado",
                "Borgonha",
                "Ruivo cereja",
                "Chocolate frio"
            ],
            "avoid": ["Tons muito dourados ou alaranjados"],
            "tips": [
                "Tons frios e acinzentados complementam sua pele",
                "Loiros platinados ficam incríveis",
                "Considere reflexos violeta ou azulados"
            ]
        },
        SkinTone.NEUTRAL: {
            "colors": [
                "Praticamente qualquer cor funciona!",
                "Castanho neutro",
                "Loiro natural",
                "Chocolate médio",
                "Ruivo natural",
                "Balayage natural",
                "Ombré suave"
            ],
            "avoid": ["Evite apenas cores muito extremas sem teste"],
            "tips": [
                "Você tem sorte - quase tudo fica bem!",
                "Experimente diferentes tons",
                "Balayage e ombré são ótimas opções"
            ]
        }
    }
    
    @staticmethod
    def calculate_face_shape(landmarks: Dict) -> FaceShape:
        """
        Calcula o formato do rosto baseado nos landmarks faciais
        
        Args:
            landmarks: Dicionário com pontos faciais (x, y)
            
        Returns:
            FaceShape identificado
        """
        # Extrair medidas principais
        face_length = landmarks.get('face_length', 0)
        face_width = landmarks.get('face_width', 0)
        forehead_width = landmarks.get('forehead_width', 0)
        jawline_width = landmarks.get('jawline_width', 0)
        cheekbone_width = landmarks.get('cheekbone_width', 0)
        
        # Calcular proporções
        if face_length == 0 or face_width == 0:
            return FaceShape.OVAL  # Default
        
        length_width_ratio = face_length / face_width
        
        # Lógica de classificação baseada em proporções
        if abs(length_width_ratio - 1.0) < 0.15:
            # Rosto mais redondo
            if cheekbone_width > forehead_width and cheekbone_width > jawline_width:
                return FaceShape.ROUND
            else:
                return FaceShape.SQUARE
        
        elif length_width_ratio > 1.5:
            # Rosto alongado
            return FaceShape.OBLONG
        
        elif forehead_width > cheekbone_width and cheekbone_width > jawline_width:
            # Testa larga, queixo estreito
            return FaceShape.HEART
        
        elif cheekbone_width > forehead_width and cheekbone_width > jawline_width:
            # Maçãs do rosto proeminentes
            return FaceShape.DIAMOND
        
        else:
            # Proporções equilibradas
            return FaceShape.OVAL
    
    @staticmethod
    def estimate_skin_tone(rgb_values: Optional[Dict] = None) -> SkinTone:
        """
        Estima o tom de pele (quente, frio ou neutro)
        
        Args:
            rgb_values: Valores RGB médios da pele (opcional)
            
        Returns:
            SkinTone estimado
        """
        if not rgb_values:
            return SkinTone.NEUTRAL  # Default se não houver dados
        
        r = rgb_values.get('r', 128)
        g = rgb_values.get('g', 128)
        b = rgb_values.get('b', 128)
        
        # Análise simplificada baseada em tons
        # Tom quente: mais vermelho/amarelo
        # Tom frio: mais azul
        
        yellow_ratio = (r + g) / (2 * (b + 1))  # +1 para evitar divisão por zero
        
        if yellow_ratio > 1.3:
            return SkinTone.WARM
        elif yellow_ratio < 0.9:
            return SkinTone.COOL
        else:
            return SkinTone.NEUTRAL
    
    @classmethod
    def get_recommendations(cls, face_shape: FaceShape, skin_tone: SkinTone) -> Dict:
        """
        Obtém recomendações de cabelo baseadas no formato do rosto e tom de pele
        
        Args:
            face_shape: Formato do rosto
            skin_tone: Tom de pele
            
        Returns:
            Dicionário com recomendações completas
        """
        hairstyle_rec = cls.HAIRSTYLE_RECOMMENDATIONS.get(face_shape, {})
        color_rec = cls.COLOR_RECOMMENDATIONS.get(skin_tone, {})
        
        return {
            "hairstyles": hairstyle_rec.get("styles", []),
            "avoid_styles": hairstyle_rec.get("avoid", []),
            "style_tips": hairstyle_rec.get("tips", []),
            "colors": color_rec.get("colors", []),
            "avoid_colors": color_rec.get("avoid", []),
            "color_tips": color_rec.get("tips", [])
        }


class AzureFaceAPI:
    """Cliente para Azure Face API (30.000 chamadas grátis/mês)"""
    
    def __init__(self, api_key: str, endpoint: str):
        """
        Inicializa o cliente Azure Face API
        
        Args:
            api_key: Chave da API Azure
            endpoint: URL do endpoint (ex: https://YOUR_REGION.api.cognitive.microsoft.com/)
        """
        self.api_key = api_key
        self.endpoint = endpoint.rstrip('/')
        self.headers = {
            'Ocp-Apim-Subscription-Key': api_key,
            'Content-Type': 'application/octet-stream'
        }
    
    def analyze_face(self, image_path: str) -> Dict:
        """
        Analisa uma imagem usando Azure Face API
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dicionário com dados da análise
        """
        url = f"{self.endpoint}/face/v1.0/detect"
        params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'true',
            'returnFaceAttributes': 'age,gender,headPose,facialHair,glasses'
        }
        
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        response = requests.post(
            url,
            params=params,
            headers=self.headers,
            data=image_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Azure API Error: {response.status_code} - {response.text}")


class FacePlusPlusAPI:
    """Cliente para Face++ API (versão gratuita disponível)"""
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Inicializa o cliente Face++ API
        
        Args:
            api_key: Chave da API Face++
            api_secret: Secret da API Face++
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api-us.faceplusplus.com/facepp/v3"
    
    def analyze_face(self, image_path: str) -> Dict:
        """
        Analisa uma imagem usando Face++ API
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dicionário com dados da análise
        """
        url = f"{self.base_url}/detect"
        
        with open(image_path, 'rb') as image_file:
            files = {'image_file': image_file}
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'return_landmark': '2',  # 106 pontos
                'return_attributes': 'gender,age,skinstatus'
            }
            
            response = requests.post(url, data=data, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Face++ API Error: {response.status_code} - {response.text}")


class FaceAnalyzer:
    """Analisador facial principal que integra APIs e recomendações"""
    
    def __init__(self, api_provider: str = "azure", **api_credentials):
        """
        Inicializa o analisador facial
        
        Args:
            api_provider: "azure" ou "facepp"
            **api_credentials: Credenciais da API escolhida
                Para Azure: api_key, endpoint
                Para Face++: api_key, api_secret
        """
        self.api_provider = api_provider.lower()
        
        if self.api_provider == "azure":
            self.api_client = AzureFaceAPI(
                api_key=api_credentials.get('api_key'),
                endpoint=api_credentials.get('endpoint')
            )
        elif self.api_provider == "facepp":
            self.api_client = FacePlusPlusAPI(
                api_key=api_credentials.get('api_key'),
                api_secret=api_credentials.get('api_secret')
            )
        else:
            raise ValueError("API provider deve ser 'azure' ou 'facepp'")
        
        self.recommender = HairStyleRecommender()
    
    def _extract_landmarks_azure(self, api_response: Dict) -> Dict:
        """Extrai landmarks da resposta Azure"""
        if not api_response or len(api_response) == 0:
            raise ValueError("Nenhum rosto detectado na imagem")
        
        face = api_response[0]
        landmarks = face.get('faceLandmarks', {})
        
        # Calcular medidas baseadas nos landmarks
        pupil_left = landmarks.get('pupilLeft', {})
        pupil_right = landmarks.get('pupilRight', {})
        nose_tip = landmarks.get('noseTip', {})
        upper_lip_top = landmarks.get('upperLipTop', {})
        under_lip_bottom = landmarks.get('underLipBottom', {})
        
        # Estimativas de largura e altura
        if pupil_left and pupil_right:
            face_width = abs(pupil_right.get('x', 0) - pupil_left.get('x', 0)) * 2.5
        else:
            face_width = 100  # Default
        
        if nose_tip and under_lip_bottom:
            face_height = abs(under_lip_bottom.get('y', 0) - nose_tip.get('y', 0)) * 3.5
        else:
            face_height = 150  # Default
        
        return {
            'face_width': face_width,
            'face_height': face_height,
            'forehead_width': face_width * 0.9,
            'jawline_width': face_width * 0.85,
            'cheekbone_width': face_width * 1.0,
            'face_length': face_height
        }
    
    def _extract_landmarks_facepp(self, api_response: Dict) -> Dict:
        """Extrai landmarks da resposta Face++"""
        if 'faces' not in api_response or len(api_response['faces']) == 0:
            raise ValueError("Nenhum rosto detectado na imagem")
        
        face = api_response['faces'][0]
        landmarks = face.get('landmark', {})
        face_rect = face.get('face_rectangle', {})
        
        # Usar dimensões do retângulo facial
        face_width = face_rect.get('width', 100)
        face_height = face_rect.get('height', 150)
        
        # Calcular proporções das diferentes áreas
        return {
            'face_width': face_width,
            'face_height': face_height,
            'forehead_width': face_width * 0.9,
            'jawline_width': face_width * 0.85,
            'cheekbone_width': face_width * 1.0,
            'face_length': face_height
        }
    
    def _extract_skin_tone_azure(self, api_response: Dict) -> Optional[Dict]:
        """Extrai informações de tom de pele da resposta Azure (limitado)"""
        # Azure Face API não fornece cor de pele diretamente
        # Retorna None para usar estimativa padrão
        return None
    
    def _extract_skin_tone_facepp(self, api_response: Dict) -> Optional[Dict]:
        """Extrai informações de tom de pele da resposta Face++"""
        if 'faces' not in api_response or len(api_response['faces']) == 0:
            return None
        
        face = api_response['faces'][0]
        skin_status = face.get('attributes', {}).get('skinstatus', {})
        
        # Face++ fornece informações sobre pele, mas não RGB direto
        # Usar valores padrão baseados em características
        return None  # Usar estimativa padrão
    
    def analyze_and_recommend(self, image_path: str) -> FaceAnalysis:
        """
        Analisa uma foto e retorna recomendações completas de cabelo
        
        Args:
            image_path: Caminho para a imagem do rosto
            
        Returns:
            FaceAnalysis com todas as recomendações
        """
        # Validar arquivo
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
        
        # Chamar API
        print(f"Analisando imagem com {self.api_provider.upper()}...")
        api_response = self.api_client.analyze_face(image_path)
        
        # Extrair landmarks baseado na API
        if self.api_provider == "azure":
            landmarks = self._extract_landmarks_azure(api_response)
            skin_rgb = self._extract_skin_tone_azure(api_response)
        else:  # facepp
            landmarks = self._extract_landmarks_facepp(api_response)
            skin_rgb = self._extract_skin_tone_facepp(api_response)
        
        # Calcular formato do rosto
        face_shape = self.recommender.calculate_face_shape(landmarks)
        print(f"Formato do rosto detectado: {face_shape.value}")
        
        # Estimar tom de pele
        skin_tone = self.recommender.estimate_skin_tone(skin_rgb)
        print(f"Tom de pele estimado: {skin_tone.value}")
        
        # Obter recomendações
        recommendations = self.recommender.get_recommendations(face_shape, skin_tone)
        
        # Criar resultado
        analysis = FaceAnalysis(
            face_shape=face_shape,
            skin_tone=skin_tone,
            face_width=landmarks['face_width'],
            face_height=landmarks['face_height'],
            jawline_width=landmarks['jawline_width'],
            forehead_width=landmarks['forehead_width'],
            cheekbone_width=landmarks['cheekbone_width'],
            confidence=0.85,  # Placeholder
            recommended_hairstyles=recommendations['hairstyles'],
            recommended_colors=recommendations['colors'],
            style_tips=recommendations['style_tips'] + recommendations['color_tips']
        )
        
        return analysis


def analyze_face_for_hairstyle(
    image_path: str,
    api_provider: str = "azure",
    **api_credentials
) -> FaceAnalysis:
    """
    Função principal para analisar rosto e obter recomendações de cabelo
    
    Args:
        image_path: Caminho para a imagem do rosto
        api_provider: "azure" ou "facepp"
        **api_credentials: Credenciais da API
            Para Azure: api_key="...", endpoint="https://..."
            Para Face++: api_key="...", api_secret="..."
    
    Returns:
        FaceAnalysis com recomendações completas
    
    Exemplo de uso:
        # Usando Azure Face API
        result = analyze_face_for_hairstyle(
            "minha_foto.jpg",
            api_provider="azure",
            api_key="SUA_CHAVE_AZURE",
            endpoint="https://REGIAO.api.cognitive.microsoft.com/"
        )
        
        # Usando Face++
        result = analyze_face_for_hairstyle(
            "minha_foto.jpg",
            api_provider="facepp",
            api_key="SUA_CHAVE_FACEPP",
            api_secret="SEU_SECRET_FACEPP"
        )
        
        print(f"Formato: {result.face_shape.value}")
        print(f"Tom de pele: {result.skin_tone.value}")
        print(f"Cortes recomendados: {result.recommended_hairstyles}")
        print(f"Cores recomendadas: {result.recommended_colors}")
    """
    analyzer = FaceAnalyzer(api_provider=api_provider, **api_credentials)
    return analyzer.analyze_and_recommend(image_path)


def print_analysis_report(analysis: FaceAnalysis):
    """
    Imprime um relatório formatado da análise
    
    Args:
        analysis: Resultado da análise facial
    """
    print("\n" + "="*70)
    print("📊 RELATÓRIO DE ANÁLISE FACIAL E RECOMENDAÇÕES DE CABELO")
    print("="*70)
    
    print(f"\n🔍 ANÁLISE FACIAL:")
    print(f"   Formato do rosto: {analysis.face_shape.value.upper()}")
    print(f"   Tom de pele: {analysis.skin_tone.value.upper()}")
    print(f"   Confiança: {analysis.confidence * 100:.1f}%")
    
    print(f"\n📏 MEDIDAS:")
    print(f"   Largura do rosto: {analysis.face_width:.1f}px")
    print(f"   Altura do rosto: {analysis.face_height:.1f}px")
    print(f"   Largura da testa: {analysis.forehead_width:.1f}px")
    print(f"   Largura do maxilar: {analysis.jawline_width:.1f}px")
    
    print(f"\n💇 CORTES RECOMENDADOS:")
    for i, style in enumerate(analysis.recommended_hairstyles, 1):
        print(f"   {i}. {style}")
    
    print(f"\n🎨 CORES RECOMENDADAS:")
    for i, color in enumerate(analysis.recommended_colors, 1):
        print(f"   {i}. {color}")
    
    print(f"\n💡 DICAS DE ESTILO:")
    for i, tip in enumerate(analysis.style_tips, 1):
        print(f"   {i}. {tip}")
    
    print("\n" + "="*70 + "\n")


# Função de compatibilidade com o código existente
def edit_hair_style(file_path: str, style: str = "auto") -> bytes:
    """
    Função de compatibilidade com a API original.
    Analisa o rosto e retorna a imagem original com análise impressa.
    
    Args:
        file_path: Caminho para a imagem
        style: Não usado (mantido para compatibilidade)
    
    Returns:
        Bytes da imagem original
    """
    file_path = file_path.replace("\\", "/")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    # Nota: Para usar análise real, configure as credenciais da API
    print("\n⚠️  MODO DEMO - Configure as credenciais da API para análise real")
    print("Exemplo de configuração no código:")
    print("""
    from hair_style_ai import analyze_face_for_hairstyle, print_analysis_report
    
    # Para Azure Face API (grátis: 30.000 chamadas/mês)
    result = analyze_face_for_hairstyle(
        "foto.jpg",
        api_provider="azure",
        api_key="SUA_CHAVE",
        endpoint="https://REGIAO.api.cognitive.microsoft.com/"
    )
    
    # Para Face++ (grátis com limitações)
    result = analyze_face_for_hairstyle(
        "foto.jpg",
        api_provider="facepp",
        api_key="SUA_CHAVE",
        api_secret="SEU_SECRET"
    )
    
    print_analysis_report(result)
    """)
    
    with open(file_path, "rb") as f:
        return f.read()


if __name__ == "__main__":
    # Exemplo de uso
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  Sistema de Análise Facial e Recomendação de Cabelo com IA      ║
    ║  Usando Azure Face API ou Face++ (ambas com tiers gratuitos)    ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    📋 INSTRUÇÕES DE USO:
    
    1️⃣  OBTER CREDENCIAIS GRATUITAS:
    
       OPÇÃO A - Azure Face API (RECOMENDADO):
       • Acesse: https://portal.azure.com
       • Crie uma conta gratuita (cartão necessário, mas não cobra)
       • Crie um recurso "Face" em Cognitive Services
       • Copie a chave e o endpoint
       • GRÁTIS: 30.000 transações/mês
       
       OPÇÃO B - Face++ API:
       • Acesse: https://www.faceplusplus.com
       • Crie uma conta gratuita
       • Obtenha API Key e API Secret no console
       • GRÁTIS: uso limitado, sem custo
    
    2️⃣  USAR NO CÓDIGO:
    
       # Azure
       from hair_style_ai import analyze_face_for_hairstyle, print_analysis_report
       
       result = analyze_face_for_hairstyle(
           "sua_foto.jpg",
           api_provider="azure",
           api_key="sua_chave_azure",
           endpoint="https://sua-regiao.api.cognitive.microsoft.com/"
       )
       
       print_analysis_report(result)
    
    3️⃣  RESULTADO:
       • Formato do rosto identificado
       • Tom de pele analisado
       • Lista de cortes recomendados
       • Lista de cores recomendadas
       • Dicas personalizadas de estilo
    
    💡 DICA: Tire uma foto de frente, bem iluminada, sem óculos!
    """)