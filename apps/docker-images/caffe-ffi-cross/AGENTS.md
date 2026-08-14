# caffe-ffi-cross - AI协作者入口 (AGENTS Manifest)

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
> 本文件是 caffe-ffi-cross 子项目的 AI 协作者入口。本项目是一个交叉编译构建镜像，
> 基于 continuumio/miniconda3，提供 Linux→macOS/Windows 的 conda 包交叉编译能力，
> **不包含运行时服务（无SSH/Jupyter/supervisord/entrypoint）**，是纯构建工具镜像。
> 所有全局规则继承自 SpecWeave 根工作区，本文件仅定义本项目特有的上下文路由与约束入口。

## 项目概述

- **项目类型**：Docker 构建工具镜像（conda包交叉编译，无运行时服务）
- **基础镜像**：continuumio/miniconda3:latest（基于Debian，非ubuntu基础）
- **核心功能**：
  - Dockerfile.macos-cross：Linux→macOS（osx-64）交叉编译
  - Dockerfile.win-cross：Linux→Windows（win-64）交叉编译 + Wine L3测试
- **Locale**：C.UTF-8（构建镜像不需要中文locale）
- **无服务**：无SSH/Jupyter/supervisord/entrypoint/tini
- **非root用户**：不创建（构建容器以root运行）
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）
- **AI资产容器**：`.agents/` 目录

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/docker-images/caffe-ffi-cross/AGENTS.md（本文件，交叉编译构建工具入口）
       ├─ .agents/README.md       ← AI资产容器索引
       │   └─ rules/
       │       ├─ dockerfile.md   ← Dockerfile 交叉编译规范（双Dockerfile/conda-forge编译器）
       │       └─ build-test.md   ← 构建与测试流程
       ├─ Dockerfile.macos-cross  ← macOS交叉编译单阶段构建
       ├─ Dockerfile.win-cross    ← Windows交叉编译双阶段构建（含Wine）
       ├─ build.sh                ← macOS构建脚本（--mirror/--skip-sdk）
       ├─ run.sh                  ← 运行脚本
       ├─ docker-compose.yml      ← Compose编排
       ├─ conda_build_config.yaml ← conda-build配置
       └─ scripts/                ← 辅助脚本（build-macos-cross.sh/build-win-cross.sh/test-cross-build.sh）
```

**重要**：本项目是**纯构建工具镜像**，与apps下其他运行时镜像（jupyter-ssh-base/devcontainer-base等）有本质区别：不启动任何服务，无ENTRYPOINT，运行时用户指定编译命令。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/交叉编译器配置 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 双Dockerfile结构、conda-forge交叉编译器、SDK下载、Wine L3测试 |
| macOS交叉编译构建 | [.agents/rules/dockerfile.md#macos交叉编译dockerfilemacos-cross](.agents/rules/dockerfile.md#macos交叉编译dockerfilemacos-cross) | clang_osx-64、MacOSX11.3.sdk、CONDA_BUILD_SYSROOT |
| Windows交叉编译构建 | [.agents/rules/dockerfile.md#windows交叉编译dockerfilewin-cross](.agents/rules/dockerfile.md#windows交叉编译dockerfilewin-cross) | clang_win-64、m2w64-sysroot、两阶段构建、Wine可选 |
| 构建脚本/镜像源配置 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh参数、--mirror/--skip-sdk、跨平台构建命令 |
| 运行编译/产物验证 | [.agents/rules/build-test.md](.agents/rules/build-test.md#运行交叉编译) | VOLUME挂载、Mach-O/PE格式验证、test-cross-build.sh |
| AI资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/目录结构、无entrypoint/services说明 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口 |
| 本文件入口 | AGENTS.md（本文件） | caffe-ffi-cross子项目路由入口 |
| AI资产容器 | [.agents/README.md](.agents/README.md) | .agents/目录索引（仅2个rules，无entrypoint/services） |
| Dockerfile规范 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 双Dockerfile/交叉编译器/SDK/Wine/无服务 |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh参数/跨平台命令/产物验证 |
| macOS构建文件 | Dockerfile.macos-cross | 单阶段：miniconda3→交叉编译器→macOS SDK→conda-build配置 |
| Windows构建文件 | Dockerfile.win-cross | 两阶段：cross-builder（编译器）→wine-runtime（Wine+L3测试） |
| 构建脚本 | build.sh | macOS构建，支持--mirror/--skip-sdk |
| Compose编排 | docker-compose.yml | 构建/运行编排 |
| conda-build配置 | conda_build_config.yaml | conda-build版本/平台配置 |

## 项目约束速览

| 约束主题 | 所在文件 |
|---------|---------|
| 基础镜像为continuumio/miniconda3（非ubuntu） | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| 双Dockerfile（macos + win-cross） | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| 纯构建镜像，无SSH/Jupyter/entrypoint/services | [dockerfile.md](.agents/rules/dockerfile.md#反模式) |
| 不创建非root用户（root运行） | [dockerfile.md](.agents/rules/dockerfile.md#反模式) |
| Locale为C.UTF-8（无中文locale包） | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| conda-forge交叉编译器（clang_osx-64/clang_win-64） | [dockerfile.md](.agents/rules/dockerfile.md#macos交叉编译dockerfilemacos-cross) |
| macOS SDK下载/跳过机制 | [dockerfile.md](.agents/rules/dockerfile.md#构建参数) |
| Wine L3测试best-effort（失败不阻断） | [dockerfile.md](.agents/rules/dockerfile.md#windows交叉编译dockerfilewin-cross) |

## 快速开始

```bash
# 构建macOS交叉编译镜像
bash build.sh --mirror tuna

# 构建Windows交叉编译镜像
docker build -f Dockerfile.win-cross -t caffe-ffi-cross-win:latest .

# 运行macOS交叉编译
docker run --rm \
  -v /path/to/caffe-ffi:/workspace/caffe-ffi \
  -v $(pwd)/output:/output \
  caffe-ffi-cross-macos:latest
```

完整构建参数和问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- AI资产原子化拆分至 `.agents/` 目录，遵循单一职责原则
- 明确标注本项目的特殊性（纯构建工具镜像，无运行时服务）

## 变更日志

- 2026-08-07 | feat | 新增AGENTS.md和.agents/原子化结构（2个rules文件），明确标注纯构建镜像特性
