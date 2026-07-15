---
id: "scripts-usage-fix-scripts"
title: "批量修复脚本使用说明"
source: "README.md#使用说明"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/docs/usage/04-fix-scripts.toml"
---
# 批量修复脚本使用说明

本文档描述 `.agents/scripts/` 目录下批量修复（fix）与分析（analyze）类脚本的用法。这些脚本源自 2026-07-10 的 frontmatter 路径与链接批量修复工作（8 阶段修复：frontmatter 357→0 + 内联断链 63→0 + 目录链接 849→63），可直接用于未来同类问题的批量处理。

---

## 脚本分类总览

| 分类 | 脚本数 | 说明 |
|------|--------|------|
| Frontmatter source 路径修复 | 4 个 | 修复 YAML/TOML frontmatter 中 source 字段的路径问题 |
| Markdown 链接修复 | 2 个 | 修复正文中的断链和目录链接警告 |
| 分析工具（只读） | 2 个 | 不修改文件，用于评估问题规模和分类 |

**共同特性**：
- 所有写入操作使用 `newline=""` 保留 LF 行尾（符合 `.gitattributes` 规范）
- `fix_directory_and_missing.py` 和 `fix_docs_prefix_paths.py` 通过 `importlib` 动态导入 `check-links.py` 和 `lib.markdown`
- 部分脚本依赖 `check-links.py` 输出的日志文件，需先运行 check-links 生成日志

---

## 分析工具（建议先运行）

### analyze_frontmatter_issues.py

分析 frontmatter 路径问题的分类统计。调用 `check-links.py` 的 `check_frontmatter_paths()` 函数扫描 `docs/` 下所有 `.md` 文件，按问题类型（`docs/` 前缀、文件不存在）分类输出统计和样例。

```bash
python .agents/scripts/analyze_frontmatter_issues.py
```

**输入**：`docs/` 目录下所有 `.md` 文件
**输出**：stdout，打印问题分类统计和前 15 个样例
**依赖**：`check-links.py`（importlib 动态导入）、`lib.markdown.find_markdown_files()`
**用途**：修复前评估 frontmatter 路径问题规模，了解 `docs/` 前缀 vs 文件缺失的分布

---

### analyze_missing_sources.py

扫描所有 `.md` 文件的 frontmatter `source` 字段，检查指向的文件是否存在。输出缺失 source 目标的文件列表，用于手动修复决策。

```bash
python .agents/scripts/analyze_missing_sources.py
```

**输入**：`docs/` 目录下所有 `.md` 文件
**输出**：stdout，打印扫描文件数、缺失 source 数量、每个缺失项的文件路径和 source 值
**依赖**：`lib.frontmatter.parse_frontmatter_unified()`
**用途**：定位所有 source 指向已删除/已迁移文件的文档，辅助手动修复决策

---

## Frontmatter source 路径修复脚本

### fix_remaining_frontmatter.py

修复 frontmatter source 字段中的 4 类路径问题（同时处理 `.md` 和 `.toml` 文件）：

