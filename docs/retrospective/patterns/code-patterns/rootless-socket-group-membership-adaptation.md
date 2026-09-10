---
id: "rootless-socket-group-membership-adaptation"
title: "跨边界 socket 属组自适应授权模式"
type: code-pattern
date: 2026-09-10
maturity: L1
maturity_note: "单案例（C-I2 容器内 Podman socket EACCES），待第二案例验证"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/rootless-socket-group-membership-adaptation.toml"
source: "../../reports/incident-reports/retrospective-c-i2-eacces-20260910/retrospective-report.md"
related_patterns:
  - "host-channel-pass-through"
  - "fixuid-runtime-uid-mapping"
  - "docker-ssh-noninteractive-path-fix"
  - "multi-entrypoint-config-unification"
tags: ["podman", "container", "userns", "rootless", "socket", "permission", "eacces", "group", "usermod", "supervisord", "authorization"]
validation_count: 1
reuse_count: 0
---

# 跨边界 socket 属组自适应授权模式

> **一句话**：跨 userns/跨用户边界把宿主 socket（或设备节点）透传给非 root 调用方时，「路径可达」不等于「权限可访问」——必须在**调用方视角**解析目标属组，并在守护进程 `exec` **之前**把调用方加入该属组，最后以**生产上下文**复测。

## 触发场景

- 容器/沙箱内非 root 用户需要访问**宿主侧受保护的 socket 或设备节点**（如 `/run/user/<uid>/podman/podman.sock`、`/var/run/docker.sock`、`/dev/*`）
- 目标对象仅对**属组**开放（典型 `srw-rw---- 1 root root`，即 `0660`），调用方既非属主也不在其许可属组内
- 宿主与调用方之间存在 **UID/GID 映射边界**（rootless userns、多用户映射、user namespace 嵌套），宿主侧看到的属主/属组在调用方视角下被**压扁**为另一个身份
- 授权动作需要在**守护进程启动之前**完成（补充组继承只在进程 spawn 时刻生效）

## 不适用场景（边界与反目标）

1. **调用方本就在目标属组内**：无需本模式，只需常规路径暴露（见 [host-channel-pass-through.md](host-channel-pass-through.md)）
2. **目标是网络端点而非 Unix socket / 设备节点**：TCP 端口授权靠网络策略与认证，不涉及 POSIX 属组
3. **需要的是「隔离」而非「授权」**：若安全目标是不让容器访问宿主 daemon（跨租户越权场景），正确做法是拒绝透传或引入 socket 代理，而不是本模式（本模式只解决授权可达问题，不提供隔离）
4. **无法获得 root 且无法修改镜像构建链**：本模式依赖入口脚本在特权阶段执行 `usermod` 或等价的成员关系写入，纯运行时无特权进程无法自授权
5. **目标对象在调用方视角为只增不少的一次性消费**：若调用方对目标仅有极少量、可预授权的访问，直接以属主身份代理转发更简单

## 失败案例

### 案例：容器内非 root 用户访问宿主 rootless Podman socket 报 EACCES（C-I2）

**场景**：WSL 宿主 rootless podman socket 经 B-scheme bind-mount 进容器同一路径，容器内 `devuser`（UID 1001）通过 SDK / CLI 调用 podman。

**现象**：
```
PermissionError: [Errno 13] Permission denied
  File ".../podman/api/uds.py", line 41, in UDSSocket.connect
    super().connect(netloc)

Error: unable to connect to Podman socket: ... dial unix /run/user/1001/podman/podman.sock:
       connect: permission denied: unix:///run/user/1001/podman/podman.sock
```

**根因**：

1. 宿主 socket 权限为 `srw-rw---- 1 root root`（`0660`），仅属组可读写
2. 宿主 socket 经 rootless userns 映射进入容器后，数值属主/属组被**压扁**为容器内 `root:root`（gid 0）
3. 通道实现只做了「路径暴露」（符号链接 + `CONTAINER_HOST` 导出），**从未做属组衔接**——`devuser` 不在 `root` 组内
4. 生成环境的修正验证又一度被误判为"没修好"：复测命令 `su - devuser` 是登录 shell，剥离了 `CONTAINER_HOST`/`XDG_RUNTIME_DIR`，podman 退化为本地模式并抛 `newuidmap ... Operation not permitted`，被误当成属组修复失败

