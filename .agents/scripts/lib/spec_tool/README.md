# spec_tool — Spec 文档工具集

统一的 Spec 文档质量工具链，提供元数据校验、内容一致性检查、格式标准化和测试代码生成等功能。

## 快速开始

```bash
# 方式一：通过 spec-tool.py 入口（推荐）
python .agents/scripts/spec-tool.py check --help
python .agents/scripts/spec-tool.py format --help

# 方式二：通过 python -m
cd .agents/scripts
python -m lib.spec_tool check --help
python -m lib.spec_tool format --help
```

## 子命令总览

| 子命令 | 功能 | 主要输出 |
|---|---|---|
| `check` | 规格文档一致性与元数据检查 | 错误/警告列表、退出码 |
| `format` | Spec 文档格式检查与自动修复 | 格式问题报告、自动修复 |
| `gen-tests` | 从 spec.md 生成 pytest 测试骨架 | 测试用例文件 |

---

## check — 一致性与元数据检查

### 两种模式

#### 1. 元数据模式（`--meta-only`）
只检查元数据层面的合规性，速度快，适合 CI 门禁：

- ✅ 三件套完整性：`spec.md` + `tasks.md` + `review.md`
- ✅ frontmatter 存在性：YAML（推荐）或 TOML（兼容）
- ✅ `status` 字段合法性：必须是 [VALID_STATUSES](#合法-status-值域) 之一

```bash
# 全量元数据检查
python spec-tool.py check --meta-only

# 指定单个 spec 目录
python spec-tool.py check --meta-only --spec-dir .trae/specs/my-spec/

# JSON 输出（CI 集成）
python spec-tool.py check --meta-only --json
```

#### 2. 内容一致性模式（默认）
检查需求与任务、场景与检查点之间的对应关系：

- 需求 → 任务覆盖度
- 场景 → 检查点覆盖度
- 数据一致性
- 交叉引用有效性
- 需求明确性、可执行性

```bash
# 全量一致性检查
python spec-tool.py check

# 指定阈值（语义匹配关键词数）
python spec-tool.py check --match-threshold 80

# JSON 输出
python spec-tool.py check --json
```

### 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 全部通过 |
| 1 | 存在错误或警告 |

---

## format — 格式检查与自动修复

### 两种模式

#### 1. 格式检查（默认）
检查 spec 文档的章节结构、格式规范等。

```bash
python spec-tool.py format
python spec-tool.py format --check-all
python spec-tool.py format --format json
```

#### 2. Frontmatter 自动修复（`--fix-frontmatter`）
批量修复 frontmatter 相关问题，**支持 dry-run 预览**：

- 🆕 为无 frontmatter 的文件自动添加（从 H1 提取 `title`，默认 `status: draft`）
- ➕ 补全已有 frontmatter 中缺失的 `status` 字段
- 🔄 归一化非法 `status` 值到合法值域（按 `STATUS_NORMALIZATION_MAP` 映射）

```bash
# 预览模式（推荐先跑）
python spec-tool.py format --fix-frontmatter --dry-run

# 实际执行
python spec-tool.py format --fix-frontmatter

# 指定默认 status（默认 draft）
python spec-tool.py format --fix-frontmatter --default-status planning

# 同时添加 date 字段
python spec-tool.py format --fix-frontmatter --add-date

# JSON 输出
python spec-tool.py format --fix-frontmatter --dry-run --json
```

### 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 执行成功（或预览通过） |
| 1 | 存在部分错误 |
| 2 | 目录不存在等致命错误 |

---

## gen-tests — 测试代码生成

从 spec.md 自动生成 pytest 测试骨架。

```bash
# 生成单个 spec 的测试
python spec-tool.py gen-tests --spec .trae/specs/my-spec/

# 全量生成
python spec-tool.py gen-tests --all

# 预览模式
python spec-tool.py gen-tests --dry-run
```

---

## 附录

### 合法 status 值域

按生命周期顺序排列：

| 值 | 含义 |
|---|---|
| `draft` | 草稿，初步构想 |
| `planning` | 规划中，需求细化 |
| `in-progress` | 实施中 |
| `pending-approval` | 待审批 |
| `approved` | 已批准 |
| `implemented` | 已实现，待验证 |
| `review` | 审查中 |
| `completed` | 已完成 |
| `deprecated` | 已废弃 |
| `archived` | 已归档 |

> 来源：[constants.py](constants.py) 中的 `VALID_STATUSES`

### Status 归一化映射

历史文件中常见的非法 status 会自动映射到合法值：

| 旧值 | 映射为 |
|---|---|
| `complete` | `completed` |
| `done` | `completed` |
| `proposed` | `draft` |
| `candidate` | `draft` |
| `pending` | `draft` |
| `todo` / `to-do` | `draft` |
| `active` / `wip` | `in-progress` |
| `in_progress` | `in-progress` |
| `awaiting-approval` | `pending-approval` |
| `approved-pending` | `pending-approval` |

> 新增映射请编辑 [constants.py](constants.py) 中的 `STATUS_NORMALIZATION_MAP`。

### 标准三件套

按 TRAE-spec-mode Skill 规范，每个 spec 目录应包含：

| 文件 | 用途 |
|---|---|
| `spec.md` | 规格说明（需求、场景、设计等） |
| `tasks.md` | 任务拆解与进度跟踪 |
| `review.md` | 审查记录与结论 |

> 历史文件名 `checklist.md` 已废弃，统一迁移为 `review.md`。

### 相关测试

单元测试位于 [`.agents/scripts/tests/`](../../tests/)：

- `test_spec_tool_metadata_checker.py` — 元数据校验测试（22 用例）
- `test_spec_tool_frontmatter_fixer.py` — frontmatter 修复测试（44 用例）
- `test_spec_tool_cli.py` — CLI 集成测试（16 用例）

```bash
# 运行全部 spec_tool 测试
pytest .agents/scripts/tests/test_spec_tool_*.py -v
```
