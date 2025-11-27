// ADICIONAR suporte para FormData (upload de logo)

async function handleConfigSubmit(e) {
    e.preventDefault();
    
    if (!authToken || !currentUser || currentUser.role !== 'admin') {
        showMessage('Acesso negado. Apenas administradores.', 'error');
        return;
    }
    
    const primaryColor = document.getElementById('primaryColor').value;
    const secondaryColor = document.getElementById('secondaryColor').value;
    const logoFile = document.getElementById('newLogo').files[0];
    
    // Usa FormData para enviar arquivo
    const formData = new FormData();
    formData.append('primary_color', primaryColor);
    formData.append('secondary_color', secondaryColor);
    
    if (logoFile) {
        formData.append('logo_file', logoFile);
    }
    
    try {
        const response = await fetch(`${API_URL}/settings/complete`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
                // NÃO adicionar Content-Type - browser define automaticamente
            },
            body: formData
        });
        
        if (response.ok) {
            showMessage('Configuração salva!', 'success');
            await AppTheme.refresh(); // Reaplica tema
        } else {
            const data = await response.json();
            showMessage(data.detail || 'Erro ao salvar', 'error');
        }
    } catch (error) {
        showMessage('Erro de conexão', 'error');
    }
}