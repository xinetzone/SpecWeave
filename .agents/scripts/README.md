# Scripts 脚本目录

`.agents/scripts/` 目录存放自动化验证与检查脚本。

## 脚本列表

| 脚本 | 用途 | 用法 |
|------|------|------|
| `check-gitignore.py` | 验证 `.gitignore` 规则覆盖所有临时依赖路径，检查 `git status` 合规性 | `python .agents/scripts/check-gitignore.py` |
| `check-vendor.py` | 验证 `vendor/` 目录结构合规性、元数据完整性，支持 submodule 深度集成验证、自动修复和引用扫描 | `python .agents/scripts/check-vendor.py [--fix] [--scan-refs] [--deep]` |
| `check-links.py` | 扫描 Markdown 文件中的链接，校验本地文件引用与外部 URL 可达性，支持自动修复相对路径层级错误 | `python .agents/scripts/check-links.py [--check-external] [--fix] [--dry-run] [--json] [--exclude DIR]` |
| `check-spec-consistency.py` | 检查 `spec.md`、`tasks.md`、`checklist.md` 之间的一致性 | `python .agents/scripts/check-spec-consistency.py [--spec-dir DIR] [--all] [--json]` |
| `check-filename-convention.py` | 检查文件名是否符合命名规范（禁止中英文混合、特殊字符等） | `python .agents/scripts/check-filename-convention.py [--fix] [--directory DIR]` |
| `generate-nav.py` | 扫描 `docs/` 目录，自动生成并更新 README.md 与 docs/README.md 的文档导航表 | `python .agents/scripts/generate-nav.py` |
| `generate-dashboard.py` | 扫描 `.trae/specs/` 目录，自动聚合各 Spec 完成状态并更新根 README.md 的执行进度看板 | `python .agents/scripts/generate-dashboard.py` |
| `finalize-atomization.py` | 原子化操作一键收尾：自动修复断链、更新导航表、刷新 Spec 看板 | `python .agents/scripts/finalize-atomization.py [--dry-run] [--no-links] [--no-nav] [--no-dashboard]` |
| `build-ref-index.py` | 构建文件引用反向索引 `{目标: [引用方列表]}`，移动/删除文件前查询受影响范围 | `python .agents/scripts/build-ref-index.py [--query <文件>] [--query-dir <目录>] [--top N] [--orphans] [--json]` |
| `check-move.py` | 文件移动时自动调整内部相对链接路径，可选更新外部引用 | `python .agents/scripts/check-move.py <源> <目标> [--dry-run] [--update-refs]` |
| `check-source-traceability.py` | 扫描 source 溯源字段，建立源文件→派生产物反向索引，支持影响分析 | `python .agents/scripts/check-source-traceability.py [--affected <源文件>] [--json]` |
| `check-role-permissions.py` | 校验角色文件 TOML frontmatter 中 tier 字段与 [permissions] 权限声明完整性 | `python .agents/scripts/check-role-permissions.py [--path DIR] [--json]` |
| `check-mermaid.py` | 扫描 Mermaid 代码块中的常见语法陷阱（空行、未加引号文本、裸中文ID等），支持自动修复 | `python .agents/scripts/check-mermaid.py [--fix] [--dry-run] [--path DIR] [--exclude DIR]` |
| `ci-check.ps1` | CI/CD 流水线检查脚本，运行所有验证并更新导航表 | `.\ci-check.ps1` |

## 使用说明

### check-gitignore.py

验证 `.gitignore` 是否包含所有必需的忽略规则，并确认 `git status` 中不包含临时依赖文件。

```bash
python .agents/scripts/check-gitignore.py
```

### check-vendor.py

验证 `vendor/` 第三方依赖目录的结构合规性和元数据完整性：

