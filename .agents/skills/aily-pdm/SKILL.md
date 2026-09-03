---
source: "镜像自 Trae IDE builtin（源镜像已清理，原路径 skills/aily-pdm/SKILL.md）"
name: aily-pdm
description: "PDM（Python Development Master）专业技能助手，提供完整的Python包管理和项目管理指导。

当用户询问以下内容时使用此技能：
- PDM安装、项目初始化、依赖管理（add/remove/update）
- pyproject.toml配置、PEP 621元数据
- PDM命令（pdm init, pdm add, pdm install, pdm lock, pdm publish等）
- 虚拟环境配置、Python版本管理
- PDM插件开发、脚本编写（tool.pdm.scripts）
- 依赖解析错误、构建配置问题
- 从Pipenv/Poetry/requirements.txt迁移到PDM
- CI/CD集成、IDE配置（VS Code/PyCharm）
- PDM高级用法（hooks、环境变量、集中式缓存）
- 项目结构设计、最佳实践
- pdm.lock锁定文件管理
- 发布到PyPI、自定义索引配置
- Python/PDM安装（系统无Python时的引导安装）
- conda环境与PDM协同使用
- monorepo多包项目管理
- PEP 723内联脚本、workspace原生支持
- uv后端集成、Docker容器化部署"
---


# PDM专业助手

PDM（Python Development Master）是一个现代Python包和依赖项管理器，支持最新PEP标准。

## 核心能力

1. **环境准备与安装** - Python/PDM安装引导
2. **项目初始化与管理**
3. **依赖管理（添加、更新、删除）**
4. **配置与最佳实践**
5. **错误诊断与解决**
6. **IDE/CI/CD集成指导**
7. **conda环境协同**
8. **Monorepo多包管理**
9. **PEP 723内联脚本**
10. **Workspace原生支持**
11. **uv后端集成**
12. **Docker容器化部署**

---

## 第一章：环境准备

### 1.1 检测当前环境

首先检查系统是否有Python和PDM：

```bash
# 检查Python
python --version
python3 --version
which python python3

# 检查PDM
pdm --version
which pdm

# 检查conda
conda --version
which conda
```

### 1.2 Python安装

#### Linux/macOS 安装Python

```bash
# 方法1: 使用系统包管理器
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# macOS (Homebrew)
brew install python@3.11

# 方法2: 使用pyenv（推荐）
curl https://pyenv.run | bash
# 配置后使用
pyenv install 3.11.8
pyenv global 3.11.8

# 方法3: 使用conda
conda create -n py311 python=3.11 -y
conda activate py311
```

#### Windows 安装Python

```powershell
# 方法1: Microsoft Store（最简单）
# 打开Microsoft Store，搜索"Python 3.11"

# 方法2: 官网下载
# https://www.python.org/downloads/windows/

# 方法3: 使用py launcher（如果安装时勾选了）
py -3.11 --version

# 方法4: winget
winget install Python.Python.3.11
```

#### 验证安装

```bash
python3 --version  # 应显示 Python 3.9+ 或更高版本
```

### 1.3 PDM安装

#### 官方推荐安装方式

```bash
# Linux/macOS
curl -sSL https://pdm-project.org/install-pdm.py | python3 -

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://pdm-project.org/install-pdm.py | py -"

# 验证安装
pdm --version
```

#### 其他安装方式

```bash
# pipx安装（隔离环境）
pipx install pdm

# pip安装（用户级）
pip install --user pdm

# uv安装（超快速）
uv tool install pdm

# Homebrew (macOS)
brew install pdm

# asdf
asdf plugin add pdm && asdf install pdm latest
```

#### 安装参数

```bash
# 指定版本
curl -sSL https://pdm-project.org/install-pdm.py | python3 - --version 2.10.0

# 安装到指定路径
curl -sSL https://pdm-project.org/install-pdm.py | python3 - --path ~/.local

# 卸载
curl -sSL https://pdm-project.org/install-pdm.py | python3 - --remove
```

### 1.4 PDM自升级

```bash
pdm self update
pdm self update --head  # 更新到最新开发版
```

---

## 第二章：Conda环境协同

### 2.1 Conda与PDM的关系

| 工具 | 职责 | 层级 |
|------|------|------|
| **conda** | 环境管理（Python版本、系统包） | 底层 |
| **PDM** | 包管理（Python包、依赖解析） | 上层 |

