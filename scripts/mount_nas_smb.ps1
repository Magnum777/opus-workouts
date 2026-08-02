$pass = ConvertTo-SecureString 'xXhFXH' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('Novasmb', $pass)
New-PSDrive -Name N -PSProvider FileSystem -Root '\\MND\Nova' -Credential $cred -Persist -Scope Global