1. `comprehensive-retrospective-template/` 路径 → `external: 模板引用` 标记（模板已删除）
2. `.agents/insights/` 路径 → `external: 已迁移` 标记（目录已迁移）
3. `d:/spaces/SpecWeave/` 绝对路径 → 转换为相对路径（目标存在时）或 `external: 不存在`
4. `d:\AI\` 或 `d:/AI/` 跨项目路径 → `external: 外部项目引用`

```bash
python .agents/scripts/fix_remaining_frontmatter.py
```

**输入**：`docs/` 下所有 `.md` 文件 + `.meta/toml/docs/` 下所有 `.toml` 文件
**输出**：直接修改源文件，打印修复的文件路径
**适用场景**：模板引用残留、绝对路径、跨项目路径的批量标记

---

### fix_docs_prefix_paths.py

修复 frontmatter source 字段中以 `docs/` 开头的路径（不规范写法，应使用相对路径）：

1. `docs/xxx.md` 目标文件存在 → 修复为正确的相对路径
2. `docs/xxx.md` 目标不存在但同目录有 `xxx/README.md`（原子化拆分）→ 修复为 README.md 引用
3. `docs/xxx.md` 目标不存在且无拆分子目录 → 标记为 `external: 不存在`

```bash
python .agents/scripts/fix_docs_prefix_paths.py
```

**输入**：`docs/` 下所有 `.md` 文件（通过 `lib.markdown.find_markdown_files()` 扫描）
**输出**：直接修改源文件，打印修复的文件路径
**依赖**：`check-links.py`（importlib 动态导入）、`lib.markdown.find_markdown_files()`
**适用场景**：source 字段使用 `docs/` 绝对前缀而非相对路径的批量修正

---

### fix_directory_and_missing.py

修复 frontmatter source 字段中的目录链接和缺失文件路径：

1. 目录链接（目录内有 README.md）→ 追加 `/README.md`
2. 目录链接（目录内无 README.md）→ 标记为 `external: 目录无README`
3. 缺失文件且包含 `d:\AI\` 或 `d:/AI/` → `external: 外部项目引用`
4. 缺失文件其他情况 → `external: 不存在`
5. 支持 `lib/`、`.agents/rules/`、`retrospective/`、`apps/`、`task-reports/` 前缀的路径自动解析为相对路径
6. 支持多路径分隔（`+`、`|`、`;`、`,`）的逐路径修复

```bash
python .agents/scripts/fix_directory_and_missing.py
```

**输入**：`docs/` 下所有 `.md` 文件（通过 `lib.markdown.find_markdown_files()` 扫描）
**输出**：直接修改源文件，打印修复的文件路径
**依赖**：`check-links.py`（importlib 动态导入）、`lib.markdown.find_markdown_files()`
**适用场景**：source 指向目录而非文件、指向已删除文件的批量修复

---

### fix_cross_project_temp.py

修复 frontmatter source 字段中的跨项目路径（`d:/AI/`、`d:\AI\`）和临时分析文件路径（`.temp/`）：

- `.temp/` 路径 → `external: 临时分析文件（已清理）`
- `d:\AI\` 或 `d:/AI/` 路径 → `external: 外部项目引用`
- 同时处理 YAML 双引号转义形式（`\\` → `\\\\`）

```bash
python .agents/scripts/fix_cross_project_temp.py
```

**输入**：`docs/` 下所有文件 + `.meta/toml/` 下所有文件（`.md` 和 `.toml`）
**输出**：直接修改源文件，打印扫描文件数和修复文件数
**适用场景**：跨项目引用和临时文件引用的批量标记清理

---

## Markdown 链接修复脚本

### fix_inline_broken_links.py

批量修复 Markdown 正文中的断链，按 5 类分类处理：

1. `.chaos/` 路径（外部项目）→ 转为行内代码
2. `file:///d:/AI/` 绝对路径（跨项目）→ 转为行内代码
3. 根路径 `/zh-Hans-CN/`、`/codex/` → 转为完整 URL（`https://platform.openai.com/...`）
4. 同目录缺失文件 → 转为行内代码
5. 相对路径层级错误（`../../../../patterns/` → `../../../../../patterns/`）→ 修复路径

```bash
python .agents/scripts/fix_inline_broken_links.py
```

**输入**：`.trae/documents/broken-links-phase7.txt`（check-links 输出日志，路径在脚本中硬编码）
**输出**：直接修改 `docs/` 下对应的 `.md` 文件，打印每文件修复数
**日志格式**：`[文件:行号] 显示文本 -> 目标路径 (文件不存在: ...)`
**复用提示**：如需用于新的断链修复，先将 check-links 输出重定向到 `.trae/documents/broken-links-phase7.txt`，或修改脚本第 139 行的 `log_file` 路径

---

### fix_directory_link_warnings.py

批量修复目录链接警告：将 `[text](dir/)` 改为 `[text](dir/README.md)`。仅修复目录内有 README.md 的链接，跳过目录内无 README.md 的链接。

```bash
# 预览模式（不修改文件）
python .agents/scripts/fix_directory_link_warnings.py --dry-run

# 实际修复
python .agents/scripts/fix_directory_link_warnings.py
```

