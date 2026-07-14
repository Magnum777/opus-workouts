$body = @{
    jsonrpc = "2.0"
    id = 1
    method = "getBalance"
    params = @("7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA")
} | ConvertTo-Json

$headers = @{
    "x-api-key" = $env:HELIUS_API_KEY
}

$response = Invoke-RestMethod -Uri "https://mainnet.helius-rpc.com" -Method Post -ContentType "application/json" -Body $body -Headers $headers
$response | ConvertTo-Json