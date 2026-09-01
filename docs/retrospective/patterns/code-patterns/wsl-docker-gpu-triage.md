---
id: bp-wsl-docker-gpu-triage-v1
title: "WSL Docker GPU三层诊断修复模式"
type: code
date: 2026-08-15
maturity: L1-draft
source: ../../reports/environment-setup/retrospective-wsl-docker-gpu-fix-20260815/README.md
related_patterns:
  - wsl2-docker-selection-decision
  - wsl-docker-command-safety
  - wsl-docker-storage-cleanup-five-step-method
  - build-failure-layered-triage
tags: [wsl2, docker, nvidia, gpu, troubleshooting, infrastructure, layered-diagnosis]
category: infrastructure/troubleshooting
time_estimate: "~25分钟（5分钟诊断+15分钟安装+5分钟验证）"
---

# WSL Docker GPU三层诊断修复模式

## 前置条件

执行本模式前需确认：
- WSL2已安装（WSL1不支持GPU直通）
- WSL内Docker Engine已安装（非Docker Desktop）
- Windows侧NVIDIA驱动版本 ≥ 470.x（支持WSL2 GPU直通）
- 当前架构为amd64/x86_64（arm64未验证）

## 触发场景

**适用于**：
- WSL2环境中执行`docker run --gpus all`报错`could not select device driver "" with capabilities: [[gpu]]`
- WSL中nvidia-smi正常但容器无法访问GPU
- 新WSL发行版初始化Docker GPU支持
- 重建/重置WSL后恢复Docker GPU能力

**不适用于**：
- 原生Linux（非WSL）有systemd环境（直接用systemctl管理Docker）
- Docker Desktop for Windows（WSL2集成模式不同，由Docker Desktop自动管理GPU）
- 宿主机nvidia-smi本身不工作（需先修复Windows侧NVIDIA驱动）
- WSL1环境（WSL1不支持GPU直通和Docker Engine）
- arm64架构（本模式仅在amd64验证）

## 回滚说明

所有修改均可回滚：
1. `sudo apt remove -y nvidia-container-toolkit` 卸载工具包
2. 还原 `/etc/docker/daemon.json`（删除runtimes.nvidia段）
3. 还原 `/etc/wsl.conf`（从备份恢复）
4. 删除 `/etc/apt/sources.list.d/nvidia-container-toolkit.list`
5. `wsl --shutdown` 重启WSL

## 诊断三层模型

Docker GPU支持依赖三层架构，逐层验证5分钟定位问题（与[build-failure-layered-triage.md](build-failure-layered-triage.md)分层思路一致）：

```
┌─────────────────────────────────────────────┐
│  L3 运行时层 (Runtime)                        │
│  docker info | grep Runtimes → 需含 nvidia   │
├─────────────────────────────────────────────┤
│  L2 工具层 (Toolkit)                          │
│  nvidia-container-toolkit + nvidia-ctk        │
│  dpkg -l | grep nvidia-container-toolkit     │
├─────────────────────────────────────────────┤
│  L1 驱动层 (Driver)                           │
│  nvidia-smi → 需正常输出GPU信息               │
└─────────────────────────────────────────────┘
```

**关键认知**：L1（nvidia-smi正常）≠ L3（Docker可用GPU），WSL自动透传GPU只到L1层，L2/L3需要手动配置。

## 核心做法（8步）

### 步骤1：三层快速诊断（5分钟）

```bash
# L1: 驱动层
nvidia-smi
# 失败 → 修复Windows驱动/WSL GPU透传，不要继续后续步骤

# L2: 工具层
dpkg -l | grep nvidia-container-toolkit
which nvidia-container-runtime
# 缺失 → 执行步骤2-4

# L3: 运行时层
docker info 2>&1 | grep -A5 Runtimes
# 无nvidia → 执行步骤5-6
```

### 步骤2：添加NVIDIA GPG Key

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
```

国内环境优先中科大镜像（见步骤3）。

### 步骤3：配置apt源

```bash
# 官方源
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 国内推荐：中科大镜像（替换上述URL）
# deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://mirrors.ustc.edu.cn/libnvidia-container/stable/deb/amd64 /
```

**关键检查**：执行完后必须验证文件内容（`$(ARCH)`变量展开问题）：
```bash
cat /etc/apt/sources.list.d/nvidia-container-toolkit.list
# 确认 $(ARCH) 已被替换为 amd64，不能有未展开的变量
```

> **为什么要检查**：NVIDIA官方list文件中的`$(ARCH)`在curl+sed+tee管道中，只有交互式shell会展开变量；脚本写入或某些shell环境下`$(ARCH)`会原样保留，导致apt找不到包。

如存在 `$(ARCH)` 字面量，手动替换：
```bash
sudo sed -i 's/\$(ARCH)/amd64/g' /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

### 步骤4：安装nvidia-container-toolkit

```bash
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
```

验证安装：
```bash
nvidia-container-runtime --version
nvidia-ctk --version
```

