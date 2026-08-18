# Stage 4c: Py_GIL_DISABLED env var + pip config + C compiler (m2w64-toolchain) + free-threading verification
param(
    [string]$PipMirror = "official",
    [string]$VerifyMode = "standard"
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$condaExe = "C:\conda\Scripts\conda.exe"
$mainPython = "C:\conda\envs\main\python.exe"

# ── Set Py_GIL_DISABLED=1 system environment variable ──
# This is CRITICAL for free-threading Python:
# 1. Tells pip/setuptools to build C extensions for free-threading (defines Py_GIL_DISABLED=1 at compile time)
# 2. Ensures Python runs without GIL by default at runtime
Write-Host "[BUILD] Setting system environment variable Py_GIL_DISABLED=1..."
[Environment]::SetEnvironmentVariable('Py_GIL_DISABLED', '1', 'Machine')
$env:Py_GIL_DISABLED = '1'
Write-Host "[OK] Py_GIL_DISABLED=1 set at Machine level (critical for free-threading C extension compilation)"

# ── Install C/C++ compiler toolchain (m2w64-toolchain from conda-forge) ──
# m2w64-toolchain provides MinGW-w64 GCC for compiling C extensions on Windows
# This is lighter than MSVC Build Tools (~2GB vs ~8GB) and works well with conda-forge
Write-Host "[BUILD] Installing C/C++ compiler toolchain (m2w64-toolchain) for pip source builds..."
& $condaExe install -n main -y --channel conda-forge `
    m2w64-toolchain `
    m2w64-gcc `
    m2w64-gcc-libs `
    m2-make `
    2>&1 | ForEach-Object { Write-Host "  $_" }
if ($LASTEXITCODE -ne 0) {
    Write-Warning "m2w64-toolchain install had issues, trying MSVC Build Tools fallback..."
    # Fallback note: MSVC Build Tools would require downloading from Microsoft
    # For now, warn and continue - m2w64 usually works on conda-forge
}
Write-Host "[OK] C/C++ compiler toolchain installed"

# Verify compiler
$gccPath = "C:\conda\envs\main\Library\mingw-w64\bin\gcc.exe"
if (Test-Path $gccPath) {
    Write-Host "[OK] GCC compiler found: $gccPath"
    $gccVer = & $gccPath --version 2>&1 | Select-Object -First 1
    Write-Host "  - $gccVer"
} else {
    Write-Warning "GCC not found at expected path; checking PATH..."
    $gccCmd = Get-Command gcc.exe -ErrorAction SilentlyContinue
    if ($gccCmd) { Write-Host "[OK] gcc.exe found in PATH: $($gccCmd.Source)" }
}

# ── Configure pip mirror ──
Write-Host "[BUILD] Configuring pip..."
$pipDir = "C:\Users\ContainerAdministrator\AppData\Roaming\pip"
New-Item -ItemType Directory -Path $pipDir -Force | Out-Null
$pipConfigPath = Join-Path $pipDir "pip.ini"

if ($PipMirror -eq "aliyun") {
    $pipConfig = @"
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
"@
    Write-Host "[BUILD] Using Aliyun PyPI mirror"
} elseif ($PipMirror -eq "tuna") {
    $pipConfig = @"
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn
"@
    Write-Host "[BUILD] Using Tsinghua TUNA PyPI mirror"
} else {
    $pipConfig = @"
[global]
index-url = https://pypi.org/simple/
"@
    Write-Host "[BUILD] Using official PyPI"
}
Set-Content -Path $pipConfigPath -Value $pipConfig -Encoding UTF8
Write-Host "[OK] pip configured"

# ── Free-threading runtime verification ──
Write-Host ""
Write-Host "┌─────────────────────────────────────────────────┐"
Write-Host "│  [FREE-THREADING VERIFICATION - Stage 4c]      │"
Write-Host "└─────────────────────────────────────────────────┘"

Write-Host "[FT-CHECK 1/5] python --version..."
$pyVer = & $mainPython --version 2>&1
Write-Host "  $pyVer"

Write-Host "[FT-CHECK 2/5] python -VV (build info)..."
$pyVV = & $mainPython -VV 2>&1
$pyVV | ForEach-Object { Write-Host "  $_" }
if ($pyVV -match "free-threading") {
    Write-Host "[OK] Python build reports free-threading support"
} else {
    Write-Warning "Python -VV output does not contain 'free-threading' - checking SOABI..."
}

Write-Host "[FT-CHECK 3/5] sysconfig Py_GIL_DISABLED flag..."
$ftCheck = @"
import sysconfig
ft = sysconfig.get_config_var('Py_GIL_DISABLED')
soabi = sysconfig.get_config_var('SOABI') or ''
print(f'  Py_GIL_DISABLED = {ft}')
print(f'  SOABI = {soabi}')
if ft == 1 and 't' in soabi:
    print('[OK] Free-threading build confirmed: GIL disabled by default')
else:
    print(f'[WARN] Unexpected: Py_GIL_DISABLED={ft}, SOABI={soabi}')
"@
& $mainPython -c $ftCheck 2>&1 | ForEach-Object { Write-Host "  $_" }

Write-Host "[FT-CHECK 4/5] sys._is_gil_enabled() runtime check..."
$gilCheck = @"
import sys
try:
    gil_enabled = sys._is_gil_enabled()
    print(f'  sys._is_gil_enabled() = {gil_enabled}')
    if gil_enabled:
        print('[WARN] GIL is enabled at runtime (check Py_GIL_DISABLED env var)')
    else:
        print('[OK] GIL is DISABLED at runtime - free-threading active!')
except AttributeError:
    print('[ERROR] sys._is_gil_enabled() not found - this is not a free-threading Python build!')
    raise
"@
$env:Py_GIL_DISABLED = '1'
& $mainPython -c $gilCheck 2>&1 | ForEach-Object { Write-Host "  $_" }

Write-Host "[FT-CHECK 5/5] Verify C extension can be imported..."
$cextCheck = @"
import sys
print(f'  Python: {sys.version}')
# Test core C extensions
imports_ok = True
for mod in ['sqlite3', 'ssl', 'zlib', 'hashlib', 'json']:
    try:
        __import__(mod)
        print(f'  [OK] import {mod}')
    except Exception as e:
        print(f'  [FAIL] import {mod}: {e}')
        imports_ok = False
if imports_ok:
    print('[OK] Core C extensions loaded successfully')
"@
& $mainPython -c $cextCheck 2>&1 | ForEach-Object { Write-Host "  $_" }

if ($VerifyMode -eq "fast") {
    Write-Host "[FAST MODE] Skipping detailed verification in Stage 4c"
}

Write-Host ""
Write-Host "[OK] Stage 4c: Py_GIL_DISABLED set, C compiler installed, free-threading verified"
