---
title: "Hermes Agent 安装方案 - Windows PowerShell 安装指南"
chapter: 3
source:
  - external/libs/hermes-agent/scripts/install.ps1
  - external/libs/hermes-agent/README.md
  - external/libs/hermes-agent/.env.example
  - external/libs/hermes-agent/pyproject.toml
  - external/libs/hermes-agent/.gitattributes
  - external/libs/hermes-agent/website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/windows-native.md
  - external/libs/hermes-agent/website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/windows-wsl-quickstart.md
---

# 3. Windows PowerShell 安装指南

本章面向 Windows 10/11 用户，详细说明如何使用官方 `install.ps1` 脚本在原生 Windows 上完成 Hermes Agent 的安装，包括一键安装命令、执行策略配置、Windows 特有注意事项（8.3 短路径、长路径、CRLF、pywin32）、环境变量配置、终端重启要求、WSL2 备选方案以及 Windows 专属故障排查。所有内容均以项目源码中的 `scripts/install.ps1`、`README.md`、`.env.example` 与 `pyproject.toml` 为准。

> 原生 Windows 支持 CLI、gateway、TUI、浏览器工具、MCP 服务器、cron 调度器等绝大多数功能。Dashboard 的 `/chat` 内嵌终端面板需要 POSIX PTY，仅 WSL2 支持，详见 3.6 节。

---

## 3.1 PowerShell 一键安装命令

### 3.1.1 标准一键安装

打开 **PowerShell**（或 Windows Terminal），执行以下命令：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

其中：
- `irm` 是 `Invoke-RestMethod` 的别名，用于下载脚本内容；
- `iex` 是 `Invoke-Expression` 的别名，用于执行下载的脚本。

该命令**无需管理员权限**，脚本会自动完成以下工作：

1. 将托管版 `uv`（Astral 的 Python 包管理器）安装到 `%LOCALAPPDATA%\hermes\bin\uv.exe`；
2. 通过 `uv` 自动安装 Python 3.11（若系统未找到，回退顺序为 3.12 → 3.13 → 3.10）；
3. 安装 Node.js 22（优先 winget，否则解压便携版到 `%LOCALAPPDATA%\hermes\node`）；
4. 检测系统 Git；若不存在则下载约 45 MB 的 PortableGit（MinGit）到 `%LOCALAPPDATA%\hermes\git`，不干扰系统 Git；
5. 将仓库克隆到 `%LOCALAPPDATA%\hermes\hermes-agent`；
6. 创建 Python 虚拟环境（venv）并分层安装依赖（优先 `uv.lock` 哈希验证，回退到 `.[all]` → `.[messaging,dashboard,ext]` → `.[messaging]` → `.`）；
7. 安装 Node.js 依赖、`agent-browser` 与 Playwright Chromium（浏览器工具所需）；
8. 安装 ripgrep、ffmpeg（通过 winget/chocolatey/scoop 或便携下载）；
9. 将 `hermes` 命令所在目录添加到**用户 PATH**；
10. 设置用户环境变量 `HERMES_HOME`；
11. 运行交互式 `hermes setup` 向导（可通过 `-SkipSetup` 跳过）。

安装程序会自动重试不稳定的 git 拉取，并剥离下载内容中的 UTF-8 BOM，因此 HTTP 传输携带 BOM 不会破坏脚本执行。

### 3.1.2 向安装脚本传递参数

`irm | iex` 管道形式无法直接传参。如需使用参数，采用 scriptblock 形式：

```powershell
& ([scriptblock]::Create((irm https://hermes-agent.nousresearch.com/install.ps1))) -SkipSetup -Branch main
```

### 3.1.3 先下载再执行（便于审计与重试）

若希望在执行前审查脚本内容，或在网络不稳定时避免重复下载：

```powershell
Invoke-WebRequest https://hermes-agent.nousresearch.com/install.ps1 -OutFile install.ps1
# 可选：审查脚本内容
notepad install.ps1
# 执行（可带参数）
.\install.ps1 [-参数]
```

> **注意 BOM 问题**：若手动下载的 `install.ps1` 携带 UTF-8 BOM，`[scriptblock]::Create((irm ...))` 形式会报错"The assignment expression is not valid"。`irm | iex` 形式会自动剥离 BOM；手动保存时请使用不带 BOM 的 UTF-8 编码：
>
> ```powershell
> $text = (irm https://hermes-agent.nousresearch.com/install.ps1)
> [IO.File]::WriteAllText("$PWD\install.ps1", $text, (New-Object Text.UTF8Encoding $false))
> ```

### 3.1.4 常用安装参数

| 参数 | 默认值 | 用途 |
|---|---|---|
| `-Branch` | `main` | 克隆指定分支（用于测试 PR） |
| `-Commit` | 未设置 | 将安装固定到指定 commit SHA（优先级高于 `-Branch`） |
| `-Tag` | 未设置 | 将安装固定到指定 git tag（如 `v0.14.0`） |
| `-ForceCommit` | 关闭 | 配合 `-Commit`，即使会回滚版本也强制检出 |
| `-NoVenv` | 关闭 | 跳过 venv 创建（高级用法——自行管理 Python） |
| `-SkipSetup` | 关闭 | 跳过安装后的 `hermes setup` 向导 |
| `-HermesHome` | `%LOCALAPPDATA%\hermes` | 覆盖数据目录 |
| `-InstallDir` | `%LOCALAPPDATA%\hermes\hermes-agent` | 覆盖代码存放位置 |
| `-IncludeDesktop` | 关闭 | 同时构建 Electron 桌面应用 |
| `-NonInteractive` | 关闭 | 跳过所有需要用户输入的阶段（CI/无人值守） |
| `-ShowResolvedPaths` | 关闭 | 以 JSON 打印安装程序实际解析的路径后退出（诊断 8.3 短路径问题） |

