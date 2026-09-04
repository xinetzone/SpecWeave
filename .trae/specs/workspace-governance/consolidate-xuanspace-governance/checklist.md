---
id: "consolidate-xuanspace-governance-checklist"
source: "../../.agents/docs/retrospective/2026-08-25-xuanspace-milestone-retro.md"
---

# Checklist

## 版本与 Python 要求一致（Task 1）
- [ ] 根 `pyproject.toml` 的 `requires-python` 与 CHANGELOG、README、AGENTS.md 一致
- [ ] `projects/AGENTS.md`（SpecWeave 侧）对 xuanspace 的 Python 版本描述已同步
- [ ] caffe-ffi 的 pyproject/CMakeLists/`__init__.py` 版本号与 CHANGELOG 一致
- [ ] 版本一致性检查已接入 `xs doctor` 或专用脚本，可检出不一致

## 子项目定位标注（Task 2）
- [ ] demo-ffi 有明确维护状态标注
- [ ] npu-ffi 有明确维护状态标注
- [ ] 根 README 索引的状态字段与标注一致

## submodule 初始化策略（Task 3）
- [ ] 文档说明 libs/tvm-book、vendor/caffe、vendor/tvm-ffi 的初始化时机
- [ ] 提供具体初始化命令（`git submodule update --init <path>`）
- [ ] 明确"延迟初始化"策略，消除"未初始化即未开发"的歧义

## README 项目索引完整（Task 4）
- [ ] 索引覆盖 caffe-ffi、demo-ffi、npu-ffi、xuan-core、xuan-ext-demo、tvm-book
- [ ] 索引覆盖 tools/（xs、okf）
- [ ] 索引名称、状态、文档链接与实际目录一致

## agent 提交验收基线（Task 5）
- [ ] 定义了可度量的质量指标（测试覆盖率阈值、防回归用例数）
- [ ] 验收基线写入 AGENTS.md 或 `.agents/` 规则文档
- [ ] 基线可被 agent 提交流程引用为验收依据