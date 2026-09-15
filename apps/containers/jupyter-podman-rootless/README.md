# jupyter-podman-rootless

> 基于 Podman rootless 模式的 Jupyter 开发容器：Python 3.14t (free-threading) + Miniforge3 + SSH + rootless Podman，通过 supervisord 管理多服务。三层后端编排（podman-compose 声明式 → podman-py SDK → CLI fallback），内置 OMLMD 模型 artifact 分发、OLOT KServe ModelCar 打包、Toolbx 透传兼容，镜像内嵌容器编排上游工具（podman-compose / podman-py / toolbox，经 SpecWeave 根 vendor/ 子模块固定 commit 引入），配套 `jpman` 零依赖 CLI 提供镜像缓存、WSL2 发行版一键导出、增量重建等功能。

---

## 快速开始

### 方式一：jpman 零依赖 CLI（推荐，WSL/Linux/macOS）

```bash
# WSL/Linux：直接使用（无需安装Python依赖）
bash bin/jpman rebuild-all   # 全量构建镜像（清华源加速）
bash bin/jpman start         # 启动容器（幂等，自动处理依赖）
bash bin/jpman info          # 查看访问信息

# 安装为全局命令（可选）
bash bin/jpman install       # 创建symlink到 ~/.local/bin/jpman
jpman status                 # 之后可全局使用
```

Windows 用户可使用 `bin\jpman.cmd` 或 `bin\jpman.ps1`。

### 方式二：invoke 封装（功能完整，需要Python依赖）

```bash
# 安装依赖（invoke + podman-compose）
pip install -e ".[compose]"

# 构建镜像（清华镜像源加速）
invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna

# 启动容器（自动生成密码和token，端口2222:22, 8888:8888）
invoke run
```

### 访问信息

启动成功后，终端会打印访问信息：
```
SSH:       ssh -p 2222 devuser@localhost
Jupyter:   http://localhost:8888/lab?token=<自动生成的token>
Password:  <自动生成或配置的密码>
```

详细使用指南见 [docs/](docs/README.md)。

## 文档导航

### 📚 使用文档

| 文档 | 说明 |
|------|------|
| [docs/README.md](docs/README.md) | 文档索引 |
| [docs/00-overview.md](docs/00-overview.md) | 特性一览 |
| [docs/01-getting-started.md](docs/01-getting-started.md) | 快速开始：前置条件、四种使用方式 |
| [docs/02-invoke-reference.md](docs/02-invoke-reference.md) | Invoke命令参考：核心命令、ML命令、参数说明 |
| [docs/03-environment-variables.md](docs/03-environment-variables.md) | 环境变量参考 |
| [docs/04-image-architecture.md](docs/04-image-architecture.md) | 镜像架构：多阶段构建与运行时分层、7步启动、服务管理 |
| [docs/05-rootless-podman.md](docs/05-rootless-podman.md) | Rootless Podman使用说明 |
| [docs/06-ml-model-management.md](docs/06-ml-model-management.md) | ML模型管理：OMLMD+OLOT、ModelCar打包 |
| [docs/07-toolbx-passthrough.md](docs/07-toolbx-passthrough.md) | Toolbx透传开发模式 |
| [docs/08-directory-structure.md](docs/08-directory-structure.md) | 目录结构说明 |
| [docs/09-three-tier-backend.md](docs/09-three-tier-backend.md) | 三层后端编排架构 |
| [docs/10-direct-cli-usage.md](docs/10-direct-cli-usage.md) | 直接使用Podman/Docker命令 |
| [docs/11-free-threading.md](docs/11-free-threading.md) | Python Free-Threading（无GIL）说明 |
| [docs/12-healthcheck.md](docs/12-healthcheck.md) | 健康检查机制 |
| [docs/13-faq.md](docs/13-faq.md) | 常见问题解答 |
| [docs/14-jpman-cli.md](docs/14-jpman-cli.md) | jpman 零依赖CLI参考 |
| [docs/15-wsl-export.md](docs/15-wsl-export.md) | WSL2发行版导出与使用 |
| [docs/16-image-cache.md](docs/16-image-cache.md) | 镜像缓存与增量重建 |
| [docs/17-upstream-tools.md](docs/17-upstream-tools.md) | 容器编排上游工具内嵌：vendor/ 子模块引入、upstream/ stage 机制 |

### 🤖 AI协作者规范

项目特有的AI协作者规范已原子化拆分至 [.agents/](.agents/README.md) 目录：

