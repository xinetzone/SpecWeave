# Caffe-FFI Jupyter Docker 开发环境

基于 [jupyter-ssh-base](../jupyter-ssh-base/) 的 Caffe-FFI 开发环境 Docker 镜像，提供 SSH + Jupyter Notebook 双服务访问，预装 Miniconda3 + Python 3.14 + caffe-ffi。

## 功能特性

- **SSH + Jupyter 双服务**：通过 supervisord 管理，支持 SSH 登录和 Jupyter Notebook/Lab 访问
- **Miniconda3 + Python 3.14**：独立 conda 环境 `caffe-ffi`，路径 `/opt/conda/envs/caffe-ffi/`
- **Caffe-FFI 预安装**：基于 projects/xuanspace/libs/caffe-ffi/ 源码编译安装，支持 C++ FFI 绑定
- **Jupyter 内核**：注册 `Python 3.14 (caffe-ffi)` 内核
- **中文环境**：zh_CN.UTF-8 编码，Asia/Shanghai 时区
- **非root用户**：jupyteruser（UID 1000），默认密码认证
- **国内镜像源支持**：一键 `--cn` 参数使用阿里云/清华镜像源
- **继承基础镜像**：复用 jupyter-ssh-base 的 SSH/Jupyter/supervisord/健康检查配置

## 前置条件

- Docker（支持 BuildKit）
- **WSL2/Linux**（必须在 WSL2 或 Linux 环境中构建，不支持 Windows 原生 Docker Desktop 直接构建）
- 已构建 jupyter-ssh-base:1.1 基础镜像

## 快速开始

### 1. 构建基础镜像（首次使用）

```bash
cd ../jupyter-ssh-base
bash scripts/build.sh
# 国内网络环境使用：
# bash scripts/build.sh --cn
```

### 2. 构建 caffe-ffi-jupyter 镜像

```bash
cd ../caffe-ffi-jupyter

# 默认构建（官方源）
bash scripts/build.sh

# 国内网络环境（推荐）
bash scripts/build.sh --cn

# 自定义标签
bash scripts/build.sh --tag my-caffe-ffi:0.1.0

# 无缓存构建（调试用）
bash scripts/build.sh --no-cache

# 构建并自动验证
bash scripts/build.sh --cn --verify
```

### 3. 运行容器

**方式一：docker run**

```bash
docker run -d \
  -p 2222:22 \
  -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v $(pwd)/workspace:/workspace \
  --name caffe-ffi \
  caffe-ffi-jupyter:latest
```

**方式二：docker compose**

```bash
# 国内镜像源
APT_MIRROR=aliyun PIP_MIRROR=aliyun CONDA_MIRROR=tuna docker compose up -d

# 默认配置
docker compose up -d
```

### 4. 连接使用

**SSH 连接**：

```bash
ssh -p 2222 jupyteruser@localhost
# 密码：changeme（或通过 USER_PASSWORD 环境变量设置）
```

SSH 登录后自动激活 caffe-ffi conda 环境。

**Jupyter Notebook**：

浏览器访问：`http://localhost:8888/?token=mysecret`

在 Kernel 菜单中选择 `Python 3.14 (caffe-ffi)` 内核。

### 5. 验证安装

```bash
# 在容器内验证
docker exec caffe-ffi bash -lc \
  "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && \
   python -c 'import caffe_ffi; print(caffe_ffi.__version__)'"

# SSH 会话中验证
ssh -p 2222 jupyteruser@localhost "python -c 'import caffe_ffi; import numpy; print(\"OK\")'"
```

## 开发模式（Volume 挂载源码）

挂载本地 caffe-ffi 源码目录进行开发：

```bash
docker run -d \
  -p 2222:22 \
  -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v $(pwd)/workspace:/workspace \
  -v /path/to/SpecWeave/projects/xuanspace/libs/caffe-ffi:/home/jupyteruser/caffe-ffi-dev \
  -w /home/jupyteruser/caffe-ffi-dev \
  --name caffe-ffi-dev \
  caffe-ffi-jupyter:latest
```

进入容器后在开发目录重新安装（editable 模式）：