**推荐用法**: conda管理Python版本，PDM管理项目依赖

### 2.2 使用Conda创建的Python环境

```bash
# 1. 用conda创建Python环境
conda create -n myproject python=3.11 -y
conda activate myproject

# 2. 在该环境中安装PDM
pip install pdm

# 3. 用PDM初始化项目
pdm init

# 4. 后续用PDM管理依赖
pdm add requests flask
```

### 2.3 Conda + PDM 最佳实践

#### 方案A: Conda基础环境 + PDM项目依赖

```bash
# 创建基础conda环境
conda create -n base python=3.11 -y
conda activate base

# 安装PDM（用户级）
pip install --user pdm

# 初始化PDM项目
mkdir myproject && cd myproject
pdm init

# PDM管理所有Python包
pdm add numpy pandas scikit-learn
```

#### 方案B: 每个项目独立Conda环境

```bash
# 为项目创建独立conda环境
conda create -n myproject python=3.11 -y
conda activate myproject

# 安装PDM到该环境
pip install pdm

# 初始化项目
pdm init --python 3.11
```

### 2.4 PDM识别Conda环境

```bash
# PDM会自动检测conda环境
conda activate myenv
pdm info  # 会显示当前使用的Python路径

# 手动指定conda环境的Python
pdm use /home/user/miniconda3/envs/myenv/bin/python
```

### 2.5 环境切换脚本

```toml
# pyproject.toml
[tool.pdm.scripts]
# 激活conda环境后运行
activate-conda = {shell = "conda activate myproject && pdm run start"}
```

### 2.6 常见问题

```bash
# Q: conda环境中的PDM无法识别？
# A: 确保在conda激活状态下安装PDM

conda activate myenv
pip install pdm

# Q: 如何让PDM使用conda的包？
# A: PDM不使用conda包，通过conda安装系统依赖（如CUDA）
```

---

## 第三章：项目初始化

### 3.1 基础初始化

```bash
# 交互式初始化
pdm init

# 非交互式初始化（CLI应用）
pdm init --name my-app --python 3.11 --license MIT

# 从模板创建
pdm init --template flask
```

### 3.2 项目类型选择

| 类型 | 特点 | 适用场景 |
|------|------|----------|
| **库项目** | 有name/version字段，可发布到PyPI | 需要分发的包 |
| **应用项目** | 无name字段，不可发布 | 内部工具、CLI应用 |

### 3.3 Python版本配置

```toml
# pyproject.toml
[project]
requires-python = ">=3.9"
```

**注意事项**：
- `requires-python` 必须覆盖所有依赖项的Python支持范围
- 依赖项 `requires-python` 必须包含项目的 `requires-python` 范围

---

## 第四章：依赖管理

### 4.1 添加依赖

```bash
# 添加生产依赖
pdm add requests
pdm add "flask>=2.0"
pdm add requests[socks]  # 带额外依赖

# 添加开发依赖
pdm add -dG test pytest
pdm add -dG lint "flake8; python_version >= '3.9'"

# 添加本地/VCS依赖
pdm add ./my-package
pdm add "git+https://github.com/user/repo.git@main"
```

### 4.2 版本保存策略

| 策略 | 说明 | 示例 |
|------|------|------|
| `--save-minimum` | 最低版本（默认） | `>=2.21.0` |
| `--save-compatible` | 兼容版本 | `>=2.21.0,<3.0.0` |
| `--save-exact` | 精确版本 | `==2.21.0` |
| `--save-wildcard` | 通配符 | `*` |

### 4.3 更新依赖

```bash
# 更新所有依赖
pdm update

# 更新指定依赖
pdm update requests

# 忽略版本约束更新
pdm update -u requests

# 更新策略
pdm update --update-eager requests  # 递归更新
```

### 4.4 删除依赖

```bash
pdm remove requests
pdm remove -G test pytest
pdm remove -dG lint flake8
```

### 4.5 依赖覆盖

```toml
# pyproject.toml
[tool.pdm.resolution.overrides]
pytz = "2023.3"
requests = ">=2.28.0"
```

---

## 第五章：Monorepo多包项目管理

### 5.1 Monorepo架构设计

