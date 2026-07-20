---
id: "docker-ssh-dind-decision-001"
title: "决策 001：DinD vs DooD 模式选型"
date: "2026-07-20"
status: "accepted"
source: ".trae/specs/standards-tools/create-docker-ssh-containerfile/spec.md#open-questions"
---

# 决策 001：DinD vs DooD 模式选型

**决策背景**：本项目需要构建一个包含 Docker 引擎和 OpenSSH 服务的基础镜像，用于 CI/CD 流水线、远程开发环境等场景。Spec 文档提出了一个待决问题：是否需要同时支持 Docker socket 挂载（Docker-outside-of-Docker）作为 Docker-in-Docker 的替代方案。需要明确两种模式的定位、支持方式和取舍。

---

## 备选方案

### 方案 A：仅实现 DinD（Docker-in-Docker）

| 维度 | 说明 |
|------|------|
| **描述** | 容器内运行独立的 dockerd 守护进程，使用 `--privileged` 模式启动，完全隔离的 Docker 环境 |
| **优点** | 1. 完全隔离，容器内操作不影响宿主机<br>2. 每次启动都是干净环境，适合 CI 构建<br>3. Docker 版本可独立控制，不与宿主机耦合<br>4. 适合多租户场景，安全边界清晰 |
| **缺点** | 1. 必须使用 `--privileged` 特权模式，安全风险较高<br>2. 无法复用宿主机镜像缓存，拉取镜像慢<br>3. 存储性能有损耗，配置复杂（cgroup/iptables/存储驱动）<br>4. 额外 dockerd 进程资源开销大<br>5. 需要处理数据持久化（挂载 `/var/lib/docker`） |
| **风险** | 特权模式在某些生产环境/K8s 集群中被禁用；内核版本兼容性可能导致 dockerd 启动失败 |

### 方案 B：仅实现 DooD（Docker-outside-of-Docker）

| 维度 | 说明 |
|------|------|
| **描述** | 仅安装 docker CLI，通过挂载宿主机 `/var/run/docker.sock` 直接操作宿主机 Docker daemon |
| **优点** | 1. 无需 `--privileged`，安全模型更容易被生产环境接受<br>2. 配置极其简单，只需挂载 socket<br>3. 直接复用宿主机镜像缓存，构建速度快<br>4. 性能接近原生，无额外 dockerd 开销<br>5. 启动快，兼容性好 |
| **缺点** | 1. 隔离性极差——容器内可完全控制宿主机 Docker，等同于宿主机 root 权限<br>2. 容器内创建的资源会残留在宿主机，造成环境污染<br>3. CLI 版本与宿主机 dockerd 版本可能不兼容<br>4. 不适合多租户场景，任务间会互相干扰<br>5. volume 挂载路径容易混淆（相对于宿主机而非容器内） |
| **风险** | 安全隐患极大，挂载 socket 等于交出宿主机控制权；用户容易忽略安全警告在生产环境滥用 |

### 方案 C：DinD 为默认，同时支持 DooD 作为可选模式（推荐）

| 维度 | 说明 |
|------|------|
| **描述** | 默认完整实现 DinD 模式（启动容器内 dockerd），同时通过环境变量和自动检测支持 DooD 模式；DooD 不需要额外安装组件，复用 DinD 已安装的 docker CLI |
| **优点** | 1. 覆盖所有使用场景，用户可按需选择<br>2. DooD 实现成本极低——镜像本来就要装 docker CLI，只需在 entrypoint 加模式判断<br>3. 核心定位仍以 DinD 为主，保持 Spec 设计一致性<br>4. 为无法使用特权模式的环境提供替代方案 |
| **缺点** | 1. 需要维护两种模式的文档和测试用例<br>2. 用户可能混淆两种模式，需要清晰的日志提示和文档说明 |
| **风险** | 风险可控：通过启动日志明确告知当前模式，DooD 模式启动时打印醒目安全警告 |

---

## 最终选择

**✅ 方案 C：DinD 为默认实现，同时支持 DooD 作为可选模式**

---

## 决策依据

1. **与 Spec 定位一致**：项目名称和核心需求都是 "Docker-in-Docker SSH 容器镜像"，DinD 是名义上和架构上的核心功能，必须完整实现。

