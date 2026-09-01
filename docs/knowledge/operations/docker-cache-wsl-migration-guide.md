---
type: Guide

id: "docker-cache-wsl-migration-guide"
title: "Docker镜像缓存→WSL2发行版迁移操作指南"
x-toml-ref: "../../../.meta/toml/docs/knowledge/operations/docker-cache-wsl-migration-guide.toml"
category: "operations"
date: "2026-08-18"
status: "reviewed"
version: "1.0"
source:
  - "../../retrospective/reports/environment-setup/retrospective-docker-cache-to-wsl-migration-20260818/README.md"
  - "../../retrospective/patterns/code-patterns/oci-image-wsl-rootfs-bridge.md"
related_patterns:
  - "oci-image-wsl-rootfs-bridge.md"
  - "wsl-distro-install-migration-guide.md"
  - "p1-06-docker-image-build-run.md"
tags: ["docker-cache", "wsl2", "podman", "wsl-import", "rootfs", "image-migration", "offline-environment"]
validation:
  image: "devcontainer-base:latest (Ubuntu 26.04 + Python 3.14t + conda, 26层/1.41GB)"
  date: "2026-08-18"
  result: "两套方案均验证通过，Podman方案文件系统精确，Python方案功能可用"
---
# Docker镜像缓存→WSL2发行版迁移操作指南

## 概述

本指南描述如何将 `docker save` 格式的镜像缓存（tar.gz）转换为可通过 `wsl -d <distro>` 直接启动的WSL2发行版，覆盖**完整生命周期**：保存镜像 → 选择转换方案 → 导入WSL → 配置默认用户 → 验证环境。

核心原理：`docker save` 输出的是OCI分层镜像格式（含whiteout删除标记、多层叠加），而 `wsl --import` 需要flat rootfs格式。两者之间必须经过格式转换。

### 方案选择决策树

```
你现在有WSL Linux发行版可用吗？（wsl -l -v 能列出非Stopped状态的发行版）
├─ 有（推荐方案A：Podman运行时桥接）
│   └─ 精确转换，文件系统100%还原，无残留文件，约5分钟
│
└─ 没有/不想安装额外WSL（方案B：纯Python离线转换）
    └─ 零依赖纯Windows运行，无需Linux环境，约5分20秒
    └─ ⚠️ whiteout处理不完整，多~15%冗余文件（不影响功能）
```

**方案对比表**：

| 维度 | 方案A：Podman桥接（推荐） | 方案B：Python脚本（备用） |
|------|:---:|:---:|
| 前置依赖 | WSL Linux + podman | Python 3（Windows自带或conda） |
| 文件精确度 | ✅ 100%精确还原 | ⚠️ 多~15%冗余文件（65MB+/1.4GB镜像） |
| 转换耗时（1.4GB镜像） | ~5分钟 | 5分20秒 |
| 输出大小（压缩） | 452 MB | 423 MB |
| VHDX大小 | 1.43 GB | 1.51 GB |
| 适用场景 | 有可用WSL时首选 | WSL完全重置后的Bootstrap、无网络环境 |
| 验证状态 | ✅ 稳定 | ✅ 功能可用，已知whiteout缺陷 |

---

## 前置准备

### 目录约定

本指南使用以下路径（可根据实际情况调整）：

```powershell
# 以下命令均以仓库根目录为当前工作目录（CWD）
# Docker镜像缓存目录
$cacheDir = ".docker-cache"
# WSL发行版安装目录（推荐非系统盘）
$wslDir = "D:\WSL"
# Python脚本位置（方案B）
$pyScript = ".agents\scripts\docker-save-to-wsl-rootfs.py"
```

### 前置检查

```powershell
# 1. 确认docker-cache中已有镜像tar.gz
Get-ChildItem "$cacheDir\images\*.tar.gz"
# 应看到 devcontainer-base_latest.tar.gz 等文件

# 2. 确认目标WSL目录有足够空间（VHDX≈镜像虚拟大小，通常1.5-2x压缩大小）
Get-PSDrive D | Select-Object Free

# 3. 确认WSL2可用
wsl --version
```

### 第一步：保存镜像到缓存（如果还没有tar.gz）

如果镜像还在本地Docker/Podman中，先保存：

