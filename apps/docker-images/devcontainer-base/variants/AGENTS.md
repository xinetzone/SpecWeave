# devcontainer-base/variants - 镜像变体系列 AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本子系统是 devcontainer-base 的变体管理子目录，规则继承自 ../AGENTS.md
> 步骤 3：按上下文路由表加载变体管理特有规范（.agents/rules/ 下对应文件）
> 步骤 3.5：自检 — 确认已理解父级规则与本系统特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 devcontainer-base 镜像变体系列的 AI 协作者入口。本子系统管理基于 devcontainer-base 基础镜像的
> 特殊功能镜像变体（如 conda、conda-llvm），提供统一构建脚本、依赖拓扑排序、分层验证和模板化新增能力。
> 所有全局规则和 devcontainer-base 项目规则继承自父级，本文件仅定义变体管理子系统特有的上下文路由与约束。
> 子系统详细规范已原子化到 [.agents/](.agents/README.md) 目录。

## 子系统概述

- **子系统类型**：Docker 镜像变体管理系统（"基础继承+配置化"模式）
- **父级工作区**：devcontainer-base（[../AGENTS.md](../AGENTS.md)）
- **核心功能**：多变体统一构建（拓扑排序）、构建阶段计时、逐条验证、国内镜像源支持、模板化新增
- **共享组件**：`shared/lib/logging.sh`（结构化日志库，双格式text+JSON）
- **可用变体**：
  - `conda-llvm`：基础镜像 + LLVM 22.1.8/clang/cmake/ninja 编译工具链（直接基于 devcontainer-base:latest，镜像源已内置于基础镜像）
  - `onnx-dev`：conda-llvm + 纯 ONNX 生态（onnx/onnxruntime/onnx-simplifier/onnxscript，安装于 main 环境，**不含 PyTorch**，onnxoptimizer 因 free-threading 不兼容而排除，基于 conda-llvm 变体）
  - `onnx-pytorch`：conda-llvm + PyTorch CPU + ONNX 生态全工具链（torch 一等公民，base 环境 GIL 启用，含 onnxoptimizer，基于 conda-llvm 变体）
  - `onnx-quantized`：onnx-dev + onnxruntime.quantization 量化工具链（INT8/FP16动态/静态量化，纯 ONNX 无 PyTorch，free-threading main 环境，基于 onnx-dev 变体）
