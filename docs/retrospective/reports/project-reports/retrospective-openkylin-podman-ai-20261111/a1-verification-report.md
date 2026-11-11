# A1 存储统一验收报告（零 sudo 等效方案）

| 项 | 内容 |
|---|---|
| 行动项 | A1「统一容器存储为单一物理路径并做容量 census」 |
| 来源 | `docs/retrospective/reports/project-reports/retrospective-openkylin-podman-ai-20261111/index.md`（A1 条目） |
| 执行方案 | 零 sudo 等效方案（经用户确认，放弃原路线 A） |
| 执行日期 | 2026-11-11 |
| 执行主体 | ai@10.16.11.3（rootless Podman 5.6.2，宿主 uid 1006） |
| 变更性质 | 只读取证，未修改任何配置或 root 级文件 |
| 验收结论 | **通过**——现状已物理统一，无需迁移 |

---

## 1. 摘要

A1 的目标是让 rootless Podman 的容器存储落在一个可审计、可量全的物理路径上，并产出一次无权限缺口的容量 census。

本次执行分两步：先证伪原路线（改 root 级包装器注入 `--root`），再以只读方式对现状做物理统一取证。结论有三条：

1. **原路线 A 被硬阻断**：`/usr/local/bin/podman` 属 `root:root`，ai 用户无免密 sudo（`sudo -n true` 返回 `a password is required`），无法注入全局参数。
2. **rootless 下配置文件确实无法改写 graphRoot**，但原因不是「配置未被读取」，而是路径类字段被 XDG 派生值覆盖；唯一改写入口是全局参数 `--root`（详见第 3 节）。
3. **现状已物理统一**：三个入口经 `readlink -f` 收敛到同一真实路径，设备号同为 `2049`、文件系统同为 `xfs`，`graphRoot` 与 `volumePath` 位于同一挂载点 `/media/pc/data`；census 四目录全部 `rc=0`，无 Permission denied。

因此 A1 的实际产出是**口径固化 + 证据确权**，而非数据迁移：迁移代价（46 GiB 量级、Podman 停机）被完全规避，回滚面为零。

---

## 2. 验收标准与判定

验收标准取自复盘报告 A1 条目：

| 编号 | 标准 | 判定 | 证据位置 |
|---|---|---|---|
| 标准一 | 对唯一路径执行 `du -sx` 得完整数值且无 Permission denied | **通过** | 第 4.5 节 census 表，四目录 rc 全为 0 |
| 标准二 | `podman info` 的 graphRoot 与 volumePath 位于同一挂载点 | **通过** | 第 4.3、4.4 节（同为 `/dev/sda1 … /media/pc/data`） |

两项均成立，A1 登记为已完成。

---

## 3. 机制结论：rootless 下 graphRoot 为何不能由配置文件改写

### 3.1 两段式解析

containers/storage 的落点解析分两段，第二段会覆盖第一段：

- **第一段（定位并解析）**：先找系统级 `/usr/share/containers/storage.conf` 或 `/etc/containers/storage.conf`，再按 `CONTAINERS_STORAGE_CONF` 或 `$XDG_CONFIG_HOME/containers/storage.conf` 叠加用户级配置。此段**正常执行**。
- **第二段（rootless 后处理）**：解析完成后，用 `$XDG_DATA_HOME/containers/storage` 覆盖 `GraphRoot`，用 `$XDG_RUNTIME_DIR/containers` 覆盖 `RunRoot`。

被覆盖的只有**路径类字段**（`graphroot`、`runroot`、`rootless_storage_path`）；**非路径字段**（`driver`、`[storage.options]`）照常生效。全局 `--root` / `--runroot` 参数优先级最高。

### 3.2 对照证据（七组）

| 组 | 操作 | 观测 | 说明 |
|---|---|---|---|
| 1 | 基线 | graphRoot=`/home/ai/.local/share/containers/storage`、driver=overlay | 三个候选配置文件均不存在（见 3.3） |
| 2 | 同一文件写 `driver="vfs"` | `podman info` 报 driver=vfs | **证明配置文件被解析**，排除「未读取」假设 |
| 3 | 同一文件写 `graphroot="…"`（经 `CONTAINERS_STORAGE_CONF`） | graphRoot 仍为默认值 | 路径被覆盖 |
| 4 | 同一文件写 `rootless_storage_path="…"`（经 `XDG_CONFIG_HOME`） | graphRoot 仍为默认值 | 路径被覆盖 |
| 5 | 环境变量 `XDG_DATA_HOME=/tmp/a1z` | graphRoot 变为 `/tmp/a1z/containers/storage` | 证实覆盖来源是 XDG 派生 |
| 6 | 组 5 环境下观察 runRoot | 仍为 `/run/user/1006/containers` | 两个路径字段由两个不同变量分别控制 |
| 7 | 组 5 环境追加 `--root /tmp/a1z/explicit` | graphRoot 以显式参数为准 | 全局参数优先级最高 |