```
my-monorepo/
├── pyproject.toml          # 根配置
├── pdm.lock               # 统一锁定文件
├── packages/
│   ├── core/              # 核心包
│   │   ├── pyproject.toml
│   │   └── src/
│   ├── api/               # API包
│   │   ├── pyproject.toml
│   │   └── src/
│   └── cli/               # CLI工具包
│       ├── pyproject.toml
│       └── src/
├── scripts/               # 构建脚本
├── docs/                  # 文档
└── tests/                 # 集成测试
```

### 5.2 根项目配置

```toml
# pyproject.toml (根目录)
[project]
name = "my-monorepo"
version = "0.1.0"
requires-python = ">=3.9"

# 定义所有包的位置
[tool.pdm.resolution]
includes = [
    "packages/core",
    "packages/api",
    "packages/cli",
]

[tool.pdm.scripts]
# 安装所有包（可编辑模式）
install-all = {composite = [
    "pdm install",
    "pdm run --project packages/core install",
    "pdm run --project packages/api install",
    "pdm run --project packages/cli install",
]}

# 清理所有包
clean = {shell = "rm -rf packages/*/__pycache__ packages/*/.venv packages/*/build"}
```

### 5.3 子包配置

#### core/pyproject.toml

```toml
# packages/core/pyproject.toml
[project]
name = "@my-monorepo/core"  # 作用域包名
version = "0.1.0"
description = "Core utilities"
requires-python = ">=3.9"
dependencies = []

[tool.pdm]
distribution = true

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
```

#### api/pyproject.toml

```toml
# packages/api/pyproject.toml
[project]
name = "@my-monorepo/api"
version = "0.1.0"
description = "API service"
requires-python = ">=3.9"
dependencies = [
    "@my-monorepo/core>=0.1.0",
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
]

[tool.pdm]
distribution = true
```

#### cli/pyproject.toml

```toml
# packages/cli/pyproject.toml
[project]
name = "@my-monorepo/cli"
version = "0.1.0"
description = "CLI tool"
requires-python = ">=3.9"
dependencies = [
    "@my-monorepo/core>=0.1.0",
    "click>=8.0.0",
]

[project.scripts]
mycli = "my_monorepo_cli:main"

[tool.pdm]
distribution = true
```

### 5.4 跨包依赖配置

```toml
# packages/api/pyproject.toml
[project]
dependencies = [
    "@my-monorepo/core@ file:///${PROJECT_ROOT}/../core",
    "fastapi>=0.100.0",
]
```

### 5.5 Monorepo常用命令

```bash
# 根目录：安装所有依赖并锁定
pdm lock

# 根目录：在所有包中搜索
pdm run --project packages/core search requests
pdm run --project packages/api add fastapi

# 根目录：更新所有包
pdm update

# 根目录：构建所有包
for pkg in packages/*/; do
    pdm build --project "$pkg" -d dist/
done

# 发布所有包
pdm publish --project packages/core
pdm publish --project packages/api
pdm publish --project packages/cli
```

### 5.6 Monorepo脚本

```toml
# pyproject.toml (根目录)
[tool.pdm.scripts]

# 安装所有包为可编辑模式
bootstrap = {shell = """
    pdm install && \
    pdm run --project packages/core install && \
    pdm run --project packages/api install && \
    pdm run --project packages/cli install
"""}

# 发布所有包到PyPI
publish-all = {composite = ["publish-core", "publish-api", "publish-cli"]}

publish-core = "pdm publish --project packages/core"
publish-api = "pdm publish --project packages/api"
publish-cli = "pdm publish --project packages/cli"

# 格式化所有包
format-all = {shell = """
    pdm run --project packages/core run format && \
    pdm run --project packages/api run format && \
    pdm run --project packages/cli run format
"""}

# 运行所有测试
test-all = {composite = ["test-core", "test-api", "test-cli"]}

test-core = "pdm run --project packages/core run test"
test-api = "pdm run --project packages/api run test"
test-cli = "pdm run --project packages/cli run test"
```

### 5.7 Monorepo + Git

```bash
# .gitignore
__pycache__/
*.py[cod]
*.so
.Python
.venv/
.eggs/
*.egg-info/
dist/
build/
*.egg

# pdm.lock 和 pdm.toml 应该提交
# .pdm-python 不应提交
```

### 5.8 依赖组在Monorepo中的应用

