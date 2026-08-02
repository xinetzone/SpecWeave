# build_native_ext.ps1 - Generic native C++ extension builder (scikit-build-core + MSVC)
# Uses NativeBuild.psm1 for auto-discovery of project, conda env, and Visual Studio.
#
# Usage:
#   pwsh -File build_native_ext.ps1                                        # auto-detect everything
#   pwsh -File build_native_ext.ps1 -ProjectName caffe-ffi                 # build specific project
#   pwsh -File build_native_ext.ps1 -ProjectDir <path>                     # explicit project path
#   pwsh -File build_native_ext.ps1 -CondaEnv py314                        # specify conda env
#   pwsh -File build_native_ext.ps1 -VsPath <path>                         # specify VS path
#   pwsh -File build_native_ext.ps1 -PythonMinVersion 3.13                 # override Python min version
#   pwsh -File build_native_ext.ps1 -VerboseBuild                          # detailed discovery logs
#   pwsh -File build_native_ext.ps1 -NoClean -NoVerify                     # skip steps
#
# Must be run with pwsh7 (PowerShell 7+)

param(
    [string]$ProjectDir = "",
    [string]$ProjectName = "*",
    [string]$CondaEnv = "",
    [string]$VsPath = "",
    [string]$Arch = "amd64",
    [string]$BuildType = "Release",
    [double]$PythonMinVersion = 3.14,
    [string]$CondaEnvNamePattern = "314|py314|3\.14",
    [string[]]$CMakeArgs = @(),
    [string[]]$CleanDirs = @("build", "build-vs", "_skbuild"),
    [switch]$NoClean,
    [switch]$NoVerify,
    [switch]$VerboseBuild
)

$ErrorActionPreference = "Stop"

