from typing import Dict, Optional
from enum import Enum

class Language(str, Enum):
    """Idiomas suportados"""
    PT = "pt"  # Português
    EN = "en"  # English
    IT = "it"  # Italiano
    ES = "es"  # Español

# ============================================================
# TRADUÇÕES
# ============================================================

TRANSLATIONS = {
    # GERAL
    "app_name": {
        "pt": "Salão IA",
        "en": "AI Salon",
        "it": "Salone IA",
        "es": "Salón IA"
    },
    "welcome": {
        "pt": "Bem-vindo(a)",
        "en": "Welcome",
        "it": "Benvenuto/a",
        "es": "Bienvenido/a"
    },
    "save": {
        "pt": "Salvar",
        "en": "Save",
        "it": "Salva",
        "es": "Guardar"
    },
    "cancel": {
        "pt": "Cancelar",
        "en": "Cancel",
        "it": "Annulla",
        "es": "Cancelar"
    },
    "confirm": {
        "pt": "Confirmar",
        "en": "Confirm",
        "it": "Conferma",
        "es": "Confirmar"
    },
    "back": {
        "pt": "Voltar",
        "en": "Back",
        "it": "Indietro",
        "es": "Volver"
    },
    "loading": {
        "pt": "Carregando...",
        "en": "Loading...",
        "it": "Caricamento...",
        "es": "Cargando..."
    },
    "error": {
        "pt": "Erro",
        "en": "Error",
        "it": "Errore",
        "es": "Error"
    },
    "success": {
        "pt": "Sucesso",
        "en": "Success",
        "it": "Successo",
        "es": "Éxito"
    },
    
    # AUTENTICAÇÃO
    "login": {
        "pt": "Entrar",
        "en": "Login",
        "it": "Accedi",
        "es": "Iniciar sesión"
    },
    "register": {
        "pt": "Registar",
        "en": "Register",
        "it": "Registrati",
        "es": "Registrarse"
    },
    "logout": {
        "pt": "Sair",
        "en": "Logout",
        "it": "Esci",
        "es": "Salir"
    },
    "email": {
        "pt": "Email",
        "en": "Email",
        "it": "Email",
        "es": "Correo electrónico"
    },
    "password": {
        "pt": "Senha",
        "en": "Password",
        "it": "Password",
        "es": "Contraseña"
    },
    "name": {
        "pt": "Nome",
        "en": "Name",
        "it": "Nome",
        "es": "Nombre"
    },
    "phone": {
        "pt": "Telefone",
        "en": "Phone",
        "it": "Telefono",
        "es": "Teléfono"
    },
    "address": {
        "pt": "Morada",
        "en": "Address",
        "it": "Indirizzo",
        "es": "Dirección"
    },
    
    # AGENDAMENTOS
    "appointments": {
        "pt": "Agendamentos",
        "en": "Appointments",
        "it": "Appuntamenti",
        "es": "Citas"
    },
    "new_appointment": {
        "pt": "Novo Agendamento",
        "en": "New Appointment",
        "it": "Nuovo Appuntamento",
        "es": "Nueva Cita"
    },
    "my_appointments": {
        "pt": "Meus Agendamentos",
        "en": "My Appointments",
        "it": "I Miei Appuntamenti",
        "es": "Mis Citas"
    },
    "date": {
        "pt": "Data",
        "en": "Date",
        "it": "Data",
        "es": "Fecha"
    },
    "time": {
        "pt": "Horário",
        "en": "Time",
        "it": "Orario",
        "es": "Hora"
    },
    "service": {
        "pt": "Serviço",
        "en": "Service",
        "it": "Servizio",
        "es": "Servicio"
    },
    "services": {
        "pt": "Serviços",
        "en": "Services",
        "it": "Servizi",
        "es": "Servicios"
    },
    "professional": {
        "pt": "Profissional",
        "en": "Professional",
        "it": "Professionista",
        "es": "Profesional"
    },
    "duration": {
        "pt": "Duração",
        "en": "Duration",
        "it": "Durata",
        "es": "Duración"
    },
    "total_duration": {
        "pt": "Duração Total",
        "en": "Total Duration",
        "it": "Durata Totale",
        "es": "Duración Total"
    },
    "status": {
        "pt": "Estado",
        "en": "Status",
        "it": "Stato",
        "es": "Estado"
    },
    "pending": {
        "pt": "Pendente",
        "en": "Pending",
        "it": "In Attesa",
        "es": "Pendiente"
    },
    "confirmed": {
        "pt": "Confirmado",
        "en": "Confirmed",
        "it": "Confermato",
        "es": "Confirmado"
    },
    "completed": {
        "pt": "Concluído",
        "en": "Completed",
        "it": "Completato",
        "es": "Completado"
    },
    "cancelled": {
        "pt": "Cancelado",
        "en": "Cancelled",
        "it": "Annullato",
        "es": "Cancelado"
    },
    
    # SERVIÇOS
    "haircut": {
        "pt": "Corte",
        "en": "Haircut",
        "it": "Taglio",
        "es": "Corte"
    },
    "coloring": {
        "pt": "Coloração",
        "en": "Coloring",
        "it": "Colorazione",
        "es": "Coloración"
    },
    "highlights": {
        "pt": "Luzes",
        "en": "Highlights",
        "it": "Colpi di Sole",
        "es": "Mechas"
    },
    "hydration": {
        "pt": "Hidratação",
        "en": "Hydration",
        "it": "Idratazione",
        "es": "Hidratación"
    },
    "root_touch_up": {
        "pt": "Retoque de Raiz",
        "en": "Root Touch-up",
        "it": "Ritocco Radici",
        "es": "Retoque de Raíces"
    },
    "manicure": {
        "pt": "Manicure",
        "en": "Manicure",
        "it": "Manicure",
        "es": "Manicura"
    },
    "pedicure": {
        "pt": "Pedicure",
        "en": "Pedicure",
        "it": "Pedicure",
        "es": "Pedicura"
    },
    
    # IA
    "use_ai": {
        "pt": "Usar IA",
        "en": "Use AI",
        "it": "Usa IA",
        "es": "Usar IA"
    },
    "ai_suggestions": {
        "pt": "Sugestões de IA",
        "en": "AI Suggestions",
        "it": "Suggerimenti IA",
        "es": "Sugerencias de IA"
    },
    "with_ai": {
        "pt": "Com IA",
        "en": "With AI",
        "it": "Con IA",
        "es": "Con IA"
    },
    "without_ai": {
        "pt": "Sem IA",
        "en": "Without AI",
        "it": "Senza IA",
        "es": "Sin IA"
    },
    
    # HISTÓRICO MÉDICO
    "medical_history": {
        "pt": "Histórico Médico",
        "en": "Medical History",
        "it": "Storia Medica",
        "es": "Historial Médico"
    },
    "medications": {
        "pt": "Medicamentos",
        "en": "Medications",
        "it": "Farmaci",
        "es": "Medicamentos"
    },
    "allergies": {
        "pt": "Alergias",
        "en": "Allergies",
        "it": "Allergie",
        "es": "Alergias"
    },
    "previous_treatments": {
        "pt": "Tratamentos Anteriores",
        "en": "Previous Treatments",
        "it": "Trattamenti Precedenti",
        "es": "Tratamientos Anteriores"
    },
    "pool_swimming": {
        "pt": "Banho de Piscina Frequente",
        "en": "Frequent Pool Swimming",
        "it": "Nuoto in Piscina Frequente",
        "es": "Natación Frecuente en Piscina"
    },
    
    # CONSULTA
    "consultation": {
        "pt": "Consulta",
        "en": "Consultation",
        "it": "Consulenza",
        "es": "Consulta"
    },
    "request_consultation": {
        "pt": "Solicitar Consulta",
        "en": "Request Consultation",
        "it": "Richiedi Consulenza",
        "es": "Solicitar Consulta"
    },
    "strand_test": {
        "pt": "Teste de Mecha",
        "en": "Strand Test",
        "it": "Test della Ciocca",
        "es": "Prueba de Mecha"
    },
    "request_strand_test": {
        "pt": "Solicitar Teste de Mecha",
        "en": "Request Strand Test",
        "it": "Richiedi Test della Ciocca",
        "es": "Solicitar Prueba de Mecha"
    },
    
    # FICHA DE ATENDIMENTO
    "attendance_record": {
        "pt": "Ficha de Atendimento",
        "en": "Attendance Record",
        "it": "Scheda di Servizio",
        "es": "Ficha de Atención"
    },
    "products_used": {
        "pt": "Produtos Utilizados",
        "en": "Products Used",
        "it": "Prodotti Utilizzati",
        "es": "Productos Utilizados"
    },
    "techniques_applied": {
        "pt": "Técnicas Aplicadas",
        "en": "Techniques Applied",
        "it": "Tecniche Applicate",
        "es": "Técnicas Aplicadas"
    },
    "processing_time": {
        "pt": "Tempo de Processamento",
        "en": "Processing Time",
        "it": "Tempo di Lavorazione",
        "es": "Tiempo de Procesamiento"
    },
    "photos_before": {
        "pt": "Fotos Antes",
        "en": "Before Photos",
        "it": "Foto Prima",
        "es": "Fotos Antes"
    },
    "photos_after": {
        "pt": "Fotos Depois",
        "en": "After Photos",
        "it": "Foto Dopo",
        "es": "Fotos Después"
    },
    "can_publish_photos": {
        "pt": "Pode Publicar Fotos",
        "en": "Can Publish Photos",
        "it": "Può Pubblicare Foto",
        "es": "Puede Publicar Fotos"
    },
    "client_feedback": {
        "pt": "Feedback do Cliente",
        "en": "Client Feedback",
        "it": "Feedback del Cliente",
        "es": "Opinión del Cliente"
    },
    "satisfaction": {
        "pt": "Satisfação",
        "en": "Satisfaction",
        "it": "Soddisfazione",
        "es": "Satisfacción"
    },
    "liked_result": {
        "pt": "Gostou do Resultado",
        "en": "Liked Result",
        "it": "Risultato Piaciuto",
        "es": "Le Gustó el Resultado"
    },
    "allergic_reaction": {
        "pt": "Reação Alérgica",
        "en": "Allergic Reaction",
        "it": "Reazione Allergica",
        "es": "Reacción Alérgica"
    },
    
    # ADMIN
    "admin_panel": {
        "pt": "Painel de Administrador",
        "en": "Admin Panel",
        "it": "Pannello Amministratore",
        "es": "Panel de Administrador"
    },
    "settings": {
        "pt": "Configurações",
        "en": "Settings",
        "it": "Impostazioni",
        "es": "Configuración"
    },
    "logo": {
        "pt": "Logo",
        "en": "Logo",
        "it": "Logo",
        "es": "Logo"
    },
    "colors": {
        "pt": "Cores",
        "en": "Colors",
        "it": "Colori",
        "es": "Colores"
    },
    "primary_color": {
        "pt": "Cor Primária",
        "en": "Primary Color",
        "it": "Colore Primario",
        "es": "Color Primario"
    },
    "secondary_color": {
        "pt": "Cor Secundária",
        "en": "Secondary Color",
        "it": "Colore Secondario",
        "es": "Color Secundario"
    },
    
    # MENSAGENS
    "appointment_created": {
        "pt": "Agendamento criado com sucesso!",
        "en": "Appointment created successfully!",
        "it": "Appuntamento creato con successo!",
        "es": "¡Cita creada con éxito!"
    },
    "appointment_confirmed": {
        "pt": "Agendamento confirmado!",
        "en": "Appointment confirmed!",
        "it": "Appuntamento confermato!",
        "es": "¡Cita confirmada!"
    },
    "appointment_cancelled": {
        "pt": "Agendamento cancelado",
        "en": "Appointment cancelled",
        "it": "Appuntamento annullato",
        "es": "Cita cancelada"
    },
    "login_success": {
        "pt": "Login realizado com sucesso!",
        "en": "Login successful!",
        "it": "Login effettuato con successo!",
        "es": "¡Inicio de sesión exitoso!"
    },
    "error_connection": {
        "pt": "Erro de conexão",
        "en": "Connection error",
        "it": "Errore di connessione",
        "es": "Error de conexión"
    },
    "google_calendar_synced": {
        "pt": "Sincronizado com Google Calendar",
        "en": "Synced with Google Calendar",
        "it": "Sincronizzato con Google Calendar",
        "es": "Sincronizado con Google Calendar"
    }
}