```bash
ssh -p 2222 jupyteruser@localhost
cd ~/caffe-ffi-dev
pip install -e . --no-build-isolation -v
```

## 构建参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--tag TAG` | 镜像标签 | latest |
| `--name NAME` | 镜像名 | caffe-ffi-jupyter |
| `--base-image IMG` | 基础镜像 | jupyter-ssh-base:1.1 |
| `--python-version VER` | Python 版本 | 3.14 |
| `--cn` | 使用国内镜像源 | - |
| `--apt-mirror M` | APT 源 (official/aliyun/tuna) | official |
| `--pip-mirror M` | PyPI 源 (official/aliyun/tuna) | official |
| `--conda-mirror M` | Conda 源 (official/tuna) | official |
| `--no-cache` | 禁用构建缓存 | - |
| `--verify` | 构建后验证 | - |

## 环境变量

容器运行时支持以下环境变量（继承自 jupyter-ssh-base）：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `USER_PASSWORD` | jupyteruser SSH 密码 | 随机生成 |
| `JUPYTER_TOKEN` | Jupyter Notebook token | 随机生成 |
| `JUPYTER_PASSWORD` | Jupyter 密码（替代 token） | - |
| `GRANT_SUDO` | 是否启用 sudo 免密 (yes/no) | no |
| `ALLOW_ROOT_SSH` | 是否允许 root SSH (yes/no) | no |
| `JUPYTER_ALLOW_ORIGIN` | CORS 允许源 | 空（同源限制） |

## 镜像架构

```
caffe-ffi-jupyter:latest
  └── jupyter-ssh-base:1.1
        ├── OpenSSH Server (port 22)
        ├── Jupyter Notebook/Lab (port 8888, /opt/venv)
        ├── supervisord (进程管理)
        ├── tini (init)
        ├── jupyteruser (UID 1000, 中文环境)
        └── Miniconda3 (/opt/conda)
             └── caffe-ffi conda env (/opt/conda/envs/caffe-ffi/)
                  ├── Python 3.14
                  ├── numpy >= 2.3
                  ├── protobuf >= 7
                  ├── apache-tvm-ffi
                  ├── scikit-build-core + cmake + ninja
                  ├── ipykernel (Python 3.14 caffe-ffi kernel)
                  └── caffe-ffi (源码编译安装)
```

## 目录结构

```
caffe-ffi-jupyter/
├── AGENTS.md                 # AI 智能体路由入口
├── Dockerfile                # 镜像构建定义（双阶段构建）
├── Dockerfile.dockerignore   # BuildKit 构建上下文过滤
├── docker-compose.yml        # Compose 编排示例
├── README.md                 # 本文档
└── scripts/
    └── build.sh              # 一键构建脚本
```

## 测试验证步骤

```bash
# 1. 构建镜像
bash scripts/build.sh --cn --verify

# 2. 启动容器
docker run -d -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=test123 -e JUPYTER_TOKEN=test123 \
  --name caffe-test caffe-ffi-jupyter:latest

# 3. 等待服务启动
sleep 15

# 4. 检查服务状态
docker exec caffe-test supervisorctl status

# 5. SSH 连接测试
sshpass -p test123 ssh -o StrictHostKeyChecking=no -p 2222 jupyteruser@localhost \
  "python -c 'import caffe_ffi; import numpy; print(\"SSH OK\")'"

# 6. Jupyter API 测试
curl -sf http://localhost:8888/api?token=test123 && echo "Jupyter OK"

# 7. 清理
docker rm -f caffe-test
```

## 常见问题

**Q: 构建时提示 jupyter-ssh-base:1.1 未找到？**
A: 先构建基础镜像：`cd ../jupyter-ssh-base && bash scripts/build.sh`

**Q: caffe-ffi 编译失败？**
A: 确保 projects/xuanspace/libs/caffe-ffi/ 子模块已初始化：
```bash
cd ../../.. && git submodule update --init projects/xuanspace
```

**Q: 国内网络构建慢或超时？**
A: 使用 `--cn` 参数启用阿里云/清华镜像源。

**Q: 如何进入调试模式？**
A: 不启动服务直接进入 shell：`docker run -it --rm caffe-ffi-jupyter:latest bash`
