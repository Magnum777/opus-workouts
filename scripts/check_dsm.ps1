add-type @"
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
public class SSL {
    public static void Bypass() {
        ServicePointManager.ServerCertificateValidationCallback = 
            delegate(object s, X509Certificate c, X509Chain ch, SslPolicyErrors e) { return true; };
    }
}
"@
[SSL]::Bypass()
try {
    $r = Invoke-WebRequest -Uri 'https://MND:8443' -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host 'STATUS:' $r.StatusCode
    Write-Host 'LOCATION:' $r.Headers['Location']
    $r.Content | Select-Object -First 20
} catch {
    Write-Host 'FAIL:' $_.Exception.Message
}
