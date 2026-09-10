---
id: "container-copy-context-whitelist"
title: "容器构建 COPY 上下文白名单（.containerignore/.dockerignore）"
type: "code-pattern"
maturity: "L2-validated"
maturity_note: "在 jupyter-podman-client 叠加镜像中验证：client:latest 2.82 GB → 1.80 GB，/opt/apps 从 1.1 GB 缩至 260 KB；构建器覆盖：Podman 5.x、Docker BuildKit、K8s Kaniko"
date: 2026-09-08
source:
  - "SpecWeave apps/containers/client 叠加镜像大小优化里程碑（commit d5cbfd979：2.82 GB → 1.80 GB，降幅 36%）"
  - "Containerfile.client 的 COPY . → .containerignore 白名单改造（apps/containers/client/.containerignore，2026-09-08）"
related_patterns:
  - "docker-deep-slim-8step.md"
  - "docker-buildkit-optimization-best-practices.md"
  - "docker-cow-same-layer-modification.md"
  - "docker-image-layered-verification.md"
  - "content-hash-build-cache.md"
tags: ["container", "docker", "podman", "kaniko", "buildx", "oci", "containerfile", "dockerfile", ".containerignore", ".dockerignore", "build-context", "copy", "image-optimization", "cache"]
validation_count: 1
reuse_count: 1
---

# 容器构建 COPY 上下文白名单（.containerignore / .dockerignore）

## 触发场景

- **Containerfile 中只要出现 `COPY . <target>` 或 `ADD . <target>`，就必须应用本模式**（没有例外）
- 工作目录下存在任何**体积不可控**的子目录/文件：
  - 镜像缓存：`.image-cache/`、`images/`、`export/`（rootfs tar.gz，典型大小 0.5–5 GB）
  - 包管理器缓存：`node_modules/`、`target/`（Maven/Gradle/Rust）、`.m2/`、`.venv/`、`__pycache__/`
  - 构建产物：`build/`、`dist/`、`*.egg-info/`、`*.whl`、`dist-newstyle/`
  - 工作区挂载：`workspace/`、`.wsl-cache/`、`export/`、`tmp/`、`.temp/`
  - IDE/OS 杂项：`.vscode/`、`.idea/`、`.DS_Store`、`Thumbs.db`、`error.log`
  - 环境变量：`.env`、`.env.local`、`secrets.json`（不仅体积，还有安全风险）
- 历史上发现"构建出来的镜像比预期大"，且 `docker history` / `podman history` 顶层 COPY 层 Size 占比异常高（>200MB）时
- CI/CD pipeline 中，build context 的 `Sending build context to Docker daemon...` 阶段耗时 > 5s

**适用于**：Podman ≥ 4.x、Docker Engine ≥ 20.x、BuildKit、Kaniko、img、Buildah，以及任何遵循 OCI Build Context 规范的镜像构建器。

**不适用于**：
- Containerfile 完全不使用 `COPY .`，所有 COPY 都是精确路径（`COPY src/ app/src/` 等）
- 项目极小（源码树 < 1MB，无任何缓存目录）
- 使用 `docker build - < Dockerfile` 显式传入 `-` context（无 build context，不适用）

## 问题本质

大多数容器构建者在 Dockerfile/Containerfile 里写 `COPY . /app`，同时在项目根放一个 `.gitignore`，**天真地以为构建器会自动排除 `.gitignore` 里列的内容**。这是本模式要消灭的头号误区：

| 机制 | 构建器读它吗？ | 说明 |
|------|:---:|------|
| `.gitignore` | ❌ **绝不读** | 这是 git 工具链的忽略规则，Podman/Docker/Kaniko **完全独立**于 git |
| `.dockerignore` | ✅ 读（Docker/Podman/Kaniko/Buildah 均支持，作为回退） | Docker 原生，历史最久的入口 |
| `.containerignore` | ✅ **优先读**（Podman 5+ / Buildah 首选） | OCI 世界的新规范，Podman 优先找 `.containerignore`，没有才 fall back 到 `.dockerignore` |

> **核心洞察（I·四元组）**：
> - **现象**：`COPY .` 层镜像体积异常，从几十 MB 跳到数 GB
> - **根因**：构建器只解析 `.containerignore` / `.dockerignore`，忽略 `.gitignore`；而大多数项目把大目录只写在 `.gitignore` 里，没写给构建器看的文件
> - **影响**：镜像大 1–10 倍，拉取慢、推送慢、Registry 存储贵、Podman Load/导出 tar.gz 慢（1GB 要几十秒）
> - **建议**：在 Containerfile 同层目录**必放**一个 `.containerignore`（Podman 5+ 优先）+ `.dockerignore`（跨构建器保险），推荐使用"黑名单+反向白名单"结构，白名单只保留真正需要 COPY 进镜像的源码+配置

## 典型踩坑案例（本次实战数据）