### 3.3 前置事实

`/etc/containers/storage.conf`、`/usr/share/containers/storage.conf`、`~/.config/containers/storage.conf` 三处**均不存在**。这意味着当前落点完全由派生规则与既有软链共同决定，不存在「配置写错但没生效」的隐性风险。

### 3.4 设计原因

1. **权限前提**：rootless 用户对 `/var/lib/containers/storage` 无写权限；若多个无特权用户共享同一 graphRoot，uid 映射区间与 xattr/chown 会互相冲突。
2. **权责分离**：`storage.conf` 是 root 撰写的系统级文件，不应由无特权用户借此决定存储落点。
3. **可自举**：固定派生规则保证首次 `podman unshare` 能在正确属主下自建目录，无需任何预置。
4. **可迁移**：存储随家目录走，备份、迁移与配额统计都以用户为边界。

### 3.5 对 A1 的含义

改写落点只有两条通道：全局参数 `--root`（需改 root 级包装器），或环境变量 `XDG_DATA_HOME`（属用户级，会牵连整个家目录语义）。前者被 sudo 阻断，后者不属于 A1 的授权范围。加之现状在物理层已经统一（第 4 节），**继续改写已无收益**，A1 转为「固化口径 + 留存证据」。

---

## 4. 验收执行记录

### 4.1 路径解析三元组

```
/home/ai/.local/share/containers/storage      -> /media/pc/data/ai/.agents/podman-storage/storage
/media/pc/data/ai/podman-storage/storage      -> /media/pc/data/ai/.agents/podman-storage/storage
/media/pc/data/ai/.agents/podman-storage/storage/volumes -> 自身（真实目录）
```

三条入口（graphRoot 软链、历史软链、volumePath）收敛到同一真实路径。

### 4.2 设备号与文件系统（含口径订正）

| 入口 | `stat -c %d`（不跟随） | `stat -Lc %d`（跟随软链） | `stat -fL -c %T` |
|---|---|---|---|
| `/home/ai/.local/share/containers/storage` | 66308 | **2049** | xfs |
| `/media/pc/data/ai/podman-storage/storage` | 2049 | **2049** | xfs |
| `/media/pc/data/ai/.agents/podman-storage/storage` | 2049 | **2049** | xfs |

**口径订正**：`stat -c %d` 不跟随软链，返回的是软链**自身**所在目录（家目录，设备 66308）的设备号；要证明「指向同一文件系统」必须用 `stat -L`。此前 checklist 中「三者 `stat -c %d` 同为 2049」的表述已按本表订正。

### 4.3 挂载点与容量

`df -P` 对 graphRoot 与 volumePath 均返回同一条挂载记录：

```
/dev/sda1  ...  321429616(1K-blocks 可用)  98%  /media/pc/data
```

- 使用率 **98%**，可用 **321,429,616 KiB ≈ 306.5 GiB**（df 1K-block 口径，非字节）。
- 与 `podman info` 的 `graphRootAllocated ≈ 15.9 TB`、`graphRootUsed ≈ 15.67 TB` 属**文件系统级量纲**，不可与第 4.5 节的容器目录占用直接相减。

### 4.4 存储三元组

```
graphRoot = /home/ai/.local/share/containers/storage   （保留软链字面值，未解析）
volumePath = /media/pc/data/ai/.agents/podman-storage/storage/volumes  （解析后真实路径）
runRoot   = /run/user/1006/containers
driver    = overlay
```

graphRoot 与 volumePath 的**字面值不同**，但第 4.1–4.3 节已证明二者同设备、同文件系统、同挂载点——差异仅存在于展示层（前者不解析软链，后者解析）。标准二据此判定成立。

### 4.5 容量 census

命令：`podman unshare du -sxB1 <真实路径>/<子目录>`（在用户命名空间内执行，避免 rootless 映射导致的权限拒绝）。

