/**
 * PROFESSIONAL.JS - PAINEL DO PROFISSIONAL
 * =========================================
 * 🚨 Nota: Assumimos que API_URL, showMessage, formatDate, formatTime
 * e getClientName (se for um mock) são funções globais definidas noutros ficheiros (ex: api.js)
 */

// CARREGAR AGENDA DO DIA
async function loadProfessionalSchedule(data) {
    if (!data) {
        data = new Date().toISOString().split('T')[0];
    }
    
    // 🚨 CORREÇÃO: Obter token diretamente da fonte correta
    const token = localStorage.getItem('access_token'); 
    if (!token) {
        showMessage('Sessão expirada. Por favor, faça login.', 'error');
        // Redireciona para login (Assumindo que window.logout() é global)
        if (typeof window.logout === 'function') window.logout(); 
        return;
    }
    
    try {
        const response = await fetch(
            `${API_URL}/appointments/professional/schedule?data=${data}`,
            {
                // ✅ Usar o token localmente
                headers: { 'Authorization': `Bearer ${token}` } 
            }
        );
        
        // Verifica status da resposta
        if (response.status === 401) {
            throw new Error('Não autorizado. O token é inválido.');
        }
        
        const schedule = await response.json();
        renderSchedule(schedule);
        
    } catch (error) {
        showMessage(error.message || 'Erro ao carregar agenda', 'error');
    }
}

function renderSchedule(schedule) {
    const container = document.getElementById('scheduleContainer');
    
    container.innerHTML = `
        <h3>📅 Agenda do dia ${formatDate(schedule.data)}</h3>
        <p>Total de agendamentos: ${schedule.total_agendamentos}</p>
        
        <div class="appointments-list">
            ${schedule.agendamentos.map(apt => renderAppointmentCard(apt)).join('')}
        </div>
        
        <h4>Horários Disponíveis:</h4>
        <div class="available-times">
            ${schedule.horarios_disponiveis.map(h => `
                <span class="time-badge available">${formatTime(h)}</span>
            `).join('')}
        </div>
    `;
}

function renderAppointmentCard(appointment) {
    const statusClass = appointment.status.toLowerCase();
    const statusText = {
        'pendente': 'Aguardando confirmação',
        'confirmado': 'Confirmado',
        'em_atendimento': 'Em atendimento',
        'concluido': 'Concluído',
        'cancelado': 'Cancelado'
    }[appointment.status];
    
    return `
        <div class="appointment-card ${statusClass}">
            <div class="appointment-header">
                <h4>${formatTime(appointment.data_hora)}</h4>
                <span class="status-badge ${statusClass}">${statusText}</span>
            </div>
            
            <div class="appointment-body">
                <p><strong>Cliente:</strong> ${getClientName(appointment.cliente_id)}</p>
                
                <div class="services-list">
                    <strong>Serviços:</strong>
                    ${appointment.servicos.map(s => `
                        <div class="service-item-small">
                            ${s.tipo} ${s.descricao ? `- ${s.descricao}` : ''}
                            (${s.duracao_estimada} min)
                        </div>
                    `).join('')}
                </div>
                
                ${appointment.usar_ia ? '<span class="ia-badge">✨ Com IA</span>' : ''}
                ${appointment.observacoes ? `<p class="obs">${appointment.observacoes}</p>` : ''}
            </div>
            
            <div class="appointment-actions">
                ${getAppointmentActions(appointment)}
            </div>
        </div>
    `;
}

function getAppointmentActions(appointment) {
    if (appointment.status === 'pendente') {
        return `
            <button onclick="confirmAppointment('${appointment.id}')" class="btn-primary">
                ✓ Confirmar
            </button>
            <button onclick="cancelAppointment('${appointment.id}')" class="btn-secondary">
                × Cancelar
            </button>
        `;
    }
    
    if (appointment.status === 'confirmado') {
        return `
            <button onclick="startAttendance('${appointment.id}')" class="btn-primary">
                ▶ Iniciar Atendimento
            </button>
        `;
    }
    
    if (appointment.status === 'em_atendimento') {
        return `
            <button onclick="finishAttendance('${appointment.id}')" class="btn-primary">
                ✓ Finalizar e Registrar
            </button>
        `;
    }
    
    if (appointment.status === 'concluido') {
        return `
            <button onclick="viewAttendanceRecord('${appointment.id}')" class="btn-secondary">
                📋 Ver Ficha
            </button>
        `;
    }
    
    return '';
}

