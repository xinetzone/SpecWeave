---
id: "dev-container-image-construction-discipline"

title: "开发容器镜像构建纪律模式"

type: "code-pattern"

date: "2026-10-12"

maturity: "L1-draft"

maturity_note: "单工程实例（openkylin-dev-container，基于本地导入 openKylin 3.0 WSL rootfs 构建，双环境 25 步构建 exit 0 + 冒烟全绿），待其他开发容器/基底镜像复用后升级 L2"

source:
  - "../../../../apps/dev-tools/openkylin-wsl-devkit/doc/05-openkylin-dev-container.md"
  - "../../../../apps/dev-tools/openkylin-wsl-devkit/apps/openkylin-dev-container/README.md"
  - "../../reports/build-engineering/retrospective-openkylin-wsl-to-podman-20261009/README.md#洞察2执行通道选择决定成败"

related_patterns:
  - "wsl-rootfs-oci-image-export.md"
  - "oci-image-wsl-rootfs-bridge.md"
  - "wsl-podman-build-bridge.md"
  - "container-healthcheck-minimal-probe.md"
  - "docker-image-offline-export-distribution.md"

tags: ["container", "containerfile", "dockerfile", "podman", "oci", "base-image", "healthcheck", "rootless", "nested-userns", "base64", "multi-layer", "double-env"]

validation_count: 1

reuse_count: 0
---

# 开发容器镜像构建纪律模式

## 触发场景

适用于需要从本地导入的根文件系统 / WSL 导出产物 / 非 registry 基底构建一个**可运行的开发容器镜像**（内置 SSH、Jupyter、包管理器、rootless 容器等），并希望构建→验证→运行全程可复现、可审计、不因环境差异静默出错的工程。

### 识别信号

* 需要一个基于特定发行版（如 openKylin / 企业级发行版）的容器化开发环境，但官方 registry 的 tag 语义与期望版本不符
* 基底是本地导入的 rootfs / WSL 导出镜像，而非 registry 镜像，构建与运行都靠本地存储
* 需要构建 + 冒烟 + 运行三阶段闭环，且冒烟必须证明镜像真实可跑（而非仅构建成功）
* 想在企业内重复搭建多个开发容器而沉淀一套可复用纪律

### 不适用场景

* 已有官方 registry 基镜像且 tag 语义明确 → 直接用 `FROM <官方镜像>` 即可，无需本地导入基底
* 只需跑一个一次性容器而非"可复现的工程镜像" → 用 `podman run` 现拉现用更轻
* 目标是把镜像转回 WSL 发行版 → 使用 [oci-image-wsl-rootfs-bridge.md](oci-image-wsl-rootfs-bridge.md)（镜像→WSL 正向桥接）
* 只导出归档分发而非重建开发环境 → 使用 [docker-image-offline-export-distribution.md](docker-image-offline-export-distribution.md)

## 问题背景

一个开发镜像工程的价值往往不在 Dockerfile/Containerfile 的语法熟练度，而在三类隐性决策纪律——它们决定了镜像"能不能稳定构建""构建了能不能真跑""跑起来会不会静默出错"。三个工程痛点反复出现：

1. **基底真值不清**：registry tag（如 `latest`）的语义可能随时间/轨（LTS vs 创新版）漂移；"以为用的是 2.0，实际是 3.0，或反之"，若不实测 os-release，镜像基底就是假定的。
2. **镜像格式隐性丢失**：buildah 从某些导入基底继承 OCI 格式，OCI 格式会**静默丢弃** `SHELL` / `HEALTHCHECK` 指令——镜像构建成功但不声明健康检查，验证流程会错位。
3. **验证体系面对环境限制一刀切**：嵌套 rootless 用户命名空间在受限外层宿主上系统性失败，若验证脚本把所有非成功输出都判 fail，就把"平台限制"误报为"镜像坏了"。

本模式把这三类纪律固化为可迁移做法。

## 核心做法（六步法）

### Step 1：基底真值实证裁定

构建前，对基底镜像执行 `cat /etc/os-release`（或其他发行版标识文件）实测，确认其真实版本与期望一致，不轻信 registry tag 语义。

