# pytorch-base - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/ 下的子应用，全局规则继承自 SpecWeave 根 AGENTS.md
> 步骤 3：按上下文路由表加载本项目特有规范
> 步骤 3.5：自检 — 确认已理解父级规则与本项目特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 pytorch-base 子项目的 AI 协作者入口。本项目是一个 PyTorch Docker 基础镜像构建项目，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束。

## 项目概述

- **项目类型**：Docker 镜像构建项目（PyTorch 基础开发环境）
- **基础镜像**：ubuntu:26.04
- **核心组件**：Miniconda3 + Python 3.14 + PyTorch
- **离线包支持**：`offline/` 目录统一存放离线资源
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准

## 目录结构说明

```
pytorch-base/
├── AGENTS.md           ← 本文件，AI协作者入口
├── Dockerfile          ← 主镜像构建定义（7阶段构建）
├── .dockerignore       ← Docker构建忽略规则
├── build.sh            ← 一键构建脚本（含离线模式、自动验证）
├── entrypoint.sh       ← 容器入口点脚本（环境激活、信号转发）
├── environment.yml     ← Conda环境定义（可选参考）
└── offline/            ← 离线资源目录（始终包含在构建上下文中）
    ├── miniconda/      ← Miniconda安装脚本
    │   └── .gitkeep
    ├── wheels/         ← pip wheel包
    │   └── .gitkeep
    └── conda-pkgs/     ← conda包缓存
        └── .gitkeep
```

**嵌套路由关系**：

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/pytorch-base/AGENTS.md（本文件，项目特有约束）
       ├─ Dockerfile         ← 主镜像构建定义（7阶段）
       ├─ build.sh           ← 构建脚本（在线/离线/验证）
       ├─ entrypoint.sh      ← 容器入口点
       ├─ environment.yml    ← Conda环境参考
       └─ offline/           ← 离线资源统一目录
```

**嵌套优先原则**：进入本目录后优先读取本文件；本文件未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/构建优化 | 本文件 + Dockerfile | PyTorch基础镜像构建规范、7阶段构建、层缓存策略、国内源配置 |
| 离线包管理 | offline/ 目录 + build.sh | 离线资源统一存放于 offline/，通过 build.sh --prepare-offline 自动下载 |
| 构建脚本修改 | build.sh | 参数解析、离线准备、BuildKit缓存、13项自动验证 |
| 入口点逻辑 | entrypoint.sh | conda环境自动激活、用户切换、信号转发、启动横幅 |
| 镜像构建与测试 | 本文件「构建命令速查」章节 | ./build.sh 一键构建，自动运行验证测试 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | pytorch-base子项目路由 |
| Docker构建文件 | Dockerfile | 7阶段构建：系统包→Miniconda→镜像源→PyTorch→用户→entrypoint→验证 |
| 构建脚本 | build.sh | 一键构建，支持--gpu/--offline/--prepare-offline/--no-cache等参数 |
| 入口点脚本 | entrypoint.sh | 容器启动逻辑，默认以ai用户运行，自动激活conda环境 |
| 离线资源目录 | offline/ | 统一存放miniconda安装包、wheels、conda缓存 |
| Docker忽略规则 | .dockerignore | 排除.git/.trae/.agents/specs等非构建文件 |

## 构建命令速查

构建 PyTorch 基础镜像：

```bash
# 在线构建（默认，从国内镜像源下载包）
./build.sh

# 指定PyTorch版本和Python版本
./build.sh --torch-version 2.5.1 --python-version 3.14

# GPU版本（CUDA 12.4，需要nvidia-docker2）
./build.sh --gpu

# 自定义镜像标签
./build.sh --tag my-pytorch:latest

# 无缓存构建（用于调试）
./build.sh --no-cache

# 离线构建（使用offline/目录中的本地包）
./build.sh --offline

# 第一步：准备离线资源（在有网络的机器上执行）
./build.sh --prepare-offline
# 第二步：离线构建（offline/中有缓存后，可无网络构建）
./build.sh --offline

# 跳过验证（不推荐）
./build.sh --no-verify

# 运行容器（验证环境）
docker run --rm pytorch-base:2.5.1-py3.14-cpu python -c "import torch; print(torch.__version__)"

# 交互式shell
docker run -it --rm pytorch-base:2.5.1-py3.14-cpu

# 作为基础镜像被其他Dockerfile引用
FROM pytorch-base:2.5.1-py3.14-cpu
```

## 项目特有约束

1. **基础镜像锁定**：固定使用 `ubuntu:26.04`，除非用户明确要求变更
2. **Python版本**：默认使用 Python 3.14（通过 Miniconda3 安装）
3. **离线资源目录**：所有离线资源统一存放在 `offline/` 的三个子目录中，该目录始终包含在构建上下文中（空目录仅含.gitkeep，不影响构建速度）
4. **构建日志**：Dockerfile 中每个阶段使用 `echo "=== Stage N/7: ... ==="` 输出阶段标题，步骤内使用 `echo "[BUILD] ..."` 输出日志
5. **镜像体积**：每个 RUN 指令后清理 apt/pip/conda 缓存，减小最终镜像体积
6. **中文环境**：容器内默认 locale 为 `zh_CN.UTF-8`，时区 `Asia/Shanghai`
7. **非root用户**：容器默认以 `ai` 用户（UID 1000）运行，配置sudo免密
8. **conda环境**：环境名为 `pytorch`，路径为 `/opt/conda/envs/pytorch/`，通过 .bashrc 和 profile.d 自动激活
9. **BuildKit缓存**：使用 `--mount=type=cache` 缓存 conda pkgs 和 pip cache，加速重复构建
10. **网络容错**：apt配置5次重试，wget配置5次重试/120秒超时，conda安装失败自动fallback到pip

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程

## 变更日志

- 2026-07-22 | feat | 重构离线资源管理：统一使用 offline/ 目录替代分散的 wheels/ 和 conda-cache/，Dockerfile通过COPY+shell检测实现条件离线安装；build.sh 增加 --prepare-offline 自动下载离线资源
- 2026-07-22 | feat | 初始化 pytorch-base 项目结构：AGENTS.md、Dockerfile、build.sh、entrypoint.sh、environment.yml