> **版本选择**：使用stable分支即可，experimental分支可能有兼容性问题。

### 步骤5：配置Docker runtime

```bash
sudo nvidia-ctk runtime configure --runtime=docker
```

**重要**：此命令会**合并**配置而非覆盖——如果你的daemon.json已有其他runtimes（如crun、runsc、youki），nvidia配置会追加进去，不会删除已有配置。但仍建议先备份：

```bash
# 备份现有配置
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak.$(date +%Y%m%d%H%M%S)
```

验证daemon.json：
```bash
cat /etc/docker/daemon.json
# 应包含 runtimes.nvidia 配置项，且整体为合法JSON
python3 -m json.tool /etc/docker/daemon.json > /dev/null && echo "JSON valid"
```

### 步骤6：启动/重启Docker守护进程

**关键判断**：先确认是否运行在systemd环境：
```bash
ps -p 1 -o comm=
# 输出 systemd → 用systemctl
# 输出 init → WSL无systemd模式，用setsid
```

> **setsid vs nohup**：`nohup`只忽略SIGHUP，但WSL会话结束时除了SIGHUP还会发送其他信号；`setsid`将进程放入新的会话组，完全脱离控制终端，是WSL无systemd环境下后台进程持久化的正确方式。

**systemd环境**：
```bash
sudo systemctl restart docker
```

**WSL无systemd环境**：
```bash
# 先启动containerd（如果未运行）
if ! pgrep -x containerd >/dev/null; then
  sudo setsid containerd > /var/log/containerd.log 2>&1 < /dev/null &
  sleep 2
fi

# 启动dockerd
sudo setsid dockerd > /var/log/dockerd.log 2>&1 < /dev/null &

# 等待就绪（最多20秒）
for i in $(seq 1 20); do
  docker info >/dev/null 2>&1 && echo "Docker is ready!" && break
  sleep 1
done
```

### 步骤7：配置WSL持久化（防止重启丢失）

先备份现有wsl.conf：
```bash
sudo cp /etc/wsl.conf /etc/wsl.conf.bak.$(date +%Y%m%d%H%M%S)
```

编辑 `/etc/wsl.conf`，添加 `[boot]` 段：

```ini
[network]
generateResolvConf = false

[boot]
command="nohup containerd > /var/log/containerd-boot.log 2>&1 & sleep 2; nohup dockerd > /var/log/dockerd-boot.log 2>&1"

[automount]
enabled = true
options = "metadata,umask=0022,fmask=0011"
mountFsTab = true
```

> **关于wsl --shutdown**：此命令会关闭所有WSL发行版中运行的进程，请确保没有未保存的工作后再执行。这是唯一使wsl.conf [boot]配置生效的方式，无法在不重启WSL的情况下应用。

**使配置生效**（在Windows PowerShell中执行，不需要管理员权限）：
```powershell
wsl --shutdown
# 然后重新打开WSL终端，Docker将自动启动
```

重启后验证自启：
```bash
# 重新打开WSL后立即执行，应无需手动启动即可成功
docker info 2>&1 | grep Runtimes
```

### 步骤8：端到端验证

```bash
# 方法1：使用基础ubuntu镜像（无需下载大镜像，验证nvidia-smi）
docker run --rm --gpus all ubuntu:22.04 nvidia-smi

# 方法2：如果已有CUDA/PyTorch镜像，验证框架可用性
docker run --rm --gpus all <your-cuda-image> python -c "import torch; print(torch.cuda.is_available())"
```

成功标志：容器内nvidia-smi正常输出GPU信息，PyTorch中`torch.cuda.is_available()`返回True。

## 反模式（5个，来自实际教训）

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 看到nvidia-smi正常就以为Docker GPU可用 | 浪费时间在容器内排查CUDA/PyTorch问题，实际是宿主机缺toolkit | 必须三层逐层验证，nvidia-smi正常只代表L1通过 |
| 2 | 在WSL无systemd环境用systemctl/service重启Docker | 命令无报错但Docker实际未重启，配置不生效 | 先执行 `ps -p 1 -o comm=` 判断init系统；无systemd时用setsid |
| 3 | 直接tee NVIDIA官方list文件不检查$(ARCH)展开 | apt update无法索引包，报"Unable to locate package" | tee之后立即cat检查，将$(ARCH)替换为`$(dpkg --print-architecture)`或直接写amd64 |
| 4 | 用nohup而非setsid启动dockerd | WSL会话结束（关闭终端/wsl命令退出）时进程被杀死 | WSL无systemd环境必须用setsid完全脱离会话，不能仅靠nohup |
| 5 | 修改daemon.json后忘记配置wsl.conf持久化 | wsl --shutdown或Windows重启后Docker不自启，每次需手动启动 | 修复完成后立即配置/etc/wsl.conf [boot]段，并验证wsl --shutdown后自启 |

## 检验标准

修复完成后，以下检查项必须全部通过：

