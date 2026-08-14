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
> 本项目特有的上下文路由与约束。项目详细规范已原子化到 [.agents/](.agents/README.md) 目录。

## 项目概述

- **项目类型**：Docker 镜像构建项目（Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter，supervisord 管理多服务）
- **基础镜像**：ubuntu:26.04
- **核心功能**：OpenSSH Server + Docker-in-Docker + Podman(rootless) + Jupyter Notebook/Lab，通过 supervisord 统一管理四服务
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：devuser (UID 1000)，加入docker组，可选NOPASSWD sudo（通过GRANT_SUDO环境变量控制）
- **服务端口**：sshd(22) + dockerd(unix socket) + podman(rootless unix socket) + jupyter(8888)
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准
- **镜像变体**：`variants/` 目录（基于基础镜像的特殊功能变体，共4个：conda, conda-llvm, onnx-pytorch, onnx-quantized）
- **AI资产容器**：`.agents/` 目录（本项目特有规则/脚本/模板）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/docker-images/devcontainer-base/AGENTS.md（本文件，项目路由入口）
       ├─ .agents/             ← 本项目AI资产容器（详细规范）
       │   ├─ README.md        ← .agents 目录索引
       │   └─ rules/           ← 项目特有规则
       │       ├─ dockerfile.md  ← Dockerfile 多阶段构建规范
       │       ├─ entrypoint.md  ← Entrypoint 启动脚本规范
       │       ├─ services.md    ← 服务管理规范（supervisord/SSH/Docker/Podman/Jupyter）
       │       └─ build-test.md  ← 构建与测试流程
       ├─ Dockerfile           ← 多阶段构建定义（builder + runtime）
       ├─ entrypoint.sh        ← 容器启动脚本
       ├─ requirements.txt     ← Python 依赖包列表
       ├─ config/              ← 配置文件目录
       │   ├─ supervisord.conf ← supervisord 主配置
       │   ├─ sshd_config      ← SSH 服务配置
       │   ├─ jupyter_notebook_config.py ← Jupyter 基础配置
       │   └─ supervisor/      ← supervisord 配置
       │       └─ conf.d/      ← 服务配置文件（sshd/dockerd/podman/jupyter）
       ├─ scripts/             ← 辅助脚本
       │   ├─ lib/             ← 脚本共享库
       │   │   └─ logging.sh   ← 结构化日志函数
       │   ├─ build.sh         ← 一键构建脚本
       │   ├─ start.sh         ← 一键启动脚本
       │   ├─ local-build.sh   ← WSL2本地构建脚本（变体依赖链）
       │   ├─ healthcheck.sh   ← 健康检查脚本
       │   ├─ verify-deployment.py ← 部署验证脚本（多维度检查）
       │   ├─ ci_quantization_gate.py ← CI量化门禁脚本
       │   ├─ ci-requirements.txt    ← CI Python依赖清单
       │   ├─ onnx_quantize_kit/     ← ONNX量化工具包（onnxruntime.quantization封装）
       │   │   ├─ __init__.py
       │   │   ├─ quantize.py        ← 高层量化API
       │   │   ├─ accuracy.py        ← 精度验证
       │   │   ├─ benchmark.py       ← 性能基准
       │   │   ├─ calibration.py     ← 校准数据读取
       │   │   ├─ model_detect.py    ← 模型类型检测
       │   │   ├─ cli.py             ← 命令行接口
       │   │   └─ reporting.py       ← 报告生成
       │   ├─ test_quantize_kit.py   ← 工具包单元测试
       │   ├─ test_ort_quantization_regression.py ← ORT回归测试(G1-G11)
       │   ├─ test_onnxruntime_quantization.py    ← ORT API单元测试
       │   ├─ test_neural_compressor.py           ← NC兼容性测试（可选）
       │   ├─ models/             ← 测试用ONNX模型
       │   └─ ...                ← 其他辅助脚本（benchmark/batch/analyze等）
       ├─ docker-compose.yml   ← Compose 编排
       ├─ .env.example         ← 环境变量模板
       ├─ variants/            ← 镜像变体系列（子系统，有独立AGENTS.md）
       │   ├─ AGENTS.md        ← 变体系列路由入口（进入variants/必读）
       │   ├─ .agents/         ← 变体管理子系统AI资产容器
       │   │   ├─ README.md    ← 子系统.agents索引
       │   │   └─ rules/       ← 变体管理规则（构建编排/共享约定/测试/新增指南）
       │   ├─ README.md        ← 人类可读：变体索引和使用指南
       │   ├─ build.sh         ← 变体统一构建脚本（拓扑排序+依赖处理）
       │   ├─ shared/              ← 变体间共享组件
       │   │   ├─ lib/logging.sh  ← 共享结构化日志库
       │   │   └─ scripts/conda-mirror-setup.sh ← conda/pip镜像源配置
       │   ├─ scripts/            ← 单变体辅助脚本
       │   │   ├─ build-conda-llvm.sh
       │   │   ├─ build-onnx-pytorch.sh
       │   │   ├─ test-conda-llvm.sh
       │   │   ├─ test-onnx-pytorch.sh
       │   │   └─ test-onnx-quantized.sh
       │   ├─ _template/          ← 新变体模板（复制后修改）
       │   │   ├─ Dockerfile
       │   │   ├─ .env.example
       │   │   ├─ README.md
       │   │   └─ .agents/rules/dockerfile.md
       │   ├─ conda/              ← Miniconda3 基础环境变体
       │   │   ├─ Dockerfile
       │   │   ├─ .env.example
       │   │   ├─ README.md
       │   │   └─ .agents/rules/dockerfile.md
       │   ├─ conda-llvm/         ← conda+LLVM/clang 编译工具链变体
       │   │   ├─ Dockerfile
       │   │   ├─ .env.example
       │   │   ├─ README.md
       │   │   └─ .agents/rules/dockerfile.md
       │   ├─ onnx-pytorch/       ← PyTorch CPU+ONNX Runtime 深度学习运行时
       │   │   ├─ Dockerfile
       │   │   ├─ .env.example
       │   │   ├─ README.md
       │   │   └─ .agents/rules/dockerfile.md
       │   └─ onnx-quantized/     ← ONNX量化工具链变体（INT8/FP16）
       │       ├─ Dockerfile
       │       ├─ .env.example
       │       ├─ README.md
       │       └─ .agents/rules/dockerfile.md
       ├─ docs/                ← 人类可读文档（最佳实践等）
       └─ README.md            ← 使用文档