```powershell
# Docker Desktop
docker save <image-name>:<tag> -o "$cacheDir\images\<image-name>_<tag>.tar.gz"

# 或使用docker-cache-cmd Skill（带校验、锁文件、压缩等功能）
```

---

## 方案A：Podman运行时桥接转换（推荐）

### A1. 确认转换工作区

你需要一个可用的WSL Linux发行版（可以是临时安装的Ubuntu）：

```powershell
# 列出已有发行版
wsl -l -v

# 如果没有任何发行版，安装一个临时Ubuntu
wsl --install -d Ubuntu
# ⚠️ 安装后重启终端，首次启动Ubuntu会要求设置Linux用户名和密码
#    记住这个密码——后续sudo需要用到
```

### A2. 在WSL中安装Podman

```bash
# 进入Ubuntu WSL（首次进入会要求设置用户名密码）
wsl -d Ubuntu

# 安装podman（Ubuntu 24.04+官方源自带）
sudo apt-get update && sudo apt-get install -y podman

# 配置rootful模式（推荐——避免rootless模式下uid映射导致文件权限问题）
sudo systemctl enable --now podman.socket 2>/dev/null || true
# 如果systemctl不可用（WSL默认不启动systemd），直接用sudo podman即可

# 验证（rootful模式用sudo podman）
sudo podman info 2>&1 | head -5
```

> **💡 rootful vs rootless**：在WSL中推荐使用 `sudo podman`（rootful模式），避免rootless模式下uid/gid映射导致导出的文件所有权错乱。如果你的WSL已配置好rootless podman且工作正常，也可以使用rootless模式。

### A3. 加载镜像到Podman

> ⚠️ **路径说明**：以下命令中的 `/mnt/d/...` 路径需要替换为你自己的实际路径。
> Windows路径 `D:\spaces\SpecWeave\.docker-cache\images\xxx.tar.gz` 在WSL中对应 `/mnt/d/spaces/SpecWeave/.docker-cache/images/xxx.tar.gz`（盘符小写，反斜杠改正斜杠）。

```bash
# 设置变量（替换为你的实际路径）
IMAGE_TAR="/mnt/d/spaces/SpecWeave/.docker-cache/images/devcontainer-base_latest.tar.gz"
ROOTFS_OUT="/mnt/d/spaces/SpecWeave/.docker-cache/devcontainer-base-rootfs.tar.gz"
IMAGE_NAME="devcontainer-base:latest"

# 加载镜像到podman
sudo podman load -i "$IMAGE_TAR"

# 确认镜像加载成功
sudo podman images
# 正常输出示例：
# REPOSITORY          TAG         IMAGE ID      CREATED       SIZE
# devcontainer-base   latest      6580bb1f...   3 days ago    1.41 GB
#
# 如果REPOSITORY/TAG显示为<none>/<none>，用IMAGE ID替代：
# IMAGE_ID=$(sudo podman images -q | head -1)
```

**处理镜像名为\<none\>的情况**：
```bash
# 如果podman load后镜像名显示<none>，手动tag
sudo podman tag <IMAGE-ID> devcontainer-base:latest
```

### A4. 创建容器并导出flat rootfs

```bash
# 创建容器（不启动，仅注册元数据）
sudo podman create --name wsl-export "$IMAGE_NAME"

# 导出rootfs并压缩（gzip -1快速压缩，rootfs只被读取一次）
sudo podman export wsl-export | gzip -1 > "$ROOTFS_OUT"

# 清理临时容器
sudo podman rm wsl-export

# 验证rootfs大小（应接近镜像虚拟大小的30-40%压缩比）
ls -lh "$ROOTFS_OUT"
```

> ⚠️ **VOLUME数据警告**：`podman export` 导出的是容器的rootfs，**不包含Dockerfile中VOLUME声明的挂载点内容**。
> 如果镜像包含 `VOLUME /var/lib/mysql` 等数据目录声明，export时这些目录是空的。
> 开发环境镜像通常不依赖VOLUME存放核心工具链（Python/Node/GCC等），但数据库镜像需额外处理数据目录。

### A5. 导入WSL发行版

回到PowerShell：

