"""
TESTE DEMO - Sistema de Análise Facial (SEM API)
================================================
Este arquivo demonstra como o sistema funciona sem precisar de uma API real.
Útil para testar a estrutura antes de configurar as credenciais.
"""

from hair_style_ai import (
    FaceShape, 
    SkinTone, 
    HairStyleRecommender,
    FaceAnalysis
)


def demo_analise_completa():
    """Demonstra uma análise completa com dados simulados"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          DEMO - Sistema de Análise Facial e Cabelo            ║
    ║                  (Funcionando sem API)                         ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Simular diferentes tipos de análises
    cenarios = [
        {
            "nome": "Pessoa 1 - Rosto Oval, Tom Quente",
            "face_shape": FaceShape.OVAL,
            "skin_tone": SkinTone.WARM
        },
        {
            "nome": "Pessoa 2 - Rosto Redondo, Tom Frio",
            "face_shape": FaceShape.ROUND,
            "skin_tone": SkinTone.COOL
        },
        {
            "nome": "Pessoa 3 - Rosto Quadrado, Tom Neutro",
            "face_shape": FaceShape.SQUARE,
            "skin_tone": SkinTone.NEUTRAL
        },
        {
            "nome": "Pessoa 4 - Rosto Coração, Tom Quente",
            "face_shape": FaceShape.HEART,
            "skin_tone": SkinTone.WARM
        }
    ]
    
    recommender = HairStyleRecommender()
    
    for cenario in cenarios:
        print(f"\n{'='*70}")
        print(f"📊 {cenario['nome']}")
        print('='*70)
        
        # Obter recomendações
        recomendacoes = recommender.get_recommendations(
            cenario['face_shape'],
            cenario['skin_tone']
        )
        
        # Exibir resultados
        print(f"\n🔍 ANÁLISE:")
        print(f"   Formato do rosto: {cenario['face_shape'].value.upper()}")
        print(f"   Tom de pele: {cenario['skin_tone'].value.upper()}")
        
        print(f"\n💇 CORTES RECOMENDADOS:")
        for i, estilo in enumerate(recomendacoes['hairstyles'][:4], 1):
            print(f"   {i}. {estilo}")
        
        print(f"\n🎨 CORES RECOMENDADAS:")
        for i, cor in enumerate(recomendacoes['colors'][:4], 1):
            print(f"   {i}. {cor}")
        
        print(f"\n💡 PRINCIPAIS DICAS:")
        for i, dica in enumerate(recomendacoes['style_tips'][:2], 1):
            print(f"   {i}. {dica}")
        
        print(f"\n⚠️  EVITE:")
        for evitar in recomendacoes['avoid_styles'][:2]:
            print(f"   • {evitar}")


def demo_todos_formatos():
    """Mostra recomendações para todos os formatos de rosto"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║      GUIA COMPLETO: CORTES PARA CADA FORMATO DE ROSTO         ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    recommender = HairStyleRecommender()
    
    for formato in FaceShape:
        print(f"\n{'='*70}")
        print(f"✨ FORMATO: {formato.value.upper()}")
        print('='*70)
        
        recomendacoes = recommender.get_recommendations(formato, SkinTone.NEUTRAL)
        
        print(f"\n✂️ MELHORES CORTES:")
        for i, estilo in enumerate(recomendacoes['hairstyles'], 1):
            print(f"   {i}. {estilo}")
        
        print(f"\n💡 DICAS:")
        for dica in recomendacoes['style_tips']:
            print(f"   • {dica}")
        
        print(f"\n❌ EVITE:")
        for evitar in recomendacoes['avoid_styles']:
            print(f"   • {evitar}")


