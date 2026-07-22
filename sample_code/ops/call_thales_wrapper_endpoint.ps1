$Headers = @{ Authorization = "Bearer demo-token"; "Content-Type" = "application/json" }

Invoke-RestMethod -Method Post -Uri "https://gateway.example.internal/revealInput" -Headers $Headers -Body '{"recordId":"ABC-100"}'
Invoke-WebRequest -Method Post -Uri "https://gateway.example.internal/protectInput" -Headers $Headers -Body '{"customerId":"12345"}'
