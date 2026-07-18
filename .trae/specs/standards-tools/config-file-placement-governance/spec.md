---
id: "config-file-placement-governance"
source: "用户需求：验证sitecustomize.py迁移后自动加载，并制定文件错误放置预防方案"
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/config-file-placement-governance/spec.toml"
---
# 配置文件放置治理与自动加载验证 Spec

## Why

刚完成的文件归档将 `sitecustomize.py`、`setup-utf8-env.ps1`、`thesis-writing-guide/`、`RETROSPECTIVE-CI-PATH-MIGRATION-20260718.md` 从项目根目录迁移到 `.agents/` 下对应位置。其中 `sitecustomize.py` 的迁移最敏感——它是 Python 启动时由 `site` 模块自动加载的约定文件，迁移后能否在新终端会话中自动加载取决于 PYTHONPATH 是否正确配置。本次需要：
1. 用可复现的运行时验证确认迁移未破坏自动加载行为
2. 沉淀文件放置治理机制，避免同类关键配置文件再次被错误放置到根目录

## What Changes

- 新增 **sitecustomize.py 自动加载验证脚本**：可复现地检查新终端会话中 sitecustomize.py 是否被 Python 自动加载，覆盖三种场景（裸终端 / 已运行 setup-utf8-env.ps1 / 已加载 profile.ps1）
- 新增 **关键配置文件放置校验脚本**：扫描项目根目录与 `.agents/scripts/`，检测关键配置文件是否被错误放置到根目录
- 新增 **`.temp/` 生命周期治理脚本**：按用途分类检查 `.temp/` 下内容的保留期，输出过期清单并支持 `--clean` 清理
- 新增 **文件放置治理文档**：在 `.agents/docs/knowledge/best-practices/` 下沉淀关键配置文件的标准存放路径表、放置决策树，以及 `.temp/` 临时文件治理约定（定义、用途分类、命名规则、保留期、清理机制、责任人）
- 新增 **预提交钩子集成**：将放置校验脚本与 `.temp` 生命周期检查接入 `.githooks/` 与 CI 质量门禁，阻止错误放置的文件进入仓库，并告警/阻塞过期临时内容
- **不修改**已迁移的 sitecustomize.py 本身（保持三层防御逻辑不变）
- **不修改** `.gitignore` 中已存在的 `.temp/` 排除规则（保留"可随时清理"语义，由生命周期脚本提供确定性清理而非依赖人工记忆）

## Impact

- **Affected specs**: `fix-windows-terminal-chinese-encoding`（原创建 spec，已完成，仅作为溯源参考）、`migrate-docs-into-agents-docs`（曾产生 `.temp/backup/docs-before-agents-docs-20260715/`，已清理，本 spec 沉淀此类备份的保留期规则避免复发）
- **Affected code**:
  - 新增：`.agents/scripts/verify-sitecustomize-autoload.py`（验证脚本）
  - 新增：`.agents/scripts/check-file-placement.py`（放置校验脚本）
  - 新增：`.agents/scripts/check-temp-lifecycle.py`（`.temp/` 生命周期检查与清理脚本）
  - 新增：`.agents/docs/knowledge/best-practices/config-file-placement-convention.md`（治理文档，含 `.temp/` 治理小节）
  - 修改：`.agents/scripts/lib/checks/`（新增 `file_placement` 与 `temp_lifecycle` 检查模块，供 ci-check 集成）
  - 修改：`.githooks/pre-commit`（追加放置校验与 `.temp` 生命周期调用）
- **Affected docs**: `windows-terminal-utf8-complete-guide.md`、`windows-platform-compatibility-guide.md`（补充自动加载验证小节）
- **Affected config**: `.gitignore`（不修改内容，但治理文档需引用其第 2 行 `.temp/` 规则作为溯源依据）

## ADDED Requirements

### Requirement: sitecustomize.py 自动加载验证

系统 SHALL 提供一个可独立运行的 Python 验证脚本，用于确认 `sitecustomize.py` 在新终端会话中被 Python `site` 模块自动加载。

#### Scenario: 裸终端（未加载 profile、未运行 setup 脚本）

- **WHEN** 用户在未加载 profile.ps1 且未运行 setup-utf8-env.ps1 的新终端中执行验证脚本
- **THEN** 脚本报告 PYTHONPATH 未包含 `.agents/scripts/`，sitecustomize.py 不会被自动加载
- **AND** 脚本提示用户运行 `.\.agents\scripts\setup-utf8-env.ps1` 或加载 profile 以启用自动加载
- **AND** 脚本以非零退出码退出（标识需要配置）

#### Scenario: 已持久化 PYTHONPATH 的新终端

