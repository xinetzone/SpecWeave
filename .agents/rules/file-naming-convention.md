+++
id = "file-naming-convention"
domain = "development-standards"
layer = "convention"
maturity = "L1"
validation_count = 0
reuse_count = 0
documentation_level = "standard"
source = "spec:standardize-file-naming-convention"
+++

# 文件命名规范（File Naming Convention）

## 目的

确保项目中所有文件名遵循统一的命名规范，避免跨平台兼容性问题，提升搜索和排序的一致性，并维护项目的整体专业性。

## 适用范围

项目内所有文件（文档、代码、配置文件等），包括但不限于：
- `docs/` 目录下的所有文档文件
- `.agents/` 目录下的所有配置和定义文件
- `scripts/` 目录下的所有脚本文件
- 项目根目录及其他子目录中的所有文件

## 语言要求

| 文件类型 | 语言要求 | 示例 |
|---------|---------|------|
| 文档文件 (.md) | 统一使用英文 | `report-as-tracking.md` |
| 代码文件 (.py/.js/.ts 等) | 统一使用英文 | `file_operations.py` |
| 配置文件 (.yaml/.json/.toml 等) | 统一使用英文 | `config.yaml` |

**强制要求**：禁止在单一文件名中混合使用中英文。

## 允许使用的字符

- **英文字母**：a-z, A-Z（全小写或全大写）
- **数字**：0-9（但不能作为文件名的首个字符）
- **连接符**：
  - 连字符 `-`（推荐用于语义分隔，推荐使用 kebab-case）
  - 下划线 `_`（适用于需要强调单词边界时）
- **点号**：`.`（仅用于分隔文件名与扩展名）

## 命名格式

### 文档文件

使用 `kebab-case`（全小写 + 连字符分隔）：

```
kebab-case-example.md
multi-level-nesting-example.md
```

### 代码文件

根据编程语言惯例选择：
- Python: `snake_case.py`
- JavaScript/TypeScript: `camelCase.js` 或 `snake_case.js`
- Go: `snake_case.go`

### 配置文件

使用 `kebab-case` 或 `snake_case`：
```
config.yaml
pipeline-config.yaml
```

### 编号型文件

使用 `序号-描述` 格式（序号使用两位数字）：
```
01-introduction.md
02-installation.md
```

## 特殊字符限制

禁止在文件名中使用：

| 类别 | 字符 |
|-----|------|
| 空格 | ` ` |
| 中文 | 任何中文字符 |
| 其他非 ASCII 字符 | 俄文、日文、韩文等 |
| 特殊符号 | `!@#$%^&*()+={}[]|\\:;"'<>,?/~` |
| 连续连接符 | `--` 或更多连续连字符 |

## 长度限制

- 文件名最长不超过 128 个字符
- 完整路径总长度不超过 260 个字符（Windows 限制）

## 保留名称

以下名称不能作为文件名：

| 系统 | 保留名称 |
|-----|---------|
| Windows | `CON`, `PRN`, `AUX`, `NUL` |
| Windows | `COM1`-`COM9`, `LPT1`-`LPT9` |
| Windows | `desktop.ini` |

## 文件扩展名规范

| 文件类型 | 扩展名 | 说明 |
|---------|-------|------|
| Markdown 文档 | `.md` | 统一使用小写扩展名 |
| Python | `.py` | - |
| JavaScript | `.js` | - |
| TypeScript | `.ts` | - |
| YAML 配置 | `.yaml` | 优先于 `.yml` |
| JSON | `.json` | - |
| TOML | `.toml` | - |

## 目录命名规范

目录命名应与文件命名规范保持一致：
- 使用英文全小写
- 使用连字符分隔语义
- 避免使用数字开头

## 检查机制

### 本地检查

使用 `scripts/check-filename-convention.py` 脚本进行本地检查：

```bash
python scripts/check-filename-convention.py [--fix]
```

### 预提交检查

可在 Git pre-commit hook 中集成文件名检查。

### CI 检查

在持续集成流程中加入文件名规范检查步骤。

## 违规处理

对于已存在的违规文件名，应进行重命名并更新所有相关引用。

## 规范更新

本规范的更新需要通过正式流程：
1. 在 `.trae/specs/` 下创建新的规范 spec
2. 经过评审后更新本文件
3. 更新版本记录
