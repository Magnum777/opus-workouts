try {
    $url = 'https://zkillboard.com/api/corporationID/98754582/limit/100/'
    Write-Output 'Fetching data...'
    $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
    Write-Output 'Parsing JSON...'
    $data = $resp.Content | ConvertFrom-Json
    $count = $data | Measure-Object | Select-Object -ExpandProperty Count
    Write-Output "Total kills: $count"
    
    $big = New-Object System.Collections.ArrayList
    foreach ($k in $data) {
        $attackers = $k.attackers.Count
        if ($attackers -ge 20) {
            $val = $k.zkb.totalValue
            $rid = $k.regionID
            $kid = $k.killmail_id
            $sys = $k.solarSystemID
            $obj = New-Object PSObject -Property @{
                KillID = $kid
                Attackers = $attackers
                Value = $val
                Region = $rid
                System = $sys
            }
            [void]$big.Add($obj)
        }
    }
    
    $bigCount = $big | Measure-Object | Select-Object -ExpandProperty Count
    Write-Output "Fights with 20+ attackers: $bigCount"
    
    $big | Sort-Object -Property Attackers -Descending | Select-Object KillID, Attackers, System, Region, Value
    
} catch {
    Write-Output "Error: $_"
}
