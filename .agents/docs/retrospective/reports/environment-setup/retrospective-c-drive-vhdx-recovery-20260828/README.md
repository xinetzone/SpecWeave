---
id: retrospective-c-drive-vhdx-recovery-20260828
date: 2026-08-28
type: retrospective
methodology: seven-concepts (R-I-E-C)
depth: standard
scenario: problem-solving + milestone
source: "C盘空间耗尽诊断 → 嵌套容器镜像清理 → Ubuntu注销 → sparse/compact互斥发现 → podman vhdx物理压缩"
tags: [wsl2, vhdx, diskpart-compact, sparse-vhd, fstrim, podman, nested-containers, disk-space, pagefile]
session: sc-20260828-c-drive-cleanup-retro
---

# C盘空间耗尽治理（vhdx 回收）复盘

## 一、背景与目标

C盘（400GB Windows-SSD）剩余空间耗尽，系统濒临崩溃。本会话执行完整诊断与治理：识别三大 vhdx 占用、清理嵌套容器镜像、注销冗余发行版、物理压缩 podman machine vhdx。

**最终状态：**

| 指标 | 治理前 | 治理后 |
|------|--------|--------|
| C盘剩余空间 | 3.3GB（一度降至 1 字节） | **73.79GB** |
| podman machine vhdx | 33.04GB | **11.93GB** |
| Ubuntu 发行版 vhdx | 50.53GB（占C盘） | 已注销（用户预期操作） |
| jupyter-podman 容器 | 僵尸态 | Up (healthy) |

---

## 二、事实还原（R - Retrospective）

### 2.1 空间占用诊断结果

| # | 事实 | 编号 |
|---|------|------|
| 1 | C盘总容量 429GB，任务开始时剩余 3.3GB | F-001 |
| 2 | 诊断期间剩余空间一度降至 **1 字节**（FreeSpace=1） | F-002 |
| 3 | `pagefile.sys` 占 29.6GB（系统托管） | F-003 |
| 4 | 三个 vhdx 合计 92GB 位于C盘：Ubuntu 50.53GB / podman-machine-default 33.04GB / wslc storage 8.75GB | F-004 |
| 5 | Ubuntu vhdx 内部 df 显示已用 40GB，其中 `/home/xinzo` 占 35GB（du实测39G） | F-005 |
| 6 | podman machine 内部 df 显示已用 31GB；普通用户 du 仅见 7.3GB，root du 见 32GB | F-006 |
| 7 | podman machine 内 `/var/lib/containers/storage/overlay` 占 24GB（root视角） | F-007 |
| 8 | `podman system df` 显示 jupyter-podman 容器可写层 22.76GB | F-008 |
| 9 | jupyter 容器**内部嵌套 podman** 存储 `/var/lib/containers` 占 21GB | F-009 |
| 10 | 嵌套 podman 含 91 个镜像：xmnn-whl-builder-full 6.07GB、xmnn-whl-builder 5.2GB、devcontainer-base 3.5GB、xmnn-runtime-slim 2.86GB 及大量悬空层 | F-010 |
| 11 | AppData\Local 其余大户：Feishu 3.7GB / uv 3.46GB / datalab 3.21GB / Microsoft 2.57GB | F-011 |

### 2.2 治理动作时间线

| # | 动作 | 结果 | 编号 |
|---|------|------|------|
| 12 | 用户 Temp 目录清理 | 释放 2GB | F-012 |
| 13 | `uv cache clean` + npm-cache 清理 | 释放 ~4.5GB（uv 642MB 中清 337MB+） | F-013 |
| 14 | 用户确认清理全部嵌套镜像 | 决策输入 | F-014 |
| 15 | 容器内 `podman rm -af` + `system prune -a -f` 报"image in use" | 改用 `podman rmi -af --force` | F-015 |
| 16 | 嵌套存储 21GB → **764KB** | ✅ | F-016 |
| 17 | 容器内 podman 报 boot ID 缓存不一致 | 删 `/run/containers/storage` 与 `/run/libpod` 后恢复 | F-017 |
| 18 | `wsl --manage Ubuntu --set-sparse true` 首次失败（缺 `--allow-unsafe`） | 加参数后转换成功 | F-018 |
| 19 | sparse 转换后 vhdx 获得 `SparseFile` 属性 | ✅ | F-019 |
| 20 | sparse 后 `fstrim` 仅归还 **0.1GB**（967GiB trimmed 声明与实际归还不符） | ⚠️ | F-020 |
| 21 | 用户在另一会话注销 Ubuntu 发行版 | 释放 ~50GB（预期操作） | F-021 |
| 22 | 阶段一结束：C盘剩余 1GB → **53.6GB** | ✅ | F-022 |

### 2.3 diskpart compact 攻坚过程（第二阶段）

