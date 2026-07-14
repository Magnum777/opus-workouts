$body = @{
    jsonrpc = "2.0"
    id = 1
    method = "getBalance"
    params = @("7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $env:HELIUS_RPC_URL -Method Post -ContentType "application/json" -Body $body
$response | ConvertTo-Json -Depth 10
