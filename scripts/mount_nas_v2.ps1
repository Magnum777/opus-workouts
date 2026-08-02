$pass = ConvertTo-SecureString 'xXhFXH' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('Novasmb', $pass)
$smbUri = New-Object System.Uri '\\MND\Nova'
New-PSDrive -Name N -PSProvider FileSystem -Root $smbUri.AbsoluteUri -Credential $cred
