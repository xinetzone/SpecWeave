---
id: "consolidate-xuanspace-governance-spec"
source: "../../.agents/docs/retrospective/2026-08-25-xuanspace-milestone-retro.md"
---

# xuanspace 治理加固 Spec

## Why

里程碑复盘发现 xuanspace 在一阶段（2026-07-24 ~ 2026-08-19，314 次提交）存在 4 类治理缺口：版本/Python 要求多处不一致、demo-ffi/npu-ffi 等子项目定位模糊、3 个 submodule 未初始化且无策略、README 项目索引与实际目录脱节。此外，70% 提交来自 AI agent，但缺少可审计的质量验收基线。

## What Changes

- 建立版本号与 Python 要求（`requires-python`）的单一可信源，并纳入检查工具
- 为 libs/ 各子项目明确维护状态（活跃 / 孵化中 / 已归档）
- 为 3 个未初始化 submodule（libs/tvm-book、vendor/caffe、vendor/tvm-ffi）提供文档化初始化策略
- 更新根 README「项目索引」，完整覆盖实际子项目（caffe-ffi、demo-ffi、npu-ffi、okf、xs）
- 定义 AI agent 提交的可审计质量指标（测试覆盖率、防回归用例数）
- 以上均为文档与治理工具变更，**无运行时行为破坏**（无 **BREAKING**）

## Impact

- Affected specs：新 spec（本文件），与既有 [xuanspace-mono-repo](../../../.trae/specs/xuanspace-mono-repo/spec.md) 的 FR-3/FR-6/FR-9/FR-35 相关
- Affected code：`projects/xuanspace/CHANGELOG.md`、`projects/xuanspace/README.md`、`projects/xuanspace/AGENTS.md`、`projects/xuanspace/pyproject.toml`、`projects/xuanspace/.gitmodules`、`libs/caffe-ffi` 版本文件、`tools/xs/src/xs/commands/doctor.py`（如需）

## MODIFIED Requirements

### Requirement: 版本与 Python 要求单一可信源

项目 SHALL 以根 `pyproject.toml` 作为版本号与 `requires-python` 的唯一可信源，CHANGELOG、README、AGENTS.md 中的相关声明 SHALL 与该源保持一致，并由检查工具校验。

#### Scenario: 一致性检查发现偏差

- **WHEN** 运行 `xs doctor`（或专用一致性检查）
- **THEN** 输出 CHANGELOG/README/AGENTS.md 与 pyproject.toml 之间版本号或 `requires-python` 不一致的位置及修正建议

#### Scenario: 修改 trusted source 后同步提示

- **WHEN** 修改根 `pyproject.toml` 的 `version` 或 `requires-python`
- **THEN** 检查工具能列出需要同步的文档位置（CHANGELOG/README/AGENTS.md/projects 侧描述）

### Requirement: README 项目索引完整覆盖

根 README「项目索引」SHALL 覆盖所有实际存在的子项目，与实际目录结构一致。

#### Scenario: 索引与目录一致

- **WHEN** 打开根 README 的「项目索引」表
- **THEN** 列出 libs/（caffe-ffi、demo-ffi、npu-ffi、xuan-core、xuan-ext-demo、tvm-book）与 tools/（xs、okf）的实际子项目，且名称、状态、文档链接准确

## ADDED Requirements

### Requirement: 子项目维护状态标注

每个 libs/ 子项目 SHALL 拥有明确的维护状态标注（活跃 / 孵化中 / 已归档），消除"空壳目录是否开发中"的模糊状态。

#### Scenario: 识别空壳子项目状态

- **WHEN** 查看 demo-ffi 或 npu-ffi 的 README 或根索引
- **THEN** 能明确判断该子项目属"孵化中"还是"已归档"

### Requirement: submodule 初始化策略文档化

项目 SHALL 为未初始化的 submodule（libs/tvm-book、vendor/caffe、vendor/tvm-ffi）提供书面初始化策略。

#### Scenario: 新贡献者初始化

- **WHEN** 新贡献者 clone 仓库后查阅文档
- **THEN** 能明确知道哪些 submodule 需初始化、何时初始化、执行 `git submodule update --init <path>` 的具体命令

### Requirement: AI agent 提交质量验收基线

项目 SHALL 定义 AI agent 提交的可审计质量指标，作为 agent 提交的验收基线。

#### Scenario: agent 提交的验收依据

- **WHEN** AI agent 完成一次提交
- **THEN** 存在可度量的质量指标（测试覆盖率阈值、防回归用例数）作为该提交是否合入的验收依据