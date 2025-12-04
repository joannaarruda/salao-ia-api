# Script para testar agendamento do profissional via API

$API_URL = "http://localhost:8000/api/v1"

$scheduleData = @{
    client_name = "João Silva"
    client_email = "joao@example.com"
    client_phone = "+351912345678"
    appointment_date = "2025-12-15"
    appointment_time = "14:30"
    professional_id = "prof-123"
    professional_name = "Ana Profissional"
    services = @(
        @{
            id = "corte_feminino"
            name = "Corte Feminino"
            duration = 60
            price = 25
        }
    )
    notes = "Cliente novo, primeira vez"
} | ConvertTo-Json

Write-Host "📝 Enviando requisição para criar agendamento como profissional..."
Write-Host "URL: $API_URL/appointments/professional/create"
Write-Host "Dados: $scheduleData"
Write-Host ""

$response = Invoke-WebRequest -Uri "$API_URL/appointments/professional/create" `
    -Method POST `
    -Headers @{
        "Content-Type" = "application/json"
    } `
    -Body $scheduleData `
    -ErrorAction Continue

Write-Host "✅ Resposta:"
Write-Host $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "📂 Verificando pasta exports/databricks..."
Get-ChildItem exports\databricks | Select-Object Name, LastWriteTime | Sort-Object LastWriteTime -Descending | Select-Object -First 3