- **目录结构检查**：验证根目录是否存在 `README.md` 和 `VERSION.md`
- **元数据完整性**：检查每个手动管理依赖子目录的 `README.md` 是否包含必需字段（名称、版本、来源、引入日期、用途、许可证）
- **.gitignore 规则验证**：确认 `vendor/` 已在 `.gitignore` 中配置忽略
- **Submodule 深度集成验证（--deep）**：检查 git submodule 初始化状态、工作树清洁度、VERSION.md commit 一致性、项目中非法 vendor 引用（sys.path hack/import vendor.）、pytest 测试路径隔离
- **自动修复（--fix）**：自动创建缺失的模板文件和目录结构
- **引用扫描（--scan-refs）**：扫描代码中对 vendor 路径的引用，辅助识别未使用依赖

```bash
# 合规性检查（默认，快速）
python .agents/scripts/check-vendor.py

# 深度集成验证（包含 submodule 检查、非法引用扫描、测试隔离检查）
python .agents/scripts/check-vendor.py --deep

# 自动创建缺失的模板文件
python .agents/scripts/check-vendor.py --fix

# 扫描代码中的 vendor 引用
python .agents/scripts/check-vendor.py --scan-refs

# 修复并扫描引用
python .agents/scripts/check-vendor.py --fix --scan-refs

# 完整检查（深度+引用扫描）
python .agents/scripts/check-vendor.py --deep --scan-refs
```

### check-links.py

扫描项目中的所有 Markdown 文件，提取并校验链接有效性：

- **本地文件引用**：检查相对路径引用的目标文件是否存在（默认启用）
- **外部 URL 检查**：通过 HTTP HEAD 请求检查外部链接可达性，HEAD 失败时自动用 GET `Range: bytes=0-0` 回退（需显式启用）
- **结果缓存**：外部链接检查结果缓存 7 天（存于 `.agents/cache/external-links-cache.json`），避免重复请求
- **模板占位符过滤**：自动跳过 `<!-- ... -->` 格式的模板占位符与 `{变量名}` 占位符
- **智能容错**：401/403（反爬虫/需认证）和 405（不支持 HEAD）视为链接可达

```bash
# 仅检查本地文件引用（默认，快速）
python .agents/scripts/check-links.py

# 同时检查外部链接（使用缓存，7天内不重复请求）
python .agents/scripts/check-links.py --check-external

# 强制重新检查所有外部链接（忽略缓存）
python .agents/scripts/check-links.py --check-external --no-cache

# 清除外部链接检查缓存
python .agents/scripts/check-links.py --clear-cache

# 指定超时与并发数
python .agents/scripts/check-links.py --check-external --timeout 10 --workers 8

# 自定义缓存有效期（天）
python .agents/scripts/check-links.py --check-external --cache-ttl 14

# 排除指定目录
python .agents/scripts/check-links.py --exclude docs/templates vendor

# 自动修复可修复的断链（预览模式，不写入文件）
python .agents/scripts/check-links.py --fix --dry-run

# 自动修复可修复的断链（实际写入）
# 修复类型：绝对路径→相对路径、相对路径层级校正（../层数错误）、目录斜杠补全
python .agents/scripts/check-links.py --fix

# 修复同时处理文件重命名映射
python .agents/scripts/check-links.py --fix --rename 旧名.md=新名.md

# JSON 格式输出（便于 CI 集成）
python .agents/scripts/check-links.py --json

# 检查指定目录
python .agents/scripts/check-links.py --path docs/
```

**定期检查建议**：
- CI 中仅检查本地链接（快速、无网络依赖）
- 外部链接检查可定期（每周/每月）手动运行 `--check-external` 或加入定时任务
- 缓存机制确保频繁运行不会对目标网站造成压力

### check-spec-consistency.py

检查指定 spec 目录或全部 spec 目录中三份文档（spec.md、tasks.md、checklist.md）的一致性：

- 需求 → 任务覆盖检查
- 场景 → 检查点覆盖检查
- 关键数据引用一致性检查
- 交叉引用有效性检查

```bash
# 扫描所有 spec 目录
python .agents/scripts/check-spec-consistency.py

# 检查指定 spec 目录
python .agents/scripts/check-spec-consistency.py --spec-dir .trae/specs/create-agents-md-and-config

# JSON 格式输出
python .agents/scripts/check-spec-consistency.py --json
```

### check-filename-convention.py

检查文件名是否符合命名规范：

