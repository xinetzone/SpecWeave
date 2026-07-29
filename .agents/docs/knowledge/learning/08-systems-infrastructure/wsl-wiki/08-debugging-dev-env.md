---
id: "wsl-wiki-08-debugging-dev-env"
title: "调试诊断与开发环境搭建"
source: "spec:create-wsl-wiki-tutorial"
date: "2026-07-20"
category: "learning"
tags: ["wsl", "debugging", "diagnostics", "development", "vscode", "gpu", "cuda", "docker", "debug-shell"]
---

# 调试诊断与开发环境搭建

本文档介绍 WSL 的调试诊断工具、日志收集方法、常见问题排查流程，以及开发环境搭建指南。

---

## 第一部分：调试诊断工具与方法

### 1.1 诊断命令集合

#### Windows 侧命令

| 命令 | 用途 |
|---|---|
| `wsl --status` | 查看运行状态、默认版本、内核版本 |
| `wsl --version` | 查看 WSL/内核/WSLg 各组件版本 |
| `wsl -l -v` | 列出所有发行版状态（Running/Stopped）和 WSL 版本 |
| `wsl --debug-shell` | 进入 VM root 调试 shell（需管理员） |
| `wsl --shutdown` | 终止所有发行版和 VM，用于重启使配置生效 |
| `wsl --update` | 更新 WSL 内核组件 |

```powershell
wsl -l -v
wsl --version
wsl --shutdown
```

#### WSL 内命令

| 命令 | 用途 |
|---|---|
| `dmesg` | 查看内核日志 |
| `journalctl -b` | 查看 systemd 启动日志 |
| `ps aux \| grep -E "gns\|plan9\|init"` | 检查核心进程 |
| `ip a` | 查看网络接口 |
| `ls -la /mnt/wsl/` | 查看跨分发版共享目录 |
| `mount \| grep drvfs` | 检查 Windows 驱动器挂载 |
| `cat /etc/resolv.conf` | 查看 DNS 配置 |

#### /mnt/wsl/ 共享目录

`/mnt/wsl/` 是 VM 内所有分发版共享的运行时挂载点：
- `/mnt/wsl/log/`：WSL 运行日志
- `/mnt/wsl/data/`：跨分发版共享数据
- `/mnt/wslg/`：WSLg（GUI）运行时和 X11 socket

### 1.2 日志收集

#### 日志位置

| 日志来源 | 位置/访问方式 |
|---|---|
| WSL 临时日志 | `/mnt/c/Users/<用户名>/AppData/Local/Temp/wsl/` |
| WSL 服务事件日志 | 事件查看器 → 应用程序和服务日志 → Microsoft → Windows → WSL |
| LxssManager 日志 | 事件查看器 → 同上路径下的 LxssManager |
| 内核日志 | WSL 内执行 `dmesg` |
| 系统日志 | WSL 内 `/var/log/syslog` 或 `journalctl` |

#### 启用详细日志

**方法 1：环境变量启用 ETW**
```powershell
$env:WSL_ETW=1
wsl
```

**方法 2：官方诊断脚本**
```powershell
# 从 https://github.com/microsoft/WSL/blob/master/diagnostics/collect-wsl-logs.ps1 获取
.\collect-wsl-logs.ps1                  # 常规日志
.\collect-wsl-logs.ps1 -LogProfile networking  # 网络专项
.\collect-wsl-logs.ps1 -Dump            # 含崩溃转储
```

**方法 3：ETL 追踪**
```powershell
wpr -start wsl.wprp!WSL-Networking -filemode
# 复现问题
wpr -stop wsl-trace.etl
```

### 1.3 常见问题诊断流程

#### WSL 无法启动
1. **检查虚拟化**：任务管理器 → 性能 → CPU → 虚拟化：已启用（未启用则 BIOS 开启 VT-x/AMD-V）
2. **检查 Windows 功能**：管理员 PowerShell 执行：
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
   重启后执行 `wsl --update`
3. **查看事件日志**：事件查看器中 WSL/LxssManager 节点定位具体错误