- **新增变体模板**：`_template/` 目录（复制→替换占位符→注册→验证）
- **AI资产容器**：`.agents/` 目录（本子系统特有规则）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ devcontainer-base/AGENTS.md（项目路由入口）
            ├─ .agents/                    ← 项目AI资产容器
            │   └─ rules/                  ← 项目特有规则（Dockerfile/entrypoint/services/build-test）
            ├─ Dockerfile                  ← 基础镜像定义
            ├─ scripts/                    ← 项目辅助脚本
            └─ variants/                   ← 镜像变体系列（本子系统）
                 ├─ AGENTS.md              ← 本文件（变体系列路由入口）
                 ├─ .agents/               ← 本子系统AI资产容器
                 │   ├─ README.md          ← .agents 目录索引
                 │   └─ rules/             ← 变体管理子系统规则
                 │       ├─ build-orchestration.md  ← 构建编排规范
                 │       ├─ variant-conventions.md  ← 变体Dockerfile共享约定
                 │       ├─ testing.md              ← 测试规范
                 │       └─ new-variant-guide.md    ← 新增变体操南
                 ├─ build.sh               ← 统一构建脚本（拓扑排序+依赖处理+计时+验证）
                 ├─ shared/                ← 变体间共享组件
                 │   ├─ lib/logging.sh     ← 共享结构化日志库
                 │   └─ scripts/conda-mirror-setup.sh ← conda/pip镜像源配置脚本
                 ├─ scripts/               ← 单变体辅助脚本
                 │   ├─ build-conda-llvm.sh    ← conda-llvm一键构建脚本
                 │   ├─ build-onnx-dev.sh      ← onnx-dev一键构建脚本（依赖链 base→conda-llvm→onnx-dev）
                 │   ├─ build-onnx-pytorch.sh  ← onnx-pytorch一键构建脚本
                 │   ├─ test-conda-llvm.sh     ← conda-llvm单元测试
                 │   ├─ test-conda-llvm-smoke.sh ← conda-llvm冒烟测试
                 │   ├─ test-onnx-dev.sh       ← onnx-dev单元测试（23项，含torch缺席负向验证）
                 │   ├─ test-onnx-pytorch.sh   ← onnx-pytorch单元测试（23项，含GIL启用守卫）
                 │   ├─ test-onnx-quantized.sh ← onnx-quantized单元测试
                 │   └─ test-timer-parser.sh   ← [TIMER]日志解析单元测试
                 ├─ _template/             ← 新变体模板
                 │   ├─ Dockerfile
                 │   ├─ .env.example
                 │   ├─ README.md
                 │   └─ .agents/rules/dockerfile.md
                 ├─ conda-llvm/            ← 基础镜像+LLVM 变体（镜像源已内置）
                 │   ├─ Dockerfile
                 │   ├─ .env.example
                 │   ├─ README.md
                 │   ├─ DEPENDENCIES.md
                 │   ├─ RELEASE.md
                 │   ├─ RELEASE-GUIDE.md
                 │   └─ .agents/rules/dockerfile.md
                 ├─ onnx-dev/             ← 纯ONNX生态变体（无PyTorch，main环境）
                 │   ├─ AGENTS.md         ← 变体级智能体入口（嵌套优先）
                 │   ├─ Dockerfile
                 │   ├─ .env.example
                 │   ├─ README.md
                 │   └─ .agents/rules/dockerfile.md
                 ├─ onnx-pytorch/          ← PyTorch CPU+ONNX Runtime 变体
                 │   ├─ Dockerfile
                 │   ├─ .env.example
                 │   ├─ README.md
                 │   └─ .agents/rules/dockerfile.md
                 └─ onnx-quantized/        ← ONNX量化工具链变体（INT8/FP16）
                     ├─ AGENTS.md         ← 变体级智能体入口（嵌套优先）
                     ├─ Dockerfile
                     ├─ .env.example
                     ├─ README.md
                     ├─ ADVANCED-QUANTIZATION-GUIDE.md
                     ├─ QUANTIZATION-BEST-PRACTICES.md
                     └─ .agents/rules/dockerfile.md
