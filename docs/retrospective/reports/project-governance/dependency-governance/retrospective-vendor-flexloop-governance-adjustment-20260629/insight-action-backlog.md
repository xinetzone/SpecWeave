---
title: "flexloop子模块治理模式调整复盘 - 洞察行动项 Backlog"
version: "1.0"
date: "2026-07-06"
type: insight-action-backlog
source: "export-suggestions.md"
project: retrospective-vendor-flexloop-governance-adjustment-20260629
template_upgrade: "2026-07-06 v1.2"
scenario: "B-single-task-light"
---

# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） |
|---|---|---|---|---|---|
| IMP-001 | 建议1 | 修复flexloop存量反向依赖链接 | P0 | 📋 待执行 | `repo-check.py vendor --deep` 0错误 |
| IMP-002 | 建议2 | 沉淀双模式治理等5个模式到模式库 | P1 | 📋 待执行 | 5个模式文档创建完成，模式库索引更新 |
| IMP-003 | 建议3 | 反向依赖检测添加文件类型过滤配置 | P1 | 📋 待规划 | vendor.py支持文件类型过滤，默认仅检查代码文件 |
| IMP-004 | 建议4 | 沙箱写入路径强制限制升级 | P2 | 📋 待规划 | 沙箱能可靠阻止脚本写入白名单外路径 |
| IMP-005 | 建议5 | 添加子模块开发状态检查与提交指引 | P2 | 📋 待规划 | vendor check错误/警告信息包含明确可操作指引 |

## 行动项详情

### IMP-001: 修复flexloop存量反向依赖链接
- **优先级**: P0（高）
- **来源**: export-suggestions.md §建议1
- **问题描述**: 提交后验证发现flexloop子模块内有8处Markdown反向依赖链接，指向`../../../apps/chaos/.agents/`路径
- **涉及文件**:
  - `docs/topics/designer-deviation.md` L75、L106
  - `docs/topics/doc-ahead-of-implementation.md` L117
  - `docs/topics/extraction-methodology.md` L125、L139
  - `docs/topics/governance-gap.md` L131
  - `docs/topics/philosophy-as-dao.md` L136
  - `docs/topics/retrospective-rethinking.md` L143
  - `docs/topics/skeleton-vs-runtime.md` L123
- **可选方案**:
  - 方案A：在flexloop仓库内修复链接（改为内部文档或标记为外部链接）
  - 方案B：反向依赖检测添加"仅检查代码文件"配置选项
  - 方案C：改为绝对URL（如有线上文档）
- **建议产出物**: flexloop子模块内Markdown链接修复
- **验收标准**: `repo-check.py vendor --deep` 0错误
- **状态**: 📋 待执行

---

### IMP-002: 沉淀双模式治理等5个模式到模式库
- **优先级**: P1（中）
- **来源**: export-suggestions.md §建议2
- **说明**: 将本次复盘中萃取的5个可复用模式入库
- **模式清单**:
  | 模式名称 | 建议入库路径 | 成熟度 |
  |---------|------------|--------|
  | 双模式子模块治理框架 | [governance-strategy/dual-mode-submodule-governance.md](../../../../patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md) | L2 |
  | 新检测规则存量暴露效应 | [tools-automation/legacy-exposure-effect.md](../../../../patterns/methodology-patterns/tools-automation/legacy-exposure-effect.md) | L2 |
  | 跨平台输出编码强制设置 | [cross-platform-encoding-enforcement.md](../../../../patterns/code-patterns/cross-platform-encoding-enforcement.md) | L2 |
  | 临时路径修改条件导入 | [temporary-syspath-modification.md](../../../../patterns/code-patterns/temporary-syspath-modification.md) | L2 |
  | 路径锚点语义化 | [path-anchor-semantization.md](../../../../patterns/code-patterns/path-anchor-semantization.md) | L1 |
- **建议产出物**: 5个模式文档创建+索引更新
- **验收标准**: 5个模式文档创建完成，模式库索引更新
- **状态**: 📋 待执行

---

### IMP-003: 反向依赖检测添加文件类型过滤配置
- **优先级**: P1（中）
- **来源**: export-suggestions.md §建议3
- **问题描述**: 当前`_check_reverse_dependency`检查所有文件类型，Markdown历史链接、注释路径示例不应被视为"反向依赖"
- **功能需求**:
  - 仅检查`.py`代码文件的import/路径引用
  - Markdown链接可配置为warning或忽略
  - 注释中的路径不检查
- **建议产出物**: [vendor.py](../../../../../../.agents/scripts/lib/checks/vendor.py) 更新
- **验收标准**: vendor.py支持文件类型过滤配置，默认仅检查代码文件
- **状态**: 📋 待规划

---

### IMP-004: 沙箱写入路径强制限制升级
- **优先级**: P2（低）
- **来源**: export-suggestions.md §建议4
- **问题描述**: 当前`run_flexloop_script()`仅通过cwd和环境变量约定，无强制阻止写入其他路径
- **可选方案**:
  - 方案A：使用`tempfile.TemporaryDirectory`作为工作目录
  - 方案B：操作系统级权限控制（Windows DACL/Linux chroot）
  - 方案C：子进程中拦截文件系统调用（复杂，不推荐）
- **建议产出物**: [vendor_sandbox.py](../../../../../../.agents/scripts/lib/vendor_sandbox.py) 升级
- **验收标准**: 沙箱能可靠阻止脚本写入白名单外路径（测试脚本验证）
- **状态**: 📋 待规划

---

### IMP-005: 添加子模块开发状态检查与提交指引
- **优先级**: P2（低）
- **来源**: export-suggestions.md §建议5
- **问题描述**: vendor check发现子模块状态异常时只报告状态，无操作指引
- **功能需求**:
  - 子模块有未提交修改时：提示commit/push或提交子模块指针更新
  - 子模块ahead of remote时：提示推送到flexloop远程仓库
  - 添加`--fix`选项辅助处理（如自动打开子模块目录）
- **建议产出物**: [check-vendor.py](../../../../../../.agents/scripts/check-vendor.py) 提示信息优化
- **验收标准**: vendor check错误/警告信息包含明确的可操作指引
- **状态**: 📋 待规划

---

## 相关资源索引

- **可复用模式库**: [patterns/](../../../../patterns/)
- **技术知识库**: [knowledge/](../../../../../knowledge/)
- **子模块治理规范**: [VENDOR-INTEGRATION.md](../../../../../knowledge/VENDOR-INTEGRATION.md)
- **双模式检查脚本**: [vendor.py](../../../../../../.agents/scripts/lib/checks/vendor.py)
- **运行时沙箱**: [vendor_sandbox.py](../../../../../../.agents/scripts/lib/vendor_sandbox.py)

---

## Changelog

<!-- changelog -->
- 2026-07-06 | docs | v1.2模板轻量升级：创建insight-action-backlog.md，结构化记录5项待执行改进项
