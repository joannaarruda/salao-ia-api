"""
MAIN.PY - API PRINCIPAL DO SALÃO IA
===================================
Sistema completo com CORS configurado e servidor de frontend
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

import os
from pathlib import Path

# ============================================
# CRIAR APP
# ============================================
app = FastAPI(
    title="Salão IA API",
    version="2.0.0",
    description="Sistema Inteligente de Agendamento com Análise Facial por IA"
)

# ============================================
# CONFIGURAR CORS
# ============================================
print("\n" + "="*70)
print("🔧 Configurando CORS...")
print("="*70)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "null"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ CORS configurado")

# ============================================
# CRIAR DIRETÓRIOS
# ============================================
print("\n🗂️  Criando diretórios...")

directories = [
    "static",
    "static/uploads",
    "static/profile_photos"
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"✅ {directory}")

# ============================================
# SERVIR ARQUIVOS ESTÁTICOS
# ============================================
print("\n📁 Configurando arquivos estáticos...")

app.mount("/static", StaticFiles(directory="static"), name="static")
print("✅ /static montado")

# ============================================
# IMPORTAR ROUTERS
# ============================================
print("\n🔧 Importando routers...")

try:
    from app.routes.auth import router as auth_router
    print("✅ Router de autenticação")
except ImportError as e:
    print(f"⚠️  Erro: {e}")
    auth_router = None

try:
    from app.routes.ai import router as ai_router
    print("✅ Router de IA")
except ImportError as e:
    print(f"⚠️ Erro ao importar o router AI (app.routes.ai): {e}")
    ai_router = None

try:
    from app.routes.users import router as users_router
    print("✅ Router de usuários")
except ImportError as e:
    print(f"⚠️  Erro: {e}")
    users_router = None

try:
    from app.routes.appointments import router as appointments_router
    print("✅ Router de agendamentos")
except ImportError as e:
    print(f"⚠️  Erro: {e}")
    appointments_router = None

try:
    from app.routes.professionals import router as professionals_router
    print("✅ Router de profissionais")
except ImportError as e:
    print(f"⚠️  Erro: {e}")
    professionals_router = None

# ============================================
# REGISTRAR ROUTERS
# ============================================
print("\n📌 Registrando routers...")

if auth_router:
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["🔐 Autenticação"])
    print("✅ /api/v1/auth")

if ai_router:
    app.include_router(ai_router, prefix="/api/v1/ai", tags=["🤖 IA"])
    print("✅ /api/v1/ai")

if users_router:
    app.include_router(users_router, prefix="/api/v1/users", tags=["👥 Usuários"])
    print("✅ /api/v1/users")

if appointments_router:
    app.include_router(appointments_router, prefix="/api/v1/appointments", tags=["📅 Agendamentos"])
    print("✅ /api/v1/appointments")

if professionals_router:
    app.include_router(professionals_router, prefix="/api/v1/professionals", tags=["💼 Profissionais"])
    print("✅ /api/v1/professionals")

# ============================================
# ROTAS BÁSICAS
# ============================================

@app.get("/health", tags=["🏥 Health"])
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "cors": "enabled"
    }


@app.get("/api/v1", tags=["📋 Info"])
async def api_info():
    """Informações da API"""
    return {
        "name": "Salão IA API",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "ai": "/api/v1/ai",
            "users": "/api/v1/users",
            "appointments": "/api/v1/appointments",
            "professionals": "/api/v1/professionals"
        }
    }


# ============================================
# SERVIR FRONTEND
# ============================================

@app.get("/", tags=["🎨 Frontend"])
async def serve_frontend():
    """
    Serve o frontend HTML.
    
    Procura em:
    1. ./index.html (raiz do backend)
    2. ../frontend/index.html (pasta frontend ao lado)
    """
    
    # Opção 1: index.html na raiz do backend
    if os.path.exists("index.html"):
        print("📄 Servindo: ./index.html")
        return FileResponse("index.html")
    
    # Opção 2: index.html na pasta frontend (um nível acima)
    frontend_path = Path("../frontend/index.html")
    if frontend_path.exists():
        print(f"📄 Servindo: {frontend_path}")
        return FileResponse(str(frontend_path))
    
    # Não encontrou
    return {
        "error": "Frontend não encontrado",
        "message": "Coloque index.html em:\n1. backend/index.html\nOU\n2. frontend/index.html",
        "current_dir": os.getcwd(),
        "tried": [
            os.path.abspath("index.html"),
            os.path.abspath("../frontend/index.html")
        ]
    }


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint não encontrado",
            "path": str(request.url),
            "docs": "http://localhost:8000/docs"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    import traceback
    error_traceback = traceback.format_exc()
    
    print("\n" + "="*70)
    print("❌ ERRO INTERNO")
    print("="*70)
    print(error_traceback)
    print("="*70 + "\n")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "message": str(exc)
        }
    )


# ============================================
# STARTUP
# ============================================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*70)
    print("🚀 SALÃO IA API")
    print("="*70)
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🎨 Frontend: http://localhost:8000")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n⚠️  Use: uvicorn app.main:app --reload")
    print("Não execute este arquivo diretamente!\n")