| # | 事实 | 编号 |
|---|------|------|
| 23 | 首次 compact 失败：「文件被另一程序使用」——vhdx 句柄由 wslservice + vmcompute 持有 | F-023 |
| 24 | 停止两服务后仍失败，错误变为「**文件不能是稀疏文件**」——sparse 属性阻止 compact | F-024 |
| 25 | `fsutil sparse setflag <vhdx> 0` 清除稀疏标志 | ✅ | F-025 |
| 26 | 清标志后 diskpart compact 成功：32.31GB → **11.93GB**（回收 20.4GB） | F-026 |
| 27 | 压缩后 C盘剩余 **73.79GB** | ✅ | F-027 |
| 28 | 压缩后 vhdx 大小与 machine 内部实际用量 11.93GB **完全一致** | F-028 |
| 29 | 压缩窗口期间另一会话执行 `podman machine start` 与压缩撞车（第一次尝试失败诱因之一） | F-029 |
| 30 | 服务恢复后容器首次启动失败（systemd connection reset），等待后二次启动成功 | F-030 |
| 31 | 按项目约定挂起 `sleep infinity` 保活进程防 WSL 自动关机 | F-031 |
| 32 | jupyter-podman-rootless 发行版已位于 D盘（`.wsl-cache`，此前会话迁移） | F-032 |
| 33 | sparse+fstrim 二次尝试（sparse状态下重跑）仅归还 1GB trimmed / 0.1GB 实际 | F-033 |

**G1 质量门**：✅ 33条事实，纯客观陈述，无因果推断词，关键数值完整。

---

## 三、核心洞察（I - Insight）

### I-1 嵌套容器可写层是宿主磁盘的隐形黑洞

- **陈述**：容器内运行嵌套容器引擎时，其镜像/构建层永久驻留外层容器的可写层，宿主侧 `podman system df` 只见总量不见构成。
- **证据**：F-008（可写层22.76GB）、F-009（其中21GB是容器内podman）、F-010（91个镜像明细）、F-016（清理后764KB）。
- **反常识**：直觉认为「镜像在镜像里」不占额外空间——实际嵌套引擎的 overlay 存储全部落在外层可写层，且普通用户 `du` 因权限只见 7.3GB（F-006），双重不可见。
- **行动**：容器内构建完成后立即 `podman system prune -a -f`；长期方案是构建缓存挂载到外部卷（`-v buildcache:/cache`），使可写层保持近零增长。

### I-2 sparse 与 compact 是互斥的两条 vhdx 回收路径

- **陈述**：NTFS 稀疏属性（`set-sparse`）与 `diskpart compact vdisk` 不能叠加使用——sparse 文件会直接被 compact 拒绝。
- **证据**：F-019（sparse设置成功）、F-024（compact报「文件不能是稀疏文件」）、F-025（清标志）、F-026（随后compact成功）。
- **反常识**：直觉认为「先转 sparse 自动缩，再 compact 兜底」双保险更稳妥——实际两者互斥，转了 sparse 就堵死 compact 路径，必须先 `fsutil sparse setflag <file> 0` 还原。
- **行动**：二选一决策——在线场景（不能停机）选 sparse + 定期 fstrim；离线场景（可 shutdown）选保持非sparse + 停 wslservice/vmcompute + diskpart compact。本案例离线路径单次回收 20.4GB。

### I-3 删除数据只是元数据操作，空间归还需要显式物理回收

- **陈述**：ext4 TRIM 将块标记为 VHDX 未映射仅是元数据层面的记账，vhdx 文件大小纹丝不动；必须由 compact（离线重写文件）或 sparse 模式下的 TRIM 穿透（在线归还）才实际释放宿主空间。
- **证据**：F-016（容器内删除21GB）+ F-020/F-033（fstrim 前后 vhdx 仍 32.31GB）+ F-026（compact 后 11.93GB）+ F-028（与内部用量完全一致）。
- **反常识**：直觉认为「容器里删了、fstrim 也跑了，宿主空间就该回来了」——实际 fstrim 的 trimmed 字节数（967GiB）是文件系统视角的声明，与宿主实际归还量（0.1GB）是两回事；删除时机的 TRIM 已被记账，第二次 fstrim 无事可做。
- **行动**：vhdx 膨胀治理的标准三步——①容器/发行版内删除数据 ②fstrim 一次（把未映射状态写入 VHDX 元数据）③compact 物理回收。跳过任何一步都拿不到空间。

**G2 质量门**：✅ 3条洞察，四元组完整（陈述/证据/反常识/行动），维度独立（存储构成/回收路径互斥/回收时机），证据均可追溯事实编号。

---

## 四、模式萃取（E - Extraction）

### 模式1：VHDX 二相回收模式（sparse在线相 ↔ compact离线相）

**YAML:**
```yaml
id: bp-vhdx-two-phase-recovery
name: VHDX二相回收
maturity: L2
cases: [c-drive-vhdx-recovery-20260828, docker-cache-to-wsl-migration-20260818]
```

**触发场景**：WSL2/Podman machine/Hyper-V 虚拟磁盘 vhdx 文件大小远超内部实际用量（差值>5GB 值得处理）。
**不适用于**：vhdx 大小与内部用量基本一致（无可回收空洞）；系统盘有充足空间（收益低于停机成本）。

