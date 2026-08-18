# escape=`
# =============================================================================
# DevContainer Win11 - Dockerfile (7-stage single-image build)
# Project: SpecWeave Windows 11 Development Container Base Image
# Base: mcr.microsoft.com/windows/servercore:ltsc2022 (Windows 11 kernel LTSC2022)
# Core: OpenSSH Server + Docker CLI (DooD, host named pipe) + JupyterLab + Miniforge3(conda-forge)
# Locale: zh-CN / Timezone: China Standard Time (UTC+8)
# Non-admin user: devuser (local user, not in Administrators group)
# Services: sshd(22) + jupyter(8888), managed by PowerShell entrypoint
# Python: Miniforge3 (conda-forge) at C:\conda (Python 3.14.6 free-threading cp314t via python-freethreading metapackage)
# Free-threading: System env var Py_GIL_DISABLED=1 set for C extension source compilation
# C compiler: conda-forge m2w64-toolchain (MinGW-w64 GCC) for pip source builds
# Docker CLI: static binary, DooD mode via npipe:////./pipe/docker_engine
#
# Build: docker build -t devcontainer-win11 .
# CN:    docker build --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun -t devcontainer-win11 .
# Run:   docker run -d -p 2222:22 -p 8888:8888 `
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret `
#          -v //./pipe/docker_engine://./pipe/docker_engine `
#          -v ${PWD}/workspace:C:\workspace devcontainer-win11
# Debug: docker run -it --rm devcontainer-win11 powershell
#
# Runtime Stage Layering:
#
#   Stage 1/7: 基础镜像设置 + 环境变量 + PowerShell配置 + 中文编码/时区    (变化频率: 最低)
#   Stage 2/7: 系统工具安装 (PowerShell 7 + Git for Windows + 常用工具)   (变化频率: 低)
#   Stage 3/7: OpenSSH Server 安装与配置                                (变化频率: 低)
#   Stage 4/7: Miniforge3 + Python free-threading (cp314t) + Jupyter + C编译工具链 (变化频率: 中)
#     4a: Miniforge3安装 + .condarc 配置                                (变化频率: 低)
#     4b: conda create main环境 (python-freethreading + Jupyter求解)    (变化频率: 中，高耗时)
#     4c: Py_GIL_DISABLED环境变量 + pip配置 + C编译器 + free-threading验证 (变化频率: 中高)
#   Stage 5/7: Docker CLI + Compose Plugin 安装 (DooD模式)              (变化频率: 低)
#   Stage 6/7: 用户devuser创建 + 工作目录 + 配置文件COPY + entrypoint    (变化频率: 中)
#   Stage 7/7: build-info + 清理 + 最终验证 + 计时汇总                  (变化频率: 最低)
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时，最终输出汇总表
# =============================================================================

ARG CONDA_MIRROR=official
ARG PIP_MIRROR=official
ARG PYTHON_VERSION=3.14
ARG BUILD_VERIFY_MODE=standard

# -----------------------------------------------------------------------------
# Stage: Runtime - Windows Server Core 2022 base
# -----------------------------------------------------------------------------
FROM mcr.microsoft.com/windows/servercore:ltsc2022

ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG PYTHON_VERSION
ARG BUILD_VERIFY_MODE

LABEL maintainer="SpecWeave"
LABEL description="Full-featured Windows Server 2022 (Win11 kernel) dev container with SSH + Docker DooD + Jupyter + Miniforge3(Python 3.14 free-threading cp314t, conda-forge), managed by PowerShell entrypoint"
LABEL version="1.0-ft"

# ── 元数据层：环境变量声明 ──
ENV TZ=China Standard Time `
    LANG=zh_CN.UTF-8 `
    CONDA_DIR=C:\conda `
    CONDA_DEFAULT_ENV=main `
    PYTHONDONTWRITEBYTECODE=1 `
    NON_ROOT_USER=devuser `
    JUPYTER_PORT=8888 `
    SSH_PORT=22 `
    ENABLE_SSH=yes `
    ENABLE_DOCKER=yes `
    ENABLE_JUPYTER=yes `
    JUPYTER_ALLOW_ORIGIN="" `
    JUPYTER_ROOT_DIR=C:\workspace

