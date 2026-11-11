---
type: action-plan
title: 反模式 P1–P5 整改方案
date: 2026-11-11
status: proposed
source: retrospective-openkylin-podman-ai-20261111/index.md
---

# 反模式 P1–P5 整改方案

本文件是[主报告](index.md) E 段反模式清单的整改附件，只回答一件事：每条反模式**怎么修、怎么防、怎么判、谁负责、怎么退**。五条方案与主报告 C 段行动 A1–A6 一一映射，不新增行动编号。

事实基线沿用主报告 R 段（采集日期 2026-11-11），容量与镜像清单类数值引用时须重新测量。

## 0. 通用约定

| 项 | 约定 |
|---|---|
| 命令执行位置 | 标 `[服务器]` 的命令经 `ssh ai@10.16.11.3` 执行；标 `[Windows]` 的在本地 PowerShell 7.4+ 执行；标 `[WSL]` 的在 `wsl -d openkylin-test` 内执行 |
| 路径口径 | 一律先 `readlink -f` 取真实路径，再对真实路径取数；禁止对软链路径直接 `du`/`df` |
| 权限口径 | rootless 下宿主 `du` 读不到子 uid 目录，统一用 `podman unshare` 取数 |
| 验收口径 | 每条只给一条可复制命令，输出 `PASS` 或 `FAIL`；`FAIL` 不得继续下一步 |
| 变更审批 | 改 `storage.conf`、`wsl --unregister`、删除镜像三类操作须人类批准后执行 |

## 1. P1 在网络盘/SMB 放容器存储或 VHDX

### 1.1 识别信号

出现任一即判定命中：

- `[服务器]` 存储底层文件系统属 `cifs`/`smb3`/`nfs`/`nfs4`/`9p`/`fuse.*`；
- `[服务器]` `graphStatus` 中 `Native Overlay Diff` 或 `Supports d_type` 不为 `true`（F1 判据）；
- `[Windows]` vhdx 所在卷的 `DriveType != 3`（4 为网络盘，F3 判据）。

```bash
# [服务器] 一行取三值：真实 graphRoot、底层 fstype、关键 graphStatus
REAL="$(readlink -f "$(podman info --format '{{.Store.GraphRoot}}')")"
echo "$REAL"; findmnt -no FSTYPE --target "$REAL"
podman info --format json | jq -r '.store.graphStatus | to_entries | map("\(.key)=\(.value)") | .[]'
```

```powershell
# [Windows] vhdx 落位与卷类型
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,DriveType,FileSystem
# DriveType: 3=本地固定盘（允许）；4=网络盘（`wsl --import` 直接拒绝）
```

### 1.2 立即修复

```bash
# [服务器] 第一步：留证并备份配置（不备份不动手）
podman info --format '{{.Store.GraphRoot}} {{.Store.VolumePath}}' | tee ~/podman-store-before-$(date +%Y%m%d).txt
cp -p ~/.config/containers/storage.conf ~/.config/containers/storage.conf.bak-$(date +%Y%m%d)
```

第二步按两种情形分流：

- **有本地大容量盘**（本例 `/media/pc/data`，xfs，attr2/inode64，可用 306G）：把 `storage.conf` 的 `graphroot` 与 `volume_path` 同时改为该盘下同一挂载点内的**实路径**，再用 `podman system migrate` 让运行中容器重新适配。禁止保留中间软链层（与 P2 合并修复）。
- **只有网络盘**：不得使用 overlay。要么放弃该位置，要么显式降级 `driver = "vfs"`——体积约为 overlay 的 2–3 倍、启动明显变慢，属主报告 F1 的「推翻条件」，且必须在交付文档中同时下调交付等级（A4）。

```bash
# [服务器] 改完 storage.conf 后
podman system migrate
podman info --format '{{.Store.GraphRoot}} {{.Store.VolumePath}} {{.Store.GraphDriverName}}'
```

