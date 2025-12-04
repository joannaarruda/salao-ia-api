## 🧪 COMO TESTAR AS NOVAS FUNCIONALIDADES

### 1. EXPORTAÇÃO DATABRICKS ✨

Quando você faz um agendamento (cliente ou profissional), um arquivo é automaticamente criado em:
```
exports/databricks/appointments_YYYYMMDD_HHMMSS.json.gz
```

Quando você conclui um atendimento, outro arquivo é criado com o resultado do teste:
```
exports/databricks/appointments_YYYYMMDD_HHMMSS.json.gz
```

**Para Verificar:**
```powershell
Get-ChildItem exports\databricks -OrderBy LastWriteTime -Descending | Select -First 5
```

---

### 2. AGENDAMENTO PELO PROFISSIONAL 📅

**No Frontend (index.html):**

1. Login como Profissional (role: "profissional")
2. Clique no botão verde "📅 Agendar Cliente" no painel
3. Preencha:
   - Nome do Cliente: "João Silva"
   - Email (opcional): "joao@example.com"
   - Telefone (opcional): "+351912345678"
   - Data: Selecione uma data futura
   - Hora: Selecione um horário
   - Serviços: Marque um ou mais
4. Clique em "✅ Agendar Cliente"
5. Sucesso! Agendamento criado e exportado

---

### 3. RESULTADO DO TESTE DE MECHA OBRIGATÓRIO 🧪 [NOVO]

**No Frontend (index.html):**

#### Cenário A: Serviço Requer Teste (ex: Coloração, Luzes)

1. Profissional clica "✅ Concluído" no atendimento
2. **Modal "Resultado do Teste de Mecha" aparece automaticamente**
3. Seleciona resultado:
   - 🔴 POSITIVO (Cliente com reação) → Observações obrigatórias
   - 🟢 NEGATIVO (Sem reação) → Pode continuar normalmente
   - 🟡 ADIADO (Reagendar) → Teste será marcado para outra data
4. Adiciona observações (opcional)
5. Clica "✅ Confirmar e Concluir"
6. Resultado:
   - Atendimento concluído
   - Resultado do teste salvo
   - **Automaticamente exportado para Databricks com os dados do teste** 📂

#### Cenário B: Serviço Sem Teste (ex: Corte, Escova)

1. Profissional clica "✅ Concluído" no atendimento
2. Confirma a conclusão diretamente (sem modal)
3. **Automaticamente exportado para Databricks** 📂

---

### 4. ESTRUTURA DE DADOS EXPORTADA

**Agendamento Concluído COM Teste:**
```json
{
  "appointment_id": "APT-...",
  "booking_code": "BOOK-...",
  "status": "completed",
  "completed_at": "2025-12-04T15:30:00",
  "strand_test_result": {
    "result": "positivo|negativo|adiado",
    "observations": "Cliente com irritação leve após teste",
    "tested_at": "2025-12-04T15:30:00"
  },
  "services": [...],
  "client_name": "João Silva"
}
```

**Agendamento Concluído SEM Teste:**
```json
{
  "appointment_id": "APT-...",
  "booking_code": "BOOK-...",
  "status": "completed",
  "completed_at": "2025-12-04T15:20:00",
  "services": [...],
  "client_name": "Maria Santos"
}
```

---

### 5. VERIFICAR API DIRETAMENTE

**Endpoint para exportar agendamento concluído:**
```
POST http://localhost:8000/api/v1/appointments/export-completed
```

**Body com resultado POSITIVO:**
```json
{
  "appointment_id": "APT-abc123def456",
  "booking_code": "BOOK-20251204-xyz789",
  "status": "completed",
  "completed_at": "2025-12-04T15:30:00",
  "services": [
    {
      "id": "coloracao_completa",
      "name": "Coloração Completa",
      "duration": 120,
      "price": 45,
      "requiresTest": true
    }
  ],
  "client_name": "Ana Maria",
  "strand_test_result": {
    "result": "positivo",
    "observations": "Cliente com irritação no couro cabeludo",
    "tested_at": "2025-12-04T15:30:00"
  }
}
```

**Resposta Esperada:**
```json
{
  "status": "exported",
  "export_path": "exports/databricks/appointments_20251204_153000.json.gz",
  "message": "Agendamento concluído exportado com sucesso"
}
```

---

## 📋 CHECKLIST DE TESTES

### Agendamento (Já Funcionando):
- [ ] Cliente consegue agendar normalmente
- [ ] Arquivo é criado em `exports/databricks/`

### Agendamento pelo Profissional:
- [ ] Profissional consegue clicar em "📅 Agendar Cliente"
- [ ] Modal abre com formulário completo
- [ ] Seleção de serviços funciona e calcula total
- [ ] Agendamento é criado com sucesso
- [ ] Novo arquivo é criado em `exports/databricks/`

### Conclusão com Teste (NOVO):
- [ ] Profissional clica "✅ Concluído" em atendimento com coloração
- [ ] Modal de teste aparece automaticamente
- [ ] Consegue selecionar POSITIVO, NEGATIVO ou ADIADO
- [ ] Consegue adicionar observações
- [ ] Clica "Confirmar e Concluir"
- [ ] Atendimento é marcado como concluído
- [ ] **Arquivo com resultado do teste é criado em `exports/databricks/`**

### Conclusão sem Teste:
- [ ] Profissional clica "✅ Concluído" em atendimento com corte
- [ ] Modal NÃO aparece (sem teste)
- [ ] Confirma conclusão direto
- [ ] Atendimento é marcado como concluído
- [ ] **Arquivo é criado em `exports/databricks/`**

---

## 🔗 ARQUIVOS PRINCIPAIS

- `backend/index.html` - Frontend com modais de agendamento e teste
- `backend/app/routes/appointments.py` - Backend com endpoints
- `backend/app/databricks_export.py` - Classe exportadora
- `backend/exports/databricks/` - Pasta com exports



