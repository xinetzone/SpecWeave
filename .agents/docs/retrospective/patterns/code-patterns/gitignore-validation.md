---
id: "gitignore-validation"
source: "external: 不存在-docs/retrospective/knowledge-extraction.md + retro-20260702-frontmatter-migration实践（.coverage治理案例）"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/gitignore-validation.toml"
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

### 新工具引入检查清单（强制Checklist）

引入新工具/脚本/依赖时，**必须逐项确认并执行**，不能事后补漏：

- [ ] **识别产出物类型**：运行一次工具/测试，观察`git status`出现了哪些新的未跟踪文件
- [ ] **缓存目录**：如`.pytest_cache/`、`__pycache__/`、`.mypy_cache/`、`.ruff_cache/`等，加入`.gitignore`
- [ ] **测试/覆盖率报告**：如`.coverage`、`htmlcov/`、`.coverage.*`、`coverage.xml`等
- [ ] **构建/打包产物**：如`dist/`、`build/`、`*.egg-info/`、`*.whl`
- [ ] **临时文件/日志**：如`*.log`、`*.tmp`、工具特定的临时输出
- [ ] **环境/IDE文件**：如`.env`、`.venv/`、`.idea/`、`.vscode/`（仅忽略用户特定配置）
- [ ] **运行验证**：执行`python .agents/scripts/check-gitignore.py`验证规则完整性
- [ ] **文档记录**：在工具文档或脚本注释中注明产出物路径

> **为什么？** 本项目在2026-07-02的frontmatter治理复盘中，先后3次遗漏工具产出物的.gitignore配置（.coverage、htmlcov/、.pytest_cache/），每次都是在文件污染工作区后才发现补全。根本原因是缺少"新增工具→检查产出物→更新.gitignore"的强制检查环节。

### 案例：.pytest_cache/遗漏与批量补全（2026-07-02 Frontmatter治理复盘）

**问题**：运行`check-spec-adoption.py`的测试时，pytest自动创建`.pytest_cache/`目录存储缓存数据，该目录未被`.gitignore`覆盖，导致工作区被污染。

**发现过程**：
1. 运行pytest后，`git status`显示`.pytest_cache/`为未跟踪目录
2. 检查发现`.gitignore`中有`__pycache__/`但遗漏了`.pytest_cache/`
3. 同时遗漏的还有`.coverage`（pytest-cov）和`htmlcov/`（coverage html）

**修复**：
1. 在`.gitignore`中补充`.pytest_cache/`规则
2. 清理已生成的缓存目录
3. 增强"新工具引入Checklist"（即上文的8项检查清单）
4. 将此案例写入模式文档

**教训**：即使是Python生态的标准工具（pytest），其产出物也不会自动被忽略——不能假设"常用工具的产出物大家都知道要加"，必须通过Checklist强制检查。

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