```toml
# packages/api/pyproject.toml
[dependency-groups]
dev = ["pytest", "pytest-cov", "pytest-asyncio"]
lint = ["ruff", "mypy"]
docs = ["mkdocs", "mkdocs-material"]

# 安装开发依赖
pdm install -G dev -G lint
```

---

## 第六章：PEP 723 内联脚本（PDM 2.16+）

### 6.1 什么是PEP 723

PEP 723允许在Python脚本顶部声明依赖，运行时自动创建临时环境：

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "rich>=13.0",
# ]
# ///
"""
数据分析脚本
直接运行：pdm run script.py
"""
import requests
from rich import print

response = requests.get("https://api.github.com")
print(response.json())
```

### 6.2 运行内联脚本

```bash
# PDM自动创建临时环境并运行
pdm run script.py

# 指定额外的依赖
pdm run script.py --with numpy,pandas

# 指定Python版本
pdm run script.py --python 3.11
```

### 6.3 内联脚本元数据

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["flask", "sqlalchemy"]
# sources = ["src/", "lib/"]
# ///
```

| 字段 | 说明 | 示例 |
|------|------|------|
| `requires-python` | Python版本要求 | `>=3.11` |
| `dependencies` | 依赖列表 | `["requests"]` |
| `sources` | 额外源码目录 | `["src/"]` |
| `dev-dependencies` | 开发依赖 | `["pytest"]` |

### 6.4 实际应用场景

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx", "rich", "pydantic"]
# ///
"""API测试脚本"""
import httpx
from rich.console import Console
from pydantic import BaseModel

console = Console()

class User(BaseModel):
    name: str
    email: str

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://jsonplaceholder.typicode.com/users/1")
        user = User.model_validate(response.json())
        console.print(f"[green]Name:[/green] {user.name}")
        console.print(f"[blue]Email:[/blue] {user.email}")

import asyncio
asyncio.run(main())
```

---

## 第七章：Workspace原生支持（PDM 2.15+）

### 7.1 Workspace vs 传统Monorepo

| 特性 | 传统方式 | Workspace原生 |
|------|---------|---------------|
| 依赖解析 | 手动配置includes | 自动发现子包 |
| 跨包引用 | file://路径 | 原生支持 |
| 锁定文件 | 手动同步 | 统一管理 |

### 7.2 Workspace配置

```toml
# pyproject.toml (根目录)
[tool.pdm.workspace]
packages = [
    {path = "packages/core"},
    {path = "packages/api"},
    {path = "packages/cli"},
]
```

### 7.3 子包Workspace配置

```toml
# packages/api/pyproject.toml
[project]
name = "@my-monorepo/api"
version = "0.1.0"
dependencies = [
    "@my-monorepo/core",  # 直接引用，无需file://
]

[tool.pdm]
is-initializer = false  # 非workspace根
```

### 7.4 Workspace命令

```bash
# 查看所有包
pdm workspace list

# 查看依赖关系
pdm workspace list --graph

# 构建所有包
pdm build --all

# 发布所有包
pdm publish --all
```

### 7.5 Workspace + CI/CD

```yaml
# .github/workflows/release.yml
- name: Build and publish
  run: |
    pdm install
    pdm workspace list --graph
    pdm publish --all
```

---

## 第八章：uv后端集成（PDM 2.19+ 实验性）

### 8.1 为什么使用uv

uv是Rust编写的高速包解析器，比传统pip快10-100倍。

### 8.2 启用uv后端

```bash
# 安装uv
pip install uv

# 使用uv作为后端（实验性）
pdm lock --backend uv

# 或在配置中启用
[tool.pdm.resolution]
backend = "uv"
```

### 8.3 uv后端限制

```toml
# 目前不支持的功能
# 1. VCS依赖需要配置
# 2. 某些特殊索引

[tool.pdm.resolution]
backend = "uv"
```

### 8.4 性能对比

| 操作 | pip | uv |
|------|-----|-----|
| 锁定依赖 | 30s | 1s |
| 安装依赖 | 60s | 3s |
| 增量更新 | 15s | 0.5s |

---

## 第九章：Docker容器化部署

### 9.1 基础镜像选择

| 镜像 | 特点 | 适用场景 |
|------|------|----------|
| `python:3.11-slim` | 体积小(~150MB) | 生产环境推荐 |
| `python:3.11-alpine` | 最小(~50MB) | 极致精简 |
| `python:3.11` | 完整镜像 | 需要系统依赖 |

### 9.2 多阶段构建（推荐）

```dockerfile
# Stage 1: 构建阶段
FROM python:3.11-slim as builder

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装PDM
RUN pip install pdm

