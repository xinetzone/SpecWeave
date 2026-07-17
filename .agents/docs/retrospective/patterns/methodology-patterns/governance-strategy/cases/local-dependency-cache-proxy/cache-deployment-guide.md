---
id: "cache-deployment-guide"
title: "本地依赖缓存代理体系部署指南"
version: "1.0"
date: "2026-07-17"
source: "TVM Python 3.14 + LLVM 22 构建验证项目"
related_files:
  - "local-cache-proxy-config.md"
  - "cache_diagram.md"
---

# 本地依赖缓存代理体系部署指南

## 一、文档说明

本文档描述如何按五层架构部署本地依赖缓存代理体系，解决构建过程中网络超时、重复下载、构建速度慢等问题。

**目标读者**：开发环境运维人员、构建系统管理员
**部署时间**：单节点约 15 分钟，团队环境约 1 小时
**预期效果**：重复构建速度提升 10-100 倍，网络超时率从 >50% 降至 <1%

## 二、前置条件

| 项 | 要求 |
|---|---|
| 操作系统 | Linux (Ubuntu 20.04+/CentOS 8+) 或 Windows 10/11 + Docker Desktop |
| Docker 版本 | ≥ 20.10.0（推荐开启 BuildKit） |
| 磁盘空间 | ≥ 50GB 可用空间（缓存目录） |
| 网络 | 首次部署需访问外网，冷缓存完成后可半离线工作 |
| 权限 | sudo/root 权限（修改 Docker 配置） |

## 三、部署架构回顾

> 📊 **架构图**：参见 [cache_diagram.md](cache_diagram.md) 中的五层缓存架构图

快速部署从第一层到第五层逐层配置。生产团队环境可按需选配高级组件（Harbor/Squid/devpi/Verdaccio）。

## 四、部署步骤

### 阶段一：第一层 - Docker Registry Mirror 配置

**适用**：所有环境（必选）
**耗时**：约 3 分钟

#### 4.1.1 配置 Docker 镜像加速器

**Linux 系统**：

```bash
# 创建 Docker 配置目录
sudo mkdir -p /etc/docker

# 写入 daemon.json 配置
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub-mirror.c.163.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

# 重启 Docker 生效
sudo systemctl daemon-reload
sudo systemctl restart docker
```

**Windows (Docker Desktop)**：

1. 打开 Docker Desktop → Settings → Docker Engine
2. 在 JSON 配置中添加 `registry-mirrors` 字段（同上）
3. 点击 "Apply & Restart"

**PowerShell 命令**：
```powershell
Restart-Service docker
```

#### 4.1.2 验证配置生效

```bash
# 查看 Docker 信息，确认 Registry Mirrors 已列出
docker info | grep -A 5 "Registry Mirrors"

# 测试拉取（应明显快于未配置时）
time docker pull hello-world
```

✅ **验证标准**：`docker info` 输出中能看到配置的三个镜像加速器地址

---

### 阶段二：第二层 - Dockerfile 构建缓存优化

**适用**：所有环境（必选）
**耗时**：约 5 分钟

#### 4.2.1 启用 BuildKit（推荐）

**Linux/macOS**：
```bash
# 临时启用
export DOCKER_BUILDKIT=1

# 永久启用（写入 ~/.bashrc 或 /etc/profile）
echo 'export DOCKER_BUILDKIT=1' >> ~/.bashrc
source ~/.bashrc
```

**Windows**：
```powershell
#  PowerShell 永久设置
[Environment]::SetEnvironmentVariable("DOCKER_BUILDKIT", "1", "User")
```

#### 4.2.2 优化 Dockerfile 层顺序

按「变化频率从低到高」排列指令：

```dockerfile
# ✅ 正确顺序（参考模板）
FROM continuumio/miniconda3:latest

# 1. 配置文件（变化少）
COPY docker/condarc /opt/conda/.condarc
COPY docker/pip.conf /root/.pip/pip.conf

# 2. 系统依赖安装（变化少）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git wget && \
    rm -rf /var/lib/apt/lists/*

# 3. 语言依赖安装（变化中等）
RUN conda create -n tvm-build python=3.14 -c conda-forge && \
    conda install -n tvm-build -c conda-forge llvmdev=22 ninja cmake && \
    conda clean -a -y

# 4. 项目源代码（变化频繁）
COPY . /workspace/npu_tvm

# 5. 编译构建（变化频繁）
RUN cd /workspace/npu_tvm/build && cmake .. -G Ninja && ninja
```

#### 4.2.3 创建 .dockerignore

在项目根目录创建 `.dockerignore`：

```
# Version control
.git
.gitignore

# Python
__pycache__
*.pyc
.pytest_cache
*.egg-info

# Build artifacts
build/
dist/
*.so

# IDE
.vscode
.idea
*.swp

# OS
.DS_Store
Thumbs.db
```

#### 4.2.4 验证缓存命中