参数可组合使用，例如：

```powershell
# 跳过设置向导，固定到指定 tag，自定义数据目录
.\install.ps1 -SkipSetup -Tag v0.20.0 -HermesHome "D:\hermes-data"
```

### 3.1.5 安装完成后的第一步

安装结束后，脚本会打印完成横幅并提示重启终端。**关闭当前 PowerShell 窗口并打开一个新窗口**，然后启动 Hermes：

```powershell
hermes              # 进入交互式 CLI
```

若安装时使用了 `-SkipSetup`，手动运行配置向导：

```powershell
hermes setup
```

---

## 3.2 执行策略设置

### 3.2.1 为什么需要关注执行策略

Windows PowerShell（5.1）默认的执行策略（Execution Policy）通常为 `Restricted` 或 `RemoteSigned`。虽然 `irm | iex` 形式通过内存执行脚本，不受执行策略直接限制，但以下场景会受到影响：

- 手动下载 `install.ps1` 后通过 `.\install.ps1` 执行；
- Node.js 自带的 `npm.ps1` 垫片（shim）需要执行 `.ps1` 文件，而安装程序检测到 `npm.ps1` 时会优先切换到 `npm.cmd`；
- 安装过程中子进程调用的 PowerShell 脚本。

### 3.2.2 查看当前执行策略

```powershell
Get-ExecutionPolicy -List
```

输出示例：

```
            Scope ExecutionPolicy
            ----- ---------------
    MachinePolicy       Undefined
       UserPolicy       Undefined
          Process       Undefined
      CurrentUser       Undefined
     LocalMachine    RemoteSigned
```

### 3.2.3 推荐设置：CurrentUser 作用域 RemoteSigned

以**当前用户**身份（无需管理员）执行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

`RemoteSigned` 的含义：
- 本地编写的脚本可以直接运行；
- 从互联网下载的脚本（带有 Mark-of-the-Web 标记）必须由受信任的发布者签名才能运行。

这是安全性与可用性的平衡，也是 Windows 开发者社区最常用的设置。

### 3.2.4 临时绕过（仅当前进程）

若不想修改全局设置，可在启动 PowerShell 时临时绕过：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

或在当前会话中临时设置：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# 关闭窗口后自动恢复
```

> `install.ps1` 在内部安装 `uv` 时，会通过 `-ExecutionPolicy ByPass` 启动子 PowerShell 进程（见脚本中 `Get-PowerShellHostExe` 的调用），因此 uv 的引导安装不受宿主执行策略限制。

### 3.2.5 PowerShell 7（pwsh）用户

若使用 PowerShell 7+（`pwsh.exe`），执行策略同样适用，但默认策略通常更宽松。建议同样检查：

```powershell
pwsh -Command "Get-ExecutionPolicy -List"
```

安装程序会自动检测当前运行的 PowerShell 宿主可执行文件路径（通过 `Get-Process -Id $PID`），避免硬编码 `powershell` 导致在 pwsh 环境下找不到 `powershell.exe` 的问题。

---

## 3.3 Windows 特有注意事项

### 3.3.1 8.3 短路径处理

#### 问题背景

Windows 会为包含空格、点号或重音字符的用户配置文件夹生成 8.3 短文件名别名，例如：

- `C:\Users\First Last` → `C:\Users\FIRST~1.LAS`
- `C:\Users\Stone.ZEN8` → `C:\Users\STONE~1.ZEN`
- 含重音字符的用户名 → `C:\Users\RUBN~1`

系统可能通过该短形式暴露 `%TEMP%`、`%TMP%`、`%LOCALAPPDATA%`、`%APPDATA%`、`%USERPROFILE%` 等环境变量，导致默认的 `HERMES_HOME` 和 `InstallDir` 路径也携带短别名。

PowerShell 的 FileSystem Provider 在处理短路径时会抛出"An object at the specified path ... does not exist"错误（非英文系统上为本地化消息），导致 `Tee-Object`、`Out-File`、`New-Item`、`Test-Path` 等 cmdlet 失败。Node/Electron 构建阶段通过 `Tee-Object` 向 `%TEMP%` 写入日志时尤为明显。

#### 安装程序的自动处理

`install.ps1` 内置了三级 8.3 短路径解析器（`ConvertTo-LongPath` 函数），在安装开始前自动将所有配置文件根路径展开为长路径：

1. **kernel32!GetLongPathNameW**（首选）：通过 P/Invoke 调用 Windows API，能正确处理含重音字符的用户名；
2. **Scripting.FileSystemObject**（COM 回退）：当 P/Invoke 被组策略阻止时使用；
3. **Profile-root 替换**（最终回退）：当卷禁用了 8.3 生成或别名已过期时，用长路径的用户配置根目录重建路径。

安装程序会对 `TEMP`、`TMP`、`LOCALAPPDATA`、`APPDATA`、`USERPROFILE` 五个环境变量逐一规范化，然后重新推导 `HermesHome` 和 `InstallDir`。

#### 诊断方法

若安装程序报告路径不存在，可使用 `-ShowResolvedPaths` 参数查看实际解析的路径：

```powershell
.\install.ps1 -ShowResolvedPaths
```

输出 JSON 示例：

```json
{
  "long_profile_root": "C:\\Users\\First Last",
  "normalized": {
    "TEMP": "C:\\Users\\FIRST~1.LAS\\AppData\\Local\\Temp -> C:\\Users\\First Last\\AppData\\Local\\Temp",
    "LOCALAPPDATA": "C:\\Users\\FIRST~1.LAS\\AppData\\Local -> C:\\Users\\First Last\\AppData\\Local"
  },
  "resolver": "kernel32",
  "temp": "C:\\Users\\First Last\\AppData\\Local\\Temp",
  "hermes_home": "C:\\Users\\First Last\\AppData\\Local\\hermes",
  "install_dir": "C:\\Users\\First Last\\AppData\\Local\\hermes\\hermes-agent"
}
```

#### 手动规避

若自动解析失败（极少见），可显式指定不含空格和特殊字符的安装路径：

```powershell
.\install.ps1 -HermesHome "C:\hermes" -InstallDir "C:\hermes\hermes-agent"
```

或在安装前预设环境变量：

```powershell
$env:HERMES_HOME = "C:\hermes"
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