| 规范 | 说明 |
|------|------|
| [.agents/README.md](.agents/README.md) | AI资产容器索引 |
| [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | Containerfile编写规范（构建架构、内嵌编排工具、Toolbx兼容） |
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
| **Jupyter** | JupyterLab ≥4.4 + Notebook ≥7.3，端口 8888，支持隐藏文件显示 |
| **SSH** | OpenSSH Server，端口 22，支持密码/公钥认证 |
| **Podman** | Rootless 模式（fuse-overlayfs + crun），支持 DinP（容器内运行容器） |
| **服务管理** | supervisord 管理 sshd + jupyter，tini 作为 PID 1 |
| **非root用户** | devuser (UID 1000)，sudo 默认关闭（`--grant-sudo`/`GRANT_SUDO=yes` 开启） |
| **中文环境** | zh_CN.UTF-8 locale + Asia/Shanghai 时区 |
| **镜像源** | APT/Conda/PIP 均支持 official / tuna / aliyun |
| **三层后端** | 宿主机 invoke：podman-compose（优先）→ podman-py SDK → CLI fallback（pip 安装，与镜像内嵌版本独立） |
| **内嵌编排工具** | 镜像内置 podman-compose / podman-py SDK / toolbox（经 vendor/ 子模块固定 commit 引入，详见 [docs/17-upstream-tools.md](docs/17-upstream-tools.md)） |
| **ML 模型** | OMLMD OCI artifact分发 + OLOT KServe ModelCar打包 + 本地model-registry |
| **Toolbx 兼容** | 宿主 `toolbox create/enter` 经专用 `:toolbx` 变体支持（`invoke build-toolbx`），自动透传HOME/cwd/X11；镜像内另内嵌 toolbox CLI |
| **开发透传** | compose.dev.yaml：SSH agent/git/X11/pip cache（opt-in） |
| **零依赖CLI** | `jpman`：纯bash脚本，无需Python依赖，提供快速管理 |
| **镜像缓存** | `.image-cache/`：podman save/load 快速备份恢复，pigz多线程压缩 |
| **WSL2导出** | 一键导出为WSL2发行版，自动配置wsl.conf和Conda激活 |
| **增量重建** | `jpman rebuild`：基于主 Containerfile 层缓存，配置变更仅重建 Layer 4/5（<10秒） |
| **跨平台** | 支持WSL/Linux/macOS（bash）+ Windows（cmd/ps1） |

## 项目结构

```
jupyter-podman-rootless/
├── AGENTS.md              # AI协作者入口（SpecWeave路由）
├── README.md              # 本文件（项目入口）
├── Containerfile          # 多阶段构建定义（3 阶段 + toolbox-builder aux；passt 已固化，Layer 4/5 支持缓存增量重建，内嵌编排工具）
├── entrypoint.sh          # 7步启动脚本
├── compose.yaml           # podman-compose编排（jupyter + model-registry）
├── compose.dev.yaml       # 开发透传覆盖（opt-in）
├── pyproject.toml         # Python项目配置（scikit-build-core 纯 Python wheel；invoke + jpman-common + python-dotenv）
├── ../shared/             # 组内共享包 apps/containers/shared（jpman_common：连接层/进程/平台/容器只读工具，先于本包安装）
├── tasks.py               # invoke 入口（转发到 jpman_builder.tasks）
├── .env.example           # 环境变量模板
├── .containerignore       # Podman构建忽略规则（upstream/*/README.md 反白放行）
├── .gitignore             # Git忽略规则（upstream/ 等）
├── bin/                   # jpman零依赖CLI
│   ├── jpman              # WSL/Linux/macOS bash版本
│   ├── jpman.cmd          # Windows cmd版本
│   └── jpman.ps1          # Windows PowerShell版本
├── src/jpman_builder/tasks/  # invoke任务定义（三层后端 + stage_upstream 构建前置 stage）
├── upstream/              # 构建上下文临时目录（stage 机制生成，git忽略）
├── config/                # 配置文件（sshd/supervisord/jupyter/podman）
├── scripts/               # 辅助脚本（healthcheck/olot_car）
├── conda-lock/            # Conda环境定义（含omlmd+olot）
├── docs/                  # 人类可读文档（原子化拆分）
├── .agents/               # AI协作者规范容器（原子化拆分）
├── .image-cache/          # 镜像缓存目录（git忽略）
└── .wsl-cache/            # WSL发行版缓存目录（git忽略）
```

## 核心命令速查

### jpman CLI（零依赖）

```bash
# 容器生命周期
bash bin/jpman start       # 启动容器（幂等，自动等待健康检查）
bash bin/jpman stop        # 停止并删除容器
bash bin/jpman restart     # 重启
bash bin/jpman status      # 查看状态（含镜像信息）
bash bin/jpman info        # 查看访问信息（URL、凭证、端口）
bash bin/jpman url         # 仅打印Jupyter URL（方便复制粘贴）

# 交互
bash bin/jpman shell       # 进入容器shell（devuser）
bash bin/jpman shell --root # 以root进入
bash bin/jpman logs        # 查看日志（--follow/-f 实时跟踪）
bash bin/jpman exec CMD    # 以devuser执行命令
bash bin/jpman root CMD    # 以root执行命令

# 构建与缓存
bash bin/jpman rebuild     # 增量重建（仅配置变更，<10秒）
bash bin/jpman rebuild-all # 全量重建（需要网络，较慢）
bash bin/jpman save        # 保存镜像到.image-cache/（备份）
bash bin/jpman load        # 从.image-cache/加载镜像

# WSL2集成
bash bin/jpman wsl-export  # 一键导出为WSL2发行版
bash bin/jpman wsl-verify  # 验证WSL2发行版环境（冒烟测试）
bash bin/jpman keepalive   # 启动WSL保活进程（防止容器自动退出）
bash bin/jpman install     # 安装为全局命令
```

### invoke 封装（功能完整）

```bash
# 查看所有可用命令
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

## 四种使用方式

1. **jpman零依赖CLI（推荐快速上手）**：纯bash实现，无需Python依赖，提供镜像缓存、WSL导出、增量重建等实用功能
2. **invoke封装（推荐日常开发）**：自动密码生成、路径转换、三层后端选择、ML模型管理完整功能
3. **podman-compose直接使用**：标准Compose Spec，支持多文件覆盖和profiles
4. **Toolbx模式**（宿主机侧）：`invoke build-toolbx` 后 `toolbox create/enter -i ...:toolbx`，深度主机集成，透传HOME/cwd/X11（见 docs/07）

详见 [docs/01-getting-started.md](docs/01-getting-started.md)。

## License

与 SpecWeave 主仓库保持一致。