#### 分发版启动失败
```powershell
wsl --shutdown
wsl -d <发行版名>
# 若仍失败，管理员 PowerShell 进入 debug-shell：
wsl --debug-shell
# 在 debug-shell 中检查：
ps aux          # init 进程是否正常
dmesg | tail    # 最后内核消息
```

#### 网络问题
```bash
cat /etc/resolv.conf           # 检查 DNS
ps aux | grep gns              # gns 进程是否运行
ping 8.8.8.8                   # IP 连通性
ping github.com                # DNS 解析
# NAT 模式有问题可切换 mirrored：编辑 %USERPROFILE%/.wslconfig
# [wsl2]
# networkingMode=mirrored
# wsl --shutdown 重启
```

#### 文件系统问题
```bash
mount | grep drvfs             # DrvFs 挂载检查
ps aux | grep plan9            # plan9 进程
ls -la /mnt/c/Users/           # 权限检查
```

#### 性能问题
1. 配置内存限制（`%USERPROFILE%/.wslconfig`）：
   ```ini
   [wsl2]
   memory=4GB
   processors=2
   swap=2GB
   ```
2. ✅ 项目文件放在 WSL 文件系统（`~/projects/`）性能最佳
3. ❌ 避免在 `/mnt/c/` 下频繁读写开发项目（DrvFs 性能差）

### 1.4 wsl --debug-shell 使用说明

`wsl --debug-shell` 进入 VM 的 root shell，可访问所有命名空间和内核接口，是终极诊断工具。

**进入方式**：管理员 PowerShell 执行 `wsl --debug-shell`

**debug-shell 能力**：

| 能力 | 说明 | 示例命令 |
|---|---|---|
| 检查核心进程 | 查看 mini_init/gns/plan9/relay 所有进程 | `ps auxf`、`top` |
| 访问 procfs/sysfs | 不受分发版 namespace 限制 | `cat /proc/meminfo` |
| 检查所有挂载点 | 包括提权/非提权双 drvfs 命名空间 | `cat /proc/mounts` |
| 修复损坏配置 | 手动挂载分发版 VHD 编辑文件 | `mount /dev/sdX /mnt && vi /mnt/etc/wsl.conf` |
| gdb 调试 | 附加核心进程 | `gdb -p <pid>` |

**典型场景**：分发版无法启动时检查 init 是否崩溃、修复损坏的配置文件

> ⚠️ **安全警告**：debug-shell 权限极高，可访问所有分发版文件系统，错误操作可能导致数据丢失，仅用于诊断，常规操作在普通分发版内执行。

---

## 第二部分：开发环境搭建

### 2.1 VS Code + WSL 开发（推荐）

VS Code Remote - WSL 扩展提供无缝 Linux 开发体验。

**安装步骤**：
1. 安装 Windows 版 VS Code：https://code.visualstudio.com/
2. 安装扩展：搜索 `Remote - WSL`（ID: `ms-vscode-remote.remote-wsl`）
3. 打开项目：
   ```bash
   cd ~/projects/my-project
   code .
   ```
   或在 VS Code 中按 `Ctrl+Shift+P` → "WSL: Connect to WSL"

**工作原理**（客户端-服务器架构）：
- **Windows 侧（UI）**：窗口管理、编辑器 UI、主题/图标等 UI 扩展
- **WSL 侧（Server）**：文件访问、终端、Git、语言服务（LSP）、调试器、工作区扩展
- 首次连接自动在 WSL 内安装 VS Code Server

**优势**：终端/Git/语言服务全在 WSL 内运行，保留 Windows 侧编辑体验，端口自动转发。

### 2.2 GPU 计算（CUDA/DirectML）

**前提条件**：Windows 11 或 Win10 21H2+、支持 WDDM 3.0 的 GPU 驱动、WSL2。

**NVIDIA CUDA 搭建**：

1. **安装 Windows 侧 NVIDIA 驱动**：https://www.nvidia.com/download/index.aspx
   > ⚠️ **不要**在 WSL 内安装 NVIDIA Linux 驱动，只安装 Windows 侧驱动

