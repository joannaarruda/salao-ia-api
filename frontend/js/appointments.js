// ==================== SISTEMA DE AGENDAMENTOS ====================

let selectedTime = null;
let professionals = [];

// --- Funções de Carregamento e Seleção ---

// Carregar profissionais por tipo de serviço
async function loadProfessionals() {
    const tipoServico = document.getElementById('tipoServico').value;
    const profissionalSelect = document.getElementById('profissional');
    
    if (!tipoServico) {
        profissionalSelect.innerHTML = '<option value="">Selecione o tipo de serviço primeiro</option>';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/professionals?tipo_servico=${tipoServico}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        professionals = await response.json();
        
        profissionalSelect.innerHTML = '<option value="">Selecione um profissional</option>';
        
        // Mapeia e adiciona as opções de profissionais
        professionals.forEach(prof => {
            const option = document.createElement('option');
            option.value = prof.id;
            option.textContent = `${prof.nome} - ${prof.especialidades.join(', ')}`;
            profissionalSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Erro ao carregar profissionais:', error);
        showMessage('❌ Erro ao carregar profissionais', 'error');
    }
}

// Verificar disponibilidade de horários
async function checkAvailability() {
    const profissionalId = document.getElementById('profissional').value;
    const data = document.getElementById('dataAgendamento').value;
    const horariosDiv = document.getElementById('horariosDisponiveis');
    
    if (!profissionalId || !data) {
        horariosDiv.innerHTML = '<p class="info-text">Selecione profissional e data</p>';
        return;
    }
    
    try {
        const response = await fetch(
            `${API_URL}/appointments/available?profissional_id=${profissionalId}&data=${data}`,
            {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            }
        );
        
        const horarios = await response.json();
        
        horariosDiv.innerHTML = '';
        
        // Cria botões de horário
        horarios.forEach(horario => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `horario-btn ${horario.disponivel ? '' : 'disabled'}`;
            btn.textContent = new Date(horario.horario).toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            if (horario.disponivel) {
                btn.onclick = () => selectTime(horario.horario, btn);
            } else {
                btn.disabled = true;
            }
            
            horariosDiv.appendChild(btn);
        });
        
    } catch (error) {
        console.error('Erro ao verificar disponibilidade:', error);
        showMessage('❌ Erro ao verificar disponibilidade', 'error');
    }
}

// Selecionar horário
function selectTime(time, button) {
    // Remove seleção anterior e adiciona a nova
    document.querySelectorAll('.horario-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    button.classList.add('selected');
    selectedTime = time;
}

// Configurar data mínima (hoje)
document.addEventListener('DOMContentLoaded', () => {
    const dataInput = document.getElementById('dataAgendamento');
    if (dataInput) {
        const hoje = new Date().toISOString().split('T')[0];
        dataInput.setAttribute('min', hoje);
    }
});

// --- Criação de Agendamento ---

// Submit do formulário de agendamento
document.getElementById('appointmentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 1. VERIFICAÇÕES PRÉVIAS
    if (!currentUser || !authToken) { 
        showMessage('❌ Faça login para criar um agendamento.', 'error');
        return;
    }

    if (!selectedTime) {
        showMessage('❌ Selecione um horário', 'error');
        return;
    }
    
    // OBTENÇÃO E CONVERSÃO DE DADOS (Correções para o erro 422)
    const clienteId = parseInt(currentUser.id); // Garante que o ID do Cliente é INT
    if (isNaN(clienteId)) {
        showMessage('❌ Erro: ID de Cliente inválido (NaN).', 'error');
        return;
    }

    const tipoServico = document.getElementById('tipoServico').value;
    const profissionalId = document.getElementById('profissional').value;
    if (!profissionalId || profissionalId.trim() === "") {
    showMessage('❌ Selecione um profissional', 'error');
    return;
    }
    
    
    // Garante que o array de serviços não inclua strings vazias
    const servicosEscolhidos = document.getElementById('servicosEscolhidos').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0); 
    if (!servicosEscolhidos || servicosEscolhidos.length === 0) {
    showMessage('❌ Selecione pelo menos um serviço', 'error');
    return;
}
    
    // 2. REQUISIÇÃO POST
    try {
        showMessage('⏳ Criando agendamento...', 'info');
        
        const response = await fetch(`${API_URL}/appointments/`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                cliente_id: clienteId, 
                profissional_id: profissionalId, // Garante que o ID do Profissional é INT
                tipo_servico: tipoServico,
                servico: servicosEscolhidos[0] || tipoServico,
                data_hora: selectedTime,
                servicos_escolhidos: servicosEscolhidos
            })
        });

        // 3. TRATAMENTO DA RESPOSTA
        const responseText = await response.text();
        const data = responseText ? JSON.parse(responseText) : {};
        
        if (response.ok) {
            showMessage('✅ Agendamento realizado com sucesso!', 'success');
            
            // Limpar formulário e navegar
            document.getElementById('appointmentForm').reset();
            selectedTime = null;
            
            setTimeout(loadMyAppointments, 2000);
            
        } else {
            // TRATAMENTO DE ERRO MELHORADO (422)
            let errorMessage = 'Erro ao criar agendamento. Verifique o console.';
            
            if (data.detail) {
                if (Array.isArray(data.detail) && data.detail.length > 0) {
                    const firstError = data.detail[0];
                    const loc = firstError.loc ? firstError.loc.join('.') : 'campo desconhecido';
                    errorMessage = `Erro de validação no campo: ${loc}. Detalhe: ${firstError.msg}`;
                } else if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                }
            }

            console.error('Detalhes da Falha (422 ou outro):', data.detail || responseText);
            showMessage(`❌ ${errorMessage}`, 'error');
        }
        
    } catch (error) {
        console.error('Erro geral na requisição:', error);
        showMessage('❌ Erro inesperado ao criar agendamento', 'error');
    }
});

