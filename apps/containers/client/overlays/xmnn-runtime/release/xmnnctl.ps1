#!/usr/bin/env pwsh
#requires -Version 7.0
# ==============================================================================
# xmnnctl.ps1 — XMNN Runtime 客户控制脚本（Windows，PowerShell 7.4+）
#
# 用法: ./xmnnctl.ps1 [-Runtime podman|docker|auto] <命令>
#   -Runtime/-r  选择容器运行时（可放在命令前或后；默认 auto：先探测
#                podman 再 docker；命令行优先级高于环境变量 XMNN_RUNTIME）
#   init     创建 .env 并自动生成登录密码与 Jupyter token
#   load     校验并导入 artifacts\ 内随包镜像 tar.gz，随后自动运行守卫
#   up       启动服务（缺 .env 时自动 init），就绪后打印访问信息
#   down     停止并删除容器（workspace 与 SSH host key 卷保留）
#   ps       查看服务状态
#   logs     查看服务日志（Ctrl+C 退出，不影响容器运行）
#   smoke    运行 10 项运行时守卫
#   version  显示版本与交付清单信息
#
# 环境变量: XMNN_RUNTIME=podman|docker|auto 选择容器运行时（被 -Runtime 覆盖）
# 执行策略: 如被拦截，运行
#           pwsh -ExecutionPolicy Bypass -File .\xmnnctl.ps1 <命令>
# 注意: 请始终使用本脚本，不要在 Git Bash 中运行同名 bash 脚本控制
#       Windows 容器（路径转换会导致参数错误）。
# ==============================================================================
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$Script:Rt = ""
$Script:Compose = @()
$Script:Files = @()
$Script:RunFlags = @()
$Script:CliRuntime = ""   # 命令行 -Runtime 选择（podman|docker|auto）；空=未提供
$Script:Remain = @()      # 剥离全局参数后剩余的命令与命令参数

