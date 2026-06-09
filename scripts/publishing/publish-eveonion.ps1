$user = "nova"
$pass = "EVEONION_APP_PASSWORD_REDACTED"
$pair = "$user`:`$pass"
$encoded = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
$headers = @{"Authorization" = "Basic $encoded"}
$body = Get-Content "C:\Users\compj\.openclaw\workspace\eveonion-post.json" -Raw
Invoke-RestMethod -Uri "https://eveonion.com/wp-json/wp/v2/posts" -Method Post -ContentType "application/json" -Headers $headers -Body $body