```powershell
# [Windows] vhdx 已在网络盘时，只能导出-注销-重导入到本地固定盘（须人类批准）
wsl --export openkylin-test D:\WSL\backup\openkylin-test-20261111.tar
wsl --unregister openkylin-test
wsl --import openkylin-test D:\WSL\openkylin-test D:\WSL\backup\openkylin-test-20261111.tar --version 2
```

### 1.3 防复发门禁

- **代码落点**：`src/okw/podman.py` 的 `preflight_check` 增加 storage 段，三项断言——真实 graphRoot 的 fstype ∈ {xfs, ext4, btrfs}；`Supports d_type` 为 `true`；`volumePath` 与 `graphRoot` 的设备号一致（`stat -c %d` 相等）。任一项失败即 `preflight` 返回非零，阻断后续 install。
- **文档落点**：`doc/03-podman-rootless.md` 的存储章节加一张「允许/禁止的底层文件系统」判据表，判据引用 F1、F3。
- **流程落点**：`.agents/podman-storage/` 为硬编码引用路径（工作区红线 6），任何迁移不得改名该目录，只允许改 `storage.conf` 指向。

### 1.4 验收（一条命令）

```bash
# [服务器] 期望输出 PASS
REAL="$(readlink -f "$(podman info --format '{{.Store.GraphRoot}}')")"; \
findmnt -no FSTYPE --target "$REAL" | grep -Eq '^(xfs|ext4|btrfs)$' && \
podman info --format json | jq -e '.store.graphStatus["Supports d_type"] == true' >/dev/null && \
[ "$(stat -c %d "$REAL")" = "$(stat -c %d "$(podman info --format '{{.Store.VolumePath}}')")" ] && \
echo PASS || echo FAIL
```

### 1.5 责任与代价

| 项 | 内容 |
|---|---|
| Owner | 环境维护者 |
| 代价 | 需迁移约 46G 下限数据（F-B13），迁移窗口内 Podman 停机 |
| 风险 | `podman system migrate` 后运行中容器需重启；配置写错会导致镜像不可见 |
| 回滚 | 还原 `storage.conf.bak-<日期>` 后再次 `podman system migrate`；vhdx 侧保留导出 tar，必要时重新 import |
| 映射 | A1（主修复）；与 P2 同一变更批次 |

## 2. P2 用软链拼存储后依赖 du 报数

### 2.1 识别信号

- 满足任一即命中：`du -sh <软链路径>` 返回 `0` 或 `4.0K`；`du -x` 结果中出现 `Permission denied`；`df` 与 `du` 对同一对象量级不一致。
- 本例实况：`du -x -sh` 得 `overlay` 39G、`volumes` 7.0G，均**只是下限**，且有 100 余子目录 `Permission denied`（F-B13）。

```bash
# [服务器] 三个诊断值
ls -ld ~/.local/share/containers/storage; readlink -f ~/.local/share/containers/storage
du -sh ~/.local/share/containers/storage      # 返回 0 即为假数
podman unshare du -sx -h "$(readlink -f "$(podman info --format '{{.Store.GraphRoot}}')")/overlay" 2>&1 | tail -3
```

### 2.2 立即修复

```bash
# [服务器] 口径修正：真实路径 + 用户命名空间 + 单挂载点
REAL="$(readlink -f "$(podman info --format '{{.Store.GraphRoot}}')")"
podman unshare du -sx -B1 "$REAL/overlay" "$REAL/volumes" 2>/tmp/du-p2.err | tee /tmp/du-p2.out
grep -c 'Permission denied' /tmp/du-p2.err   # 期望 0
```

三项处理：

1. `podman unshare` 进入用户命名空间（uid0→宿主 1006，subuid 493216:65536，F-B11），可读小写层；这一步消除绝大多数 `Permission denied`。
2. 若仍报权限拒绝，用 `stat -c '%U:%G %a' <路径>` 确认归属；归属异常属宿主侧 chown，须人类批准，不得 `sudo chmod -R 777`。
3. 终态按 A1 收敛：`graphRoot` 直接写真实路径（去掉软链层），`volumePath` 落到同一挂载点，使一条 `du -sx` 能一次量全；收敛前 `du -x` 会因跨挂载点漏计。

### 2.3 防复发门禁

