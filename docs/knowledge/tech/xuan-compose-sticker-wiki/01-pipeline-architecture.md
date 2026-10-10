---
type: Reference
id: "xuan-compose-sticker-01-pipeline-architecture"
title: "流水线设计与 xuan-compose 七层架构"
tags: ["xuan-compose", "podman", "compose", "架构", "服务拓扑"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: xuan-compose README.md 架构图、src/xuan_compose 分层源码；skills: travel-memory-card-duo、seedream-50"
summary: "先按『长驻/一次性』『确定性/模型判断』两个轴切分创意流水线，再把每个环节映射到 xuan-compose 的服务与一次性任务；最后对照引擎七层架构理解编排是如何被翻译为 podman 调用的。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 流水线设计与 xuan-compose 七层架构

## 第一步：按两个轴切分环节，而不是按代码模块切

拿到一条创意流水线，先回答两个问题：

1. **长驻还是一次性？** 一直提供服务的走 `up -d`；跑完就退出、产物落盘的走 `run --rm`。
2. **确定性还是模型判断？** 同样输入必然得到同样输出、可离线复现的环节，优先做成纯本地容器；依赖模型/外部 API 的环节才需要密钥与网络。

| 环节 | 长驻/一次性 | 确定性/模型 | 编排形态 |
|------|------------|-----------|---------|
| 调 Seedream 5.0 Pro 生成记忆卡、色幕贴纸稿 | 两者皆可 | 模型判断 | `generator` 服务：默认长驻 API；也可 `run --rm` 批处理 |
| 色幕去底 + RGBA 校验 | 一次性 | **完全确定**（Pillow/numpy） | `keychroma` 任务：`run --rm`，退出码即成败 |
| 浏览成品（只读静态托管） | 长驻 | 确定 | `gallery` 服务，profile=`web`，可选 |

> **反直觉点**：很多人以为容器编排只属于 Web + 数据库。对本地创意工具链，最高频的其实是**一次性容器 + 绑定挂载 + 退出码判定**——它把"我这台机器能跑、依赖装了一堆"变成"在任何装了 Podman 的机器上同一条命令"。

数据依赖（去底必须等贴纸稿生成完）发生在两次 `run` 之间，**Compose 的 `depends_on` 不表达跨任务的数据依赖**，它只表达运行中服务的状态条件。两次一次性任务的顺序由调用方保证（shell 的 `&&`，或像 [examples/README.md](examples/README.md) 那样顺序执行）。

## 第二步：服务拓扑

```{mermaid}
flowchart TD
    subgraph pod["pod_sticker-studio（默认 in-pod=true）"]
        GEN["generator<br/>build ./generator<br/>:8000 /health"]
        GAL["gallery（profile=web）<br/>python:3.12-alpine<br/>:8080（同 Pod 避开 8000）"]
        KEY["keychroma<br/>build ./keychroma<br/>run --rm 一次性"]
    end
    H1["./photos → /work/photos"] --> GEN
    H2["./prompts → /work/prompts:ro"] --> GEN
    H3["./out → /work/out"] --> GEN
    H3 --> KEY
    H3 --> GAL
    SEC["./secrets/ark_key.txt<br/>→ /run/secrets/ark_key:ro"] --> GEN
    VOL[("命名卷 gen-cache")] --> GEN
    GAL -. "depends_on:<br/>service_healthy" .-> GEN
```

- `generator` 与 `gallery` 是长驻服务；`keychroma` 只在被 `run` 时短暂存在。
- 默认所有服务进同一个 Pod（`pod_<project>`），共享网络命名空间；这是 x-podman 的默认行为（`in_pod=true`），需要 Docker 风格独立网络栈时可关（见 [09](09-pitfalls-faq.md)）。
- `gallery` 通过 `depends_on.condition: service_healthy` 等待 `generator` 健康后才启动。

## 第三步：理解 xuan-compose 如何把 YAML 变成 podman 调用

xuan-compose 由 5541 行的上游单体 `podman_compose.py` 翻译式分层重构而来，依赖严格单向、无环：

```{mermaid}
flowchart TD
    CLI["cli/：parser.py 解析参数 · main.py 装配（sys.argv 单点读取）"]
    CMD["commands/：24 个 handler + 显式注册表"]
    ENG["engine.py：ComposeEngine 状态装配"]
    EXE["执行层：runner.py（全包唯一 import subprocess）· dependencies · pull · logs"]
    TR["translate/：container_args · mounts · networks · ports · build · secrets · resources · run_args"]
    SPEC["规范层：normalize · merge · discovery · interpolation · envfile"]
    DATA["基础层：compat · errors · types · model · logging_utils"]
    CLI --> CMD --> ENG
    ENG --> EXE
    ENG --> TR
    ENG --> SPEC
    EXE --> TR
    TR --> SPEC
    SPEC --> DATA
    TR --> DATA
    EXE --> DATA
```

对写 compose 文件的人，最该建立的心智模型是**三段管道**：

1. **发现与加载（规范层）**：`discovery` 找到 compose 文件 → `envfile` 读 `.env` → `interpolation` 做 `$VAR` 插值 → `merge` 合并多文件/override（支持 `!override`/`!reset`）→ `normalize` 把各种短语法归一化（如 `build: .` 变成 `build: {context: .}`，`depends_on` 字符串变带条件的字典）。
2. **翻译（translate 层）**：归一化后的服务描述被逐块翻译成 `podman create/run` 参数——卷（`mounts`）、端口（`ports`）、网络（`networks`）、密钥（`secrets`）、资源（`resources`）、构建（`build`），最后由 `container_args` 汇总。
3. **执行（执行层）**：`runner.py` 是全包**唯一**触碰子进程的模块；`up/down/run/...` 等 handler 编排拉镜像、构建、建 Pod/网络/卷、等待依赖条件、启动与清理。

这条管道带来两个直接好处：

- **`config` 命令能看到第 1 段的完整产物**（合并+插值+规范化后的 YAML），不用真起容器就能排查大部分编排错误；
- **`--dry-run` 走完前两段、模拟第三段**，把将要执行的 podman 调用打印出来而不真正执行。

> 库优先设计：`import xuan_compose` **零副作用**——不读 `argv`、不建引擎、不起子进程。这让"在 Python 里静态校验编排"成为可能，详见 [08 章](08-library-api.md)。

## 24 个命令速览

`ls / version / wait / systemd / pull / push / build / up / down / ps / run / cp / exec / start / stop / restart / logs / config / port / pause / unpause / kill / stats / images`（外加 `help` 伪命令）。本教程会用到其中最核心的 `config / build / pull / up / down / run / logs / ps / exec / version`。