- **语言要求**：文档、代码、配置文件均统一使用英文命名
- **允许字符**：字母、数字、连字符 `-`、下划线 `_`、点号 `.`
- **禁止**：空格、中文及其他非 ASCII 字符、连续连字符 `--`
- **保留名称**：Windows 系统保留名称（CON、PRN、AUX、NUL、COM1-9、LPT1-9）

此检查已集成到 pre-commit hook 和 CI 流程中。

```bash
# 检查项目所有文件
python .agents/scripts/check-filename-convention.py

# 指定目录检查
python .agents/scripts/check-filename-convention.py --directory docs/

# 尝试自动修复（仅对部分问题有效）
python .agents/scripts/check-filename-convention.py --fix
```

### generate-nav.py

扫描 `docs/` 目录下的所有 `.md` 文件，提取标题和描述，自动生成文档导航表，
并更新 `README.md` 和 `docs/README.md` 中 `<!-- NAV_TABLE_START -->` 与 `<!-- NAV_TABLE_END -->` 标记之间的内容。

```bash
# 自动生成并更新导航表
python .agents/scripts/generate-nav.py
```

### generate-dashboard.py

扫描 `.trae/specs/` 目录下所有 Spec 的 `tasks.md`，自动聚合各主题和 Spec 的完成状态，
更新根 `README.md` 中 `<!-- SPEC_DASHBOARD_START -->` 与 `<!-- SPEC_DASHBOARD_END -->` 标记之间的执行进度看板。

判定规则：
1. 优先读取 TOML/YAML frontmatter 中的 `status` 字段，若为 `completed`/`done`/`finished` 则视为已完成
2. 否则检查是否存在未勾选的复选框（`- [ ]` 或 `## [ ]`），无未勾选项则视为已完成
3. 自动跳过代码块中的复选框（避免误判示例代码）

```bash
# 自动扫描并更新 Spec 执行进度看板
python .agents/scripts/generate-dashboard.py
```

### finalize-atomization.py

原子化操作一键收尾脚本。在文档/代码原子化拆分、文件移动、目录重构等操作完成后运行，
一键执行断链自动修复、导航表更新、Spec 看板刷新等后处理工作，确保原子化完成后项目状态一致。

执行步骤：
1. **自动断链修复**：调用 link_fixer 扫描全项目，自动修复相对路径层级错误、绝对路径转换、目录尾部斜杠补全等
2. **导航表更新**：运行 generate-nav.py 刷新文档导航表
3. **Spec 看板更新**：运行 generate-dashboard.py 刷新 Spec 执行进度看板

```bash
# 完整后处理（实际执行修复）
python .agents/scripts/finalize-atomization.py

# 预览模式，不修改文件
python .agents/scripts/finalize-atomization.py --dry-run

# 跳过链接修复
python .agents/scripts/finalize-atomization.py --no-links

# 指定目标目录（仅修复特定子树）
python .agents/scripts/finalize-atomization.py --target docs/retrospective/
```

### build-ref-index.py

构建文件引用反向索引。扫描项目中所有 Markdown 文件提取本地相对链接，建立 `{目标文件: [引用文件列表]}` 的反向映射。
在文件移动、删除、大规模重构前，可快速查询受影响的引用方，避免断链遗漏。

功能特性：
- 自动跳过代码块内的示例链接
- 支持文件查询、目录查询、孤立文件检测
- 支持 JSON 格式输出（便于与其他工具集成）
- 自动排除 `.git/`、`vendor/`、`node_modules/` 等目录

```bash
# 构建索引并显示统计摘要 + Top 被引用文件
python .agents/scripts/build-ref-index.py

# 查询哪些文件引用了指定文件（移动前查询影响面）
python .agents/scripts/build-ref-index.py --query AGENTS.md

# 批量查询多个文件
python .agents/scripts/build-ref-index.py --query file1.md path/to/file2.md

# 查询哪些文件引用了指定目录下的任意文件
python .agents/scripts/build-ref-index.py --query-dir docs/retrospective/patterns/

# 显示被引用次数最多的 Top 20 文件
python .agents/scripts/build-ref-index.py --top 20

# 列出未被任何文件引用的孤立文件
python .agents/scripts/build-ref-index.py --orphans

# JSON 格式输出（便于工具集成）
python .agents/scripts/build-ref-index.py --query README.md --json
```

