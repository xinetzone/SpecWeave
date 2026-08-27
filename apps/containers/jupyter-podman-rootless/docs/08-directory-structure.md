---
id: "jupyter-directory-structure"
title: "目录结构"
source: "README.md#目录结构"
---
# 目录结构

```
jupyter-podman-rootless/
├── Containerfile              # 7层镜像构建定义（含Toolbx兼容标记）
├── entrypoint.sh              # 7步启动脚本
├── compose.yaml               # podman-compose 声明式编排（jupyter + model-registry服务）
├── compose.dev.yaml           # 开发透传覆盖文件（SSH/git/X11/pip cache）
├── .env.example               # 环境变量模板（含REGISTRY/DEV透传配置说明）
├── pyproject.toml             # Python 项目配置（invoke 依赖，含[compose]/[full]/[model] extras）
├── .containerignore           # 构建忽略规则
├── .gitignore                 # Git忽略规则
├── README.md                  # 项目文档入口（已原子化至docs/）
├── AGENTS.md                  # AI 协作者入口（SpecWeave 路由，已精简）
├── docs/                      # 人类可读文档（原子化拆分，14个文档+索引）
│   └── README.md              # 文档索引
│
├── tasks/                     # invoke 任务定义
│   ├── __init__.py            # 任务入口与命名空间配置（核心命令+model.*命令）
│   ├── utils.py               # 工具函数（运行时检测/路径转换/随机字符串）
│   ├── client.py              # Podman/Docker client wrapper（三层后端优先级检测）
│   ├── compose_backend.py     # podman-compose 后端封装
│   ├── build.py               # 镜像构建任务
│   ├── manage.py              # 容器生命周期管理（run/stop/status/clean）
│   ├── interact.py            # 容器交互（shell/logs/exec）
│   ├── model.py               # ML模型管理任务（push/pull/config/pack/extract）
│   └── container.py           # 向后兼容聚合模块（re-export所有子模块任务）
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
│       ├── containerfile.md   # Containerfile编写规范
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
- **Containerfile**：7层镜像构建定义，遵循BuildKit最佳实践，包含Toolbx兼容标记
- **.containerignore**：构建时排除文件（.git、.trae、.agents/docs、workspace等）

### 启动相关
- **entrypoint.sh**：7步启动流程（密码→SSH keys→Podman→Jupyter→supervisord）
- **config/supervisord.conf**：服务管理配置（sshd + jupyter）
- **scripts/healthcheck.sh**：30秒间隔健康检查（5项检查）

### 编排相关
- **compose.yaml**：标准声明式配置（jupyter服务 + model-registry profile）
- **compose.dev.yaml**：开发透传覆盖（SSH/GUI/pip cache等opt-in透传）
- **.env.example**：环境变量模板

### Invoke任务
- **tasks/client.py**：三层后端自动检测和封装（compose → SDK → CLI）
- **tasks/compose_backend.py**：podman-compose后端实现
- **tasks/子模块**：build/manage/interact/model各职责分离

### 配置文件
- **config/containers/storage.conf**：fuse-overlayfs存储配置
- **config/sshd_config**：SSH服务配置
- **config/supervisor/conf.d/**：各服务的supervisord配置

### AI协作者
- **AGENTS.md**：AI协作者入口路由（已精简）
- **.agents/**：项目特有规范容器（按单一职责拆分）

### 文档
- **docs/**：人类可读文档（原子化拆分，每个文件一个主题）