```bash
# 首次构建（慢，填充缓存）
docker build -t test-cache .

# 修改任意源代码文件后第二次构建
docker build --progress=plain -t test-cache . 2>&1 | grep CACHED
```

✅ **验证标准**：第二次构建日志中依赖层（apt/conda/pip install）显示 `CACHED`，只有 COPY 和编译步骤重新执行

---

### 阶段三：第三层 - Conda 包缓存配置

**适用**：Python/Conda 环境（必选）
**耗时**：约 2 分钟

#### 4.3.1 配置 Conda 国内镜像源

```bash
# 写入 ~/.condarc
cat > ~/.condarc << 'EOF'
channels:
  - defaults
show_channel_urls: true
channel_priority: flexible
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
remote_connect_timeout_secs: 60
remote_read_timeout_secs: 300
remote_max_retries: 10
EOF
```

#### 4.3.2 配置本地缓存目录（可选）

```yaml
# 在 ~/.condarc 中追加
pkgs_dirs:
  - ~/conda-cache
  - /opt/conda/pkgs
```

```bash
# 创建缓存目录
mkdir -p ~/conda-cache
```

#### 4.3.3 验证配置

```bash
# 查看配置
conda config --show-sources

# 测试安装（首次慢，后续快）
time conda create -n test-cache python=3.11 numpy -y
```

✅ **验证标准**：下载包时显示镜像源 URL 为 `mirrors.tuna.tsinghua.edu.cn`，二次安装提示 "All requested packages already installed" 或从本地缓存读取

---

### 阶段四：第四层 - Pip 包缓存配置

**适用**：Python 项目（必选）
**耗时**：约 2 分钟

#### 4.4.1 配置 Pip 国内镜像源

```bash
# 创建配置目录
mkdir -p ~/.pip

# 写入 pip.conf
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
```

**Windows**：配置文件位置为 `%APPDATA%\pip\pip.ini`

#### 4.4.2 验证配置

```bash
# 查看配置
pip config list

# 测试安装
time pip install numpy pandas
```

✅ **验证标准**：Looking in indexes 显示清华源地址，下载速度 > 1MB/s

---

### 阶段五：第五层 - NPM 包缓存配置（可选）

**适用**：Node.js/前端项目按需配置
**耗时**：约 1 分钟

```bash
# 配置淘宝镜像
npm config set registry https://registry.npmmirror.com/

# 验证配置
npm config get registry
```

✅ **验证标准**：输出 `https://registry.npmmirror.com/`

---

### 阶段六（可选）：团队级高级组件部署

**适用**：≥ 3 人团队或 CI/CD 环境
**耗时**：约 30 分钟

#### 4.6.1 部署 Squid HTTP 代理缓存

创建 `docker-compose.proxy.yml`：

```yaml
version: '3.8'
services:
  squid:
    image: sameersbn/squid:3.5.27-2
    container_name: squid-proxy
    restart: always
    ports:
      - "3128:3128"
    volumes:
      - ./squid/cache:/var/spool/squid
      - ./squid/squid.conf:/etc/squid/squid.conf
    environment:
      - TZ=Asia/Shanghai
```

创建 `squid/squid.conf`：
```conf
http_port 3128
cache_dir aufs /var/spool/squid 20000 16 256
maximum_object_size 1024 MB
cache_mem 256 MB

acl all src 0.0.0.0/0
http_access allow all

access_log /var/log/squid/access.log squid
cache_log /var/log/squid/cache.log
```

启动：
```bash
mkdir -p squid/cache squid
docker-compose -f docker-compose.proxy.yml up -d squid
```

配置环境变量使用代理：
```bash
export http_proxy=http://localhost:3128
export https_proxy=http://localhost:3128
```

#### 4.6.2 部署 devpi PyPI 私有缓存（可选）

在 `docker-compose.proxy.yml` 中追加：

```yaml
  devpi:
    image: scrapinghub/devpi:latest
    container_name: devpi-server
    restart: always
    ports:
      - "3141:3141"
    volumes:
      - ./devpi/data:/data
    environment:
      - DEVPI_SERVERDIR=/data
```

启动后配置 pip 使用：
```bash
pip config set global.index-url http://localhost:3141/root/pypi/+simple/
pip config set global.trusted-host localhost
```

## 五、快速部署脚本（单节点开发环境）

将以下内容保存为 `setup-cache.sh`，一键完成前五层配置：

