# build_npu_ffi.ps1 - Build npu-ffi C++ extension (thin wrapper around build_native_ext.ps1)
# Usage: pwsh -File build_npu_ffi.ps1 [options]

$ErrorActionPreference = "Stop"

$builder = Join-Path $PSScriptRoot "build_native_ext.ps1"
& $builder -ProjectName "npu-ffi" -PythonMinVersion 3.13 -CondaEnvNamePattern "31[3-9]|py31[3-9]|3\.1[3-9]" @args
exit $LASTEXITCODE