**教训**：
- 排除 `ENOENT`（socket 不存在）**不代表**通道可用；`EACCES` 是**独立故障类别**，需要独立诊断编号与独立修复动作
- 判断可访问性必须以**调用方视角的映射结果**为准，不能用宿主侧 `ls -l` 结果推理
- 唯一正确解是「在容器内把调用方加入目标属组」，而非「在宿主侧改 socket 属主/权限」

## 核心做法

### 1. 在调用方视角解析目标的属组（而非凭宿主观察推理）

```bash
# 属组名 + 数值 gid 双取
sock_gid="$(stat -Lc '%g' "${target}" 2>/dev/null || true)"
sock_group="$(stat -Lc '%G' "${target}" 2>/dev/null || true)"

# %G 在某些映射/不解组环境下返回空或 UNKNOWN，必须回退数值 gid
if [ -z "${sock_group}" ] || [ "${sock_group}" = "UNKNOWN" ]; then
    sock_group="${sock_gid}"
fi

# stat 失败不得静默 —— 必须显式告警，否则会把"属组未知"伪装成"无需授权"
if [ -z "${sock_group}" ]; then
    log_warn "Cannot resolve target group (stat failed on ${target}); ${NON_ROOT_USER} may hit EACCES"
fi
```

> 关键：这里 `root` / `0` 是**调用方视角的属组标识**，与宿主侧同名属组未必是同一实体；不要试图在宿主侧「修正」。

### 2. 幂等加入属组（已属则跳过）

```bash
if id -nG "${NON_ROOT_USER}" 2>/dev/null | tr ' ' '\n' | grep -qx "${sock_group}"; then
    log_info "${NON_ROOT_USER} already in target group '${sock_group}' (gid ${sock_gid})"
elif usermod -aG "${sock_group}" "${NON_ROOT_USER}" 2>/dev/null; then
    log_info "Added ${NON_ROOT_USER} to target group '${sock_group}' (gid ${sock_gid})"
else
    log_warn "Failed to add ${NON_ROOT_USER} to target group '${sock_group}' (gid ${sock_gid})"
fi
```

- **只用 `-aG`（append）**，绝不用 `-G`（会覆盖既有属组，破坏其他权限）
- 只加属组、**不改目标对象的模式位与属主**（`chmod 666` / `chown` 属于反模式）

### 3. 时序：授权必须早于守护进程 `exec`

补充组在进程 **spawn 时刻**由「当时 `/etc/group` 的成员关系」派生（supervisord `drop_privileges` 走 `grp.getgrall()` → `os.setgroups()` → `setgid` → `setuid`）：

```
入口脚本（特权阶段）
├─ 解析目标属组
├─ usermod -aG <group> <user>      ← 必须在此处
└─ exec supervisord                ← 之后 spawn 的子进程才继承新属组
    └─ spawn sshd / jupyter ...    ← 继承到的补充组在此刻固化
```

晚于 `exec` 的 `usermod` 会**静默失效**：命令返回 0（"加组成功"），但已 spawn 的进程不继承。

### 4. 反查实际继承（不要相信命令返回码）

```bash
# 用进程的补充组列表证明"确实生效"，而不是命令退出码
grep '^Groups:' /proc/$(pgrep -f 'jupyter' | head -n1)/status
# Groups: 0 27 997 1001   ← gid 0（目标属组）已注入
```

### 5. 自验证 + 以生产上下文复测

```bash
# 自验证：以调用方身份实测目标可读写（仅告警不阻断 —— 映射不匹配时仍可能失败）
if su - "${NON_ROOT_USER}" -c "test -r '${target}' && test -w '${target}'"; then
    log_info "[OK] ${NON_ROOT_USER} can read/write ${target}"
else
    log_warn "${NON_ROOT_USER} still cannot access ${target} (EACCES risk)"
fi
```

