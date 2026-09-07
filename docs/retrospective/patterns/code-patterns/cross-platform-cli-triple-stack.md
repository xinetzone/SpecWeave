---
id: "cross-platform-cli-triple-stack"
title: "三栈跨平台 CLI 模式"
type: "code-pattern"
date: "2026-09-07"
maturity: "L2-validated"
source:
  - "apps/containers/jupyter-podman-rootless jpman CLI（bash/cmd/ps1 三栈实现）"
  - "R→I→E 七概念知识沉淀链路"
  - "实际踩坑：9p 文件系统 CRLF 混入 set -o pipefail\\r、jpman.ps1 默认发行版硬编码 Ubuntu"
related_patterns:
  - "powershell-wsl-cross-shell-wrapper"
  - "wsl-docker-command-safety"
  - "bash-unified-structured-logging"
  - "shell-nested-quote-file-based-strategy"
tags: ["cli", "cross-platform", "bash", "cmd", "powershell", "wsl", "crlf", "zero-dependency", "shell-wrapper"]
validation_count: 2
reuse_count: 0
---

# 三栈跨平台 CLI 模式

## 触发场景

同一个容器管理/构建/运维命令需要在三种完全不同的用户环境中直接执行，不要求用户先切换 shell：
- Linux / macOS 原生开发者：终端打开直接 `bash bin/jpman start`
- Windows 重度命令行用户（Git Bash / WSL bash / MSYS2 / Cygwin）：在 bash 环境里直接 `bash bin/jpman start`
- Windows PowerShell 用户：右键 Terminal 默认 pwsh，直接 `.\bin\jpman.ps1 start` 或 `.\bin\jpman.cmd start`
- CI/CD runner：可能是 pwsh、可能是 cmd、可能是 bash shell，环境取决于 gitlab-runner / github-actions runner 的 executor

核心矛盾：**三种 shell 语法不兼容**（bash 的 `set -euo pipefail` 无法在 cmd 里跑；PowerShell 的 `$ErrorActionPreference='Stop'` 在 bash 里就是变量名含 `$` 的非法 shell 语法），但用户期望"同一个 bin 目录下的 CLI，在我当前终端里直接敲命令就能跑"。

**适用于**：
- Python / Node 环境可能不存在（或还没 pip install），CLI 必须零依赖（shell 原生脚本）
- 同一个 CLI 内部的子命令是跨平台的（容器操作 podman/docker、文件路径转换、WSL 发行版导出等），语义在 Linux/macOS/Windows 下等价
- 目标用户覆盖了 Linux + Windows 双栈（如本机既用 WSL 跑容器，又用 Windows IDE 写代码）

**不适用于**：
- 纯 GUI 程序：命令行只是个安装器，shell 体验不重要
- 全 Linux 环境：没有 Windows 用户，不需要 ps1/cmd 双栈
- 复杂业务逻辑：超过 500 行的 CLI，直接用 Python/Go/Rust 写二进制比维护三个 shell 栈更可维护

## 核心公理

模式基于以下不可再分的公理成立：

1. **shell 不可互操作公理**：bash、cmd、pwsh 是三种没有任何语法互操作保证的独立执行器。把 `.ps1` 用 bash 执行，或者把 `.sh` 用 cmd 执行，99% 的脚本会在第一行或第二行直接语法报错。没有"跨所有 shell 的通用脚本"这种东西。
2. **路径转换重复公理**：任何跨 Windows/macOS/Linux 的容器脚本，至少有 30% 的代码是路径转换、目录定位、环境变量读取、文件存在判断。三个栈分别写这 30% 是重复劳动，但三个栈共享同一份 bash 核心逻辑 + ps1/cmd 只做 wrapper，可以省掉 2 × 70% 的重写。
3. **工作目录自举公理**：CLI 脚本被双击执行、被 npm scripts 从项目外目录调用、被 CI runner 从随机工作目录 invoke 时，**不能依赖「当前目录 = 项目根」的假设**。脚本必须在第一行自己定位 `$ProjectRoot`：`${BASH_SOURCE%/*}/..` / `Split-Path -Parent $MyInvocation.MyCommand.Path` / `%~dp0..`。
4. **编码陷阱累积公理**：在 drvfs（WSL 的 /mnt/d/，9p 协议）上读写的文件，行尾 LF 有一定概率被写回时混入 CRLF（Windows 编辑器保存、git autocrlf、Python open 默认编码叠加触发）。导致 `set -o pipefail\r` 中 `\r` 被 shell 当成选项名一部分——`invalid option name: pipefail\r`，显示出来就是「set: pipefail: invalid option」这种诡异报错。

