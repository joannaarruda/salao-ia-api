"""
MAIN.PY - APLICAÇÃO PRINCIPAL
==============================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes.admin import router as admin_router # ⬅️ ADICIONAR ESTA LINHA
import os

# ✅ IMPORT DIRETO DOS ROUTERS
from app.routes.professionals import router as professionals_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.appointments import router as appointments_router
from app.routes.statistics import router as statistics_router
from app.routes.ai import router as ai_router
from app.routes.media import router as media_router
from app.routes.medical import router as medical_router
from app.routes.attendance import router as attendance_router

app = FastAPI(
    title="Salão IA API",
    description="Sistema completo de agendamento para salões de beleza",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTRAR ROUTERS
print("\n🔧 Registrando routers...")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
print("  ✅ auth")
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
print("  ✅ users")
app.include_router(appointments_router, prefix="/api/v1/appointments", tags=["appointments"])
print("  ✅ appointments")
app.include_router(professionals_router, prefix="/api/v1/professionals", tags=["professionals"])
print("  ✅ professionals")
app.include_router(statistics_router, prefix="/api/v1/statistics", tags=["statistics"])
print("  ✅ statistics")
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
print("  ✅ ai")
app.include_router(media_router, prefix="/api/v1/media", tags=["media"])
print("  ✅ media")
app.include_router(medical_router, prefix="/api/v1/medical", tags=["medical"])
print("  ✅ medical")
app.include_router(attendance_router, prefix="/api/v1/attendance", tags=["attendance"])
print("  ✅ attendance")
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"]) # ⬅️ ADICIONAR ESTA LINHA

# STATIC FILES
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/logos", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/attendance", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serve o arquivo index.html"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "Salão IA API v2.0 - Online", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "message": "API funcionando"}

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*70)
    print("🚀 SALÃO IA API INICIADA")
    print("="*70)
    print("\n📋 Rotas Registradas:\n")
    
    routes_by_prefix = {}
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            prefix = route.path.split('/')[1:3]
            prefix_str = '/'.join(prefix) if len(prefix) > 1 else route.path
            if prefix_str not in routes_by_prefix:
                routes_by_prefix[prefix_str] = []
            methods = ', '.join(route.methods)
            routes_by_prefix[prefix_str].append(f"  [{methods:12}] {route.path}")
    
    for prefix, routes in sorted(routes_by_prefix.items()):
        print(f"\n{prefix}:")
        for route in routes:
            print(route)
    
    print("\n" + "="*70)
    print("✅ API Online: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("="*70 + "\n")