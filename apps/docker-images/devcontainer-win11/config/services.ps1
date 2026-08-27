# DevContainer Win11 - Services Helper Module
# Provides utility functions for service management

Set-StrictMode -Version Latest

function Test-ServiceRunning {
    param([string]$ServiceName)
    $svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    return ($svc -and $svc.Status -eq 'Running')
}

function Test-PortListening {
    param([int]$Port)
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return ($null -ne $listener)
}

function Wait-ForService {
    param(
        [string]$Name,
        [int]$Port,
        [int]$TimeoutSeconds = 60
    )
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        if (Test-PortListening -Port $Port) {
            Write-Host "[OK] $Name is ready on port $Port"
            return $true
        }
        Start-Sleep -Seconds 2
        $elapsed += 2
    }
    Write-Warning "$Name did not become ready within ${TimeoutSeconds}s"
    return $false
}

Export-ModuleMember -Function @(
    'Test-ServiceRunning',
    'Test-PortListening',
    'Wait-ForService'
)
