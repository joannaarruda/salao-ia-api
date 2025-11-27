"""
GOOGLE_CALENDAR.PY - INTEGRAÇÃO COM GOOGLE CALENDAR
====================================================
Sincroniza agendamentos com o Google Calendar
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

# Escopos necessários para o Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# ============================================================
# CLASSE DE INTEGRAÇÃO
# ============================================================

class GoogleCalendarIntegration:
    """Gerenciador de integração com Google Calendar"""
    
    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Inicializa a integração
        
        Args:
            credentials_file: Caminho para o arquivo de credenciais do Google
        """
        self.credentials_file = credentials_file
        self.token_file = "token.pickle"
        self.service = None
        self.creds = None
    
    def authenticate(self) -> bool:
        """
        Autentica com o Google Calendar
        
        Returns:
            True se autenticado com sucesso
        """
        # Carrega token salvo se existir
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # Se não há credenciais válidas, faz o login
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Arquivo de credenciais não encontrado: {self.credentials_file}\n"
                        "Baixe em: https://console.cloud.google.com/apis/credentials"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Salva token para próximas execuções
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Erro ao autenticar: {e}")
            return False
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict]:
        """
        Cria um evento no Google Calendar
        
        Args:
            summary: Título do evento
            start_time: Data/hora de início
            end_time: Data/hora de fim
            description: Descrição do evento
            location: Local do evento
            attendees: Lista de emails dos participantes
            calendar_id: ID do calendário (padrão: 'primary')
        
        Returns:
            Dicionário com dados do evento criado ou None em caso de erro
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        event = {
            'summary': summary,
            'description': description or '',
            'location': location or '',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Europe/Lisbon',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Lisbon',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 dia antes
                    {'method': 'popup', 'minutes': 60},  # 1 hora antes
                ],
            },
        }
        
        # Adiciona participantes se fornecidos
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'  # Envia email para participantes
            ).execute()
            
            print(f'Evento criado: {event.get("htmlLink")}')
            return event
            
        except HttpError as error:
            print(f'Erro ao criar evento: {error}')
            return None
    
    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict]:
        """
        Atualiza um evento existente
        
        Args:
            event_id: ID do evento no Google Calendar
            summary: Novo título
            start_time: Nova data/hora de início
            end_time: Nova data/hora de fim
            description: Nova descrição
            calendar_id: ID do calendário
        
        Returns:
            Dicionário com dados do evento atualizado ou None em caso de erro
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # Busca o evento atual
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Atualiza campos fornecidos
            if summary:
                event['summary'] = summary
            if description:
                event['description'] = description
            if start_time:
                event['start']['dateTime'] = start_time.isoformat()
            if end_time:
                event['end']['dateTime'] = end_time.isoformat()
            
            # Atualiza o evento
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            print(f'Evento atualizado: {updated_event.get("htmlLink")}')
            return updated_event
            
        except HttpError as error:
            print(f'Erro ao atualizar evento: {error}')
            return None
    
    def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> bool:
        """
        Deleta um evento
        
        Args:
            event_id: ID do evento no Google Calendar
            calendar_id: ID do calendário
        
        Returns:
            True se deletado com sucesso
        """
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            print(f'Evento deletado: {event_id}')
            return True
            
        except HttpError as error:
            print(f'Erro ao deletar evento: {error}')
            return False
    
    def list_events(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10,
        calendar_id: str = 'primary'
    ) -> List[Dict]:
        """
        Lista eventos do calendário
        
        Args:
            time_min: Data/hora mínima
            time_max: Data/hora máxima
            max_results: Número máximo de resultados
            calendar_id: ID do calendário
        
        Returns:
            Lista de eventos
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Define intervalo de tempo
            if not time_min:
                time_min = datetime.utcnow()
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z' if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except HttpError as error:
            print(f'Erro ao listar eventos: {error}')
            return []


# ============================================================
# FUNÇÕES AUXILIARES PARA AGENDAMENTOS
# ============================================================

def sync_appointment_to_calendar(
    appointment: Dict,
    professional_name: str,
    client_name: str,
    client_email: str,
    calendar_integration: GoogleCalendarIntegration
) -> Optional[str]:
    """
    Sincroniza um agendamento com o Google Calendar
    
    Args:
        appointment: Dicionário com dados do agendamento
        professional_name: Nome do profissional
        client_name: Nome do cliente
        client_email: Email do cliente
        calendar_integration: Instância da integração
    
    Returns:
        ID do evento criado no Google Calendar ou None
    """
    # Prepara dados do evento
    start_time = datetime.fromisoformat(appointment['data_hora'])
    
    # Calcula duração total dos serviços
    duration_minutes = sum(
        service.get('duracao_estimada', 60) 
        for service in appointment.get('servicos', [])
    )
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Prepara título
    services_list = ', '.join([
        service['tipo'] for service in appointment.get('servicos', [])
    ])
    summary = f"{services_list} - {client_name}"
    
    # Prepara descrição
    description = f"""
