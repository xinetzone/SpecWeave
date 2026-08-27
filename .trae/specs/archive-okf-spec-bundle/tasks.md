---
id: archive-okf-spec-bundle-tasks
title: OKF 规范知识包归档 - 实施计划
type: Tasks
timestamp: 2026-08-21
method: seven-concepts（I→A→V→C）
---

# OKF 规范知识包归档 - 实施计划

> 方法论链路：场景3 迁移归档，裁剪为 **I → A → V → C**。
> 执行约定：每任务委托子代理完成；迁移类操作（复制/删除/路径修改）优先直接执行并验证；最终以原子提交闭环。

## [x] Task 1（I 洞察）: 迁移前准备与备份
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 确认源 bundle 完整文件清单（24 个 .md，位于 `bundles/okf-spec/`）。
  - 确认目标位置 `projects/awesome-okf-xs/bundles/okf-spec/`（目标 `bundles/` 目录不存在，需创建）。
  - 确认 awesome-okf-xs 子模块 git 状态（当前 detached HEAD @213113b，需在迁移前 checkout main 或创建归档分支）。
  - 记录受影响引用面：`okf-100ep-anime`（活跃）、`okf-spec-to-bundle`（历史，不改）。
- **Acceptance Criteria**: 源清单与受影响文件已盘点，无遗漏。
- **Test**: `git -C projects/awesome-okf-xs status` 确认仓库状态；`git -C SpecWeave status --short` 确认源 bundle 为已跟踪状态。

## [x] Task 2（A 原子化）: 复制 bundle 到目标位置
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 复制 `bundles/okf-spec/` → `projects/awesome-okf-xs/bundles/okf-spec/`，保持目录结构与文件内容逐字一致。
  - 校验文件数量（24 个 .md）与结构（concepts/examples/references/index/log）。
- **Acceptance Criteria**: 目标路径存在完整 bundle，与源一致。
- **Test**: 对比源/目标文件清单与数量；抽查 2-3 个文件内容一致。

## [x] Task 3（A 原子化）: resource 改为 GitHub 权威源
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 对 `projects/awesome-okf-xs/bundles/okf-spec/` 下 19 个文档（15 概念 + 3 示例 + 1 信源），将 frontmatter `resource: ../../../vendor/knowledge-catalog/okf/SPEC.md` 调整为 GitHub 权威源 `https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md`。
  - 不修改脚注式文字描述（"见 vendor/knowledge-catalog/okf/SPEC.md"）。
- **Acceptance Criteria**: 19 个文档 resource 均为 GitHub URL，无相对路径残留。
- **Test**: Grep 检查目标目录 `resource:` 行，确认均为 GitHub URL；无 `../../../vendor/...` 相对路径残留。

## [x] Task 4（A 原子化）: 更新目标项目 README 登记 bundle
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 在 `projects/awesome-okf-xs/README.md` 中登记新收录的 `bundles/okf-spec` bundle（含一句话简介与路径）。
- **Acceptance Criteria**: README 可见 okf-spec bundle 条目。
- **Test**: 阅读 README 确认条目存在且路径正确。

## [x] Task 5（A 原子化）: 更新活跃 spec 引用
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 更新 `okf-100ep-anime` 的 spec.md / tasks.md / checklist.md 中所有 `bundles/okf-spec/` → `projects/awesome-okf-xs/bundles/okf-spec/`。
  - `okf-spec-to-bundle`（历史）不改，保留档案。
- **Acceptance Criteria**: 活跃 spec 中无指向旧路径的残留。
- **Test**: Grep 检查 `okf-100ep-anime` 目录，确认路径均已更新。

## [x] Task 6（A 原子化）: 移除主权区源 bundle 并原子提交
- **Priority**: high
- **Depends On**: Task 3, Task 5
- **Description**:
  - 从 SpecWeave 主权区 `git rm -r bundles/okf-spec/`。
  - awesome-okf-xs 子模块内提交新增 bundle（Conventional Commits，中文描述"为什么"）。
  - SpecWeave 主仓库提交：git rm 源 bundle + 更新 gitlink + 更新 okf-100ep-anime 引用（若 Task 5 未单独提交）。
- **Acceptance Criteria**: 两仓库各自原子提交完成；主权区不再存在 `bundles/okf-spec` 路径；gitlink 已指向子模块新 commit。
- **Test**: `git -C projects/awesome-okf-xs show --stat HEAD`；`git -C SpecWeave submodule status`；`git -C SpecWeave show --stat HEAD`。

## [x] Task 7（V 对抗审查）: 迁移后等价性验证
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 文件完整性：目标 bundle 24 个 .md 全存在，结构与源一致。
  - 路径修正：Grep 目标目录 `resource:` 行，确认均为 GitHub URL，无相对路径残留。
  - 引用一致性：SpecWeave 工作区无 `bundles/okf-spec` 残留（除历史 spec 档案与 .git）；活跃 spec 引用已更新。
  - 链接有效性：目标 bundle 内部相对链接可解析，无死链。
- **Acceptance Criteria**: 全部核查通过，无回归。
- **Test**: 逐项运行 Grep/文件比对/链接检查。

## Task Dependencies
- Task 1 → Task 2（先盘点再复制）
- Task 2 → Task 3 / Task 4 / Task 5（先落位再修路径/登记/改引用）
- Task 3+5 → Task 6（路径修正与引用更新完成后才可删源并提交）
- Task 6 → Task 7（提交后做等价性验证）
