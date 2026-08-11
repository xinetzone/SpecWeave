# xmnn-runtime Docker - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本文件位于 apps/xmnn-runtime/docker/，
>         全局规则继承自 SpecWeave 根 AGENTS.md（路径：../../../AGENTS.md）
> 步骤 3：按上下文路由表加载本项目特有规范（.agents/rules/ 下对应文件）
> 步骤 3.5：自检 — 确认已理解父级规则与本项目特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 xmnn-runtime Docker 构建的 AI 协作者入口。本项目是一个 XMNN 运行时镜像，
> 基于 npu-tvm-build:conda 外部基础镜像，提供 TVM/VTA/XMNN Python 运行环境，
> 通过 entrypoint.sh 实现 conda 激活 + UID/GID 自适应 + gosu 用户切换。
> 所有全局规则继承自 SpecWeave 根工作区，本文件仅定义 Docker 构建特有的上下文路由。
>
> **注意**：本AGENTS.md位于`docker/`子目录（非项目根目录），.agents/也在docker/下。

## 项目概述

- **项目类型**：Docker 运行时镜像（XMNN/TVM Python环境）
- **基础镜像**：npu-tvm-build:conda（外部预构建，conda环境tvm-build，Python 3.14.6）
- **核心组件**：TVM + VTA + XMNN + pandas/matplotlib/openpyxl/tqdm/tomlkit
- **中文时区**：Asia/Shanghai（locale继承基础镜像）
- **非root用户**：ai（默认UID/GID=1000，运行时自动适配/workspace权限）
- **无服务**：无SSH/Jupyter/supervisord/tini
- **父级工作区**：SpecWeave 根目录（`../../../AGENTS.md`）
- **AI资产容器**：`.agents/` 目录（位于docker/下）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/xmnn-runtime/docker/AGENTS.md（本文件，Docker构建路由入口）
       ├─ .agents/README.md          ← AI资产容器索引
       │   └─ rules/
       │       ├─ dockerfile.md      ← Dockerfile 6阶段构建规范
       │       ├─ entrypoint.md      ← 启动脚本规范
       │       └─ build-test.md      ← 构建与测试流程
       ├─ Dockerfile                 ← 6阶段构建定义（系统包→pip→用户→xmnn→entrypoint→验证）
       ├─ entrypoint.sh              ← 容器入口（conda激活+UID自适应+gosu切换）
       ├─ build.sh / build.ps1       ← 构建脚本（含日志库和计时）
       ├─ verify.sh                  ← 验证脚本
       ├─ lib/logging.sh             ← 结构化日志共享库
       ├─ _xmnn_init.py / xmnn_init.pth ← XMNN初始化文件
       ├─ run_redlines.py / test_redlines.py ← 红线测试
       └─ .dockerignore              ← Docker构建忽略规则
```

**注意路径层级**：本文件位于`docker/`子目录，引用SpecWeave根目录需要`../../../`前缀。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/层缓存优化 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | BuildKit语法、6阶段结构、缓存挂载、构建计时、★热点层设计 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | conda激活、UID/GID自适应、gosu切换、TVM/VTA路径配置 |
| 构建脚本/日志库 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh参数、JSON日志、构建上下文（项目根目录）、verify.sh |
| XMNN安装/依赖验证 | [.agents/rules/dockerfile.md#验证检查点](.agents/rules/dockerfile.md#验证检查点) | ldd检查、核心导入、TE compute验证 |
| 权限问题排查 | [.agents/rules/entrypoint.md#uidgid自适应逻辑](.agents/rules/entrypoint.md#uidgid自适应逻辑) | HOST_UID/HOST_GID自动检测、冲突处理 |
| AI资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/目录结构、路径说明 |
| 全局规则（提交/代码风格/沟通） | [../../../AGENTS.md](../../../AGENTS.md) → [../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../../.agents/skills/](../../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../../.agents/commands/](../../../.agents/commands/) | 七概念指令集，通过父级调用 |
| Dockerfile自动化测试 | [../../../.agents/scripts/test-dockerfiles.ps1](../../../.agents/scripts/test-dockerfiles.ps1) | 项目根目录测试脚本 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../../AGENTS.md](../../../AGENTS.md) | SpecWeave根工作区入口 |
| 本文件入口 | AGENTS.md（本文件） | xmnn-runtime Docker构建路由入口 |
| AI资产容器 | [.agents/README.md](.agents/README.md) | .agents/目录索引（位于docker/下） |
| Docker构建规范 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 6阶段/缓存/计时/★热点/验证检查点 |
| 入口点脚本规范 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | conda激活/UID自适应/gosu/无tini/无服务 |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh/verify.sh/上下文路径/权限排查 |
| Docker构建文件 | Dockerfile | 6阶段：系统包→pip依赖→ai用户→xmnn安装→entrypoint→最终验证 |
| 入口点脚本 | entrypoint.sh | conda activate + UID/GID自适应 + gosu切换 |
| 构建脚本 | build.sh / build.ps1 | 含结构化日志、JSON事件、构建计时 |
| 日志库 | lib/logging.sh | 统一日志（彩色分级+JSON指标） |

## 项目约束速览

| 约束主题 | 所在文件 |
|---------|---------|
| BuildKit语法声明 | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| 6阶段构建结构（★热点Stage 4） | [dockerfile.md](.agents/rules/dockerfile.md#6阶段结构runtime-logical-layering-v13) |
| BuildKit缓存挂载（apt+pip） | [dockerfile.md](.agents/rules/dockerfile.md#层缓存优化) |
| 构建计时+[TIMER]+汇总表 | [dockerfile.md](.agents/rules/dockerfile.md#构建计时build-timing) |
| COPY隔离（wheels vs entrypoint分层） | [dockerfile.md](.agents/rules/dockerfile.md#层缓存优化) |
| ai用户UID/GID自适应（非固定1000） | [entrypoint.md](.agents/rules/entrypoint.md#uidgid自适应逻辑) |
| gosu用户切换（无tini） | [entrypoint.md](.agents/rules/dockerfile.md#反模式) |
| conda环境tvm-build激活 | [entrypoint.md](.agents/rules/entrypoint.md#启动流程) |
| TVM_LIBRARY_PATH/VTA_HW_PATH | [entrypoint.md](.agents/rules/entrypoint.md#启动流程) |
| 无SSH/Jupyter/supervisord/tini | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| 构建上下文为项目根目录（非docker/） | [build-test.md](.agents/rules/build-test.md#构建前提) |
| bash -n语法验证检查点 | [dockerfile.md](.agents/rules/dockerfile.md#验证检查点) |

## 快速开始

```bash
# 构建（在docker/目录执行，上下文自动设为项目根目录）
cd docker/ && bash build.sh xmnn-runtime:latest

# 运行（推荐--init，因镜像无内置tini）
docker run -it --rm --init -v $(pwd):/workspace xmnn-runtime:latest

# 验证
python -c "import tvm, vta, xmnn; print('OK')"
```

完整构建参数和问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../../AGENTS.md`（注意：比其他apps项目多一层`../`）
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- AI资产原子化拆分至 `.agents/` 目录，遵循单一职责原则

## 变更日志

- 2026-08-07 | feat | 新增AGENTS.md和.agents/原子化结构（3个rules文件），.agents位于docker/子目录
