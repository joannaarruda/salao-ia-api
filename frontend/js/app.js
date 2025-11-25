// ==================== CONFIGURAÇÃO GLOBAL ====================
// A URL AGORA INCLUI O /v1 PARA ALINHAR COM O BACKEND DO FASTAPI
const API_URL = 'http://localhost:8000/api/v1'; 
let currentUser = null; // Objeto do usuário logado
let authToken = null; // Token de autenticação
let isLoginMode = true; // Define o modo inicial como 'Entrar'

// ==================== UTILITÁRIOS E NAVEGAÇÃO ====================

/**
 * Exibe uma tela específica e oculta as outras.
 * Também gerencia a visibilidade do menu rápido.
 * @param {string} screenId O ID da tela a ser mostrada.
 */
function showScreen(screenId) {
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        screen.classList.remove('active');
    });
    
    document.getElementById(screenId).classList.add('active');
    
    // Atualiza o menu rápido (mostra ou oculta conforme a tela)
    const quickMenu = document.getElementById('quickMenu');
    if (screenId !== 'authScreen') {
        quickMenu.style.display = 'flex';
        // Se estiver na tela de agendamentos, garante que o formulário está limpo
        if (screenId === 'scheduleScreen') {
            document.getElementById('tipoServico').value = '';
            document.getElementById('profissional').innerHTML = '<option value="">Selecione o tipo de serviço primeiro</option>';
            document.getElementById('timesGrid').innerHTML = '<p class="info-text">Selecione o profissional e a data.</p>';
        }
    } else {
        quickMenu.style.display = 'none';
    }
}

/**
 * Exibe uma mensagem flutuante (não usar alert!).
 * @param {string} message A mensagem a ser exibida.
 * @param {'success'|'error'|'info'} type O tipo de mensagem para estilização.
 */
