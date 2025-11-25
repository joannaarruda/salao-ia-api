// ==================== CÂMERA E CAPTURA DE FOTO ====================

let stream = null;
let capturedFile = null;

// Iniciar câmera
async function startCamera() {
    try {
        const video = document.getElementById('video');
        const cameraContainer = document.getElementById('cameraContainer');
        const startCameraBtn = document.getElementById('startCameraBtn');
        
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 640, 
                height: 480 
            } 
        });
        
        video.srcObject = stream;
        cameraContainer.style.display = 'block';
        startCameraBtn.style.display = 'none';
        
        showMessage('📷 Câmera ativada!', 'success');
    } catch (error) {
        console.error('Erro ao acessar câmera:', error);
        showMessage('❌ Não foi possível acessar a câmera. Verifique as permissões.', 'error');
    }
}

// Parar câmera
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    const video = document.getElementById('video');
    const cameraContainer = document.getElementById('cameraContainer');
    const startCameraBtn = document.getElementById('startCameraBtn');
    
    if (video) video.srcObject = null;
    if (cameraContainer) cameraContainer.style.display = 'none';
    if (startCameraBtn) startCameraBtn.style.display = 'block';
}

// Capturar foto da webcam
function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    
    // Desenhar frame atual do vídeo no canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Converter canvas para blob
    canvas.toBlob(async (blob) => {
        // Criar arquivo a partir do blob
        capturedFile = new File([blob], 'webcam_photo.jpg', { type: 'image/jpeg' });
        
        // Fazer upload
        await uploadPhoto(capturedFile);
        
        // Parar câmera
        stopCamera();
    }, 'image/jpeg', 0.95);
}

// Upload de arquivo selecionado
const fileInput = document.getElementById('fileInput');
if (fileInput) {
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
            console.log('📁 Arquivo selecionado:', file.name);
            await uploadPhoto(file);
        }
    });
}