```

**嵌套优先原则**：进入本目录后优先读取本文件；变体管理子系统规范在 `.agents/rules/` 下；单个变体的特有规则在各变体目录 `.agents/rules/dockerfile.md` 中；本文件和 `.agents/` 未覆盖的规则回退到 devcontainer-base 父级。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 修改/理解 build.sh 构建逻辑 | [.agents/rules/build-orchestration.md](.agents/rules/build-orchestration.md) | VARIANTS数组格式（`|`分隔）、拓扑排序、构建参数传递、[TIMER]日志解析、逐条验证机制、独立构建脚本约定 |
| 编写/修改变体 Dockerfile | [.agents/rules/variant-conventions.md](.agents/rules/variant-conventions.md) | FROM继承模式、SHELL重置、禁止覆盖项、PATH优先级、缓存挂载规范、[VALIDATION CHECKPOINT] |
| conda-llvm 变体 Dockerfile | [conda-llvm/.agents/rules/dockerfile.md](conda-llvm/.agents/rules/dockerfile.md) | LLVM安装、clang/cmake/ninja、PATH配置（镜像源已内置基础镜像） |
| onnx-dev 变体 Dockerfile | [onnx-dev/.agents/rules/dockerfile.md](onnx-dev/.agents/rules/dockerfile.md) | 纯ONNX生态（main环境安装）、PyTorch一等排除约束（双重负向验证）、free-threading防线、4追加阶段 |
| onnx-pytorch 变体 Dockerfile | [onnx-pytorch/.agents/rules/dockerfile.md](onnx-pytorch/.agents/rules/dockerfile.md) | PyTorch CPU安装、ONNX生态、PATH优先级（/opt/conda/bin最前）、4追加阶段 |
| onnx-quantized 变体 Dockerfile | [onnx-quantized/.agents/rules/dockerfile.md](onnx-quantized/.agents/rules/dockerfile.md) | onnxruntime.quantization量化工具链、FP16/INT8、neural-compressor可选、共享脚本COPY模式 |
| 编写/运行测试脚本 | [.agents/rules/testing.md](.agents/rules/testing.md) | L1-L6六层测试策略、脚本模板、pass/fail辅助函数、冒烟验证vs完整测试对比 |
| 新增镜像变体 | [.agents/rules/new-variant-guide.md](.agents/rules/new-variant-guide.md) | 7步流程：复制模板→替换占位符→更新配置→创建规则→注册到build.sh→创建测试→更新README |
| 共享日志库使用 | [shared/lib/logging.sh](shared/lib/logging.sh) | log_info/log_ok/log_error/log_step/log_metric/log_event/log_summary API |
| 基础镜像构建规范 | [../.agents/rules/dockerfile.md](../.agents/rules/dockerfile.md) | 回退到父级 devcontainer-base Dockerfile规范 |
| 全局规则（提交/代码风格） | [../../../AGENTS.md](../../../AGENTS.md) | 回退到 SpecWeave 根工作区 |
| Skill使用 | [../../../.agents/skills/](../../../../.agents/skills/) | 所有SpecWeave全局Skill可用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级项目规则 | [../AGENTS.md](../AGENTS.md) | devcontainer-base 项目路由（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | 镜像变体系列路由 |
| AI资产目录 | [.agents/README.md](.agents/README.md) | .agents目录索引和加载顺序 |
| 构建编排规范 | [.agents/rules/build-orchestration.md](.agents/rules/build-orchestration.md) | build.sh用法、VARIANTS格式、拓扑排序、镜像源、计时、验证 |
| 变体共享约定 | [.agents/rules/variant-conventions.md](.agents/rules/variant-conventions.md) | FROM模式、禁止覆盖项、PATH优先级、缓存挂载、验证检查点 |
| 测试规范 | [.agents/rules/testing.md](.agents/rules/testing.md) | 6层测试策略、脚本模板、快速验证vs完整测试 |
| 新增变体操南 | [.agents/rules/new-variant-guide.md](.agents/rules/new-variant-guide.md) | 7步新增流程、模板占位符、注册检查清单 |
| conda-llvm变体规范 | [conda-llvm/.agents/rules/dockerfile.md](conda-llvm/.agents/rules/dockerfile.md) | LLVM/clang变体特有Dockerfile规则 |
| onnx-dev变体规范 | [onnx-dev/.agents/rules/dockerfile.md](onnx-dev/.agents/rules/dockerfile.md) | 纯ONNX生态变体特有规则（无PyTorch，main环境） |
| onnx-pytorch变体规范 | [onnx-pytorch/.agents/rules/dockerfile.md](onnx-pytorch/.agents/rules/dockerfile.md) | PyTorch CPU+ONNX Runtime变体特有规则 |
| onnx-quantized变体规范 | [onnx-quantized/.agents/rules/dockerfile.md](onnx-quantized/.agents/rules/dockerfile.md) | ONNX量化工具链变体特有规则 |
| 共享性能配置脚本 | [shared/scripts/conda-perf-setup.sh](shared/scripts/conda-perf-setup.sh) | conda性能参数配置（线程、超时、solver）；镜像源已内置基础镜像 |
| 新变体模板 | [_template/](_template/) | 复制模板创建新变体 |
| 人类可读文档 | [README.md](README.md) | 变体列表和快速开始（面向人类用户） |

## 约束速览

详细约束已按主题拆分到 `.agents/rules/` 下各文件，以下是核心约束索引：

| 约束主题 | 所在文件 |
|---------|---------|
| VARIANTS数组字段分隔符（`|` 而非 `:`） | [build-orchestration.md](.agents/rules/build-orchestration.md#variants-数组格式) |
| FROM后必须重置SHELL指令 | [variant-conventions.md](.agents/rules/variant-conventions.md#shell-指令重置) |
| 禁止覆盖ENTRYPOINT/CMD/WORKDIR | [variant-conventions.md](.agents/rules/variant-conventions.md#禁止覆盖的基础镜像设置) |
| PATH优先级：/opt/venv/bin 必须高于变体路径 | [variant-conventions.md](.agents/rules/variant-conventions.md#path-优先级规则) |
| Dockerfile必须输出[TIMER]阶段标记 | [variant-conventions.md](.agents/rules/variant-conventions.md#构建阶段结构) |
| 末尾必须有[VALIDATION CHECKPOINT] | [variant-conventions.md](.agents/rules/variant-conventions.md#validation-checkpoint-规范) |
| 测试6层覆盖（L1工具链→L6配置） | [testing.md](.agents/rules/testing.md#测试分层策略) |
| 新变体7步注册流程 | [new-variant-guide.md](.agents/rules/new-variant-guide.md#新增步骤7步) |
| 镜像命名：devcontainer-base:\<variant\>-\<TAG\> | [build-orchestration.md](.agents/rules/build-orchestration.md#镜像命名约定) |

## 快速开始

```bash
# 列出可用变体
bash build.sh --list