```bash
podman run --rm <base-image> cat /etc/os-release
# 关注 VERSION_ID / VERSION_CODENAME：确认是期望版本而非 tag 名义版本
```

若基底为纯 rootfs 导入、无默认 `ENTRYPOINT`/`CMD`（`podman run --rm <img> <cmd>` 会因无默认命令而失败），改用 `/bin/sh` 显式执行探测：`podman run --rm --entrypoint /bin/sh <base-image> -c "cat /etc/os-release"`。核心是拿到 os-release 的真实版本字段，而非执着于某条具体命令。

若期望版本不在官方 registry 轨（如创新版 openKylin 3.0），采用本地导入的 WSL rootfs 作真版本基底（转换见 [wsl-rootfs-oci-image-export.md](wsl-rootfs-oci-image-export.md)），并在 Containerfile 顶部注释记录"为何用本地基底、registry 实际解析为何版本"。

### Step 2：构建期禁隐式拉取 + 前置门

构建脚本对基底做存在性检查，默认禁止隐式拉取；仅当显式开关（`--pull-base` / `PULL_BASE=1`）才允许真实拉取。前置检查弹夹：`command -v podman`（引擎存在）→ `podman info`（后端可达）→ `podman image exists <base>`（基底就绪），任一项失败立即以明确退出码（如 2）终止。

```bash
command -v podman >/dev/null 2>&1 || { echo "podman not found" >&2; exit 2; }
podman info >/dev/null 2>&1    || { echo "backend unreachable" >&2; exit 2; }
podman image exists "$BASE"    || { echo "base missing; import first" >&2; exit 2; }
```

### Step 3：强制镜像格式并显式声明服务元数据

构建命令显式 `--format docker`，确保 `SHELL` / `HEALTHCHECK` 指令生效（避免 OCI 静默丢弃）。同时用 `HEALTHCHECK` 定义健康探针、`ENTRYPOINT` + `CMD` 提供 init 与默认进程，使镜像"可启动、可上报健康、可被验证"。

```bash
podman build --format docker -t localhost/mydev:1.0 .
```

Containerfile 内须包含：
* `HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 CMD ["/healthcheck.sh"]`
* `ENTRYPOINT ["/usr/bin/tini","--","/entrypoint.sh"]` + 具体 `CMD`（如 supervisord）

### Step 4：分层编排 + 平台陷阱内联注释

单阶段构建按"变更频率从低到高"分层（系统包 → 应用层 → 用户/账户 → 配置 → 元数据），并把平台陷阱写成相邻注释，避免后人重踩：

* **UID 冲突**：WSL 桌面版基底自带桌面默认用户（如 openkylin，uid 1000）；需先 `userdel -r` 再 `useradd -u 1000 devuser`，`2>/dev/null || true` 容忍基底差异。
* **subuid 起点**：`devuser:100000:65536`，起点须**高于用户自身 UID**；含自身 UID 的区间（`1000:...`）被 containers/storage 拒绝（报 `includes the user UID`）。
* **PEP 668**：新发行版启用 externally-managed-environment，系统级 pip 需 `--break-system-packages`（容器作用域内安全）。

### Step 5：三层验证闭环（静态→全量→服务）

验证分三层，逐层加码，任何一层失败都回送可诊断信息：

* **层 1 静态探针**：`--entrypoint /bin/bash` 注入一次性容器，检查 `sshd -t`、jupyter/supervisord 版本、locale、时区、用户 uid、subuid、容器二进制齐备。用 `--entrypoint` 覆盖是为了跳过镜像默认启动（supervisord 等长驻进程）而只取一个只读的 shell 探针，避免容器反复启动/退出。
* **层 2 全量启动**：`podman run -d` 后轮询 `podman inspect -f '{{.State.Health.Status}}'` 等 HEALTHCHECK healthy；超时则 `podman logs` 取尾部诊断。
* **层 3 服务探针**：`podman exec` 检查核心进程 `pgrep`、端口 `ss -ltn`、HTTP 终态 `curl -w %{http_code}`。

全程用 `--pull=never`（仅本地镜像），保证验证不依赖网络、不复现不等于发布环境。

### Step 6：环境限制显式降级而非误报

