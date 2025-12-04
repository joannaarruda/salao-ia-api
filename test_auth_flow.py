#!/usr/bin/env python3
"""
TEST_AUTH_FLOW.PY
==================
Script para testar todo o fluxo de autenticação
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """Testa registro de novo usuário"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: REGISTRO DE NOVO USUÁRIO")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_email = f"teste_cliente_{timestamp}@test.com"
    test_password = "senha123"
    test_nome = f"Cliente Teste {timestamp}"
    
    payload = {
        "nome": test_nome,
        "email": test_email,
        "senha": test_password
    }
    
    print(f"\n📝 Dados: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("✅ Registro bem-sucedido!")
            return test_email, test_password
        else:
            print("❌ Falha no registro")
            return None, None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None, None


def test_login(email, password):
    """Testa login de usuário"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: LOGIN DE USUÁRIO")
    print("="*60)
    
    print(f"\n📧 Email: {email}")
    print(f"🔐 Senha: {'*' * len(password)}")
    
    # Form data para OAuth2PasswordRequestForm
    form_data = {
        'username': email,
        'password': password
    }
    
    print(f"\n📤 Enviando: {json.dumps({'username': email, 'password': '***'})}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=form_data  # Usar 'data' para form data, não 'json'
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        response_json = response.json()
        print(f"📋 Response Keys: {response_json.keys()}")
        
        # Verificar estrutura da resposta
        if 'access_token' in response_json:
            print(f"✅ access_token presente")
            token = response_json['access_token']
            print(f"   Token (primeiros 50 chars): {token[:50]}...")
        else:
            print("❌ access_token ausente")
            
        if 'user' in response_json:
            print(f"✅ user presente")
            user = response_json['user']
            print(f"   Email: {user.get('email')}")
            print(f"   Nome: {user.get('nome')}")
            print(f"   Role: {user.get('role')}")
            print(f"   ID: {user.get('id')}")
        else:
            print("❌ user ausente na resposta")
            
        print(f"\n📋 Resposta completa:\n{json.dumps(response_json, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Login bem-sucedido!")
            return response_json
        else:
            print("❌ Falha no login")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None


def test_ai_status():
    """Testa endpoint de status de IA"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: VERIFICAÇÃO DE STATUS DE IA")
    print("="*60)
    
    print(f"\n🔍 URL: {BASE_URL}/ai/status")
    
    try:
        response = requests.get(
            f"{BASE_URL}/ai/status",
            timeout=5
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Endpoint existe!")
            print(f"📋 Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"⚠️ Endpoint retornou {response.status_code}")
            print(f"📋 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⚠️ Timeout ao verificar /ai/status (esperado se endpoint lento)")
    except requests.exceptions.ConnectionError:
        print("⚠️ /ai/status não está disponível (endpoint não existe? normal)")
    except Exception as e:
        print(f"⚠️ Erro na requisição: {e}")


def main():
    """Executa todos os testes"""
    print("\n🚀 INICIANDO TESTES DE AUTENTICAÇÃO")
    print("="*60)
    
    # Teste 1: Registro
    email, password = test_register()
    
    if not email:
        print("\n⚠️ Pulando testes de login - registro falhou")
        return
    
    # Teste 2: Login
    login_response = test_login(email, password)
    
    if not login_response:
        print("\n⚠️ Pulando testes de IA - login falhou")
        return
    
    # Teste 3: Status de IA
    test_ai_status()
    
    print("\n" + "="*60)
    print("✅ TESTES CONCLUÍDOS")
    print("="*60)


if __name__ == "__main__":
    main()