- [ ] L1：`nvidia-smi` 正常输出GPU信息
- [ ] L2：`which nvidia-container-runtime` 返回有效路径，`dpkg -l`显示nvidia-container-toolkit已安装
- [ ] L3：`docker info 2>&1 | grep Runtimes` 输出包含 `nvidia`
- [ ] 端到端：`docker run --rm --gpus all ubuntu:22.04 nvidia-smi` 在容器内正常显示GPU
- [ ] 持久化：`/etc/wsl.conf` 包含 `[boot]` 段，且有containerd+dockerd启动命令
- [ ] `/etc/apt/sources.list.d/nvidia-container-toolkit.list` 中无 `$(ARCH)` 字面量
- [ ] `/etc/docker/daemon.json` 为合法JSON（可用 `python3 -m json.tool` 验证）
- [ ] 重启验证：`wsl --shutdown`后重新进入WSL，`docker info`无需手动启动即可执行

## 故障排查速查表

| 错误信息 | 可能原因 | 排查步骤 |
|---------|---------|---------|
| `could not select device driver "" with capabilities: [[gpu]]` | L2或L3缺失 | 检查nvidia-container-toolkit是否安装、daemon.json是否有nvidia runtime、Docker是否重启加载配置 |
| `nvidia-container-cli: initialization error: nvml error: driver not loaded` | L1问题，WSL内看不到驱动 | 在WSL外（Windows）确认NVIDIA驱动正常；wsl --shutdown后重试；检查Windows版本是否支持WSL2 GPU |
| `docker: Error response from daemon: failed to create shim task: OCI runtime create failed: ... nvidia-container-runtime: not found` | nvidia-container-runtime不在PATH中 | 执行`which nvidia-container-runtime`确认；重新安装nvidia-container-toolkit；检查daemon.json中path配置 |
| apt install报"Unable to locate package nvidia-container-toolkit" | apt源配置错误 | 检查源URL是否可访问、$(ARCH)是否展开、apt update是否成功、是否使用了正确的发行版codename |
| wsl重启后Docker不自动启动 | wsl.conf [boot]配置问题 | 检查wsl.conf语法（boot段无引号错误）；检查/var/log/dockerd-boot.log；确认已wsl --shutdown使配置生效 |

## 跨场景迁移示例

### 迁移1：WSL2 Podman GPU支持（同领域）

Podman不使用Docker daemon架构，GPU支持通过CDI（Container Device Interface）实现：

1. L1驱动层验证与Docker完全相同：`nvidia-smi`
2. L2工具层：同样安装nvidia-container-toolkit（提供nvidia-ctk）
3. L3运行时层配置不同：
   ```bash
   # 启用CDI并生成规范文件
   sudo nvidia-ctk config --set cdi.enabled=true --in-place
   sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
   # Podman原生支持CDI，无需额外runtime配置
   ```
4. 验证方式：
   ```bash
   podman run --rm --device nvidia.com/gpu=all ubuntu:22.04 nvidia-smi
   ```
5. wsl.conf持久化逻辑类似，只需将dockerd替换为podman system service（如需要API服务）

### 迁移2：WSL2 启用systemd模式（同领域）

如果选择在 `/etc/wsl.conf` 中设置 `systemd=true` （WSL2 0.67.6+支持）：

```ini
[boot]
systemd=true
```

启用后Docker管理方式与原生Ubuntu完全一致，不再需要setsid：
```bash
sudo systemctl enable docker
sudo systemctl enable containerd
sudo systemctl restart docker
```

此时步骤6和步骤7的启动逻辑可替换为标准systemctl命令。

### 迁移3：通用分层诊断模型（跨领域，非容器）

本模式的核心——"三层依赖逐层诊断"模型可迁移到任意多层依赖系统排障：

**迁移场景：网络故障排查**
- L1物理层：网线/WiFi是否连接、网卡灯是否亮（类似nvidia-smi）
- L2协议层：IP地址是否分配、DNS是否可解析（类似nvidia-container-toolkit）
- L3应用层：浏览器能否打开网页、端口是否可通（类似docker run --gpus）
- 反模式同样适用："能ping通网关≠能上网"（类似"nvidia-smi正常≠Docker可用GPU"）

**迁移场景：应用服务启动失败**
- L1运行时层：语言运行时（Node/Python/Java）是否安装正确
- L2依赖层：npm/pip/maven依赖是否完整安装
- L3配置层：配置文件是否正确、端口是否被占用
- 核心原则：不要在高层排查问题前跳过底层验证。

## 参考资料

- [NVIDIA Container Toolkit官方安装文档](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [中科大镜像帮助](https://mirrors.ustc.edu.cn/help/libnvidia-container.html)
- [Microsoft WSL GPU加速文档](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute)
- 本模式来源复盘：[retrospective-wsl-docker-gpu-fix-20260815](../../reports/environment-setup/retrospective-wsl-docker-gpu-fix-20260815/README.md)
- 分层诊断思想参考：[build-failure-layered-triage.md](build-failure-layered-triage.md)
