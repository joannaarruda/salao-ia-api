from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
# Assumindo que a base de dados (db) e as funções de segurança (get_current_user_id)
# já foram definidas nos outros módulos.
from app.database import db
from app.routes.users import get_current_user_id # Reutilizando a dependência de segurança

# =============================================================
# --- ROTAS DE ESTATÍSTICAS ---
# =============================================================
router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_system_statistics(current_user_id: str = Depends(get_current_user_id)):
    """
    Retorna estatísticas de alto nível para o sistema.
    Acesso restrito apenas a utilizadores autenticados (simulando um painel de administrador/gestor).
    """
    # 1. Verificar se o utilizador autenticado tem permissão para ver estatísticas
    # Esta é uma simulação; num projeto real, você verificaria uma função (role) do utilizador.
    # Por agora, assumimos que qualquer utilizador autenticado pode ver.
    user = db.get_user_by_id(current_user_id)
    if not user:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. O utilizador não está registado."
        )

    try:
        # 2. Obter dados brutos
        all_users = db.get_all_users()
        all_appointments = db.get_all_appointments()
        all_professionals = db.get_all_professionals()

        # 3. Processar e calcular estatísticas
        total_users = len(all_users)
        total_appointments = len(all_appointments)
        total_professionals = len(all_professionals)

        # Contagem de agendamentos por status
        appointments_by_status = {}
        for apt in all_appointments:
            status_key = apt.get("status", "desconhecido").lower()
            appointments_by_status[status_key] = appointments_by_status.get(status_key, 0) + 1
            
        # Contagem de agendamentos por serviço (simulação)
        appointments_by_service = {}
        for apt in all_appointments:
            service_key = apt.get("servico", "desconhecido").lower()
            appointments_by_service[service_key] = appointments_by_service.get(service_key, 0) + 1


        return {
            "total_utilizadores": total_users,
            "total_agendamentos": total_appointments,
            "total_profissionais": total_professionals,
            "agendamentos_por_status": appointments_by_status,
            "agendamentos_por_servico": appointments_by_service,
            "ultima_atualizacao": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Lidar com falhas de acesso à base de dados
        print(f"Erro ao gerar estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao aceder aos dados da base de dados."
        )