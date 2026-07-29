---
title: "迁移级联更新清单模板"
id: "migration-cascade-checklist"
source: "retrospective:retrospective-specweave-full-project-20260719"
x-toml-ref: "../../.meta/toml/.agents/templates/migration-cascade-checklist-template.toml"
type: "checklist-template"
maturity_level: "L1"
created_date: "2026-07-19"
tags: [migration, refactor, checklist, cascade-update, path-migration, directory-restructure]
trigger_conditions:
  - 任何涉及目录/文件重命名或位置迁移的 refactor 提交前
  - docs/ 与 .agents/docs/ 等文档根路径调整
  - 跨模块资源路径变更（脚本、模板、配置、TOML 元数据）
  - Spec 主题目录重组或归档
validation_count: 0
reuse_count: 0
related_patterns:
  - cascade-update-prerequisite-check
  - cascade-update-topology
---
# 迁移级联更新清单（Migration Cascade Update Checklist）

> **来源**：从[SpecWeave全项目复盘报告](../docs/retrospective/reports/project-reports/retrospective-specweave-full-project-20260719/README.md)ACT-03萃取。核心教训：2026-07-15文档根路径迁移（`docs/`→`.agents/docs/`）后，docgen.py stats路径未同步更新，导致核心数据连续3天显示"模式0+"而未被发现。根本原因是缺少三类引用方的系统化扫描。本清单确保迁移类重构不遗漏任何引用方。

---

## 迁移前（Pre-Migration）——必须执行的全量扫描

> **原则**：先扫描、后迁移。在移动任何文件之前，必须完成对三类引用方的全量Grep扫描，记录所有引用点，形成迁移影响清单。

### 一、基础信息记录

- [ ] **迁移源路径**（Source）：`<旧路径，如 docs/retrospective/>`
- [ ] **迁移目标路径**（Target）：`<新路径，如 .agents/docs/retrospective/>`
- [ ] **迁移类型**：□ 目录整体迁移 □ 目录拆分 □ 文件重命名 □ 根路径变更 □ 其他：______
- [ ] **影响域预估**：□ 仅文档链接 □ 含脚本硬编码 □ 含TOML元数据 □ 含CI配置

### 二、第一类引用方：Markdown 相对链接扫描

> **风险**：Markdown 文档中的 `[text](relative/path.md)` 相对链接在迁移后会断链。

- [ ] 执行扫描命令：
  ```bash
  # 扫描所有 md 文件中对旧路径前缀的引用
  grep -rn "<旧路径片段>" --include="*.md" .
  # Windows PowerShell:
  # Get-ChildItem -Recurse -Filter *.md | Select-String "<旧路径片段>"
  ```
- [ ] 记录命中文件数：______ 个文件
- [ ] 识别链接类型：
  - [ ] **同目录互引**：文件在迁移目录内部互相引用，迁移后路径关系不变（通常无需修改）
  - [ ] **跨目录引用**：外部文件指向迁移目录内文件（**必须修改**）
  - [ ] **锚点引用**：`#L行号-L行号` 锚点（文件存在则锚点通常仍有效，需抽查）
- [ ] **frontmatter 中的 `source` 字段**：检查是否有 `source: "旧路径/..."` 溯源引用
- [ ] **AGENTS.md 导航表**：检查核心入口文件中的路径引用
- [ ] **README 索引表**：检查各 README.md 中的表格链接

### 三、第二类引用方：x-toml-ref TOML元数据引用扫描

> **风险**：Markdown frontmatter 中的 `x-toml-ref` 字段指向 `.meta/toml/` 下的TOML元数据文件，路径不匹配会导致元数据加载失败、双斜杠断裂错误。

- [ ] 执行扫描命令：
  ```bash
  grep -rn "x-toml-ref:.*<旧路径片段>" --include="*.md" .
  ```