对"取决于外层宿主能力"的特性（尤其容器内嵌套 rootless 用户命名空间），用三分支探针记录为三态，而非一刀切 fail：

* 能力可用 → 记为正常（可跑）。
* 能力受环境限制（如 `Operation not permitted` / `newuidmap` 内出现 `Invalid argument` 这类随后者宿主而异的 EPERM/EINVAL 错误码）→ 记为 **ENV-LIMIT**（预期降级，镜像就绪已验证，live 能力需更强的宿主）。
* 其他真实失败（如 `podman bin not found`、镜像缺失、命令不存在）→ 记 FAIL。

判据边界：判 ENV-LIMIT 的前提是**报错发生在嵌套 userns 初始化环节，且错误码指向权限/映射受限**；凡属"组件缺失、依赖不全、命令不存在"等镜像自身缺陷，一律判 FAIL，不得借降级掩盖包装缺陷。如此把"镜像就绪"与"镜像可跑高级特性"分离评估，避免把 OS 平台级限制误报为镜像缺陷。

### 洞察：镜像存储可见性与运行身份绑定

rootful 与 rootless podman 的镜像存储是**两个独立的 store**：root 镜像落在 `/var/lib/containers`，普通用户落在各自的 `~/.local/share/containers`。因此 root 构建的镜像，默认用户用 `podman images` 查询会得到空列表——这是存储身份差异而非"镜像未构建"。

* **现象**：`openKylin-3.0-desktop` 发行版内，默认用户 `podman images` 返回空表头；`--user root podman images` 却能列出 `localhost/openkylin:3.0` 与 `localhost/openkylin-dev:3.0`（2026-10-12 实测）。
* **根因**：root 身份构建的镜像只写入 rootful store，与 rootless store（默认用户查询路径）互不可见。
* **影响**：若以错身份枚举镜像，会产出"镜像不存在/未构建"的假性结论，直接误导后续 `podman load` / 导出分发 / 验证步骤；跨 WSL 环境打包导出时尤易踩中。
* **行动**：凡镜像生命周期操作（构建/导出 `save` / 导入 `load` / 枚举 `images`）一律在 rootful store 内以显式 `--user root`（或 `sudo`）身份执行；默认用户查询仅用于确认 non-root store 状态。

## 反模式（不要这么做）

* ❌ **轻信 registry tag 语义**：直接用 `FROM openkylin/openkylin:latest` 假设是目标版本，而不实测 os-release——`latest` 可能解析为 LTS 轨而非期望的创新版，基底版本与预期错位。
* ❌ **忽略格式隐性丢失**：不显式 `--format docker`，镜像构建成功但 `HEALTHCHECK`/`SHELL` 被 OCI 格式静默丢弃，验证体系因"无健康检查"而错位。
* ❌ **subuid 起点含自身 UID**：用 `devuser:1000:65536`，构建被 containers/storage 以 `includes the user UID` 拒绝，反复排查仍找不到原因。
* ❌ **不处理基底自带同名用户**：`useradd -u 1000` 遇 WSL 桌面基底的 `openkylin`（uid 1000）报 `UID 1000 并不唯一`，未先 `userdel`。
* ❌ **探针不兼容目标环境拼写**：探针用严格 `zh_CN.UTF-8` 精确匹配，实测基底为 `zh_CN.utf8`；正确做法是大小写/连字符兼容匹配。
* ❌ **多跳 shell 直接透传多行脚本**：把含引号与 `$` 的多行脚本经 wsl.exe argv 透传，被二次 shell 展开破坏，产生假性失败（如 `id: "devuser": 无此用户`）；应 base64 单 token 解码执行。
* ❌ **验证一刀切判 fail**：对嵌套 rootless 等平台限制输出也判 fail，把 ENV-LIMIT 误报为镜像缺陷，掩盖"镜像就绪已验证"的真实结论。
* ❌ **用错身份枚举/导出镜像**：默认用户执行 `podman images` / `podman save`，因只读 rootless store 而看不到 root 构建的镜像，把"存储身份差异"误判为"镜像未构建"，导出到空 tar 或误走重新构建流程。正确做法：root 或 `sudo podman` 操作。

## 检验标准

