---
type: Reference
id: "xuan-compose-sticker-02-install-discovery"
title: "安装、工程骨架与 compose 文件发现规则"
tags: ["xuan-compose", "安装", "compose", "文件发现", "项目名"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: xuan-compose README.md、pyproject.toml、src/xuan_compose/discovery.py、cli/parser.py、engine.py"
summary: "安装 xuan-compose 与 Podman，搭好 sticker-studio 工程骨架；讲透 compose 文件的 14 个默认名、向上 10 层递归发现、-f/COMPOSE_FILE 指定方式，以及项目名与 .env 的解析优先级。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 安装、工程骨架与文件发现

## 前置：Podman

xuan-compose 自己是纯 Python，但它翻译并调用的是 `podman`。先装好 Podman 并确认：

```bash
podman --version        # xuan-compose 运行时会探测版本，部分能力（如 --wait）需 podman >= 4.6.0
podman run --rm docker.io/library/hello-world
```

Windows 用户建议在 **WSL2** 里装 Podman 并在 WSL 中跑 xuan-compose（xuan-compose 的权威测试门禁就是 WSL + Python 3.14；Windows 原生主要承担 ruff/mypy 门禁，路径分隔符相关行为与上游同构）。

## 安装 xuan-compose

xuan-compose 位于 xuanspace monorepo（要求 **Python ≥ 3.14**，仅依赖 `python-dotenv` 与 `PyYAML`）：

```bash
cd projects/xuanspace/libs/xuan-compose
pip install -e .                 # 或 pip install -e ".[test,lint]"
```

安装后同时得到两个等价入口：

- console script：`xuan-compose ...`
- 模块入口：`python -m xuan_compose ...`

版本号独立于上游，引擎上报的兼容版本为 `1.6.0+xuan.1`（会写进容器标签 `io.podman.compose.version`）：

```bash
xuan-compose version             # 注意：无参数 / help 的退出码沿用上游怪癖为 -1，见 09 章
```

> `version` 与 `systemd create-unit` 是少数**不需要** compose 文件就能跑的命令。

## 工程骨架

在任意工作目录按 [examples/](examples/README.md) 搭好骨架（本教程后续命令都假设在该目录执行）：

```text
sticker-studio/
├── compose.yaml          # 编排主文件
├── .env                  # 环境变量（不入库）
├── secrets/ark_key.txt   # 文件 secret（不入库）
├── photos/               # 输入照片
├── out/                  # 产物输出
├── prompts/              # 提示词模板
├── generator/            # 生图镜像构建上下文
└── keychroma/            # 去底镜像构建上下文
```

## compose 文件是怎么被找到的

不显式 `-f` 时，xuan-compose 从**当前目录向上递归最多 10 层**，在每层按固定顺序找默认文件名，找到即停止，并把工作目录切到该文件所在目录（相对路径因此都相对 compose 文件解析）。14 个默认名按顺序为：

```text
compose.yaml                compose.yml
compose.override.yaml       compose.override.yml
podman-compose.yaml         podman-compose.yml
docker-compose.yml          docker-compose.yaml
docker-compose.override.yml docker-compose.override.yaml
container-compose.yml       container-compose.yaml
container-compose.override.yml  container-compose.override.yaml
```

同目录若同时存在多个候选（如 `compose.yaml` 与 `compose.override.yaml`），会按顺序一起加载、后者覆盖合并。

三种显式指定方式：

```bash
xuan-compose -f compose.yaml config            # -f 可重复，多次追加按序合并
cat compose.yaml | xuan-compose -f - config    # “-” 表示从标准输入读
COMPOSE_FILE=a.yaml:b.yaml xuan-compose config # 环境变量；分隔符用 COMPOSE_PATH_SEPARATOR
```

> 教学建议：本案例统一用标准名 `compose.yaml`，享受"向上递归发现"，命令最干净。

## 项目名（project name）的解析优先级

项目名决定 Pod、网络、命名卷、容器名的前缀（如 `pod_sticker-studio`、`sticker-studio_gen-cache`）。优先级从高到低：

1. 命令行 `-p/--project-name`；
2. 环境变量 `COMPOSE_PROJECT_NAME`；
3. compose 文件顶层 `name:`（本案例写的是 `name: sticker-studio`）；
4. compose 文件所在**目录名小写**，并用正则去掉 `[^-_a-z0-9]` 以外的字符。

## .env 与环境变量

- compose 文件**所在目录**下的 `.env` 会被自动加载；`--env-file` 可多次指定，**后者覆盖**前者。
- `.env` 里的变量用于 compose 文件插值；`PODMAN_` 前缀的变量还会被注入执行 podman 的进程环境。
- 插值在 YAML 解析**之前**进行，语法与 bash 风格一致（详见 [03 章](03-compose-walkthrough.md)）。

先做个零成本自检：把 [examples/compose.yaml](examples/compose.yaml) 和 `.env.example` 放好后运行

```bash
xuan-compose config --services     # 只列出服务名：generator / gallery / keychroma
```

能列出三个服务名，说明文件发现、解析、合并链路已经通了——此时还没有构建任何镜像、没有启动任何容器。
