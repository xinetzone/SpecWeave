# jupyter-podman-rootless

> 基于 Podman rootless 模式的 Jupyter 开发容器：Python 3.14t (free-threading) + Miniforge3 + SSH + rootless Podman，通过 supervisord 管理多服务。三层后端编排（podman-compose 声明式 → podman-py SDK → CLI fallback），内置 OMLMD 模型 artifact 分发、OLOT KServe ModelCar 打包、Toolbx 透传兼容。

---

## 快速开始

```bash
# 安装依赖（推荐：invoke + podman-compose）
pip install -e ".[compose]"

# 构建镜像（使用清华镜像源加速）
invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna

# 启动容器（自动生成密码和token，端口2222:22, 8888:8888）
invoke run

# 查看访问信息（启动时会打印）
# SSH:       ssh -p 2222 devuser@localhost
# Jupyter:   http://localhost:8888/lab?token=<自动生成的token>
```

详细使用指南见 [docs/](docs/README.md)。

## 文档导航

### 📚 使用文档

| 文档 | 说明 |
|------|------|
| [docs/README.md](docs/README.md) | 文档索引 |
| [docs/00-overview.md](docs/00-overview.md) | 特性一览 |
| [docs/01-getting-started.md](docs/01-getting-started.md) | 快速开始：前置条件、三种使用方式 |
| [docs/02-invoke-reference.md](docs/02-invoke-reference.md) | Invoke命令参考：核心命令、ML命令、参数说明 |
| [docs/03-environment-variables.md](docs/03-environment-variables.md) | 环境变量参考 |
| [docs/04-image-architecture.md](docs/04-image-architecture.md) | 镜像架构：7层构建、7步启动、服务管理 |
| [docs/05-rootless-podman.md](docs/05-rootless-podman.md) | Rootless Podman使用说明 |
| [docs/06-ml-model-management.md](docs/06-ml-model-management.md) | ML模型管理：OMLMD+OLOT、ModelCar打包 |
| [docs/07-toolbx-passthrough.md](docs/07-toolbx-passthrough.md) | Toolbx透传开发模式 |
| [docs/08-directory-structure.md](docs/08-directory-structure.md) | 目录结构说明 |
| [docs/09-three-tier-backend.md](docs/09-three-tier-backend.md) | 三层后端编排架构 |
| [docs/10-direct-cli-usage.md](docs/10-direct-cli-usage.md) | 直接使用Podman/Docker命令 |
| [docs/11-free-threading.md](docs/11-free-threading.md) | Python Free-Threading（无GIL）说明 |
| [docs/12-healthcheck.md](docs/12-healthcheck.md) | 健康检查机制 |
| [docs/13-faq.md](docs/13-faq.md) | 常见问题解答 |

### 🤖 AI协作者规范

项目特有的AI协作者规范已原子化拆分至 [.agents/](.agents/README.md) 目录：

| 规范 | 说明 |
|------|------|
| [.agents/README.md](.agents/README.md) | AI资产容器索引 |
| [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | Containerfile编写规范（7层架构、Toolbx兼容） |
| [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | Entrypoint启动脚本规范（7步启动流程） |
| [.agents/rules/services.md](.agents/rules/services.md) | 服务配置规范（supervisord/SSH/Jupyter/Podman） |
| [.agents/rules/compose.md](.agents/rules/compose.md) | Compose编排与透传规范 |
| [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) | Invoke任务开发规范（三层后端架构） |
| [.agents/rules/ml-models.md](.agents/rules/ml-models.md) | ML模型管理规范（OMLMD/OLOT） |
| [.agents/rules/build-test.md](.agents/rules/build-test.md) | 构建与测试规范 |

## 特性一览

| 特性 | 说明 |
|------|------|
| **基础镜像** | Ubuntu 26.04 |
| **Python** | 3.14 cp314t (free-threading，无GIL)，Miniforge3 + libmamba |
| **Jupyter** | JupyterLab ≥4.4 + Notebook ≥7.3，端口 8888 |
| **SSH** | OpenSSH Server，端口 22，支持密码/公钥认证 |
| **Podman** | Rootless 模式（fuse-overlayfs + crun），支持 DinP |
| **服务管理** | supervisord 管理 sshd + jupyter，tini 作为 PID 1 |
| **非root用户** | devuser (UID 1000)，sudo 默认关闭 |
| **中文环境** | zh_CN.UTF-8 locale + Asia/Shanghai 时区 |
| **镜像源** | APT/Conda/PIP 均支持 official / tuna / aliyun |
| **三层后端** | podman-compose（优先）→ podman-py SDK → CLI fallback |
| **ML 模型** | OMLMD OCI artifact分发 + OLOT KServe ModelCar打包 |
| **Toolbx 兼容** | 可直接 `toolbox create/enter`，自动透传HOME/cwd/X11 |
| **开发透传** | compose.dev.yaml：SSH agent/git/X11/pip cache（opt-in） |

## 项目结构

```
jupyter-podman-rootless/
├── AGENTS.md              # AI协作者入口（SpecWeave路由）
├── README.md              # 本文件（项目入口）
├── Containerfile          # 7层镜像构建定义
├── entrypoint.sh          # 7步启动脚本
├── compose.yaml           # podman-compose编排
├── compose.dev.yaml       # 开发透传覆盖
├── pyproject.toml         # Python项目配置（invoke依赖）
├── tasks/                 # invoke任务定义
├── config/                # 配置文件（sshd/supervisord/jupyter/podman）
├── scripts/               # 辅助脚本（healthcheck/olot_car）
├── conda-lock/            # Conda环境定义
├── docs/                  # 人类可读文档（原子化拆分）
└── .agents/               # AI协作者规范容器（原子化拆分）
```

## 核心命令速查

```bash
# 查看所有可用命令（13个：8核心+5model）
invoke --list

# 构建与运行
invoke build --apt-mirror tuna    # 构建镜像（清华源）
invoke run                        # 启动容器
invoke status                     # 查看状态
invoke logs                       # 查看日志
invoke shell                      # 进入容器
invoke stop                       # 停止容器
invoke clean --image              # 清理镜像

# ML模型管理
podman-compose --profile registry up -d  # 启动本地模型仓库
invoke model.push ./model --ref localhost:5000/models/bert:v1
invoke model.pack ./model --base jupyter-podman-rootless:latest --ref localhost:5000/models/car:v1
```

## 三种使用方式

1. **invoke封装（推荐）**：自动密码生成、路径转换、三层后端选择
2. **podman-compose直接使用**：标准Compose Spec，支持多文件覆盖和profiles
3. **开发透传模式**：叠加compose.dev.yaml，透传SSH agent/GUI/pip cache
4. **Toolbx模式**：`toolbox create/enter`，深度主机集成

详见 [docs/01-getting-started.md](docs/01-getting-started.md)。

## License

与 SpecWeave 主仓库保持一致。
