---
id: veadk-python-installation
title: 安装指南
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- 火山引擎
- AI Agent
- 安装
- 环境配置
- Python
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: VeADK-Python 安装指南，涵盖系统要求、PyPI安装、uv安装、源码构建、验证安装及常见问题
wiki_version: '1.0'
---


# VeADK-Python 安装指南

本文档介绍如何在不同环境下安装和配置 VeADK-Python 开发框架。

---

## 系统要求

### Python 版本

VeADK-Python 要求 **Python 3.10 或更高版本**。

- 最低支持版本：Python 3.10
- 推荐版本：Python 3.12（uv 安装示例使用 Python 3.12）

版本约束定义在 [file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L10-L10](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L10-L10)：

```toml
requires-python = ">=3.10"
```

### 操作系统

VeADK-Python 支持以下操作系统：

- **Windows**：Windows 10/11，推荐使用 WSL2 或 PowerShell
- **macOS**：macOS 11 (Big Sur) 及以上版本
- **Linux**：Ubuntu 20.04+、CentOS 8+ 等主流 Linux 发行版

### 可选系统依赖

某些功能可能需要系统级依赖：

- **PostgreSQL 支持**：需要安装 `libpq-dev`（Linux）或使用预编译的 `psycopg2-binary`
- **MySQL 支持**：需要安装 MySQL 客户端库（可选，默认使用纯 Python 实现）
- **Milvus 向量数据库**：如需使用 Milvus 后端，需要运行 Milvus 服务或使用 Milvus Lite

---

## 安装方式

### 方式一：PyPI 安装（推荐）

使用 pip 从 PyPI 安装最新稳定版本。

#### 基础安装

安装核心功能包（包含 Agent、Runner、短期记忆、基础工具等）：

```bash
pip install veadk-python
```

包名定义在 [file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L6-L6](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L6-L6)。

#### 安装扩展功能

安装包含所有可选扩展的完整版本（推荐用于生产环境）：

```bash
pip install "veadk-python[extensions]"
```

`extensions` 额外依赖包含（[file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L65-L78](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L65-L78)）：
- Redis 数据库支持
- Cozeloop Prompt 管理器
- LlamaIndex（知识库和长期记忆）
- OpenSearch/Milvus 向量数据库
- 飞书渠道集成

#### 按功能模块安装

VeADK 提供多个可选依赖分组，可根据需要选择安装：

```bash
# 数据库支持（Redis、MySQL、Mem0 等）
pip install "veadk-python[database]"

# A2UI 智能体驱动 UI
pip install "veadk-python[a2ui]"

# 评估功能（DeepEval、Prometheus）
pip install "veadk-python[eval]"

# Codex 运行时支持
pip install "veadk-python[codex]"

# 开发工具（pre-commit、pytest 等）
pip install "veadk-python[dev]"

# Harness 扩展
pip install "veadk-python[harness]"
```

可选依赖完整列表参见 [file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L60-L104](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L60-L104)。

---

### 方式二：使用 uv 安装