1. **基底版本实证**：构建产物 `cat /etc/os-release` 的 VERSION_ID / CODENAME 与期望一致，且已在 Containerfile 注释记录裁定依据。
2. **构建无隐式拉取**：构建日志无任何 registry 拉取（除非显式 `--pull-base`），仅依赖本地已就绪基底。
3. **健康检查生效**：`podman inspect` 能读取到 Health 字段，镜像具备 `HEALTHCHECK` 声明而非被 OCI 丢弃。
4. **三层验证全过**：静态探针 / 全量启动 healthy / 服务探针（进程 + 端口 + HTTP）三层均通过。
5. **环境限制闭环**：受宿主限制的高级特性被显式记录为 ENV-LIMIT（预期降级），未误报为 FAIL；未以违规参数（如 `--privileged`）绕过。
6. **安全边界明确**：无硬编码密码/密钥，敏感服务（如无 token Jupyter / 密码 SSH）仅限本地，运行契约参数（`--device /dev/fuse` 等 + 严禁 `--privileged`）被文档化。
7. **镜像身份可见性核验**：以 root 身份执行 `podman images` 能列出目标镜像；`podman save` 产出的 tar 非空且 `manifest` config 摘要与源镜像 ID 一致，导出/验证未因身份错位而失真。

## 迁移示例

* **场景 1（跨领域）**：企业级服务器基础镜像（RHEL/CentOS 系，来自本地导入的安装介质 ISO→rootfs）构建开发容器 —— 基底真值实证、格式显式强制、三层验证、契约参数文档化均适用，仅包管理器从 APT 换 dnf。
* **场景 2（跨领域）**：GPU 开发容器（CUDA 基底 + 框架）—— 基底来源实证与格式强制同样关键，验证层需追加 GPU 设备探针。
* **场景 3（领域内变体）**：其余发行版基于 WSL rootfs 的开发容器 —— 步骤一致；Alpine 无 `/etc/os-release` 以外的发行版专属文件，探针命令以 os-release 为准。
* **场景 4（领域内变体）**：仅做镜像离线分发（不打开发栈）—— 本模式聚焦"构建纪律"，分发环节可叠加 [docker-image-offline-export-distribution.md](docker-image-offline-export-distribution.md)。

## 与既有模式的关系

* [wsl-rootfs-oci-image-export.md](wsl-rootfs-oci-image-export.md)：本模式的前置步骤（把 WSL rootfs 转为 OCI 基底镜像），二者衔接构成"rootfs→开发容器"完整链路。
* [oci-image-wsl-rootfs-bridge.md](oci-image-wsl-rootfs-bridge.md)：方向相反（镜像→WSL），本模式与它互补不重复。
* [wsl-podman-build-bridge.md](wsl-podman-build-bridge.md)：其构建桥接细节与本模式相互印证。
* [container-healthcheck-minimal-probe.md](container-healthcheck-minimal-probe.md)：健康探针的编写细节；本模式的 Step 5 依赖其探针约定。
* [docker-image-offline-export-distribution.md](docker-image-offline-export-distribution.md)：离线导出分发；本模式聚焦构建纪律，最终发布可叠加。

## 已知限制与待验证

1. **单工程（L1-draft）**：仅在 `openkylin-dev-container`（openKylin 3.0 基底）上真实验证，双环境（Windows Podman Machine + openKylin WSL）25 步构建 exit 0 + 冒烟全绿；待其他发行版/基底复用后升级 L2。
2. **嵌套 rootless 为平台级限制**：容器内 live rootless（嵌套 userns）在受限外层宿主上系统性失败属内核级约束，本模式仅提供"降级记录"而非"使其可用"的解法。
3. **仅 amd64 真实验证**：`--platform` 透传保留但不承诺多架构验收。
4. **未做镜像尺寸优化**：本模式聚焦构建纪律与可复现性；如需极致瘦身，可另行结合镜像裁剪/分层优化模式。
5. **引擎与版本适用边界**：`--format docker` 强制为 podman/buildah 特定行为，且"OCI 静默丢 SHELL/HEALTHCHECK"基于当前实测；docker build 或未来 podman 版本可能改变该行为。复用时应以"验证 HEALTHCHECK 字段是否生效"而非盲目沿用 `--format` 参数。