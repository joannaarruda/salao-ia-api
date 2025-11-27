/**
 * THEME.JS - SISTEMA DE TEMAS DINÂMICO
 * =====================================
 */

const API_BASE_URL = "http://localhost:8000/api/v1";

const AppTheme = {
    settings: null,
    
    async loadSettings() {
        try {
            const response = await fetch(`${API_BASE_URL}/settings/`);
            this.settings = await response.json();
            return this.settings;
        } catch (error) {
            console.error("Erro ao carregar configurações:", error);
            return this.getDefaultSettings();
        }
    },
    
    getDefaultSettings() {
        return {
            salon_name: "Salão IA",
            logo_url: "/static/images/default_logo.png",
            colors: {
                primary: "#6366f1",
                secondary: "#8b5cf6",
                accent: "#ec4899",
                background: "#ffffff",
                text: "#1f2937"
            }
        };
    },
    
    applyColors(colors) {
        const root = document.documentElement;
        root.style.setProperty('--color-primary', colors.primary);
        root.style.setProperty('--color-secondary', colors.secondary);
        root.style.setProperty('--color-accent', colors.accent);
        root.style.setProperty('--color-background', colors.background);
        root.style.setProperty('--color-text', colors.text);
    },
    
    updateLogo(logoUrl) {
        const logos = document.querySelectorAll('.salon-logo, #systemLogo');
        logos.forEach(logo => {
            logo.src = `${API_BASE_URL.replace('/api/v1', '')}${logoUrl}`;
        });
    },
    
    async applyTheme() {
        const settings = await this.loadSettings();
        
        if (settings.colors) {
            this.applyColors(settings.colors);
        }
        
        if (settings.logo_url) {
            this.updateLogo(settings.logo_url);
        }
        
        if (settings.salon_name) {
            document.title = `${settings.salon_name} - Agendamento`;
        }
    },
    
    async refresh() {
        await this.applyTheme();
    }
};

// Inicializa ao carregar
document.addEventListener('DOMContentLoaded', () => {
    AppTheme.applyTheme();
});

window.AppTheme = AppTheme;