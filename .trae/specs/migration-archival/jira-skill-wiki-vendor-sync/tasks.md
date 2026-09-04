# Jira Skill Wiki 供应商源码同步更新 - 实施计划

## Task 1: 更新 references/source-code.md（信源先行）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 3 处 `file:///d:/.chaos/libs/tests/jira-skill/` 替换为 `file:///d:/AI/vendor/jira-skill/`
  - 第 62 行测试文件数从 "23个测试文件" 修正为 "24个 test_*.py + conftest.py（共25个 Python 文件）"
  - 在目录结构或基本信息中补充 pyproject.toml 说明：仅含 ruff/bandit 工具配置，无 `[project]` 表，运行时依赖通过 PEP 723 内联声明
  - frontmatter 从块格式改为 inline flow：`generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }` 和 `verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }`
  - stale_after 更新为 "2027-08-29T00:00:00Z"
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Completion Evidence**:
  - frontmatter 已改为 inline flow（Read 第 6-9 行确认）
  - 3 处 file:/// 路径已更新为 vendor/jira-skill（Read 第 11-17 行确认）
  - 测试文件数已修正为 "24个 test_*.py + conftest.py（共25个 Python 文件）"（Read 第 58 行确认）
  - pyproject.toml 描述已补充 "仅含 ruff/bandit 工具配置，无 [project] 表"（Read 第 59 行确认）
  - stale_after 更新为 2027-08-29

## Task 2: 更新 references/api-reference.md（信源先行）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 4 处 `file:///d:/.chaos/libs/tests/jira-skill/` 替换为 `file:///d:/AI/vendor/jira-skill/`
  - 在 changelog.py 部分补全 4 个遗漏函数：
    - `parse_jira_datetime(s: str) -> datetime` — 解析 Jira ISO 8601 日期时间字符串
    - `extract_status_transitions_with_authors(issue: dict) -> list[dict]` — 提取状态变更记录（含作者信息）
    - `find_transition_window(transitions: list[dict], target_index: int) -> tuple[datetime | None, datetime | None]` — 查找指定转换的时间窗口
    - `format_timedelta(delta: timedelta) -> str` — 将 timedelta 格式化为人类可读字符串
  - frontmatter 同 Task 1 格式更新，verified.by 改为 "process:seven-concepts-v"
  - stale_after 更新为 "2027-08-29T00:00:00Z"
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-7
- **Completion Evidence**:
  - frontmatter 已改为 inline flow（Read 第 6-9 行确认）
  - 4 处 file:/// 路径已更新为 vendor/jira-skill（Read 第 11-20 行确认）
  - changelog.py 部分列出全部 7 个函数（Read 第 358-367 行确认）
  - compute_time_in_status 签名已与源码逐字核对（Read 源码第 55-60 行）
  - stale_after 更新为 2027-08-29

## Task 3: 更新 references/official-docs.md（信源先行）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - frontmatter 从块格式改为 inline flow，verified.by 从 "manual-verification" 改为 "process:seven-concepts-v"
  - generated.at 和 verified.at 更新为 "2026-08-29T00:00:00Z"
  - stale_after 更新为 "2027-08-29T00:00:00Z"
  - 正文内容不做修改（外部 URL 已验证有效）
- **Acceptance Criteria Addressed**: AC-2
- **Completion Evidence**:
  - frontmatter 已改为 inline flow（Read 第 6-9 行确认）
  - verified.by 已改为 "process:seven-concepts-v"
  - stale_after 从 2027-02-28 更新为 2027-08-29

## Task 4: 更新 concepts/ 批次1（00-04）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 为以下 5 个文件更新 frontmatter（块格式→inline flow，date→at，verified.by→"process:seven-concepts-v"，时间戳更新）：
    - concepts/00-overview.md
    - concepts/01-architecture.md — 额外修正第 52 行 "16 份" → "17 份"
    - concepts/02-installation.md
    - concepts/03-quickstart.md
    - concepts/04-jira-communication.md
  - stale_after 统一更新为 "2027-08-29T00:00:00Z"
  - 正文内容不做其他修改
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Completion Evidence**:
  - PowerShell 批量替换 13 个文件 frontmatter 全部成功（含本批 5 个）
  - 01-architecture.md "16 份" → "17 份" 已修正（Read 第 52 行确认）

## Task 5: 更新 concepts/ 批次2（05-09）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 为以下 5 个文件更新 frontmatter（同 Task 4 格式要求）：
    - concepts/05-jira-syntax.md
    - concepts/06-jql.md
    - concepts/07-best-practices.md
    - concepts/08-troubleshooting.md
    - concepts/09-glossary.md
  - stale_after 统一更新为 "2027-08-29T00:00:00Z"
  - 正文内容不做修改