# 构建单个变体（国内源）
bash build.sh --variant conda-llvm --cn
bash build.sh --variant onnx-pytorch --cn
bash build.sh --variant onnx-quantized --cn
bash build.sh --variant onnx-dev --cn

# 构建所有变体（按依赖顺序：conda-llvm → onnx-pytorch → onnx-quantized、onnx-dev）
bash build.sh --all --cn

# 一键构建+测试 onnx-pytorch
bash scripts/build-onnx-pytorch.sh

# 仅运行测试（镜像已存在）
bash scripts/test-conda-llvm.sh
bash scripts/test-onnx-pytorch.sh
bash scripts/test-onnx-quantized.sh

# 新增变体（7步流程）
cp -r _template <new-variant>
# 详见 .agents/rules/new-variant-guide.md
```

## 引用父级规范

本目录完全遵循 SpecWeave 工作区发现协议和嵌套路由原则：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级（devcontainer-base → SpecWeave 根）
- 子系统详细规范原子化到 `.agents/rules/` 目录，遵循单一职责原则
- 单个变体通过各自 `.agents/rules/dockerfile.md` 定义变体特有规则

## 变更日志

- 2026-08-14 | refactor | onnx-quantized v2.0.0：基础镜像从 onnx-pytorch 迁移至 onnx-dev（纯 ONNX 无 PyTorch，main 环境 free-threading cp314t），量化测试模型全部改用 onnx.helper 纯构建（make_tensor 传 bytes 必须显式 raw=True，onnx 1.22 不再自动识别）
- 2026-08-09 | feat | 新增 onnx-quantized 变体（onnxruntime.quantization 量化工具链），注册到 build.sh VARIANTS 数组
- 2026-08-08 | feat | 新增 onnx-pytorch 变体（PyTorch CPU + ONNX Runtime 深度学习运行时），添加 build-onnx-pytorch.sh/test-onnx-pytorch.sh 脚本
- 2026-08-08 | feat | 新增 shared/scripts/conda-mirror-setup.sh 共享镜像源配置脚本，变体通过环境变量驱动
- 2026-08-07 | feat | 初始化 variants/AGENTS.md + .agents/ 目录，原子化4个规则文件（build-orchestration/variant-conventions/testing/new-variant-guide）