# Helper: timestamped log
function Log-Step { param([string]$Msg) Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Msg" -ForegroundColor DarkCyan }
function Log-Info { param([string]$Msg) Write-Host "  $Msg" }
function Log-OK   { param([string]$Msg) Write-Host "  ✓ $Msg" -ForegroundColor Green }
function Log-Warn { param([string]$Msg) Write-Host "  ⚠ $Msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Native C++ Extension Builder (scikit-build)║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Log-Step "Build started $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Log-Info "Effective parameters:"
Log-Info "  ProjectDir     = '$ProjectDir'"
Log-Info "  ProjectName    = '$ProjectName'"
Log-Info "  CondaEnv       = '$CondaEnv'"
Log-Info "  VsPath         = '$VsPath'"
Log-Info "  Arch           = '$Arch'"
Log-Info "  BuildType      = '$BuildType'"
Log-Info "  PythonMinVer   = $PythonMinVersion"
Log-Info "  CondaPattern   = '$CondaEnvNamePattern'"
Log-Info "  CMakeArgs      = $($CMakeArgs.Count) items"
Log-Info "  CleanDirs      = $($CleanDirs -join ', ')"
Log-Info "  NoClean        = $NoClean  NoVerify=$NoVerify  VerboseBuild=$VerboseBuild"
Write-Host ""

# ── Phase 1: Auto-discover paths ──
Log-Step "Phase 1/6: Discovering build environment"

# Import shared module
$modulePath = Join-Path $PSScriptRoot "lib" "NativeBuild.psm1"
Log-Info "Loading module: $modulePath"
Import-Module $modulePath -Force
Log-OK  "NativeBuild module loaded"
Write-Host ""

Log-Info "Discovering project directory..."
Log-Info "  Hint='$ProjectDir'  ProjectName='$ProjectName'  ScriptDir='$PSScriptRoot'"
$projectDir = Find-NativeProject -Hint $ProjectDir -ProjectName $ProjectName -ScriptDir $PSScriptRoot
Log-OK  "Project dir: $projectDir"

$detectedName = "native-ext"
$tomlPath = Join-Path $projectDir "pyproject.toml"
if (Test-Path $tomlPath) {
    $tomlContent = Get-Content $tomlPath -Raw
    if ($tomlContent -match 'name\s*=\s*"([^"]+)"') {
        $detectedName = $Matches[1]
    }
    if ($tomlContent -match 'build-backend\s*=\s*"([^"]+)"') {
        Log-Info "Build backend: $($Matches[1])"
    }
}
Log-OK  "Project name: $detectedName"
Write-Host ""

Log-Info "Discovering conda environment..."
Log-Info "  Hint='$CondaEnv'  MinVersion=$PythonMinVersion  NamePattern='$CondaEnvNamePattern'  Verbose=$VerboseBuild"
$condaPrefix = Find-CondaEnvPython -Hint $CondaEnv -MinVersion $PythonMinVersion -NamePattern $CondaEnvNamePattern -VerboseLog:$VerboseBuild
$pyExe = Join-Path $condaPrefix "python.exe"
$pyVer = & $pyExe --version 2>&1
Log-OK  "Conda env:    $condaPrefix"
Log-OK  "Python:       $pyVer"
Write-Host ""

Log-Info "Discovering Visual Studio..."
if ($VsPath) { Log-Info "  Explicit VsPath: $VsPath" }
$vsInstallPath = if ($VsPath) { $VsPath } else { Find-VisualStudio -VerboseLog:$VerboseBuild }
$devShellDll = [IO.Path]::Combine($vsInstallPath, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
Log-OK  "VS install:   $vsInstallPath"
Log-Info "DevShell.dll: $devShellDll (exists=$(Test-Path $devShellDll))"
Log-Info "Architecture: $Arch"
Log-Info "Build type:   $BuildType"
Write-Host ""

# ── Phase 2: Clean build directories ──
if (-not $NoClean) {
    Log-Step "Phase 2/6: Cleaning old build directories"
    Set-Location $projectDir
    foreach ($d in $CleanDirs) {
        $path = Join-Path $projectDir $d
        if (Test-Path $path) {
            Log-Info "Removing: $d"
            Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
            if (Test-Path $path) {
                Log-Warn "Failed to fully remove $d (may have locked files)"
            } else {
                Log-OK "Removed $d"
            }
        } else {
            Log-Info "Skip (not found): $d"
        }
    }
    Write-Host ""
} else {
    Log-Info "Phase 2/6: Skipping clean (-NoClean)"
    Write-Host ""
}

# ── Phase 3: Load MSVC environment ──
Log-Step "Phase 3/6: Loading MSVC DevShell environment"
$pathBefore = $env:PATH.Length
Log-Info "PATH length before DevShell: $pathBefore chars"
Log-Info "VS install:   $vsInstallPath"
Log-Info "DevShell.dll: $devShellDll"
if (-not (Test-Path $devShellDll)) {
    throw "DevShell.dll not found at: $devShellDll`nIs Visual Studio with C++ workload installed?"
}
Log-Info "Loading DevShell module and entering VS dev environment ($Arch)..."
Enter-MsvcDevShell -VsInstallPath $vsInstallPath -Arch $Arch
$pathAfter = $env:PATH.Length
$clCmd = Get-Command cl -ErrorAction SilentlyContinue
if ($clCmd) {
    $clVer = & cl 2>&1 | Select-Object -First 1
    Log-OK  "MSVC DevShell loaded ($Arch)"
    Log-Info "cl.exe: $($clCmd.Source)"
    Log-Info "PATH length after DevShell: $pathAfter chars (delta: $($pathAfter - $pathBefore))"
} else {
    throw "MSVC DevShell loaded but cl.exe not found in PATH!`nCheck that the 'Desktop development with C++' workload is installed in Visual Studio."
}
Write-Host ""

# ── Phase 4: Configure conda environment PATH ──
Log-Step "Phase 4/6: Configuring conda environment"
$condaPathParts = [System.Collections.Generic.List[string]]::new()
$condaPathParts.Add($condaPrefix)
$condaPathParts.Add([IO.Path]::Combine($condaPrefix, "Library", "bin"))
$condaPathParts.Add([IO.Path]::Combine($condaPrefix, "Scripts"))
$condaLibUsrBin = [IO.Path]::Combine($condaPrefix, "Library", "usr", "bin")
if (Test-Path $condaLibUsrBin) { $condaPathParts.Add($condaLibUsrBin); Log-Info "Added Library/usr/bin" }
$condaMingwBin = [IO.Path]::Combine($condaPrefix, "mingw-w64", "bin")
if (Test-Path $condaMingwBin) { $condaPathParts.Add($condaMingwBin); Log-Info "Added mingw-w64/bin" }

$env:PATH = [string]::Join(";", $condaPathParts) + ";" + $env:PATH
$env:CONDA_PREFIX = $condaPrefix
$env:CMAKE_GENERATOR = "Ninja"
$env:SKBUILD_CMAKE_GENERATOR = "Ninja"
$env:CMAKE_PREFIX_PATH = Join-Path $condaPrefix "Library"

# Apply extra CMake args as SKBUILD_CMAKE_ARGS
if ($CMakeArgs.Count -gt 0) {
    $env:SKBUILD_CMAKE_ARGS = [string]::Join(" ", $CMakeArgs)
    Log-Info "SKBUILD_CMAKE_ARGS: $env:SKBUILD_CMAKE_ARGS"
}
Log-OK  "Environment configured (PATH length: $($env:PATH.Length) chars)"
Write-Host ""

# ── Phase 5: Verify build environment ──
if (-not $NoVerify) {
    Log-Step "Phase 5/6: Verifying build environment"
    $pyVerCheck = & $pyExe --version 2>&1
    Log-Info "Python: $pyVerCheck"
    $verDouble = Get-PythonVersion -PythonExe $pyExe
    if ($verDouble -lt $PythonMinVersion) {
        throw "Python version must be >= $PythonMinVersion, found: $pyVerCheck"
    }

    $cmakeCmd = Get-Command cmake -ErrorAction SilentlyContinue
    if ($cmakeCmd) {
        $cmakeVer = & cmake --version 2>&1 | Select-Object -First 1
        Log-Info "CMake:  $cmakeVer"
    } else { Log-Warn "cmake not found in PATH" }

    $ninjaCmd = Get-Command ninja -ErrorAction SilentlyContinue
    if ($ninjaCmd) {
        $ninjaVer = & ninja --version 2>&1
        Log-Info "Ninja:  $ninjaVer"
    } else { Log-Warn "ninja not found in PATH" }

    # Quick MSVC compiler smoke test
    Log-Info "Running MSVC smoke test..."
    $testSrc = Join-Path $env:TEMP "msvc_test_$PID.cpp"
    @'
#include <iostream>
int main() { std::cout << "MSVC works!" << std::endl; return 0; }
'@ | Set-Content $testSrc -Encoding ASCII
    Push-Location $env:TEMP
    $compileOk = $false
    try {
        & cl /nologo /EHsc $testSrc /Femsvc_test_$PID.exe 2>&1 | Out-Null
        $testExe = "msvc_test_$PID.exe"
        if (Test-Path $testExe) {
            $smokeOut = & ".\$testExe" 2>&1
            Log-Info "Smoke test output: $smokeOut"
            Remove-Item "msvc_test_$PID.*" -Force -ErrorAction SilentlyContinue
            $compileOk = $true
        }
    } finally {
        Pop-Location
        Remove-Item $testSrc -Force -ErrorAction SilentlyContinue
    }
    if ($compileOk) {
        Log-OK "MSVC:   OK"
    } else {
        throw "MSVC compiler test FAILED. Check that VS C++ tools are properly installed."
    }

    & $pyExe -c "import tvm_ffi" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Log-Info "tvm_ffi: not available (project may not require it)"
    } else {
        Log-OK  "tvm_ffi: OK"
    }
    Write-Host ""
} else {
    Log-Info "Phase 5/6: Skipping verification (-NoVerify)"
    Write-Host ""
}

# ── Phase 6: Build ──
Log-Step "Phase 6/6: Building $detectedName"
Write-Host "=============================================="
Write-Host "=== pip install -e . --no-build-isolation ==="
Write-Host "=============================================="
Set-Location $projectDir
$buildStart = Get-Date
& $pyExe -m pip install -e . --no-build-isolation -v 2>&1
$exitCode = $LASTEXITCODE
$buildEnd = Get-Date
$buildDuration = $buildEnd - $buildStart
Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "=== BUILD SUCCEEDED ===" -ForegroundColor Green
    Log-OK "Build completed in $([math]::Round($buildDuration.TotalSeconds, 1))s"
} else {
    Write-Host "=== BUILD FAILED (exit code: $exitCode, duration: $([math]::Round($buildDuration.TotalSeconds, 1))s) ===" -ForegroundColor Red
}
exit $exitCode