Agendamento - Salão IA
━━━━━━━━━━━━━━━━━━━━━
Cliente: {client_name}
Profissional: {professional_name}

Serviços:
{chr(10).join([f"• {s['tipo']}" + (f" - {s['descricao']}" if s.get('descricao') else '') for s in appointment.get('servicos', [])])}

Duração Total: {duration_minutes} minutos

{'✨ Com sugestões de IA' if appointment.get('usar_ia') else ''}

{f"Observações: {appointment['observacoes']}" if appointment.get('observacoes') else ''}

ID do Agendamento: {appointment['id']}
""".strip()
    
    # Cria evento
    event = calendar_integration.create_event(
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        attendees=[client_email]
    )
    
    return event['id'] if event else None


def update_appointment_in_calendar(
    appointment: Dict,
    google_calendar_event_id: str,
    professional_name: str,
    client_name: str,
    calendar_integration: GoogleCalendarIntegration
) -> bool:
    """
    Atualiza um agendamento no Google Calendar
    
    Args:
        appointment: Dicionário com dados atualizados
        google_calendar_event_id: ID do evento no Google Calendar
        professional_name: Nome do profissional
        client_name: Nome do cliente
        calendar_integration: Instância da integração
    
    Returns:
        True se atualizado com sucesso
    """
    start_time = datetime.fromisoformat(appointment['data_hora'])
    
    duration_minutes = sum(
        service.get('duracao_estimada', 60) 
        for service in appointment.get('servicos', [])
    )
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    services_list = ', '.join([
        service['tipo'] for service in appointment.get('servicos', [])
    ])
    summary = f"{services_list} - {client_name}"
    
    description = f"""
Agendamento Atualizado - Salão IA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cliente: {client_name}
Profissional: {professional_name}
Status: {appointment.get('status', 'pendente').upper()}

Serviços:
{chr(10).join([f"• {s['tipo']}" + (f" - {s['descricao']}" if s.get('descricao') else '') for s in appointment.get('servicos', [])])}

ID do Agendamento: {appointment['id']}
""".strip()
    
    event = calendar_integration.update_event(
        event_id=google_calendar_event_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description
    )
    
    return event is not None


def cancel_appointment_in_calendar(
    google_calendar_event_id: str,
    calendar_integration: GoogleCalendarIntegration
) -> bool:
    """
    Cancela um agendamento no Google Calendar
    
    Args:
        google_calendar_event_id: ID do evento no Google Calendar
        calendar_integration: Instância da integração
    
    Returns:
        True se cancelado com sucesso
    """
    return calendar_integration.delete_event(google_calendar_event_id)


# ============================================================
# EXEMPLO DE USO
# ============================================================

if __name__ == "__main__":
    # Inicializa integração
    calendar = GoogleCalendarIntegration()
    
    # Autentica
    if calendar.authenticate():
        print("✅ Autenticado com sucesso!")
        
        # Exemplo: criar evento de teste
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        event = calendar.create_event(
            summary="Teste - Corte de Cabelo",
            start_time=start,
            end_time=end,
            description="Agendamento de teste do sistema Salão IA",
            attendees=["cliente@example.com"]
        )
        
        if event:
            print(f"✅ Evento criado: {event['id']}")
    else:
        print("❌ Erro na autenticação")