- **口径三条**固化进 A6 快照脚本：①取数前 `readlink -f`；②取数用 `podman unshare`；③必须带 `-x` 并同时记录挂载点。
- **交叉校验**：快照同时输出 `df -h <真实路径>` 与 `du -sx` 结果，两者差异超 10% 时脚本以非零退出，禁止只留 `du` 单一口径。
- **文档落点**：`doc/03-podman-rootless.md` 容量章节写明「软链路径不参与容量统计」。
- **验收门禁**：A6 快照连跑两次结果可 diff，且第二次不含 `Permission denied`。

### 2.4 验收（一条命令）

```bash
# [服务器] 期望输出 PASS（真实路径、无权限拒绝）
REAL="$(readlink -f "$(podman info --format '{{.Store.GraphRoot}}')")"; \
podman unshare du -sx -h "$REAL" >/tmp/du-check.out 2>/tmp/du-check.err; \
grep -q 'Permission denied' /tmp/du-check.err && echo FAIL || \
grep -qE '^[0-9.]+[KMGTP]?\s+/' /tmp/du-check.out && echo PASS || echo FAIL
```

### 2.5 责任与代价

| 项 | 内容 |
|---|---|
| Owner | 环境维护者 |
| 代价 | 口径修正零成本；路径收敛（去软链）与 P1 同批次，代价同 P1 |
| 风险 | 仅改口径不改路径时，容量数字仍会漏计跨挂载点部分 |
| 回滚 | 仅涉及命令与脚本，无状态变更，无需回滚；路径收敛回滚同 P1 |
| 映射 | A1（路径唯一化）+ A6（快照口径） |

## 3. P3 把 import/启动成功当可用

### 3.1 识别信号

- 验收记录只有 `wsl --import` 返回码或 `podman ps` 显示 `Up`；
- 没有任何**版本断言**（工具存在 ≠ 版本正确）；
- 存在声明标签与实际标签不一致的镜像（本例 3 个 `<none>:<none>`，F-B9）。

典型假通过：C10-3 的 LLVM 版本错配——容器起得来、`command -v clang` 有输出，但版本与构建声明不符。

### 3.2 立即修复

分两层补验收，第二层才是「可用」：

```bash
# 第一层：结构验收（已实现）——发行版在列且 WSL2、os-release、UID、wsl.conf、包计数
okw verify openkylin-test
```

```bash
# 第二层：功能冒烟（新增口径）——版本门禁 + 真编译一条最小程序
podman run --rm localhost/openkylin-npu-toolchain:3.0 bash -lc '
  set -e
  gcc --version | head -1
  clang --version | head -1
  python3 -c "import sys; print(sys.version)"
  printf "int main(void){return 0;}" > /tmp/t.c
  gcc /tmp/t.c -o /tmp/t && /tmp/t
' && echo SMOKE_PASS
```

判定规则：冒烟返回非零即「不可用」，无论容器是否在运行；版本行必须与交付声明（A4 登记值）逐字比对，不接受「有输出即通过」。镜像标签必须与声明标签一致，`<none>` 条目不得计入可用资产（与 A3 合并处理）。

### 3.3 防复发门禁

- **代码落点**：`src/okw/podman.py` 的 `verify_run` 增加 `smoke` 段，复用既有 `CheckItem` 结构，把「版本等于声明值」写成断言而不是描述；`src/okw/verify.py` 的五步验收保持不变，作为第一层。
- **文档落点**：`doc/05-openkylin-dev-container.md`（A4 写入点）把「可用」定义为「五步结构验收全 PASS **且** 冒烟 rc=0 且版本匹配」，L1/L2 交付等级均须附一次冒烟记录。
- **流程落点**：复盘与验收记录中禁止只写「import 成功」「容器已启动」，必须附冒烟命令与输出摘要。

### 3.4 验收（一条命令）

```bash
# [服务器] 期望 SMOKE_PASS；镜像名按 A4 声明的等级取
podman run --rm localhost/openkylin-npu-toolchain:3.0 bash -lc 'set -e; gcc --version|head -1; printf "int main(void){return 0;}" >/tmp/t.c; gcc /tmp/t.c -o /tmp/t && /tmp/t' && echo SMOKE_PASS || echo SMOKE_FAIL
```