## 核心做法（七要素三栈实现）

### 1. 文件布局：三个同名入口 + 一个 bash 核心逻辑

```
bin/
├── jpman          # bash 核心逻辑（≥80% 业务代码在这里）
├── jpman.cmd      # cmd 包装（≈30 行，把参数透传给 pwsh 或 bash）
└── jpman.ps1      # pwsh 包装（≈80 行，自举项目根+读.env+WSL 路径转换+调bash）
```

bash 脚本是权威事实源（Single Source of Truth）。cmd 和 ps1 都是**薄包装器（thin wrapper）**，只做三件事：
① 自举 ProjectRoot
② 读 .env（如果存在）
③ 参数透传给 bash 核心逻辑（Linux/macOS 直接 exec bash，Windows 通过 `wsl.exe -d <distro> bash /mnt/d/.../jpman` 或 `bash -lc "..."` 透传）

### 2. ProjectRoot 自举（第一行就做）

三个栈都**必须**在脚本初始化早期自举，不能假设当前目录是项目根。

Bash：
```bash
# 解析 $BASH_SOURCE，跟随符号链接
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"  # 之后所有相对路径都是对的
```

PowerShell：
```powershell
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
```

CMD：
```bat
@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
pushd %PROJECT_ROOT%
```

### 3. WSL 发行版自动探测（拒绝硬编码）

ps1 包装器里**禁止**写死 `$WslDistro = 'Ubuntu'`——用户环境里可能根本没有 Ubuntu 发行版，但有 `podman-machine-default`（Podman Desktop 生成）、`docker-desktop`（Docker Desktop）、`Ubuntu-26.04`、`Debian` 等多种情况。

自动按优先级探测：
```powershell
function Find-DefaultWslDistro {
    # 1) env 显式设置 > 2) podman-machine-* 前缀（Podman 用户）>
    # 3) Ubuntu*（默认首选）> 4) Running 状态的第一个 > 5) 任何已安装
    $candidates = wsl.exe --list --quiet 2>$null | Where-Object { $_ }
    if (-not $candidates) { throw "未检测到 WSL 发行版，请先 wsl --install" }

    $priorities = @(
        { $env:JUPYTER_WSL_DISTRO },
        { ($candidates | Where-Object { $_ -like 'podman-machine-*' }) | Select-Object -First 1 },
        { ($candidates | Where-Object { $_ -like 'Ubuntu*' }) | Select-Object -First 1 },
        { (wsl.exe --list --verbose 2>$null | ConvertFrom-Csv |
            Where-Object { $_.State -eq 'Running' }).Name | Select-Object -First 1 },
        { $candidates[0] }
    )
    foreach ($p in $priorities) { $result = & $p; if ($result) { return $result } }
}
```

### 4. .env 读取兼容（env > .env > 代码内默认）

三栈都要实现同样的优先级：**环境变量 > .env 文件 > 默认值**，缺一不可。
- env 已设置的变量绝不被 .env 覆盖（已有配置优先级最高）
- .env 里带引号的值（`JUPYTER_TOKEN="abc"`）必须去引号（Trim `"` 和 `'`）
- 注释行 `#` 和空行跳过
- .env 不存在直接跳过，不报错

PowerShell 示例（bash/cmd 同理）：
```powershell
function Import-EnvFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    foreach ($line in Get-Content $Path) {
        if ($line -match '^\s*#' -or $line -match '^\s*$') { continue }
        if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
            $name  = $Matches[1]
            $value = $Matches[2].Trim('"', "'")
            if (-not (Get-Item env:$name -ErrorAction SilentlyContinue)) {
                Set-Item env:$name -Value $value   # env 已有则不覆盖
            }
        }
    }
}
Import-EnvFile (Join-Path $ProjectRoot '.env')
```

### 5. Windows→WSL 路径双函数（双向转换）

ps1 调 bash 之前，所有传给 bash 的 Windows 路径（`D:\spaces\...`）必须先转成 WSL POSIX 路径（`/mnt/d/spaces/...`）。回来的 WSL 路径如果要显示给 Windows 用户或给 cmd，再转回去。双向转换，避免一半路径是 Windows 风格一半是 WSL 风格。

