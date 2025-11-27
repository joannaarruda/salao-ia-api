document.addEventListener("DOMContentLoaded", function() {
    const authForm = document.getElementById("authForm");
    const authTitle = document.getElementById("authTitle");
    const registerFields = document.getElementById("registerFields");
    const authToggleText = document.getElementById("authToggleText");
    
    // Configuração da API (garantir consistência com app.js)
    const API_URL = 'http://localhost:8000/api/v1'; 

authForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const isRegistering = authTitle.textContent === "Criar Conta";
    const url = isRegistering ? `${API_URL}/auth/register` : `${API_URL}/auth/login`; 
    const method = "POST";

    // 1. Coletar os dados do formulário
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value; 
    
    let requestBody;
    let requestHeaders = {};

    if (isRegistering) {
        // === REGISTO (JSON) ===
        const nome = document.getElementById('nome').value;
        const telefone = document.getElementById('telefone').value;
        const morada = document.getElementById('morada').value;
        
        requestBody = JSON.stringify({
            nome: nome,
            telefone: telefone,
            email: email,
            morada: morada,
            senha: senha
        });
        requestHeaders['Content-Type'] = 'application/json';

    } else {
        // === LOGIN (CORREÇÃO FINAL: FORM DATA) ===
        // O backend espera Form Data com chaves 'username' e 'password'.
        
        const formBody = new URLSearchParams();
        formBody.append('username', email); // Mapeia email para 'username'
        formBody.append('password', senha); // Mapeia senha para 'password'
        
        requestBody = formBody;
        
        // 2. Não definir Content-Type, o browser define 'application/x-www-form-urlencoded'
        // Se colocar 'application/json' AQUI, o erro 422 volta!
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: requestHeaders, // Headers só contêm Content-Type para o Registo
            body: requestBody, 
        });

        const data = await response.json();

        // Se a resposta for 401, 400 ou 422
        if (!response.ok) {
            // Tenta obter a melhor mensagem de erro
            const errorMessage = (data.detail && typeof data.detail === 'string') 
                ? data.detail 
                : (data.detail && Array.isArray(data.detail) && data.detail[0].msg) 
                ? `Erro: Campo '${data.detail[0].loc.join('.')}': ${data.detail[0].msg}` 
                : "Erro de credenciais ou formato inválido.";

            throw new Error(errorMessage); 
        }

        // Se o código for 200/201 (Sucesso)
        if (isRegistering) {
            alert("Conta criada com sucesso! Faça login.");
            window.toggleAuthMode();
        } else {
            // ✅ Salva o token devolvido pelo backend
            localStorage.setItem("access_token", data.access_token);
            
            // ✅ Salva o objeto do usuário (retornado na nova rota Python)
            if (data.user) {
                localStorage.setItem("currentUser", JSON.stringify(data.user));
            }
            
            alert("Login efetuado com sucesso!");
            window.location.reload(); 
        }

    } catch (error) {
        alert(error.message);
    }
});

    // =================================================================
    // FUNÇÕES GLOBAIS
    // =================================================================

    // Função para alternar entre "Entrar" e "Criar Conta"
    window.toggleAuthMode = function(event) {
        if (event) event.preventDefault();
        
        const isCurrentlyRegistering = authTitle.textContent === "Criar Conta";
        
        authTitle.textContent = isCurrentlyRegistering ? "Entrar" : "Criar Conta";
        registerFields.style.display = isCurrentlyRegistering ? "none" : "block";
        
        const toggleLink = document.querySelector('.auth-toggle a');
        if (toggleLink) {
            toggleLink.textContent = isCurrentlyRegistering ? "Criar conta" : "Entrar";
        }

        authToggleText.textContent = isCurrentlyRegistering ? "Não tem conta?" : "Já tem conta?";
    };

    // Função de logout global
    window.logout = function() {
        localStorage.removeItem("access_token"); 
        localStorage.removeItem("currentUser");
        
        if (typeof window.showScreen === 'function') {
            window.showScreen('authScreen');
        } else {
            window.location.reload(); 
        }
    };
});