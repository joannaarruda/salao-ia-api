// Dependências: API_URL, authToken (devem estar disponíveis globalmente via app.js)
// Dependências: showMessage, loadAndApplyConfig (devem estar disponíveis globalmente via app.js)

// ==================== ADMIN CONFIGURAÇÃO (CORES E LOGO) ====================

document.addEventListener('DOMContentLoaded', () => {
    // 1. O formulário de configuração só existe na tela de admin
    const configForm = document.getElementById('configForm');
    if (configForm) {
        console.log('⚙️ Admin: Inicializando listener do formulário de configuração.');
        configForm.addEventListener('submit', handleConfigSubmit);
        
        // 2. Listener para preview da nova logo (mantido, mas a lógica de upload no submit foi removida)
        const logoInput = document.getElementById('newLogo');
        if (logoInput) {
            logoInput.addEventListener('change', previewNewLogo);
        }
    } else {
        console.log('⚙️ Admin: Formulário de configuração não encontrado. Skip.');
    }
});

/**
 * Atualiza o preview da imagem no formulário de admin quando uma nova logo é selecionada.
 */
function previewNewLogo(event) {
    // ESTA FUNÇÃO PERMANECE INALTERADA
    const file = event.target.files[0];
    const previewElement = document.getElementById('newLogoPreview');
    
    if (file && previewElement) {
        console.log('🖼️ Admin: Gerando preview da nova logo.');
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.src = e.target.result;
            previewElement.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else if (previewElement) {
        previewElement.style.display = 'none';
        previewElement.src = ''; // Limpa o preview se não houver ficheiro
    }
}


/**
 * Lida com a submissão do formulário de configuração (cores e logo).
 * AGORA ENVIA APENAS JSON. (A lógica de upload de arquivo foi simplificada/removida)
 */
async function handleConfigSubmit(e) {
    e.preventDefault();
    console.log('💾 Admin: Tentando salvar a configuração do sistema...');
    
    // Verificação de dependências globais e permissões
    if (typeof API_URL === 'undefined' || typeof loadAndApplyConfig === 'undefined') {
        showMessage('❌ Erro de inicialização. Verifique se app.js foi carregado corretamente.', 'error');
        console.error('❌ Dependências globais (API_URL ou loadAndApplyConfig) não encontradas.');
        return;
    }

    // Nota: current_user e authToken devem ser globais.
    if (!authToken || !currentUser || currentUser.role !== 'admin') {
        showMessage('❌ Acesso negado. Apenas administradores podem configurar o sistema.', 'error');
        console.error('❌ Tentativa de configuração sem permissão de admin.');
        return;
    }

    try {
        showMessage('⏳ A salvar configurações...', 'info');

        const primaryColor = document.getElementById('primaryColor').value;
        const secondaryColor = document.getElementById('secondaryColor').value;
        const newLogoFile = document.getElementById('newLogo').files[0];

        // 1. CRIA O OBJETO DE DADOS JSON com base no modelo AdminConfig do backend
        const configData = {
            primary_color: primaryColor,
            secondary_color: secondaryColor,
            // NOTA: Se o campo newLogoFile for preenchido, ele será ignorado por esta versão simplificada do frontend
            // Para manter o contrato com o backend, vamos enviar a logo_url padrão ou a URL atual
            // Para simplificar, vamos assumir que apenas as cores são configuráveis por enquanto, 
            // e a URL da logo será atualizada em uma etapa futura com lógica de upload completa.
            // Para que o backend não dê erro por falta de logo_url, vamos enviar a URL atual (se disponível).
            logo_url: window.currentConfig ? window.currentConfig.logo_url : "https://placehold.co/120x30/667eea/ffffff?text=Salão+IA" 
        };

        // Envia a requisição POST para o endpoint de configuração
        // CORREÇÃO: Endpoint ajustado para /admin/config/save conforme o app/config.py
        const response = await fetch(`${API_URL}/admin/config/save`, {
            method: 'POST',
            // Define o Content-Type como JSON
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            // Converte o objeto de dados para string JSON
            body: JSON.stringify(configData)
        });

        const data = await response.json();
        
        if (response.ok) {
            showMessage('✅ Configuração salva com sucesso! Tema aplicado.', 'success');
            console.log('✔️ Configuração salva:', data);

            // IMPORTANTE: Recarrega as configurações globalmente para aplicar as mudanças
            await loadAndApplyConfig(); 

            // Limpa o campo de ficheiro (se houver) e preview
            document.getElementById('newLogo').value = ''; 
            const previewElement = document.getElementById('newLogoPreview');
            if (previewElement) {
                previewElement.style.display = 'none';
                previewElement.src = '';
            }


        } else {
            showMessage(`❌ ${data.detail || 'Erro ao salvar a configuração'}`, 'error');
            console.error('❌ Falha ao salvar configuração:', data.detail);
        }

    } catch (error) {
        console.error('❌ Erro de conexão ou inesperado ao salvar configuração:', error);
        showMessage('❌ Erro de conexão ao salvar configuração', 'error');
    }
}