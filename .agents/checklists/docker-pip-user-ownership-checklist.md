---
id: "docker-pip-user-ownership-checklist"
title: "Docker 构建时/运行时属主分离（PIP_USER 治理）检查清单"
source: "docs/retrospective/reports/build-engineering/retrospective-chaos-ai-portable-slim-20260811/README.md"
related_patterns:
  - "docker-buildtime-runtime-ownership-separation.md"
  - "docker-buildtime-vs-runtime-config.md"
  - "docker-buildkit-optimization-best-practices.md"
  - "dockerfile-runtime-logical-layering.md"
tags: ["docker", "checklist", "pip-user", "ownership", "non-root-user", "conda", "multistage-build"]
---

# Docker 构建时/运行时属主分离（PIP_USER 治理）检查清单

> 基于混沌 AI portable 镜像瘦身复盘萃取。核心问题：构建期以 root 关闭 `PIP_USER` 写入共享 site-packages，运行期非 root 用户可读；**禁止对大型目录整体 `chown -R`**（产生数 GB 复制层）。
>
> **适用场景**：任何「多阶段 Dockerfile + 非 root 运行用户 + conda/pip AI 开发容器」，尤其是交互式多用户镜像（jupyter/SSH）与运行时镜像。

---

## 使用方法

在 Dockerfile 编写/审查时，按阶段逐项打勾。**任一阶段存在 🔴 项未满足即视为不合格**，需回退修复。

---

## 阶段1：构建时（deps）——包写入共享目录

| # | 检查项 | 反模式 | 说明 |
|---|--------|--------|------|
| 1 | 🔴 **构建期显式声明 `ENV PIP_USER=0`**，确保 pip 包写入共享 site-packages（如 `/opt/conda`，root 属主、全局可读） | ❌ 依赖基础镜像默认值；或构建期 `PIP_USER=1` 导致包写入 root 的 user-site（`/root/.local`），运行期非 root 用户无法 import | 若基础镜像已设置 `PIP_USER=1`，必须在构建阶段覆盖为 0 |
| 2 | 🔴 **构建期以 root 身份执行 pip/conda 安装**，必要时显式 `USER root` | ❌ 以非 root 用户安装导致 Permission denied 或意外写入 user-site | 与检查项1 配套，保证写入全局目录 |
| 3 | ✅ **确认安装后包的属主与权限**（`ls -la`）：root:root + 644/755，运行期用户可读 | ❌ 安装到 `/root/.local`，属主 root 且运行期用户无读权限 | 属主分离的最终验收标准 |
| 4 | ✅ **`pip install` 使用 `--no-cache-dir`**，避免层内重复缓存 | ❌ 不加 `--no-cache-dir`，wheel 缓存残留在层中增大体积 | 与 BuildKit 缓存挂载配套 |

## 阶段2：运行时（final）——非 root 用户可读 + 支持升级

| # | 检查项 | 反模式 | 说明 |
|---|--------|--------|------|
| 5 | ✅ **final 阶段创建专用非 root 用户**（如 `ai`/`devuser`），作为默认运行用户 | ❌ 以 root 运行容器，或用户 UID/GID 与基础镜像不一致 | 最小权限原则 |
| 6 | ✅ **交互式多用户镜像（jupyter/SSH）final 恢复 `ENV PIP_USER=1`**，支持运行期 `--user` 安装 | ❌ 交互式镜像保持 `PIP_USER=0`，运行期 `pip install --user` 不生效 | 仅交互式镜像需要；单场景运行时镜像（根安装全局可见）可保持 `PIP_USER=0` |
| 7 | ✅ **非交互/运行时镜像 final 保持 `PIP_USER=0`**（根安装需全局可见，供非 root 用户 import） | ❌ 运行时镜像误设 `PIP_USER=1`，`docker run img pip install x` 写入 `/root/.local`，非 root 用户 import 失败 | 判断标准：该镜像是否面向多用户交互 |
| 8 | ✅ **客户/运行时升级路径显式验证**：`docker run <image> pip install <pkg>` 后非 root 用户可 import | ❌ 升级后非 root 用户 ImportError，仅 root 可 import | 模拟客户升级链路 |

