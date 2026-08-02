# build_xuan_ext_demo.ps1 - Build xuan-ext-demo C/C++ extension (thin wrapper)
# Usage: pwsh -File build_xuan_ext_demo.ps1 [options]

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "▸ xuan-ext-demo builder wrapper" -ForegroundColor DarkMagenta
Write-Host "  Project:    xuan-ext-demo (C/C++ extension demo)" -ForegroundColor DarkGray
Write-Host "  Python:     >= 3.14 (py314 environment)" -ForegroundColor DarkGray
Write-Host "  Builder:    $(Join-Path $PSScriptRoot 'build_native_ext.ps1')" -ForegroundColor DarkGray
if ($args.Count -gt 0) {
    Write-Host "  Arguments:  $($args -join ' ')" -ForegroundColor DarkGray
}
Write-Host ""

$builder = Join-Path $PSScriptRoot "build_native_ext.ps1"
& $builder -ProjectName "xuan-ext-demo" -PythonMinVersion 3.14 -CondaEnvNamePattern "314|py314|3\.14" @args
$ec = $LASTEXITCODE

Write-Host ""
if ($ec -eq 0) {
    Write-Host "▸ xuan-ext-demo build finished successfully" -ForegroundColor Green
} else {
    Write-Host "▸ xuan-ext-demo build failed with exit code $ec" -ForegroundColor Red
}
exit $ec
