// =============================================================
// SISTEMA DE TESTE DE MECHA
// Adicionar ao index_final_completo.html
// =============================================================

/**
 * Exibe modal para registrar teste de mecha
 * @param {string} appointmentId - ID do agendamento
 * @param {string} clientName - Nome do cliente
 */
function showStrandTestModal(appointmentId, clientName) {
    const existing = document.getElementById('strandTestModal');
    if (existing) existing.remove();
    
    const modal = document.createElement('div');
    modal.id = 'strandTestModal';
    modal.className = 'modal active';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 2px solid #e2e8f0;">
                <h2 style="color: #667eea; margin: 0;">🧪 Teste de Mecha</h2>
                <button onclick="closeStrandTestModal()" style="background: #f56565; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 22px; font-weight: bold;">×</button>
            </div>
            
            <div style="background: #f7fafc; padding: 18px; border-radius: 12px; margin-bottom: 25px;">
                <strong style="color: #2d3748; font-size: 16px;">👤 Cliente: ${clientName}</strong>
            </div>
            
            <div class="alert alert-info" style="margin-bottom: 25px;">
                <strong>ℹ️ Importante:</strong> O teste de mecha deve ser realizado 48h antes do procedimento químico para verificar possíveis reações alérgicas.
            </div>
            
            <form id="strandTestForm">
                <div style="margin-bottom: 25px;">
                    <label style="display: block; font-weight: 700; color: #2d3748; margin-bottom: 12px; font-size: 15px;">
                        1. O teste de mecha foi realizado?
                    </label>
                    <div style="display: flex; gap: 15px;">
                        <label style="flex: 1; padding: 15px; border: 2px solid #e2e8f0; border-radius: 12px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 10px;">
                            <input type="radio" name="test_done" value="sim" required onchange="toggleTestResult()">
                            <span style="font-weight: 600;">✅ Sim</span>
                        </label>
                        <label style="flex: 1; padding: 15px; border: 2px solid #e2e8f0; border-radius: 12px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 10px;">
                            <input type="radio" name="test_done" value="nao" required onchange="toggleTestResult()">
                            <span style="font-weight: 600;">❌ Não</span>
                        </label>
                    </div>
                </div>
                
                <div id="testResultSection" style="display: none; margin-bottom: 25px;">
                    <label style="display: block; font-weight: 700; color: #2d3748; margin-bottom: 12px; font-size: 15px;">
                        2. Qual foi o resultado do teste?
                    </label>
                    <div style="display: flex; gap: 15px;">
                        <label style="flex: 1; padding: 15px; border: 2px solid #e2e8f0; border-radius: 12px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 10px; background: #f0fff4;">
                            <input type="radio" name="test_result" value="aprovado">
                            <span style="font-weight: 600; color: #22543d;">✅ Aprovado<br><small style="font-weight: 400; color: #2f855a;">Sem reações alérgicas</small></span>
                        </label>
                        <label style="flex: 1; padding: 15px; border: 2px solid #e2e8f0; border-radius: 12px; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 10px; background: #fff5f5;">
                            <input type="radio" name="test_result" value="reprovado">
                            <span style="font-weight: 600; color: #742a2a;">⚠️ Reprovado<br><small style="font-weight: 400; color: #c53030;">Cliente apresentou reação</small></span>
                        </label>
                    </div>
                </div>
                
                <div id="notDoneWarning" style="display: none; margin-bottom: 25px;">
                    <div class="alert alert-warning">
                        <strong>⚠️ Atenção:</strong> Para procedimentos químicos, o teste de mecha é obrigatório. Não é recomendado prosseguir sem o teste.
                    </div>
                </div>
                
                <div id="failedWarning" style="display: none; margin-bottom: 25px;">
                    <div class="alert alert-danger">
                        <strong>🚨 ALERTA:</strong> Cliente apresentou reação alérgica no teste de mecha. NÃO prossiga com o procedimento químico! Recomende que o cliente consulte um dermatologista.
                    </div>
                </div>
                
                <div style="margin-bottom: 25px;">
                    <label style="display: block; font-weight: 700; color: #2d3748; margin-bottom: 12px; font-size: 15px;">
                        Observações sobre o teste (opcional)
                    </label>
                    <textarea id="testObservations" rows="3" style="width: 100%; padding: 14px; border: 2px solid #e2e8f0; border-radius: 12px; font-family: inherit; font-size: 14px; resize: vertical;" placeholder="Ex: Teste realizado na nuca, sem vermelhidão após 48h..."></textarea>
                </div>
                
                <div style="display: flex; gap: 12px;">
                    <button type="button" onclick="closeStrandTestModal()" class="button-secondary" style="flex: 1;">
                        Cancelar
                    </button>
                    <button type="submit" class="button-primary" style="flex: 2;">
                        💾 Salvar Teste de Mecha
                    </button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Event listener do form
    document.getElementById('strandTestForm').onsubmit = async (e) => {
        e.preventDefault();
        await saveStrandTest(appointmentId);
    };
}

