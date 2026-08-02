# build_xuan_ext_demo.ps1 - Build xuan-ext-demo C/C++ extension (thin wrapper)
# Usage: pwsh -File build_xuan_ext_demo.ps1 [options]

$ErrorActionPreference = "Stop"

$builder = Join-Path $PSScriptRoot "build_native_ext.ps1"
& $builder -ProjectName "xuan-ext-demo" -PythonMinVersion 3.14 -CondaEnvNamePattern "314|py314|3\.14" @args
exit $LASTEXITCODE
