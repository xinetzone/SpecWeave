# build_caffe_ffi.ps1 - Build caffe-ffi C++ extension (thin wrapper around build_native_ext.ps1)
# Usage: pwsh -File build_caffe_ffi.ps1 [options]
# See build_native_ext.ps1 for available parameters.

$ErrorActionPreference = "Stop"

$builder = Join-Path $PSScriptRoot "build_native_ext.ps1"
& $builder -ProjectName "caffe-ffi" @args
exit $LASTEXITCODE
