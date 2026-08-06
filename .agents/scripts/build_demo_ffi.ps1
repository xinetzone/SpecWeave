# build_demo_ffi.ps1 - Build demo-ffi C++ extension (thin wrapper around build_native_ext.ps1)
# Usage: pwsh -File build_demo_ffi.ps1 [options]

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "▸ demo-ffi builder wrapper" -ForegroundColor DarkMagenta
Write-Host "  Project:    demo-ffi (Demo C++ extension)" -ForegroundColor DarkGray
Write-Host "  Python:     >= 3.13" -ForegroundColor DarkGray
Write-Host "  Builder:    $(Join-Path $PSScriptRoot 'build_native_ext.ps1')" -ForegroundColor DarkGray
if ($args.Count -gt 0) {
    Write-Host "  Arguments:  $($args -join ' ')" -ForegroundColor DarkGray
}
Write-Host ""

$builder = Join-Path $PSScriptRoot "build_native_ext.ps1"
& $builder -ProjectName "demo-ffi" -PythonMinVersion 3.13 -CondaEnvNamePattern "31[3-9]|py31[3-9]|3\.1[3-9]" @args
$ec = $LASTEXITCODE

Write-Host ""
if ($ec -eq 0) {
    Write-Host "▸ demo-ffi build finished successfully" -ForegroundColor Green
} else {
    Write-Host "▸ demo-ffi build failed with exit code $ec" -ForegroundColor Red
}
exit $ec