- **Acceptance Criteria Addressed**: AC-2
- **Completion Evidence**:
  - PowerShell 批量替换 13 个文件 frontmatter 全部成功（含本批 5 个）

## Task 6: 更新 examples/ 和根 index.md

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 为以下 4 个文件更新 frontmatter：
    - examples/basic-cli-usage.md（inline flow, date→at, verified.by→"process:seven-concepts-v"）
    - examples/workflow-automation.md（同上）
    - examples/syntax-templates.md（同上）
    - index.md（根索引，仅 generated 字段改为 inline flow，无 verified 字段）
  - 所有 stale_after 更新为 "2027-08-29T00:00:00Z"
  - 正文内容不做修改
- **Acceptance Criteria Addressed**: AC-2
- **Completion Evidence**:
  - 3 个 example 文件通过 PowerShell 批量替换成功
  - 根 index.md frontmatter 已改为 inline flow（Read 第 6 行确认）
  - 根 index.md stale_after 更新为 2027-08-29（Read 第 8 行确认）

## Task 7: 更新 log.md 变更记录

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 在 log.md 顶部（标题后）新增 "## 2026-08-29：供应商源码同步" 条目
  - 记录以下变更类别：
    - 信源路径从旧临时克隆目录迁移至 `vendor/jira-skill/`（git submodule v3.29.0）
    - frontmatter 格式从块格式 `date:` 修正为 OKF v0.2 inline flow `at:`
    - 事实校正：测试文件数 23→25，参考文档数 16→17
    - API 补全：changelog.py 新增 4 个函数文档
    - pyproject.toml 描述修正（仅 ruff/bandit 配置，PEP 723 依赖）
  - 更新历史记录中的源码路径为 `d:\AI\vendor\jira-skill`
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Completion Evidence**:
  - 新增 2026-08-29 条目，含 6 项修复记录（Read 第 3-14 行确认）
  - 历史源码路径已更新为 `d:\AI\vendor\jira-skill`（Read 第 47 行确认）
  - 全文无 `.chaos` 字面量（满足 AC-1 零匹配要求）

## Task 8: V 阶段 — 独立验证与修复

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 结构检查：22 个文件全部存在
  - 路径检查：Grep `.chaos` 在整个 Bundle 中零匹配
  - Frontmatter 检查：17 个文件使用 inline flow 格式，Grep `  date:` 零匹配，Grep `generated: {` 匹配 17 次
  - 事实检查：测试文件数 25、参考文档数 17、changelog.py 7 个函数
  - API 真实性检查：Grep 验证补全的 4 个函数签名在源码中存在
  - 链接回归检查：所有 `/` 开头的 bundle-relative 链接目标存在
  - pyproject.toml 描述准确性检查
  - log.md 变更记录完整性检查
  - 发现问题逐一修复
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9
- **Completion Evidence**:
  - TR-8.1 ✅ Grep `.chaos` 零匹配
  - TR-8.2 ✅ Grep `generated: {` 匹配 17 次（17 文件各 1 次）
  - TR-8.3 ✅ Grep `  date:` 零匹配
  - TR-8.4 ✅ changelog.py 7 个函数在 api-reference.md 第 360-366 行全部存在
  - TR-8.5 ✅ 4 个新函数在源码 changelog.py 中验证：parse_jira_datetime(L9)、extract_status_transitions_with_authors(L105)、find_transition_window(L172)、format_timedelta(L194)；原有 3 个：extract_status_transitions(L20)、compute_time_in_status(L55)、classify_transition(L140)
  - TR-8.6 ✅ 100 处 bundle-relative 链接，17 个目标文件全部存在
  - TR-8.7 ✅ rubric 评分 5/5：git diff --stat 18 文件 81 增 130 删，净删除主要为 frontmatter 块→inline 格式压缩（每文件省约 3 行），正文仅事实修正和 API 补全
  - 额外验证：pyproject.toml 17 行仅含 [tool.ruff] 和 [tool.bandit]，无 [project] 表，与文档一致
  - 额外验证：stale_after 17 文件全部为 2027-08-29
  - 额外验证：verified: { 匹配 16 次（根 index.md 无 verified 符合 OKF 规范）
  - V 阶段发现并修复 1 个问题：log.md 中"8 处 file:/// URL"描述不精确，修正为"7 处 file:/// URL + 1 处 Windows 路径"