```powershell
$distro = "devcontainer-base"
$rootfs = "$cacheDir\devcontainer-base-rootfs.tar.gz"
$install = "$wslDir\$distro"

# 创建安装目录
New-Item -ItemType Directory -Path $install -Force | Out-Null

# 导入WSL2
wsl --import $distro $install $rootfs --version 2
```

⏭️ **跳到「导入后配置」章节继续**

---

## 方案B：纯Python离线转换（备用）

### 适用场景

- WSL完全重置后没有任何Linux发行版可用
- 不想/不能安装额外WSL发行版
- 离线环境无法apt安装podman
- 作为Bootstrap：先用Python转出一个基础WSL，再在此WSL中安装podman做精确转换

### B1. 准备Python环境

```powershell
# 确认Python可用
python --version
# 需要Python 3.10+（使用了tarfile filter参数）
```

### B2. 运行转换脚本

```powershell
$input = "$cacheDir\images\devcontainer-base_latest.tar.gz"
$output = "$cacheDir\devcontainer-base-python-rootfs.tar.gz"

# 创建输出目录（脚本不自动创建父目录）
New-Item -ItemType Directory -Path (Split-Path $output) -Force | Out-Null

# 运行转换（带计时）
Measure-Command { python $pyScript $input $output --compress --verbose }
```

**脚本参数说明**：

| 参数 | 说明 |
|------|------|
| `input.tar.gz` | docker save格式的镜像tar.gz |
| `output.tar` | 输出rootfs tar路径（加--compress则输出.tar.gz） |
| `--compress` | 输出gzip压缩格式 |
| `--verbose` | 显示详细进度 |

**预期输出**：
```
=== OCI → WSL rootfs 转换器 ===
输入镜像: devcontainer-base_latest.tar.gz
输出文件: devcontainer-base-python-rootfs.tar.gz
压缩输出: 是
输出大小: ~423 MB
耗时: ~5分20秒
```

### B3. 导入WSL发行版

```powershell
$distro = "devcontainer-base"
$rootfs = "$cacheDir\devcontainer-base-python-rootfs.tar.gz"
$install = "$wslDir\$distro"

New-Item -ItemType Directory -Path $install -Force | Out-Null
wsl --import $distro $install $rootfs --version 2
```

### B4.（可选）二次精确化

由于Python方案有whiteout残留文件，如需精确文件系统，可在Python方案产出的WSL中安装podman，再用方案A对原始镜像做一次精确转换：

```bash
# 进入Python方案生成的WSL
wsl -d devcontainer-base
sudo apt-get update && sudo apt-get install -y podman
podman load -i /mnt/d/.../devcontainer-base_latest.tar.gz
# ... 重复方案A的A3-A5步骤，生成精确rootfs
```

⏭️ **跳到「导入后配置」章节继续**

---

## 导入后配置

### 步骤1：确认镜像中的默认用户

镜像中的默认用户名不固定（不一定是root，也不一定是devuser），需要先探测：

```bash
# 方法1：查看镜像中UID=1000的用户（通常是开发用户）
wsl -d <distro-name> -u root -- sh -c 'awk -F: "\$3==1000 {print \$1}" /etc/passwd'

# 方法2：列出所有普通用户（UID≥1000）
wsl -d <distro-name> -u root -- sh -c 'awk -F: "\$3>=1000 && \$3<65534 {print \$1, \$3}" /etc/passwd'
```

将探测到的用户名记为 `<username>`（本案例中为 `devuser`）。

### 步骤2：配置wsl.conf

```powershell
$distro = "devcontainer-base"
$username = "devuser"   # 替换为步骤1探测到的用户名

# 配置默认用户和启动选项
# systemd=false 适用于无systemd的镜像（如大多数Docker基础镜像）
# 如果镜像内置systemd（如官方Ubuntu镜像），改为 systemd=true
wsl -d $distro -u root -- sh -c "printf '[user]\ndefault=$username\n[boot]\nsystemd=false\n' > /etc/wsl.conf"

# 验证写入正确
wsl -d $distro -u root -- cat /etc/wsl.conf
```

> **Alpine注意**：Alpine镜像无bash，所有 `wsl -d` 命令用 `sh` 替代 `bash`；systemd在Alpine上也不可用。
>
> **systemd说明**：Docker基础镜像通常不含systemd（容器里不需要），用 `systemd=false`。如果转换的是完整操作系统镜像（如从ISO/rootfs构建的镜像），可能需要 `systemd=true`。设置错误通常表现为启动后服务不工作，但不影响基本shell访问。