WORKDIR /app

# 复制配置文件
COPY pyproject.toml pdm.lock ./

# 构建依赖（只安装，不复制源码）
RUN pdm install --prod --no-editable --python /app/.venv/bin/python

# Stage 2: 运行阶段
FROM python:3.11-slim as runner

# 只复制虚拟环境和源码
COPY --from=builder /app/.venv /app/.venv
COPY . .

# 设置环境
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# 运行应用
CMD ["pdm", "run", "start"]
```

### 9.3 非Root用户运行

```dockerfile
FROM python:3.11-slim

RUN pip install pdm

WORKDIR /app

# 创建非root用户
RUN useradd --create-home appuser
COPY --chown=appuser:appuser pyproject.toml pdm.lock ./

# 安装依赖
USER appuser
RUN pdm install --prod --python /home/appuser/.local/share/pdm/python/cpython-3.11.5-linux-x86_64-gnu/bin/python3

ENV PATH="/home/appuser/.local/share/pdm/python/cpython-3.11.5-linux-x86_64-gnu/bin:$PATH"
CMD ["pdm", "run", "start"]
```

### 9.4 Docker Compose集成

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - .:/app
    environment:
      - PDM_SKIP_SELF=1
    command: pdm run dev

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
```

### 9.5 Docker最佳实践

```dockerfile
# 1. 使用特定版本，避免latest
FROM python:3.11.5-slim

# 2. 利用构建缓存
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# 3. 使用.pdm-python固定Python版本
COPY .pdm-python /app/.pdm-python

# 4. 清理缓存
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
```

---

## 第十章：平台特定锁定

### 10.1 多平台配置

```toml
# pyproject.toml
[tool.pdm.resolution]
targets = [
    "x86_64-linux-gnu",
    "aarch64-linux-gnu",
    "x86_64-apple-darwin",
    "x86_64-pc-windows-msvc",
]
```

### 10.2 条件依赖

```toml
[project]
dependencies = [
    "numpy>=1.24; platform_system == 'Windows'",
    "pyobjc-framework-Cocoa>=9.0; platform_system == 'Darwin'",
]
```

---

## 第十一章：安全扫描

### 11.1 依赖漏洞检查

```bash
# 安装安全工具
pdm add -dG security pip-audit safety

# 运行扫描
pdm run pip-audit
pdm run safety check
```

### 11.2 GitHub Actions集成

```yaml
- name: Security audit
  run: |
    pip install pip-audit
    pip-audit --strict
```

---

## 第十二章：配置文件结构

### 12.1 pyproject.toml 基础结构

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "A short description"
requires-python = ">=3.9"
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0.0", "black"]
doc = ["mkdocs"]

[dependency-groups]
lint = ["flake8", "mypy"]

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"

[tool.pdm.distribution]
package = true

[tool.pdm.scripts]
start = "flask run"
test = "pytest"
```

### 12.2 pdm.toml 配置

```toml
[python]
path = ".venv/bin/python"

[mirror]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

---

## 第十三章：PDM脚本

### 13.1 脚本类型

```toml
[tool.pdm.scripts]
# 命令脚本
start = {cmd = "flask run -p 5000"}

# Shell脚本（支持管道）
filter = {shell = "cat error.log | grep ERROR"}

# Python函数调用
main = {call = "my_package:main"}

# 组合脚本
dev = {composite = ["start", "test"]}
```

### 13.2 脚本选项

```toml
[tool.pdm.scripts]
start.cmd = "flask run"
start.env = {FLASK_ENV = "development"}
start.env_file = ".env"
start.working_dir = "src"
```

### 13.3 钩子脚本

```toml
[tool.pdm.scripts]
pre_install = "echo 'Installing...'"
post_install = "echo 'Done!'"
pre_build = "echo 'Building...'"
post_publish = "echo 'Published!'"
```

---

## 第十四章：常用命令速查

