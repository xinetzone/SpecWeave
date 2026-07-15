---
title: XMNN目录复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-xmnn-folder-20260701/insight-action-backlog.toml"
project: retrospective-xmnn-folder-20260701
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本项目方法论已在npu-project-hub中完成跨项目复用验证，xmnn本体改进项待推进。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 行动项§P0 | 明确xmnn的"包形态"边界（module vs package） | P0 | ⏳ 待办 | 文档与实际import行为一致；不再出现"同名但语义不同"的歧义 | - |
| IMP-002 | 行动项§P1-1 | 拆分依赖为runtime/dev/extras三层 | P1 | ⏳ 待办 | pip install xmnn安装体积与依赖数量显著降低；pip install xmnn[frontends]仍可获得完整前端能力 | - |
| IMP-003 | 行动项§P1-2 | 离线闭环制度化 | P1 | ⏳ 待办 | 纯离线环境可构建或可运行（明确二选一策略）；有网络时可启用extras | - |
| IMP-004 | 行动项§P2-1 | 运行时基线/兼容性声明与自动校验 | P2 | ⏳ 待办 | 构建产物能自描述其绑定的LLVM/系统库基线；运行时启动阶段能检测出明显不匹配 | - |
| IMP-005 | 行动项§P2-2 | 统一与校准交付文档引用路径 | P2 | ⏳ 待办 | client/README.md等文档的链接不指向不存在路径；交付入口清晰可追溯 | - |
| IMP-006 | 下一步方向§维护规则 | 方法论复用状态回写维护规则 | P2 | ⏳ 待办 | 建议在其他真实工程落地后回写"复用验证状态"，文档从一次性复盘升级为持续演进模式库 | - |

## 行动项详情

### IMP-001: 明确xmnn的"包形态"边界（module vs package）
- **优先级**: P0
- **来源**: export-suggestions.md §一 行动项
- **可选实现方向**:
  - 方案A：把site-packages/xmnn/数据目录改为site-packages/xmnn_data/（避免与扩展模块同名）
  - 方案B：保留xmnn/目录，但让其成为明确的Python package（含__init__.py），并把扩展模块更名为xmnn_core（避免import歧义）
- **复用验证**: 包边界原则在npu-project-hub中已验证有效
- **状态**: ⏳ 待办
- **执行结果**: -

---

### IMP-002: 拆分依赖为runtime/dev/extras三层
- **优先级**: P1
- **来源**: export-suggestions.md §一 行动项 + §2.1
- **建议结构**:
  - project.dependencies：仅保留运行时最小集（numpy、psutil、cloudpickle等）
  - project.optional-dependencies.dev：放入pytest、pandas、openpyxl、matplotlib等
  - project.optional-dependencies.frontends：保持现有前端组合（onnx/pytorch/tensorflow）
- **复用验证**: 依赖分层策略在npu-project-hub中已验证有效
- **状态**: ⏳ 待办
- **执行结果**: -

---

### IMP-003: 离线闭环制度化
- **优先级**: P1
- **来源**: export-suggestions.md §一 行动项 + §2.2
- **建议方案**:
  - 引入显式策略变量（例如INSTALL_EXTRAS=0/1或OFFLINE_MODE=1）
  - 若目标是"离线可构建"：准备本地wheels缓存目录并在Containerfile中优先--find-links
  - 若目标是"离线可运行"：将extras统一预装到镜像，构建时不再访问网络
- **复用验证**: 离线闭环策略在npu-project-hub中已验证有效（扩展到全栈镜像场景）
- **状态**: ⏳ 待办
- **执行结果**: -

---

### IMP-004: 运行时基线/兼容性声明与自动校验
- **优先级**: P2
- **来源**: export-suggestions.md §一 行动项
- **验收口径**: 构建产物能自描述其绑定的LLVM/系统库基线；运行时启动阶段能检测出明显不匹配
- **复用验证**: 在npu-project-hub中部分落地（已具备健康检查与容器约束，但未形成显式"运行时基线清单"），未完全验证
- **状态**: ⏳ 待办
- **执行结果**: -

---

### IMP-005: 统一与校准交付文档引用路径
- **优先级**: P2
- **来源**: export-suggestions.md §一 行动项
- **验收口径**: client/README.md等文档的链接不指向不存在路径；交付入口清晰可追溯
- **复用验证**: 交付文档路径统一在npu-project-hub中已验证有效
- **状态**: ⏳ 待办
- **执行结果**: -

---

### IMP-006: 方法论复用状态回写维护规则
- **优先级**: P2
- **来源**: export-suggestions.md §四 下一步更新方向
- **内容**: 每当某条建议在其它真实工程中完成落地，应回写"复用验证状态"，把文档从一次性复盘升级为持续演进的模式库
- **当前进展**: npu-project-hub复用验证状态已回写至export-suggestions.md §三
- **状态**: ⏳ 待办（建立正式维护规则）
- **执行结果**: -

## 复用验证记录（跨项目）

| 建议项 | npu-project-hub映射动作 | 验证状态 |
|---|---|---|
| 统一打包/构建入口 | pyproject.toml + scikit-build-core + CMake + Ninja | ✅ 已验证 |
| 依赖分层 | 后端运行依赖与dev依赖收敛 | ✅ 已验证 |
| 离线闭环制度化 | Dockerfile/Compose/健康检查 + 离线基础镜像导入 | ✅ 已验证 |
| 交付文档路径统一 | README/deploy/CI路径统一 | ✅ 已验证 |
| 运行时基线/兼容性声明 | 尚未形成显式基线文件或自动校验 | ⏳ 未验证完成 |
| 用户侧操作闭环 | 项目页补齐完整性、备份恢复、Git历史 | ✅ 已验证扩展 |

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| - | - | - | xmnn本体改进项暂无执行记录；方法论已在npu-project-hub中完成跨项目复用验证 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件
