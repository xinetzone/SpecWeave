# Pickle 序列化源码层修复知识沉淀 Spec

> **方法论编排**：场景4 知识沉淀（R→I→E 链路）
> **Session**: sc-20260723-pickle-knowledge-sediment

## Why

SpecWeave 知识库已有 `python-314-multiprocessing-fork-compat.md`（运行时兼容层：wrapper 注入强制 fork）和 `python-version-upgrade-compatibility-check.md`（升级检查清单），但**缺失源码层正本清源修复模式**——即如何从源头消除不可 pickle 对象，而非用运行时兼容层绕过。

本次沉淀的源材料来自 npuusertools 项目的 Python 3.14 DataLoader forkserver 兼容性修复实战，包含三份高质量文档：
- `DEBUG_PICKLE.md`：6 种不可序列化模式 + 3 种修复方案模板 + 验证步骤
- `PICKLE_CHECKLIST.md`：5 步诊断流程 + 代码审查附加检查项 + 错误信息对照表
- `task-summary-20260723.md`：完整任务复盘（11 测试、5 关键决策、经验萃取）

这些材料沉淀的「源码层修复」知识与已有「运行时兼容层」形成**互补闭环**，补全 Python 3.14 pickle 序列化问题的完整知识图谱。

## What Changes

- **新增 1 个代码模式**（code-patterns）：`pickle-serialization-source-fix.md` — 模块级命名类替换 lambda 的源码层修复模式，明确与已有 `python-314-multiprocessing-fork-compat.md` 的互补关系
- **新增 1 个最佳实践**（best-practices）：`dataloader-pickle-diagnosis-sop.md` — DataLoader pickle 序列化问题诊断 SOP，整合 DEBUG_PICKLE.md + PICKLE_CHECKLIST.md 精华（5 步流程 + 6 种模式识别 + 3 种修复方案 + 验证矩阵）
- **更新 2 个索引**：`code-patterns/README.md` 模式清单、`best-practices/README.md` 文档索引与快速导航
- **不修改**源材料文件（npuusertools/doc/ 下的文档保持原状，仅作为萃取来源）

## Impact

- **Affected specs**: 无（纯知识沉淀，不涉及功能 spec）
- **Affected code**: 无（仅新增/更新 `.agents/docs/` 下的 Markdown 文档）
- **Affected knowledge**:
  - `.agents/docs/retrospective/patterns/code-patterns/` 新增 1 个模式文件
  - `.agents/docs/knowledge/best-practices/` 新增 1 个实践文档
  - 上述两个目录的 README.md 索引同步更新
- **互补关系**：与已有的 `python-314-multiprocessing-fork-compat.md`、`python-version-upgrade-compatibility-check.md`、`wrapper-script-injection-pattern.md` 形成「运行时兼容层 + 源码层修复 + 升级检查 + 诊断 SOP」四位一体的知识闭环

## ADDED Requirements

### Requirement: 源码层 Pickle 序列化修复模式

系统 SHALL 在 code-patterns 库提供「模块级命名类替换 lambda」的源码层修复模式文档，包含以下要素：
- 触发场景（可改源码场景，与运行时兼容层场景对比）
- 三种修复方案（命名类 / 命名函数 / functools.partial）及适用条件
- pickle 序列化四条黄金法则（模块级别 / 无 lambda / 无状态 / 可导入）
- 反模式（在 `__call__` 加日志、改函数签名、零收益重构）
- 与 `python-314-multiprocessing-fork-compat.md` 的互补关系声明

#### Scenario: 可修改源码的 lambda pickle 修复
- **WHEN** 开发者遇到 `PicklingError: Can't pickle <function <lambda>>` 且可修改源码
- **THEN** 参考源码层修复模式，将 lambda 替换为模块级 `IdentityTransform` 类，通过 `pickle.dumps()` 验证可序列化

#### Scenario: 不可修改源码的兼容性修复
- **WHEN** 开发者遇到同类问题但源码不可修改（编译型包/第三方库）
- **THEN** 转而参考 `python-314-multiprocessing-fork-compat.md` 的运行时兼容层方案

### Requirement: DataLoader Pickle 诊断 SOP

系统 SHALL 在 best-practices 库提供 DataLoader pickle 序列化问题诊断 SOP 文档，整合诊断指南与检查清单的精华，包含：
- 5 步诊断流程（复现 → 定位 → 识别 → 修复 → 验证）
- 6 种不可序列化模式对照表（lambda / 闭包 / 局部类 / 文件句柄 / 网络连接 / CUDA 张量）
- 3 种修复方案模板及适用场景
- 跨启动模式验证矩阵（fork / forkserver / spawn）
- 常见错误信息对照表
- 环境变量速查（XMN_MP_START_METHOD / XMN_DEBUG_PICKLE）

#### Scenario: 开发者按 SOP 诊断 pickle 问题
- **WHEN** 开发者遇到 DataLoader worker 启动失败且错误信息含 "pickle"
- **THEN** 按 SOP 5 步流程诊断：spawn 模式复现 → pickle.dumps 逐级定位 → 对照 6 种模式识别 → 选方案修复 → 跨模式验证

## MODIFIED Requirements

### Requirement: code-patterns 索引同步

`code-patterns/README.md` 模式清单 SHALL 新增 `pickle-serialization-source-fix.md` 条目，并在快速导航中建立与 `python-314-multiprocessing-fork-compat.md` 的关联。

### Requirement: best-practices 索引同步

`best-practices/README.md` 文档索引 SHALL 新增 `dataloader-pickle-diagnosis-sop.md` 条目，快速导航新增「序列化诊断」场景分组，并标注与 `python-version-upgrade-compatibility-check.md` 的关联。

## REMOVED Requirements

无（本 spec 为纯新增知识沉淀，不删除任何现有内容）
