// ==================== CONFIGURAÇÃO CORRIGIDA ====================
// A URL AGORA INCLUI O /v1 PARA ALINHAR COM O BACKEND DO FASTAPI
const API_URL = 'http://localhost:8000/api/v1'; 
let currentUser = null;
let authToken = null;

// ==================== AUTENTICAÇÃO ====================

// Modo de autenticação (login/registro)
let isLoginMode = true;

function toggleAuthMode(event) {
    event.preventDefault();
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
        submitButton.textContent = 'Criar Conta';
        toggleText.textContent = 'Já tem conta?';
        toggleLink.textContent = 'Entrar';
    }
}

// Submit do formulário de autenticação
document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    if (isLoginMode) {
        await login(email, senha);
    } else {
        const nome = document.getElementById('nome').value;
        const telefone = document.getElementById('telefone').value;
        const morada = document.getElementById('morada').value;
        await register(nome, telefone, email, morada, senha);
    }
});

async function register(nome, telefone, email, morada, senha) {
    try {
        // O URL agora é ${API_URL}/auth/register => http://localhost:8000/api/v1/auth/register
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nome,
                telefone,
                email,
                morada,
                senha
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Conta criada com sucesso! Faça login.', 'success');
            toggleAuthMode(new Event('click'));
        } else {
            showMessage(data.detail || 'Erro ao criar conta', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao conectar com o servidor. Certifique-se que a API está rodando.', 'error');
    }
}

async function login(email, senha) {
    try {
        // O URL agora é ${API_URL}/auth/login => http://localhost:8000/api/v1/auth/login
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, senha })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            showMessage('Login realizado com sucesso!', 'success');
            showScreen('uploadScreen');
            updateUserMenu();
        } else {
            showMessage(data.detail || 'Erro ao fazer login', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao conectar com o servidor. Certifique-se que a API está rodando.', 'error');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    showScreen('authScreen');
    updateUserMenu();
    showMessage('Logout realizado com sucesso!', 'success');
}

function updateUserMenu() {
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');
    
    if (currentUser) {
        userName.textContent = currentUser.nome;
        userMenu.style.display = 'flex';
    } else {
        userMenu.style.display = 'none';
    }
}

// ==================== NAVEGAÇÃO ====================

function showScreen(screenId) {
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
        screen.classList.remove('active');
    });
    
    document.getElementById(screenId).classList.add('active');
}

// ==================== MENSAGENS ====================

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

// ==================== INICIALIZAÇÃO ====================

// Verificar se já está logado
document.addEventListener('DOMContentLoaded', () => {
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showScreen('uploadScreen');
        updateUserMenu();
    }
});

// ==================== TESTE DE CONEXÃO ====================

async function testConnection() {
    try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        console.log('✅ API conectada:', data);
        return true;
    } catch (error) {
        console.error('❌ Erro ao conectar com API:', error);
        showMessage('⚠️ API não está rodando! Execute: uvicorn app.main:app --reload', 'error');
        return false;
    }
}

// Testar conexão ao carregar
testConnection();