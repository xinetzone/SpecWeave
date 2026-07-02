+++
id = "retrospective-xmnn-folder-20260701-readme"
date = "2026-07-01"
type = "index"
source = "server/libs/notebook/xmnn 目录结构与打包系统静态分析"
+++

# XMNN 目录复盘：Nuitka 运行时 wheel + 离线部署包

> **复盘对象**：`server/libs/notebook/xmnn`（XMNN：TVM+VTA+xmnn 的 Nuitka 预编译运行时）
> **复盘日期**：2026-07-01
> **报告类型**：洞察萃取（代码与工程结构审计）

## 项目概览

`xmnn/` 的核心目标是将 TVM/VTA 运行时与 NPU 专用运行时（xmnn）封装成一个可分发的 Linux x86_64 wheel，并通过 `client/` 提供离线部署与运行镜像。

本次复盘聚焦“目录结构是否自洽、打包/安装链路是否清晰、离线部署是否真正闭环、依赖与数据边界是否明确”四个方面，输出标准四件套以便后续改进与复用。

### 关键入口（被分析对象）

| 类型 | 路径 | 说明 |
|---|---|---|
| 项目说明 | [xmnn/README.md](../../../../../../../../server/libs/notebook/xmnn/README.md) | wheel 内容、安装与容器运行策略 |
| Python 打包元数据 | [xmnn/pyproject.toml](../../../../../../../../server/libs/notebook/xmnn/pyproject.toml) | 版本、依赖、extras、scikit-build-core 配置 |
| 安装规则 | [xmnn/CMakeLists.txt](../../../../../../../../server/libs/notebook/xmnn/CMakeLists.txt) | 复用 tvm/vta 子工程 install 规则 + xmnn_data 安装 |
| 客户交付包 | [xmnn/client/README.md](../../../../../../../../server/libs/notebook/xmnn/client/README.md) | 离线 wheel 分发、校验与运行策略 |
| 运行镜像 | [xmnn/client/Containerfile](../../../../../../../../server/libs/notebook/xmnn/client/Containerfile) | 多阶段复制 LLVM 运行时 + wheel 安装 + 构建期 import 校验 |

### 核心指标（静态审计视角）

| 指标 | 数值 |
|---|---:|
| 复盘交付物 | 4 个 Markdown 文件 |
| 关键打包入口 | 2 个（`pyproject.toml` + `CMakeLists.txt`） |
| 关键交付形态 | 2 个（wheel + client 运行镜像） |
| 核心风险面 | 4 类（包结构边界、依赖膨胀、离线闭环、运行时二进制可迁移性） |

## 子模块导航

| 章节 | 文件 | 说明 |
|------|------|------|
| 执行复盘 | [execution-retrospective.md](execution-retrospective.md) | 本次审计过程、关注点与判断依据 |
| 洞察萃取 | [insight-extraction.md](insight-extraction.md) | 可复用模式、风险点与结构性结论 |
| 导出建议 | [export-suggestions.md](export-suggestions.md) | 可执行行动项（优先级/验收口径） |

## 方法论复用进展

2026-07-02 已在 `workspace/apps/npu-project-hub/apps/project-hub` 完成一次跨项目复用验证，验证重点不是“XMNN 代码本身是否修改”，而是本目录沉淀的方法论是否足以驱动另一个工程的现代化改造与交付闭环。

复用结果摘要：

| 建议主题 | 在 `npu-project-hub` 中的映射 | 当前状态 |
|---|---|---|
| 依赖与构建入口收敛 | 迁移到 `pyproject.toml` + `scikit-build-core` + `CMake` + `Ninja` | 已落地 |
| 离线/镜像化交付闭环 | 后端/前端 Dockerfile、Compose、健康检查、离线基础镜像导入验证 | 已落地 |
| 文档路径与交付入口统一 | README、deploy 文档、CI、Compose 路径统一 | 已落地 |
| 运行时基线与兼容性声明 | 已具备健康检查与容器约束，但未形成显式“运行时基线清单” | 部分落地 |
| 用户侧操作闭环 | 项目页已接入完整性、备份恢复、Git 历史 | 已落地 |

这说明本目录中的“包边界/依赖分层/离线闭环/交付入口统一”四类判断，不只适用于 `xmnn`，也可作为其它 Python + 前端混合工程的现代化改造参考模板。