```powershell
function Convert-ToWslPath {
    param([string]$WindowsPath)
    $full = [IO.Path]::GetFullPath($WindowsPath)
    if ($full.Length -ge 2 -and $full[1] -eq ':') {
        $drive = $full[0].ToString().ToLower()
        $rest  = $full.Substring(2).Replace('\', '/')
        return "/mnt/$drive$rest"
    }
    return $full.Replace('\', '/')
}
```

### 6. 跨 WSL 调用：用 -File 不用 -Command

在 pwsh 里调 WSL bash 执行命令，禁止用：
```powershell
wsl.exe -d $distro -- bash -c "cd /mnt/d/... && bash bin/jpman save $arg1 $arg2"  # ❌
```
三重转义（pwsh 外层引号 → wsl.exe 解析 → bash 解析）会把 `$ErrorActionPreference`、带空格的参数、`'Stop'` 等引号全剥光，得到诡异的 `Continue=Stop: command not found` 假报错。
**正确做法**：用 bash 脚本直接执行（如果命令本来就在 bash 里），或者把参数拼成数组传给 `wsl.exe -- bash <绝对WSL路径> args`，不套 `-c`：
```powershell
$wslJpman = Convert-ToWslPath (Join-Path $ProjectRoot 'bin/jpman')
& wsl.exe -d $distro -- bash $wslJpman start @args  # ✅
```

### 7. CRLF 铁律：两个防线

LF/CRLF 问题是跨三栈脚本最常见的隐蔽陷阱。两道防线缺一不可：
- **防线 1（源文件侧）**：写 `.gitattributes` 强制 bin/jpman 为 LF：
  ```gitattributes
  bin/jpman  text eol=lf
  bin/*.sh   text eol=lf
  *.ps1      text eol=crlf  # Windows 下 ps1 通常用 CRLF，但 pwsh 都能跑
  ```
- **防线 2（运行时 Containerfile 侧，若涉及镜像内使用）**：在镜像构建时 COPY 完 sh 脚本之后，显式跑一次 `sed`/`dos2unix`：
  ```dockerfile
  COPY entrypoint.sh /usr/local/bin/entrypoint.sh
  RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh
  ```
  这行 sed 可以保证任何 Windows 编辑器保存过的脚本（行尾变 CRLF），进入镜像后一定是干净 LF，防止 `set: pipefail\r: invalid option` 出现在镜像内 entrypoint 启动阶段。

## 反模式（实际踩坑教训，至少 3 条）

### 反模式 1：cmd 直接复制 bash 逻辑，两个版本双维护
早期为了"兼容 cmd 用户"，直接把 bash 里 200 行 save/load/start 用 batch 语法重写了一份。结果改一次逻辑（如 manifest.txt 新增字段）需要同时改 bash + cmd + ps1，改漏了一处 cmd 的版本 SHA256 算法不同就导致 load 失败，debug 了整整一下午。
**对策**：cmd 和 ps1 都只做薄包装，所有业务逻辑永远只在 bash 脚本里写一次。

### 反模式 2：PowerShell 用 System.IO.Compression 代替 bash 的 gzip
用户只执行 `jpman save` 不需要装 Python、不需要 bash，但 `jpman.ps1` 的 WSL 调用因为发行版检测失败（硬编码了 Ubuntu），工程师图省事直接重写了一个 PowerShell 原生的 podman save + .NET GZipStream 版本。产物虽然字节级等价（gzip 格式标准），但 save/load 的代码路径变成两套——bash 一套 / ps1 一套——以后新增 manifest 字段要改两处。
**对策**：ps1 版本只保留"紧急 fallback 能力"，对外文档始终写"请通过 WSL 发行版自动探测走 bash 主路径"，不鼓励平行开发两套实现。

### 反模式 3：ps1 把所有错误都 catch 掉，继续执行下一个子命令
```powershell
$ErrorActionPreference = 'Continue'  # ❌ 不是 Stop
try { Import-EnvFile xxx } catch { }  # 吞掉 .env 不存在的异常
```
后果：USER_PASSWORD 没从 .env 读进来，默认值 `changeme` 启动容器，用户误以为密码改成功了，SSH 登不上又找不到原因。
**对策**：ps1 开头必须 `$ErrorActionPreference = 'Stop'`，非致命错误（.env 文件不存在）用 if (Test-Path) 提前判断而不是 try/catch 兜底。

