---
id: "retrospective-wslc-vs-podman-comparison-20260701-export"
title: "导出建议：wslc 与 Podman 对比分析"
source: "会话对话产出（wslc vs podman 主题问答）"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-wslc-vs-podman-comparison-20260701/export-suggestions.toml"
---
# 导出建议：wslc 与 Podman 对比分析

> 本章节给出基于对比结论的行动项、选型清单与后续学习方向。

## 一、行动项

### 1.1 即时可执行（用户当前环境）

| 行动 | 命令/操作 | 预期产出 |
|------|-----------|----------|
| 验证 wslc 可用性 | `wslc --version` 或 `wslc create --help` | 确认 wslc.exe 已随 Windows 内置 |
| 试运行 wslc 容器 | 参考 `.temp/libs/WSL/doc/docs/api-reference/c/end-to-end-example.md` | 取得 wslc 实际运行体验 |
| 安装 Podman 对照 | `winget install RedHat.Podman` | 取得 Docker 兼容工具链 |
| 初始化 Podman VM | `podman machine init && podman machine start` | 在 Windows 上启用 Podman |

### 1.2 短期跟进（1-2 周内）

| 行动 | 说明 | 优先级 |
|------|------|--------|
| 实测 wslc 与 Podman 启动延迟对比 | 用 `Measure-Command` 测 `wslc create` vs `podman run` 的冷启动 | 中 |
| 实测 wslc 与 Podman 镜像拉取速度 | 同一镜像（如 alpine）从同一 registry 拉取计时 | 中 |
| 整理 wslc 网络模式实测表现 | 测试 None 模式的隔离性与 Bridged 模式的端口映射行为 | 高（关系到生产可用性判断） |
| 调研 wslc 的 Pod 路线图 | 查 WSL GitHub Issues/Roadmap 是否有 Pod 计划 | 中 |

### 1.3 长期沉淀（按需）

| 行动 | 说明 |
|------|------|
| 将本对比报告关键结论写入 `docs/knowledge/learning/` | 与 `wsl-learning-plan.md` 形成姊妹条目 |
| 跟踪 wslc 版本演进 | 当 wslc 脱离 Preview 时更新本报告的"硬门禁"判断 |
| 跟踪 Podman 在 Windows 上的体验演进 | 当 Podman Machine 在 Windows 上原生支持（无需 WSL）时更新选型建议 |

## 二、选型决策清单

### 2.1 选 wslc 的判定清单

满足以下**全部**条件时选 wslc：

- [ ] 目标宿主为 Windows
- [ ] 需要 Windows 原生 SDK 集成（C++/C#/.NET 应用直接调用容器 API）
- [ ] 接受 Preview 状态的 API 稳定性风险（非生产负载）
- [ ] 不需要 Docker Compose / Kubernetes YAML 兼容
- [ ] 不需要镜像签名（cosign/sigstore）
- [ ] 网络需求在 None / Bridged 范围内
- [ ] 不需要 Pod（单容器即可满足需求）

### 2.2 选 Podman 的判定清单

满足以下**任一**条件时选 Podman：

- [ ] 需要 Docker CLI/REST 兼容（drop-in 替换 Docker）
- [ ] 需要 Pod 或 `podman-compose` 编排
- [ ] 需要 Kubernetes YAML 互操作（`podman play kube`）
- [ ] 需要 rootless 默认的安全模型
- [ ] 需要镜像签名 / 供应链安全
- [ ] 需要跨平台一致行为（Linux/Mac/Windows）
- [ ] 目标场景为生产负载（需 GA 成熟度）

### 2.3 混合使用场景

两者并非互斥，可共存：

- **Podman 用于开发/CI**：Docker 兼容工作流，复用现有 Compose/K8s YAML
- **wslc 用于 Windows 集成**：需要从 Windows 原生应用调用容器能力的场景

## 三、后续学习方向

### 3.1 wslc 深入

> wslc 一手源（`.temp/libs/WSL`）为临时检出，正式查阅请参考已归档的 [wsl-learning-plan.md](../../../../knowledge/learning/wsl-learning-plan.md)（含三语言 API 投影、错误码表、架构细节整合）或在线官方文档 [wsl.dev](https://wsl.dev/)。

| 主题 | 入口 |
|------|------|
| wslc C API 完整结构 | wsl.dev → API Reference → C → Structures |
| wslc 容器 API | wsl.dev → API Reference → C → Container APIs |
| wslc 端到端示例 | wsl.dev → API Reference → C → End-to-End Example |
| wslc 错误码 | wsl.dev → API Reference → C → Error Codes |
| WSL 架构细节 | wsl.dev → Technical Documentation → Index |

### 3.2 Podman 深入

| 主题 | 资源 |
|------|------|
| Podman 官方文档 | https://docs.podman.io/ |
| Podman Desktop（GUI） | https://podman-desktop.io/ |
| Podman Kubernetes 互操作 | `podman generate kube --help` |
| Podman rootless 配置 | https://github.com/containers/podman/blob/main/docs/tutorials/rootless.md |

### 3.3 横向扩展

| 主题 | 价值 |
|------|------|
| Docker Desktop vs Podman | 补全"已购 Docker Desktop"场景的决策树分支 |
| containerd vs runc vs crun | 理解 wslc 与 Podman 共用的底层运行时差异 |
| OCI 镜像/运行时/分发规范 | 理解 wslc 与 Podman 共同遵循的标准层 |
| Windows Containers（`--isolation=process`） | 补全 wslc 无法承载 Windows 容器的对照面 |

## 四、报告自维护建议

| 触发条件 | 维护动作 |
|----------|----------|
| wslc 脱离 Preview 状态 | 更新 README.md 成熟度行；移除选型清单中的"接受 Preview 风险"项 |
| wslc 新增网络模式 | 更新对比表网络行；重评"网络能力代差"洞察 |
| wslc 新增 Pod 抽象 | 更新对比表 Pod/Compose 行；重评选型决策树 |
| Podman 在 Windows 上原生支持 | 更新"选 Podman"分支的安装步骤；重评 wslc 的"Windows 原生"独占优势 |
| 本地完成性能实测 | 新增性能维度章节；补全执行复盘的"未实测对比"局限 |
