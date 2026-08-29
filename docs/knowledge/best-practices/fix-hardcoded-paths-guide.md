---
id: "fix-hardcoded-paths-guide"
title: "硬编码路径批量修复工具使用指南（fix-hardcoded-paths.py）"
category: "best-practices"
tags: ["hardcoded-paths", "refactor", "python", "path-migration", "dry-run", "ipynb", "script"]
date: "2026-08-07"
last_updated: "2026-08-07"
status: "stable"
author: "SpecWeave"
summary: "可复用硬编码路径批量修复工具使用指南：正则保留分隔符风格与盘符大小写，支持 .py/.ipynb 双处理与 dry-run/apply 双模式。"
security_level: "public"
knowledge_type: "procedural"
validation_status: "verified"
reuse_count: 0
integrity: "unchecked"
---

# 硬编码路径批量修复工具使用指南（fix-hardcoded-paths.py）

> 沉淀自 `chaos/flexloop/scripts/fix_hardcoded_paths.py`，泛化为可复用的「硬编码路径批量修复」工具，供项目迁移、仓库重构时批量替换源码与 Notebook 中的旧路径根目录。

---

## 目录

- [用途](#用途)
- [文件位置](#文件位置)
- [正则逻辑说明](#正则逻辑说明)
- [参数说明](#参数说明)
- [.py / .ipynb 双处理](#py--ipynb-双处理)
- [dry-run 与 apply 验证方式](#dry-run-与-apply-验证方式)
- [自定义旧/新路径](#自定义旧新路径)
- [变更历史](#变更历史)

---

## 用途

当仓库中的 `.py` 源码或 `.ipynb` Notebook 硬编码了某个旧路径根目录，且路径整体迁移到新位置时，用本工具批量扫描、预览并替换。

默认配置为将旧路径根目录 `flexloop` 替换为新路径片段 `spaces/chaos/flexloop`（例如 `d:\flexloop` → `d:\spaces\chaos\flexloop`）。旧路径/新路径可在脚本顶部常量中调整，见[自定义旧/新路径](#自定义旧新路径)。

> **安全说明**：脚本不内置真实个人路径作为默认值；默认扫描目录为当前工作目录，建议始终用 `--dir` 显式指定目标目录。

## 文件位置

- 脚本：`SpecWeave/.agents/scripts/fix-hardcoded-paths.py`
- 本文档：`SpecWeave/.agents/docs/knowledge/best-practices/fix-hardcoded-paths-guide.md`

## 正则逻辑说明

核心正则（`_OLD_PATH_RE`）：

```
(?i)(?P<drive>[a-z]):(?P<sep>\\+|/+){旧路径根目录}
```

- **`(?i)`**：整体不区分大小写，可匹配 `d:` 或 `D:`。
- **`(?P<drive>[a-z])`**：捕获盘符字母，替换时**保留盘符原始大小写**。
- **`(?P<sep>\\+|/+)`**：捕获分隔符，可匹配单个或多个反斜杠，或正斜杠；替换时**保留原始分隔符风格与反斜杠数量**。
- **结尾**：匹配旧路径根目录名（默认 `flexloop`）。

由此实现四种风格的保留与映射：

| 源写法 | 替换结果 |
|--------|----------|
| `d:\\flexloop`（源码双反斜杠） | `d:\\spaces\\chaos\\flexloop` |
| `d:\flexloop`（单反斜杠） | `d:\spaces\chaos\flexloop` |
| `d:/flexloop`（正斜杠） | `d:/spaces/chaos/flexloop` |
| `D:\flexloop`（大写盘符） | `D:\spaces\chaos\flexloop` |

**关键设计**：不做大小写归一化、不强制统一分隔符，最大限度减少对原有代码风格的扰动，避免引入无谓 diff。

## 参数说明

| 参数 | 说明 |
|------|------|
| `--dir <路径>` | 指定要扫描的目录（递归仅限该层目录下的 `.py`/`.ipynb` 文件，非递归）。默认值为当前工作目录，建议显式指定。 |
| `--apply` | 确认写入，实际修改文件内容。**默认不加此参数即为 dry-run（仅预览，不写文件）。** |

示例：

```bash
# 预览某目录下的待修复项（不写文件）
python fix-hardcoded-paths.py --dir <目标目录>

# 实际写入修复
python fix-hardcoded-paths.py --dir <目标目录> --apply
```

## .py / .ipynb 双处理

- **`.py` 文件**（`fix_py_file`）：以 UTF-8 读取全文，对文本整体正则替换；有改动时逐行打印「旧→新」差异；`--apply` 时写回。
- **`.ipynb` 文件**（`fix_ipynb_file`）：通过 `json.load` 解析，遍历各 `cells[].source` 字符串列表逐块替换，兼容单字符串形式；写回用 `json.dump(ensure_ascii=False, indent=2)` 保证 JSON 合法且保留中文可读。

## dry-run 与 apply 验证方式

1. **dry-run 预检（默认）**：运行后输出扫描目录、模式（DRY-RUN）、待修复文件与逐行差异、统计（扫描文件数 / 修复位置数 / 跳过项）。此时**不会修改任何文件**，可安全审查将要发生的变化。
2. **人工核对**：确认 dry-run 输出的差异符合预期（分隔符风格、盘符大小写均被保留）。
3. **apply 提交**：确认无误后加 `--apply` 执行实际写入。
4. **回归验证**：写回后用 `git diff` 复查改动是否局限于路径替换，未引入无关改动；对 `.ipynb` 确认仍是合法 JSON（可用 `json.load` 快速校验）。

> 建议始终先在副本或 dry-run 模式下核对，确认无误后再对真实仓库执行 `--apply`。

## 自定义旧/新路径

脚本顶部有两个常量可按需调整：

```python
_OLD_ROOT = "flexloop"            # 旧路径根目录名（正则匹配结尾）
_NEW_ROOT = "spaces/chaos/flexloop"  # 新路径片段（不含盘符与首个分隔符）
```

调整后无需改动其余逻辑，正则会基于 `_OLD_ROOT` 动态构建，替换会基于 `_NEW_ROOT` 按原始分隔符风格拼接。

## 变更历史

- **v1.0 / 2026-08-07**：初始沉淀。由 `chaos/flexloop/scripts/fix_hardcoded_paths.py` 泛化而来，保留核心逻辑（`_OLD_PATH_RE`、`_replacement`、`fix_py_file`、`fix_ipynb_file`、dry-run/apply、`--dir`）；将默认扫描目录改为由命令行 `--dir` 决定（不内置真实个人路径），旧/新路径提取为可配置常量。
