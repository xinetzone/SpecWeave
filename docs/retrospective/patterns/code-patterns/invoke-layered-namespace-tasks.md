---
id: "invoke-layered-namespace-tasks"
title: "invoke 任务分层命名空间模式"
type: "code-pattern"
date: "2026-08-27"
maturity: "L1-draft"
source: "retrospective-jupyter-podman-rootless-seven-rounds 模式P3 + 洞察I5"
related_patterns:
  - "capability-stack-progressive-building"
  - "container-devtool-seven-layer-stack"
  - "scikit-build-core-pure-python-minimal"
tags: ["invoke", "task-runner", "namespace", "cli", "python", "task-management", "collection", "command-aliases"]
validation_count: 1
reuse_count: 0
---

# invoke 任务分层命名空间模式

## 模式概述

使用Python invoke作为项目任务管理工具时，最常见的失败组织方式有两种：
1. **全平铺**：所有20+个任务都放在根命名空间，`invoke --list`一屏放不下，难以发现和记忆
2. **全分层**：所有任务都放在子命名空间，日常高频命令（build/run/stop）需要输入`invoke container.build`这样的前缀，降低使用效率

invoke任务分层命名空间模式采用**"核心命令平铺+领域命令分层"**的二八原则：80%高频日常命令在根命名空间直接访问（便捷），20%领域特定命令在子命名空间分类组织（避免命名冲突），核心命令同时在子命名空间暴露别名（方便分类浏览）。

## 触发场景

- 使用invoke作为Python项目的任务运行器/构建工具时
- 项目任务数量超过10个，需要分类组织时
- 既有日常高频命令（build/run/stop/test），又有领域特定命令（model.pack/db.migrate等）时
- 适用于：容器管理工具、开发环境CLI、Python库项目任务管理、ML/数据工程项目
- 不适用于：任务数量≤8个的简单项目（直接平铺即可）、非Python项目（使用make/just/Task等其他工具）、单命令脚本

## 核心配置

### 目录结构

```
<project-root>/
├── pyproject.toml          # 配置[tool.invoke]
└── tasks/
    ├── __init__.py         # Collection入口+命名空间配置（核心）
    ├── <core_module>.py    # 核心任务模块（如container.py）
    ├── <domain1>.py        # 领域任务模块1（如model.py）
    ├── <domain2>.py        # 领域任务模块2（如db.py）
    └── utils.py            # 工具函数（无@task装饰）
```

### 核心代码：tasks/__init__.py（直接复制修改即可）

```python
"""项目任务入口。

常用命令：
    invoke build      - 构建
    invoke run        - 运行
    invoke stop       - 停止
    invoke clean      - 清理
    invoke status     - 状态
    invoke <domain>.* - 领域子命令（见 invoke --list）
"""
from invoke import Collection

# 导入各任务模块
from . import core, model, db  # 根据实际模块名修改

ns = Collection()

# ===== 核心高频任务：提升到根命名空间（80%日常使用） =====
ns.add_task(core.build, default=True)  # default=True表示`invoke`不带参数时执行
ns.add_task(core.run)
ns.add_task(core.stop)
ns.add_task(core.clean)
ns.add_task(core.status)
ns.add_task(core.shell)
ns.add_task(core.logs)
ns.add_task(core.exec_task)  # 注意：exec是Python保留字，用exec_task

# ===== 核心命令别名：同时在子命名空间暴露（方便分类浏览） =====
ns.add_collection(Collection.from_module(core), name="core")

# ===== 领域特定任务：仅在子命名空间暴露（20%领域操作） =====
ns.add_collection(Collection.from_module(model), name="model")
ns.add_collection(Collection.from_module(db), name="db")

# ===== 默认配置 =====
ns.configure(
    {
        "core": {
            "image_tag": "myproject:latest",
            "workspace": "./workspace",
        },
        "model": {
            "registry_url": "localhost:5000",
        },
        "db": {
            "connection_string": "sqlite:///dev.db",
        },
    }
)
```

### pyproject.toml 配置

```toml
[tool.invoke]
package = "tasks"  # 指向tasks包目录
```

### 任务模块写法示例：tasks/core.py

```python
from invoke import task

@task
def build(c):
    """构建镜像/项目"""
    c.run("echo 'building...'")

@task
def run(c):
    """运行服务"""
    c.run("echo 'running...'")

@task
def stop(c):
    """停止服务"""
    c.run("echo 'stopping...'")

# ... 其他核心任务
```

### 领域模块写法示例：tasks/model.py

```python
from invoke import task

@task
def push(c, path, ref=None):
    """推送模型到OCI registry"""
    c.run(f"omlmd push {path} --ref {ref or c.model.registry_url}")

@task
def pull(c, ref):
    """从OCI registry拉取模型"""
    c.run(f"omlmd pull {ref}")

@task
def pack(c, path, base=None, ref=None):
    """打包模型为ModelCar镜像"""
    c.run(f"olot pack {path} --base {base} --ref {ref}")
```

