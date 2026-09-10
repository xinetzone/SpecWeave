---
id: "jupyter-directory-structure"
title: "目录结构"
source: "README.md#目录结构"
---
# 目录结构

```
jupyter-podman-rootless/
├── Containerfile              # 多阶段构建定义（3 阶段运行时链 + toolbox-builder aux 阶段，final 内 5 层运行时分层，含 Toolbx 兼容标记与内嵌编排工具）
├── entrypoint.sh              # 7步启动脚本
├── compose.yaml               # podman-compose 声明式编排（jupyter + model-registry服务）
├── compose.dev.yaml           # 开发透传覆盖文件（SSH/git/X11/pip cache）
├── compose.passthrough.yaml   # 运行时透传主层（Host 网络 + D-Bus，专用 tag :passthrough）
├── compose.passthrough.gui.yaml  # 运行时透传分层：Wayland 套接字
├── compose.passthrough.gpu.yaml  # 运行时透传分层：GPU（/dev/dri）
├── compose.passthrough.usb.yaml  # 运行时透传分层：USB（/dev/bus/usb）
├── .env.example               # 环境变量模板（含REGISTRY/DEV/透传分层配置说明）
├── pyproject.toml             # Python 项目配置（invoke 依赖，scikit-build-core，含[compose]/[full]/[model] extras）
├── CMakeLists.txt             # scikit-build-core CMake配置
├── tasks.py                   # invoke 入口（src/ 加入 sys.path 并转发到 jpman_builder.tasks）
├── mirror.conf                # 镜像源配置
├── .containerignore           # 构建忽略规则（含 upstream/*/README.md 反白放行）
├── .gitignore                 # Git忽略规则（upstream/ 等）
├── README.md                  # 项目文档入口（已原子化至docs/）
├── AGENTS.md                  # AI 协作者入口（SpecWeave 路由，已精简）
├── bin/                       # jpman 零依赖 CLI
│   ├── jpman                  # WSL/Linux/macOS bash 版本
│   ├── jpman.cmd              # Windows cmd 版本
│   └── jpman.ps1              # Windows PowerShell 版本
├── docs/                      # 人类可读文档（原子化拆分，18个编号文档+索引）
│   └── README.md              # 文档索引
│
├── src/jpman_builder/tasks/   # invoke 任务定义（jpman_builder 包，经 tasks.py 暴露）
│   ├── __init__.py            # 任务入口与命名空间配置（核心命令+model.*命令）
│   ├── stage_upstream.py      # 构建前置 stage：vendor/ 子模块 → <应用根>/upstream/（podman-compose/podman-py/toolbox）
│   ├── utils.py               # 工具函数（运行时检测/路径转换/随机字符串）
│   ├── client.py              # Podman/Docker client wrapper（三层后端优先级检测）
│   ├── compose_backend.py     # podman-compose 后端封装
│   ├── build.py               # 镜像构建任务（构建前自动 stage 上游源树）
│   ├── manage.py              # 容器生命周期管理（run/stop/status/clean）
│   ├── interact.py            # 容器交互（shell/logs/exec）
│   ├── model.py               # ML模型管理任务（push/pull/config/pack/extract）
│   └── container.py           # 向后兼容聚合模块（re-export所有子模块任务）
│
├── upstream/                  # 构建上下文临时目录（构建前 stage 生成、git-ignored，源来自 SpecWeave 根 vendor/ 子模块）
│   ├── podman-compose/        #   上游源树快照（conda-builder 本地 pip 安装用）
│   ├── podman-py/             #   上游源树快照（conda-builder 本地 pip 安装用）
│   └── toolbox/               #   上游源树快照（toolbox-builder go build 用）
│
├── local-cache/               # 本地安装包缓存（构建上下文内，网络源之前优先使用）
│   └── miniforge/             #   预下载的 Miniforge3-Linux-<arch>.sh（*.sh 被 git-ignored，.gitkeep 保证 COPY 有效）
│
├── config/                    # 配置文件
│   ├── supervisord.conf       # supervisord 主配置
│   ├── sshd_config            # SSH 服务配置
│   ├── jupyter_notebook_config.py  # Jupyter 基础配置
│   ├── containers/
│   │   └── storage.conf       # Podman 系统级存储配置（fuse-overlayfs）
│   └── supervisor/
│       └── conf.d/
│           ├── sshd.conf      # supervisord sshd 服务配置
│           └── jupyter.conf   # supervisord jupyter 服务配置
│
├── scripts/                   # 辅助脚本
│   ├── healthcheck.sh         # 健康检查脚本（sshd + jupyter + podman）
│   ├── olot_car.py            # 容器内OLOT ModelCar辅助脚本
│   └── lib/
│       └── logging.sh         # 彩色日志库
│
├── .agents/                   # AI协作者规范容器（原子化拆分，7个规则文件）
│   ├── README.md              # AI资产索引
│   └── rules/
│       ├── containerfile.md   # Containerfile编写规范（多阶段构建架构+运行时分层）
│       ├── entrypoint.md      # Entrypoint启动脚本规范
│       ├── services.md        # 服务配置规范
│       ├── compose.md         # Compose编排与透传规范
│       ├── invoke-tasks.md    # Invoke任务开发规范
│       ├── ml-models.md       # ML模型管理规范
│       └── build-test.md      # 构建与测试规范
│
├── conda-lock/
│   └── environment.yml        # Conda 环境定义（Python 3.14t + Jupyter + omlmd + olot）
│
└── workspace/                 # 工作目录挂载点（容器内 /workspace）
    └── .gitkeep
```

