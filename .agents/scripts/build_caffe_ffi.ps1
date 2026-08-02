# build_caffe_ffi.ps1 - Build caffe-ffi C++ extension (thin wrapper around build_native_ext.ps1)
# Usage: pwsh -File build_caffe_ffi.ps1 [options]
#
# This is a thin wrapper that sets project-specific defaults and delegates to
# the generic builder. All extra arguments (e.g. -VerboseBuild, -Clean) are
# forwarded via @args.

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "▸ caffe-ffi builder wrapper" -ForegroundColor DarkMagenta
Write-Host "  Project:    caffe-ffi (Caffe C++ extension via TVM FFI)" -ForegroundColor DarkGray
Write-Host "  Python:     >= 3.14 (py314 environment)" -ForegroundColor DarkGray
Write-Host "  Builder:    $(Join-Path $PSScriptRoot 'build_native_ext.ps1')" -ForegroundColor DarkGray
if ($args.Count -gt 0) {
    Write-Host "  Arguments:  $($args -join ' ')" -ForegroundColor DarkGray
}
Write-Host ""

$builder = Join-Path $PSScriptRoot "build_native_ext.ps1"
& $builder -ProjectName "caffe-ffi" @args
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "▸ caffe-ffi build finished successfully" -ForegroundColor Green
} else {
    Write-Host "▸ caffe-ffi build failed with exit code $exitCode" -ForegroundColor Red
}
exit $exitCode