# 设置默认 Shell 为 PowerShell
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue'; $ExecutionContext.SessionState.LanguageMode = 'FullLanguage';"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/7: 基础环境配置 + PowerShell设置 + 中文编码/时区
# 变化频率：最低（基础镜像确定后很少改）
# ═══════════════════════════════════════════════════════════════════
RUN Write-Host '=== Stage 1/7: Base environment + Chinese locale/timezone ==='; `
    $stageStart = Get-Date; `
    Write-Host ('[TIMER] Runtime build started at {0:yyyy-MM-ddTHH:mm:ssZ}' -f (Get-Date).ToUniversalTime()); `
    $script:buildStart = $stageStart; `
    Write-Host '[BUILD] Setting PowerShell execution policy...'; `
    Set-ExecutionPolicy Bypass -Scope Process -Force; `
    Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force; `
    Write-Host '[BUILD] Enabling TLS 1.2 for secure downloads...'; `
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; `
    Write-Host '[BUILD] Setting console code page to UTF-8 (65001)...'; `
    chcp 65001 | Out-Null; `
    Write-Host '[BUILD] Setting timezone to China Standard Time (UTC+8)...'; `
    Set-TimeZone -Id 'China Standard Time'; `
    Write-Host ('[INFO] Current timezone: {0}' -f (Get-TimeZone).Id); `
    Write-Host ('[INFO] Current time: {0}' -f (Get-Date)); `
    Write-Host '[BUILD] Creating base directories...'; `
    New-Item -ItemType Directory -Path 'C:\workspace' -Force | Out-Null; `
    New-Item -ItemType Directory -Path 'C:\ProgramData\sshd' -Force | Out-Null; `
    New-Item -ItemType Directory -Path 'C:\temp' -Force | Out-Null; `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 1/7 (base+locale) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# ═══════════════════════════════════════════════════════════════════
# Stage 2/7: 系统工具安装 (PowerShell 7 + Git for Windows)
# 变化频率：低（工具版本升级时改）
# ═══════════════════════════════════════════════════════════════════
RUN Write-Host '=== Stage 2/7: Install PowerShell 7 + Git for Windows ==='; `
    $stageStart = Get-Date; `
    Write-Host '[BUILD] Downloading and installing PowerShell 7...'; `
    $pwshUrl = 'https://github.com/PowerShell/PowerShell/releases/download/v7.4.6/PowerShell-7.4.6-win-x64.msi'; `
    $pwshMsi = 'C:\temp\pwsh.msi'; `
    Invoke-WebRequest -Uri $pwshUrl -OutFile $pwshMsi -UseBasicParsing; `
    Start-Process msiexec.exe -ArgumentList '/i', $pwshMsi, '/quiet', '/norestart', 'ADD_EXPLORER_CONTEXT_MENU_OPENPOWERSHELL=0', 'ENABLE_PSREMOTING=0', 'REGISTER_MANIFEST=0' -Wait -NoNewWindow; `
    Remove-Item $pwshMsi -Force; `
    $pwshPath = 'C:\Program Files\PowerShell\7\pwsh.exe'; `
    if (Test-Path $pwshPath) { Write-Host ('[OK] PowerShell 7 installed at {0}' -f $pwshPath) } else { Write-Error 'PowerShell 7 installation failed' }; `
    Write-Host '[BUILD] Downloading and installing Git for Windows (minimal, no GUI)...'; `
    $gitUrl = 'https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe'; `
    $gitExe = 'C:\temp\git-install.exe'; `
    Invoke-WebRequest -Uri $gitUrl -OutFile $gitExe -UseBasicParsing; `
    Start-Process $gitExe -ArgumentList '/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-', `
        '/COMPONENTS=gitlfs', '/o:PathOption=CmdTools', '/o:BashTerminalOption=ConHost', `
        '/o:EnableSymlinks=Enabled', '/o:AutoCrlf=Input', '/o:FileMode=false' -Wait -NoNewWindow; `
    Remove-Item $gitExe -Force; `
    $gitPath = 'C:\Program Files\Git\cmd\git.exe'; `
    if (Test-Path $gitPath) { Write-Host ('[OK] Git installed at {0}' -f $gitPath); & $gitPath --version } else { Write-Error 'Git installation failed' }; `
    Write-Host '[BUILD] Setting system PATH for PowerShell 7 and Git...'; `
    $env:PATH = 'C:\Program Files\PowerShell\7;C:\Program Files\Git\cmd;' + $env:PATH; `
    [Environment]::SetEnvironmentVariable('PATH', $env:PATH, 'Machine'); `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 2/7 (PowerShell7+Git) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# 切换到 PowerShell 7 作为默认 Shell