| 命令 | 说明 |
|------|------|
| `pdm init` | 初始化项目 |
| `pdm add <pkg>` | 添加依赖 |
| `pdm remove <pkg>` | 删除依赖 |
| `pdm update` | 更新依赖 |
| `pdm install` | 安装依赖 |
| `pdm lock` | 生成/更新锁定文件 |
| `pdm sync` | 同步工作集 |
| `pdm run <script>` | 运行脚本 |
| `pdm build` | 构建分发包 |
| `pdm publish` | 发布到PyPI |
| `pdm list` | 列出依赖 |
| `pdm outdated` | 检查过时依赖 |
| `pdm info` | 显示项目信息 |
| `pdm python install <ver>` | 安装Python版本 |
| `pdm self update` | 更新PDM |
| `pdm workspace list` | 列出workspace包 |
| `pdm run script.py` | 运行PEP 723脚本 |

---

## 第十五章：虚拟环境管理

```bash
# 创建虚拟环境
pdm venv create

# 列出虚拟环境
pdm venv list

# 激活虚拟环境
eval $(pdm venv activate)

# 删除虚拟环境
pdm venv remove
```

---

## 第十六章：从其他工具迁移

### 16.1 从requirements.txt迁移

```bash
pdm import requirements.txt
```

### 16.2 从Pipfile迁移

```bash
pdm import Pipfile
```

### 16.3 从Poetry迁移

Poetry的`pyproject.toml`部分可直接被PDM读取。

---

## 第十七章：CI/CD集成

### 17.1 GitHub Actions

```yaml
- uses: pdm-project/setup-pdm@v4
  with:
    python-version: '3.11'
- name: Install dependencies
  run: pdm install
- name: Run tests
  run: pdm run test
```

### 17.2 发布配置

```yaml
- name: Publish to PyPI
  run: pdm publish
  env:
    PDM_PUBLISH_REPO: pypi
    PDM_PUBLISH_USERNAME: __token__
    PDM_PUBLISH_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

### 17.3 GitLab CI

```yaml
# .gitlab-ci.yml
image: python:3.11-slim

before_script:
  - pip install pdm
  - pdm use 3.11

test:
  script:
    - pdm install
    - pdm run test

publish:
  script:
    - pdm build
    - pdm publish
  only:
    - tags
```

---

## 第十八章：常见问题诊断

### 18.1 Resolution Impossible

```
Resolution Impossible: The project's requires-python doesn't allow all dependencies
```

**解决**：调整`requires-python`范围，确保覆盖所有依赖项的Python要求。

### 18.2 包版本冲突

**解决**：使用依赖覆盖
```toml
[tool.pdm.resolution.overrides]
problematic-package = ">=1.0.0"
```

### 18.3 构建后端问题

确保`build-system`配置正确：
```toml
[build-system]
requires = ["pdm-backend>=2.0.0"]
build-backend = "pdm.backend"
```

### 18.4 Python/PDM未安装

**解决**：参考第一章环境准备部分进行安装

### 18.5 Conda环境问题

```bash
# Q: PDM无法找到conda的Python
# A: 确保conda环境已激活

conda activate myenv
pdm use python  # 让PDM检测当前Python

# 或手动指定
pdm use /path/to/conda/envs/myenv/bin/python
```

### 18.6 uv后端兼容性问题

```bash
# Q: 使用uv后端后某些依赖安装失败
# A: 降级到标准后端

pdm lock --backend pdm
```

---

## 第十九章：最佳实践

1. **始终提交`pdm.lock`** - 确保团队使用相同依赖版本
2. **合理设置`requires-python`** - 避免不必要的版本限制
3. **使用依赖组** - 分离生产/开发依赖
4. **启用脚本钩子** - 自动化重复任务
5. **配置包索引** - 企业使用私有源提升速度
6. **Monorepo结构清晰** - 使用workspace原生支持
7. **conda + PDM协同** - conda管理Python环境，PDM管理依赖
8. **PEP 723内联脚本** - 快速原型开发和数据分析
9. **Docker多阶段构建** - 生产镜像更小更安全
10. **定期安全扫描** - 使用pip-audit检查漏洞
11. **使用uv后端** - 加速CI/CD构建

---

## 参考文档

- [PDM官方文档](https://pdm-project.org/zh-cn/latest/)
- [CLI命令参考](references/cli_reference.md) - 完整命令列表
- [配置参考](references/config_reference.md) - 详细配置项
- [插件开发](references/plugin_development.md) - 开发PDM插件指南