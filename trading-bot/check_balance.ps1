$body = @{
    jsonrpc = "2.0"
    id = 1
    method = "getBalance"
    params = @("7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887" -Method Post -ContentType "application/json" -Body $body
$response | ConvertTo-Json -Depth 10