2. **WSL 内安装 CUDA Toolkit**：
   ```bash
   wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
   sudo dpkg -i cuda-keyring_1.1-1_all.deb
   sudo apt-get update && sudo apt-get -y install cuda-toolkit-12-6
   echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
   echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **验证**：
   ```bash
   nvidia-smi  # 应显示 GPU 信息
   # PyTorch GPU 验证
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   python3 -c "import torch; print(torch.cuda.is_available())"
   ```

DirectML 支持全厂商 GPU，`pip install tensorflow-directml-plugin` 即可。

### 2.3 Docker 容器开发

**方式 1：Docker Desktop with WSL2 backend（推荐新手）**
- 自动集成 WSL2、提供 GUI、支持 Docker Compose/Kubernetes
- 安装：https://www.docker.com/products/docker-desktop/
- 设置 → Resources → WSL Integration 中启用需要的发行版
- 验证：`docker run hello-world`

**方式 2：原生 Docker Engine in WSL（轻量纯 CLI）**
```bash
# 需先启用 systemd（第7章）
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```

**选择建议**：需要 GUI/Kubernetes/Windows 容器用 Docker Desktop；纯 CLI/最小化资源用原生 Docker。

### 2.4 Web 与通用开发环境

**基础工具**：
```bash
sudo apt-get update && sudo apt-get install -y build-essential git curl wget
```

**Node.js（nvm 管理版本）**：
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install --lts && nvm use --lts
```

**Python（pyenv 管理版本）**：
```bash
# 先安装 pyenv 依赖（build-essential libssl-dev zlib1g-dev 等）
curl https://pyenv.run | bash
# 按提示添加 PATH 到 ~/.bashrc
pyenv install 3.12 && pyenv global 3.12
```

**端口自动转发**：WSL 内启动的服务（如 `npm run dev`、`python3 -m http.server`），Windows 浏览器直接访问 `localhost:端口` 即可。

**数据库**：
```bash
# PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
# MySQL
sudo apt-get install -y mysql-server && sudo systemctl start mysql
# Redis
sudo apt-get install -y redis-server && sudo systemctl start redis-server
```

**C/C++ 开发**：
```bash
sudo apt-get install -y gdb cmake gcc g++
g++ -g hello.cpp -o hello && gdb ./hello
```

### 2.5 Git 配置

```bash
git config --global user.name "你的名字"
git config --global user.email "y*********@***********"
git config --global core.autocrlf input          # CRLF 换行符处理
git config --global core.editor "nano"           # 默认编辑器
# 凭据缓存（可选：Git Credential Manager 集成 Windows）
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'

# SSH 密钥
ssh-keygen -t ed25519 -C "y*********@***********"
eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub  # 添加到 GitHub/GitLab
```

### 2.6 Windows Terminal 集成（推荐终端）

- **安装**：Microsoft Store 搜索"Windows Terminal"
- **自动特性**：自动识别所有已安装 WSL 发行版并添加 Profile，无需手动配置
- **推荐配置**（`Ctrl+,` 打开设置）：
  1. 设置 WSL 为默认启动 Profile
  2. 字体推荐 `Cascadia Code PL`
  3. 常用快捷键：`Ctrl+Shift+T` 新建标签、`Alt+D` 分屏

---

## 本章小结

- 快速状态查看：`wsl --status`、`wsl --version`、`wsl -l -v`
- 问题排查第一步：`wsl --shutdown` 重启，再查事件日志
- `wsl --debug-shell` 是终极诊断工具，需管理员权限且谨慎操作
- VS Code + Remote-WSL 是最佳开发体验组合
- GPU 计算：只装 Windows 侧 NVIDIA 驱动，WSL 内装 CUDA toolkit
- Docker 二选一：Docker Desktop（GUI 友好）或原生 Docker Engine（轻量）
- 性能关键：项目文件放在 WSL 文件系统（`~/`）内，不要放 `/mnt/c/`

---

← [上一章：网络、配置与systemd](07-network-config-systemd.md) | [返回目录](README.md) | [下一章：最佳实践与FAQ](09-best-practices-faq.md) →
