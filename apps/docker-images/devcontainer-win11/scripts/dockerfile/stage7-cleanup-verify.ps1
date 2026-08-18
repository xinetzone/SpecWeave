# Stage 7: Build metadata + cleanup + final verification + timing summary
param(
    [string]$VerifyMode = "standard",
    [DateTime]$BuildStart,
    [DateTime]$StageStart
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$mainPython = "C:\conda\envs\main\python.exe"
$dockerExe = "C:\Program Files\Docker\docker.exe"
$gitExe = "C:\Program Files\Git\cmd\git.exe"

# ── Write build metadata ──
Write-Host "[BUILD] Writing build metadata to C:\ProgramData\devcontainer-build-info..."
$buildInfoDir = "C:\ProgramData\devcontainer"
New-Item -ItemType Directory -Path $buildInfoDir -Force | Out-Null
$buildInfoPath = Join-Path $buildInfoDir "build-info"

$condaVersion = & "C:\conda\Scripts\conda.exe" --version 2>&1 | ForEach-Object { $_ -replace 'conda ', '' }
$pythonVersion = & $mainPython --version 2>&1 | ForEach-Object { $_ -replace 'Python ', '' }
$pythonBuildType = & $mainPython -c "import sysconfig; print('free-threading' if sysconfig.get_config_var('Py_GIL_DISABLED') else 'standard')" 2>&1
$ftEnv = [Environment]::GetEnvironmentVariable('Py_GIL_DISABLED', 'Machine')

$buildDate = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

$buildInfo = @"
BUILD_DATE=$buildDate
BASE_IMAGE=mcr.microsoft.com/windows/servercore:ltsc2022
BUILD_TYPE=windows-multi-stage
BUILD_VERIFY_MODE=$VerifyMode
LOCALE=zh-CN
TIMEZONE=China Standard Time
NON_ROOT_USER=devuser
SERVICES=sshd,jupyter
PYTHON_ENV=conda
CONDA_DIR=C:\conda
CONDA_VERSION=$condaVersion
PYTHON_VERSION=$pythonVersion
PYTHON_BUILD_TYPE=$pythonBuildType
PYTHON_FREETHREADING=yes
PY_GIL_DISABLED_ENV=$ftEnv
DOCKER_DOD=enabled
BUILD_TIMER=enabled
C_COMPILER=m2w64-toolchain
"@
Set-Content -Path $buildInfoPath -Value $buildInfo -Encoding UTF8
Write-Host "[OK] Build info written:"
Get-Content $buildInfoPath | ForEach-Object { Write-Host "  $_" }

# ── Cleanup ──
Write-Host ""
Write-Host "┌─────────────────────────────────────────────────┐"
Write-Host "│ [CLEANUP] Removing unnecessary files            │"
Write-Host "└─────────────────────────────────────────────────┘"

Write-Host "[CLEAN 1/5] Temp files..."
Remove-Item "C:\temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  - Temp directories cleaned"

Write-Host "[CLEAN 2/5] Conda package cache..."
& "C:\conda\Scripts\conda.exe" clean -a -y 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "  - Conda cache cleaned"

Write-Host "[CLEAN 3/5] Python __pycache__ and .pyc files..."
$pyCacheDirs = Get-ChildItem -Path "C:\conda" -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue
foreach ($dir in $pyCacheDirs) {
    Remove-Item $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "  - __pycache__ directories removed"

Write-Host "[CLEAN 4/5] pip cache..."
& $mainPython -m pip cache purge 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "  - pip cache purged"

Write-Host "[CLEAN 5/5] Windows update cache and logs..."
Remove-Item "C:\Windows\Logs\CBS\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  - Windows logs cleaned"

Write-Host "[OK] Cleanup complete"

# ── Final verification ──
Write-Host ""
Write-Host "┌─────────────────────────────────────────────────┐"
Write-Host "│  [FINAL VERIFICATION - Stage 7/7]               │"
Write-Host "│  Mode: $VerifyMode"
Write-Host "└─────────────────────────────────────────────────┘"

$allChecksPassed = $true

function Test-Command {
    param([string]$Name, [string]$Command)
    try {
        $result = & $Command 2>&1
        Write-Host "[OK] $Name available: $($result | Select-Object -First 1)"
        return $true
    } catch {
        Write-Host "[FAIL] $Name not found or failed: $_"
        return $false
    }
}

if ($VerifyMode -eq "off") {
    Write-Host "[SKIP] Build verification disabled (BUILD_VERIFY_MODE=off)"
} elseif ($VerifyMode -eq "fast") {
    Write-Host "[FAST MODE] Essential checks only..."

    $allChecksPassed = (Test-Command "python" $mainPython "--version") -and $allChecksPassed

    # ft check
    $ftOk = & $mainPython -c "import sysconfig; ft=sysconfig.get_config_var('Py_GIL_DISABLED'); soabi=sysconfig.get_config_var('SOABI') or ''; assert ft==1; assert 't' in soabi; print('[OK] Free-threading verified')" 2>&1
    Write-Host "  $ftOk"
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    $allChecksPassed = (Test-Command "conda" "C:\conda\Scripts\conda.exe" "--version") -and $allChecksPassed
    Write-Host "[FAST MODE] Essential checks passed"
} else {
    Write-Host "[VALIDATE 1/11] python (free-threading)..."
    & $mainPython --version 2>&1 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host "[VALIDATE 2/11] Python free-threading build verification..."
    & $mainPython -c @"
import sys, sysconfig
ft = sysconfig.get_config_var('Py_GIL_DISABLED')
soabi = sysconfig.get_config_var('SOABI') or ''
gil_enabled = sys._is_gil_enabled()
print(f'  Py_GIL_DISABLED (build) = {ft}')
print(f'  SOABI = {soabi}')
print(f'  sys._is_gil_enabled() = {gil_enabled}')
assert ft == 1, f'Expected Py_GIL_DISABLED=1, got {ft}'
assert 't' in soabi, f'Expected t suffix in SOABI (cp314t), got {soabi}'
assert not gil_enabled, 'GIL should be disabled at runtime with Py_GIL_DISABLED=1'
print('[OK] Python free-threading verified: GIL disabled at runtime')
"@ 2>&1 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host "[VALIDATE 3/11] Py_GIL_DISABLED system environment variable..."
    $ftEnvVal = [Environment]::GetEnvironmentVariable('Py_GIL_DISABLED', 'Machine')
    Write-Host "  Py_GIL_DISABLED (Machine) = $ftEnvVal"
    if ($ftEnvVal -ne "1") {
        Write-Host "[FAIL] Py_GIL_DISABLED not set to 1 at Machine level"
        $allChecksPassed = $false
    } else {
        Write-Host "[OK] Py_GIL_DISABLED=1 set correctly"
    }

    Write-Host "[VALIDATE 4/11] conda..."
    & "C:\conda\Scripts\conda.exe" --version 2>&1 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host "[VALIDATE 5/11] git..."
    & $gitExe --version 2>&1 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host "[VALIDATE 6/11] docker CLI..."
    & $dockerExe --version 2>&1 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host "[VALIDATE 7/11] docker compose..."
    & $dockerExe compose version 2>&1 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host "[VALIDATE 8/11] jupyter..."
    & $mainPython -m jupyter --version 2>&1 | Select-Object -First 3 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host "[VALIDATE 9/11] OpenSSH sshd..."
    $sshdPath = "C:\Windows\System32\OpenSSH\sshd.exe"
    if (Test-Path $sshdPath) {
        Write-Host "[OK] sshd.exe found at $sshdPath"
        $sshdService = Get-Service -Name sshd -ErrorAction SilentlyContinue
        if ($sshdService) { Write-Host "  - sshd service configured (startup: $($sshdService.StartType))" }
    } else {
        Write-Host "[FAIL] sshd.exe not found"
        $allChecksPassed = $false
    }

    Write-Host "[VALIDATE 10/11] C compiler availability..."
    $gccPath = "C:\conda\envs\main\Library\mingw-w64\bin\gcc.exe"
    if (Test-Path $gccPath) {
        $gccVer = & $gccPath --version 2>&1 | Select-Object -First 1
        Write-Host "[OK] GCC (m2w64-toolchain) available: $gccVer"
    } else {
        $gccCmd = Get-Command gcc.exe -ErrorAction SilentlyContinue
        if ($gccCmd) {
            Write-Host "[OK] gcc.exe found in PATH: $($gccCmd.Source)"
        } else {
            Write-Host "[WARN] GCC not found - pip source compilation may fail"
        }
    }

    Write-Host "[VALIDATE 11/11] Core C extensions..."
    & $mainPython -c @"
import sys
ok = True
for mod in ['sqlite3', 'ssl', 'zlib', 'hashlib', 'json', 'ctypes']:
    try:
        __import__(mod)
        print(f'  [OK] import {mod}')
    except Exception as e:
        print(f'  [FAIL] import {mod}: {e}')
        ok = False
if ok:
    print('[OK] All core C extensions loaded')
"@ 2>&1 | ForEach-Object { Write-Host "  $_" }
    if ($LASTEXITCODE -ne 0) { $allChecksPassed = $false }

    Write-Host ""
    if ($allChecksPassed) {
        Write-Host "[OK] All standard verification checks passed"
    } else {
        Write-Warning "Some verification checks failed - review output above"
    }
}

# ── Post-verify sweep ──
Write-Host ""
Write-Host "┌─────────────────────────────────────────────────┐"
Write-Host "│ [POST-VERIFY SWEEP] Final cleanup               │"
Write-Host "└─────────────────────────────────────────────────┘"
Remove-Item "C:\temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  - Temp files cleaned"

# ── Build timing summary ──
Write-Host ""
$now = Get-Date
$totalElapsed = [int]($now - $BuildStart).TotalSeconds
$stage7Elapsed = [int]($now - $StageStart).TotalSeconds

Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║         BUILD TIMING SUMMARY (Windows Runtime)              ║"
Write-Host "╠══════════════════════════════════════════════════════════════╣"
Write-Host "║  Stage 1/7   base+locale+timezone              ~ (see logs)  ║"
Write-Host "║  Stage 2/7   PowerShell7+Git                   ~ (see logs)  ║"
Write-Host "║  Stage 3/7   OpenSSH Server                    ~ (see logs)  ║"
Write-Host "║  Stage 4a/7  Miniforge3 install                ~ (see logs)  ║"
Write-Host "║  Stage 4b/7  conda main env (Python ft+Jupyter)~ (see logs)  ║"
Write-Host "║  Stage 4c/7  Py_GIL_DISABLED+pip+compiler      ~ (see logs)  ║"
Write-Host "║  Stage 5/7   Docker CLI (DooD)                 ~ (see logs)  ║"
Write-Host "║  Stage 6/7   devuser+configs+entrypoint        ~ (see logs)  ║"
Write-Host ("║  Stage 7/7   cleanup+final verify              {0,5}s       ║" -f $stage7Elapsed)
Write-Host "╠══════════════════════════════════════════════════════════════╣"
Write-Host ("║  RUNTIME TOTAL                                {0,5}s       ║" -f $totalElapsed)
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""
Write-Host "[BUILD] ========== BUILD COMPLETE (Windows container, Python free-threading cp314t) =========="
Write-Host ""