**核心步骤**：
1. 测差值：内部 `df -h /` vs 宿主 vhdx 文件大小，确认回收潜力
2. 备数据：发行版内删除不需要的数据，`fstrim -v /` 一次
3. 选路径（互斥二选一）：
   - **在线相**：`wsl --manage <distro> --set-sparse true --allow-unsafe`，此后定期 fstrim 即时归还
   - **离线相**：`fsutil sparse setflag <vhdx> 0`（若曾设sparse）→ `wsl --shutdown` → 停 `wslservice` + `vmcompute` 服务 → `diskpart: select vdisk → attach readonly → compact → detach` → 恢复服务
4. 验收：vhdx 大小 ≈ 内部实际用量（本案例 11.93GB = 11.93GB，F-028）

**反模式**（均来自本案例实际教训）：
- ❌ 先 `set-sparse` 再 diskpart compact——sparse 属性导致 compact 直接报错（F-024），需先清标志
- ❌ 只停 wslservice 不停 vmcompute——vhdx 句柄仍被 Hyper-V 宿主计算服务持有（F-023）
- ❌ 压缩窗口期间允许并行会话重启 machine——句柄竞争导致「文件被使用」（F-029）
- ❌ 删除数据后反复 fstrim 指望回收——TRIM 已记账的块二次 trim 无效果（F-033）

**检验标准**：compact 后 vhdx 大小与 `df` 实际用量偏差 <5%。
**迁移示例**：Hyper-V 代管虚拟机磁盘收缩、Windows Dev Drive、Docker Desktop（WSL后端）的 `wsl --shrink` 均遵循同一二相模型。

### 模式2：嵌套引擎存储卷外置模式

**YAML:**
```yaml
id: bp-nested-engine-storage-externalize
name: 嵌套存储卷外置
maturity: L1
cases: [c-drive-vhdx-recovery-20260828]
note: 单案例待验证
```

**触发场景**：容器内需运行嵌套容器引擎（podman-in-podman、docker-in-docker）进行构建。
**核心步骤**：①嵌套引擎存储根目录指向命名卷或 bind mount ②构建产物即时导出到挂载卷 ③构建会话结束 prune。
**反模式**：❌ 默认存储路径直接写可写层（21GB黑洞，F-009）❌ 依赖普通用户 du 排查（权限遮蔽，F-006）❌ 用后不清理（xmnn 系列构建完成后镜像滞留）。
**检验标准**：外层容器可写层大小长期稳定（`podman system df` 的 Containers SIZE 不随嵌套构建增长）。
**迁移示例**：CI 流水线中 docker-in-docker 构建器的 /var/lib/docker 卷外置。

**G3 质量门**：✅ 模式1 达 L2（双案例：本案例 + docker-cache-to-wsl-migration-20260818 的 vhdx 处理）；模式2 标注 L1 单案例待验证；触发/步骤/反模式/检验/迁移五要素完整。

---

## 五、行动项（A - Atomization）

| # | 行动项 | Owner | 验收标准 | 优先级 |
|---|--------|-------|----------|--------|
| A-1 | 将「podman machine vhdx compact」纳入季度维护（参照模式1离线相步骤） | xinzo | vhdx ≤ 内部用量×1.05 | 中 |
| A-2 | jupyter 容器内构建 SOP 增加「结束即 prune」步骤 | xinzo | 可写层 <1GB | 中 |
| A-3 | pagefile 迁 D盘/限大小评估（29.6GB，需重启，当前不紧急） | xinzo | 决策记录 | 低 |

**G4 质量门**：✅ 单一职责、可独立验收。

---

## 六、质量门通过记录

| 质量门 | 结果 | 说明 |
|--------|------|------|
| G1 事实无因果词 | ✅ | 33条事实纯客观 |
| G2 洞察四元组 | ✅ | 3条完整 |
| G3 模式可迁移 | ✅ | 模式1(L2)+模式2(L1) |
| G4 行动项原子化 | ✅ | 3项 |

## 七、关联

- 前序案例：[retrospective-docker-cache-to-wsl-migration-20260818](../retrospective-docker-cache-to-wsl-migration-20260818/README.md)（vhdx 处理先例，模式1的第二案例）
- 模式1已入库：[vhdx-two-phase-recovery-sop](../../../patterns/process-patterns/vhdx-two-phase-recovery-sop.md)（process-patterns，L2，validation_count=2，含实际案例与跨场景迁移）
- 模式2已入库：[nested-engine-storage-externalize](../../../patterns/process-patterns/nested-engine-storage-externalize.md)（process-patterns，L1，validation_count=1，反模式实证完整，正向卷外置实施待下次构建任务验证后升 L2）
- 洞察I-1诊断侧面已入库：[nested-disk-blindspot-diagnosis](../../../patterns/process-patterns/nested-disk-blindspot-diagnosis.md)（process-patterns，L1，validation_count=1，四层下钻诊断链；与模式2/模式1构成诊断→预防→治理三部曲）
- 相关约定：`vmIdleTimeout=-1` 保活约定（AGENTS 项目记忆）