function toggleTestResult() {
    const testDone = document.querySelector('input[name="test_done"]:checked')?.value;
    const resultSection = document.getElementById('testResultSection');
    const notDoneWarning = document.getElementById('notDoneWarning');
    const failedWarning = document.getElementById('failedWarning');
    
    if (testDone === 'sim') {
        resultSection.style.display = 'block';
        notDoneWarning.style.display = 'none';
    } else {
        resultSection.style.display = 'none';
        notDoneWarning.style.display = 'block';
    }
    
    failedWarning.style.display = 'none';
    
    // Event listener para resultado
    document.querySelectorAll('input[name="test_result"]').forEach(radio => {
        radio.onchange = () => {
            if (radio.value === 'reprovado' && radio.checked) {
                failedWarning.style.display = 'block';
            } else {
                failedWarning.style.display = 'none';
            }
        };
    });
}

async function saveStrandTest(appointmentId) {
    const testDone = document.querySelector('input[name="test_done"]:checked')?.value;
    const testResult = document.querySelector('input[name="test_result"]:checked')?.value;
    const observations = document.getElementById('testObservations').value;
    
    if (!testDone) {
        alert('⚠️ Por favor, indique se o teste foi realizado');
        return;
    }
    
    if (testDone === 'sim' && !testResult) {
        alert('⚠️ Por favor, indique o resultado do teste');
        return;
    }
    
    // Validação crítica
    if (testResult === 'reprovado') {
        const confirmCancel = confirm(
            '⚠️ ATENÇÃO!\n\n' +
            'O cliente apresentou reação alérgica no teste de mecha.\n\n' +
            'Recomendamos CANCELAR este agendamento e orientar o cliente a procurar um dermatologista.\n\n' +
            'Deseja cancelar o agendamento agora?'
        );
        
        if (confirmCancel) {
            await cancelAppointmentWithReason(appointmentId, 'Cliente reprovou no teste de mecha - reação alérgica');
            closeStrandTestModal();
            return;
        }
    }
    
    const strandTestData = {
        test_done: testDone === 'sim',
        test_result: testResult || null,
        test_approved: testResult === 'aprovado',
        observations: observations,
        tested_at: new Date().toISOString(),
        tested_by: JSON.parse(localStorage.getItem('user')).id
    };
    
    try {
        const response = await fetch(`${API_BASE}/appointments/${appointmentId}/strand-test`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(strandTestData)
        });
        
        if (!response.ok) {
            throw new Error('Erro ao salvar teste de mecha');
        }
        
        alert('✅ Teste de mecha registrado com sucesso!');
        closeStrandTestModal();
        loadProfessionalAppointments();
        
    } catch (error) {
        console.error('❌ Erro:', error);
        alert('Erro ao salvar teste de mecha. Tente novamente.');
    }
}

function closeStrandTestModal() {
    const modal = document.getElementById('strandTestModal');
    if (modal) modal.remove();
}

async function cancelAppointmentWithReason(appointmentId, reason) {
    try {
        const response = await fetch(`${API_BASE}/appointments/${appointmentId}/cancel`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ motivo: reason })
        });
        
        if (!response.ok) {
            throw new Error('Erro ao cancelar agendamento');
        }
        
        alert('✅ Agendamento cancelado por segurança do cliente');
        loadProfessionalAppointments();
        
    } catch (error) {
        console.error('❌ Erro:', error);
        alert('Erro ao cancelar agendamento');
    }
}

/**
 * Renderiza badge do status do teste de mecha
 */
function renderStrandTestBadge(strandTest) {
    if (!strandTest || !strandTest.test_done) {
        return '<span style="padding: 4px 10px; background: #e2e8f0; color: #4a5568; border-radius: 12px; font-size: 11px; font-weight: 600;">🧪 Teste pendente</span>';
    }
    
    if (!strandTest.test_approved) {
        return '<span style="padding: 4px 10px; background: #fed7d7; color: #c53030; border-radius: 12px; font-size: 11px; font-weight: 600;">⚠️ Reprovado</span>';
    }
    
    return '<span style="padding: 4px 10px; background: #c6f6d5; color: #22543d; border-radius: 12px; font-size: 11px; font-weight: 600;">✅ Aprovado</span>';
}

/**
 * Verifica se pode prosseguir com procedimento químico
 */
function canProceedWithChemical(appointment) {
    // Se tem teste de mecha e foi reprovado
    if (appointment.teste_mecha && appointment.teste_mecha.test_done && !appointment.teste_mecha.test_approved) {
        return false;
    }
    
    // Se tem questionário médico com riscos
    const medicalData = appointment.questionario_medico || appointment.medical_questionnaire;
    if (medicalData && (medicalData.q2 === 'sim' || medicalData.q4 === 'sim')) {
        return false;
    }
    
    return true;
}

// =============================================================
// EXPORT PARA USO
// =============================================================

window.showStrandTestModal = showStrandTestModal;
window.closeStrandTestModal = closeStrandTestModal;
window.renderStrandTestBadge = renderStrandTestBadge;
window.canProceedWithChemical = canProceedWithChemical;
