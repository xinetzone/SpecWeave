+++
id = "standardize-file-naming-convention"
domain = "development-standards"
layer = "convention"
maturity = "L1"
validation_count = 0
reuse_count = 0
documentation_level = "standard"
source = "用户需求：解决中英文混合命名问题"
+++

# 文件命名规范（File Naming Convention）

## 问题背景

当前项目 `docs/retrospective/patterns/` 目录下存在中英文混合命名的文件，例如 `report-as-tracking载体.md`，这种命名方式导致：
- 跨平台兼容性问题（中文字符在某些环境下可能导致路径解析错误）
- 搜索和排序行为不一致
- 规范不一致影响项目整体专业性

## 规范要求

### 1. 语言要求

| 文件位置 | 语言要求 | 示例 |
|---------|---------|------|
| 文档文件 (.md) | 统一使用英文 | `report-as-tracking.md` |
| 代码文件 (.py/.js/.ts 等) | 统一使用英文 | `file_operations.py` |
| 配置文件 (.yaml/.json/.toml 等) | 统一使用英文 | `config.yaml` |

**禁止**：在单一文件名中混合使用中英文。

### 2. 允许使用的字符

- **英文字母**：a-z, A-Z
- **数字**：0-9（但不能作为文件名的首个字符）
- **连接符**：
  - 连字符 `-`（推荐用于语义分隔）
  - 下划线 `_`（适用于需要强调单词边界时）
- **点号**：`.`（仅用于分隔文件名与扩展名）

### 3. 命名格式

| 类型 | 格式 | 示例 |
|-----|------|------|
| 语义描述型 | `kebab-case`（全小写 + 连字符） | `report-as-tracking.md` |
| 编号型 | `序号-描述` | `01-introduction.md` |
| 技术型 | `snake_case` 或 `camelCase` | `file_operations.py`, `getUser.js` |

**说明**：文档文件推荐使用 `kebab-case`，代码文件可使用 `snake_case` 或 `camelCase`。

### 4. 特殊字符限制

禁止在文件名中使用：
- 空格 ` `
- 中文及其他非 ASCII 字符
- 特殊符号：`!@#$%^&*()+={}[]|\\:;"'<>,?/~`
- 连续连接符：`--`（两个或以上连字符）

### 5. 长度限制

- 文件名最长不超过 128 个字符
- 路径总长度不超过 260 个字符（Windows 限制）

### 6. 保留名称

以下名称不能作为文件名：
- `CON`, `PRN`, `AUX`, `NUL`
- `COM1`-`COM9`, `LPT1`-`LPT9`
- `desktop.ini`（Windows 系统特殊文件）

## 现有问题修复

### 需要重命名的文件

| 当前文件名 | 规范文件名 |
|-----------|-----------|
| `report-as-tracking载体.md` | `report-as-tracking.md` |

## 审核机制

### 预提交检查

在 Git 提交前，应检查新增或重命名的文件是否符合本规范：
- 使用 `lint-staged` 或类似工具进行自动检查
- 或在 `.git/hooks/pre-commit` 中嵌入检查脚本

### CI 检查

在持续集成流程中加入命名规范检查：
- 使用正则表达式验证文件名模式
- 检查是否存在非 ASCII 字符

### 人工审查

代码审查时，应将文件名规范作为审查项之一。

## 影响范围

- **受影响目录**：`docs/retrospective/patterns/`
- **新增规范**：`.agents/rules/file-naming-convention.md`（如尚不存在）
- **相关工具**：Git hooks、CI 流水线、linting 配置

## 实施计划

1. 创建文件命名规范文档
2. 重命名现有违规文件
3. 配置预提交钩子或 CI 检查
4. 更新相关索引和引用