### 3.3.2 长路径支持

#### Windows 路径长度限制

Windows 传统上限制单个路径最长为 260 个字符（`MAX_PATH`）。Hermes 的依赖树（尤其 `node_modules` 和 Python venv）可能产生超过此限制的深层路径，导致"路径过长"错误。

#### 安装程序的缓解措施

- 默认安装路径 `%LOCALAPPDATA%\hermes\hermes-agent` 相对较短，尽量减少路径深度；
- Python 依赖通过 `uv` 安装，uv 在 Windows 上对长路径有较好的处理能力；
- Node.js 依赖树可能触发长路径问题，尤其是在嵌套较深时。

#### 启用 Windows 长路径支持（推荐）

以**管理员身份**打开 PowerShell，执行：

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

该设置对应组策略：**计算机配置 → 管理模板 → 系统 → 文件系统 → 启用 Win32 长路径**。

启用后，Windows API 将支持最长 32767 个字符的路径（各应用程序仍需在 manifest 中声明 `longPathAware`）。Node.js、Python 3.6+、Git for Windows 等现代工具均支持此设置。

验证是否已启用：

```powershell
(Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem").LongPathsEnabled
# 返回 1 表示已启用
```

### 3.3.3 CRLF 行尾符问题

#### 问题背景

Windows 使用 CRLF（`\r\n`，即回车+换行）作为行尾符，而 Linux/macOS 使用 LF（`\n`，仅换行）。Hermes 的部分组件在 Windows 上通过 Git Bash 执行 shell 脚本，CRLF 会导致：

- shell 脚本报错 `bad interpreter: /bin/bash^M`；
- `.env` 文件中的 BOM 或 CRLF 导致 Python 解析失败；
- Docker 容器内执行挂载的 Windows 文件时报错 `no such file or directory`。

#### 项目级防护

仓库的 `.gitattributes` 文件已强制关键文件使用 LF：

```gitattributes
*.sh        text eol=lf
Dockerfile  text eol=lf
*.dockerfile text eol=lf
docker/entrypoint.sh text eol=lf
```

这确保了即使在 Windows 上 `git clone`，这些文件也不会被转换为 CRLF。

#### Git 全局配置建议

若你在 Windows 上同时使用其他项目，建议配置 Git 的行尾符策略：

```powershell
# 推荐：检出时使用 CRLF（Windows 编辑器友好），提交时转为 LF
git config --global core.autocrlf true

# 更严格：检出时不转换，提交时转为 LF（适合跨平台项目）
git config --global core.autocrlf input
```

对于 Hermes 仓库本身，`.gitattributes` 的优先级高于全局配置，因此无需特别调整。

#### 修复已污染的 CRLF 文件

若已有文件被错误转换为 CRLF（例如手动从 Windows 编辑器保存），可使用 `dos2unix` 修复（在 Git Bash 中）：

```bash
dos2unix path/to/script.sh
```

或使用 PowerShell：