// --- Visualização de Agendamentos ---

// --- Carregar meus agendamentos ---
async function loadMyAppointments() {
    showScreen('myAppointmentsScreen');

    const appointmentsList = document.getElementById('appointmentsList');
    appointmentsList.innerHTML = '<div class="loading"><div class="spinner"></div><p>Carregando...</p></div>';

    try {
        const response = await fetch(`${API_URL}/appointments/my`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const appointments = await response.json();

        if (!appointments || appointments.length === 0) {
            appointmentsList.innerHTML = '<p class="info-text">Você ainda não tem agendamentos</p>';
            return;
        }

        // Renderiza a lista de agendamentos com proteção contra valores undefined
        appointmentsList.innerHTML = appointments.map(apt => {
           const dataHora = apt.data_hora ? new Date(apt.data_hora) : new Date();
           const profissionalObj = professionals.find(prof => prof.id == apt.profissional_id);
           const nomeProfissional = profissionalObj ? profissionalObj.nome : 'Profissional Não Encontrado';
           const tipoServico = apt.servico || 'SERVIÇO';
           const servicosDetalhes = apt.servico || '-'; 
        
        const status = apt.status || 'PENDENTE';

        return `
            <div class="appointment-card">
                <h4>${tipoServico.toLowerCase().includes('corte') || tipoServico.toLowerCase().includes('cabelo') ? '💇‍♀️' : '💅'} ${tipoServico.toUpperCase()}</h4>
                <p><strong>📅 Data:</strong> ${dataHora.toLocaleDateString('pt-BR')}</p>
                <p><strong>🕐 Horário:</strong> ${dataHora.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}</p>
                <p><strong>👤 Profissional:</strong> ${nomeProfissional}</p>
                <p><strong>✨ Serviços:</strong> ${servicosDetalhes}</p>
                <span class="status ${status.toLowerCase()}">${status.toUpperCase()}</span>
            </div>
        `;
        }).join('');

    } catch (error) {
        console.error('Erro ao carregar agendamentos:', error);
        appointmentsList.innerHTML = '<p class="info-text">Erro ao carregar agendamentos</p>';
    }
}


// --- Menu de Navegação ---

// Mostrar menu rápido quando logado
function updateQuickMenu() {
    const quickMenu = document.getElementById('quickMenu');
    if (currentUser) {
        quickMenu.style.display = 'flex';
    } else {
        quickMenu.style.display = 'none';
    }
}