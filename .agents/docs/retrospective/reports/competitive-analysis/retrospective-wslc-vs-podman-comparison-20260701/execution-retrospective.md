---
id: "retrospective-wslc-vs-podman-comparison-20260701-execution"
title: "执行复盘：wslc 与 Podman 对比分析"
source: "会话对话产出（wslc vs podman 主题问答）"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/competitive-analysis/retrospective-wslc-vs-podman-comparison-20260701/execution-retrospective.toml"
---
# 执行复盘：wslc 与 Podman 对比分析

> 本章节记录对比分析的执行过程、信息源取证与关键判断节点。

## 一、执行时间线

| 阶段 | 动作 | 产出 |
|------|------|------|
| S1 上下文确认 | 检查 `.temp/` 下既有 WSL 资料 | 确认 `external/WSL` 已本地检出 |
| S2 一手源取证 | 读取 wslc 官方文档（README、technical index、C API index、ContainerNetworkingMode 枚举） | 取得 wslc 架构、API 形态、网络模式上限等可引用事实 |
| S3 对比维度搭建 | 基于 wslc 实际能力反推对比维度（隔离单元/守护/API/网络/Pod/K8s/签名/存储/成熟度等 14 项） | 形成对比矩阵骨架 |
| S4 Podman 侧填充 | 基于公开知识（Docker 兼容契约、OCI 标准、rootless 默认、CNI 生态）补充对照 | 完整对比表 |
| S5 选型决策推导 | 从"是否需要 Docker 兼容"和"是否需要 Windows 原生 SDK"两个分叉点推导选型场景 | 输出 2 类决策场景 |
| S6 短板识别 | 对照 Podman 成熟生态，识别 wslc 在网络/Pod/K8s/签名/容器类型覆盖上的 6 项短板 | 输出短板清单 |
| S7 实操建议 | 结合用户当前环境（`external/WSL` 已检出）给出最小摩擦路径 | 输出 wslc 直接可用 / Podman 需 `winget install` 的差异 |

## 二、信息源取证策略

### 2.1 三角验证法应用

本次对比遵循"源码 + 官方文档 + 公开规范"的三角验证：

| 信息源 | 类型 | 用途 |
|--------|------|------|
| `external/WSL/doc/docs/api-reference/c/index.md` | 官方 API 文档 | 确认 wslc API 形态、preview 状态声明 |
| `external/WSL/doc/docs/api-reference/c/enumerations/wslccontainernetworkingmode.md` | 官方枚举定义 | 取得 wslc 网络模式上限（仅 None/Bridged） |
| `external/WSL/doc/docs/technical-documentation/index.md` | 官方架构图 | 取得 Windows/Linux 三层架构与 hvsocket 通道拓扑 |
| `external/WSL/src/windows/wslc/README.md` | 源码 README | 确认 wslc CLI 存在（内容仅占位） |
| 公开 OCI 规范 / Docker 契约 / Podman 文档 | 行业标准 | Podman 侧能力对照基线 |

### 2.2 关键事实核对

| 事实 | 取证源 | 结论 |
|------|--------|------|
| wslc 是否在 Preview | `wslcsdk.h` preview notice（在 C API index 引用） | 是，已声明可能破坏性变更 |
| wslc 网络模式数 | `WslcContainerNetworkingMode` 枚举 | 仅 2 个（None + Bridged） |
| wslc 是否支持 Pod | C API 全集扫描（container-apis 目录） | 无 pod 抽象，仅单容器 |
| wslc 隔离边界 | technical-documentation index 架构图 | WSL 工具 VM（Hyper-V API 轻量级 VM） |
| wslc 守护进程 | technical-documentation index（wslservice.exe 节点） | `wslservice.exe` 基于 COM |

## 三、关键决策节点

### 3.1 决策一：不把 wslc 定位为 Docker 替代品

**判断依据**：wslc 的 API 是 Session → Container → Process 三层原语，与 Docker/Podman 的 image → container → exec 模型表面相似但语义不同（Session 是 VM 实例，不是 Docker context）。同时 wslc 没有守护进程契约（不是 Docker REST），也没有 Pod/Compose/K8s 生态。把 wslc 与 Podman 放在"Docker 替代品"维度对比会产生误导。

**采用定位**：wslc = Windows 原生容器 API；Podman = Docker 兼容容器引擎。两者在"运行 OCI 容器"的最低层交集上可比，但生态目标不同。

### 3.2 决策二：选型决策树采用双分叉

**判断依据**：单一"哪个更好"答案会掩盖场景差异。本次采用两个分叉：

- 分叉 A：是否需要 Docker 兼容工作流 → 是则 Podman
- 分叉 B：是否需要 Windows 原生 SDK 集成 → 是则 wslc

**舍弃方案**：按"性能/资源占用"维度排序——因 wslc 仍在 Preview，性能基准数据不完整，避免给出未经验证的性能结论。

### 3.3 决策三：明确列出 wslc 短板而非粉饰

**判断依据**：对比报告若回避短板会失去决策价值。本次明确列出 wslc 在网络（仅 2 模式）、Pod（无）、K8s 互操作（无）、镜像签名（无）、API 稳定性（Preview）、容器类型覆盖（仅 Linux，无法承载 Windows 容器）6 项短板，并逐项给出 Podman 对照。

## 四、问题与局限

| 问题 | 说明 | 影响 |
|------|------|------|
| 未实测对比 | 本次为静态文档对比，未在本地实测 wslc 与 Podman 的启动/运行性能 | 性能维度结论缺失 |
| Podman 侧未引用具体文档路径 | Podman 能力基于公开知识，未取本地文档作证 | 可追溯性弱于 wslc 侧 |
| 未覆盖 Docker Desktop | 用户仅问 wslc vs podman，未纳入 Docker Desktop 对照 | 选型决策树未覆盖"已购 Docker Desktop"场景 |
| 未深入 wslc 的 C#/C++ 投影差异 | 对比聚焦能力面，未展开 SDK 三语言投影的细节差异 | SDK 选型建议较粗 |

## 五、执行评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 信息源充分性 | 4/5 | wslc 侧充分，Podman 侧较弱 |
| 对比维度完整性 | 4/5 | 14 项覆盖主要面，缺性能基准 |
| 决策可操作性 | 5/5 | 双分叉决策树+实操命令直接可用 |
| 客观性 | 5/5 | 明确列短板，未粉饰 wslc |
| 局限声明 | 5/5 | 4 项局限均显式列出 |