```powershell
$content = [IO.File]::ReadAllText("path\to\script.sh")
$content = $content -replace "`r`n", "`n"
[IO.File]::WriteAllText("path\to\script.sh", $content, (New-Object Text.UTF8Encoding $false))
```

#### BOM 注意事项

避免使用旧版 Windows Notepad 编辑 Hermes 配置文件（`.env`、`.yaml`、`.md`），它们可能带 UTF-8 BOM 保存。虽然 Hermes 在大多数配置读取中容忍 `utf-8-sig`，但折叠 YAML 标量（`description: >`）内部的 BOM 会静默破坏 YAML 解析。推荐使用 VS Code、Notepad++ 等现代编辑器，并确认保存为"UTF-8（无 BOM）"。

### 3.3.4 pywin32 依赖

#### 依赖说明

`pywin32` 是 Python 访问 Windows 原生 API 的扩展库。Hermes 在 Windows 上通过 `pyproject.toml` 声明了以下平台条件依赖：

```toml
"pywin32>=306,<312; sys_platform == 'win32'",
"pywinpty>=2.0.0,<3; sys_platform == 'win32'",
"concurrent-log-handler==0.9.29; sys_platform == 'win32'",
"tzdata==2025.3; sys_platform == 'win32'",
```

| 包 | 用途 |
|---|---|
| `pywin32` | Desktop SSH 的 Windows 远程运行时（`hermes_cli/windows_ssh_runtime.py`）直接导入 `win32security`、`win32file` 等模块；`portalocker` 也依赖它实现跨进程文件锁 |
| `pywinpty` | Windows 上的伪终端（PTY）支持，替代 Linux 的 `ptyprocess` |
| `concurrent-log-handler` | Windows 日志轮转：标准库 `RotatingFileHandler.doRollover()` 使用 `os.rename()`，在 Windows 上因其他进程持有文件句柄而失败（`WinError 32`）；此包通过跨进程文件锁安全轮转 |
| `tzdata` | Windows 不内置 IANA 时区数据库，Python `zoneinfo` 需要此包 |

这些包仅在 `sys_platform == 'win32'` 时安装，不影响 Linux/macOS。

#### 安装方式

这些依赖由 `uv pip install` 自动从 PyPI 安装预编译的 wheel，**无需手动编译**，也无需安装 Visual C++ Build Tools。`pywin32` 的 wheel 已包含所有必要的 DLL。

#### 常见问题

**`ImportError: DLL load failed while importing win32xxx`**

极少数情况下，`pywin32` 的系统 DLL 未正确注册。可在 venv 中手动运行 post-install 脚本：

```powershell
# 激活 venv（或直接使用 venv 中的 python）
& "$env:LOCALAPPDATA\hermes\hermes-agent\venv\Scripts\python.exe" -m pywin32_postinstall -install
```

**`pywin32` 版本冲突**

Hermes 要求 `pywin32>=306,<312`。若系统 Python 中已安装不兼容版本，由于 Hermes 使用独立 venv，不会产生冲突。若使用了 `-NoVenv`，需自行确保版本兼容。

---

## 3.4 环境变量配置

### 3.4.1 PATH 配置

安装程序的 `Set-PathVariable` 函数会将以下目录添加到**用户 PATH**（通过 `[Environment]::SetEnvironmentVariable("Path", ..., "User")`）：

- 默认（使用 venv）：`%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts`
- 使用 `-NoVenv` 时：`%LOCALAPPDATA%\hermes\hermes-agent`

此外，Node.js 的托管目录（`%LOCALAPPDATA%\hermes\node`）会通过 `Set-ManagedNodeFirstOnUserPath` 函数被**移到用户 PATH 的最前面**，确保 Hermes 托管的 Node 22 优先于系统中可能存在的旧版 Node。

> **为什么移到最前面而非追加？** 如果系统已安装 Node 18 且其目录在 PATH 中靠前，独立运行的 `hermes-setup.exe` 或用户直接输入 `npm` 时会解析到错误的 Node 版本。将托管 Node 目录移到最前可确保版本正确。安装程序还会清理重复条目。

#### 验证 PATH

```powershell
# 查看 hermes 命令位置
Get-Command hermes
# 预期输出：C:\Users\<you>\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe

# 查看 Node 版本（应为 22.x）
node --version
```

#### 手动刷新当前会话的 PATH

安装程序会更新当前进程的 `$env:Path`，但**其他已打开的终端窗口不会自动获取更新**。若不想重启终端，可手动刷新：

```powershell
$env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
```

### 3.4.2 HERMES_HOME

`HERMES_HOME` 指定 Hermes 的**数据目录**，存放配置、会话、日志、技能、缓存等用户数据。

#### 默认值

- **Windows 原生**：`%LOCALAPPDATA%\hermes`（即 `C:\Users\<you>\AppData\Local\hermes`）
- 若安装前已设置 `$env:HERMES_HOME`，安装程序会使用该值

安装程序会将 `HERMES_HOME` 持久化为**用户环境变量**：

```powershell
[Environment]::SetEnvironmentVariable("HERMES_HOME", $HermesHome, "User")
```

#### 与 Linux 的差异

Linux/macOS 上默认路径为 `~/.hermes`；Windows 原生使用 `%LOCALAPPDATA%\hermes`。这是因为 Windows 上 `~`（`%USERPROFILE%`）可能受 8.3 短路径问题影响，且 `%LOCALAPPDATA%` 是 Windows 应用数据的标准位置。

> **注意**：Windows 原生安装的数据目录与 WSL2 安装的数据目录**相互独立**——原生数据在 `%LOCALAPPDATA%\hermes`，WSL2 数据在 WSL 内的 `~/.hermes`。两者可以干净共存，但配置和会话不共享。

#### 自定义 HERMES_HOME

可在安装前预设环境变量：

```powershell
# 持久化设置（推荐）
[Environment]::SetEnvironmentVariable("HERMES_HOME", "D:\hermes-data", "User")
# 当前会话也生效
$env:HERMES_HOME = "D:\hermes-data"
# 然后运行安装程序
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

或直接通过安装参数：

```powershell
.\install.ps1 -HermesHome "D:\hermes-data"
```

#### HERMES_HOME 目录布局

```
%LOCALAPPDATA%\hermes\               # HERMES_HOME
├── .env                             # API 密钥与令牌
├── config.yaml                      # CLI 行为配置
├── SOUL.md                          # 全局人格定义
├── cron\                            # 定时任务
├── sessions\                        # 对话会话（FTS5 全文索引）
├── logs\                            # 运行日志
├── memories\                        # 长期记忆
├── skills\                          # 技能库
├── bin\
│   └── uv.exe                       # 托管 uv
├── node\                            # 托管 Node.js 22
├── git\                             # PortableGit（如有）
└── hermes-agent\                    # 代码仓库（InstallDir）
    ├── venv\                        # Python 虚拟环境
    │   └── Scripts\
    │       ├── python.exe
    │       ├── hermes.exe
    │       └── ...
    ├── .git\
    ├── pyproject.toml
    ├── uv.lock
    └── ...
```

### 3.4.3 其他 Windows 专属环境变量