SHELL ["C:\\Program Files\\PowerShell\\7\\pwsh.exe", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# ═══════════════════════════════════════════════════════════════════
# Stage 3/7: OpenSSH Server 安装与配置
# 变化频率：低
# ═══════════════════════════════════════════════════════════════════
RUN Write-Host '=== Stage 3/7: Install and configure OpenSSH Server ==='; `
    $stageStart = Get-Date; `
    Write-Host '[BUILD] Installing OpenSSH Server via Windows Capability...'; `
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0; `
    Write-Host '[OK] OpenSSH Server capability installed'; `
    Write-Host '[BUILD] Setting SSH service startup type to Automatic...'; `
    Set-Service -Name sshd -StartupType Automatic; `
    Set-Service -Name ssh-agent -StartupType Manual; `
    Write-Host '[BUILD] Configuring SSH default shell to PowerShell 7...'; `
    New-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell -Value 'C:\Program Files\PowerShell\7\pwsh.exe' -PropertyType String -Force | Out-Null; `
    New-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShellCommandOption -Value '-Command' -PropertyType String -Force | Out-Null; `
    Write-Host '[OK] SSH default shell set to PowerShell 7'; `
    Write-Host '[BUILD] Generating SSH host keys...'; `
    & 'C:\Windows\System32\OpenSSH\ssh-keygen.exe' -A 2>&1 | ForEach-Object { Write-Host "  $_" }; `
    $sshdConfig = 'C:\ProgramData\ssh\sshd_config'; `
    if (Test-Path $sshdConfig) { Write-Host ('[OK] sshd_config exists at {0}' -f $sshdConfig) } else { Write-Error 'sshd_config not found' }; `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 3/7 (OpenSSH) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# ═══════════════════════════════════════════════════════════════════
# Stage 4/7: Miniforge3 + Python free-threading (cp314t) + Jupyter + C编译工具链
# 变化频率：中（Python/包版本升级时改）
# 分层设计：拆分为3个子层，4b(conda create)高耗时层被保护
#   4a: Miniforge3安装 + .condarc配置
#   4b: conda create main环境 (python-freethreading + Jupyter)
#   4c: Py_GIL_DISABLED + pip配置 + C编译器 + free-threading验证
# ═══════════════════════════════════════════════════════════════════

# ── Stage 4a: Miniforge3 安装 + .condarc ──
COPY scripts/dockerfile/stage4a-miniforge.ps1 C:\temp\stage4a-miniforge.ps1
RUN Write-Host '=== Stage 4a/7: Install Miniforge3 + configure .condarc ==='; `
    $stageStart = Get-Date; `
    & C:\temp\stage4a-miniforge.ps1 -CondaMirror $env:CONDA_MIRROR; `
    Remove-Item 'C:\temp\stage4a-miniforge.ps1' -Force; `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 4a (Miniforge install) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# ── Stage 4b: conda create main 环境（高耗时层：Python free-threading + Jupyter） ──
COPY scripts/dockerfile/stage4b-conda-env.ps1 C:\temp\stage4b-conda-env.ps1
RUN Write-Host '=== Stage 4b/7: Create conda main env (Python freethreading + Jupyter) ==='; `
    $stageStart = Get-Date; `
    & C:\temp\stage4b-conda-env.ps1 -PythonVersion $env:PYTHON_VERSION; `
    Remove-Item 'C:\temp\stage4b-conda-env.ps1' -Force; `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 4b (conda env create) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# ── Stage 4c: Py_GIL_DISABLED + pip配置 + C编译器(m2w64-toolchain) + free-threading验证 ──
COPY scripts/dockerfile/stage4c-pip-verify.ps1 C:\temp\stage4c-pip-verify.ps1
RUN Write-Host '=== Stage 4c/7: Py_GIL_DISABLED + pip + C compiler + ft verify ==='; `
    $stageStart = Get-Date; `
    & C:\temp\stage4c-pip-verify.ps1 -PipMirror $env:PIP_MIRROR -VerifyMode $env:BUILD_VERIFY_MODE; `
    Remove-Item 'C:\temp\stage4c-pip-verify.ps1' -Force; `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 4c (ft-config+pip+compiler+verify) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# ═══════════════════════════════════════════════════════════════════
# Stage 5/7: Docker CLI + Compose Plugin 安装（DooD模式）
# 变化频率：低
# ═══════════════════════════════════════════════════════════════════
COPY scripts/dockerfile/stage5-docker.ps1 C:\temp\stage5-docker.ps1
RUN Write-Host '=== Stage 5/7: Install Docker CLI + Compose Plugin (DooD mode) ==='; `
    $stageStart = Get-Date; `
    & C:\temp\stage5-docker.ps1; `
    Remove-Item 'C:\temp\stage5-docker.ps1' -Force; `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 5/7 (Docker CLI DooD) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# ═══════════════════════════════════════════════════════════════════
# Stage 6/7: 创建非管理员用户 devuser + 工作目录 + 配置文件 + entrypoint
# 变化频率：中
# ═══════════════════════════════════════════════════════════════════
COPY config\sshd_config C:\ProgramData\ssh\sshd_config
COPY config\jupyter_notebook_config.py C:\ProgramData\jupyter\jupyter_notebook_config.py
COPY config\PowerShell_profile.ps1 C:\Windows\System32\WindowsPowerShell\v1.0\profile.ps1
COPY config\services.ps1 C:\ProgramData\devcontainer\services.ps1
COPY entrypoint.ps1 C:\ProgramData\devcontainer\entrypoint.ps1
COPY scripts\healthcheck.ps1 C:\ProgramData\devcontainer\healthcheck.ps1
COPY scripts\dockerfile\stage6-user-config.ps1 C:\temp\stage6-user-config.ps1

RUN Write-Host '=== Stage 6/7: Create devuser + configs + entrypoint ==='; `
    $stageStart = Get-Date; `
    & C:\temp\stage6-user-config.ps1; `
    Remove-Item 'C:\temp\stage6-user-config.ps1' -Force; `
    Write-Host '[BUILD] Setting entrypoint permissions...'; `
    icacls 'C:\ProgramData\devcontainer\entrypoint.ps1' /grant 'Everyone:(RX)' | Out-Null; `
    icacls 'C:\ProgramData\devcontainer\healthcheck.ps1' /grant 'Everyone:(RX)' | Out-Null; `
    $elapsed = [int]((Get-Date) - $stageStart).TotalSeconds; `
    $total = [int]((Get-Date) - $script:buildStart).TotalSeconds; `
    Write-Host ('[TIMER] Stage 6/7 (user+configs) took {0}s | Cumulative: {1}s' -f $elapsed, $total)

# ═══════════════════════════════════════════════════════════════════
# Stage 7/7: 构建元数据 + 清理 + 最终验证 + 计时汇总
# 变化频率：最低
# ═══════════════════════════════════════════════════════════════════
COPY scripts\dockerfile\stage7-cleanup-verify.ps1 C:\temp\stage7-cleanup-verify.ps1
RUN Write-Host '=== Stage 7/7: Build metadata + cleanup + final verification ==='; `
    $stageStart = Get-Date; `
    & C:\temp\stage7-cleanup-verify.ps1 -VerifyMode $env:BUILD_VERIFY_MODE -BuildStart $script:buildStart -StageStart $stageStart; `
    Remove-Item 'C:\temp\stage7-cleanup-verify.ps1' -Force

# ── 元数据声明 ──
WORKDIR C:\workspace
EXPOSE 22 8888

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 `
    CMD ["C:\\Program Files\\PowerShell\\7\\pwsh.exe", "-File", "C:\\ProgramData\\devcontainer\\healthcheck.ps1"]

ENTRYPOINT ["C:\\Program Files\\PowerShell\\7\\pwsh.exe", "-File", "C:\\ProgramData\\devcontainer\\entrypoint.ps1"]
CMD []
