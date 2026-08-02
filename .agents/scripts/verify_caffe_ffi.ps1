# verify_caffe_ffi.ps1 - Verify caffe-ffi C++ extension loads and functions correctly
# Uses auto-discovery from NativeBuild.psm1 (no hardcoded paths)

param(
    [string]$CondaEnv = ""
)

$ErrorActionPreference = "Continue"

$modulePath = Join-Path $PSScriptRoot "lib" "NativeBuild.psm1"
Import-Module $modulePath -Force

$projectDir = Find-NativeProject -ProjectName "caffe-ffi" -ScriptDir $PSScriptRoot
$condaPrefix = Find-CondaEnvPython -Hint $CondaEnv -MinVersion 3.14 -NamePattern "314|py314|3\.14"

$env:CONDA_PREFIX = $condaPrefix
$env:PATH = "$condaPrefix;$condaPrefix\Library\bin;$condaPrefix\Scripts;$env:PATH"

Set-Location $projectDir

& "$condaPrefix\python.exe" -c @"
import sys, os
print(f'Python: {sys.version}')
print()

import caffe_ffi
print(f'caffe_ffi version: {caffe_ffi.__version__}')
print(f'caffe_ffi path: {caffe_ffi.__file__}')
print()

import caffe_ffi._ffi_api as ffi
print(f'_ffi_api loaded: YES')
print()

# List native files in caffe_ffi package
ffi_dir = os.path.dirname(caffe_ffi.__file__)
print(f'Package directory: {ffi_dir}')
for f in sorted(os.listdir(ffi_dir)):
    if f.endswith(('.dll', '.pyd', '.so', '.lib')):
        fp = os.path.join(ffi_dir, f)
        print(f'  {f} ({os.path.getsize(fp)/1024:.1f} KB)')

# Check build dir for DLL
build_dll = os.path.normpath(os.path.join(ffi_dir, '..', '..', 'build', 'python', 'caffe_ffi', '_caffe_ffi.dll'))
print()
print(f'Build DLL exists: {os.path.exists(build_dll)}')
if os.path.exists(build_dll):
    print(f'Build DLL size: {os.path.getsize(build_dll)/1024:.1f} KB}')

# Quick functional test
print()
print('=== Functional test: ReLU Net forward ===')
from caffe_ffi import caffe_pb2
from caffe_ffi import Net
import numpy as np

net_param = caffe_pb2.NetParameter()
net_param.name = 'test_relu'

inp = net_param.layer.add()
inp.name = 'data'
inp.type = 'Input'
inp.top.append('data')
ip = caffe_pb2.InputParameter()
sh = ip.shape.add()
sh.dim.extend([2, 3])
inp.input_param.CopyFrom(ip)

relu = net_param.layer.add()
relu.name = 'relu1'
relu.type = 'ReLU'
relu.bottom.append('data')
relu.top.append('relu1')

net = Net(net_param)
print(f'Net created successfully')

# Use input/output blobs via blob_dict
data_blob = net.blob_dict['data']
data_blob.data.shape = (2, 3)
input_data = np.array([[-1, 0, 1], [2, -3, 4]], dtype=np.float32)
data_blob.data[:] = input_data

net.Forward()
result = net.blob_dict['relu1'].data
expected = np.maximum(input_data, 0)
print(f'Input:  {input_data.tolist()}')
print(f'ReLU:   {result}')
print(f'Expected: {expected.tolist()}')
if np.allclose(result, expected):
    print('ReLU forward: CORRECT!')
else:
    print(f'ReLU forward: MISMATCH')
    sys.exit(1)

print()
print('=== ALL TESTS PASSED ===')
"@

$exitCode = $LASTEXITCODE
exit $exitCode
