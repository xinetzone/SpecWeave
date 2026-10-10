---
type: Reference
id: "xuan-compose-sticker-05-lifecycle-tasks"
title: "服务生命周期、依赖条件与 run --rm 一次性任务"
tags: ["xuan-compose", "depends_on", "healthcheck", "up", "down", "run", "一次性任务"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: src/xuan_compose/commands/updown.py、runexec.py、dependencies.py、model.py、pull.py、translate/container_args.py、cli/parser.py"
summary: "讲透 depends_on 三种条件到 podman wait 的映射、healthcheck、up 的镜像准备与配置哈希重建对账、down 的逆序清理，以及用 run --rm 把色幕去底实现为退出码可判定的一次性任务。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 生命周期、依赖条件与一次性任务

## depends_on：三种条件与运行时等待

短写法 `depends_on: [generator]` 在规范化阶段会变成带条件的字典，**默认条件 `service_started`**：

```yaml
gallery:
  depends_on:
    generator:
      condition: service_healthy     # 等健康检查通过，而不只是进程起来
```

Docker 风格条件到 podman 条件的映射（`model.ServiceDependencyCondition`）：

| Compose 条件 | podman wait 条件 |
|--------------|------------------|
| `service_started`（默认） | `running` |
| `service_healthy` | `healthy`（要求被依赖方配了 healthcheck） |
| `service_completed_successfully` | 同名条件（一次性任务跑完且退出码为 0） |

启动前 xuan-compose 用 `podman wait --condition=...` 阻塞等待；podman **< 4.6.0** 不支持 healthy/unhealthy 等待时会告警并跳过（所以 `gallery` 要等健康，务必确认 Podman 版本）。

健康检查在服务级声明，支持 `CMD` / `CMD-SHELL` / `NONE`，可配 `interval/timeout/retries/start_period`：

```yaml
generator:
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"]
    interval: 10s
    timeout: 3s
    retries: 5
    start_period: 5s
```

## up：不只是"启动"，而是一次声明式对账

`xuan-compose up` 的内部顺序（`commands/updown.py::compose_up`）：

1. **准备镜像** `prepare_images`：按拉取策略拉镜像、按 `build` 构建。策略优先级 `always > newer > missing > never/build`（同时有 `image` 和 `build` 时先尝试拉、失败再本地构建）。注意：为减少停机，显式预拉优化仅在 podman ≥ 5.6.0 生效，否则交给 `podman create` 隐式拉取。
2. **环境 secret 创建**：从宿主环境变量 `podman secret create`，缺变量立即报错。
3. **存量容器重建判定**：对每个已存在的服务容器，比较
   - 服务**原始配置 JSON 的 sha256**（`config_hash`），或
   - 镜像 ID 是否变化；
   命中则加入重建集，并**连带重建正在运行的依赖方（dependents）**。`--force-recreate` 无条件重建，`--no-recreate` 反之（二者同用直接报错）。
4. **建 Pod / 网络 / 卷**，`podman create` 缺失容器。
5. **启动**：`-d/--detach` 逐个 start（每个 start 前先等依赖条件），可选 `--wait` 等全部 `running|healthy`（需 podman ≥ 4.6.0）；前台模式并发 attach 并给日志加服务名前缀，收到 SIGINT/Ctrl-C 会自动触发一次 `down` 优雅收口。

> **反直觉点**：改完 compose（环境变量、挂载、端口……）不需要手动 `down`，**再执行一次 `up` 就是对账**——配置哈希变了的服务及其在跑的下游会被自动重建。

常用开关：`-d` 后台、`--build` 启动前强制构建、`--no-build`、`--no-start`（只创建不启动）、`--no-deps`、`--wait`、`--quiet-pull`、`--abort-on-container-exit/-failure`。

## down：逆序、并行、可连卷和镜像一起清

`compose_down` 按依赖逆序**并行** stop（超时取 `-t` 或服务的 `stop_grace_period`，时间字符串如 `1m30s` 由 `str_to_seconds` 解析）→ rm 容器 → 可选清理：

```bash
xuan-compose down                  # 停并删容器、Pod、网络（保留卷与镜像）
xuan-compose down --remove-orphans # 顺带清理同项目标签下的孤儿容器
xuan-compose down -v               # 额外删除项目命名卷（gen-cache 会没，bind 的 ./out 不受影响）
xuan-compose down --rmi local      # 额外删除本地构建镜像（all 连拉取的也删）
```

## run --rm：一次性任务的标准答案

色幕去底是典型的"跑完即走"：不需要常驻、不需要端口，只要把 `./out` 挂进去、处理完把产物写回 `./out`、用退出码告诉调用方成败。`run` 子命令的行为（`commands/runexec.py::compose_run`）：

1. 先确保 Pod 存在；
2. 若该服务有依赖且没给 `--no-deps`，**先以 detached 方式把依赖服务 up 起来**；
3. 构建本服务镜像（除非 `--no-build`，或加 `--build` 强制）；
4. 组装 `podman run` 参数：非 detached 默认加 `-i`（交互），`--rm` 时加 `--rm`（退出即删）；
5. 容器退出码经 `sys.exit(p)` **原样透传**——所以脚本返回 2，`xuan-compose run` 也返回 2，可直接进 shell 条件或 CI。

```bash
# keychroma 的 entrypoint 已固定为 python remove_chroma_key.py，
# REMAINDER 参数（-- 之后）原样作为脚本参数：
xuan-compose run --rm keychroma -- \
  /work/out/stickers-chroma.png /work/out/stickers.png \
  --soft-matte --despill --edge-contract 1
```

`run` 常用覆盖项：`--entrypoint`、`-e KEY=VAL`、`-v 宿主:容器`、`-p 宿主:容器`、`-u/--user`、`-w/--workdir`、`--name`、`-T`（不分配 TTY）、`--service-ports`（启用服务自身端口映射）。生图服务也复用同一镜像做一次性批处理：

```bash
xuan-compose run --rm --entrypoint python generator \
  generate.py pipeline photos/in.jpg "Crater Smoke" "Blue Summit" "Quiet Ridge"
```

这正体现了 [01 章](01-pipeline-architecture.md)的切分：**generator 镜像既能 `up` 成长驻 API，也能 `run --rm` 成一次性 CLI；keychroma 则天然只有一次性形态。**
