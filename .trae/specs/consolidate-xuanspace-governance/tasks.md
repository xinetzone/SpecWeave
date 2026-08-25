---
id: "consolidate-xuanspace-governance-tasks"
source: "../../.agents/docs/retrospective/2026-08-25-xuanspace-milestone-retro.md"
---

# Tasks

- [ ] Task 1：统一版本与 Python 要求为单一可信源（对应 A1）
  - [ ] SubTask 1.1：确认根 `pyproject.toml` 为唯一可信源，核对 CHANGELOG/README/AGENTS.md 中的 `requires-python`（3.13+ 与 3.14.6+ 不一致处）
  - [ ] SubTask 1.2：将 CHANGELOG、README、AGENTS.md 中的版本声明统一到可信源
  - [ ] SubTask 1.3：同步修正 `projects/AGENTS.md`（SpecWeave 侧）对 xuanspace 的 Python 版本描述
  - [ ] SubTask 1.4：在 `xs doctor` 或新增检查脚本中实现版本一致性校验

- [ ] Task 2：明确 demo-ffi/npu-ffi 的定位标注（对应 A2）
  - [ ] SubTask 2.1：为 demo-ffi、npu-ffi 的 README 增加维护状态标注（孵化中/已归档）
  - [ ] SubTask 2.2：在根 README 项目索引中同步状态字段

- [ ] Task 3：文档化 3 个 submodule 的初始化策略（对应 A3）
  - [ ] SubTask 3.1：在 README 或 CONTRIBUTING 中说明 libs/tvm-book、vendor/caffe、vendor/tvm-ffi 的初始化时机与命令
  - [ ] SubTask 3.2：明确"延迟初始化"策略（默认不初始化，按需 `git submodule update --init <path>`）

- [ ] Task 4：更新 README 项目索引，覆盖实际子项目（对应 A4）
  - [ ] SubTask 4.1：将 caffe-ffi、demo-ffi、npu-ffi、okf、xs 等实际子项目补入「项目索引」表
  - [ ] SubTask 4.2：核对索引中的名称、状态、文档链接与实际目录一致

- [ ] Task 5：定义 AI agent 提交质量验收基线（对应 A5）
  - [ ] SubTask 5.1：确定可度量指标（测试覆盖率阈值、防回归用例数）
  - [ ] SubTask 5.2：将验收基线写入 AGENTS.md 或 `.agents/` 规则文档

# Task Dependencies

- [Task 4] 依赖 [Task 2]（索引需读取子项目状态标注）
- [Task 5] 独立，可与 [Task 1] 并行