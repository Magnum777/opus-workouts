# Try SMB via different auth formats
$pass = ConvertTo-SecureString 'xXhFXH' -AsPlainText -Force

# Try with 'admin' user (Synology default)
$cred1 = New-Object System.Management.Automation.PSCredential('admin', $pass)

# Try Nova user
$cred2 = New-Object System.Management.Automation.PSCredential('Nova', $pass)

# Try NovaSMB
$cred3 = New-Object System.Management.Automation.PSCredential('Novasmb', $pass)

$targets = @(
  @{Name='N1'; Root='\\MND\Nova'; Cred=$cred2},
  @{Name='N2'; Root='\\MND\Nova'; Cred=$cred3},
  @{Name='N3'; Root='\\MND\share'; Cred=$cred2}
)

foreach ($t in $targets) {
    Write-Host "Trying $($t.Name) with root $($t.Root)..."
    try {
        New-PSDrive -Name $t.Name -PSProvider FileSystem -Root $t.Root -Credential $t.Cred -ErrorAction Stop
        Write-Host "SUCCESS: $($t.Name) mounted!"
        break
    } catch {
        Write-Host "FAILED: $($t.Name) - $($_.Exception.Message)"
    }
}
