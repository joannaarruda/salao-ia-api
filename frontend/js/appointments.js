// MÚLTIPLOS SERVIÇOS
let selectedServices = [];

function addService() {
    const tipoSelect = document.getElementById('tipoServico');
    const descricao = document.getElementById('descricaoServico').value;
    const duracao = parseInt(document.getElementById('duracaoServico').value) || 60;
    
    if (!tipoSelect.value) {
        showMessage('Selecione um tipo de serviço', 'error');
        return;
    }
    
    const service = {
        tipo: tipoSelect.value,
        descricao: descricao,
        duracao_estimada: duracao
    };
    
    selectedServices.push(service);
    renderSelectedServices();
    
    // Limpa campos
    descricao.value = '';
    duracaoServico.value = '60';
}

function renderSelectedServices() {
    const container = document.getElementById('selectedServicesList');
    
    if (selectedServices.length === 0) {
        container.innerHTML = '<p class="info-text">Nenhum serviço adicionado</p>';
        return;
    }
    
    container.innerHTML = selectedServices.map((service, index) => `
        <div class="service-item">
            <div>
                <strong>${service.tipo.toUpperCase()}</strong>
                ${service.descricao ? `<br><small>${service.descricao}</small>` : ''}
                <br><small>Duração: ${service.duracao_estimada} min</small>
            </div>
            <button onclick="removeService(${index})" class="btn-remove">×</button>
        </div>
    `).join('');
    
    // Atualiza duração total
    const duracaoTotal = selectedServices.reduce((sum, s) => sum + s.duracao_estimada, 0);
    document.getElementById('duracaoTotal').textContent = `Duração total: ${duracaoTotal} min`;
}

function removeService(index) {
    selectedServices.splice(index, 1);
    renderSelectedServices();
}

// OPÇÃO DE IA
function toggleIA() {
    const checkbox = document.getElementById('usarIA');
    const preferencesDiv = document.getElementById('preferenciasIA');
    
    if (checkbox.checked) {
        preferencesDiv.style.display = 'block';
    } else {
        preferencesDiv.style.display = 'none';
    }
}

// SUBMIT MODIFICADO
async function submitAppointment(e) {
    e.preventDefault();
    
    if (selectedServices.length === 0) {
        showMessage('Adicione pelo menos um serviço', 'error');
        return;
    }
    
    if (!selectedTime) {
        showMessage('Selecione um horário', 'error');
        return;
    }
    
    const appointmentData = {
        profissional_id: document.getElementById('profissional').value,
        data_hora: selectedTime,
        servicos: selectedServices,
        usar_ia: document.getElementById('usarIA').checked,
        preferencias_ia: document.getElementById('preferenciasIA').value || null,
        observacoes: document.getElementById('observacoes').value || null,
        requer_consulta: document.getElementById('requerConsulta').checked,
        requer_teste_mecha: document.getElementById('requerTesteMecha').checked
    };
    
    try {
        const response = await fetch(`${API_URL}/appointments/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(appointmentData)
        });
        
        if (response.ok) {
            showMessage('Agendamento criado!', 'success');
            selectedServices = [];
            renderSelectedServices();
            // ... resto do código
        }
    } catch (error) {
        showMessage('Erro ao criar agendamento', 'error');
    }
}