## 命名空间组织原则

### 80/20分层规则

| 分类 | 数量占比 | 暴露位置 | 命令类型 | 示例 |
|------|---------|---------|---------|------|
| **核心命令** | ~80%日常使用 | 根命名空间 + 子命名空间别名 | 构建、运行、停止、清理、状态、日志、Shell、执行 | build, run, stop, clean, status, logs, shell, exec |
| **领域命令** | ~20%特定操作 | 仅子命名空间 | 特定领域/功能模块操作 | model.push, model.pack, db.migrate, db.seed |

### 核心命令选择标准

提升到根命名空间的命令应满足**所有**以下条件：
1. **高频**：每周使用≥5次
2. **通用**：不属于某个特定领域模块
3. **短名**：命令名1-2个单词（build而非build-image）
4. **无冲突**：不会与其他模块命令重名

### 子命名空间划分标准

按**业务领域/功能模块**划分，而非技术类型：
- ✅ 正确：`model.*`（ML模型操作）、`db.*`（数据库操作）、`deploy.*`（部署操作）
- ❌ 错误：`python.*`、`shell.*`、`utils.*`（按技术类型划分无意义）

## 任务数量参考（来自实战验证）

| 命名空间 | 任务数量 | 命令示例 | 说明 |
|---------|---------|---------|------|
| 根命名空间 | 6-10个 | build/run/stop/clean/status/shell/logs/exec | 超过10个考虑分类到子命名空间 |
| 每个子命名空间 | 3-7个 | model.push/pull/config/pack/extract（5个） | 超过7个考虑拆分为更小的子命名空间 |
| **总计** | **15-25个** | 本项目21个（8+8+5） | 超过25个说明项目职责可能过多 |

## 反模式（不要这么做）

### ❌ 反模式1：所有任务平铺在根命名空间

```python
# ❌ 错误：20+个任务全在根，一屏列不完
ns = Collection()
ns.add_task(build)
ns.add_task(run)
ns.add_task(stop)
# ... 20个add_task
ns.add_task(model_push)  # 命名冲突被迫加前缀model_
ns.add_task(model_pull)
ns.add_task(db_migrate)  # 命名冲突被迫加前缀db_
```

**问题**：
- `invoke --list`输出超过一屏，难以发现可用命令
- 不同领域命令命名冲突，被迫加`model_`/`db_`前缀（`invoke model_push` vs `invoke model.push`）
- 没有分类，新用户不知道哪些命令相关

### ❌ 反模式2：所有任务都放在子命名空间

```python
# ❌ 错误：常用命令也需要前缀
ns = Collection()
ns.add_collection(Collection.from_module(container), name="container")
ns.add_collection(Collection.from_module(model), name="model")
# 用户必须输入 invoke container.build 而非 invoke build
```

**问题**：
- 高频命令需要额外输入前缀，降低效率
- 肌肉记忆被破坏（习惯了`make build`/`npm run build`，要额外输入`container.`）
- 核心命令没有快捷方式

### ❌ 反模式3：任务模块与业务逻辑混放

```
myproject/
├── __init__.py
├── build.py      # ❌ 既有业务逻辑又有@task
├── model.py      # ❌ 既有ML逻辑又有@task
└── utils.py
```

**问题**：
- 业务代码和任务定义耦合，难以独立测试
- 导入任务时意外触发业务逻辑副作用
- 非invoke使用场景（如作为库导入）被迫安装invoke

**正确做法**：任务定义统一放在`tasks/`目录，业务代码在其他包中，tasks/模块只导入和调用业务函数。

### ❌ 反模式4：任务名使用Python保留字

```python
# ❌ 错误：exec是Python保留字
@task
def exec(c, command):  # SyntaxError或名称冲突
    c.run(command)
```

**正确做法**：使用`exec_task`或`run_cmd`等替代名，在Collection中可以通过`name`参数映射：
```python
ns.add_task(exec_task, name="exec")  # 对外仍叫invoke exec
```

### ❌ 反模式5：根命名空间任务超过10个

根命名空间任务超过10个时，`invoke --list`的根级命令列表会超过一屏，失去"快速发现"的价值。此时应该将低频命令移到子命名空间。

## 检验标准

做完之后怎么知道做对了？