function Info($m) { Write-Host "[xmnn] $m" -ForegroundColor Blue }
function Ok($m)   { Write-Host "[ OK ] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "[ERR ] $m" -ForegroundColor Red; exit 1 }

# ── 运行时与 compose 探测 ───────────────────────────────────────────────────

# 扫描全局参数：-Runtime/-r（--runtime 同样接受，支持 -Runtime=x、-rx 粘连）
# 可出现在命令前后，其余 token 原样保留到 $Script:Remain（如 init 的 --force）；
# -- 之后全部按位置参数处理。合法性由 Detect-Runtime 判。
function Parse-GlobalArgs([string[]]$Tokens) {
    $Script:CliRuntime = ""
    $Script:Remain = @()
    for ($i = 0; $i -lt $Tokens.Count; $i++) {
        $t = $Tokens[$i]
        switch -Regex ($t) {
            '^--?runtime=(.+)$' { $Script:CliRuntime = $Matches[1]; break }
            '^--?runtime$' {
                if ($i + 1 -ge $Tokens.Count) { Die "$t 需要参数：podman|docker|auto" }
                $Script:CliRuntime = $Tokens[++$i]; break
            }
            '^-r(.+)$' { $Script:CliRuntime = $Matches[1]; break }
            '^-r$' {
                if ($i + 1 -ge $Tokens.Count) { Die "$t 需要参数：podman|docker|auto" }
                $Script:CliRuntime = $Tokens[++$i]; break
            }
            '^--$' {
                for ($i++; $i -lt $Tokens.Count; $i++) { $Script:Remain += $Tokens[$i] }
                break
            }
            default { $Script:Remain += $t }
        }
    }
}

# 用户级 compose 可执行文件的常见落点：pipx 链接在 %USERPROFILE%\.local\bin，
# pip --user 的 Scripts 在 %APPDATA%\Python\Python3xx\Scripts。
# 非交互/最小 PATH 环境下 Get-Command 搜不到，会把"已安装"误判成"缺少 compose"。
function Find-UserCompanion($name) {
    $candidates = @()
    if ($env:USERPROFILE) {
        $candidates += (Join-Path $env:USERPROFILE ".local\bin\$name.exe")
    }
    if ($env:APPDATA) {
        $pyRoot = Join-Path $env:APPDATA "Python"
        if (Test-Path $pyRoot) {
            # Scripts 固定在 Python\Python3xx\Scripts（深度 2）；限制深度避免穿入 site-packages
            $candidates += @(Get-ChildItem -Path $pyRoot -Recurse -Depth 2 -Filter "$name.exe" `
                -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
        }
    }
    return ($candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1)
}

function Detect-Runtime {
    # 优先级：命令行 -Runtime > 环境变量 XMNN_RUNTIME > auto（自动探测）
    $choice = if ($Script:CliRuntime) { $Script:CliRuntime }
              elseif ($env:XMNN_RUNTIME) { $env:XMNN_RUNTIME }
              else { "auto" }
    if ($choice -in @("podman", "docker")) {
        $Script:Rt = $choice
        if (-not (Get-Command $choice -ErrorAction SilentlyContinue)) {
            Die "指定的容器运行时 $choice 未安装或不在 PATH；可改用 auto 自动探测"
        }
    } elseif ($choice -eq "auto") {
        if (Get-Command podman -ErrorAction SilentlyContinue) {
            $Script:Rt = "podman"
        } elseif (Get-Command docker -ErrorAction SilentlyContinue) {
            $Script:Rt = "docker"
        } else {
            Die "未找到 podman 或 docker，请先安装容器运行时后重试"
        }
    } else {
        Die "运行时只允许 podman|docker|auto（当前：$choice）"
    }

    if ($Script:Rt -eq "podman") {
        $null = & podman compose version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $Script:Compose = @("podman", "compose")
        } elseif (Get-Command podman-compose -ErrorAction SilentlyContinue) {
            $Script:Compose = @("podman-compose")
        } else {
            $companion = Find-UserCompanion "podman-compose"
            if ($companion) {
                $Script:Compose = @($companion)
                Warn "podman-compose 不在 PATH，已自动启用：$companion"
                Warn "建议将其目录加入 PATH（pipx: %USERPROFILE%\.local\bin；pip --user: %APPDATA%\Python\Python3xx\Scripts）"
            } else {
                Die @"
Podman 已安装但缺少 compose 支持：
  安装（任选其一）:
    pipx install podman-compose
    python -m pip install --user podman-compose
  若已安装仍报此错，确认用户 Scripts 目录（%USERPROFILE%\.local\bin 或
  %APPDATA%\Python\Python3xx\Scripts）已加入 PATH
"@
            }
        }
        $Script:Files = @("-f", "compose.yaml", "-f", "compose.podman.yaml")
        $Script:RunFlags = @("--device", "/dev/fuse", "--security-opt", "label=disable", "--cgroupns", "host")
    } else {
        $null = & docker compose version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $Script:Compose = @("docker", "compose")
        } elseif (Get-Command docker-compose -ErrorAction SilentlyContinue) {
            $Script:Compose = @("docker-compose")
        } else {
            $companion = Find-UserCompanion "docker-compose"
            if ($companion) {
                $Script:Compose = @($companion)
                Warn "docker-compose 不在 PATH，已自动启用：$companion"
            } else {
                Die @"
Docker 已安装但缺少 compose 插件：
  安装 Docker Compose v2 插件，或安装独立版:
    pipx install docker-compose
  若已安装仍报此错，确认用户 Scripts 目录已加入 PATH
"@
            }
        }
        $Script:Files = @("-f", "compose.yaml")
        $Script:RunFlags = @()
    }
}

# ── .env 读取与初始化 ───────────────────────────────────────────────────────

function Get-EnvValue($key) {
    if (-not (Test-Path .env)) { return "" }
    $line = Select-String -Path .env -Pattern "^$key=" | Select-Object -Last 1
    if ($line) { return (($line.Line -split "=", 2)[1]).TrimEnd("`r") }
    return ""
}

function Ensure-Env {
    if (-not (Test-Path .env)) { Warn "未发现 .env，先执行初始化"; Do-Init }
}

function New-Alnum([int]$len) {
    # 加密学随机源（System.Security.Cryptography，非 System.Random）；
    # 字符集仅字母数字，避免凭证中的 shell 元字符被基底 entrypoint 展开。
    $bytes = [byte[]]::new($len)
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    $set = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    -join (0..($len - 1) | ForEach-Object { $set[[int]$bytes[$_] % 62] })
}

function Set-EnvKey($key, $val) {
    $lines = Get-Content .env | ForEach-Object {
        if ($_ -match "^$key=") { "$key=$val" } else { $_ }
    }
    # UTF-8 无 BOM + LF 换行：BOM 会使首个配置键无法被 compose 读取；
    # Set-Content 默认 CRLF 会让 bash/compose 读到带 "\r" 的值。
    $text = ($lines -join "`n") + "`n"
    [System.IO.File]::WriteAllText((Resolve-Path .env), $text,
        (New-Object System.Text.UTF8Encoding($false)))
}

function Do-Init([string]$Mode = "") {
    if ((Test-Path .env) -and $Mode -ne "--force") {
        Info ".env 已存在，跳过初始化（./xmnnctl.ps1 init --force 可重新生成凭证）"
        return
    }
    if (-not (Test-Path .env.example)) { Die "缺少 .env.example，交付包不完整" }
    Copy-Item .env.example .env
    Set-EnvKey "USER_PASSWORD" (New-Alnum 16)
    Set-EnvKey "JUPYTER_TOKEN" (New-Alnum 32)
    Ok "初始化完成，配置写入 .env"
    Write-Host "    SSH 登录密码 : $(Get-EnvValue USER_PASSWORD)"
    Write-Host "    Jupyter Token: $(Get-EnvValue JUPYTER_TOKEN)"
    Warn "请妥善保存凭证；不要将容器日志直接外发（日志可能含凭证）"
}

# ── 交付制品定位与完整性校验 ───────────────────────────────────────────────

function Find-Archive {
    $ver = Get-EnvValue XMNN_VERSION
    $archive = ""
    if (Test-Path artifacts/release.json) {
        $json = Get-Content artifacts/release.json -Raw | ConvertFrom-Json
        $candidate = Join-Path "artifacts" $json.archive.file
        if (Test-Path $candidate) { $archive = $candidate }
    }
    if (-not $archive -and $ver -and (Test-Path "artifacts/xmnn-runtime-$ver.tar.gz")) {
        $archive = "artifacts/xmnn-runtime-$ver.tar.gz"
    }
    if (-not $archive) {
        $latest = Get-ChildItem artifacts -Filter "xmnn-runtime-*.tar.gz" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latest) { $archive = $latest.FullName }
    }
    return $archive
}

function Verify-Archive([string]$archive) {
    if (Test-Path artifacts/release.json) {
        $json = Get-Content artifacts/release.json -Raw | ConvertFrom-Json
        $expected = [string]$json.archive.sha256
        if ($expected) {
            $actual = (Get-FileHash -Algorithm SHA256 $archive).Hash.ToLower()
            if ($actual -ne $expected.ToLower()) {
                Die "完整性校验失败：$archive 的 sha256 与 release.json 不符（文件可能已损坏）"
            }
            Ok "完整性校验通过（sha256 一致）"
        }
    }
}

function Do-Load {
    New-Item -ItemType Directory -Force artifacts | Out-Null
    $archive = Find-Archive
    if (-not $archive -or -not (Test-Path $archive)) {
        Die "artifacts 下未找到 xmnn-runtime-*.tar.gz，请确认交付包已完整解压"
    }
    Verify-Archive $archive
    Info "导入镜像：$archive"
    & $Script:Rt load -i $archive
    $ver = Get-EnvValue XMNN_VERSION
    if (-not $ver) { Die ".env 缺少 XMNN_VERSION" }
    # 镜像 tar 由 podman save 产出：打包机 podman tag 时裸名已归一化，归档内
    # RepoTag 固定为 localhost/xmnn-runtime:<ver>；docker load 原样保留该名，
    # 故双运行时统一引用 localhost/ 全称（裸名在 docker 下会按 docker.io 远程镜像解析）。
    # load 返回后镜像索引偶发瞬时未就绪，重试 5 次（间隔 2s）。
    $imgRef = "localhost/xmnn-runtime:$ver"
    $ready = $false
    for ($i = 0; $i -lt 5; $i++) {
        try {
            $null = & $Script:Rt image inspect $imgRef 2>$null
            if ($LASTEXITCODE -eq 0) { $ready = $true; break }
        } catch { }
        Start-Sleep -Seconds 2
    }
    if (-not $ready) {
        Die "导入的镜像中没有 $imgRef；请核对 .env 的 XMNN_VERSION 与交付包版本"
    }
    Ok "镜像 $imgRef 已就绪"
    Info "执行交付守卫（10 项）"
    Do-Smoke
}

# ── compose 包装与服务管理 ─────────────────────────────────────────────────

function Invoke-Compose([Parameter(Position = 0)][string]$ArgsLine) {
    # 以字符串行传入再 split：直接调用 Invoke-Compose up -d 时，"-d"
    # 会被 PowerShell 当作本函数的参数名而吞掉（实际执行前台 up 挂住）。
    $rest = @($ArgsLine -split '\s+' | Where-Object { $_ })
    if ($Script:Compose.Count -eq 2) {
        & $Script:Compose[0] $Script:Compose[1] @Script:Files @rest
    } else {
        & $Script:Compose[0] @Script:Files @rest
    }
}

function Do-Down { Invoke-Compose "down"; Ok "已停止（workspace 与 SSH host key 卷保留）" }
function Do-Ps   { Invoke-Compose "ps" }
function Do-Logs { Invoke-Compose "logs -f --tail 100" }

function Wait-Ready([int]$port) {
    for ($i = 0; $i -lt 150; $i++) {
        try {
            $resp = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$port/lab" -TimeoutSec 3
            if ($resp.StatusCode -lt 400) { return $true }
        } catch { }
        Start-Sleep -Seconds 2
    }
    return $false
}

function Print-Banner {
    $sport = Get-EnvValue XMNN_SSH_PORT; if (-not $sport) { $sport = "2225" }
    $jport = Get-EnvValue XMNN_JUPYTER_PORT; if (-not $jport) { $jport = "8893" }
    $ver = Get-EnvValue XMNN_VERSION
    Write-Host ""
    Write-Host "============================================================"
    Write-Host " XMNN Runtime $ver 已启动"
    Write-Host " JupyterLab : http://localhost:$jport"
    Write-Host "              内核选择 Python 3.14 (xmnn runtime)"
    Write-Host " SSH        : ssh -p $sport devuser@localhost"
    Write-Host " 工作区     : ./workspace （容器内 /workspace）"
    Write-Host " 凭证       : .env（USER_PASSWORD / JUPYTER_TOKEN）"
    Write-Host " 停止       : ./xmnnctl.ps1 down"
    Write-Host "============================================================"
    Write-Host ""
}

function Do-Up {
    New-Item -ItemType Directory -Force workspace | Out-Null
    Info "启动 xmnn-runtime（$($Script:Rt)）"
    Invoke-Compose "up -d"
    $jport = Get-EnvValue XMNN_JUPYTER_PORT; if (-not $jport) { $jport = "8893" }
    Info "等待 Jupyter 就绪（冷启动约需 1-3 分钟）"
    if (Wait-Ready([int]$jport)) {
        Ok "服务已就绪"
    } else {
        Warn "限定时间内未检测到 Jupyter 响应，请用 ./xmnnctl.ps1 logs 查看启动进度"
    }
    Print-Banner
}

# ── 运行时守卫 ──────────────────────────────────────────────────────────────

function Container-Running([string]$name) {
    $names = @(& $Script:Rt ps --format "{{.Names}}" 2>$null)
    return ($names -contains $name)
}

function Do-Smoke {
    $cname = Get-EnvValue XMNN_CONTAINER_NAME; if (-not $cname) { $cname = "xmnn-runtime" }
    $ver = Get-EnvValue XMNN_VERSION
    if (Container-Running $cname) {
        Info "容器运行中，经 exec 执行守卫"
        & $Script:Rt exec $cname /opt/conda/bin/python /opt/xmnnrt-smoke/_runtime_smoke.py
    } else {
        if (-not $ver) { Die ".env 缺少 XMNN_VERSION；请先 ./xmnnctl.ps1 init" }
        Info "容器未运行，使用一次性容器执行守卫"
        # 必须显式 --entrypoint：镜像默认 entrypoint 的命令模式会把脚本交给
        # cp314t 登录环境解析（实测会 9 项失败）。
        & $Script:Rt run --rm @Script:RunFlags --entrypoint /opt/conda/bin/python `
            "localhost/xmnn-runtime:$ver" /opt/xmnnrt-smoke/_runtime_smoke.py
    }
}

# ── 版本信息 ────────────────────────────────────────────────────────────────

function Do-Version {
    $ver = Get-EnvValue XMNN_VERSION
    if ($ver) { Write-Host "xmnn-runtime release: $ver" }
    else      { Write-Host "xmnn-runtime release: 未知（请先 ./xmnnctl.ps1 init）" }
    if (Test-Path artifacts/release.json) {
        $json = Get-Content artifacts/release.json -Raw | ConvertFrom-Json
        Write-Host "archive sha256: $($json.archive.sha256)"
    }
}

# ── 入口分发 ────────────────────────────────────────────────────────────────

Parse-GlobalArgs $args
$cmd = if ($Script:Remain.Count -ge 1) { [string]$Script:Remain[0] } else { "" }
switch ($cmd) {
    "init" {
        Detect-Runtime
        $mode = if ($Script:Remain.Count -ge 2) { [string]$Script:Remain[1] } else { "" }
        Do-Init $mode
    }
    "load"    { Detect-Runtime; Ensure-Env; Do-Load }
    "up"      { Detect-Runtime; Ensure-Env; Do-Up }
    "down"    { Detect-Runtime; Ensure-Env; Do-Down }
    "ps"      { Detect-Runtime; Ensure-Env; Do-Ps }
    "logs"    { Detect-Runtime; Ensure-Env; Do-Logs }
    "smoke"   { Detect-Runtime; Ensure-Env; Do-Smoke }
    "version" { Do-Version }
    { $_ -in @("-h", "--help", "help") } {
        Write-Host "用法: ./xmnnctl.ps1 [-Runtime podman|docker|auto] <init|load|up|down|ps|logs|smoke|version>"
    }
    default {
        if (-not $cmd) { Write-Host "用法: ./xmnnctl.ps1 [-Runtime podman|docker|auto] <init|load|up|down|ps|logs|smoke|version>"; exit 1 }
        Die "未知命令：$cmd（支持 init/load/up/down/ps/logs/smoke/version）"
    }
}