### 3.5 责任与代价

| 项 | 内容 |
|---|---|
| Owner | 环境维护者（执行）+ 文档维护者（定义「可用」） |
| 代价 | 每次交付多跑一条命令，秒级；写入门禁需改 `verify_run` 一处 |
| 风险 | 版本断言过严会误伤补丁升级，需在 A4 声明中写明允许的版本区间 |
| 回滚 | 冒烟仅读不写，无状态变更；门禁逻辑可独立回退 |
| 映射 | A4（交付等级声明）；与 A3 共用镜像清单口径 |

## 4. P4 只做单点实测就标注「已验证」

### 4.1 识别信号

- 文档出现「已验证」，但同段没有证据等级标注；
- 结论只有一个观测点、一个通道、一次执行；
- 后续被另一条单点观测推翻却无法判定谁对（C11-5 即此型）。

### 4.2 立即修复

按主报告 I4 的四级口径统一表述，并给每条结论补一次反事实对照：

| 等级 | 含义 | 允许的表述 |
|---|---|---|
| E0 | 文档推断，无实测 | 「据文档推断」 |
| E1 | 单点实测，一次观测无对照 | 「单点实测（1 次）」 |
| E2 | 对照实测（反事实或双通道比对） | 「对照实测」 |
| E3 | 可重复脚本化，一条命令可复现并产出可 diff 结果 | 「已验证」 |

补对照的三种低成本做法（任选其一即可从 E1 升到 E2）：

1. **换通道**：同一事实在服务器直连与 WSL sshfs 两处取数比对（工作区已有事实核验纪律）。
2. **前后对照**：如 F5 的 podman 版本问题——同一台机 `command -v podman` 与写死 `/usr/bin/podman` 两条路径取版本，差异即反事实证据。
3. **脚本化升 E3**：把取数固化为 A6 快照脚本，连跑两次输出可 diff。

### 4.3 防复发门禁

- **模板落点**：复盘结论表增加两列——「证据等级（E0–E3）」「复核触发条件（版本/容量/挂载变化时重测）」；A5 对三篇既有复盘各补一处。
- **措辞门禁**：只有 E3 可用「已验证」；E1/E2 必须写明等级与观测次数。
- **复核触发条件**：易变项（容量、镜像清单、连接配置）附采集日期，稳定项（文件系统语义、userns 结构）附版本前提。

### 4.4 验收（一条命令）

```bash
# [服务器或仓库根] 期望输出 0：所有「已验证」都带 E3 标注
grep -rn "已验证" docs/retrospective/reports/project-reports/retrospective-openkylin-podman-ai-20261111/ | grep -v "E3" | wc -l
```

### 4.5 责任与代价

| 项 | 内容 |
|---|---|
| Owner | 复盘维护者 |
| 代价 | 每条结论补一次对照，分钟级；文档改动不动代码 |
| 风险 | 等级标注流于形式——须以「能否被第三人用一条命令复现」为唯一判据 |
| 回滚 | 纯文档变更，回退到前一版即可 |
| 映射 | A5（三篇复盘补等级栏）+ I4 的等级约定 |

## 5. P5 在根分区余量 <20 G 的主机做多层镜像构建

### 5.1 识别信号

- 构建目标盘可用 < 20 G，或 < 2 × 基础层体积；
- `TMPDIR` 仍指向 `/tmp`（根分区），构建上下文与临时层落在系统盘；
- 构建过程出现 `no space left on device` 或中途被杀。

本例实况：`/` 仅 13G（F-A6），而 `openkylin:3.0` 单镜像 26 GB（F-B9），差额不可能在 `/` 上完成。

```bash
# [服务器] 两个盘分别取余量（构建前必跑）
df -BG --output=source,avail / | tail -1
REAL="$(readlink -f "$(podman info --format '{{.Store.GraphRoot}}')")"
df -BG --output=source,avail "$REAL" | tail -1
df -BG --output=avail /tmp /var/tmp | tail -3
```

