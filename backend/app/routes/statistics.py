"""
STATISTICS.PY - ESTATÍSTICAS E RELATÓRIOS
==========================================
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated, Optional
from datetime import datetime, timedelta

from app.models import User
from app.database import db
from app.auth import get_current_user  # ← CORRETO: Importa de auth.py

router = APIRouter()


# ============================================================
# ESTATÍSTICAS GERAIS
# ============================================================

@router.get("/overview")
async def get_statistics_overview(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Retorna visão geral das estatísticas do sistema.
    Apenas administradores e profissionais podem ver.
    """
    if current_user.role not in ["admin", "profissional"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado"
        )
    
    # Total de usuários
    users = db.get_all_users()
    total_users = len(users)
    total_clientes = len([u for u in users if u.get("role") == "cliente"])
    total_profissionais = len([u for u in users if u.get("role") == "profissional"])
    
    # Total de agendamentos
    appointments = db.get_all_appointments()
    total_appointments = len(appointments)
    
    # Agendamentos por status
    status_counts = {}
    for apt in appointments:
        status = apt.get("status", "pendente")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Agendamentos este mês
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    appointments_this_month = [
        apt for apt in appointments
        if datetime.fromisoformat(apt.get("created_at", "")) >= month_start
    ]
    
    return {
        "users": {
            "total": total_users,
            "clientes": total_clientes,
            "profissionais": total_profissionais
        },
        "appointments": {
            "total": total_appointments,
            "this_month": len(appointments_this_month),
            "by_status": status_counts
        }
    }


# ============================================================
# ESTATÍSTICAS DE AGENDAMENTOS
# ============================================================

@router.get("/appointments")
async def get_appointment_statistics(
    start_date: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Estatísticas detalhadas de agendamentos.
    """
    if current_user.role not in ["admin", "profissional"]:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado"
        )
    
    appointments = db.get_all_appointments()
    
    # Filtra por período se fornecido
    if start_date:
        start = datetime.fromisoformat(start_date)
        appointments = [
            apt for apt in appointments
            if datetime.fromisoformat(apt.get("data_hora", "")) >= start
        ]
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        appointments = [
            apt for apt in appointments
            if datetime.fromisoformat(apt.get("data_hora", "")) <= end
        ]
    
    # Agrupamentos
    by_professional = {}
    by_service = {}
    by_day = {}
    
    for apt in appointments:
        # Por profissional
        prof_id = apt.get("profissional_id")
        by_professional[prof_id] = by_professional.get(prof_id, 0) + 1
        
        # Por serviço
        for service in apt.get("servicos", []):
            service_type = service.get("tipo")
            by_service[service_type] = by_service.get(service_type, 0) + 1
        
        # Por dia da semana
        data_hora = datetime.fromisoformat(apt.get("data_hora", ""))
        day_name = data_hora.strftime("%A")
        by_day[day_name] = by_day.get(day_name, 0) + 1
    
    return {
        "total": len(appointments),
        "by_professional": by_professional,
        "by_service": by_service,
        "by_day_of_week": by_day
    }


# ============================================================
# ESTATÍSTICAS DO PROFISSIONAL
# ============================================================

@router.get("/my-stats")
async def get_my_statistics(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Estatísticas do profissional logado.
    """
    if current_user.role != "profissional":
        raise HTTPException(
            status_code=403,
            detail="Apenas profissionais podem ver suas estatísticas"
        )
    
    # Agendamentos do profissional
    appointments = db.get_appointments_by_professional(current_user.id)
    
    # Total e por status
    total = len(appointments)
    by_status = {}
    for apt in appointments:
        status = apt.get("status", "pendente")
        by_status[status] = by_status.get(status, 0) + 1
    
    # Este mês
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    this_month = [
        apt for apt in appointments
        if datetime.fromisoformat(apt.get("created_at", "")) >= month_start
    ]
    
    # Próximos agendamentos
    upcoming = [
        apt for apt in appointments
        if apt.get("status") == "confirmado" and
        datetime.fromisoformat(apt.get("data_hora", "")) >= now
    ]
    
    return {
        "total_appointments": total,
        "by_status": by_status,
        "this_month": len(this_month),
        "upcoming": len(upcoming),
        "upcoming_appointments": sorted(
            upcoming,
            key=lambda x: x.get("data_hora", "")
        )[:5]  # Próximos 5
    }


# ============================================================
# RELATÓRIO DE RECEITA (ADMIN)
# ============================================================

@router.get("/revenue")
async def get_revenue_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Relatório de receita.
    Apenas administradores.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem ver relatórios de receita"
        )
    
    appointments = db.get_all_appointments()
    
    # Filtra concluídos
    completed = [apt for apt in appointments if apt.get("status") == "concluido"]
    
    # Filtra por período
    if start_date:
        start = datetime.fromisoformat(start_date)
        completed = [
            apt for apt in completed
            if datetime.fromisoformat(apt.get("completed_at", apt.get("data_hora", ""))) >= start
        ]
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        completed = [
            apt for apt in completed
            if datetime.fromisoformat(apt.get("completed_at", apt.get("data_hora", ""))) <= end
        ]
    
    # Calcula receita (se tiver preços nos serviços)
    total_revenue = 0
    by_service = {}
    by_professional = {}
    
    for apt in completed:
        for service in apt.get("servicos", []):
            service_type = service.get("tipo")
            price = service.get("preco", 0)
            
            total_revenue += price
            by_service[service_type] = by_service.get(service_type, 0) + price
            
            prof_id = apt.get("profissional_id")
            by_professional[prof_id] = by_professional.get(prof_id, 0) + price
    
    return {
        "total_appointments": len(completed),
        "total_revenue": total_revenue,
        "by_service": by_service,
        "by_professional": by_professional
    }