- **WHEN** 用户曾运行 `setup-utf8-env.ps1 -Scope User`（PYTHONPATH 已持久化），在新终端中执行验证脚本
- **THEN** 脚本报告 `.agents/scripts/` 在 sys.path 中
- **AND** 脚本报告 `import sitecustomize` 成功且 `sitecustomize.__file__` 指向 `.agents/scripts/sitecustomize.py`
- **AND** 脚本报告 stdout/stderr 编码为 utf-8（sitecustomize 的 _reconfigure_std_streams 副作用）
- **AND** 脚本以零退出码退出

#### Scenario: 已加载 profile.ps1 的终端

- **WHEN** 用户在已加载 profile.ps1（profile 已设置 PYTHONPATH）的终端中执行验证脚本
- **THEN** 验证结果与"已持久化 PYTHONPATH"场景一致
- **AND** 脚本以零退出码退出

#### Scenario: sitecustomize.py 被错误放回根目录

- **WHEN** 项目根目录存在 `sitecustomize.py`（被错误放回）
- **THEN** 脚本发出警告：根目录存在 sitecustomize.py，可能与 .agents/scripts/ 版本冲突
- **AND** 脚本建议删除根目录的副本

### Requirement: 关键配置文件放置校验

系统 SHALL 提供一个放置校验脚本，检测关键配置文件是否被错误放置到项目根目录。

#### Scenario: 关键文件全部在正确位置

- **WHEN** 运行放置校验脚本，所有受管关键文件均位于 `.agents/scripts/` 或其他指定位置
- **THEN** 脚本报告所有文件位置正确
- **AND** 脚本以零退出码退出

#### Scenario: 关键文件被错误放置到根目录

- **WHEN** 运行放置校验脚本，检测到 `sitecustomize.py`、`setup-utf8-env.ps1` 或其他受管文件出现在项目根目录
- **THEN** 脚本列出每个错误放置的文件及其正确位置
- **AND** 脚本以非零退出码退出

#### Scenario: CI/预提交集成

- **WHEN** 预提交钩子或 CI 流水线调用放置校验脚本
- **THEN** 若存在错误放置的文件，提交/CI 失败并显示修复指引
- **AND** 若全部正确，提交/CI 通过此检查项

### Requirement: 文件放置治理文档

系统 SHALL 在 `.agents/docs/knowledge/best-practices/` 下提供一份配置文件放置约定文档，覆盖关键配置文件放置规则与 `.temp/` 临时文件治理约定。

#### Scenario: 团队成员查阅放置约定

- **WHEN** 团队成员需要决定某个配置文件的存放位置
- **THEN** 文档提供关键配置文件的标准路径表（含 sitecustomize.py、setup-utf8-env.ps1、profile.ps1、pth 文件等）
- **AND** 文档提供放置决策树：判断"应放根目录"还是"应放 .agents/scripts/"的依据
- **AND** 文档说明 Python 自动加载约定（sitecustomize.py、.pth 文件）与 PYTHONPATH 的关系

#### Scenario: 团队成员查阅 .temp 治理约定

- **WHEN** 团队成员需要决定某个临时产物的存放位置或清理时机
- **THEN** 文档提供 `.temp/` 治理小节，包含以下完整规范：
  - **定义**：`.temp/` 是项目根目录下由 `.gitignore` 第 2 行排除的临时文件目录，语义为"可随时清理"，存放任务执行过程中的中间产物
  - **用途分类**（按子目录组织）：
    - `backup/`：迁移/重构前的备份快照
    - `experiments/`：实验性脚本（PoC、调试工具、一次性脚本）
    - `exports/`：临时数据导出（报告草稿、中间数据集）
    - `screenshots/`：调试截图、临时图片产物
  - **命名规则**：子目录与文件名必须包含创建日期（`YYYYMMDD`）或关联 task-id；格式为 `{purpose}/{task-id-or-date}-{描述}/` 或 `{purpose}/{date}-{描述}.{ext}`；示例 `backup/docs-migration-20260715/`、`experiments/color-palette-20260718/`
  - **存储位置**：仅限项目根目录 `.temp/`，禁止散落到其他目录（如根目录直接放临时文件、`.agents/` 下放临时文件）
  - **保留期**（按用途分类）：`backup/` 类 3 天；`experiments/`、`exports/`、`screenshots/` 类 14 天；未分类根级文件 7 天
  - **清理机制**：手动执行 `python .agents/scripts/check-temp-lifecycle.py` 查看过期清单；加 `--clean` 参数交互式清理；CI 质量门禁自动检测（详见生命周期治理 Requirement）
  - **责任人**：创建者（开发者/智能体）负责正确命名、任务完成后主动清理；CI/预提交钩子负责自动检测过期内容；项目维护者定期审查