## 阶段3：禁止整体 chown（镜像体积红线）

| # | 检查项 | 反模式 | 说明 |
|---|--------|--------|------|
| 9 | 🔴 **禁止对大型共享目录（`/opt/conda`、`/usr/local`、site-packages）执行 `chown -R`** | ❌ `RUN chown -R ai:ai /opt/conda` 复制整个目录产生数 GB 层 | 目录本身保持 root:root，通过权限治理而非属主变更实现可读 |
| 10 | ✅ **如需运行期写目录，仅对必要小目录 `chown`/`mkdir -p && chown`**（如 `/workspace`、`/home/<user>` 数据卷） | ❌ 对 conda/site-packages 等大目录 chown | 权限最小化到真正需要写的地方 |
| 11 | ✅ **利用 sudo 授权运行期用户的必要特权操作**（如 `sudo pip install`），而非全局 chown | ❌ 依赖 chown 让非 root 用户获得写共享目录权限 | sudo 规则精确到命令，符合最小权限 |

## 阶段4：构建验证（属主分离生效性）

| # | 检查项 | 验证方法 |
|---|--------|---------|
| 12 | ✅ **构建期安装位置验证**：`docker run --rm <image> pip show <pkg>` 或 `python -c "import <pkg>; print(<pkg>.__file__)"`，路径应在共享 site-packages 而非 `/root/.local` | 确认包落在 `/opt/conda/lib/python*/site-packages` 等共享路径 |
| 13 | ✅ **非 root 用户 import 验证**：`docker run --rm -u <nonroot_uid>:<gid> <image> python -c "import <pkg>"` 无 ImportError | 模拟运行期用户真实权限 |
| 14 | ✅ **升级路径验证**：root 执行 `pip install <pkg>` 后再以非 root 用户 import 新版本 | 验证 `PIP_USER=0` 的全局可见性 |
| 15 | ✅ **镜像体积检查**：确认无因 chown 产生的异常大层（对比 `docker history` 各层大小） | 任何 `chown -R` 后的巨层（>500MB）都应排查 |

---

## 质量门（零容忍红线）

| 红线 | 验证方式 | 失败后果 |
|------|---------|---------|
| 🔴 构建期 `PIP_USER=0` | grep Dockerfile 确认构建阶段显式声明 | 运行期非 root 用户 ImportError |
| 🔴 无大型整体 chown | `docker history` 无巨层 / Dockerfile 无 `chown -R /opt/conda` | 镜像体积膨胀数 GB |
| 🔴 非 root 用户可 import 全部核心包 | `-u <uid>` 运行容器 import 验证 | 生产环境权限故障 |

---

## 决策速查：final 阶段 PIP_USER 该设什么？

```
final 镜像是否面向交互式多用户（jupyter/SSH/dev）？
├─ 是 → ENV PIP_USER=1（支持运行期 --user 安装，base/deps 已分离属主）
└─ 否（单场景运行时：根安装需全局可见） → ENV PIP_USER=0
    └─ 判断依据：运行期是否需要 `docker run img pip install x` 对非 root 用户可见
```

---

## 关联模式索引

| 关键问题 | 对应模式文件 |
|---------|-------------|
| 属主分离核心模式 | [docker-buildtime-runtime-ownership-separation.md](../docs/retrospective/patterns/code-patterns/docker-buildtime-runtime-ownership-separation.md) |
| 构建时 vs 运行时配置分离 | [docker-buildtime-vs-runtime-config.md](../docs/retrospective/patterns/code-patterns/docker-buildtime-vs-runtime-config.md) |
| BuildKit 优化三件套 | [docker-buildkit-optimization-best-practices.md](../docs/retrospective/patterns/code-patterns/docker-buildkit-optimization-best-practices.md) |
| 运行时逻辑分层 | [dockerfile-runtime-logical-layering.md](../docs/retrospective/patterns/code-patterns/dockerfile-runtime-logical-layering.md) |
| 复盘原始报告 | [retrospective-chaos-ai-portable-slim-20260811](../docs/retrospective/reports/build-engineering/retrospective-chaos-ai-portable-slim-20260811/README.md) |