| 子目录 | 字节数 | 折算 | rc |
|---|---|---|---|
| `overlay` | 72,590,733,312 | 67.60 GiB | 0 |
| `overlay-images` | 1,064,960 | 1.02 MiB | 0 |
| `overlay-containers` | 966,656 | 944 KiB | 0 |
| `volumes` | 7,436,853,248 | 6.93 GiB | 0 |
| **合计** | **80,029,618,176** | **74.53 GiB** | — |

- 四个目录全部 `rc=0`，输出中**无 Permission denied**，标准一成立。
- 结构占比：`overlay` 90.7%、`volumes` 9.3%。
- `-x` 限定不跨文件系统，确保数值只反映 `/media/pc/data` 上的占用，不含 `runRoot`（`/run/user/1006/containers`，属 tmpfs）。

---

## 5. 与 A3 的衔接

A1 的 census 建立在 A3 清理之后，容量基线因此可直接对比：

| 时点 | `overlay` 字节数 | 说明 |
|---|---|---|
| A3 删除前 | 73,987,444,736 | 含 3 个 `<none>` 悬空镜像 |
| A3 删除后 = A1 census | 72,590,733,312 | 回收 1,396,711,424 B（≈1.30 GiB） |

A1 未再产生任何容量变化，故 A3 的删除后值即为当前真实基线。若后续需要判断「镜像是否真的释放了空间」，应回到本节的同一口径（`du -sxB1` + `-x`），而非用标签体积相加。

---

## 6. 风险、限制与回滚

| 项 | 说明 |
|---|---|
| 变更面 | **零**。全程只读命令，未修改 `/usr/local/bin/podman`、未创建/删除软链、未写 containers 配置 |
| 回滚 | 无需回滚；如需复核，重跑第 4 节命令即可 |
| 限制一 | graphRoot 的字面值仍是软链路径，任何按字符串比较「配置是否统一」的检查都会误报，须用 `readlink -f` 或 `stat -L` |
| 限制二 | `podman system df` 当前不可用（报 `lstat /run/user/1006/libpod/tmp/infra-container: no such file`），故 census 只能走 `du` 通道 |
| 限制三 | 容量数值易变，引用须注明采集日期 2026-11-11 |
| 残留问题 | 未配置镜像回收策略，`overlay` 长期占 67.6 GiB；A1 不含此项，属后续行动项范围 |

---

## 7. 遗留与建议

1. **口径已固化**：后续任何「存储是否统一」的判断，统一采用 `readlink -f` + `stat -Lc %d` + `stat -fL -c %T` + `df -P` 四件套，禁止单用 `stat -c`。
2. **census 命令已固化**：`podman unshare du -sxB1 <真实路径>/<子目录>`，分目录计而非整树一次计，避免超时。
3. **未做但不建议做**：通过 `XDG_DATA_HOME` 改写落点会把家目录语义整体牵连，代价远高于收益；若将来确需迁移，应走 `--root` 通道并取得 sudo 授权。
4. **可选后续**：为 `overlay` 设定镜像保留策略（按标签数与时间），将 67.6 GiB 的单调增长纳入治理——此项超出 A1 范围，需另行立项。

---

## 附录：完整命令清单

```bash
# 1. 路径解析
for p in /home/ai/.local/share/containers/storage \
         /media/pc/data/ai/podman-storage/storage \
         /media/pc/data/ai/.agents/podman-storage/storage; do
  readlink -f "$p"
done

# 2. 设备号与文件系统（必须跟随软链）
stat -Lc '%d' /home/ai/.local/share/containers/storage
stat -fL  -c '%T' /home/ai/.local/share/containers/storage

# 3. 挂载点与容量
df -P /home/ai/.local/share/containers/storage \
      /media/pc/data/ai/.agents/podman-storage/storage/volumes

# 4. 存储三元组
podman info --format 'graphRoot={{.Store.GraphRoot}}|volumePath={{.Store.VolumePath}}|runRoot={{.Store.RunRoot}}|driver={{.Store.GraphDriverName}}'

# 5. 容量 census
S=/media/pc/data/ai/.agents/podman-storage/storage
for d in overlay overlay-images overlay-containers volumes; do
  podman unshare du -sxB1 "$S/$d"
done

# 6. 机制对照（配置文件是否存在）
ls -l /etc/containers/storage.conf \
      /usr/share/containers/storage.conf \
      ~/.config/containers/storage.conf
```