复测**功能路径**（而非仅文件位）时，必须复刻生产执行上下文：守护进程树继承入口脚本导出的环境变量，因此复测也要显式带上同一组变量：

```bash
# ❌ 反例：su - 是登录 shell，会剥离环境变量
su - devuser -c 'podman images'

# ✅ 正例：显式沿用入口脚本导出的契约变量
su - devuser -c '
  export CONTAINER_HOST="unix:///run/user/1001/podman/podman.sock"
  export XDG_RUNTIME_DIR="/run/user/1001"
  podman images
'
```

## 反模式（不要这么做）

### ❌ 反模式1：只验证目标「存在」就判定通道可用

```bash
[ -S "${sock}" ] && echo "channel OK"   # 只排除了 ENOENT
```
目标存在与可访问是两个独立维度。`EACCES` 不会被这类检查捕获，故障会推迟到业务调用时才暴露。必须补「属组授权 + 可读写实测」两个动作，并把 `EACCES` 与 `ENOENT` 拆成**独立诊断编号**（否则会把属组问题误诊为路径问题）。

### ❌ 反模式2：在宿主侧改 socket 属主/权限

```bash
# 在宿主执行
sudo chown devuser /run/user/1000/podman/podman.sock
sudo chmod 666 /run/user/1000/podman/podman.sock
```
跨 userns 映射下这些改动**语义不对应**：宿主侧 UUID 无法表达容器内调用方身份。而 `chmod 666` 更是把宿主 daemon 暴露给所有本地用户，是安全红线。正确解是**在调用方侧加入属组**。

### ❌ 反模式3：硬编码边界另一侧的 UID/GID

```bash
export XDG_RUNTIME_DIR=/run/user/1000   # 硬编码宿主/容器 UID
```
UID 由镜像 `useradd` 或平台动态分配（1000 被占用时会得到 1001），一旦漂移即失效。应使用 `$(id -u <user>)` 动态推导，配置文件用 `%(ENV_X)s` 继承入口脚本的运行时导出值。

### ❌ 反模式4：在守护进程 `exec` 之后才授权

```bash
exec supervisord &
usermod -aG root devuser   # 太晚了：已 spawn 的进程不会继承新属组
```
`usermod` 返回 0 只说明"成员关系已写入磁盘"，**不说明"运行中的进程已生效"**——这是典型的「成功但无效」陷阱。必须把授权放在 `exec` 之前的特权阶段，并用 `/proc/<pid>/status` 的 `Groups:` 反查验证。

### ❌ 反模式5：用登录 shell（`su -` / `bash -l`）复测依赖环境的功能

```bash
su - devuser -c 'podman images'
```
登录 shell 的设计目标是提供**干净环境**，因此会剥离入口脚本导出的契约变量；功能退化后抛出的错误（如 `newuidmap ... Operation not permitted`）会被误读为授权修复失败。复测必须与生产上下文一致（显式带上同一组环境变量），否则诊断结论不可信。

### ❌ 反模式6：用提权或放开权限位"解决"授权

```bash
podman run --privileged ...          # 或 chmod 666 socket
```
`--privileged` 抹平了边界，等于放弃隔离；放开 socket 模式位则把宿主 daemon 暴露给任意本地用户。本模式的授权粒度应始终是**「把调用方加入目标属组」**，不引入更宽权限。

## 检验标准

做完之后怎么知道做对了？

1. **启动日志自证**：入口脚本出现「已加入目标属组」与「可读写实测通过」两条结构化日志
   ```
   [B-scheme] Added devuser to socket group 'root' (gid 0)
   [B-scheme] [OK] devuser can read/write host podman socket
   ```
2. **进程级反查**：守护进程 `/proc/<pid>/status` 的 `Groups:` 含目标 gid
3. **业务路径复测**：以调用方身份、在**生产上下文环境变量**下调用真实功能成功（SDK `PodmanClient.from_env()` 无 `PermissionError`；CLI `podman images` 正常返回）
4. **无越界改动**：`git diff` 中不包含目标对象模式位/属主变更，不引入 `--privileged`；配置无硬编码 UID 字面量
5. **可回滚**：授权逻辑位于单一函数/分支内，删除该分支后系统退回"路径可达但无权限"的先前状态，不产生额外副作用

