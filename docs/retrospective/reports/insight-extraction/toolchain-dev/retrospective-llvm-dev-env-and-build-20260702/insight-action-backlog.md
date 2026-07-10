---
title: LLVM Dev环境与构建任务复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-llvm-dev-env-and-build-20260702/insight-action-backlog.toml"
project: retrospective-llvm-dev-env-and-build-20260702
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本项目所有行动计划均已在本次会话内闭环完成。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 立即执行§1 | 清理或归档构建日志避免仓库膨胀 | 高 | ✅ 已完成 | clang.log和gcc.log已移动到.temp/logs/归档 | 2026-07-02 |
| IMP-002 | 立即执行§2 | 构建说明明确推荐GCC编译器 | 高 | ✅ 已完成 | README.md和entrypoint.sh已更新，明确CC/CXX环境变量设置 | 2026-07-02 |
| IMP-003 | 立即执行§3 | 配置llvm-dev远程SSH配置 | 高 | ✅ 已完成 | ~/.ssh/config已添加llvm-dev Host配置（127.0.0.1:2222） | 2026-07-02 |
| IMP-004 | 短期执行§1 | 正式确认编译器优先级策略 | 中 | ✅ 已完成 | 默认GCC构建，Clang仅用于兼容性/质量检查；VLA初始化问题记录 | 2026-07-02 |
| IMP-005 | 短期执行§2 | Dockerfile预配置默认编译器 | 中 | ✅ 已完成 | Dockerfile已设置CC/CXX环境变量默认指向GCC | 2026-07-02 |
| IMP-006 | 短期执行§3 | "重构三步法"加入团队工程文档 | 中 | ✅ 已完成 | development-standards.md已更新，加入镜像/环境重构三步法 | 2026-07-02 |
| IMP-007 | 长期规划§1 | 评估VTA源码C++标准兼容性修复 | 低 | ✅ 已评估 | 结论：现阶段以GCC为稳定路径，未来需要Clang时再推进源码修复 | 2026-07-02 |
| IMP-008 | 长期规划§2 | Docker构建最佳实践提取为通用模板 | 低 | ✅ 已完成 | server/dev-env/README.md已新增，包含阿里云源、基础镜像复用等最佳实践 | 2026-07-02 |
| IMP-009 | 长期规划§3 | 建立定期清理旧镜像机制 | 低 | ✅ 已完成 | cleanup_images.py已新增，默认dry-run，--apply执行删除 | 2026-07-02 |

## 行动项详情

### IMP-001: 清理或归档构建日志避免仓库膨胀
- **优先级**: 高
- **来源**: export-suggestions.md §二 2.1
- **执行结果**: clang.log和gcc.log已移动到.temp/logs/目录归档，不纳入版本控制
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-002: 构建说明明确推荐GCC编译器
- **优先级**: 高
- **来源**: export-suggestions.md §二 2.1
- **执行结果**: server/dev-env/llvm-dev/docs/README.md和entrypoint.sh已更新，明确推荐使用`CC=/opt/conda/bin/gcc CXX=/opt/conda/bin/g++`环境变量构建
- **产出物**: [README.md](../../../../../README.md) + [entrypoint.sh](../../../../../../external/multica-ai/multica/docker/entrypoint.sh)
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-003: 配置llvm-dev远程SSH配置
- **优先级**: 高
- **来源**: export-suggestions.md §二 2.1
- **执行结果**: ~/.ssh/config已添加llvm-dev Host配置，包含端口2222、用户dev、KeepAlive设置等
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-004: 正式确认编译器优先级策略
- **优先级**: 中
- **来源**: export-suggestions.md §二 2.2
- **执行结果**: 正式确立策略：默认使用GCC构建，Clang仅用于兼容性检查或代码质量验证；根因是vta/vta_hw中的VLA初始化写法被GCC接受但Clang 22拒绝
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-005: Dockerfile预配置默认编译器
- **优先级**: 中
- **来源**: export-suggestions.md §二 2.2
- **执行结果**: Dockerfile已预配置CC/CXX环境变量默认指向/opt/conda/bin/gcc和g++
- **产出物**: `Dockerfile`
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-006: "重构三步法"加入团队工程文档
- **优先级**: 中
- **来源**: export-suggestions.md §二 2.2
- **执行结果**: development-standards.md已更新，镜像/环境"重构三步法"已纳入团队工程规范
- **产出物**: [development-standards.md](../../../../../development-standards.md)
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-007: 评估VTA源码C++标准兼容性修复
- **优先级**: 低
- **来源**: export-suggestions.md §二 2.3
- **执行结果**: 已完成评估，结论：当前不需要立即修改挂载源码；现阶段以GCC作为稳定构建路径，若未来必须恢复Clang全量构建，再单独推进源码标准化修复
- **状态**: ✅ 已评估
- **完成日期**: 2026-07-02

---

### IMP-008: Docker构建最佳实践提取为通用模板
- **优先级**: 低
- **来源**: export-suggestions.md §二 2.3
- **执行结果**: server/dev-env/README.md已新增，沉淀Docker构建最佳实践：阿里云源加速、基础镜像复用、默认编译器统一、去版本号命名原则等
- **产出物**: `server/dev-env/README.md`
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

---

### IMP-009: 建立定期清理旧镜像机制
- **优先级**: 低
- **来源**: export-suggestions.md §二 2.3
- **执行结果**: cleanup_images.py已新增，默认dry-run模式预览清理列表，--apply参数才会真实删除旧镜像
- **产出物**: `cleanup_images.py`
- **状态**: ✅ 已完成
- **完成日期**: 2026-07-02

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~009 | 2026-07-02 | 本次任务会话内完成 | 全部9项行动计划闭环完成，含3项高优先级环境配置、3项中优先级规范确认、3项低优先级评估/工具/文档 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件（历史项目补建，所有项已闭环）