# ============================================================
# CLASSE DE TRADUÇÃO
# ============================================================

class Translator:
    """Gerenciador de traduções"""
    
    def __init__(self, default_language: Language = Language.PT):
        self.current_language = default_language
    
    def set_language(self, language: Language):
        """Define o idioma atual"""
        self.current_language = language
    
    def get(self, key: str, language: Optional[Language] = None) -> str:
        """
        Obtém tradução de uma chave
        
        Args:
            key: Chave da tradução
            language: Idioma (usa o atual se não especificado)
        
        Returns:
            Texto traduzido ou a chave se não encontrado
        """
        lang = language or self.current_language
        
        if key not in TRANSLATIONS:
            return key
        
        return TRANSLATIONS[key].get(lang.value, TRANSLATIONS[key].get("pt", key))
    
    def get_all(self, language: Optional[Language] = None) -> Dict[str, str]:
        """
        Retorna todas as traduções para um idioma
        
        Args:
            language: Idioma (usa o atual se não especificado)
        
        Returns:
            Dicionário com todas as traduções
        """
        lang = language or self.current_language
        
        return {
            key: value.get(lang.value, value.get("pt", key))
            for key, value in TRANSLATIONS.items()
        }
    
    def translate_dict(self, data: Dict, keys: list, language: Optional[Language] = None) -> Dict:
        """
        Traduz campos específicos de um dicionário
        
        Args:
            data: Dicionário com dados
            keys: Lista de chaves a traduzir
            language: Idioma (usa o atual se não especificado)
        
        Returns:
            Dicionário com campos traduzidos
        """
        lang = language or self.current_language
        result = data.copy()
        
        for key in keys:
            if key in result:
                translated_key = self.get(key, lang)
                result[translated_key] = result.pop(key)
        
        return result


# Instância global
translator = Translator()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_translation(key: str, language: Optional[Language] = None) -> str:
    """Atalho para obter tradução"""
    return translator.get(key, language)


def set_language(language: Language):
    """Atalho para definir idioma"""
    translator.set_language(language)


def get_all_translations(language: Optional[Language] = None) -> Dict[str, str]:
    """Atalho para obter todas as traduções"""
    return translator.get_all(language)