VeADK 项目推荐使用 `uv` 作为 Python 包管理器（[file:///d:/AI/.chaos/libs/veadk-python/README.md#L29-L29](file:///d:/AI/.chaos/libs/veadk-python/README.md#L29-L29)）。uv 是一个极速的 Python 包管理器和虚拟环境工具。

#### 安装 uv

首先安装 uv（如尚未安装）：

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

更多安装方式参见 [uv 官方安装文档](https://docs.astral.sh/uv/getting-started/installation/)。

#### 使用 uv 创建项目并安装 VeADK

```bash
# 创建新项目目录
mkdir my-veadk-project
cd my-veadk-project

# 使用 Python 3.12 创建虚拟环境
uv venv --python 3.12

# 激活虚拟环境
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# 安装 VeADK
uv pip install veadk-python

# 或安装带扩展的完整版本
uv pip install "veadk-python[extensions]"
```

---

### 方式三：从源码构建安装

如需使用最新开发版本或参与贡献，可以从源码构建安装。

完整源码构建流程参见 [file:///d:/AI/.chaos/libs/veadk-python/README.md#L27-L52](file:///d:/AI/.chaos/libs/veadk-python/README.md#L27-L52)。

```bash
# 克隆仓库
git clone https://github.com/volcengine/veadk-python.git
cd veadk-python

# 使用 uv 创建虚拟环境（Python 3.12）
uv venv --python 3.12

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或 .venv\Scripts\Activate.ps1  # Windows PowerShell
# 或 .venv\Scripts\activate.bat  # Windows CMD

# 安装核心依赖
uv sync

# 安装额外依赖（可选）
# uv sync --extra database    # 数据库扩展
# uv sync --extra eval        # 评估扩展
# uv sync --extra cli         # CLI 扩展
# uv sync --all-extras        # 安装所有可选依赖

# 以可编辑模式安装 veadk-python
uv pip install -e .
```

源码构建使用 setuptools 和 setuptools-scm（[file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L1-L3](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L1-L3)），版本号从 git tag 自动推导。

---

## 验证安装

安装完成后，可以通过以下方式验证安装是否成功。

### 方式一：Python 导入测试

在 Python 交互式环境中执行导入测试：

```python
import veadk

# 查看版本号
print(f"VeADK 版本: {veadk.VERSION}")

# 验证核心类可正常导入
from veadk import Agent, Runner
print("Agent 和 Runner 导入成功")
```

VeADK 采用懒加载机制，`Agent` 和 `Runner` 在首次访问时从对应模块导入（[file:///d:/AI/.chaos/libs/veadk-python/veadk/__init__.py#L24-L34](file:///d:/AI/.chaos/libs/veadk-python/veadk/__init__.py#L24-L34)）。

### 方式二：命令行工具验证

VeADK 安装后提供 `veadk` 命令行工具（[file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L57-L58](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L57-L58)）：

```bash
veadk --help
```

如果显示命令帮助信息，说明 CLI 工具安装成功。

### 方式三：运行最小示例

创建 `test_install.py` 文件，运行最小化的 Agent 对话测试：

```python
import asyncio
from veadk import Agent, Runner

async def main():
    agent = Agent(
        name="test_agent",
        instruction="你是一个测试助手，请用一句话回复。"
    )
    runner = Runner(agent=agent, app_name="test")
    answer = await runner.run(messages="你好，请介绍一下自己。", session_id="test-session")
    print(f"Agent 回复: {answer}")

if __name__ == "__main__":
    asyncio.run(main())
```

> **注意**：运行此示例需要先配置 API Key，请参考 [配置指南](configuration.md) 完成配置后再测试。

---

## 核心依赖说明

VeADK 核心依赖包含 34 个直接依赖项（[file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L18-L55](file:///d:/AI/.chaos/libs/veadk-python/pyproject.toml#L18-L55)），主要依赖包括：

| 依赖包 | 版本约束 | 用途 |
|--------|----------|------|
| google-adk | >=1.34.0 | Google Agent Development Kit，基础 Agent 架构 |
| litellm | >=1.83.7 | 统一大模型调用接口 |
| sqlalchemy | >=2,<3 | 数据库 ORM，会话存储 |
| pydantic-settings | ==2.10.1 | 配置管理 |
| python-dotenv | >=1.1.0 | .env 文件加载 |
| volcengine-python-sdk | >=5.0.36 | 火山引擎云服务 SDK |
| volcengine | >=1.0.193 | 火山引擎签名和 AgentKit API |
| fastmcp | >=2.12.3 | MCP 协议支持 |
| opentelemetry-exporter-otlp | ==1.37.0 | OpenTelemetry 链路追踪 |
| psycopg2-binary | >=2.9.10 | PostgreSQL 数据库驱动 |
| asyncpg | >=0.29.0 | 异步 PostgreSQL 驱动 |
| pymysql | ==1.1.1 | MySQL 数据库驱动 |
| aiomysql | ==0.3.2 | 异步 MySQL 驱动 |
| vikingdb-python-sdk | >=0.1.3 | 火山引擎 VikingDB 向量数据库 |
| openviking-sdk | >=0.1.3 | OpenViking 知识库和记忆 |
| agentkit-sdk-python | >=0.8.0 | AgentKit SDK |
| tos | >=2.8.4 | 火山引擎 TOS 对象存储 |

完整依赖清单参见 [supporting-analysis/03-dependencies.md](../supporting-analysis/03-dependencies.md)。

---

## 常见安装问题

### 问题 1：Python 版本不兼容

**症状**：安装时出现 `ERROR: Package 'veadk-python' requires a different Python` 错误。

**解决方案**：
- 检查 Python 版本：`python --version` 或 `python3 --version`
- 确保 Python 版本 >= 3.10
- 推荐使用 pyenv、conda 或 uv 管理 Python 版本
- 使用 uv 时可通过 `uv venv --python 3.12` 指定 Python 版本

### 问题 2：psycopg2 安装失败

**症状**：在 Linux 环境下安装时，psycopg2 编译失败。

**原因**：VeADK 使用 `psycopg2-binary`（预编译版本），通常不会出现编译问题。如果系统强制从源码编译，可能缺少 libpq 开发库。

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev

# CentOS/RHEL
sudo yum install postgresql-devel python3-devel

# macOS
brew install postgresql
```

或直接重新安装预编译版本：
```bash
pip install --force-reinstall psycopg2-binary
```

### 问题 3：依赖冲突

**症状**：安装时出现依赖版本冲突错误，如 `ResolutionImpossible`。

**解决方案**：
- 推荐使用 uv 进行依赖解析，uv 的依赖解析器比 pip 更快更准确
- 使用虚拟环境隔离项目依赖，避免全局包污染
- 如遇到特定包冲突，可尝试升级 pip：`pip install --upgrade pip`

```bash
# 使用 uv 创建干净的虚拟环境
uv venv --python 3.12
source .venv/bin/activate
uv pip install veadk-python
```

### 问题 4：网络超时或下载慢

**症状**：安装过程中下载包超时或速度很慢。

**解决方案**：使用国内 PyPI 镜像源：

```bash
# 临时使用清华镜像
pip install veadk-python -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或永久配置镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

uv 配置镜像源：
```bash
uv pip install veadk-python --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 5：Windows 上 uv 激活脚本执行策略问题

**症状**：在 PowerShell 中执行 `.venv\Scripts\activate` 时提示"无法加载文件，因为在此系统上禁止运行脚本"。

**解决方案**：以管理员身份打开 PowerShell，执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

然后重新激活虚拟环境。

### 问题 6：import veadk 时出现 ModuleNotFoundError

**症状**：安装成功后，在 Python 中 `import veadk` 提示找不到模块。

**可能原因**：
1. 使用了不同的 Python 环境
2. 虚拟环境未激活
3. 安装到了用户目录但 Python 路径未包含

**排查步骤**：
```bash
# 检查当前使用的 Python 路径
which python  # macOS/Linux
where python  # Windows

# 检查 pip 安装路径
which pip
pip show veadk-python

# 确认在正确的虚拟环境中
# 激活虚拟环境后再检查
```

---

## 安装后下一步

安装完成后，建议继续阅读：

1. [配置指南](configuration.md) - 配置 API Key 和其他必要参数
2. [快速入门](quickstart.md) - 5 分钟创建你的第一个 Agent
3. [examples/01_quickstart/](file:///d:/AI/.chaos/libs/veadk-python/examples/01_quickstart/) 目录查看官方示例代码

---

> **版本说明**：本文档基于 VeADK-Python 代码库分析生成，对应 Wiki 版本 1.0。如发现文档内容与实际代码不符，请参考源代码为准。
