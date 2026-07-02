---
id: "scripts-usage-check-scripts"
title: "检查类脚本使用说明"
source: "README.md#使用说明"
x-toml-ref: "../../../../../.meta/toml/.agents/scripts/docs/usage/01-check-scripts.toml"
---

# 检查类脚本使用说明

本文档描述 `.agents/scripts/` 目录下所有检查（check）类脚本的用法。

---

## check-gitignore.py

验证 `.gitignore` 是否包含所有必需的忽略规则，并确认 `git status` 中不包含临时依赖文件。

```bash
python .agents/scripts/check-gitignore.py
```

---

## check-vendor.py

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

---

## check-links.py

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

---

## check-spec-consistency.py

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

---

## check-filename-convention.py

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

---

## check-move.py

当 Markdown 文件需要移动到新目录时，自动调整文件内部的相对链接路径，确保移动后所有链接仍然有效。支持 `--update-refs` 选项同时更新其他文件中对源文件的引用。

```bash
# 预览变更（不实际修改）
python .agents/scripts/check-move.py --dry-run docs/old.md docs/new/location.md

# 执行移动并调整链接
python .agents/scripts/check-move.py docs/old.md docs/new/location.md

# 执行移动并同步更新其他文件中的引用
python .agents/scripts/check-move.py --update-refs docs/old.md docs/new/location.md
```

---

## check-source-traceability.py

扫描含 TOML frontmatter 的 Markdown 文件，提取 `source` 溯源字段，建立"源文件→派生产物"反向索引。当源文档变更时，可快速定位受影响的派生产物，避免信息失同步。

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

---

## check-role-permissions.py

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

---

## check-mermaid.py

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

---

## 相关模式

- [工具链成熟度](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/toolchain-maturity.md)
- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [Dry-Run预览优先](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/dry-run-first.md)

---

**[返回索引](../../README.md)** | 下一章 → [生成与构建脚本](02-generate-build-scripts.md)