### 5.2 立即修复

```bash
# [服务器] 构建临时区外置到 15T 盘（本例可用 306G）
export TMPDIR=/media/pc/data/ai/.temp/podman-build-tmp-$(date +%Y%m%d)
mkdir -p "$TMPDIR"
podman build --tmpdir "$TMPDIR" --layers -t localhost/openkylin:3.0-<tag> -f <Containerfile> <context>
```

三项约束：

1. **空间归属**：镜像层写入 `graphRoot`，临时层写入 `--tmpdir`，两者都必须在 15T 盘上；只改 `TMPDIR` 不改 `graphRoot` 仍会撑爆根分区。
2. **门槛**：可用空间 ≥ 20 G 且 ≥ 2 × 基础层体积，任一不满足即停建。
3. **可清理性**：构建前用 `podman system df` 核对可回收量——该命令当前因 infra-container 缺失而失败（F-B14），故 P5 的清理决策依赖 A2 先行修复。

```bash
# [服务器] 构建残留清理（须人类批准）
podman image prune -f
rm -rf "$TMPDIR"
```

### 5.3 防复发门禁

- **脚本落点**：A6 快照脚本增加 build-precheck 段，构建前输出两个盘的余量与门槛判定，未达标以非零退出阻断构建。
- **文档落点**：`doc/05-openkylin-dev-container.md` 写明「构建必须在 15T 盘上进行，`TMPDIR` 与 `graphRoot` 同盘」。
- **流程落点**：容器镜像构建类任务在计划阶段即写明目标盘与预估体积，不接受「先跑再看」。

### 5.4 验收（一条命令）

```bash
# [服务器] 期望 PASS：目标盘余量 ≥ 20G
avail=$(df -BG --output=avail "$(readlink -f "$(podman info --format '{{.Store.GraphRoot}}')")" | tail -1 | tr -dc '0-9'); [ "${avail:-0}" -ge 20 ] && echo PASS || echo FAIL
```

### 5.5 责任与代价

| 项 | 内容 |
|---|---|
| Owner | 环境维护者 |
| 代价 | 零成本（仅设置环境变量与门槛脚本）；若需扩容则属人类决策 |
| 风险 | 门槛按 20 G 固定值可能对超大镜像仍不够，故叠加「≥2× 基础层」判据 |
| 回滚 | 恢复默认 `TMPDIR` 即可；外置目录按 `.temp` 治理规则清理，删除须人类批准 |
| 映射 | A6（快照门禁）+ A2（可回收量前置）；与 P1 共用「存储单一路径」前提 |

## 6. 落地顺序与总体验收

### 6.1 顺序

1. **同一批次、需人类批准**：P1 + P2（存储路径唯一化，A1）。二者共用一次 `storage.conf` 变更与一次 `podman system migrate`，不可分开做。
2. **独立、可立即做**：P3（冒烟）、P4（证据等级）、P5（构建门槛）——均为只读或文档动作，可并行。
3. **依赖项**：P5 的清理决策依赖 A2；P2 的脚本口径依赖 A6；P3 的「可用」定义依赖 A4。

### 6.2 完成判据（五条命令全 PASS）

| 反模式 | 判据 | 关联行动 |
|---|---|---|
| P1 | 1.4 的 fstype + `Supports d_type` + 同设备断言 | A1 |
| P2 | 2.4 的真实路径 `podman unshare du -sx` 无权限拒绝 | A1、A6 |
| P3 | 3.4 冒烟输出 `SMOKE_PASS`，且版本与声明一致 | A4 |
| P4 | 4.4 的 `grep` 结果为 `0` | A5 |
| P5 | 5.4 目标盘余量 ≥ 20G 且 ≥ 2× 基础层 | A6、A2 |

### 6.3 不做的事

- 不把网络盘挂到本地路径后再当本地盘用（语义仍是网络盘，F1 不满足）。
- 不为了 `du` 出数而放宽目录权限（应改用 `podman unshare`）。
- 不以「容器在运行」替代冒烟，不以「跑过一次」替代证据分级。