### 反模式 4：嵌套终端停留在 WSL 交互 shell 上
终端 1 第一次 `wsl.exe -d Ubuntu` 因为发行版不存在失败，但 shell 切到了 WSL 的 `[user@xin ~]$` 提示符；之后同一个终端里再送的 pwsh 命令被当 bash 命令执行，`trae-sandbox: command not found` 无限卡住，用户感觉"又卡住了"。
**对策**：每次调 CLI 的子命令都用**新终端**执行，保证最外层 shell 是 Windows pwsh / cmd / Git Bash；不要复用已经 `wsl.exe` 进入交互模式的终端会话。

### 反模式 5：只跑通一个 shell 栈就宣称跨平台
用 pwsh 写好了 jpman.ps1，测试通过就写文档"Windows 上用 ps1，不用 bash"，但用户的 CI 是 `shell: cmd` 的 gitlab-runner（executor=shell）——cmd 下无法直接执行 `.ps1`，CI 全挂。
**对策**：三栈必须全跑：同一台 Windows 机器上分别在三种 shell 中执行最小化 smoke test（`jpman info` / `jpman version` 这类退出码轻命令），确认都能返回退出码 0。

## 检验标准

做完怎么知道做对了？以下 7 条全部满足：

1. [ ] 三栈 smoke test：在 Linux bash / Windows pwsh / Windows cmd 三个终端里分别执行 CLI 的 info/version 子命令，退出码都是 0，输出内容格式一致。
2. [ ] 发行版硬编码检查：ps1 全文 grep `'Ubuntu'` 不出现硬编码的默认值（只允许在"找不到任何候选时的错误消息提示用户可安装 Ubuntu"里出现）。
3. [ ] 工作目录隔离：从任何外部目录（如 `%USERPROFILE%\Desktop` 或 `C:\Users\用户名\Desktop`）调用绝对路径 `<project>\bin\jpman.ps1 start`，脚本能正确找到 ProjectRoot 下的 .env、Containerfile、.image-cache/，不依赖当前 CWD。
4. [ ] .env 优先级：同时在系统 env 中 `$env:USER_PASSWORD='foo'` 又在 .env 里写 `USER_PASSWORD=bar`，最终生效的是 env 的 `foo`（env > .env > 默认，不是 .env 覆盖 env）。
5. [ ] CRLF 零问题：项目里所有 `.sh` 文件的 `file <shfile>` 输出 `POSIX shell script, ASCII text executable`（不是 `with CRLF line terminators`），Containerfile 构建镜像 entrypoint 不出现 pipefail\r。
6. [ ] 三重转义隔离：ps1 调 bash 不使用任何 `bash -c "..."` 或 `wsl.exe ... -- bash -c "..."` 带 `-c` 的包装，都是直接传脚本路径 + 参数数组。
7. [ ] 零依赖：`bin/jpman` 不调用任何 Python/Node/Go 二进制，只用系统自带命令（bash/podman/docker/wsl/gunzip 等），`venv` 不存在也能跑通。

## 迁移验证（非当前领域）

**迁移 1：前端 monorepo 的 release CLI（非容器领域）**
- `bin/release` bash（Linux/macOS CI runner + vscode 终端）
- `bin/release.cmd`（Windows 上 npm scripts 入口，调 npx 或调 pwsh）
- `bin/release.ps1`（读 .env + 路径转换 + 调 changelog/gulp/tsc）
- 痛点一模一样：三平台都要跑 release，changelog 生成的路径格式必须在 Windows 下 POSIX 化、.env 要读、CWD 不一定在项目根。

**迁移 2：嵌入式项目烧录 CLI（非 Web 领域）**
- `bin/flash` bash（Linux udev 规则、ttyUSB0 设备访问）
- `bin/flash.ps1`（Windows 检测 COM 端口号自举 + 转 WSL 烧录 + 路径转换 elf 文件）
- `bin/flash.cmd`（老版烧录工具只支持 cmd 批处理）
- 同样需要"工作目录自举"（firmware binary 相对于 project root 的路径）+ "设备检测自动探测"（和 WSL 发行版探测本质一样：枚举可用设备，按优先级挑选）。

三个完全不相关的领域（容器 / 前端 / 嵌入式）都能套入同一模式结构，证明模式 7 要素抽象的正确性与可迁移性。