| 变量 | 效果 | 设置时机 |
|---|---|---|
| `HERMES_GIT_BASH_PATH` | 覆盖 `bash.exe` 的发现路径，可指向系统 Git for Windows、WSL bash、MSYS2、Cygwin | 安装程序自动设置为 PortableGit 的 `bash.exe` |
| `HERMES_DISABLE_WINDOWS_UTF8` | 设为 `1` 禁用 UTF-8 控制台垫片，回退到系统代码页 | 排查编码问题时使用 |
| `EDITOR` / `VISUAL` | `/edit` 和 `Ctrl-X Ctrl-E` 使用的编辑器；未设置时默认为 `notepad` | 按需设置 |
| `AGENT_BROWSER_EXECUTABLE_PATH` | 指定外部浏览器可执行文件路径，跳过 Playwright Chromium 下载 | 按需设置 |
| `AGENT_BROWSER_ARGS` | 额外的 Chromium 启动参数 | 按需设置 |
| `NODE_EXTRA_CA_CERTS` | 企业代理场景下指定 Node.js 信任的根 CA 证书 | 企业网络环境 |

#### 设置编辑器示例

```powershell
# VS Code（--wait 至关重要，否则编辑器立即返回空内容）
$env:EDITOR = "code --wait"

# Notepad++
$env:EDITOR = "'C:\Program Files\Notepad++\notepad++.exe' -multiInst -nosession"
```

在 PowerShell profile 中永久设置：

```powershell
notepad $PROFILE
# 添加：$env:EDITOR = "code --wait"
```

### 3.4.4 .env 文件配置

API 密钥等敏感配置应放在 `%HERMES_HOME%\.env` 文件中（安装程序从仓库的 `.env.example` 复制），而非用户环境变量中。这与 Linux 上的做法一致。

`.env` 文件的关键配置项分类：

**LLM 提供商密钥**（至少配置一个）：

```env
# OpenRouter（推荐，一个密钥访问多个模型）
OPENROUTER_API_KEY=sk-or-...

# 或 Fireworks AI
FIREWORKS_API_KEY=...

# 或其他提供商：OpenAI、Google、Kimi、GLM、MiniMax 等
```

**工具 API 密钥**（可选）：

```env
EXA_API_KEY=...           # Web 搜索
FIRECRAWL_API_KEY=...     # 网页爬取
FAL_KEY=...               # 图片生成
BROWSERBASE_API_KEY=...   # 云浏览器
VOICE_TOOLS_OPENAI_KEY=... # TTS / 语音转录
```

**消息平台**（可选）：

```env
TELEGRAM_BOT_TOKEN=...
DISCORD_BOT_TOKEN=...
SLACK_BOT_TOKEN=xoxb-...
```

> **安全提示**：不要将 API 密钥放在系统/用户环境变量中（那样系统上每个进程都能读取）。使用 `.env` 文件，Hermes 会以用户权限读取。不要将 `.env` 提交到版本控制。

---

## 3.5 安装后重启终端的必要性

### 3.5.1 为什么必须重启

安装程序通过 `[Environment]::SetEnvironmentVariable(..., "User")` 修改的是**注册表中的用户环境变量**。Windows 的环境变量更新机制如下：

1. 注册表更新后，**新启动**的进程会从注册表读取最新的环境变量；
2. **已运行**的进程（包括安装脚本所在的 PowerShell 窗口及其所有子进程）仍然持有启动时继承的旧环境块；
3. 广播 `WM_SETTINGCHANGE` 消息可以通知部分应用刷新，但控制台窗口（PowerShell、cmd）通常不会响应。

因此，即使安装程序在当前会话中也更新了 `$env:Path` 和 `$env:HERMES_HOME`，其他**已打开的终端窗口**仍然看不到新的 PATH。

### 3.5.2 安装程序的提示

安装完成时，脚本会明确打印黄色提示：

```
[*] Restart your terminal for PATH changes to take effect
```

### 3.5.3 正确做法

1. **关闭**当前 PowerShell/Windows Terminal 窗口；
2. **重新打开**一个新的 PowerShell 窗口；
3. 验证：

```powershell
hermes --version
Get-Command hermes
```

### 3.5.4 不想重启的临时方案

若确实不想关闭当前窗口，可手动刷新 PATH（见 3.4.1 节），或直接使用完整路径：

```powershell
& "$env:LOCALAPPDATA\hermes\hermes-agent\venv\Scripts\hermes.exe" --version
```

但这对 HERMES_HOME 和其他环境变量同样存在问题，因此**重启终端是最可靠的做法**。

### 3.5.5 其他需要重启的场景

- 修改了 `HERMES_HOME` 环境变量；
- 设置了 `EDITOR`、`HERMES_GIT_BASH_PATH` 等用户环境变量；
- 更新了 Node.js 或 Python 版本（PATH 顺序变化）；
- 安装了新的系统工具（ripgrep、ffmpeg）并需要当前会话识别。

---

## 3.6 WSL2 推荐方案说明

### 3.6.1 何时选择 WSL2

虽然 Hermes 支持原生 Windows，但在以下场景中 **WSL2 是更推荐的方案**：

| 场景 | 原因 |
|---|---|
| 需要使用 Dashboard `/chat` 内嵌终端 | 该面板需要 POSIX PTY（`ptyprocess`），原生 Windows 无等效原语 |
| 大量 POSIX 开发工作 | 希望 Hermes 会话与开发工具共享同一 Linux 文件系统和路径语义 |
| 已有 WSL2 环境 | 不想维护第二套安装 |
| 需要 `fork` 语义、UNIX socket、Linux 信号 | 原生 Windows 的 Git Bash 无法提供完整 POSIX 语义 |
| 文件监视器（inotify）可靠性 | 跨 9P 协议的文件监视不稳定，WSL2 内 ext4 可靠 |

### 3.6.2 何时原生更合适

- 交互式聊天、gateway、cron、浏览器工具、MCP 服务器等绝大多数功能在原生 Windows 上运行良好；
- 不想在每次引用文件或打开 URL 时处理 WSL ↔ Windows 边界问题；
- 需要直接访问 Windows 硬件（GPU 本地模型推理使用 Windows 版 Ollama/LM Studio 即可）。

