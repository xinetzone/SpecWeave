---
id: "plane-okf-wiki-spec"
title: "Plane 博文→OKF 知识包转化 Spec"
session: "sc-20261013-plane-okf-wiki"
created: 2026-10-13
methodology: "七概念 R→I→E→V→C · blog-article-to-okf-wiki 七阶段工作流"
status: "in-progress"
---

# Plane 博文 → OKF 知识包转化 Spec

## 0. 敏感度预检（步骤1）

| 项 | 判定 |
|----|------|
| 信源 | 微信公众号「芋道源码」2026-10-12 公开推文（无 code/token/邀请码） |
| 级别 | **公开（Public）** |
| 工作流 | 标准工作流：spec 落 `.trae/specs/plane-okf-wiki/`；bundle 落 `projects/awesome-okf-xs/doc/bundles/jishu/dev/plane/` |

## 1. 骨架判定（步骤2 · 操作可复现性两问）

| 问 | 判定 | 依据 |
|----|------|------|
| ① 博文是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是** | 06 节给出社区版一键脚本完整命令序列；07 节给出端口/环境键/外部存储/Helm 参数 |
| ② 这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **部分** | 作者在 09 节明示「我没有实际部署过 Plane，文中功能与部署描述来自官方 README、开发者文档与来源正文」——**非作者实测**；但流程源自官方部署文档，有明确步骤顺序、默认值与端口，且本轮已逐条对官方源核验（见 verification.md） |

**裁决：设 `examples/`**（2 篇）。理由：步骤序列经官方部署文档核验后具备可复现性（有版本、有默认值、有输入输出），examples 非空、非伪结构。来源性质在 index 顶部与 examples 篇内显著标注「步骤源自官方部署文档（已核验），非作者实测」。

## 2. 归属判定（步骤3）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/dev`（开发与协作） | ✅ **选定** | 主线实体 Plane 是研发团队协作工具，与组内 Git/GitHub/opensource 同属「开发协作工具链」语义 |
| `jishu/web` | ❌ | 组内为 FastAPI/GraphQL 框架类，Plane 是成品应用非 Web 框架 |
| `jishu/systems` | ❌ | 组内为 WSL/PowerShell 基础设施，语义不符 |
| 新建 `jishu/pm`（项目管理）分组 | ❌ | 违反「单篇博文禁止新建分组」（最小变更原则） |

**先例核查**：`jishu/dev` 已有 `opensource`（开源实践/资源清单，非源码教程类）与 `github`（平台工具类），证明该组可容纳非源码类工具 bundle ✅

## 3. 知识拆分（步骤5 · 三层）

| 层 | 篇目 | 内容 |
|----|------|------|
| 发布事实层 | `00-overview-and-positioning.md` | 是什么、起源与规模、技术栈、许可证 |
| 机制/结构层 | `01-editions-and-licensing.md`、`02-work-model-three-scales.md`、`03-views-pages-analytics.md` | 三套版本与许可边界；Work Items/Cycles/Modules 三层时间尺度；视图/文档/统计/Intake |
| 架构与部署层 | `04-deployment-and-operations.md` | 安装路径、环境键、外部依赖、K8s、God mode |
| 选型/边界层 | `05-selection-and-boundaries.md` | 选型矩阵、适用与不适配、风险与时效边界 |
| 可演练层 | `examples/00-*`、`examples/01-*` | 社区版安装演练；生产加固清单 |

## 4. 核验策略（步骤4）

- 信源距离：**第三方自媒体转述官方信息**（第四类，非厂商自宣直发）——作者明示二手来源，故全部数字/日期/版本走 P0 或 P1 核验
- P0 项：Star 数、建库时间、三套版本边界、12 座席、许可证、2 核 4G、五视图、集成清单、安装脚本菜单、端口与环境键、容器内置组件版本
- 勘误重点：① 容器内置组件版本（源文 Postgres 15.5 / Redis 7.2.4 vs 官方当前 postgres:15.7-alpine + Valkey 7.2）；② 源文遗漏 RabbitMQ 消息队列；③ MinIO 镜像 2026-10-08 切换

## 5. 质量门（步骤7）

G1 事实无推断词 ✅ → G2 洞察与事实分层 ✅ → G3 信源先行 ✅ → G4 机械门禁（见 log.md §V）