```bash
#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "本地缓存代理体系一键部署脚本"
echo "=========================================="

# 步骤1：配置 Docker Registry Mirror
echo "[1/5] 配置 Docker Registry Mirror..."
if [ ! -f /etc/docker/daemon.json ]; then
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub-mirror.c.163.com"
  ],
  "log-driver": "json-file",
  "log-opts": {"max-size": "100m", "max-file": "3"}
}
EOF
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    echo "✅ Docker 配置完成，已重启服务"
else
    echo "ℹ️  Docker daemon.json 已存在，跳过（手动检查）"
fi

# 步骤2：启用 BuildKit
echo "[2/5] 启用 Docker BuildKit..."
if ! grep -q "DOCKER_BUILDKIT=1" ~/.bashrc; then
    echo 'export DOCKER_BUILDKIT=1' >> ~/.bashrc
    export DOCKER_BUILDKIT=1
    echo "✅ BuildKit 已启用"
else
    echo "ℹ️  BuildKit 已配置，跳过"
fi

# 步骤3：配置 Conda 镜像
echo "[3/5] 配置 Conda 清华镜像源..."
cat > ~/.condarc << 'EOF'
channels:
  - defaults
show_channel_urls: true
channel_priority: flexible
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
remote_connect_timeout_secs: 60
remote_read_timeout_secs: 300
remote_max_retries: 10
EOF
echo "✅ Conda 配置完成"

# 步骤4：配置 Pip 镜像
echo "[4/5] 配置 Pip 清华镜像源..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
echo "✅ Pip 配置完成"

# 步骤5：配置 NPM 镜像（如存在 npm）
echo "[5/5] 配置 NPM 淘宝镜像..."
if command -v npm &> /dev/null; then
    npm config set registry https://registry.npmmirror.com/
    echo "✅ NPM 配置完成"
else
    echo "ℹ️  未检测到 npm，跳过"
fi

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""
echo "验证步骤："
echo "  docker info | grep -A 3 'Registry Mirrors'"
echo "  conda info"
echo "  pip config list"
echo ""
echo "请执行 source ~/.bashrc 使环境变量生效"
```

使用方法：
```bash
chmod +x setup-cache.sh
./setup-cache.sh
source ~/.bashrc
```

## 六、验证清单

部署完成后，逐项验证：

| 检查项 | 命令 | 预期结果 |
|---|---|---|
| Docker 镜像加速器 | `docker info \| grep -A 3 "Registry Mirrors"` | 列出 3 个镜像源 |
| BuildKit 启用 | `echo $DOCKER_BUILDKIT` | 输出 `1` |
| Conda 镜像源 | `conda config --show default_channels` | 显示 tuna.tsinghua.edu.cn |
| Pip 镜像源 | `pip config get global.index-url` | 显示 tuna.tsinghua.edu.cn |
| Docker 缓存命中 | 二次构建观察日志 | 依赖层显示 `CACHED` |
| 代理端口（如部署） | `curl -I http://localhost:3128` | 返回 squid 响应头 |

## 七、日常运维

### 7.1 缓存清理

定期清理避免磁盘占满：

```bash
# 清理 Docker 无用镜像/容器/缓存（每周一次）
docker system prune -af --volumes

# 清理 Conda 缓存（每月一次）
conda clean -a -y

# 清理 Pip 缓存
pip cache purge

# 清理 Squid 缓存（如部署）
docker exec squid-proxy squid -k rotate
```

### 7.2 监控缓存命中率

```bash
# Docker 构建缓存观察
docker build --progress=plain . 2>&1 | grep -E "CACHED|RUN"

# Squid 命中率（如部署）
docker exec squid-proxy squidclient mgr:info | grep "Cache hits"
```

### 7.3 缓存预热

团队环境新机器加入时提前预热：
```bash
# 预拉取常用基础镜像
docker pull continuumio/miniconda3:latest
docker pull ubuntu:22.04

# 预安装常用 Conda 包
conda install numpy pandas cmake ninja
```

## 八、故障排查

| 问题 | 排查方向 | 解决方案 |
|---|---|---|
| Docker 拉取仍然超时 | 检查 mirror 是否可达 | `curl -I https://docker.m.daocloud.io/v2/`，不可达换备用源 |
| Conda 出现 HTTP 404 | 镜像源同步延迟 | 临时切回官方源 `conda config --remove-key default_channels` |
| 构建缓存不命中 | 检查 .dockerignore 和指令顺序 | 确认依赖安装在 COPY 源代码之前 |
| 磁盘空间不足 | 检查缓存目录大小 | `du -sh /var/lib/docker/ ~/conda-cache/`，执行清理 |
| Pip SSL 错误 | 检查 trusted-host | 确认 pip.conf 中 trusted-host 配置正确 |

## 九、相关文档

- 详细配置选项参考：[local-cache-proxy-config.md](local-cache-proxy-config.md)
- 五层架构图：[cache_diagram.md](cache_diagram.md)
- Dockerfile 优化模式：[dev-env-dockerfile-optimization.md](../../dev-env-dockerfile-optimization.md)

---

> **部署状态记录**：
> - [ ] 第一层 Docker Registry Mirror
> - [ ] 第二层 Dockerfile 构建缓存
> - [ ] 第三层 Conda 包缓存
> - [ ] 第四层 Pip 包缓存
> - [ ] 第五层 NPM 包缓存
> - [ ] 团队级 Squid/devpi（可选）