### 步骤3：配置非交互shell环境（可选，按需）

如果镜像中有conda等需要shell初始化的工具，确保非交互模式（`wsl -d distro -- command`）也能激活：

```powershell
# Conda全局激活（以/opt/conda为例，根据实际安装路径调整）
# 先确认conda路径
wsl -d $distro -u root -- sh -c "ls /opt/conda/etc/profile.d/conda.sh 2>/dev/null || ls /root/miniconda3/etc/profile.d/conda.sh 2>/dev/null || echo 'conda not found at common paths'"

# 写入全局激活脚本
wsl -d $distro -u root -- sh -c 'echo ". /opt/conda/etc/profile.d/conda.sh && conda activate base" > /etc/profile.d/conda.sh'
```

> **为什么需要这一步？** `wsl -d distro -- command` 是非交互非login shell，不加载 `~/.bashrc`，conda/PATH等初始化不会自动生效。`/etc/profile.d/*.sh` 会被所有login shell加载，配合 `sh -l -c`/`bash -l -c` 即可生效。

### 步骤4：重启发行版使配置生效

```powershell
# 温和重启（终止特定发行版）
wsl --terminate $distro

# 如果配置未生效（如默认用户仍为root），使用强制重启
wsl --shutdown

# 验证默认用户已切换
wsl -d $distro -- sh -l -c "whoami"
# 应输出你设置的用户名（如devuser），而非root
```

---

## 验证清单

### Smoke Test（必做，30秒）

```powershell
$distro = "devcontainer-base"

# 1. 发行版可启动
wsl -d $distro -- sh -l -c "echo OK"
# 期望输出: OK

# 2. 默认用户正确（非root）
wsl -d $distro -- sh -l -c "whoami"
# 期望输出: devuser（而非root）

# 3. 文件系统可写
wsl -d $distro -- sh -l -c "touch /tmp/test && rm /tmp/test && echo WRITABLE"
# 期望输出: WRITABLE

# 4. Windows盘挂载正常
wsl -d $distro -- sh -l -c "ls /mnt/d/ > /dev/null && echo D-MOUNT-OK"
# 期望输出: D-MOUNT-OK

# 5. 核心工具可用（按需替换为镜像中的核心工具）
wsl -d $distro -- sh -l -c "python3 --version && which python3"
# 期望输出: Python 3.x.x + 路径
```

### 深度验证（可选，针对开发环境）

创建验证脚本（在WSL内执行）：

```bash
# 在WSL中创建验证脚本
cat > /tmp/verify-env.sh << 'SCRIPT'
#!/bin/bash
set -e

echo "=== 环境基本信息 ==="
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)"
echo "Kernel: $(uname -r)"
echo "User: $(whoami) (uid=$(id -u))"
echo "Shell: $SHELL"
echo ""

echo "=== 工具链版本 ==="
echo "Python: $(python3 --version 2>&1)"
echo "GCC: $(gcc --version 2>&1 | head -1 || echo 'not installed')"
echo "Git: $(git --version 2>&1 || echo 'not installed')"
echo "Conda: $(conda --version 2>&1 || echo 'not installed')"
echo ""

echo "=== Python模块导入测试 ==="
python3 -c "
import sys
print(f'Python executable: {sys.executable}')
print(f'Python prefix: {sys.prefix}')
mods = ['numpy', 'pandas', 'torch', 'onnxruntime']
for m in mods:
    try:
        __import__(m)
        print(f'  ✅ {m}')
    except ImportError:
        print(f'  ⚠️  {m} (not installed, may be expected)')
"
echo ""

echo "=== Free-Threading验证（Python 3.13t/3.14t）==="
python3 -c "
import sys
gil_enabled = getattr(sys, '_is_gil_enabled', lambda: 'N/A (not free-threading)')
print(f'GIL enabled: {gil_enabled()}')
" 2>&1 || echo "(非free-threading版本，跳过)"
echo ""

echo "=== 文件系统测试 ==="
echo "/tmp writable: $([ -w /tmp ] && echo ✅ || echo ❌)"
echo "/home writable: $([ -w /home ] && echo ✅ || echo ❌)"
echo "/mnt/d accessible: $([ -d /mnt/d ] && echo ✅ || echo ❌)"
echo ""

echo "=== 所有基本验证通过 ✅ ==="
SCRIPT

chmod +x /tmp/verify-env.sh
bash /tmp/verify-env.sh
```

