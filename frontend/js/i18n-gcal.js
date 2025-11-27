/**
 * I18N.JS - INTERNACIONALIZAÇÃO NO FRONTEND
 * ==========================================
 * Sistema completo de tradução para o frontend
 */

class I18nManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'pt';
        this.translations = {};
        this.supportedLanguages = {
            'pt': { name: 'Português', flag: '🇵🇹' },
            'en': { name: 'English', flag: '🇬🇧' },
            'it': { name: 'Italiano', flag: '🇮🇹' },
            'es': { name: 'Español', flag: '🇪🇸' }
        };
    }
    
    /**
     * Carrega traduções do backend
     */
    async loadTranslations(language) {
        try {
            const response = await fetch(`${API_URL}/appointments/translations?language=${language}`);
            const data = await response.json();
            
            if (response.ok) {
                this.translations = data.translations;
                this.currentLanguage = language;
                localStorage.setItem('language', language);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Erro ao carregar traduções:', error);
            return false;
        }
    }
    
    /**
     * Obtém tradução de uma chave
     */
    t(key, defaultValue = null) {
        return this.translations[key] || defaultValue || key;
    }
    
    /**
     * Atualiza toda a interface
     */
    updateUI() {
        // Atualiza elementos com data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.dataset.i18n;
            const translation = this.t(key);
            
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });
        
        // Atualiza elementos com data-i18n-title (tooltips)
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.dataset.i18nTitle;
            element.title = this.t(key);
        });
        
        // Atualiza seletor de idioma
        const langSelector = document.getElementById('languageSelector');
        if (langSelector) {
            langSelector.value = this.currentLanguage;
        }
    }
    
    /**
     * Muda o idioma
     */
    async changeLanguage(language) {
        if (language === this.currentLanguage) return;
        
        showMessage(this.t('loading'), 'info');
        
        const success = await this.loadTranslations(language);
        
        if (success) {
            this.updateUI();
            showMessage(this.t('language_changed'), 'success');
            
            // Dispara evento customizado
            window.dispatchEvent(new CustomEvent('languageChanged', {
                detail: { language }
            }));
        } else {
            showMessage(this.t('error_loading_translations'), 'error');
        }
    }
    
    /**
     * Cria seletor de idioma
     */
    createLanguageSelector() {
        const selector = document.createElement('select');
        selector.id = 'languageSelector';
        selector.className = 'language-selector';
        
        Object.entries(this.supportedLanguages).forEach(([code, info]) => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = `${info.flag} ${info.name}`;
            selector.appendChild(option);
        });
        
        selector.value = this.currentLanguage;
        selector.addEventListener('change', (e) => {
            this.changeLanguage(e.target.value);
        });
        
        return selector;
    }
    
    /**
     * Formata data segundo idioma
     */
    formatDate(date, format = 'short') {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        
        const locales = {
            'pt': 'pt-PT',
            'en': 'en-US',
            'it': 'it-IT',
            'es': 'es-ES'
        };
        
        const options = format === 'short' 
            ? { year: 'numeric', month: '2-digit', day: '2-digit' }
            : { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
        
        return dateObj.toLocaleDateString(locales[this.currentLanguage], options);
    }
    
    /**
     * Formata hora segundo idioma
     */
    formatTime(time) {
        const timeObj = typeof time === 'string' ? new Date(time) : time;
        
        const locales = {
            'pt': 'pt-PT',
            'en': 'en-US',
            'it': 'it-IT',
            'es': 'es-ES'
        };
        
        return timeObj.toLocaleTimeString(locales[this.currentLanguage], {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    /**
     * Formata número segundo idioma
     */
    formatNumber(number, decimals = 0) {
        const locales = {
            'pt': 'pt-PT',
            'en': 'en-US',
            'it': 'it-IT',
            'es': 'es-ES'
        };
        
        return new Intl.NumberFormat(locales[this.currentLanguage], {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    }
    
    /**
     * Formata moeda segundo idioma
     */
    formatCurrency(amount) {
        const currencies = {
            'pt': { currency: 'EUR', locale: 'pt-PT' },
            'en': { currency: 'USD', locale: 'en-US' },
            'it': { currency: 'EUR', locale: 'it-IT' },
            'es': { currency: 'EUR', locale: 'es-ES' }
        };
        
        const config = currencies[this.currentLanguage];
        
        return new Intl.NumberFormat(config.locale, {
            style: 'currency',
            currency: config.currency
        }).format(amount);
    }
}

// ============================================================
// INTEGRAÇÃO COM GOOGLE CALENDAR
// ============================================================

class GoogleCalendarUI {
    constructor() {
        this.syncEnabled = localStorage.getItem('googleCalendarSync') === 'true';
    }
    
    /**
     * Checkbox para ativar/desativar sincronização
     */
    createSyncCheckbox() {
        const container = document.createElement('div');
        container.className = 'google-calendar-sync';
        container.innerHTML = `
            <label>
                <input 
                    type="checkbox" 
                    id="syncGoogleCalendar" 
                    ${this.syncEnabled ? 'checked' : ''}
                >
                <span data-i18n="google_calendar_sync">
                    📅 Sincronizar com Google Calendar
                </span>
            </label>
        `;
        
        const checkbox = container.querySelector('input');
        checkbox.addEventListener('change', (e) => {
            this.syncEnabled = e.target.checked;
            localStorage.setItem('googleCalendarSync', this.syncEnabled);
        });
        
        return container;
    }
    
    /**
     * Badge indicando sincronização
     */
    createSyncBadge(appointment) {
        if (!appointment.google_calendar_event_id) return null;
        
        const badge = document.createElement('span');
        badge.className = 'calendar-sync-badge';
        badge.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13z"/>
            </svg>
            <span data-i18n="synced_calendar">Sincronizado</span>
        `;
        badge.title = i18n.t('google_calendar_synced');
        
        return badge;
    }
}

// ============================================================
// INSTÂNCIA GLOBAL
// ============================================================

const i18n = new I18nManager();
const gcalUI = new GoogleCalendarUI();

// ============================================================
// INICIALIZAÇÃO
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Carrega traduções
    await i18n.loadTranslations(i18n.currentLanguage);
    
    // Cria seletor de idioma
    const navbar = document.querySelector('.navbar .container');
    if (navbar) {
        const langSelector = i18n.createLanguageSelector();
        navbar.appendChild(langSelector);
    }
    
    // Atualiza UI
    i18n.updateUI();
    
    // Adiciona checkbox de sincronização nos formulários de agendamento
    const appointmentForm = document.getElementById('appointmentForm');
    if (appointmentForm) {
        const syncCheckbox = gcalUI.createSyncCheckbox();
        appointmentForm.insertBefore(syncCheckbox, appointmentForm.firstChild);
    }
});

// ============================================================
// EXEMPLO DE USO EM AGENDAMENTOS
// ============================================================

async function createAppointmentWithI18n() {
    const appointmentData = {
        profissional_id: document.getElementById('profissional').value,
        data_hora: selectedTime,
        servicos: selectedServices,
        usar_ia: document.getElementById('usarIA').checked,
        observacoes: document.getElementById('observacoes').value,
        requer_consulta: document.getElementById('requerConsulta').checked,
        requer_teste_mecha: document.getElementById('requerTesteMecha').checked
    };
    
    try {
        const response = await fetch(
            `${API_URL}/appointments/?sync_calendar=${gcalUI.syncEnabled}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`,
                    'Accept-Language': i18n.currentLanguage
                },
                body: JSON.stringify(appointmentData)
            }
        );
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(i18n.t('appointment_created'), 'success');
            
            if (data.google_calendar_event_id) {
                showMessage(i18n.t('google_calendar_synced'), 'info');
            }
            
            // Recarrega lista
            await loadMyAppointments();
        } else {
            showMessage(data.detail || i18n.t('error'), 'error');
        }
    } catch (error) {
        showMessage(i18n.t('error_connection'), 'error');
    }
}

// ============================================================
// RENDERIZAÇÃO DE AGENDAMENTOS COM I18N
// ============================================================

function renderAppointmentCard(appointment) {
    const statusText = i18n.t(appointment.status);
    const dateFormatted = i18n.formatDate(appointment.data_hora, 'long');
    const timeFormatted = i18n.formatTime(appointment.data_hora);
    
    const card = document.createElement('div');
    card.className = `appointment-card ${appointment.status}`;
    
    // Badge de sincronização
    const syncBadge = gcalUI.createSyncBadge(appointment);
    
    card.innerHTML = `
        <div class="appointment-header">
            <h4>${timeFormatted}</h4>
            <span class="status-badge ${appointment.status}">${statusText}</span>
        </div>
        
        <div class="appointment-body">
            <p><strong data-i18n="date">Data</strong>: ${dateFormatted}</p>
            <p><strong data-i18n="professional">Profissional</strong>: ${getProfessionalName(appointment.profissional_id)}</p>
            
            <div class="services-list">
                <strong data-i18n="services">Serviços</strong>:
                ${appointment.servicos.map(s => `
                    <div class="service-item-small">
                        ${i18n.t(s.tipo)} ${s.descricao ? `- ${s.descricao}` : ''}
                        (${s.duracao_estimada} ${i18n.t('minutes')})
                    </div>
                `).join('')}
            </div>
            
            ${appointment.usar_ia ? `
                <span class="ia-badge">✨ ${i18n.t('with_ai')}</span>
            ` : ''}
            
            ${syncBadge ? syncBadge.outerHTML : ''}
        </div>
        
        <div class="appointment-actions">
            ${getAppointmentActions(appointment)}
        </div>
    `;
    
    return card;
}

// ============================================================
// EXPORTAÇÃO DE DADOS
// ============================================================

async function exportDataToDatabricks() {
    try {
        showMessage(i18n.t('exporting_data'), 'info');
        
        const response = await fetch(`${API_URL}/export/databricks`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Accept-Language': i18n.currentLanguage
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(
                `${i18n.t('export_success')} - ${data.files_count} ${i18n.t('files')}`,
                'success'
            );
            
            // Mostra links para download
            data.files.forEach(file => {
                console.log(`📊 ${file.type}: ${file.path}`);
            });
        } else {
            showMessage(i18n.t('export_error'), 'error');
        }
    } catch (error) {
        showMessage(i18n.t('error_connection'), 'error');
    }
}

// ============================================================
// HELPER: TRADUZIR STATUS DE SERVIÇOS
// ============================================================

function translateServiceType(type) {
    const serviceMap = {
        'corte': 'haircut',
        'coloracao': 'coloring',
        'luzes': 'highlights',
        'mechas': 'highlights',
        'hidratacao': 'hydration',
        'retoque_raiz': 'root_touch_up',
        'manicure': 'manicure',
        'pedicure': 'pedicure'
    };
    
    return i18n.t(serviceMap[type] || type);
}

// ============================================================
// EVENTOS CUSTOMIZADOS
// ============================================================

// Escuta mudanças de idioma
window.addEventListener('languageChanged', (event) => {
    console.log(`Idioma alterado para: ${event.detail.language}`);
    
    // Atualiza qualquer conteúdo dinâmico
    const appointments = document.querySelectorAll('.appointment-card');
    appointments.forEach(card => {
        // Re-renderiza cards
    });
});

// ============================================================
// CSS PARA I18N E GOOGLE CALENDAR
// ============================================================

const styleSheet = document.createElement('style');
styleSheet.textContent = `
/* Seletor de Idioma */
.language-selector {
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid #ddd;
    background: white;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s;
}

.language-selector:hover {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Badge de Sincronização */
.calendar-sync-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    background: #4285f4;
    color: white;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.calendar-sync-badge svg {
    width: 16px;
    height: 16px;
}

/* Checkbox de Sincronização */
.google-calendar-sync {
    background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
    padding: 15px;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
}

.google-calendar-sync label {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-weight: 500;
}

.google-calendar-sync input[type="checkbox"] {
    margin-right: 10px;
    width: 20px;
    height: 20px;
    cursor: pointer;
}

/* Direção de texto para idiomas RTL (se necessário futuramente) */
[dir="rtl"] {
    direction: rtl;
    text-align: right;
}
`;

document.head.appendChild(styleSheet);

console.log('✅ Sistema de i18n e Google Calendar inicializado');
