document.addEventListener("DOMContentLoaded", function() {
    const authForm = document.getElementById("authForm");
    const authTitle = document.getElementById("authTitle");
    const registerFields = document.getElementById("registerFields");
    const authToggleText = document.getElementById("authToggleText");

authForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const isRegistering = authTitle.textContent === "Criar Conta";
    const url = isRegistering ? `${API_URL}/auth/register` : `${API_URL}/auth/login`; 
    const method = "POST";

    // 1. Coletar os dados do formulário
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    let bodyData;

    if (isRegistering) {
        // Se for registo, coletar todos os campos e usar o modelo UserCreate (Backend)
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
        // Se for login, usar apenas email e senha (modelo UserLogin)
        bodyData = {
            email: email,
            senha: senha
        };
    }

    try {
        const response = await fetch(url, {
            method: method,
            // 2. Definir o Content-Type: application/json
            headers: {
                'Content-Type': 'application/json',
            },
            // 3. Serializar o objeto JavaScript para JSON
            body: JSON.stringify(bodyData),
        });

        // O resto do código permanece o mesmo, mas adaptado para o status code 401:
        const data = await response.json();

        // 4. Se a resposta for 401 ou outro erro (response.ok é false)
        if (!response.ok) {
            // Em vez de 'Erro ao autenticar', exibe a mensagem de erro da API (e.g., 'Credenciais inválidas')
            throw new Error(data.detail || "Erro desconhecido na autenticação."); 
        }

        // Se o código for 200/201 (Sucesso)
        if (isRegistering) {
            alert("Conta criada com sucesso! Faça login.");
            toggleAuthMode();
        } else {
            localStorage.setItem("access_token", data.access_token);
            // ... (restante do código de login)
        }
    } catch (error) {
        alert(error.message);
    }
});
    window.toggleAuthMode = function(event) {
        if (event) event.preventDefault();
        const isRegistering = authTitle.textContent === "Criar Conta";
        authTitle.textContent = isRegistering ? "Entrar" : "Criar Conta";
        registerFields.style.display = isRegistering ? "none" : "block";
        authToggleText.textContent = isRegistering ? "Não tem conta?" : "Já tem conta?";
    };

    window.logout = function() {
        localStorage.removeItem("access_token");
        document.getElementById("userMenu").style.display = "none";
        document.getElementById("authScreen").style.display = "block";
    };
});