SpecWeave 项目的 jupyter-podman-client 叠加镜像（commit `d5cbfd979` 之前）：

| 指标 | 无 .containerignore（旧） | 有 .containerignore（新） | 差幅 |
|---|---|---|---|
| COPY 层大小（/opt/apps） | **1.1 GB** | **260 KB** | −99.98% |
| 顶层 COPY dir 层 `podman history` Size | 1.1 GB | < 1 MB | −99.9% |
| 最终镜像 `localhost/jupyter-podman-client:latest` Size | 2.82 GB | 1.80 GB | −36%（−1.02 GB）|
| 叠加增量（相对于 rootless 基线 1.08 GB） | 1.74 GB | 720 MB | −59% |

1.1 GB 全是 3 份 rootless tar.gz（`jupyter-podman-rootless-latest.tar.gz` × 1 + 2 个旧时间戳版本）被误 COPY 进 `/opt/apps/containers/client/.image-cache/`，而 `apps/containers/client/.gitignore` 明明已经写了 `.image-cache/` ——**但 Podman 根本不读 `.gitignore`**。

## 解决方案（黑名单 + 反向白名单双段结构）

以本次实战的 `.containerignore` 为模板，推荐三段式结构：

```
# 段 1 · 敏感/临时/大文件（第一优先级）
.image-cache/
.wsl-cache/
.temp/
error.log

# 段 2 · 环境与工作区
.env
.env.*
!.env.example              # 反向保留：只保留 .env.example 模板，排除 .env.local / .env.dev
workspace/

# 段 3 · Python 构建产物/缓存
__pycache__/
*.pyc
*.pyo
build/
dist/
*.egg-info/
.eggs/

# 段 4 · 虚拟环境 & IDE/OS 杂项
.venv/
venv/
env/
.vscode/
.idea/
.DS_Store
Thumbs.db

# ============================================
# 段 5 · 反向白名单（whitelist）
# 这是关键：显式把"必须要 COPY 进镜像的内容"一条条列出
# ============================================
!src/                    # 源码树（包入口）
!.agents/rules/          # AI 治理规则骨架（运行时读）
!.agents/AGENTS.md
!.agents/README.md
!.agents/CHANGELOG.md
!AGENTS.md               # 项目入口 AGENTS
!README.md
!Containerfile.client    # 让镜像内部能看到自己的 Dockerfile（用于 env.build-layer 递归）
!pyproject.toml          # 构建后端与依赖声明（editable install 必需）
!tasks.py                # invoke 入口（必需）
!.env.example            # .env 模板（已在段 2 反向保留，再次显式声明保险）
!.gitignore              # 提供给环境内的 git 使用（可选）
```

### 关键决策（为什么这样设计）

1. **黑名单先于白名单**：先把风险高、体积大的条目排除，再用 `!` 反向保留需要的内容。这样一旦忘记更新白名单，默认是"排除"，不会误把新产生的缓存目录带入镜像。
2. **`!.env.example` 必须在 `.env.*` 之后**：`.containerignore` 规则从上往下匹配，后写的 `!` 可以覆盖先写的排除。如果顺序反了（先 `!.env.example` 再 `.env.*`），后者又会把 `.env.example` 排除。
3. **放 Containerfile 同级目录**：Podman/Docker **只在 build context 根目录查找** `.containerignore` / `.dockerignore`，不递归查找父目录。如果 build context 是 `apps/containers/client/`，那么文件必须放在该目录下，而不是仓库根。
4. **推荐镜像内保留 Containerfile 本身**：叠加镜像的 `env.build-layer` 能定位到自己的 Dockerfile，便于递归重构建；成本仅 < 500 字节，可忽略。

## 反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| "我有 `.gitignore` 了，不用写 `.containerignore`" | `.image-cache/node_modules/target` 被一起 COPY，镜像体积暴涨 3–10 倍 | 只要有 `COPY .`，就必须放 `.containerignore` + `.dockerignore` |
| 只放 `.dockerignore` 不放 `.containerignore` | 在 Podman 5+ 上虽然也工作（Podman fall back 到 `.dockerignore`），但丢失了语义，且未来 Kaniko/Buildah 可能拆分实现 | 两者都放，内容相同，`.containerignore` 作为主版本 |
| 把 `.containerignore` 放仓库根，但 build context 是子目录 | **完全不生效**，构建器只看 build context 根目录下的同名文件 | 每个 build context 根目录各放一份（或用脚本生成） |
| 只用黑名单、不用反向白名单 | 新产生的大文件（如 `debug-logs/`、`export/`）忘记加进黑名单，就会被误 COPY | 黑名单 + 反向白名单双保险 |
| 白名单里 `!src/` 写成 `!src`（缺末尾 `/`） | 前者匹配目录，后者可能匹配同名文件，语义歧义 + 将来 `src` 文件改目录会破坏行为 | 目录型白名单统一加末尾 `/` |
| 用 `COPY src/ app/`、`COPY config.json app/` 等精确路径，但还是**不写** `.containerignore` | 虽然 COPY 本身不拿别的，但构建器会把**整个 build context 打包发给 daemon**（`Sending build context to Docker daemon X MB`），CI 阶段还是会浪费带宽 | 精确 COPY 也要写 `.containerignore`，加速 `Sending context` 阶段 |
| 写了 `.containerignore`，`COPY .`，却**没验证** | 规则顺序错误、`!` 反向保留漏了、语法写了不支持的 glob | V 阶段 `podman run --rm <image> bash -lc 'ls -la /app/'` 验证 `/app/` 下没有不该有的目录 |

