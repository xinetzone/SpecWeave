# verify_native_ext.ps1 - Generic verification for native C++ extension builds
# Checks that the extension module loads and the native DLL is present.
#
# Usage:
#   pwsh -File verify_native_ext.ps1 -ProjectName caffe-ffi
#   pwsh -File verify_native_ext.ps1 -ProjectDir <path> -ModuleName caffe_ffi

param(
    [string]$ProjectDir = "",
    [string]$ProjectName = "*",
    [string]$ModuleName = "",
    [string]$CondaEnv = "",
    [double]$PythonMinVersion = 3.14,
    [string]$CondaEnvNamePattern = "314|py314|3\.14"
)

$ErrorActionPreference = "Continue"

$modulePath = Join-Path $PSScriptRoot "lib" "NativeBuild.psm1"
Import-Module $modulePath -Force

Write-Host "=== Native Extension Verification ==="
Write-Host ""

$projectDir = Find-NativeProject -Hint $ProjectDir -ProjectName $ProjectName -ScriptDir $PSScriptRoot
Write-Host "Project dir: $projectDir"

if (-not $ModuleName) {
    $tomlPath = Join-Path $projectDir "pyproject.toml"
    if (Test-Path $tomlPath) {
        $content = Get-Content $tomlPath -Raw
        if ($content -match 'name\s*=\s*"([^"]+)"') {
            $ModuleName = $Matches[1] -replace '-', '_'
        }
    }
}
Write-Host "Module name: $ModuleName"

$condaPrefix = Find-CondaEnvPython -Hint $CondaEnv -MinVersion $PythonMinVersion -NamePattern $CondaEnvNamePattern
Write-Host "Conda env:   $condaPrefix"
Write-Host ""

$env:CONDA_PREFIX = $condaPrefix
$env:PATH = "$condaPrefix;$condaPrefix\Library\bin;$condaPrefix\Scripts;$env:PATH"

Set-Location $projectDir

$pyExe = Join-Path $condaPrefix "python.exe"
& $pyExe -c @"
import sys, os, importlib
print(f'Python: {sys.version}')
print()

try:
    mod = importlib.import_module('$ModuleName')
    print(f'$ModuleName version: {getattr(mod, "__version__", "unknown")}')
    print(f'$ModuleName path: {mod.__file__}')
except Exception as e:
    print(f'ERROR: Failed to import $ModuleName: {e}')
    sys.exit(1)

# Check for native DLL/SO files
ffi_dir = os.path.dirname(mod.__file__)
print(f'Package directory: {ffi_dir}')
native_files = []
for f in sorted(os.listdir(ffi_dir)):
    if f.endswith(('.dll', '.pyd', '.so', '.lib')):
        fp = os.path.join(ffi_dir, f)
        size_kb = os.path.getsize(fp) / 1024
        native_files.append(f)
        print(f'  {f} ({size_kb:.1f} KB)')

if not native_files:
    print('  WARNING: No native DLL/SO files found in package directory!')
    print()
    # Check build directory
    for build_dir_name in ['build', '_skbuild']:
        build_dir = os.path.normpath(os.path.join(ffi_dir, '..', '..', build_dir_name))
        if os.path.exists(build_dir):
            print(f'Checking {build_dir_name}/ ...')
            for root, dirs, files in os.walk(build_dir):
                for f in files:
                    if f.endswith('.dll'):
                        fp = os.path.join(root, f)
                        print(f'  Found DLL: {fp} ({os.path.getsize(fp)/1024:.1f} KB)')
else:
    print()
    print('=== VERIFICATION PASSED: Native extension loaded successfully ===')
"@

exit $LASTEXITCODE
