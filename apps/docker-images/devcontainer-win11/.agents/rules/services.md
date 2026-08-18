# 服务配置规范

## SSH 服务 (sshd)

### 安装
Windows Server 2022 使用 `Add-WindowsCapability` 安装 OpenSSH Server：
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
```

### 配置
- 配置文件路径：`C:\ProgramData\ssh\sshd_config`
- 端口：22
- 禁用 Administrator 登录：`DenyUsers Administrator`
- 允许密码认证和公钥认证
- 默认 Shell 设置为 PowerShell 7（通过注册表）：
  ```powershell
  New-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell `
      -Value 'C:\Program Files\PowerShell\7\pwsh.exe' -PropertyType String -Force
  ```

### 启动
```powershell
Set-Service -Name sshd -StartupType Automatic
Start-Service sshd
```

## Jupyter 服务

### 环境
- Conda 环境：`C:\conda\envs\main`
- Python：free-threading (cp314t)
- 包：jupyterlab, ipykernel, notebook

### 配置
- 监听地址：0.0.0.0
- 端口：8888
- 工作目录：`C:\workspace`
- Token：运行时生成或通过 JUPYTER_TOKEN 环境变量设置
- 不自动打开浏览器

### Kernel
安装时注册 free-threading kernel：
```powershell
python -m ipykernel install --name main --display-name "Python 3.14 (free-threading)" --sys-prefix
```

## Docker DooD 服务

### 配置
- 仅安装 Docker CLI（docker.exe），不安装 dockerd
- DOCKER_HOST：`npipe:////./pipe/docker_engine`
- Compose v2 作为 CLI plugin 安装

### 运行时挂载
启动容器时必须挂载宿主命名管道：
```powershell
docker run -v //./pipe/docker_engine://./pipe/docker_engine ...
```

### 说明
- 容器内 `docker ps` 显示宿主机的容器列表
- 不能在 Windows 容器内运行嵌套容器
- 如需构建镜像，实际在宿主 Docker 引擎上执行

## 健康检查

### HEALTHCHECK 指令
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 `
    CMD ["pwsh.exe", "-File", "C:\\ProgramData\\devcontainer\\healthcheck.ps1"]
```

### 检查项
healthcheck.ps1 必须检查：
1. SSH 端口 22 监听（Get-NetTCPConnection）
2. Jupyter HTTP 响应（Invoke-WebRequest to localhost:8888）
3. （可选）Python free-threading 状态

### 返回码
- 0：healthy
- 1：unhealthy

## 用户权限

### devuser 约束
- 本地用户，非域用户
- **禁止**加入 Administrators 组
- 属于 Users 组
- 对 `C:\workspace` 有读写权限
- 对自己的用户目录 `C:\Users\devuser\` 有完全控制
- 密码永不过期

### 目录权限
- C:\workspace: Users 组修改权限
- C:\Users\devuser\.ssh: devuser 完全控制
- C:\ProgramData\ssh: System/Administrators 完全控制，Users 读取
- C:\ProgramData\devcontainer: Everyone 读取和执行