```

**嵌套优先原则**：进入本目录后优先读取本文件；项目详细规范在 `.agents/rules/` 下；本文件和 `.agents/` 未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/构建优化 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 多阶段构建、层缓存策略、BuildKit缓存挂载、SHELL pipefail、构建计时、中文环境、镜像源切换 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动流程、日志规范、信号处理、Docker/Podman初始化、密码动态设置、命令模式 |
| supervisord/服务配置 | [.agents/rules/services.md](.agents/rules/services.md) | sshd/dockerd/podman/jupyter四服务管理、daemon.json单一配置源、健康检查、端口映射 |
| Docker DinD配置 | [.agents/rules/services.md#docker-dind-服务dockerd](.agents/rules/services.md#docker-dind-服务dockerd) | DinD特权模式、daemon.json配置、docker组权限、存储驱动 |
| Podman rootless配置 | [.agents/rules/services.md#podman-rootless-服务](.agents/rules/services.md#podman-rootless-服务) | rootless Podman、subuid/subgid、用户命名空间、cgroupv2 |
| Jupyter配置 | [.agents/rules/services.md#jupyter-服务](.agents/rules/services.md#jupyter-服务) | venv路径、token配置、工作目录、CORS策略 |
| SSH配置 | [.agents/rules/services.md#ssh-服务sshd](.agents/rules/services.md#ssh-服务sshd) | ED25519优先、禁用root登录、密码+密钥认证、host keys启动时生成 |
| 镜像构建/启动/测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh/start.sh命令、.env配置、Compose/run命令、验证流程、问题排查 |
| 镜像变体构建/新增/测试 | [variants/AGENTS.md](variants/AGENTS.md) | 变体系列路由入口，构建编排/共享约定/测试/新增指南 |
| conda变体Dockerfile | [variants/conda/.agents/rules/dockerfile.md](variants/conda/.agents/rules/dockerfile.md) | Miniconda安装、/opt/conda路径、conda-init.sh、镜像源配置 |
| conda-llvm变体Dockerfile | [variants/conda-llvm/.agents/rules/dockerfile.md](variants/conda-llvm/.agents/rules/dockerfile.md) | LLVM 22.1.8安装、clang/cmake/ninja、PATH配置 |
| onnx-pytorch变体Dockerfile | [variants/onnx-pytorch/.agents/rules/dockerfile.md](variants/onnx-pytorch/.agents/rules/dockerfile.md) | PyTorch CPU安装、ONNX生态、PATH优先级（/opt/conda/bin最前） |
| onnx-quantized变体Dockerfile | [variants/onnx-quantized/.agents/rules/dockerfile.md](variants/onnx-quantized/.agents/rules/dockerfile.md) | onnxruntime.quantization量化工具链、FP16/INT8、共享脚本模式 |
| ONNX量化工具包(onnx_quantize_kit) | [scripts/QUICKSTART.md](scripts/QUICKSTART.md) | 高层量化API使用指南（auto_quantize/动态/静态/FP16） |
| CI流水线配置/触发 | [.agents/workflows/variants-ci.md](.agents/workflows/variants-ci.md) | 变体构建CI设计、依赖拓扑、触发条件 |
| 健康检查脚本 | [.agents/rules/services.md#健康检查](.agents/rules/services.md#健康检查) | healthcheck.sh条件检查逻辑、端口检测方式 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | devcontainer-base子项目路由 |
| AI资产目录 | [.agents/README.md](.agents/README.md) | .agents目录索引和结构说明 |
| Dockerfile规范 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 多阶段构建、缓存优化、中文环境、安全规范、非root用户 |
| Entrypoint规范 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动脚本、日志、信号、命令模式 |
| 服务管理规范 | [.agents/rules/services.md](.agents/rules/services.md) | supervisord/SSH/Docker/Podman/Jupyter/健康检查 |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh/start.sh/Compose/验证流程/问题排查 |
| 最佳实践文档 | [docs/best-practices.md](docs/best-practices.md) | Docker DinD无冲突配置、Compose变量覆盖、镜像源切换可复用模式 |
| 变体子系统路由 | [variants/AGENTS.md](variants/AGENTS.md) | 镜像变体系列入口（构建/测试/新增变体） |
| 变体系列AI资产 | [variants/.agents/README.md](variants/.agents/README.md) | 变体管理子系统规则索引 |
| 变体构建编排规范 | [variants/.agents/rules/build-orchestration.md](variants/.agents/rules/build-orchestration.md) | VARIANTS格式、拓扑排序、[TIMER]、验证机制 |
| 变体Dockerfile共享约定 | [variants/.agents/rules/variant-conventions.md](variants/.agents/rules/variant-conventions.md) | FROM模式、禁止覆盖项、PATH优先级、缓存挂载 |
| 变体测试规范 | [variants/.agents/rules/testing.md](variants/.agents/rules/testing.md) | 6层测试策略、脚本模板 |
| 新增变体操南 | [variants/.agents/rules/new-variant-guide.md](variants/.agents/rules/new-variant-guide.md) | 7步流程、模板替换、注册清单 |
| conda变体规范 | [variants/conda/.agents/rules/dockerfile.md](variants/conda/.agents/rules/dockerfile.md) | Miniconda基础环境变体的Dockerfile规范 |
| conda-llvm变体规范 | [variants/conda-llvm/.agents/rules/dockerfile.md](variants/conda-llvm/.agents/rules/dockerfile.md) | LLVM/clang工具链变体的Dockerfile规范 |
| onnx-pytorch变体规范 | [variants/onnx-pytorch/.agents/rules/dockerfile.md](variants/onnx-pytorch/.agents/rules/dockerfile.md) | PyTorch CPU+ONNX Runtime变体的Dockerfile规范 |
| onnx-quantized变体规范 | [variants/onnx-quantized/.agents/rules/dockerfile.md](variants/onnx-quantized/.agents/rules/dockerfile.md) | ONNX量化工具链变体的Dockerfile规范（共享脚本模式） |
| CI工作流规范 | [.agents/workflows/variants-ci.md](.agents/workflows/variants-ci.md) | 变体CI设计、依赖拓扑、on-quantize-ci.yml、量化门禁 |
| ONNX量化工具包文档 | [scripts/QUICKSTART.md](scripts/QUICKSTART.md) | onnx_quantize_kit使用指南、API说明、测试套件 |
| 共享构建脚本规范 | [variants/shared/scripts/](variants/shared/scripts/) | 变体间共享构建脚本（conda-mirror-setup.sh等） |
| 新变体模板 | [variants/_template/](variants/_template/) | 新增变体的Dockerfile/.env/README/dockerfile.md模板 |

## 项目约束速览

详细约束已按主题拆分到 `.agents/rules/` 下各文件，以下是核心约束索引：

| 约束主题 | 所在文件 |
|---------|---------|
| 中文环境（locale/timezone）、基础镜像锁定 | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| 非root用户（devuser/UID1000/docker组/sudo） | [dockerfile.md](.agents/rules/dockerfile.md#非-root-用户规范) |
| 服务管理（supervisord四服务） | [services.md](.agents/rules/services.md#总体原则) |
| Docker DinD配置（daemon.json单一配置源） | [services.md](.agents/rules/services.md#docker-dind-服务dockerd) |
| Podman rootless配置 | [services.md](.agents/rules/services.md#podman-rootless-服务) |
| 启动脚本要求（tini/日志/信号） | [entrypoint.md](.agents/rules/entrypoint.md#基础约定) |
| 构建日志格式（[BUILD]标记） | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| 敏感信息（禁止硬编码密码） | [dockerfile.md](.agents/rules/dockerfile.md#安全规范) |
| 镜像优化（多阶段/--no-install-recommends/缓存清理） | [dockerfile.md](.agents/rules/dockerfile.md#体积优化) |
| Jupyter配置（venv/token/工作目录） | [services.md](.agents/rules/services.md#jupyter-服务) |
| SSH配置（端口/root登录/密钥/认证） | [services.md](.agents/rules/services.md#ssh-服务sshd) |
| 健康检查（条件检测/端口探测） | [services.md](.agents/rules/services.md#健康检查) |
| 可复用基础镜像（WORKDIR/tini/FROM兼容） | [dockerfile.md](.agents/rules/dockerfile.md#非-root-用户规范) |
| Docker与Podman共存 | [services.md](.agents/rules/services.md) |
| conda变体约束（conda-init.sh/PATH/镜像源） | [variants/conda/.agents/rules/dockerfile.md](variants/conda/.agents/rules/dockerfile.md) |
| conda-llvm变体约束（LLVM版本/编译工具链） | [variants/conda-llvm/.agents/rules/dockerfile.md](variants/conda-llvm/.agents/rules/dockerfile.md) |
| onnx-pytorch变体约束（PyTorch CPU优先/ONNX生态） | [variants/onnx-pytorch/.agents/rules/dockerfile.md](variants/onnx-pytorch/.agents/rules/dockerfile.md) |
| onnx-quantized变体约束（共享脚本/量化API/零额外依赖） | [variants/onnx-quantized/.agents/rules/dockerfile.md](variants/onnx-quantized/.agents/rules/dockerfile.md) |
| 变体间共享脚本（shared/scripts/，禁止复制粘贴） | [variants/.agents/rules/variant-conventions.md](variants/.agents/rules/variant-conventions.md) |
| CI量化门禁（cosine_sim≥0.90，失败阻断） | [.agents/workflows/variants-ci.md](.agents/workflows/variants-ci.md) |

## 快速开始

```bash
# 一键构建基础镜像
bash scripts/build.sh