- **AND** 文档引用 `.gitignore` 第 2 行 `.temp/` 规则作为"可随时清理"语义的溯源依据
- **AND** 文档记录反模式：禁止在 `.temp/` 外放置临时文件、禁止创建无日期无 task-id 的内容、禁止依赖人工记忆清理（必须由脚本驱动）

### Requirement: 预提交钩子与 CI 集成

系统 SHALL 在预提交钩子和 CI 质量门禁中集成放置校验与 `.temp/` 生命周期检查。

#### Scenario: 预提交触发校验

- **WHEN** 开发者执行 git commit
- **THEN** pre-commit 钩子调用 `check-file-placement.py`
- **AND** 若检测到错误放置的文件，提交被阻止并显示修复指引
- **AND** pre-commit 钩子调用 `check-temp-lifecycle.py`（只读模式，不清理）
- **AND** 若检测到超过 30 天的 `.temp/` 内容，提交被阻止并提示运行 `--clean` 清理

#### Scenario: CI 质量门禁触发校验

- **WHEN** CI 流水线运行质量门禁检查
- **THEN** 质量门禁脚本调用 `check-file-placement.py` 作为其中一个检查项
- **AND** 质量门禁脚本调用 `check-temp-lifecycle.py`（只读模式）作为另一个检查项
- **AND** 检测到超过 14 天的 `.temp/` 内容时，CI 报警告（不阻塞流水线）
- **AND** 检测到超过 30 天的 `.temp/` 内容时，CI 报错误（阻塞流水线）
- **AND** 两项检查结果均纳入 CI 通过/失败判定与 CI 报告

### Requirement: .temp 临时文件生命周期治理

系统 SHALL 提供 `.temp/` 生命周期检查脚本 `check-temp-lifecycle.py`，按用途分类检测 `.temp/` 下内容的保留期，支持只读检查与交互式清理。

#### Scenario: 创建临时文件时遵循命名约定

- **WHEN** 开发者或智能体在 `.temp/` 下创建新的子目录或文件
- **THEN** 路径必须以用途分类前缀开头（`backup/`、`experiments/`、`exports/`、`screenshots/`）
- **AND** 名称必须包含创建日期（`YYYYMMDD`）或关联的 task-id
- **AND** 合规示例：`.temp/backup/docs-migration-20260715/`、`.temp/experiments/color-palette-20260718/`
- **AND** 不合规示例（被命名校验告警）：`.temp/record.md`（无用途前缀、无日期）、`.temp/backup/old/`（无日期）

#### Scenario: 检测到命名不合规的临时内容

- **WHEN** 运行 `check-temp-lifecycle.py`，检测到 `.temp/` 下存在无日期或无用途前缀的内容
- **THEN** 脚本列出每个不合规项及告警原因（缺少日期 / 缺少用途前缀）
- **AND** 脚本建议重命名为合规格式，但不自动重命名
- **AND** 此场景以非零退出码退出（命名不合规视为需修复项）

#### Scenario: 临时文件超过保留期

- **WHEN** 运行 `check-temp-lifecycle.py`，检测到超过保留期的内容
  - `backup/` 类：保留期 3 天
  - `experiments/`、`exports/`、`screenshots/` 类：保留期 14 天
  - 未分类根级文件：保留期 7 天
- **THEN** 脚本列出每个过期项及其用途分类、创建日期、保留期、已存活天数
- **AND** 脚本按用途分组汇总（如"backup 类过期 2 项、experiments 类过期 1 项"）
- **AND** 脚本建议执行清理命令：`python .agents/scripts/check-temp-lifecycle.py --clean`

#### Scenario: 交互式清理过期临时内容

- **WHEN** 开发者执行 `python .agents/scripts/check-temp-lifecycle.py --clean`
- **THEN** 脚本先列出所有过期项并按用途分组展示
- **AND** 脚本请求用户确认（`y/N`）后才执行删除
- **AND** 确认后删除过期内容，保留未过期内容与命名不合规内容（不合规项需人工处理）
- **AND** 脚本输出清理摘要：删除项数、释放空间（MB）、剩余项数
- **AND** `--clean --yes` 参数可跳过确认（用于自动化场景，需谨慎）

#### Scenario: .temp 目录为空或不存在

- **WHEN** 运行 `check-temp-lifecycle.py`，`.temp/` 目录为空或不存在
- **THEN** 脚本报告"无临时内容需检查"
- **AND** 脚本以零退出码退出

#### Scenario: 保留期基准日期的确定

- **WHEN** 脚本计算某个 `.temp/` 项的存活天数
- **THEN** 基准日期优先取名称中解析出的 `YYYYMMDD` 日期
- **AND** 若名称无日期，则取文件系统修改时间（mtime）作为回退基准
- **AND** 脚本在输出中标注每项的基准日期来源（"名称解析"或"文件 mtime"）
