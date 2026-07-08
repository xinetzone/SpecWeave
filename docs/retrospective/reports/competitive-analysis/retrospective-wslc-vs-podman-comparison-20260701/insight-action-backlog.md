---
title: wslc vs Podman容器方案对比复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-wslc-vs-podman-comparison-20260701/insight-action-backlog.toml"
project: retrospective-wslc-vs-podman-comparison-20260701
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本项目为技术方案对比分析型复盘，所有行动项均待执行/验证。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 短期跟进§高优 | 整理wslc网络模式实测表现 | 高 | ⏳ 待执行 | None模式隔离性与Bridged模式端口映射行为实测完成，形成实测报告补充到对比文档 | - |
| IMP-002 | 短期跟进§中优 | 实测wslc与Podman启动延迟对比 | 中 | ⏳ 待执行 | Measure-Command测量wslc create vs podman run冷启动时间，形成性能对比数据 | - |
| IMP-003 | 短期跟进§中优 | 实测wslc与Podman镜像拉取速度 | 中 | ⏳ 待执行 | 同一镜像（如alpine）从同一registry拉取计时，形成网络性能对比数据 | - |
| IMP-004 | 短期跟进§中优 | 调研wslc的Pod路线图 | 中 | ⏳ 待执行 | WSL GitHub Issues/Roadmap中Pod计划调研完成，形成路线图摘要 | - |
| IMP-005 | 长期沉淀§按需 | 对比报告关键结论写入知识库 | 低 | ⏳ 待执行 | docs/knowledge/learning/下新增wslc-vs-podman-comparison.md（或姊妹条目），与wsl-learning-plan.md形成配套 | - |
| IMP-006 | 长期沉淀§按需 | wslc版本演进跟踪 | 低 | ⏳ 待跟踪 | wslc脱离Preview时更新README成熟度行、选型清单、网络能力代差洞察 | - |
| IMP-007 | 长期沉淀§按需 | Podman Windows体验演进跟踪 | 低 | ⏳ 待跟踪 | Podman Machine在Windows原生支持（无需WSL）时更新选型建议和安装步骤 | - |

## 行动项详情

### IMP-001: 整理wslc网络模式实测表现
- **优先级**: 高
- **目标**: 验证wslc网络模式的实际表现，为生产可用性判断提供实证
- **落地步骤**:
  1. 测试None模式的网络隔离性
  2. 测试Bridged模式的端口映射行为
  3. 记录实测结果与文档描述的差异
- **验收标准**: 形成wslc网络模式实测报告，明确None/Bridged模式的实际行为和限制
- **状态**: ⏳ 待执行

---

### IMP-002: 实测wslc与Podman启动延迟对比
- **优先级**: 中
- **目标**: 获取冷启动性能的定量数据
- **落地步骤**:
  1. 使用Measure-Command测量`wslc create`冷启动时间
  2. 使用Measure-Command测量`podman run`冷启动时间
  3. 多次测量取平均值，对比数据
- **验收标准**: 有明确的冷启动时间对比数据（均值、样本数）
- **状态**: ⏳ 待执行

---

### IMP-003: 实测wslc与Podman镜像拉取速度
- **优先级**: 中
- **目标**: 获取镜像拉取性能的定量数据
- **落地步骤**:
  1. 选择同一镜像（如alpine:latest）
  2. 从同一registry分别拉取
  3. 使用Measure-Command计时
- **验收标准**: 有明确的镜像拉取速度对比数据
- **状态**: ⏳ 待执行

---

### IMP-004: 调研wslc的Pod路线图
- **优先级**: 中
- **目标**: 了解wslc是否有Pod抽象的规划，影响选型决策树
- **落地步骤**:
  1. 查阅WSL GitHub Issues
  2. 查阅Microsoft官方Roadmap
  3. 整理Pod相关计划的时间线
- **验收标准**: 形成wslc Pod路线图摘要，明确是否有计划、预计时间
- **状态**: ⏳ 待执行

---

### IMP-005: 对比报告关键结论写入知识库
- **优先级**: 低
- **目标**: 将对比分析成果沉淀到知识库，与wsl-learning-plan.md形成姊妹条目
- **落地步骤**:
  1. 在docs/knowledge/learning/08-systems-infrastructure/下新增wslc-vs-podman-comparison.md
  2. 提炼对比速查表、选型决策清单、核心结论
  3. 更新索引文件
- **验收标准**: 知识库中存在wslc-vs-podman对比条目，可通过索引检索到
- **状态**: ⏳ 待执行

---

### IMP-006: wslc版本演进跟踪
- **优先级**: 低
- **目标**: 持续跟踪wslc版本变化，保持报告时效性
- **触发条件**: wslc脱离Preview状态 / wslc新增网络模式 / wslc新增Pod抽象
- **更新动作**:
  - wslc脱离Preview：更新README成熟度行，移除选型清单中"接受Preview风险"项
  - 新增网络模式：更新对比表网络行，重评"网络能力代差"洞察
  - 新增Pod：更新对比表Pod/Compose行，重评选型决策树
- **状态**: ⏳ 待跟踪（长期）

---

### IMP-007: Podman Windows体验演进跟踪
- **优先级**: 低
- **目标**: 持续跟踪Podman在Windows上的体验演进
- **触发条件**: Podman Machine在Windows上原生支持（无需WSL）
- **更新动作**: 更新"选Podman"分支的安装步骤，重评wslc的"Windows原生"独占优势
- **状态**: ⏳ 待跟踪（长期）

## 用户环境即时操作参考（非项目行动项）

> 以下为给用户的即时操作建议，不属于项目沉淀行动项：

| 行动 | 命令/操作 |
|------|-----------|
| 验证wslc可用性 | `wslc --version` 或 `wslc create --help` |
| 试运行wslc容器 | 参考 `external/WSL/doc/docs/api-reference/c/end-to-end-example.md` |
| 安装Podman对照 | `winget install RedHat.Podman` |
| 初始化Podman VM | `podman machine init && podman machine start` |

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| - | - | - | 尚无执行记录 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移7个行动项至独立backlog文件（含4个短期实测/调研、1个知识库沉淀、2个长期跟踪）