## 关键文件说明

### 构建相关
- **Containerfile**：多阶段构建定义（3 阶段运行时链 + toolbox-builder aux 阶段 + final 内 5 层运行时分层），内嵌 podman-compose/podman-py/toolbox 三个编排工具，遵循 BuildKit 最佳实践，包含 Toolbx 兼容标记
- **upstream/**：构建上下文临时目录，构建前由 stage 机制从 SpecWeave 根 `vendor/` 三个 submodule 复制源树生成（git-ignored，不提交；详见 [17-upstream-tools.md](17-upstream-tools.md)）
- **local-cache/miniforge/**：本地安装包缓存。把预下载的 `Miniforge3-Linux-<arch>.sh` 放入该目录，Containerfile Stage 2 会在**任何网络源之前**优先使用它，从而规避 GitHub 限速/重置并支持离线构建；缓存为空时自动回退到镜像源（详见 [build-test.md](../.agents/rules/build-test.md) 构建 FAQ）
- **.containerignore**：构建时排除文件（.git、.trae、.agents、workspace、`*.md` 等），并对 `upstream/podman-compose/README.md`、`upstream/podman-py/README.md` 反白放行（本地 pip 构建需其作为 long_description）
- **.gitignore**：忽略 `.env`、`/workspace/`、`upstream/`、`local-cache/miniforge/*.sh`、`.image-cache/`、`.wsl-cache/` 等

### 启动相关
- **entrypoint.sh**：7步启动流程（密码→SSH keys→Podman→Jupyter→supervisord）
- **config/supervisord.conf**：服务管理配置（sshd + jupyter）
- **scripts/healthcheck.sh**：30秒间隔健康检查（5项检查）

### 编排相关
- **compose.yaml**：标准声明式配置（jupyter服务 + model-registry profile）
- **compose.dev.yaml**：开发透传覆盖（SSH/GUI/pip cache等opt-in透传）
- **.env.example**：环境变量模板

### Invoke任务（src/jpman_builder/tasks/）
- **tasks.py**（根）：invoke 入口，把 `src/` 加入 sys.path 并转发至 `jpman_builder.tasks` 命名空间
- **src/jpman_builder/tasks/stage_upstream.py**：构建前置 stage 机制（vendor/ 子模块源树 → `<应用根>/upstream/`，幂等）
- **src/jpman_builder/tasks/client.py**：三层后端自动检测和封装（compose → SDK → CLI）
- **src/jpman_builder/tasks/compose_backend.py**：podman-compose后端实现
- **src/jpman_builder/tasks/子模块**：build（构建前自动 stage）/manage/interact/model各职责分离

### 配置文件
- **config/containers/storage.conf**：fuse-overlayfs存储配置
- **config/sshd_config**：SSH服务配置
- **config/supervisor/conf.d/**：各服务的supervisord配置

### AI协作者
- **AGENTS.md**：AI协作者入口路由（已精简）
- **.agents/**：项目特有规范容器（按单一职责拆分）

### 文档
- **docs/**：人类可读文档（原子化拆分，每个文件一个主题）