- [ ] `invoke --list`根级命令≤10个，一屏可见
- [ ] 核心命令（build/run/stop等）不需要输入命名空间前缀：`invoke build`直接工作
- [ ] 领域命令有明确的命名空间前缀：`invoke model.push`而非`invoke model_push`
- [ ] 核心命令同时在子命名空间可用：`invoke container.build`也工作（别名）
- [ ] pyproject.toml配置了`[tool.invoke] package = "tasks"`
- [ ] tasks/目录只包含@task定义和任务编排，不包含业务逻辑
- [ ] 每个子命名空间任务数≤7个
- [ ] 总任务数在15-25个之间
- [ ] `invoke`（不带参数）执行默认任务（通常是build或help）
- [ ] `invoke --help <command>`对每个命令都有docstring说明
- [ ] 新增领域功能时，创建新的tasks/<domain>.py并添加Collection，不往根命名空间塞

## invoke --list 输出示例（本项目验证）

```
Available tasks:

  build       构建镜像（默认任务）
  clean       清理资源
  exec        在容器中执行命令
  logs        查看容器日志
  run         启动容器
  shell       进入容器Shell
  status      查看容器状态
  stop        停止并删除容器

  container.* 容器管理子命令集合（同根命令别名）
    build     构建镜像
    clean     清理资源
    exec      在容器中执行命令
    logs      查看容器日志
    run       启动容器
    shell     进入容器Shell
    status    查看容器状态
    stop      停止并删除容器

  model.*  ML模型管理
    config   查看模型元数据配置
    extract  从ModelCar镜像提取模型
    pack     打包模型为KServe ModelCar镜像
    pull     从OCI registry拉取模型
    push     推送模型到OCI registry
```

总计21个任务（8根+8别名+5领域），根级命令8个一屏可见。

## 迁移示例

### 示例1：容器管理工具（本项目，源案例）

- **包目录**：tasks/（9个Python模块）
- **核心命令**：8个（build/run/stop/clean/status/shell/logs/exec）
- **领域命名空间**：model.*（5个ML模型命令）
- **验证结果**：`invoke --list`列出21个任务，根级8个，使用流畅

### 示例2：Python库项目

```
tasks/
├── __init__.py
├── build.py    # 构建相关：build/install/test/lint/format/clean/docs
├── publish.py  # 发布相关：publish/test-pypi/check-dist
└── env.py      # 环境相关：venv/setup/dev-install
```

- 根命名空间：build/test/lint/format/clean（5个核心）
- 子命名空间：build.*（别名）、publish.*（3个）、env.*（3个）

### 示例3：Web应用项目

```
tasks/
├── __init__.py
├── app.py      # 应用管理：run/stop/status/logs/shell
├── db.py       # 数据库：migrate/upgrade/downgrade/seed/reset
├── deploy.py   # 部署：staging/prod/rollback/status
└── test.py     # 测试：test/coverage/e2e (提升到根：test)
```

- 根命名空间：run/stop/test/lint/build（5-6个）
- 子命名空间：app.*、db.*（5个）、deploy.*（4个）

### 示例4：跨领域——概念迁移到其他Task Runner

"常用命令短名直达+领域命令分类组织"的核心思想可迁移到：
- **make**：`.PHONY`核心目标放最前，领域目标按前缀分组（`model-push`/`db-migrate`），用注释分段
- **just**：默认recipe放最前，用`[module]`注释分组
- **npm scripts**：核心脚本（build/start/test）在根，领域脚本用前缀（`model:push`/`db:migrate`，npm支持`npm run model:push`）
- **Task (taskfile.yml)**：`cmds`核心任务放根，领域任务用namespace分组
- **poetry scripts**：核心命令直接在[tool.poetry.scripts]，领域命令用插件或额外脚本

## 命令命名最佳实践

| 原则 | 正确 | 错误 |
|------|------|------|
| 动词开头 | build, run, push, pull | image, container, model（名词） |
| 短名优先 | build, shell, logs | build-image, interactive-shell, container-logs |
| 一致命名 | 所有子模块都用push/pull/start/stop | model.upload/db.run（不一致） |
| 避免缩写 | status, config, exec | st, cfg, ex（难以记忆） |
| 保留字处理 | exec_task（映射为exec） | exec（Python保留字报错） |

## 与其他模式的关系

| 模式 | 关系 |
|------|------|
| [capability-stack-progressive-building](../methodology-patterns/governance-strategy/capability-stack-progressive-building.md) | 方法论基础：L2-L5各层能力对应的任务按本模式分层组织 |
| [container-devtool-seven-layer-stack](../architecture-patterns/container-devtool-seven-layer-stack.md) | 配套架构：容器七层栈的任务入口使用本模式 |
| [scikit-build-core-pure-python-minimal](scikit-build-core-pure-python-minimal.md) | 配套构建：pyproject.toml中[tool.invoke]配置与构建配置共存 |

## Changelog

<!-- changelog -->
- 2026-08-27 | feat | 从Jupyter Podman Rootless七轮优化复盘萃取，L1-draft单案例待验证
