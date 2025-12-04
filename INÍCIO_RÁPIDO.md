## ⚡ INÍCIO RÁPIDO - TESTAR AS NOVAS FUNCIONALIDADES

---

## 🚀 Passo 1: Iniciar a API

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎯 Passo 2: Testar no Browser

1. **Abrir:** `http://localhost:8000`
2. **Login como Profissional**
   - Email: use um email com role "profissional"
   - Senha: sua senha

---

## 🧪 Passo 3: Testar Conclusão com Teste Obrigatório

### Cenário: Atendimento com Coloração

1. **No Painel Profissional**
   - Vá para aba "Meus Atendimentos" (✅)
   - Localize um agendamento com Coloração

2. **Clique em "✅ Concluído"**
   - Modal "Resultado do Teste de Mecha" aparece
   - Selecione: POSITIVO 🔴, NEGATIVO 🟢 ou ADIADO 🟡
   - Adicione observação (opcional)
   - Clique "Confirmar e Concluir"

3. **Resultado:**
   - ✅ Atendimento concluído
   - ✅ Resultado do teste salvo
   - ✅ Arquivo criado em `exports/databricks/`

### Cenário: Atendimento com Corte (Sem Teste)

1. **No Painel Profissional**
   - Vá para aba "Meus Atendimentos"
   - Localize um agendamento com Corte

2. **Clique em "✅ Concluído"**
   - Confirme (sem modal, pois não requer teste)

3. **Resultado:**
   - ✅ Atendimento concluído
   - ✅ Arquivo criado em `exports/databricks/`

---

## 📂 Passo 4: Verificar Exportação para Databricks

```powershell
# Terminal PowerShell na pasta backend

# Ver últimos 5 arquivos criados:
Get-ChildItem exports\databricks -OrderBy LastWriteTime -Descending | Select -First 5

# Ver detalhes de um arquivo:
$file = (Get-ChildItem exports\databricks -OrderBy LastWriteTime -Descending | Select -First 1)
Write-Host "Arquivo: $($file.Name)"
Write-Host "Data: $($file.LastWriteTime)"
Write-Host "Tamanho: $($file.Length) bytes"
```

---

## 📋 Checklist de Funcionalidades

### Teste de Mecha Obrigatório ✅
- [ ] Cliquei "Concluído" em atendimento com Coloração
- [ ] Modal "Resultado do Teste" apareceu
- [ ] Consegui selecionar POSITIVO/NEGATIVO/ADIADO
- [ ] Consegui adicionar observações
- [ ] Atendimento foi concluído

### Exportação Automática ✅
- [ ] Arquivo foi criado em `exports/databricks/`
- [ ] Arquivo contém resultado do teste (se aplicável)
- [ ] Arquivo está em formato `.json.gz`

### Serviços Sem Teste ✅
- [ ] Cliquei "Concluído" em atendimento com Corte
- [ ] Modal NÃO apareceu (sem teste)
- [ ] Atendimento foi concluído direto
- [ ] Arquivo foi criado em `exports/databricks/`

---

## 🔍 Verificar Conteúdo do Arquivo Exportado

```powershell
# Descompactar um arquivo para ver conteúdo:
# (Usar software como 7-Zip ou Windows Explorer)

# Ou criar script PowerShell para ler:
$gzFile = "exports\databricks\appointments_*.json.gz" | Get-ChildItem -Descending | Select -First 1
# Descompactar manualmente e ver o JSON
```

---

## 🐛 Troubleshooting

### Problema: Modal não aparece ao clicar "Concluído"
**Solução:** Verifique se o serviço tem `requiresTest: true`

### Problema: Arquivo não é criado
**Solução:** Verifique se a API respondeu com sucesso (console do browser)

### Problema: Erro 500 na API
**Solução:** Verifique logs da API no terminal (porta 8000)

---

## 📚 Referência Rápida

### Arquivos Modificados:
- ✅ `backend/index.html` - 4 funções novas + modal
- ✅ `backend/app/routes/appointments.py` - 1 endpoint novo

### Endpoints Importantes:
- `POST /appointments/professional/create` - Agendar cliente
- `POST /appointments/export-completed` - Exportar conclusão

### Dados Salvos:
```javascript
{
  "booking_code": "BOOK-...",
  "status": "completed",
  "completed_at": "...",
  "strand_test_result": {
    "result": "positivo|negativo|adiado",
    "observations": "...",
    "tested_at": "..."
  }
}
```

---

## ✅ Tudo Pronto!

As novas funcionalidades estão implementadas e prontas para testar. Se tiver dúvidas, consulte:

- `RESUMO_IMPLEMENTAÇÕES_V3.md` - Visão geral
- `TESTE_FUNCIONALIDADES.md` - Guia detalhado de testes
- `IMPLEMENTAÇÕES_REALIZADAS_V3.md` - Documentação técnica
