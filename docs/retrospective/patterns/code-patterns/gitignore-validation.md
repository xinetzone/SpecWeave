---
id: "gitignore-validation"
source: "docs/retrospective/knowledge-extraction.md + retro-20260702-frontmatter-migration实践（.coverage治理案例）"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/gitignore-validation.toml"
---
# Git忽略规则验证与工具产出物同步治理

## 模式概述

建立项目级的`.gitignore`必需规则验证机制，同时遵循"新工具引入新产出物时必须同步更新忽略规则"的原则——新增脚本、工具、测试框架时，必须将其产生的临时文件、缓存文件、构建产物同步加入`.gitignore`，避免工作区被无关文件污染。

## 问题现象

项目在引入新工具或脚本后，经常出现工作区污染问题：

1. **遗漏基础忽略规则**：新项目或重构后忘记添加`__pycache__/`、`*.pyc`、`.env`等基础规则
2. **工具产出物无治理**：引入pytest后产生`.coverage`、`htmlcov/`，没有及时加入`.gitignore`，导致测试覆盖率二进制文件被意外提交
3. **临时文件堆积**：脚本运行产生的`.tmp`、`.log`、临时输出文件散落在工作区
4. **环境差异文件**：不同操作系统/IDE产生的`.DS_Store`、`Thumbs.db`、`.idea/`、`.vscode/`等没有统一忽略
5. **CI/CD构建产物**：构建输出目录`dist/`、`build/`、`*.egg-info/`遗漏导致仓库膨胀

## 解决方案

### 核心原则：工具产出物同步治理

> **引入新类型的工具/脚本时，必须同步完成三件事**：
> 1. 在脚本文档中注明该工具会产生哪些临时文件/产出物
> 2. 将这些产出物的路径模式加入`.gitignore`
> 3. 运行一次`check-gitignore.py`验证规则完整性

### 基础必需忽略规则（Python项目）

```python
REQUIRED_RULES = [
    # Python 缓存与编译
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    # 虚拟环境
    ".venv/",
    "venv/",
    "env/",
    # 测试与覆盖率
    ".coverage",
    "htmlcov/",
    ".pytest_cache/",
    ".tox/",
    # 环境变量与密钥
    ".env",
    ".env.local",
    "*.key",
    "*.pem",
    # 构建与打包
    "dist/",
    "build/",
    "*.egg-info/",
    "*.egg",
    # IDE 与编辑器
    ".idea/",
    ".vscode/",
    "*.swp",
    "*.swo",
    "*~",
    # 操作系统
    ".DS_Store",
    "Thumbs.db",
    "Desktop.ini",
    # 日志
    "*.log",
    # 项目特定
    "vendor/",
    ".temp/",
    "node_modules/",
]
```

### 验证脚本核心实现

```python
def check_gitignore_rules(gitignore_path: Path) -> list[str]:
    """检查 .gitignore 是否包含所有必需规则。"""
    content = gitignore_path.read_text(encoding="utf-8")
    missing = []
    for rule in REQUIRED_RULES:
        if rule not in content:
            missing.append(rule)
    return missing
```

### 新工具引入检查清单

引入新工具/脚本时，逐项检查：

| 检查项 | 操作 |
|--------|------|
| 是否产生缓存文件？ | 将缓存目录加入.gitignore |
| 是否产生测试/覆盖率报告？ | 加入报告文件/目录 |
| 是否产生临时文件？ | 加入临时文件模式 |
| 是否有环境配置文件？ | 加入配置文件模板但忽略实际配置 |
| 是否有构建产物？ | 加入构建输出目录 |

## 实际案例

### 案例：pytest覆盖率文件治理（Frontmatter迁移复盘）

**问题**：开发`check-frontmatter.py`等脚本并运行测试时，产生了`.agents/scripts/.coverage`二进制覆盖率文件，该文件未被`.gitignore`覆盖，可能被意外提交。

**应用模式**：
1. 识别新产出物类型：`.coverage`（覆盖率数据）、`htmlcov/`（HTML覆盖率报告）
2. 在`.gitignore`的Python缓存部分添加这两个规则
3. 将"工具产出物需同步纳入治理"的经验写入脚本文档
4. 运行验证脚本确认规则生效

**修正后的.gitignore片段**：
```gitignore
# Python 缓存
__pycache__/
*.pyc
.pytest_cache/

# 测试覆盖率
.coverage
htmlcov/
```

## 反模式

### 反模式1：先开发后补忽略规则

```
完成：开发了新脚本并运行测试
（发现.coverage出现在git status中才想起来加.gitignore）
```

**为什么错**：
- 容易在"忘记加"的窗口期误提交临时文件
- 多次提交历史中出现垃圾文件，污染仓库
- 团队其他成员pull后工作区也被污染

**正确做法**：引入工具的同时就更新.gitignore，将其作为工具引入的必要步骤。

### 反模式2：过度宽泛的忽略规则

```gitignore
# ❌ 反模式：过于宽泛，可能忽略需要提交的文件
*.md
*.json
temp/
```

**为什么错**：过度宽泛的规则会忽略应该纳入版本控制的文件（如文档、配置文件）。

**正确做法**：精确匹配产出物路径，优先使用目录后缀`/`明确指定目录。

## 与其他模式的关系

| 相关模式 | 关系 | 说明 |
|---------|------|------|
| spec-triple-sync | 思想同源 | 新规范发布要三同步，新工具引入也要"产出物同步治理" |
| tool-self-validation | 配套 | 新工具提交前需要自验证，.gitignore检查是自验证的一部分 |
| large-scale-duplication-elimination | 前置保障 | 重复代码检测前必须确保忽略规则正确，避免扫描无关文件 |

## 边界与选型

### 什么时候必须更新.gitignore？

满足以下任一条件时必须同步更新：
1. 新增项目依赖（引入新框架/工具）
2. 新增脚本会产生持久化的临时/缓存文件
3. 运行测试/构建后`git status`出现未跟踪的新类型文件
4. CI/CD流水线中出现新的产出物目录

### 哪些文件不应该忽略？

- ✅ 应提交：配置模板（`.env.example`）、脚本本身、文档、源代码
- ❌ 不忽略示例：`*.example`、`*.template`、`*.sample`这类模板文件不应被忽略
- ✅ 应忽略：实际运行产生的数据、缓存、密钥、构建产物

> **经验法则**：如果文件是"人写的"或"版本化的配置"，应该提交；如果是"工具生成的"或"环境特定的"，应该忽略。