- [ ] 记录命中文件数：______ 个文件
- [ ] 检查 `.meta/toml/` 下对应的 TOML 文件是否已迁移/需迁移
- [ ] 如需创建缺失 TOML 骨架，使用保守修复：
  ```bash
  python .agents/scripts/fix-x-toml-ref.py --fix-only --create-toml
  ```

### 四、第三类引用方：脚本硬编码路径扫描

> **风险**：这是最容易遗漏、危害最大的一类——脚本中的硬编码路径不会产生编译错误，只会静默返回空结果或0值（如本次 docgen.py stats 路径断链事件）。

- [ ] 执行扫描命令（Python脚本）：
  ```bash
  grep -rn '"<旧路径片段>"' --include="*.py" .agents/scripts/
  grep -rn "'<旧路径片段>'" --include="*.py" .agents/scripts/
  # 同时扫描 Path() 构造和字符串拼接
  grep -rn "docs/retrospective\|docs\\\\retrospective" --include="*.py" .agents/scripts/
  ```
- [ ] 执行扫描命令（Shell/PowerShell脚本）：
  ```bash
  grep -rn "<旧路径片段>" --include="*.sh" --include="*.ps1" .
  ```
- [ ] 执行扫描命令（CI工作流）：
  ```bash
  grep -rn "<旧路径片段>" .github/workflows/
  ```
- [ ] 记录命中文件数：______ 个文件
- [ ] 对每个命中区分：
  - [ ] **运行时路径**（如 `root / "docs/..."`）：**必须修改**，影响功能正确性
  - [ ] **帮助文本/注释**（如 `--help` 输出、docstring）：应同步更新，避免文档误导
  - [ ] **测试断言/fixture路径**：必须同步修改，否则测试失败
- [ ] **重点检查**：以下函数模式常隐藏硬编码路径：
  - [ ] 统计类函数（`_stats_count_*`、`collect_*`）
  - [ ] 文件发现/遍历函数（`glob`、`rglob`、`Path.exists()` 判断）
  - [ ] 默认参数值（`def func(path="docs/...")`）
  - [ ] 常量定义（`PATTERNS_DIR = "docs/..."`）

### 五、隐含依赖检查

- [ ] **`.gitignore`**：是否有基于旧路径的忽略规则需要同步更新？
- [ ] **`__init__.py` / 包导入**：Python包路径是否受影响？
- [ ] **配置文件**（`pyproject.toml`、`pytest.ini`、`setup.cfg`等）：路径配置是否需更新？
- [ ] **IDE配置**（`.vscode/`、`.idea/`）：如非共享配置可跳过
- [ ] **导航/索引生成脚本**：类似 docgen.py 的自动生成工具是否指向旧路径？

---

## 迁移中（Migration）——执行顺序

- [ ] **Step 1**：先创建目标目录（如不存在）
- [ ] **Step 2**：执行文件迁移（`git mv` 优先，保留历史）
  ```bash
  git mv <旧路径> <新路径>
  ```
- [ ] **Step 3**：按「迁移前」扫描结果，逐一修改三类引用方
  - [ ] Markdown 相对链接（外部引用方）
  - [ ] x-toml-ref 字段与 TOML 文件位置
  - [ ] 脚本硬编码路径（运行时路径优先于注释）
- [ ] **Step 4**：删除空的旧目录（迁移完成后确认无残留文件）

---

## 迁移后（Post-Migration）——验证与收尾

### 一、自动化验证

- [ ] **链接校验**：
  ```bash
  python .agents/scripts/check-links.py --path <迁移涉及的目录>
  ```
  结果：______ 个链接，______ 个有效，______ 个失效
- [ ] **单元测试回归**：
  ```bash
  python -m pytest .agents/scripts/tests/ -v --tb=short
  ```
  结果：______ 个通过，______ 个失败
- [ ] **关键脚本冒烟测试**：手动运行受影响的核心脚本（如 `python .agents/scripts/docgen.py stats`），确认输出正常
- [ ] **CI 工作流验证**：如有条件，触发相关 CI 工作流确认全绿

