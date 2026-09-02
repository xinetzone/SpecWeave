# native/build.ps1 — 编译 agent-monetize 原生 C++ FFI 模块（Windows / MSVC）
# 产物：native/build/score_opportunity.dll（被 core/ffi_bridge.py 加载，注册
# score_opportunity / risk_adjusted_net PackedFunc）。
#
# 前置：py314 conda 环境已安装 apache-tvm-ffi（editable），且本机有 MSVC + Windows SDK。
# 本脚本不依赖 vcvars64.bat / cmd，直接按已知目录形态定位 MSVC 与 Windows SDK，
# 以 /I 与 /LIBPATH 显式传给 cl.exe（PowerShell 直接调用）。
#
# 用法（在 apps/agent-monetize 下）：
#   pwsh -NoProfile -File native/build.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot          # apps/agent-monetize
$OutDir = Join-Path $Root "native\build"
$Src = Join-Path $Root "native\score_opportunity.cc"
$OutDll = Join-Path $OutDir "score_opportunity.dll"

# 1) 定位 Python 与 site-packages（tvm_ffi 头文件与导入库所在）
$Python = $null
if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
    $Python = Join-Path $env:CONDA_PREFIX "python.exe"
} elseif (Test-Path (Join-Path $HOME "anaconda3\envs\py314\python.exe")) {
    $Python = Join-Path $HOME "anaconda3\envs\py314\python.exe"
} else {
    $Python = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
}
if (-not $Python) { Write-Error "未找到 python，请先在 py314 环境安装 apache-tvm-ffi" }
$SitePkgs = (& $Python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])" | Select-Object -Last 1).Trim()
$TvmLibDir = Join-Path $SitePkgs "tvm_ffi\lib"
$TvmIncDir = Join-Path $SitePkgs "tvm_ffi\include"
if (-not (Test-Path (Join-Path $TvmLibDir "tvm_ffi.dll"))) {
    Write-Error "未找到 tvm_ffi.dll，请先在 py314 环境安装 apache-tvm-ffi：$TvmLibDir"
}

# 2) 定位 MSVC cl.exe 与 include/lib
$VsRoot = "C:\Program Files\Microsoft Visual Studio"
if (-not (Test-Path $VsRoot)) { $VsRoot = "C:\Program Files (x86)\Microsoft Visual Studio" }
$Cl = Get-ChildItem -Path $VsRoot -Recurse -Filter "cl.exe" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match "Hostx64\\x64" } | Select-Object -First 1 -ExpandProperty FullName
if (-not $Cl) { Write-Error "未找到 MSVC cl.exe，无法编译原生模块（demo 将走纯 Python 参考实现）" }
# cl.exe 位于 ...\Tools\MSVC\<ver>\bin\Hostx64\x64\cl.exe，向上 4 层即 MSVC 版本根
$MsvcDir = $Cl
for ($i = 0; $i -lt 4; $i++) { $MsvcDir = Split-Path $MsvcDir -Parent }
$MsvcInc = Join-Path $MsvcDir "include"
$MsvcLib = Join-Path $MsvcDir "lib\x64"
if (-not (Test-Path $MsvcLib)) { $MsvcLib = Join-Path $MsvcDir "lib\amd64" }

# 3) 定位 Windows SDK（取最新版本）
$WkRoot = "C:\Program Files (x86)\Windows Kits\10"
if (-not (Test-Path $WkRoot)) { $WkRoot = "C:\Program Files\Windows Kits\10" }
$SdkVer = Get-ChildItem (Join-Path $WkRoot "Include") -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^\d+\.\d+\.\d+\.\d+$" } |
    Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty Name
if (-not $SdkVer) { Write-Error "未找到 Windows SDK，无法编译原生模块（demo 将走纯 Python 参考实现）" }
$SdkIncBase = Join-Path $WkRoot "Include\$SdkVer"
$SdkLibBase = Join-Path $WkRoot "Lib\$SdkVer"
$IncDirs = @(
    $TvmIncDir, $MsvcInc,
    (Join-Path $SdkIncBase "ucrt"),
    (Join-Path $SdkIncBase "shared"),
    (Join-Path $SdkIncBase "um"),
    (Join-Path $SdkIncBase "winrt")
)
$LibDirs = @(
    $TvmLibDir, $MsvcLib,
    (Join-Path $SdkLibBase "ucrt\x64"),
    (Join-Path $SdkLibBase "um\x64")
)

Write-Host "cl.exe     = $Cl"
Write-Host "tvm_ffi    = $TvmLibDir"
Write-Host "Windows SDK = $SdkVer"

# 4) 编译（/MD 与 tvm_ffi.dll 保持同一运行时；/utf-8 兼容源码中文注释）
# 注意：以「参数数组 + & $Cl @ClArgs」方式调用 cl.exe（PowerShell 负责对含空格
# 路径自动加引号）。切勿把整条命令拼成字符串再 Split(" ")——那会把带空格的
# /I"C:\Program Files\..." 拆成多个 token，导致 cl.exe 无法识别源文件类型。
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$ClArgs = @()
foreach ($d in $IncDirs) { $ClArgs += "/I$d" }
$ClArgs += @("/nologo", "/O2", "/EHsc", "/MD", "/utf-8", "/std:c++17", "/LD")
$ClArgs += $Src
# 自 /link 起为链接器参数：/LIBPATH 必须在 /link 之后，否则 cl 会以 D9002 忽略
$ClArgs += @("/link", "/OUT:$OutDll", "tvm_ffi.lib")
foreach ($d in $LibDirs) { $ClArgs += "/LIBPATH:$d" }

Write-Host ""
Write-Host "编译命令："
Write-Host "  & $Cl $($ClArgs -join ' ')"

& $Cl @ClArgs
$Exit = $LASTEXITCODE
if ($Exit -ne 0 -or -not (Test-Path $OutDll)) {
    Write-Error "编译失败（cl 退出码 $Exit）：$OutDll 未生成"
}

Write-Host ""
Write-Host "✔ 原生 FFI 模块已生成：$OutDll"
Write-Host "  （启动 demo 时 core/ffi_bridge.py 将加载它并注册 score_opportunity）"
