# DevContainer Base - Conda 变体 (Miniconda3)

> 基于 devcontainer-base:latest 的 Miniconda3 变体镜像，在保留系统 venv（/opt/venv）和所有基础服务（SSH/Docker/Podman/Jupyter）的前提下，额外安装 Miniconda3 到 /opt/conda。

## ✨ 特性

- **基础镜像继承**：完全继承 devcontainer-base 的所有功能
  - Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
  - SSH(22) + Docker DinD(2375) + Podman(rootless) + Jupyter(8888)
  - supervisord 进程管理，devuser 非 root 用户 (UID 1000)
  - 系统 Python venv 位于 `/opt/venv`（Jupyter 等服务使用）
- **Miniconda3**：安装到 `/opt/conda`，默认 Python 3.14
- **PATH 设计**：不修改默认 PATH，保持 `/opt/venv/bin` 优先，避免破坏服务
- **手动激活**：conda 不自动激活 base 环境，需显式 source 激活脚本
- **国内镜像支持**：支持清华 TUNA conda 镜像、阿里云/清华 pip 镜像
- **多用户配置**：root 和 devuser 均配置好 pip 镜像源

## 📁 目录结构

```
variants/conda/
├── Dockerfile              # Conda 变体构建文件（5个追加阶段）
├── .env.example            # 构建参数配置模板
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 规范说明
```

## 🚀 构建

### 前置条件

首先需要构建基础镜像 `devcontainer-base:latest`：

```bash
# 在 devcontainer-base 根目录构建基础镜像
cd /path/to/devcontainer-base
bash scripts/build.sh --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant conda

# 使用国内镜像源构建（推荐中国网络环境）
bash variants/build.sh --variant conda --cn

# 构建后验证
bash variants/build.sh --variant conda --cn --verify
```

### 手动 docker build

```bash
# 在 devcontainer-base 根目录执行
# 标准构建
docker build -f variants/conda/Dockerfile \
  -t devcontainer-base:conda-latest .

# 国内镜像源构建
docker build -f variants/conda/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=aliyun \
  -t devcontainer-base:conda-latest .

# 指定 Python 版本
docker build -f variants/conda/Dockerfile \
  --build-arg PYTHON_VERSION=3.12 \
  -t devcontainer-base:conda-py312 .

# 指定 Miniconda 版本
docker build -f variants/conda/Dockerfile \
  --build-arg MINICONDA_VERSION=py24.9.2-0 \
  -t devcontainer-base:conda-latest .
```

## 🐳 运行

### DinD 模式（推荐开发环境）

```bash
docker run -d \
  --name devcontainer-conda \
  --privileged \
  -p 2222:22 \
  -p 2375:2375 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  devcontainer-base:conda-latest
```

### 命令模式（调试/一次性任务）

```bash
docker run -it --rm --privileged devcontainer-base:conda-latest bash
```

### DooD 模式（生产/CI 环境，无需 --privileged）

```bash
docker run -d \
  --name devcontainer-conda-dood \
  -p 2223:22 \
  -p 8889:8888 \
  -v $(pwd)/workspace:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:conda-latest
```

## 🔧 Conda 使用说明

### 重要：PATH 优先级设计

**默认情况下，`python` 和 `pip` 命令指向系统 venv（/opt/venv），而不是 conda！**
这是为了确保 Jupyter、supervisord 等服务正常运行。使用 conda 需要显式激活。

### 激活 Conda

登录容器后，执行以下命令激活 conda：

```bash
# 方法1：使用激活脚本（推荐）
source /etc/profile.d/conda-init.sh
conda activate base

# 方法2：直接使用绝对路径
/opt/conda/bin/conda --version
/opt/conda/bin/python --version
```

### 创建新环境

```bash
# 激活 conda 后
source /etc/profile.d/conda-init.sh

# 创建新环境
conda create -n myenv python=3.12

# 激活新环境
conda activate myenv

# 安装包
conda install numpy pandas
pip install requests
```

### 登录 shell 自动激活（可选）

如果希望每次登录自动激活 conda base 环境，取消注释 `~/.bashrc` 中的相关行：

```bash
# 编辑 ~/.bashrc，取消以下两行的注释：
# source /etc/profile.d/conda-init.sh
# conda activate base
```

或执行：

```bash
echo 'source /etc/profile.d/conda-init.sh' >> ~/.bashrc
echo 'conda activate base' >> ~/.bashrc
```

> ⚠️ **注意**：自动激活 conda 会改变默认 `python`/`pip` 路径，可能影响某些依赖系统 venv 的脚本。Jupyter 服务始终使用系统 venv，不受影响。

## ✅ 验证

```bash
# 验证 conda 安装
docker run --rm devcontainer-base:conda-latest /opt/conda/bin/conda --version

# 验证系统 venv 仍然存在且为默认
docker run --rm devcontainer-base:conda-latest which python
# 输出应包含: /opt/venv/bin/python

# 验证 conda 激活脚本
docker run --rm devcontainer-base:conda-latest \
  bash -c "source /etc/profile.d/conda-init.sh && conda activate base && python --version"

# 验证 Jupyter 仍然可用
docker run --rm devcontainer-base:conda-latest /opt/venv/bin/jupyter --version

# 验证 Docker 可用
docker run --rm --privileged devcontainer-base:conda-latest docker --version

# 查看构建信息
docker run --rm devcontainer-base:conda-latest cat /etc/devcontainer-variant-conda-build-info
```

## ⚙️ 构建参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | 基础镜像 devcontainer-base 的标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna（清华）/official（官方） |
| `PIP_MIRROR` | `aliyun` | PyPI 源：aliyun（阿里云）/tuna（清华）/official |
| `MINICONDA_VERSION` | `latest` | Miniconda 版本，如 `py24.9.2-0` |
| `PYTHON_VERSION` | `3.14` | Conda base 环境默认 Python 版本 |

## 📋 关键路径

| 路径 | 说明 |
|------|------|
| `/opt/conda` | Miniconda3 安装根目录 |
| `/opt/conda/bin/conda` | conda 可执行文件（绝对路径可用） |
| `/opt/venv` | 系统 Python venv（Jupyter 等服务使用） |
| `/etc/profile.d/conda-init.sh` | Conda 激活脚本 |
| `/etc/devcontainer-variant-conda-build-info` | 构建元数据 |
| `/opt/conda/.condarc` | Conda 系统级配置（镜像源） |

## ⚠️ 注意事项

1. **PATH 优先级**：默认 PATH 中 `/opt/venv/bin` 在 `/opt/conda/bin` 之前（实际上 conda/bin 不在默认 PATH 中）。这是有意设计的，确保服务稳定性。

2. **不自动激活**：`auto_activate_base` 设置为 `false`，不会在 shell 启动时自动激活 conda，避免与系统 venv 冲突。

3. **服务兼容性**：SSH、Docker、Podman、Jupyter 所有服务均继承自基础镜像，使用系统 venv 运行，不受 conda 安装影响。

4. **权限**：`/opt/conda` 为 root 所有但全局可读，devuser 可以使用 conda 命令、创建环境、安装包（环境会创建在用户目录下或使用 `conda create -p` 指定路径）。

5. **镜像源配置**：
   - Conda 镜像源配置在 `/opt/conda/.condarc`（系统级）
   - pip 镜像源同时配置了 root (`/root/.config/pip/pip.conf`) 和 devuser (`/home/devuser/.config/pip/pip.conf`)

## 🔗 相关镜像

- [devcontainer-base](../../README.md) - 基础镜像（SSH + Docker + Podman + Jupyter）