2. **DooD 边际成本极低**：
   - DinD 模式本来就要安装 docker-ce、docker-ce-cli、containerd.io
   - 支持 DooD 只需要 entrypoint 脚本中增加模式判断逻辑（约 20-30 行代码）
   - 不需要额外安装任何包，不增加镜像体积

3. **场景覆盖最全面**：
   - 多租户/不可信 CI 环境 → DinD 提供强隔离
   - 单租户/内部开发环境 → DooD 提供更好的性能和缓存体验
   - 特权模式被禁用的环境 → DooD 作为替代方案可用

4. **行业惯例参考**：官方 Docker dind 镜像和社区主流方案（如 gitlab-runner、jenkins-agent）均采用 "DinD 为主，同时文档说明 DooD 用法" 的模式。

5. **安全降级路径清晰**：当用户评估安全风险后认为 DinD 特权模式不可接受时，有 DooD 作为 Plan B，而不需要重新找其他镜像。

---

## 实施细节

### 环境变量设计

新增 `DIND_MODE` 环境变量控制运行模式：

| 值 | 行为 |
|----|------|
| `dedicated`（默认） | 启动容器内 dockerd（纯 DinD 模式），忽略宿主机 socket |
| `socket` | 不启动 dockerd，直接使用挂载的 `/var/run/docker.sock`（纯 DooD 模式） |
| `auto` | 自动检测：如果 `/var/run/docker.sock` 存在且可访问，则使用 DooD 模式；否则启动 DinD |

### Entrypoint 逻辑

1. 启动时根据 `DIND_MODE` 和 socket 存在性决定运行模式
2. 打印醒目日志明确当前模式（避免用户混淆）
3. DooD 模式下打印安全警告："WARNING: Docker socket mount detected — this container has full control over the host Docker daemon, equivalent to root access on the host"
4. DinD 模式下如果检测到 socket 挂载，提示用户可通过 `DIND_MODE=socket` 切换到 DooD 以获得更好性能

### 文档要求

Containerfile 注释和使用文档中必须包含：
- 两种模式的启动命令示例
- 适用场景对比表
- 安全风险说明
- 版本兼容性注意事项（DooD 模式下 CLI 与宿主机 dockerd 版本兼容性）

### 验收标准

- **DinD 验收**（必过，核心功能）：保持现有 AC-1~AC-9 验收标准不变
- **DooD 验收**（可选，增值功能）：
  - AC-DooD-1：设置 `DIND_MODE=socket` 并挂载 `/var/run/docker.sock` 启动时，不启动容器内 dockerd
  - AC-DooD-2：DooD 模式下执行 `docker info` 显示宿主机 Docker 信息
  - AC-DooD-3：DooD 模式下能正常执行 `docker run`、`docker build` 等操作
  - AC-DooD-4：`DIND_MODE=auto` 时能根据 socket 存在性自动选择正确模式

---

## 决策影响

### 正面影响
- 扩大了镜像适用场景，满足不同安全等级和环境约束的需求
- 对核心 DinD 功能无侵入，不影响现有设计和验收标准
- 用户有选择自由，可根据实际场景权衡安全性与性能
- 实现成本极低，维护成本可控

### 负面影响/代价
- 需要额外的文档说明和测试用例
- 入口点脚本复杂度略有增加
- 部分用户可能在不了解安全风险的情况下误用 DooD 模式（通过启动警告缓解）

### 影响范围
- Containerfile：无变化（已包含 docker CLI）
- entrypoint.sh：增加模式判断逻辑（约 30 行代码）
- 文档/注释：增加两种模式的使用说明和对比
- 测试：增加 DooD 模式的验证用例
- Spec 文档：关闭 Open Question，补充 DooD 相关需求描述

---

## 事后评估（预留）

- **正确性**：待实施后验证
- **如果有遗憾**：（实施后填写）
- **经验启示**：（实施后填写）

---

**相关文档**：
- [Spec 文档](../../.trae/specs/standards-tools/create-docker-ssh-containerfile/spec.md)
- [Containerfile](../Containerfile)