# 一键启动（含健康验证+SSH/Jupyter连接信息）
bash scripts/start.sh

# 使用国内镜像源
cp .env.example .env  # 编辑 APT_MIRROR=aliyun
bash scripts/build.sh && bash scripts/start.sh

# 构建镜像变体（在基础镜像构建完成后）
bash variants/build.sh --variant conda --cn        # 构建 conda 变体（国内源）
bash variants/build.sh --variant conda-llvm --cn   # 构建 conda-llvm 变体（国内源）
bash variants/build.sh --variant onnx-pytorch --cn # 构建 onnx-pytorch 变体
bash variants/build.sh --variant onnx-quantized --cn # 构建 onnx-quantized 量化工具链变体
bash variants/build.sh --all --cn                  # 构建所有变体（按依赖顺序）

# 查看状态 / 停止
bash scripts/start.sh status
bash scripts/start.sh stop
```

完整构建、运行、验证命令和常见问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程
- 项目详细规范原子化到 `.agents/rules/` 目录，遵循单一职责原则

## 变更日志

- 2026-08-07 | feat | 新增 onnx-pytorch/onnx-quantized 变体；onnx_quantize_kit量化工具包；CI双流水线（变体构建+量化门禁）；共享构建脚本（shared/scripts/conda-mirror-setup.sh）
- 2026-08-07 | refactor | 为 variants/ 添加 AGENTS.md + .agents/ 原子化规范结构（4个规则文件：构建编排/共享约定/测试/新增指南），更新父级路由表
- 2026-08-07 | feat | 新增 variants/ 镜像变体目录结构：统一构建脚本、conda 变体（Miniconda3）、conda-llvm 变体（LLVM 22.1.8/clang/cmake/ninja）、_template 新变体模板
- 2026-08-07 | refactor | 将AGENTS.md中项目约束和快速开始拆分为.agents/rules/下4个原子规则文件（dockerfile/entrypoint/services/build-test）
- 2026-08-07 | feat | 新增start.sh一键启动脚本、.env.example环境变量模板、docs/best-practices.md最佳实践、BuildKit缓存优化
- 2026-08-07 | feat | 初始化项目结构：AGENTS.md、目录结构config/supervisor/conf.d、scripts/lib/、.dockerignore、requirements.txt