## 检验标准（V 阶段·五问五断言）

只要**全部满足**，就证明本模式用对了；否则回到 F 阶段修正：

| 断言编号 | 检查动作 | 期望结果 |
|:---:|------|------|
| V1 | 列出 build context 根目录 | 同时存在 `.containerignore` 和 `.dockerignore`（两份内容逐字节相等或等价）|
| V2 | 在镜像内执行 `du -sh /<COPY target>/` | 目标目录大小 ≤ 纯源码大小 × 1.2（安全裕量 20%），绝不能有数 GB 的误拷贝 |
| V3 | 在镜像内执行 `ls -la /<COPY target>/` 列表 | **不存在**段 1/2/3/4 中任意一条黑名词典对应的文件/目录（`ls -la /opt/apps/containers/client/` 不能看到 `.image-cache/`）|
| V4 | `podman history <image> --format "{{.Size}}\|{{.CreatedBy}}"` 找 COPY dir 行 | Size < 10 MB（对纯 Python/Node/Go 项目）|
| V5 | 对比 `podman build` 首次日志的 `Building with podman...` 之后 context 打包大小（或 Docker 的 `Sending build context`）| context 打包体积 < 源码树大小 × 1.3，不能出现数百 MB |

## 跨构建器迁移适用性（A·迁移验证）

| 构建器 | 是否识别 `.containerignore`？ | 是否识别 `.dockerignore`？ | 本模式适用性 | 注意事项 |
|---|:---:|:---:|:---:|---|
| Podman 5+ | ✅ **优先** | ✅ 回退 | ✅ 完全 | `.containerignore` 为主；无则 fall back `.dockerignore` |
| Podman 3.x / 4.x | ⚠️ 部分（3.4+ 才加） | ✅ 完全 | ✅ 完全 | 建议同时放两份 `.containerignore + .dockerignore` |
| Docker Engine 20+ (legacy builder) | ❌ | ✅ 完全 | ✅ 完全 | Docker 不看 `.containerignore`，但 `.dockerignore` 100% 支持 |
| Docker BuildKit (DOCKER_BUILDKIT=1) | ❌ | ✅ 完全 | ✅ 完全 | BuildKit 额外支持 `.dockerignore` 的扩展语法（`**`、`!` 反向更稳） |
| Kaniko (gcr.io/kaniko-project/executor) | ❌ | ✅ 完全 | ✅ 完全 | Kaniko 严格遵循 `.dockerignore`，规则语法与 Docker 一致 |
| Buildah (buildah bud) | ✅ 完全（>=1.24） | ✅ 回退 | ✅ 完全 | 与 Podman 共享底层库 |
| img (genuinetools/img) | ❌ | ✅ 完全 | ✅ 完全 | 基于 BuildKit 早期 fork，对 `.dockerignore` 与 Docker 一致 |
| nerdctl build | ✅ 完全（>=1.0） | ✅ 回退 | ✅ 完全 | 与 Podman 相同，Containerd 原生 |

> **迁移断言**：只要同时放置 `.containerignore`（OCI 原生）+ `.dockerignore`（跨构建器兼容）两份文件，**在上述 8 个主流构建器上全部得到等价的 build context 过滤结果**。两份文件内容保持一致即可；Podman 世界优先拿 `.containerignore`，Docker/Kaniko 拿 `.dockerignore`。

## 与相关模式的协同

| 模式 | 协同方式 |
|---|---|
| `docker-deep-slim-8step.md` | 本模式只负责 COPY 层大小，8 步法负责 RUN 层/二进制大小，两者叠加通常能让镜像从 3 GB → 1.5 GB 以下 |
| `content-hash-build-cache.md` | `.containerignore` 正确后，`COPY .` 的 content hash 会稳定且小，BuildKit content hash cache 命中率显著提升 |
| `docker-cow-same-layer-modification.md` | 本模式避免 COPY 层 COW 膨胀源，COW 模式负责 RUN 与多层修改间的膨胀 |
| `docker-image-layered-verification.md` | V 阶段的验证步骤可以复用它的"分层 Size 对比 + 内部文件清单"模式 |