// Função de upload
async function uploadPhoto(file) {
    console.log('📤 Iniciando upload...', file.name);
    
    // Validar tamanho
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
        showMessage('❌ Arquivo muito grande! Máximo 5MB.', 'error');
        return;
    }
    
    // Validar formato
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
        showMessage('❌ Formato inválido! Use PNG, JPG ou JPEG.', 'error');
        return;
    }
    
    try {
        showMessage('⏳ Enviando foto...', 'info');
        
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('🌐 Fazendo upload para:', `${API_URL}/upload-photo`);
        
        const response = await fetch(`${API_URL}/upload-photo`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        const data = await response.json();
        console.log('📥 Resposta do upload:', data);
        
        if (response.ok) {
            showMessage('✅ Foto enviada com sucesso!', 'success');
            
            // Mostrar preview
            const reader = new FileReader();
            reader.onload = function(e) {
                const previewImage = document.getElementById('previewImage');
                const photoPreview = document.getElementById('photoPreview');
                
                if (previewImage) previewImage.src = e.target.result;
                if (photoPreview) photoPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
            
            console.log('✅ Foto salva no perfil do usuário');
            
        } else {
            showMessage(`❌ ${data.detail || 'Erro ao enviar foto'}`, 'error');
        }
    } catch (error) {
        console.error('❌ Erro no upload:', error);
        showMessage('❌ Erro ao enviar foto. Verifique a conexão.', 'error');
    }
}

// Limpar foto
function clearPhoto() {
    const photoPreview = document.getElementById('photoPreview');
    const fileInput = document.getElementById('fileInput');
    
    if (photoPreview) photoPreview.style.display = 'none';
    if (fileInput) fileInput.value = '';
    
    console.log('🗑️ Foto limpa');
}

// ==================== ANÁLISE COM IA ====================

// Analisar foto com IA
async function analyzePhoto() {
    console.log('🤖 Função analyzePhoto() chamada');
    
    // Verificar se está logado
    if (!authToken) {
        showMessage('❌ Você precisa estar logado!', 'error');
        showScreen('authScreen');
        return;
    }
    
    try {
        // Mostrar tela de loading
        showScreen('suggestionsScreen');
        
        const loadingIA = document.getElementById('loadingIA');
        const suggestionsContent = document.getElementById('suggestionsContent');
        
        if (loadingIA) loadingIA.style.display = 'block';
        if (suggestionsContent) suggestionsContent.style.display = 'none';
        
        console.log('🌐 Chamando API de análise:', `${API_URL}/ai/analyze`);
        showMessage('🔍 Analisando sua foto...', 'info');
        
        const response = await fetch(`${API_URL}/ai/analyze`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('📡 Status da resposta:', response.status);
        
        const suggestions = await response.json();
        console.log('📊 Sugestões recebidas:', suggestions);
        
        if (response.ok) {
            displaySuggestions(suggestions);
            
            if (loadingIA) loadingIA.style.display = 'none';
            if (suggestionsContent) suggestionsContent.style.display = 'block';
            
            showMessage('✅ Análise concluída!', 'success');
        } else {
            console.error('❌ Erro na API:', suggestions);
            showMessage(`❌ ${suggestions.detail || 'Erro ao analisar foto'}`, 'error');
            showScreen('uploadScreen');
        }
    } catch (error) {
        console.error('❌ Erro na análise:', error);
        showMessage('❌ Erro ao analisar foto. Verifique se você fez upload de uma foto primeiro.', 'error');
        showScreen('uploadScreen');
    }
}

// Exibir sugestões
function displaySuggestions(suggestions) {
    console.log('📋 Exibindo sugestões:', suggestions);
    
    // Cortes
    const cortesLista = document.getElementById('cortesLista');
    if (cortesLista && suggestions.cortes_sugeridos) {
        cortesLista.innerHTML = suggestions.cortes_sugeridos.map(corte => 
            `<div class="suggestion-item" onclick="generateAISuggestion('${corte}')">
                <strong>${corte}</strong>
                <small>Clique para gerar preview</small>
            </div>`
        ).join('');
        console.log('✅ Cortes exibidos');
    }
    
    // Cores
    const coresLista = document.getElementById('coresLista');
    if (coresLista && suggestions.cores_sugeridas) {
        coresLista.innerHTML = suggestions.cores_sugeridas.map(cor => 
            `<div class="suggestion-item" onclick="generateAISuggestion('${cor}')">
                <strong>${cor}</strong>
                <small>Clique para gerar preview</small>
            </div>`
        ).join('');
        console.log('✅ Cores exibidas');
    }
    
    // Estilos
    const estilosLista = document.getElementById('estilosLista');
    if (estilosLista && suggestions.estilos_recomendados) {
        estilosLista.innerHTML = suggestions.estilos_recomendados.map(estilo => 
            `<div class="suggestion-item" onclick="generateAISuggestion('${estilo}')">
                <strong>${estilo}</strong>
                <small>Clique para gerar preview</small>
            </div>`
        ).join('');
        console.log('✅ Estilos exibidos');
    }
    
    // Esmaltes
    const esmaltesLista = document.getElementById('esmaltesLista');
    if (esmaltesLista && suggestions.cores_esmalte) {
        esmaltesLista.innerHTML = suggestions.cores_esmalte.map(esmalte => 
            `<div class="suggestion-item">
                <strong>${esmalte}</strong>
            </div>`
        ).join('');
        console.log('✅ Esmaltes exibidos');
    }
}

// Gerar sugestão visual com IA (quando clicar em uma sugestão)
async function generateAISuggestion(style) {
    console.log('🎨 Gerando sugestão visual para:', style);
    
    if (!authToken) {
        showMessage('❌ Você precisa estar logado!', 'error');
        return;
    }
    
    try {
        showMessage('🎨 Gerando preview visual...', 'info');
        
        const response = await fetch(`${API_URL}/ai/suggestions?style=${encodeURIComponent(style)}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const result = await response.json();
        console.log('🖼️ Resultado da IA:', result);
        
        if (response.ok) {
            // Mostrar a imagem gerada
            const aiImage = document.getElementById('aiGeneratedImage');
            if (aiImage) {
                aiImage.src = result.photo_ia_url;
                aiImage.style.display = 'block';
            }
            showMessage('✅ Preview gerado!', 'success');
        } else {
            showMessage(`❌ ${result.detail || 'Erro ao gerar preview'}`, 'error');
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        showMessage('❌ Erro ao gerar preview', 'error');
    }
}

// Log de inicialização
console.log('📸 camera.js carregado com sucesso!');