**输入**：`.trae/documents/dir-warnings.txt`（check-links 目录链接警告日志，路径在脚本中硬编码）
**输出**：直接修改 `docs/` 或项目根目录下对应的 `.md` 文件，打印每文件修复数
**日志格式**：`[文件:行号] 显示文本 -> 目标路径 (链接到目录而非文件（应链接到 .../README.md）)`
**复用提示**：如需用于新的目录链接修复，先将 check-links 输出重定向到 `.trae/documents/dir-warnings.txt`，或修改脚本第 81 行的 `log_file` 路径
**注意**：dry-run 预览数可能高于实际修复数（因重复 target 在修复后内容上不再匹配），以实际修复数为准

---

## 批量修复推荐流程

当需要批量处理 frontmatter 路径或链接问题时，按以下流程执行：

### 第 1 步：分析问题规模

```bash
# 分析 frontmatter 路径问题分类
python .agents/scripts/analyze_frontmatter_issues.py

# 扫描缺失 source 目标的文件
python .agents/scripts/analyze_missing_sources.py
```

### 第 2 步：生成问题日志

```bash
# 生成 frontmatter 路径问题日志
python .agents/scripts/check-links.py --path docs --check-frontmatter-paths

# 生成断链和目录链接警告日志（重定向到文件供 fix 脚本读取）
python .agents/scripts/check-links.py --path docs > .trae/documents/check-links-output.txt
```

### 第 3 步：Frontmatter 路径修复（按顺序执行）

```bash
# 3a. 修复模板引用、绝对路径、跨项目路径
python .agents/scripts/fix_remaining_frontmatter.py

# 3b. 修复 .temp/ 和 d:/AI/ 路径
python .agents/scripts/fix_cross_project_temp.py

# 3c. 修复 docs/ 前缀路径
python .agents/scripts/fix_docs_prefix_paths.py

# 3d. 修复目录链接和缺失文件
python .agents/scripts/fix_directory_and_missing.py
```

### 第 4 步：Markdown 链接修复

```bash
# 4a. 修复内联断链（需先将 check-links 断链输出保存为 broken-links-phase7.txt）
python .agents/scripts/fix_inline_broken_links.py

# 4b. 修复目录链接警告（需先将 check-links 目录警告输出保存为 dir-warnings.txt）
python .agents/scripts/fix_directory_link_warnings.py --dry-run  # 先预览
python .agents/scripts/fix_directory_link_warnings.py            # 再执行
```

### 第 5 步：验证

```bash
# 验证 frontmatter 路径问题清零
python .agents/scripts/check-links.py --path docs --check-frontmatter-paths

# 验证断链清零
python .agents/scripts/check-links.py --path docs
```

---

## 脚本间依赖关系

```
check-links.py（核心检查器）
  ├── analyze_frontmatter_issues.py（调用 check_frontmatter_paths）
  ├── fix_directory_and_missing.py（importlib 导入 + lib.markdown）
  └── fix_docs_prefix_paths.py（importlib 导入 + lib.markdown）

lib.frontmatter.parse_frontmatter_unified()
  └── analyze_missing_sources.py

独立扫描（无外部依赖）：
  ├── fix_remaining_frontmatter.py
  ├── fix_cross_project_temp.py
  ├── fix_inline_broken_links.py（依赖日志文件）
  └── fix_directory_link_warnings.py（依赖日志文件）
```

---

## 相关文档

- [检查类脚本](01-check-scripts.md) — check-links.py 等 9 个检查脚本
- [生成与构建脚本](02-generate-build-scripts.md) — generate-nav.py 等 5 个生成脚本
- [Git 与 CI 脚本](03-git-ci-scripts.md) — git-commit-utf8.py、ci-check.ps1
- [共享库 API 参考](../../lib/README.md) — lib/ 下 14 个模块的 API 文档
- [best-practices 断链修复复盘](../../../docs/retrospective/reports/task-reports/retrospective-best-practices-readme-link-fix-20260709/README.md) — 本次修复工作的完整复盘记录