### check-move.py

当 Markdown 文件需要移动到新目录时，自动调整文件内部的相对链接路径，
确保移动后所有链接仍然有效。支持 `--update-refs` 选项同时更新其他文件中对源文件的引用。

```bash
# 预览变更（不实际修改）
python .agents/scripts/check-move.py --dry-run docs/old.md docs/new/location.md

# 执行移动并调整链接
python .agents/scripts/check-move.py docs/old.md docs/new/location.md

# 执行移动并同步更新其他文件中的引用
python .agents/scripts/check-move.py --update-refs docs/old.md docs/new/location.md
```

### check-source-traceability.py

扫描含 TOML frontmatter 的 Markdown 文件，提取 `source` 溯源字段，建立"源文件→派生产物"反向索引。
当源文档变更时，可快速定位受影响的派生产物，避免信息失同步。

- **审计模式（默认）**：列出所有 source 字段及其对应派生产物
- **影响分析模式**：给定变更的源文件，输出受影响的派生产物清单

```bash
# 审计模式：列出所有溯源关系
python .agents/scripts/check-source-traceability.py

# 影响分析：查询源文件变更的受影响产物
python .agents/scripts/check-source-traceability.py --affected README.md

# JSON 格式输出（便于 CI 集成）
python .agents/scripts/check-source-traceability.py --json
python .agents/scripts/check-source-traceability.py --affected README.md --json
```

### check-role-permissions.py

校验 `.agents/roles/` 目录下角色文件的 TOML frontmatter 中 `tier` 字段与 `[permissions]` 权限声明完整性：

- **frontmatter 有效性**：所有角色文件必须包含有效的 TOML frontmatter
- **tier 字段合法性**：`tier` 值仅允许 `co-founder` 或 `standard`（未声明时默认 `standard`）
- **权限声明完整性**：当 `tier = "co-founder"` 时，`[permissions]` 表必须存在且包含 `view` 与 `manage` 字段

```bash
# 校验默认目录（.agents/roles/）
python .agents/scripts/check-role-permissions.py

# 指定扫描目录
python .agents/scripts/check-role-permissions.py --path .agents/roles/

# JSON 格式输出（便于 CI 集成）
python .agents/scripts/check-role-permissions.py --json
```

### check-mermaid.py

扫描 Markdown 文件中的 Mermaid 代码块，检测并自动修复常见语法陷阱：

- **代码块内空行检测**：subgraph 之间、边定义与 style 之间的空行会导致解析中断（错误级）
- **裸中文 subgraph ID 检测**：含中文/全角字符的 subgraph ID 会导致渲染失败（错误级）
- **未加引号的中文节点检测**：含中文/特殊字符的节点文本应使用双引号包裹（警告级）
- **未加引号的中文边标签检测**：含中文/特殊字符的边标签应使用双引号包裹（警告级）
- **Markdown 列表触发模式检测**：节点文本中「数字+英文句点+空格」会触发列表解析错误（警告级）

自动修复（--fix）可处理空行、节点引号、边标签引号、数字点格式四类问题；裸中文 subgraph ID 需人工指定英文 ID 后修复。

```bash
# 仅检查（不修改文件）
python .agents/scripts/check-mermaid.py

# 自动修复可安全修复的问题
python .agents/scripts/check-mermaid.py --fix

# 预览修复效果（不写入文件）
python .agents/scripts/check-mermaid.py --fix --dry-run

# 指定检查目录
python .agents/scripts/check-mermaid.py --path docs/

# 排除指定目录
python .agents/scripts/check-mermaid.py --exclude docs/templates
```

### ci-check.ps1
一键运行所有验证检查（Git 忽略规则、链接有效性、规格一致性、导航表更新）。适用于 CI/CD 流水线或手动提交前检查。
```powershell
.\ci-check.ps1
```