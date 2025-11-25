from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import statistics,users,appointments, professionals # Importe seus routers existentes
from app import config 
from app.routes.users import get_current_user_id


app = FastAPI(title="Salão IA - Backend")

# Configuração de CORS para permitir acesso do frontend
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Adicione a origem do seu frontend (por exemplo, onde o canvas estiver rodando)
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Roteadores existentes
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["appointments"])
app.include_router(professionals.router, prefix="/api/v1/professionals", tags=["professionals"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["statistics"])
# Roteador para Configuração do Administrador
# 2. Registra o router que está em config.py
app.include_router(config.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API está funcionando."}

# Expondo o diretório de logos estáticos (simulação)
from fastapi.staticfiles import StaticFiles
# Crie a pasta 'static/logos' na raiz do seu backend
app.mount("/static", StaticFiles(directory="static/logos"), name="static")
app.mount("/static", StaticFiles(directory="static/uploads"), name="static")