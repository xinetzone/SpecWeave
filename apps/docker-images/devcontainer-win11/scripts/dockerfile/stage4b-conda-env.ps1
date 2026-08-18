# Stage 4b: Create conda main environment with Python free-threading + Jupyter
param(
    [string]$PythonVersion = "3.14"
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Write-Host "[BUILD] Creating conda 'main' environment with Python $PythonVersion free-threading (cp314t)..."
Write-Host "[INFO] Using python-freethreading metapackage from conda-forge..."

# Create main environment with free-threading Python
# python-freethreading is a conda-forge metapackage that pulls in cp314t build
$condaExe = "C:\conda\Scripts\conda.exe"

# Ensure libmamba solver is used
& $condaExe config --set solver libmamba 2>&1 | ForEach-Object { Write-Host "  $_" }

Write-Host "[INFO] Running conda create for main environment..."
Write-Host "[INFO] This is the high-cost layer (may take several minutes)..."

$createArgs = @(
    'create', '-n', 'main', '-y',
    '--channel', 'conda-forge',
    "python=$PythonVersion",
    'python-freethreading',
    'pip',
    'setuptools',
    'wheel',
    'jupyterlab',
    'ipykernel',
    'notebook'
)

& $condaExe @createArgs 2>&1 | ForEach-Object { Write-Host "  $_" }
if ($LASTEXITCODE -ne 0) {
    Write-Error "conda create failed with exit code $LASTEXITCODE"
}
Write-Host "[OK] conda main environment created"

# Set default environment to main
& $condaExe config --set auto_activate_base false 2>&1 | ForEach-Object { Write-Host "  $_" }

# Register main environment as a Jupyter kernel
Write-Host "[INFO] Registering main env as Jupyter kernel..."
$mainPython = "C:\conda\envs\main\python.exe"
& $mainPython -m ipykernel install --name main --display-name "Python 3.14 (free-threading)" --sys-prefix 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "[OK] Jupyter kernel registered"

# Add main env to PATH
$mainBinPath = "C:\conda\envs\main;C:\conda\envs\main\Scripts;C:\conda\envs\main\Library\bin"
$machinePath = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
if ($machinePath -notlike "*C:\conda\envs\main*") {
    [Environment]::SetEnvironmentVariable('PATH', "$mainBinPath;$machinePath", 'Machine')
    $env:PATH = "$mainBinPath;$env:PATH"
}

# Verify Python installation (quick check, full ft verify in 4c)
Write-Host "[INFO] Verifying Python installation..."
$pyVersion = & $mainPython --version 2>&1
Write-Host "  - python: $pyVersion"
$pipVersion = & $mainPython -m pip --version 2>&1
Write-Host "  - pip: $pipVersion"
$jupyterVersion = & $mainPython -m jupyter --version 2>&1
Write-Host "  - jupyter:"
$jupyterVersion | ForEach-Object { Write-Host "      $_" }

Write-Host "[OK] Stage 4b: conda main environment (Python free-threading + Jupyter) created successfully"