## 迁移示例

| 场景 | 目标对象 | 调用方 | 授权适配点 |
|------|---------|--------|-----------|
| Podman rootless + WSL | `/run/user/1000/podman/podman.sock` (0660, root:root) | 容器 devuser(1001) | 容器内 `usermod -aG root devuser`（`exec` 前） |
| Docker daemon 透传 | `/var/run/docker.sock` | 容器内非 root 用户 | 以 socket 属组为准 `usermod -aG`；或改用 socket 代理 |
| 宿主 GPU 设备透传 | `/dev/nvidia*` | 容器内非 root 用户 | 按设备节点属组授权，替代宽泛的 `--privileged` |
| 串口 / USB 设备透传 | `/dev/ttyUSB*` / `/dev/bus/usb/*` | 容器内采集进程 | 加入 `dialout`/`plugdev` 等设备属组 |
| 落盘目录共享 | bind-mount 目录 | 容器内非 root 用户 | 属组授权（对照 [fixuid-runtime-uid-mapping.md](fixuid-runtime-uid-mapping.md) 处理 UID 映射维度） |

### 跨领域迁移（去场景化抽象）

本模式的抽象内核是：**「跨信任/命名空间边界授权一个受保护资源，必须把授权动作施加在调用方侧、且在消费者进程形成之前完成」**。同构迁移：

- **数据库/中间件连接授权**：应用启动前完成凭证/角色授予，运行中再改授权对已建立的连接池无效（时序同构）
- **systemd 服务 + 属组资源**：`SupplementaryGroups=` 必须在服务启动前声明，运行中 `usermod` 不回溯
- **Kubernetes Pod 访问宿主资源**：`securityContext.fsGroup` 需在 Pod 创建时声明，运行中不可追加
- **CI Runner 访问宿主 Docker**：runner 进程加入 `docker` 组必须在 runner 服务启动前完成

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [host-channel-pass-through.md](host-channel-pass-through.md) | **互补（前置）** | 前者解决「通道如何建立」（路径暴露、符号链接、`CONTAINER_HOST` 契约），本模式解决「通道如何被授权」（属组衔接）。前者只覆盖可达性，本模式补齐可访问性维度，二者合起来才是完整通道 |
| [fixuid-runtime-uid-mapping.md](fixuid-runtime-uid-mapping.md) | 同域 | 同属「权限/UID 治理」问题域；该模式治理 bind mount 的 UID 映射维度，本模式治理 socket/设备的属组授权维度 |
| [docker-ssh-noninteractive-path-fix.md](docker-ssh-noninteractive-path-fix.md) | 结构同构 | 同为「多入口继承差异」类问题：该模式用四层配置覆盖 SSH/docker exec/supervisord 四入口的 PATH 继承差异；本模式解决补充组在 `exec` 时点固化导致的入口差异 |
| [multi-entrypoint-config-unification.md](multi-entrypoint-config-unification.md) | 互补 | 配置项去硬编码（`%(ENV_X)s` 继承）是授权可移植的前置条件，本模式复用其「环境变量命名权威」结论 |

## 待验证场景

本模式目前为 **L1**（单一案例：jpman client 容器内 Podman socket EACCES，2026-09-10），建议在以下场景验证：

1. **非 WSL 的 rootless podman 容器套容器**：验证无三层 userns 嵌套时属组是否仍被压扁（判断"压扁"是否为 WSL 特有）
2. **Docker socket 透传**（`/var/run/docker.sock` 属组 `docker`）：验证属组名与 gid 不一致（如宿主 gid 999、容器内无同名组）时 `%G` 回退 `%g` 分支的实际表现
3. **设备节点透传**：`/dev/nvidia*` 在 rootless 容器内的属组授权，验证本模式是否能替代 `--privileged`
4. **第二案例**：任一「跨边界 socket/设备 + 属组授权」的独立场景复现，用于将成熟度从 L1 提升至 L2