### 3.6.3 安装 WSL2

在**管理员 PowerShell** 中执行：

```powershell
wsl --install
```

全新 Windows 10 22H2+ 或 Windows 11 上会自动安装 WSL2 内核、虚拟机平台和默认 Ubuntu。按提示重启，重启后设置 Linux 用户名和密码。

验证 WSL 版本：

```powershell
wsl --list --verbose
```

应显示 `VERSION 2`。若为 WSL1，执行转换：

```powershell
wsl --set-version Ubuntu 2
wsl --set-default-version 2
```

> Hermes 在 WSL1 上无法可靠运行（系统调用转译存在偏差），必须使用 WSL2。

### 3.6.4 启用 systemd（推荐）

在 WSL 内执行：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[interop]
enabled=true
appendWindowsPath=true

[automount]
options = "metadata,umask=22,fmask=11"
EOF
```

然后在 PowerShell 中执行 `wsl --shutdown`，重新打开 WSL 终端。`ps -p 1 -o comm=` 应输出 `systemd`。

### 3.6.5 在 WSL2 内安装 Hermes

打开 WSL2 shell 后，使用 Linux 安装命令：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes
```

安装程序将 WSL2 视为普通 Linux，使用 `~/.hermes` 作为数据目录，无需任何 WSL 专属配置。

### 3.6.6 两种安装的共存

原生 Windows 和 WSL2 安装可以**干净共存**：

| 维度 | 原生 Windows | WSL2 |
|---|---|---|
| 数据目录 | `%LOCALAPPDATA%\hermes` | `~/.hermes`（WSL 内） |
| 代码目录 | `%LOCALAPPDATA%\hermes\hermes-agent` | `~/.hermes/hermes-agent` |
| 配置/会话 | 独立 | 独立 |
| Shell 命令 | PowerShell 中 `hermes` | WSL bash 中 `hermes` |

两者互不干扰，但配置和会话历史**不共享**。若要在两者间迁移，可手动复制 `.env`、`config.yaml`、`SOUL.md`、`skills/`、`memories/` 等文件（注意行尾符和路径格式差异）。

### 3.6.7 WSL2 文件系统注意事项

- **将项目放在 Linux 文件系统内**（`~/code/...`），不要放在 `/mnt/c/...`，否则 I/O 性能慢 10–100 倍，且文件监视器不可靠；
- WSL 内访问 Windows 文件：`/mnt/c/Users/...`；
- Windows 访问 WSL 文件：`\\wsl.localhost\Ubuntu\home\...`；
- 在 WSL 内配置 Git 使用 LF：`git config --global core.autocrlf input`。

### 3.6.8 WSL2 网络（访问 Windows 上的本地模型）

若在 Windows 上运行 Ollama/LM Studio，WSL2 内的 Hermes 需要访问它：

- **Windows 11 22H2+**：启用镜像网络模式（在 `%USERPROFILE%\.wslconfig` 中设置 `networkingMode=mirrored`，然后 `wsl --shutdown`），之后 `localhost` 在两侧互通；
- **Windows 10/旧版**：使用 WSL 网关 IP，确保 Windows 服务绑定 `0.0.0.0`，并在 Windows 防火墙放行端口。

---

## 3.7 Windows 特有故障排查

### 3.7.1 权限问题

#### 安装脚本无法运行

**现象**：`.\install.ps1` 提示"无法加载文件，因为在此系统上禁止运行脚本"。

**原因**：PowerShell 执行策略阻止了本地脚本运行。

**解决**：见 3.2 节，设置 `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`，或使用 `powershell -ExecutionPolicy Bypass -File .\install.ps1`。

#### 访问被拒绝（Access to the path is denied）

**现象**：安装过程中出现 `UnauthorizedAccessException` 或 `WinError 5`。

**可能原因与解决**：

1. **杀毒软件实时防护锁定文件**：暂时禁用实时防护或将 `%LOCALAPPDATA%\hermes` 加入排除列表（见 3.7.2 节）；
2. **文件被其他进程占用**：关闭正在运行的 Hermes、gateway、编辑器，然后重试；
3. **目录权限异常**：检查目录所有权：

```powershell
icacls "$env:LOCALAPPDATA\hermes"
# 若权限异常，重置：
icacls "$env:LOCALAPPDATA\hermes" /reset /T /C /Q
```

4. **需要管理员权限的操作**：安装程序本身不需要管理员，但如果你将 `-HermesHome` 设到了 `C:\Program Files\` 等系统目录，则需要以管理员身份运行 PowerShell。**推荐使用默认路径或用户目录下的路径**。

### 3.7.2 杀毒软件误报

#### Windows Defender / Bitdefender 隔离 uv.exe

**现象**：安装后 `hermes` 命令无法运行，或安装过程中报告 `uv.exe` 被删除；杀毒软件将 `%LOCALAPPDATA%\hermes\bin\uv.exe` 标记为恶意软件。

**原因**：这是**误报**。`uv.exe` 是 Astral 开发的 Rust 编写的 Python 包管理器，未签名。基于机器学习的杀毒引擎常将下载并安装包的未签名 Rust 二进制标记为可疑。

**验证文件真实性**：

```powershell
# 安装 GitHub CLI
winget install --id GitHub.cli
gh auth login

