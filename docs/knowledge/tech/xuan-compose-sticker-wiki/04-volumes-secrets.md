---
type: Reference
id: "xuan-compose-sticker-04-volumes-secrets"
title: "卷、密钥与网络：照片进出、API Key 托管与服务互通"
tags: ["xuan-compose", "volumes", "secrets", "networks", "安全"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: src/xuan_compose/translate/mounts.py、secrets.py、networks.py、commands/updown.py、normalize.py"
summary: "讲透短挂载语法与 bind/命名卷/tmpfs 的判定规则、宿主目录自动创建与未声明卷报错；文件 secret 与环境 secret 两种 API Key 托管方式；默认网络自动创建、命名规则与 network_mode 边界。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 卷、密钥与网络

## 卷：照片怎么进去，产物怎么出来

短语法 `源:目标[:选项]` 的**源路径形态**决定挂载类型（见 `translate/mounts.py::parse_short_mount`）：

- 源以 `~/`、`./`、`/`（或 Windows 盘符）开头 → **bind 挂载**（映射宿主具体路径）；宿主目录不存在时 xuan-compose 会**自动创建**；
- 否则视为**命名卷**（如 `gen-cache:/root/.cache`），必须在顶层 `volumes:` 声明，否则解析期直接 `RuntimeError: Named volume ... no declaration was found`；
- 只写容器路径（如 `/tmp/scratch`）是**匿名卷**。

本案例的四处挂载各有意图：

```yaml
volumes:
  - ./photos:/work/photos        # bind：把输入照片送进去（读写）
  - ./out:/work/out              # bind：双产物直接落到宿主目录
  - ./prompts:/work/prompts:ro   # 只读 bind：提示词模板，容器内不可改
  - gen-cache:/root/.cache       # 命名卷：缓存随项目生命周期管理，down -v 才删
```

常用选项：`ro` 只读 / `rw` 读写（默认）；SELinux 场景的 `z`（共享重标签）/`Z`（私有重标签）；另有 `tmpfs:` 短语法挂内存盘。`image`/`glob` 等类型以及卷类型会强制翻译成 `podman --mount`，普通 bind/命名卷默认翻译为更短的 `-v`。

**命名卷的生命周期**：首次 `up` 自动创建并打上项目标签；`external: true` 的卷必须**预先存在**，缺失会报友好错误；`down -v` 才会删除项目卷（所以缓存、数据库这类要持久的东西放命名卷，而一次性交换的素材放 bind）。

> 选型口诀：**要在宿主直接看到/拿走的产物用 bind（`./out`）；只给容器自己用、可随项目销毁的用命名卷（缓存）。**

## 密钥：API Key 的三种放法（推荐程度从高到低）

### ① 文件 secret（本案例默认）

```yaml
services:
  generator:
    secrets:
      - ark_key
secrets:
  ark_key:
    file: ./secrets/ark_key.txt
```

运行时 xuan-compose 把宿主文件以**只读 bind** 挂进容器 `/run/secrets/ark_key`（目标名可用服务级 `target` 改，默认就是 secret 名；相对路径相对 compose 文件解析）。应用侧读取顺序见 [generate.py](examples/generator/generate.py)：先读 `/run/secrets/ark_key`，再回退环境变量。

```bash
mkdir -p secrets && printf '你的KEY' > secrets/ark_key.txt
# 务必把 secrets/ark_key.txt 加进 .gitignore
```

### ② 环境 secret（值来自环境变量，不落盘成文件）

顶层声明用 `environment:` 而非 `file:`，xuan-compose 在 `up` 时执行 `podman secret create --env ...`；**环境变量缺失会立即抛错**（`Environment variable ... required by secret ... is not set`），不会带着空密钥继续。

### ③ 直接插值（最简单，但要防提交）

```yaml
environment:
  ARK_API_KEY: ${ARK_API_KEY:?缺少 ARK_API_KEY}
```

值放 `.env`（不入库）。`:?` 保证缺失即中止。任何服务引用了**未在顶层声明**的 secret，都会在翻译期 `ValueError: undeclared secret`。

> 构建期就要用密钥（例如拉私有依赖）时走 build secret：`build.secrets` 会翻译成 `podman build --secret id=,src=...` 或 `id=,env=...`，避免把密钥烤进镜像层。

## 网络：默认零配置，特殊场景才手写

- 不显式声明网络时，xuan-compose 自动创建项目默认网络并把服务接入；服务默认拥有以服务名为别名的 DNS 名（同 Pod/网络内可用服务名互访）。
- 默认网络名为 `<项目名>_<网络名>`（连接符默认 `_`；开启 `name_separator_compat` 时用 `-`）。`external: true` 的网络必须预先存在。
- `network_mode` 支持 `host / none / bridge / service:<名> / container:<名> / slirp4netns / pasta / ns:<路径>`。
- **同一服务同时写 `networks` 和 `network_mode` 会直接报错**——二者互斥，按需二选一。

本案例 `gallery` 与 `generator` 同处默认网络；端口在服务级 `ports` 发布：

```yaml
generator: { ports: ["8000:8000"] }   # 宿主 8000 → 容器 8000
gallery:   { ports: ["8080:8080"] }   # 宿主 8080 → 容器 8080
```

> **同 Pod 共享网络命名空间**：默认 `in_pod=true`，一个 Pod 内容器共享 localhost，**容器端口不能重复**。所以画廊不能像独立容器那样也监听 8000，必须改用 8080；需要 Docker 风格"每服务独立网络栈"可关闭 in_pod（见 [09 章](09-pitfalls-faq.md)）。

端口短语法 `[宿主IP:]宿主端口:容器端口[/proto]`，也支持长字典（`target/published/host_ip/protocol`），规范化后统一为字符串列表。