### Free-Threading专项验证（Python 3.13t+ 可选）

```bash
cat > /tmp/test-freethreading.py << 'PYEOF'
import sys
import time
import threading
import multiprocessing.pool

print(f"Python version: {sys.version}")
print(f"GIL enabled: {sys._is_gil_enabled() if hasattr(sys, '_is_gil_enabled') else 'N/A'}")

def cpu_work(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

N = 5_000_000

# 单线程
start = time.time()
cpu_work(N)
single = time.time() - start

# 双线程
start = time.time()
threads = [threading.Thread(target=cpu_work, args=(N,)) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()
multi = time.time() - start

print(f"Single thread: {single:.2f}s")
print(f"Two threads:   {multi:.2f}s (ratio: {multi/single:.2f}x)")
if hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled():
    print("Free-threading active: ratio ~1.0x (true parallelism)")
else:
    print("GIL active: ratio ~1.5-2.0x (GIL bottleneck)")
PYEOF

python3 /tmp/test-freethreading.py
```

**期望输出（free-threading）**：
```
GIL enabled: False
Two threads: ~1.0x (true parallelism)
```

---

## 清理旧发行版（可选）

如需替换已存在的同名发行版：

```powershell
$distro = "devcontainer-base"

# 1. 注销发行版
wsl --unregister $distro

# 2. 删除VHDX文件（wsl --unregister不会自动删除物理文件）
Remove-Item -Recurse -Force "$wslDir\$distro" -ErrorAction SilentlyContinue

# 3. 清理可能残留的临时文件
Remove-Item "$env:LOCALAPPDATA\Packages\*$distro*" -Recurse -Force -ErrorAction SilentlyContinue
```

> ⚠️ **注意**：`wsl --unregister` 会彻底删除发行版所有数据，不可恢复。执行前确认已备份重要数据。

---

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `wsl --import` 报"系统找不到指定路径" | 安装目录不存在 | 先执行 `New-Item -ItemType Directory -Path <install-dir> -Force` |
| `wsl --import` 成功但 `wsl -d` 启动报错 | rootfs格式错误（直接用了docker save tar.gz） | 使用方案A/B转换后再导入 |
| 导入后文件中有大量 `.wh.` 开头文件 | 未经过OCI运行时转换，直接解压docker save格式 | 使用方案A或方案B重新转换 |
| Podman报 "VM does not exist" | podman machine损坏（Windows Podman Desktop常见） | 在WSL Ubuntu中安装rootful podman，不使用podman machine |
| `podman load` 报错 "unrecognized image format" | tar.gz不是有效的OCI/docker save格式 | 确认是用 `docker save` 或 `podman save` 导出的（不是手动打包的） |
| `podman load` 后镜像名显示`<none>` | 部分旧版docker save格式丢失tag信息 | `sudo podman tag <IMAGE-ID> <name>:<tag>` 手动打tag |
| WSL启动后默认是root | wsl.conf未配置或未生效 | 确认wsl.conf中 `[user]` 段default用户名正确，先试 `wsl --terminate`，不行再 `wsl --shutdown` |
| wsl.conf配置重启后仍不生效 | WSL缓存了旧配置 | 执行 `wsl --shutdown`（完全关闭WSL子系统），再重新进入 |
| `wsl -d distro -- command` 找不到conda/python | 非交互shell不加载.bashrc | 通过 `/etc/profile.d/*.sh` 配置，用 `sh -l -c`/`bash -l -c` 执行 |
| `sudo podman` 报权限错误/无法连接 | WSL中podman服务未启动或用户不在podman组 | 用 `sudo podman`（rootful）或执行 `sudo systemctl start podman` |
| 导出的rootfs中文件权限异常（全是某个uid） | rootless podman的uid映射 | 使用 `sudo podman`（rootful模式）避免uid映射问题 |
| Python脚本报 `'TarInfo' object has no attribute 'copy'` | 使用了旧版脚本（未修复Bug） | 使用当前仓库中已修复的脚本（含 `import copy` + `copy.copy(tarinfo)`） |
| Python脚本报 `DeprecationWarning: filter` | Python 3.14+ 对tarfile提取的安全警告 | 当前脚本已添加 `filter='data'`，警告已消除 |
| Python脚本报 `FileNotFoundError` 输出目录不存在 | 脚本不自动创建父目录 | 先 `New-Item -ItemType Directory -Path (Split-Path $output) -Force` |
| VHDX占用空间过大 | WSL2自动扩容不会自动缩容 | 导出再导入：`wsl --export` → `wsl --unregister` → `wsl --import` |
| 方案B产出的WSL里有奇怪的.pyc/.ftl残留 | whiteout删除处理不完整 | 不影响功能，可忽略；如需精确文件系统改用方案A |
| `wsl -l -v` 显示发行版但无法启动 | VHDX文件被删除但注册表残留 | `wsl --unregister <distro>` 清除残留后重新导入 |