# 验证 uv 二进制
$uv = "$env:LOCALAPPDATA\hermes\bin\uv.exe"
$ver = (& $uv --version).Split(' ')[1]
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$zip = "$env:TEMP\uv.zip"
Invoke-WebRequest "https://github.com/astral-sh/uv/releases/download/$ver/uv-x86_64-pc-windows-msvc.zip" -OutFile $zip -UseBasicParsing
gh attestation verify $zip --repo astral-sh/uv
Expand-Archive $zip "$env:TEMP\uv_x" -Force
(Get-FileHash "$env:TEMP\uv_x\uv.exe").Hash -eq (Get-FileHash $uv).Hash
```

若 attestation 显示"Verification succeeded"且最后输出 `True`，则文件可信。

**添加排除项**：

- **Windows Defender**（以管理员身份运行 PowerShell）：

```powershell
Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\hermes\bin"
```

- **Bitdefender**：在控制台中添加例外（Protection → Antivirus → Settings → Manage Exceptions）。

> **建议排除整个文件夹而非单个文件哈希**——Hermes 更新时 `uv` 会变化，哈希也随之改变。

#### npm 安装阶段的 TLS 证书错误

**现象**：npm 报错 `unable to get local issuer certificate`、`self-signed certificate in certificate chain` 或 `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`。

**原因**：企业代理或杀毒软件拦截 HTTPS 流量并替换证书，Node.js 不信任该根 CA。这不是权限问题。

**解决**：

1. 向 IT 部门获取企业根 CA 证书（`.pem`/`.crt`）；
2. 设置环境变量：

```powershell
setx NODE_EXTRA_CA_CERTS "C:\path\to\corp-ca.pem"
```

3. **打开新终端**后重新运行安装程序。

临时（较不安全）替代方案：

```powershell
npm config set strict-ssl false
# 安装完成后重新启用：
npm config set strict-ssl true
```

### 3.7.3 路径空格问题

#### 用户名含空格

若 Windows 用户名含空格（如 `C:\Users\First Last`），安装程序的 8.3 短路径处理（见 3.3.1 节）会自动展开为长路径。若仍有问题：

1. 使用 `-ShowResolvedPaths` 诊断；
2. 显式指定不含空格的路径：

```powershell
.\install.ps1 -HermesHome "C:\hermes" -InstallDir "C:\hermes\hermes-agent"
```

#### 自定义路径含空格

若 `-HermesHome` 或 `-InstallDir` 路径含空格，确保在 PowerShell 中用引号包裹：

```powershell
.\install.ps1 -HermesHome "C:\Program Files\hermes"
```

但**不推荐**将 Hermes 安装到含空格的路径，因为部分子进程（npm scripts、Git Bash）对空格路径的处理可能不一致。推荐使用 `C:\hermes` 或默认路径。

#### WinError 193 %1 is not a valid Win32 application

**现象**：运行工具时报错 `[WinError 193] %1 is not a valid Win32 application`。

**原因**：调用了无扩展名的 shebang 脚本（如 `npx` 而非 `npx.cmd`）。Windows 的 `CreateProcessW` 无法直接执行 shebang 脚本。

**解决**：始终使用 `.cmd` 垫片。Hermes 内部通过 `shutil.which(cmd, path=...)` 解析时会让 PATHEXT 识别 `.CMD`。若你在自定义脚本中调用，使用 `npx.cmd` 而非 `npx`。

### 3.7.4 Node.js 相关问题

#### npm.ps1 被执行策略阻止

安装程序会自动检测并优先使用 `npm.cmd` 而非 `npm.ps1`。若日志中出现"Only npm.ps1 available"警告：

- 安装 Node.js via winget（提供 `npm.cmd`）；
- 或设置执行策略（见 3.2 节）。

#### 系统 Node 版本过旧

**现象**：`agent-browser` 报奇怪的 Node 版本错误，或 `npm ci` 失败。

**原因**：PATH 中靠前的位置存在旧版系统 Node（如 Node 18），覆盖了 Hermes 托管的 Node 22。

**解决**：

```powershell
# 检查实际使用的 node
where.exe node
# 若系统 Node 在前，将 Hermes 的 node 目录移到前面
$hermesNode = "$env:LOCALAPPDATA\hermes\node"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$items = $userPath -split ";" | Where-Object { $_ -ne $hermesNode }
[Environment]::SetEnvironmentVariable("Path", ($hermesNode + ";" + ($items -join ";")), "User")
```

或卸载系统 Node（如果不再需要）。

### 3.7.5 编码与显示问题

#### 中文/日文/阿拉伯文字符显示为 `?`

**原因**：UTF-8 stdio 垫片未激活，或控制台宿主不支持 UTF-8。

**排查步骤**：

1. 确认 `HERMES_DISABLE_WINDOWS_UTF8` 未设置：

```powershell
Get-ChildItem env:HERMES_DISABLE_WINDOWS_UTF8
# 若无输出则未设置
```

2. 使用 **Windows Terminal**（而非旧版 `cmd.exe` 或传统 PowerShell 控制台）；
3. 安装程序在安装时已将控制台输出编码设为 UTF-8（`[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()`），但这仅影响安装过程。

#### UnicodeEncodeError: 'charmap' codec

**原因**：Python 的 stdio 使用了系统代码页（cp1252/cp437）而非 UTF-8。

**解决**：Hermes 的 `hermes_cli/stdio.py::configure_windows_stdio()` 会在每个入口点自动处理。若手动运行 Python 脚本遇到此问题：

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
```

### 3.7.6 Git Bash 相关问题

#### 找不到 bash.exe

**现象**：终端工具报错"bash not found"。

**排查**：

1. 检查 `HERMES_GIT_BASH_PATH`：

```powershell
echo $env:HERMES_GIT_BASH_PATH
Test-Path $env:HERMES_GIT_BASH_PATH
```

2. 若 PortableGit 安装失败，手动安装 Git for Windows：

```powershell
winget install --id Git.Git
```

3. 手动指定 Git Bash 路径：

```powershell
[Environment]::SetEnvironmentVariable("HERMES_GIT_BASH_PATH", "C:\Program Files\Git\bin\bash.exe", "User")
```

#### MinGit busybox 变体问题

若手动下载 MinGit，确保选择**非 busybox** 变体（`MinGit-*-64-bit.zip`），而非 `MinGit-*-busybox-64-bit.zip`。busybox 构建附带的是 `ash` 而非 `bash`，且大多数 coreutils 工具缺失。

### 3.7.7 安装后命令找不到

**现象**：安装完成后输入 `hermes` 提示"不是内部或外部命令"。

**原因**：当前终端未获取更新后的 PATH。

**解决**：

1. **关闭并重新打开 PowerShell 窗口**（最常见原因）；
2. 验证用户 PATH 中包含 Hermes 目录：

```powershell
[Environment]::GetEnvironmentVariable("Path", "User") -split ";" | Select-String "hermes"
```

3. 直接用完整路径运行：

```powershell
& "$env:LOCALAPPDATA\hermes\hermes-agent\venv\Scripts\hermes.exe" --version
```

4. 若 PATH 中确实缺失，手动添加：

```powershell
$hermesBin = "$env:LOCALAPPDATA\hermes\hermes-agent\venv\Scripts"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$hermesBin*") {
    [Environment]::SetEnvironmentVariable("Path", "$hermesBin;$userPath", "User")
}
```

### 3.7.8 浏览器工具问题

#### Chromium 安装失败

**现象**：首次使用浏览器工具时超时或报错。

**解决**：

```powershell
hermes doctor
# 按提示手动安装：
npx playwright install chromium
```

若 GitHub 下载受限，可设置 Playwright 镜像：

```powershell
$env:PLAYWRIGHT_DOWNLOAD_HOST = "https://npmmirror.com/mirrors/playwright"
npx playwright install chromium
```

#### agent-browser 报 Node 版本错误

见 3.7.4 节。

### 3.7.9 Gateway 无法持续运行

**现象**：重启后 gateway 不自动启动。

**排查**：

```powershell
hermes gateway status
schtasks /Query /TN HermesGateway /V /FO LIST
```

若组策略阻止了 `ONLOGON` 计划任务，可回退到 Startup 文件夹方式：

```powershell
hermes gateway uninstall
$env:HERMES_GATEWAY_FORCE_STARTUP = "1"
hermes gateway install
```

### 3.7.10 安装日志与诊断

#### 查看安装过程日志

安装程序的输出直接打印到控制台。若需要保存日志：

```powershell
.\install.ps1 2>&1 | Tee-Object -FilePath install.log
```

#### 运行 hermes doctor

```powershell
hermes doctor
```

`hermes doctor` 会检查 Python 环境、Node.js、浏览器工具、配置文件、网络连通性、系统依赖（git、ripgrep、ffmpeg）、权限与目录结构等，并给出修复建议。

#### 查看 npm 调试日志

npm 失败时，安装程序会自动定位并打印 npm 调试日志（位于 `<npm-cache>\_logs\`）的最后 200 行。也可手动查看：

```powershell
$npmCache = npm config get cache
Get-ChildItem "$npmCache\_logs\*-debug-*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 50
```

---

## 3.8 卸载

### 3.8.1 标准卸载

```powershell
hermes uninstall
```

这会移除：
- schtasks 计划任务条目；
- Startup 文件夹快捷方式；
- `hermes.cmd` 垫片；
- `%LOCALAPPDATA%\hermes\hermes-agent\` 代码目录；
- 用户 PATH 中的相关条目。

**保留** `%USERPROFILE%\.hermes\`（配置、认证、技能、会话、日志），以便重新安装时恢复。

### 3.8.2 彻底清除

```powershell
hermes uninstall
Remove-Item -Recurse -Force "$env:USERPROFILE\.hermes"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"
```

若自定义了 `HERMES_HOME`，删除对应目录。

### 3.8.3 清理环境变量

卸载后手动移除残留的用户环境变量（如有）：

```powershell
[Environment]::SetEnvironmentVariable("HERMES_HOME", $null, "User")
[Environment]::SetEnvironmentVariable("HERMES_GIT_BASH_PATH", $null, "User")
```

---

## 3.9 小结

Windows PowerShell 安装脚本 `install.ps1` 为 Windows 10/11 提供了全自动的原生安装体验，核心设计要点包括：

- **零管理员权限**：所有组件（uv、Python、Node、PortableGit）均安装在用户目录 `%LOCALAPPDATA%\hermes` 下；
- **8.3 短路径自动修正**：三级解析器（kernel32 → COM → profile-root）处理含空格/特殊字符的用户名；
- **平台条件依赖**：`pywin32`、`pywinpty`、`concurrent-log-handler`、`tzdata` 仅在 Windows 上安装，预编译 wheel 无需编译工具链；
- **PATH 与 HERMES_HOME 持久化**：通过注册表写入用户级环境变量，新终端自动生效；
- **执行策略兼容**：脚本内部使用 `-ExecutionPolicy Bypass` 启动子进程，并优先使用 `.cmd` 而非 `.ps1` npm 垫片；
- **CRLF/BOM 防护**：`.gitattributes` 强制 shell 脚本使用 LF，安装程序剥离 BOM；
- **WSL2 备选**：需要完整 POSIX 语义或 Dashboard 内嵌终端时，推荐使用 WSL2 方案，两种安装可干净共存；
- **杀毒软件误报处理**：提供 uv.exe 的 GitHub attestation 验证方法与排除项配置指导。

安装完成后**务必重启终端**，使 PATH 和环境变量生效。遇到问题时优先运行 `hermes doctor` 诊断。
