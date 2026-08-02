$pass = ConvertTo-SecureString 'Kjn`B]' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('Nova', $pass)
New-PSDrive -Name N -PSProvider FileSystem -Root '\\MND\Nova' -Credential $cred -Persist -Scope Global