// CONFIRMAR AGENDAMENTO
async function confirmAppointment(appointmentId) {
    const token = localStorage.getItem('access_token'); 
    if (!token) return showMessage('Não autorizado', 'error');
    
    try {
        const response = await fetch(
            `${API_URL}/appointments/${appointmentId}/status`,
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // ✅ Usar token local
                },
                body: JSON.stringify({ new_status: 'confirmado' })
            }
        );
        
        if (response.ok) {
            showMessage('Agendamento confirmado!', 'success');
            loadProfessionalSchedule();
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Erro ao confirmar agendamento');
        }
    } catch (error) {
        showMessage(error.message || 'Erro ao confirmar', 'error');
    }
}

// CANCELAR AGENDAMENTO (Adicionado para completude)
async function cancelAppointment(appointmentId) {
    const token = localStorage.getItem('access_token'); 
    if (!token) return showMessage('Não autorizado', 'error');

    try {
        const response = await fetch(
            `${API_URL}/appointments/${appointmentId}/status`,
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ new_status: 'cancelado' })
            }
        );
        
        if (response.ok) {
            showMessage('Agendamento cancelado!', 'info');
            loadProfessionalSchedule();
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Erro ao cancelar agendamento');
        }
    } catch (error) {
        showMessage(error.message || 'Erro ao cancelar', 'error');
    }
}

// INICIAR ATENDIMENTO
async function startAttendance(appointmentId) {
    const token = localStorage.getItem('access_token'); 
    if (!token) return showMessage('Não autorizado', 'error');
    
    try {
        const response = await fetch(
            `${API_URL}/appointments/${appointmentId}/status`,
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // ✅ Usar token local
                },
                body: JSON.stringify({ new_status: 'em_atendimento' })
            }
        );
        
        if (response.ok) {
            showMessage('Atendimento iniciado!', 'success');
            loadProfessionalSchedule();
        } else {
             const data = await response.json();
            throw new Error(data.detail || 'Erro ao iniciar atendimento');
        }
    } catch (error) {
        showMessage(error.message || 'Erro ao iniciar atendimento', 'error');
    }
}

// FINALIZAR E CRIAR FICHA
async function finishAttendance(appointmentId) {
    // Abre modal para registro
    showAttendanceModal(appointmentId);
}

function showAttendanceModal(appointmentId) {
    const modal = document.getElementById('attendanceModal');
    modal.style.display = 'block';
    modal.dataset.appointmentId = appointmentId;
}

// SALVAR FICHA DE ATENDIMENTO
async function saveAttendanceRecord() {
    const token = localStorage.getItem('access_token'); 
    if (!token) return showMessage('Não autorizado', 'error');
    
    const appointmentId = document.getElementById('attendanceModal').dataset.appointmentId;
    
    const recordData = {
        appointment_id: appointmentId,
        cliente_id: getCurrentClientId(appointmentId), // ⚠️ Funções auxiliares (getCurrentClientId, getSelectedProducts, etc.) assumidas como globais.
        procedimento: {
            produtos_utilizados: getSelectedProducts(),
            tecnicas_aplicadas: getSelectedTechniques(),
            tempo_processamento: parseInt(document.getElementById('tempoProcessamento').value),
            observacoes_tecnicas: document.getElementById('observacoesTecnicas').value,
            fotos_antes: [],
            fotos_depois: [],
            pode_publicar_fotos: document.getElementById('podePublicar').checked
        },
        proxima_recomendacao: document.getElementById('proximaRecomendacao').value,
        cronograma_tratamento: getCronogramaTratamento()
    };
    
    try {
        const response = await fetch(`${API_URL}/attendance/records`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // ✅ Usar token local
            },
            body: JSON.stringify(recordData)
        });
        
        if (response.ok) {
            showMessage('Ficha registrada com sucesso!', 'success');
            document.getElementById('attendanceModal').style.display = 'none';
            loadProfessionalSchedule();
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Erro ao salvar ficha');
        }
    } catch (error) {
        showMessage(error.message || 'Erro ao salvar ficha', 'error');
    }
}

// MÚLTIPLOS SERVIÇOS E FUNÇÕES AUXILIARES (Deixadas como estavam)
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
    
    const token = localStorage.getItem('access_token'); 
    if (!token) return showMessage('Não autorizado', 'error');
    
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
                'Authorization': `Bearer ${token}` // ✅ Usar token local
            },
            body: JSON.stringify(appointmentData)
        });
        
        if (response.ok) {
            showMessage('Agendamento criado!', 'success');
            selectedServices = [];
            renderSelectedServices();
            // ... resto do código
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Erro ao criar agendamento');
        }
    } catch (error) {
        showMessage(error.message || 'Erro ao criar agendamento', 'error');
    }
}