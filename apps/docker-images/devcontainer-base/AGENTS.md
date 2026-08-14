# devcontainer-base - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/ 下的子应用，全局规则继承自 SpecWeave 根 AGENTS.md
> 步骤 3：按上下文路由表加载本项目特有规范（.agents/rules/ 下对应文件）
> 步骤 3.5：自检 — 确认已理解父级规则与本项目特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 devcontainer-base 子项目的 AI 协作者入口。本项目是一个全功能开发容器基础镜像构建项目，
> 集成 SSH + Docker DinD + Podman(rootless) + Jupyter，通过 supervisord 管理多服务，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束。项目详细规范已原子化到 [.agents/](.agents/README.md) 目录，
> 完整目录结构见 [.agents/structure.md](.agents/structure.md)。

## 项目概述

- **项目类型**：Docker 镜像构建项目（Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter，supervisord管理）
- **基础镜像**：ubuntu:26.04
- **核心功能**：OpenSSH Server + Docker-in-Docker + Podman(rootless) + JupyterLab，supervisord统一管理
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：devuser (UID 1000)，加入docker组，NOPASSWD sudo通过GRANT_SUDO控制
- **服务端口**：sshd(22) + dockerd(unix socket) + podman(rootless) + jupyter(8888)
- **Python环境**：/opt/conda（Miniforge3 + Python 3.14.6 cp314t free-threading）
- **父级工作区**：SpecWeave 根目录（[../../AGENTS.md](../../AGENTS.md)）— 全局规则、Skill、角色均以父级为准
- **镜像变体**：`variants/` 子系统（conda/conda-llvm/ai-dev/onnx-pytorch/onnx-quantized，有独立AGENTS.md）
- **AI资产容器**：[.agents/](.agents/README.md) 目录（本项目特有规则/脚本/工作流）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ devcontainer-base/AGENTS.md（本文件，项目路由入口）
            ├─ .agents/         ← 本项目AI资产容器（详细规范）
            │   ├─ README.md   ← .agents 目录索引
            │   ├─ structure.md ← 完整目录结构导航
            │   ├─ rules/      ← 项目特有规则（dockerfile/entrypoint/services/build-test）
            │   └─ workflows/  ← CI工作流设计
            ├─ Dockerfile      ← 多阶段构建定义（v2.2，7 Stage单镜像）
            ├─ entrypoint.sh   ← 容器启动脚本
            ├─ config/         ← 服务配置文件
            ├─ scripts/        ← 辅助脚本（构建/测试/量化工具）
            ├─ docs/           ← 人类可读技术文档
            ├─ conda-lock/     ← Conda环境锁定
            ├─ examples/       ← 示例代码
            ├─ templates/      ← 可复用模板
            └─ variants/       ← 镜像变体系列（子系统，有独立AGENTS.md）
```

**嵌套优先原则**：进入本目录后优先读取本文件；项目详细规范在 [.agents/rules/](.agents/README.md) 下；
完整文件树见 [.agents/structure.md](.agents/structure.md)；变体子系统见 [variants/AGENTS.md](variants/AGENTS.md)；
本文件和 `.agents/` 未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表（任务类型→必读规范）

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 定位文件/了解项目结构 | [.agents/structure.md](.agents/structure.md) | 完整目录树、目录职责、快速定位指南 |
| Dockerfile修改/构建优化 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 7 Stage架构、BuildKit缓存挂载、层优化、中文环境、非root用户、安全规范、9步清理 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动流程、日志规范、信号处理、Docker/Podman初始化、密码动态设置、命令模式 |
| supervisord/服务配置 | [.agents/rules/services.md](.agents/rules/services.md) | sshd/dockerd/podman/jupyter四服务管理、daemon.json单一配置源、健康检查、端口映射 |
| Docker DinD配置 | [.agents/rules/services.md#docker-dind-服务dockerd](.agents/rules/services.md#docker-dind-服务dockerd) | DinD特权模式、daemon.json、docker组权限、存储驱动 |
| Podman rootless配置 | [.agents/rules/services.md#podman-rootless-服务](.agents/rules/services.md#podman-rootless-服务) | rootless Podman、subuid/subgid、用户命名空间、cgroupv2 |
| Jupyter配置 | [.agents/rules/services.md#jupyter-服务](.agents/rules/services.md#jupyter-服务) | conda环境路径、token配置、工作目录、CORS策略 |
| SSH配置 | [.agents/rules/services.md#ssh-服务sshd](.agents/rules/services.md#ssh-服务sshd) | ED25519优先、禁用root登录、密码+密钥认证、host keys启动时生成 |
| 镜像构建/启动/测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh/start.sh命令、.env配置、Compose/run命令、验证流程、问题排查 |
| 镜像变体构建/新增/测试 | [variants/AGENTS.md](variants/AGENTS.md) | 变体系列路由入口，构建编排/共享约定/测试/新增指南 |
| ONNX量化工具包 | [scripts/QUICKSTART.md](scripts/QUICKSTART.md) | onnx_quantize_kit使用指南（auto_quantize/动态/静态/FP16） |
| CI流水线配置/触发 | [.agents/workflows/variants-ci.md](.agents/workflows/variants-ci.md) | 双流水线设计、依赖拓扑、量化门禁（cosine_sim≥0.90） |
| 健康检查脚本 | [.agents/rules/services.md#健康检查](.agents/rules/services.md#健康检查) | healthcheck.sh条件检查逻辑、端口检测方式 |
| 项目约束速查 | [.agents/README.md#核心约束速查](.agents/README.md#核心约束速查) | 14项核心约束快速索引 |
| 最佳实践/性能指南 | [docs/](docs/) | Docker DinD配置、Conda性能优化、Python 3.14t C扩展、风险公告 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 快速开始

```bash
# 一键构建基础镜像
bash scripts/build.sh

# 一键启动（含健康验证+SSH/Jupyter连接信息）
bash scripts/start.sh

# 使用国内镜像源
cp .env.example .env  # 编辑 APT_MIRROR=aliyun
bash scripts/build.sh && bash scripts/start.sh

# 构建所有镜像变体（在基础镜像构建完成后）
bash variants/build.sh --all --cn
```

完整构建、运行、验证命令、Compose用法和常见问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 项目详细规范原子化到 `.agents/` 目录，遵循单一职责原则
- 完整目录结构见 [.agents/structure.md](.agents/structure.md)

## 变更日志

最近变更（完整历史见 [CHANGELOG.md](CHANGELOG.md)）：

- 2026-08-14 | refactor | 原子化拆分：AGENTS.md精简为入口路由，详细目录结构迁移至.agents/structure.md，约束速查迁移至.agents/README.md
- 2026-08-07 | feat | 新增 onnx-pytorch/onnx-quantized 变体；onnx_quantize_kit量化工具包；CI双流水线
- 2026-08-07 | refactor | variants/ 添加独立AGENTS.md + .agents/原子化规范体系
