# entrypoint.ps1 编写规范

## 基本要求

### 1. 严格模式
entrypoint.ps1 必须在开头设置：
```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
```

### 2. 日志格式
使用统一的日志函数：
```powershell
function Write-Info { param([string]$Message) Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [INFO]  $Message" }
function Write-Warn { param([string]$Message) Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [WARN]  $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [ERROR] $Message" -ForegroundColor Red }
```

## 启动流程

### 服务启动顺序
1. **Banner** - 显示容器启动信息
2. **Diagnostics** - 系统诊断（Python/conda/Docker版本、free-threading状态）
3. **Password Setup** - 设置 devuser 密码（环境变量或随机生成）
4. **SSH Keys** - 注入 SSH_PUBLIC_KEY 到 authorized_keys
5. **Start sshd** - 启动 OpenSSH Server 服务
6. **Start Jupyter** - 以 devuser 身份后台启动 JupyterLab
7. **Ready Banner** - 显示连接信息
8. **Monitor Loop** - 保持容器运行，监控服务状态

### 命令模式
当传入命令参数时（`docker run ... <command>`），直接执行命令而非启动服务：
```powershell
if ($args.Count -gt 0) {
    & $args[0] $args[1..($args.Count-1)]
    exit $LASTEXITCODE
}
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| USER_PASSWORD | 随机生成 | devuser 用户密码 |
| JUPYTER_TOKEN | 随机生成 | Jupyter 认证 token |
| JUPYTER_PASSWORD | 空 | Jupyter 密码（优先级高于 token） |
| JUPYTER_PORT | 8888 | Jupyter 监听端口 |
| JUPYTER_ALLOW_ORIGIN | * | CORS 允许源 |
| ENABLE_SSH | yes | 是否启动 SSH 服务 |
| ENABLE_JUPYTER | yes | 是否启动 Jupyter 服务 |
| SSH_PUBLIC_KEY | 空 | 注入的 SSH 公钥 |
| Py_GIL_DISABLED | 1 | 已在系统级设置，entrypoint 中确保可见 |

## 密码管理

- USER_PASSWORD 未设置时生成 16 位随机密码
- 随机密码必须在启动日志中醒目标记（`****` 框）
- Windows 上使用 `Set-LocalUser` 设置密码

## 服务管理

### SSH (sshd)
- 使用 `Start-Service sshd` 启动
- 启动前确保 host keys 存在（`ssh-keygen -A`）
- 设置 sshd_config 权限
- 添加防火墙规则（如需要）

### Jupyter
- 以 devuser 身份后台启动（使用 Start-Process）
- 配置文件在运行时生成（token/password）
- 工作目录默认 `C:\workspace`
- 日志重定向到 `C:\ProgramData\devcontainer\jupyter.log`

## 信号处理

Windows 容器的信号处理有限：
- 使用 `try/catch` 捕获终止
- 监控循环中每 30 秒检查服务状态
- 服务异常退出时尝试重启

## Ready Banner

启动完成后必须显示包含以下信息的横幅：
- SSH 连接命令和密码
- Jupyter URL 和 token/password
- Docker DooD 模式说明
- 工作目录位置
- Python free-threading 说明