function showMessage(message, type = 'info') {
    // Remover mensagens antigas
    const oldMessages = document.querySelectorAll('.message');
    oldMessages.forEach(msg => msg.remove());
    
    // Criar nova mensagem
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // Remover após 5 segundos
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

/**
 * Atualiza o menu do utilizador e a mensagem de boas-vindas após o login.
 */
function updateUserMenu() {
    const userMenu = document.getElementById('userMenu');
    const userNameSpan = document.getElementById('userName');
    const welcomeNameSpan = document.getElementById('welcomeName');
    
    if (currentUser && userMenu) {
        // Exibe o nome ou email do usuário no menu
        userNameSpan.textContent = currentUser.nome || currentUser.email;
        // Exibe o nome ou email do usuário na tela de upload
        welcomeNameSpan.textContent = currentUser.nome || currentUser.email;
        userMenu.style.display = 'flex';
    } else if (userMenu) {
        userMenu.style.display = 'none';
    }
}

// ==================== TESTE DE CONEXÃO ====================

/**
 * Testa a conexão com o backend da API.
 */
async function testConnection() {
    console.log('🔍 Testando conexão com API...');
    try {
        // Tenta acessar o endpoint de saúde/status da API
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        console.log('✅ API conectada:', data);
        showMessage('✅ API conectada com sucesso!', 'success');
        return true;
    } catch (error) {
        console.error('❌ Erro ao conectar com API:', error);
        showMessage('⚠️ API não está rodando ou o endereço está incorreto (http://localhost:8000/health).', 'error');
        return false;
    }
}

// ==================== AUTENTICAÇÃO LÓGICA ====================

/**
 * Alterna entre o modo de Login e Registro.
 * @param {Event} event O evento de clique.
 */
window.toggleAuthMode = function(event) {
    if (event) event.preventDefault();
    isLoginMode = !isLoginMode;
    
    const authTitle = document.getElementById('authTitle');
    const registerFields = document.getElementById('registerFields');
    const submitButton = document.querySelector('#authForm button[type="submit"]');
    const toggleText = document.getElementById('authToggleText');
    const toggleLink = document.querySelector('.auth-toggle a');
    
    if (isLoginMode) {
        authTitle.textContent = 'Entrar';
        registerFields.style.display = 'none';
        submitButton.textContent = 'Entrar';
        toggleText.textContent = 'Não tem conta?';
        toggleLink.textContent = 'Criar conta';
    } else {
        authTitle.textContent = 'Criar Conta';
        registerFields.style.display = 'block';
        submitButton.textContent = 'Registrar';
        toggleText.textContent = 'Já tem conta?';
        toggleLink.textContent = 'Entrar';
    }
}

/**
 * Função principal para lidar com o envio do formulário de Login ou Registro.
 */
async function handleAuthSubmit(event) {
    event.preventDefault();

    const isRegistering = !isLoginMode; 
    const url = isRegistering ? `${API_URL}/auth/register` : `${API_URL}/auth/login`; 
    
    // 1. Coletar os dados do formulário
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    let bodyData;

    if (isRegistering) {
        // Se for registo, coletar todos os campos
        const nome = document.getElementById('nome').value;
        const telefone = document.getElementById('telefone').value;
        const morada = document.getElementById('morada').value;
        
        bodyData = {
            nome: nome,
            telefone: telefone,
            email: email,
            morada: morada,
            senha: senha
        };
    } else {
        // Se for login
        bodyData = {
            email: email,
            senha: senha
        };
    }

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyData),
        });

        const data = await response.json();

        if (!response.ok) {
            // Erro retornado pela API (e.g., email já existe, credenciais inválidas)
            showMessage(data.detail || "Erro desconhecido na autenticação/registro.", 'error'); 
            return;
        }

        // Sucesso (200/201)
        if (isRegistering) {
            // Após registro bem-sucedido
            showMessage("Conta criada com sucesso! Faça login.", 'success');
            toggleAuthMode(); // Muda para o modo Login
        } else {
            // Após login bem-sucedido
            const token = data.access_token;
            authToken = token; // Armazena o token globalmente
            localStorage.setItem("authToken", token); // Armazena o token no LocalStorage
            
            // Buscar detalhes completos do usuário logado
            const userResponse = await fetch(`${API_URL}/users/me`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            if (userResponse.ok) {
                const userData = await userResponse.json();
                currentUser = userData; // Armazena o usuário globalmente
                localStorage.setItem('currentUser', JSON.stringify(userData));
                
                showMessage(`👋 Bem-vindo(a), ${currentUser.nome || currentUser.email}!`, 'success');
                updateUserMenu();
                showScreen('uploadScreen'); // Vai para a tela principal
            } else {
                // Isso deve ser tratado como um erro grave, apesar do login ter funcionado
                console.error("Login ok, mas falha ao buscar dados do usuário. Token inválido ou endpoint de 'me' indisponível.");
                showMessage("Login bem-sucedido, mas falha ao carregar seus dados.", 'error');
            }
        }
    } catch (error) {
        console.error("Erro de Rede ou Processamento:", error);
        showMessage(error.message || "Ocorreu um erro de rede. Verifique a conexão com a API.", 'error');
    }
}

/**
 * Função de logout.
 */
window.logout = function() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
    showMessage("Você saiu da sua conta.", 'info');
    updateUserMenu();
    showScreen('authScreen');
}


// ==================== INICIALIZAÇÃO DA APLICAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Aplicação iniciada!');
    
    // 1. Testar conexão com a API
    testConnection();
    
    // 2. Adicionar listener de submit ao formulário de autenticação
    const authForm = document.getElementById('authForm');
    if (authForm) {
        authForm.addEventListener('submit', handleAuthSubmit);
    }
    
    // 3. Verificar se já está logado
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        updateUserMenu();
        showScreen('uploadScreen'); // Vai para a tela principal
        console.log('👤 Usuário já logado:', currentUser.nome || currentUser.email);
    } else {
        // Se não houver token, garantir que está na tela de autenticação
        showScreen('authScreen');
        console.log('🔓 Nenhum usuário logado');
    }
});