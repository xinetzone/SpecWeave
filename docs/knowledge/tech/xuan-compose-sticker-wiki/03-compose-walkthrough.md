---
type: Reference
id: "xuan-compose-sticker-03-compose-walkthrough"
title: "compose.yaml 逐段精讲：服务、插值与 config 校验"
tags: ["xuan-compose", "compose", "yaml", "插值", "build", "config"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: examples/compose.yaml；src/xuan_compose/interpolation.py、normalize.py、merge.py、commands/inspect.py、cli/parser.py"
summary: "逐段讲解 sticker-studio 的 compose.yaml：build/image/command、environment 与 bash 风格变量插值（:-/-/:?/?/:+/+ 与 $$ 转义）、profiles、顶层 volumes/secrets 声明，以及用 config 命令在起容器前验证合并结果。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# compose.yaml 逐段精讲

完整文件见 [examples/compose.yaml](examples/compose.yaml)。本章只讲**服务定义、变量与校验**；卷/secret/网络在 [04 章](04-volumes-secrets.md)，生命周期在 [05 章](05-lifecycle-tasks.md)。

## 顶层骨架

```yaml
name: sticker-studio
services: { generator: ..., gallery: ..., keychroma: ... }
volumes: { gen-cache: }      # 命名卷必须在此声明
secrets: { ark_key: { file: ./secrets/ark_key.txt } }
```

现代 Compose 规范**不再要求** `version:` 字段，xuan-compose 也不依赖它。

## 服务的两种镜像来源：build 与 image

```yaml
generator:
  build:
    context: ./generator      # 构建上下文目录（内含 Dockerfile）
  command: ["uvicorn", "generate:app", "--host", "0.0.0.0", "--port", "8000"]

gallery:
  image: docker.io/library/python:3.12-alpine   # 直接拉取现成镜像
  command: ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
```

规范化阶段，简写 `build: ./generator` 会被归一为 `build: {context: ./generator}`；最终规范化时相对 `context` 会转成绝对路径（git URL 除外）。默认 Dockerfile 查找顺序为 `Containerfile / ContainerFile / containerfile / Dockerfile / DockerFile / dockerfile`，也可用 `dockerfile:` 指定、用 `dockerfile_inline:` 内联（二者互斥）。

`command:` 是**运行期**覆盖镜像默认命令；`keychroma` 用 `entrypoint:` 固定主程序，再由 `run` 在后面追加参数：

```yaml
keychroma:
  build: { context: ./keychroma }
  entrypoint: ["python", "remove_chroma_key.py"]
```

## environment：把"会变的东西"全部外置

```yaml
generator:
  environment:
    ARK_BASE_URL: ${ARK_BASE_URL:-https://ark.cn-beijing.volces.com/api/v3}
    ARK_MODEL: ${ARK_MODEL:-doubao-seedream-5-0-pro-260628}
    OUTPUT_SIZE: ${OUTPUT_SIZE:-1248x832}
```

`environment` 支持字典或 `["KEY=VAL", ...]` 短表（规范化会互相转换）。这里体现了一条核心原则：**编排文件描述结构，端点/模型/密钥等环境差异全部走变量**，同一份 compose.yaml 可以在不同账号、不同区域、不同模型间切换而不改动正文。

### 插值语法（YAML 解析前进行）

xuan-compose 的插值与 docker-compose/bash 风格对齐：

| 写法 | 含义 |
|------|------|
| `$VAR` / `${VAR}` | 取变量值，未设置即空串 |
| `${VAR:-default}` | 未设置**或为空**时用 `default` |
| `${VAR-default}` | 仅在**未设置**时用默认（空串保留） |
| `${VAR:?err}` | 未设置或为空时**直接报错**中止 |
| `${VAR?err}` | 未设置时报错 |
| `${VAR:+alt}` / `${VAR+alt}` | 已设置（非空）时替换为 `alt` |
| `$$` | 转义为字面量 `$`（想把 `$` 传给容器必须写 `$$`） |

密钥最稳妥的写法是"缺失即拒绝启动"：

```yaml
ARK_API_KEY: ${ARK_API_KEY:?需要在 .env 或环境变量中提供 ARK_API_KEY}
```

> 本案例默认用**文件 secret**（见 [04 章](04-volumes-secrets.md)）而不是把密钥放进 interpolation；`.env.example` 里同时给出了环境变量方案，二选一即可。

## profiles：把可选服务藏起来

```yaml
gallery:
  profiles: ["web"]
```

不带 profile 执行 `up` 时 `gallery` **不会**被创建；显式开启才纳入：

```bash
xuan-compose up -d                    # 只起 generator（及默认 profile 服务）
xuan-compose --profile web up -d      # 额外起 gallery
```

`--profile` 可重复指定多个。把"锦上添花"的画廊放进独立 profile，主流水线保持最小。

## 合并：多文件与 override

`-f` 多次指定、默认的 `compose.override.yaml` 都会与主文件深度合并：字典递归合并、`command/entrypoint` 整体替换、`volumes` 列表按挂载目标去重后追加。需要整体替换一个列表项时可用 YAML 标签 `!override`，重置回空可用 `!reset`。

## 起容器前先用 config 把第 1 段管道看清楚

`config` 输出的是**发现→加载 .env→插值→合并→规范化**之后的最终 YAML：

```bash
xuan-compose config                    # 打印合并后的完整 YAML
xuan-compose config --services         # 只列服务名
xuan-compose config --quiet            # 只解析不打印（纯校验，非零退出即有问题）
xuan-compose config --no-normalize     # 跳过最终规范化，看合并原貌
```

排查顺序建议固定为：**`config --quiet`（语法/插值/引用）→ `--dry-run up`（翻译出的 podman 调用）→ 真正 `up`**。前两步都不需要真实容器，能挡掉绝大多数低级错误（变量名拼错、未声明的卷/secret、相对路径错位）。