---

## 命令速查（Cheat Sheet）

```powershell
# === 一键完整流程（方案A，已有Ubuntu WSL）===
$image = "devcontainer-base:latest"
$distro = "devcontainer-base"
$cacheDir = ".docker-cache"
$wslDir = "D:\WSL"
$rootfs = "$cacheDir\devcontainer-base-rootfs.tar.gz"
# WSL 通过 /mnt/<盘符小写>/... 访问 Windows 文件：先解析缓存目录绝对路径再转换
# （-match/$matches 写法兼容 Windows PowerShell 5.1 与 PowerShell 7+）
$cacheWsl = (Resolve-Path $cacheDir).Path -replace '\\','/'
if ($cacheWsl -match '^([A-Za-z]):(.*)$') {
    $cacheWsl = "/mnt/" + $matches[1].ToLower() + $matches[2]
}
$wslRootfs = "$cacheWsl/devcontainer-base-rootfs.tar.gz"
$wslImage = "$cacheWsl/images/devcontainer-base_latest.tar.gz"

# Step A3-A4: WSL内以root身份加载+导出（避免sudo密码问题）
wsl -d Ubuntu -u root -- bash -c "podman load -i $wslImage && podman create --name wsl-export $image && podman export wsl-export | gzip -1 > $wslRootfs && podman rm wsl-export"

# Step A5: 导入
New-Item -ItemType Directory -Path "$wslDir\$distro" -Force | Out-Null
wsl --import $distro "$wslDir\$distro" $rootfs --version 2

# 配置默认用户（Alpine用户将bash改为sh）
wsl -d $distro -u root -- bash -c 'printf "[user]\ndefault=devuser\n[boot]\nsystemd=false\n" > /etc/wsl.conf'
wsl --terminate $distro

# 验证
wsl -d $distro -- bash -l -c "echo OK && whoami && python3 --version"
```

```powershell
# === 一键完整流程（方案B，纯Python无额外WSL）===
$cacheDir = ".docker-cache"
$wslDir = "D:\WSL"
$distro = "devcontainer-base"
$pyScript = ".agents\scripts\docker-save-to-wsl-rootfs.py"
$input = "$cacheDir\images\devcontainer-base_latest.tar.gz"
$output = "$cacheDir\devcontainer-base-python-rootfs.tar.gz"

# Step B2: Python转换
python $pyScript $input $output --compress

# Step B3: 导入
New-Item -ItemType Directory -Path "$wslDir\$distro" -Force | Out-Null
wsl --import $distro "$wslDir\$distro" $output --version 2

# 配置默认用户（同方案A）
wsl -d $distro -u root -- sh -c 'printf "[user]\ndefault=devuser\n[boot]\nsystemd=false\n" > /etc/wsl.conf'
wsl --terminate $distro

# 验证
wsl -d $distro -- sh -l -c "echo OK && whoami && python3 --version"
```

```powershell
# === 日常维护 ===
wsl -l -v                                    # 列出所有发行版
wsl -d <distro>                              # 进入发行版
wsl --terminate <distro>                     # 关闭发行版
wsl --unregister <distro>                    # 删除发行版（⚠️不可恢复）
wsl --shutdown                               # 关闭所有WSL
wsl --export <distro> <path>\backup.tar.gz   # 备份发行版
```