def demo_todas_cores():
    """Mostra recomendações de cor para cada tom de pele"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         GUIA COMPLETO: CORES PARA CADA TOM DE PELE            ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    recommender = HairStyleRecommender()
    
    for tom in SkinTone:
        print(f"\n{'='*70}")
        print(f"🌈 TOM DE PELE: {tom.value.upper()}")
        print('='*70)
        
        recomendacoes = recommender.get_recommendations(FaceShape.OVAL, tom)
        
        print(f"\n🎨 MELHORES CORES:")
        for i, cor in enumerate(recomendacoes['colors'], 1):
            print(f"   {i}. {cor}")
        
        print(f"\n💡 DICAS:")
        for dica in recomendacoes['color_tips']:
            print(f"   • {dica}")
        
        if recomendacoes['avoid_colors']:
            print(f"\n❌ EVITE:")
            for evitar in recomendacoes['avoid_colors']:
                print(f"   • {evitar}")


def demo_calculadora_formato():
    """Demonstra como o sistema calcula o formato do rosto"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║      COMO O SISTEMA CALCULA O FORMATO DO ROSTO                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("\n📐 O sistema analisa as seguintes medidas:")
    print("   • Comprimento do rosto (testa ao queixo)")
    print("   • Largura do rosto (lateral a lateral)")
    print("   • Largura da testa")
    print("   • Largura das maçãs do rosto")
    print("   • Largura do maxilar")
    
    print("\n🔍 Exemplos de classificação:")
    
    exemplos = [
        {
            "medidas": {
                "face_length": 200,
                "face_width": 150,
                "forehead_width": 140,
                "cheekbone_width": 150,
                "jawline_width": 135
            },
            "descricao": "Rosto equilibrado, levemente mais longo que largo"
        },
        {
            "medidas": {
                "face_length": 150,
                "face_width": 150,
                "forehead_width": 140,
                "cheekbone_width": 155,
                "jawline_width": 145
            },
            "descricao": "Comprimento e largura similares, linhas suaves"
        }
    ]
    
    recommender = HairStyleRecommender()
    
    for i, exemplo in enumerate(exemplos, 1):
        print(f"\n{'='*70}")
        print(f"Exemplo {i}: {exemplo['descricao']}")
        print('='*70)
        
        print("\n   Medidas:")
        for medida, valor in exemplo['medidas'].items():
            print(f"   • {medida}: {valor}px")
        
        formato = recommender.calculate_face_shape(exemplo['medidas'])
        print(f"\n   → Formato detectado: {formato.value.upper()}")


def demo_quiz_interativo():
    """Quiz interativo para descobrir formato de rosto manualmente"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║           QUIZ: DESCUBRA SEU FORMATO DE ROSTO                 ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nResponda as perguntas para descobrir seu formato de rosto:\n")
    
    print("1. Seu rosto é mais COMPRIDO ou mais LARGO?")
    print("   a) Muito mais comprido que largo")
    print("   b) Levemente mais comprido")
    print("   c) Comprimento e largura similares")
    q1 = input("   Resposta (a/b/c): ").strip().lower()
    
    print("\n2. Qual parte do seu rosto é mais LARGA?")
    print("   a) Testa")
    print("   b) Maçãs do rosto")
    print("   c) Maxilar")
    print("   d) Todas são parecidas")
    q2 = input("   Resposta (a/b/c/d): ").strip().lower()
    
    print("\n3. Como é seu MAXILAR?")
    print("   a) Angular e quadrado")
    print("   b) Arredondado")
    print("   c) Pontiagudo/estreito")
    q3 = input("   Resposta (a/b/c): ").strip().lower()
    
    # Lógica simples de classificação
    formato = None
    
    if q1 == 'a':
        formato = FaceShape.OBLONG
    elif q1 == 'c':
        if q3 == 'a':
            formato = FaceShape.SQUARE
        else:
            formato = FaceShape.ROUND
    else:  # q1 == 'b'
        if q2 == 'a':
            formato = FaceShape.HEART
        elif q2 == 'b':
            formato = FaceShape.DIAMOND
        else:
            formato = FaceShape.OVAL
    
    if not formato:
        formato = FaceShape.OVAL
    
    print(f"\n{'='*70}")
    print(f"✨ SEU FORMATO DE ROSTO: {formato.value.upper()}")
    print('='*70)
    
    recommender = HairStyleRecommender()
    recomendacoes = recommender.get_recommendations(formato, SkinTone.NEUTRAL)
    
    print(f"\n💇 CORTES IDEAIS PARA VOCÊ:")
    for i, estilo in enumerate(recomendacoes['hairstyles'][:5], 1):
        print(f"   {i}. {estilo}")
    
    print(f"\n💡 DICAS:")
    for dica in recomendacoes['style_tips']:
        print(f"   • {dica}")


def menu_principal():
    """Menu principal do demo"""
    
    while True:
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    DEMO - MENU PRINCIPAL                       ║
╚════════════════════════════════════════════════════════════════╝

Escolha uma opção:

1. 📊 Ver análises de exemplo (vários formatos)
2. 📖 Guia completo: Cortes para cada formato de rosto
3. 🎨 Guia completo: Cores para cada tom de pele
4. 🔬 Como o sistema calcula o formato do rosto
5. 🎯 Quiz interativo: Descubra seu formato de rosto
6. ❌ Sair

        """)
        
        escolha = input("Digite o número da opção: ").strip()
        
        if escolha == '1':
            demo_analise_completa()
        elif escolha == '2':
            demo_todos_formatos()
        elif escolha == '3':
            demo_todas_cores()
        elif escolha == '4':
            demo_calculadora_formato()
        elif escolha == '5':
            demo_quiz_interativo()
        elif escolha == '6':
            print("\n👋 Até logo! Configure suas credenciais API para análise real.")
            break
        else:
            print("\n❌ Opção inválida! Tente novamente.")
        
        input("\n\nPressione ENTER para continuar...")
        print("\n" * 2)


if __name__ == "__main__":
    menu_principal()