### 二、人工抽查

- [ ] 抽查 3-5 个跨目录链接，确认在浏览器/Markdown预览中可跳转
- [ ] 打开迁移后目录的 README.md，确认索引表链接正确
- [ ] 检查自动生成的产物（如 docgen 生成的导航表、看板）是否正常
- [ ] 检查 AGENTS.md 核心导航表无断链

### 三、统计/缓存更新

- [ ] **快照/缓存文件**：如有运行时缓存（如 `.stats-cache.json`），确认其会在下次运行时自动重建，或手动删除触发重建
- [ ] **Changelog 验证**：如迁移影响 docgen stats 统计路径，手动运行一次 `python .agents/scripts/docgen.py stats`，确认输出数据合理（无骤降至0的异常）

### 四、提交规范

- [ ] Commit type 使用 `refactor(scope):`（纯路径迁移）或 `docs(scope):`（纯文档迁移）
- [ ] Commit subject 说明"从 X 迁移至 Y"
- [ ] Commit body 列出三类引用方的修改统计（如"修改 md 链接 N 处、脚本硬编码 M 处、x-toml-ref K 处"）
- [ ] 如迁移过程发现旧路径假设导致的Bug，使用 `fix(scope):` 并附加 `[prevent: rule-update]` 标记（引用本清单）

---

## 反例警示（来自真实事故）

| 错误操作 | 后果 | 应采取的正确做法 |
|---------|------|----------------|
| 迁移目录后只更新 Markdown 链接，不 Grep 脚本 | 脚本硬编码路径静默失效，统计返回0值，污染正式档案3天 | 三类引用方全量扫描，脚本路径最优先 |
| 路径不存在时让函数静默返回0/空列表 | 问题被掩盖，无任何报错，CI全绿但数据错误 | 关键源路径不存在时抛出异常（参考 StatsSourceError 模式） |
| 仅修改立即报错的引用点 | 级联遗漏分天暴露（D1改md链接、D2改toml、D3发现stats断链） | 迁移前完成全量扫描，一次性闭环 |
| 不更新帮助文本/注释中的旧路径 | 后续维护者被过时注释误导，重复引入旧路径 | 帮助文本与注释同步更新 |
| 依赖自动CI发现路径问题 | 若无对应检查项，CI全绿但功能已坏（CI只能覆盖它检查的维度） | 迁移后手动冒烟测试关键脚本输出 |

---

## 快速参考：三类引用方扫描命令速查表

```bash
# ====== 扫描旧路径 <OLD_PATH> 的所有引用方 ======
# 替换 <OLD_PATH> 为实际路径片段，如 "docs/retrospective"

# 1. Markdown 链接 + frontmatter
grep -rn "<OLD_PATH>" --include="*.md" .

# 2. x-toml-ref 字段
grep -rn "x-toml-ref:.*<OLD_PATH>" --include="*.md" .

# 3a. Python 脚本硬编码（字符串/Path构造）
grep -rn "<OLD_PATH>" --include="*.py" .agents/scripts/

# 3b. Shell/PowerShell 脚本
grep -rn "<OLD_PATH>" --include="*.sh" --include="*.ps1" .

# 3c. CI 工作流
grep -rn "<OLD_PATH>" .github/workflows/

# 4. 配置文件
grep -rn "<OLD_PATH>" --include="*.toml" --include="*.ini" --include="*.cfg" .
```

---

## 附录：单份迁移影响清单模板

迁移执行前，按下表记录所有引用点，迁移时逐项打勾：

| # | 文件路径 | 引用类型(md/toml/py/sh/yml) | 引用位置(行号) | 处理方式 | 处理状态 |
|---|---------|---------------------------|---------------|---------|---------|
| 1 | `example.md` | md | L25 | 相对路径更新 | ☐ |
| 2 | `docgen.py` | py | L614 | Path构造改为agents/"docs"/... | ☐ |
| ... | ... | ... | ... | ... | ☐ |
