---
id: "nested-disk-blindspot-diagnosis-sop"
title: "嵌套容器磁盘盲区诊断 SOP（四层下钻）"
type: "process-pattern"
maturity: "L1-实验性"
maturity_note: "案例1：C盘治理 20260828，四层链定位 21GB 嵌套存储（7.3GB→32GB→24GB→21GB 逐层收敛）；正向应用 1 次。方法论文档：nested-disk-blindspot-diagnosis.md"
created: "2026-08-28"
last_updated: "2026-08-28"
source:
  - "nested-disk-blindspot-diagnosis.md（方法论文档，本SOP为其可执行细化）"
  - "retrospective-c-drive-vhdx-recovery-20260828（洞察I-1，F-006~F-010）"
related_patterns:
  - "nested-disk-blindspot-diagnosis.md"
  - "nested-engine-storage-externalize.md"
  - "vhdx-two-phase-recovery-sop.md"
tags: ["nested-containers", "disk-usage", "diagnosis", "du", "overlay-upperdir", "podman", "wsl2", "zombie-container"]
validation_count: 1
---

# 嵌套容器磁盘盲区诊断 SOP（四层下钻）

## 触发场景

- 宿主磁盘/vhdx 占用异常，镜像清单与挂载卷对不上账
- `podman system df` 显示某容器可写层远超预期（>10GB）
- 容器内疑似运行嵌套引擎（podman-in-podman / dinod）
- 容器疑似僵尸态（`ps` 显示 running 但 `exec` 无响应）

**不适用于**：单层容器简单排查（`podman inspect .SizeRw` 即够）；性能问题（CPU/IO 热点）；挂载卷内容排查（宿主可直接访问）。

## 前置知识（双重不可见）

1. **宿主侧盲区**：`podman system df` 只见可写层总量，不见构成
2. **客体内盲区**：普通用户 `du` 无法统计 root-only 目录（本案例 7.3GB vs 32GB，低估 4 倍）

诊断铁律：**每层用对工具**（正确权限 + 正确视角），结论必须全链条数字闭合。

## 前置条件（B0）

- ✅ WSL 运行中（`wsl -l -v`），目标发行版/机器已启动
- ✅ 记录宿主侧基线：C盘/数据盘剩余空间、vhdx 文件大小
- ✅ 记录发行版清单与容器清单（`podman ps -a`）

---

## L1 宿主层预警：定位异常容器

```powershell
# 容器磁盘用量总览（可写层 SIZE 列）
wsl -d podman-machine-default -- podman system df
# 或按容器列出
wsl -d podman-machine-default -- podman ps -as --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"
```

**判定**：某容器 SIZE >10GB → 进入 L2；全部 <5GB → 问题不在可写层，转查镜像/卷（`podman images` / `podman volume ls` + du）。

## L2 机器层矛盾检测：盲区信号

```powershell
# 发行版内部逻辑用量 vs 普通用户可见量
wsl -d podman-machine-default -- df -h /
wsl -d podman-machine-default -- du -xsh / 2>$null
```

**判定**：`df 用量` 与 `du 求和` 差 >2 倍 → **权限遮蔽确认**，进入 L3。若基本一致 → 无 root-only 大目录，转查镜像层总量。

## L3 提权核实：还原真实分布

```powershell
# root 视角逐层还原（关键一步）
wsl -d podman-machine-default -u root -- du -xh --max-depth=2 /var/lib 2>$null | sort -rh | head -15
```

**判定**：定位最大目录（本案例 `/var/lib/containers/storage/overlay` 24GB）→ 与 L1 异常容器对应 → 进入 L4 解剖该容器。

## L4 可写层解剖：定位构成（含僵尸态）

先判容器死活（`exec` 超时即僵尸）：

```powershell
# 宿主侧获取 overlay upperdir（活/僵尸容器通用，僵尸唯一可行路径）
wsl -d podman-machine-default -- podman inspect <容器名> --format "{{.GraphDriver.Data.UpperDir}}"
# root 视角深挖构成
wsl -d podman-machine-default -u root -- du -xh --max-depth=3 <UpperDir> | sort -rh | head -15
```

**判定**：最大子目录即黑洞本体（本案例 UpperDir 下嵌套 `/var/lib/containers` 21GB）。

## L5 交叉验证（验收标准）

结论必须解释全链条数字：

```
UpperDir 黑洞 ≈ L1 可写层总量 − 镜像基础层
UpperDir 黑洞 ≈ L3 定位目录的主项
```

本案例：21GB ≈ 22.76GB（F-008）− 基础层 ≈ 24GB（F-007）主项 ✅ **闭合**。

数字不闭合 → 回到对应层重查（常见漏项：悬空卷、`podman volume` 未查、`/var/log` 日志）。

---

## 诊断后行动（超出本 SOP 范围，指向姊妹文档）

| 诊断结论 | 后续 SOP |
|---------|---------|
| 黑洞 = 嵌套引擎镜像（本案例） | 容器内 `podman rmi -af --force` 清理 → [VHDX 二相回收 SOP](vhdx-two-phase-recovery-sop.md) 归还宿主空间 |
| 黑洞 = 构建缓存 | [嵌套引擎存储卷外置](nested-engine-storage-externalize.md) 预防复发 |
| 容器僵尸态 | 重启容器后重新诊断（UpperDir 数据重启不丢） |

## 故障排查

| 症状 | 根因 | 处置 |
|------|------|------|
| L2 du 输出远小于 df 且怀疑统计错误 | 权限遮蔽（root-only 目录） | 进 L3 用 `-u root` 重跑 |
| L4 `podman exec` 卡死/失败 | 主进程已死（僵尸态） | 直接走宿主侧 inspect UpperDir |
| L4 inspect 正常但 `/proc/<pid>` 不存在 | 状态字段不可信 | 同上，以 UpperDir 为准 |
| L5 数字差悬空层 | 悬空镜像层不在 images 清单 | `podman images -f dangling=true` + `podman image prune` |
| L5 数字差悬空卷 | 匿名卷滞留 | `podman volume ls` + `podman volume prune` |
| L3 root du 也对不上 | du 不跨文件系统边界 | 加 `-x` 确保单文件系统；对比 `df -i` inode 泄漏（已删文件被进程持有） |
| L3 差值 = 已删文件被进程占用 | lsof 场景 | `lsof +L1` 找 deleted 状态文件，重启持有进程 |

## 反模式

| 反模式 | 后果 | 实证 |
|--------|------|------|
| ❌ 普通用户 du 评估机器/容器占用 | 低估 4 倍，方向全错 | F-006 |
| ❌ 僵尸容器内 exec 排查 | 卡死浪费时间 | F-021 前置 |
| ❌ 镜像清单对账（91 个镜像逐个猜） | 无法收敛 | F-010 |
| ❌ 停在 L2 矛盾下结论「df 虚报」 | 错误归因 | F-006→F-007 |
| ❌ 跳过 L5 交叉验证 | 结论数字不闭合，伪定位 | 方法论要求 |

## 失败案例（20260828 真实实证，防成功偏误）

| # | 失败尝试 | 现象 | 教训 |
|---|---------|------|------|
| 1 | 普通用户 du 排查机器 | 7.3GB vs df 31GB 矛盾 | L3 必须提权 |
| 2 | 容器内 du（exec） | 主进程已死，失败 | 僵尸态走 L4 宿主侧 |
| 3 | podman top 看进程 | 输出正常但 /proc 无此进程 | 状态不可信，UpperDir 为准 |
| 4 | 镜像清单对账 | 91 镜像估算不收敛 | 跳过清单，直接 UpperDir diff |

## 不适用/反目标/边界场景（≥3类，防确认偏误）

| 类别 | 场景 | 不适用原因 |
|------|------|-----------|
| 反目标1 | 单层容器无权限遮蔽 | `podman inspect .SizeRw` 一步出数，四层链过度工程 |
| 反目标2 | 挂载卷数据排查 | bind mount 宿主可直接访问 |
| 反目标3 | 运行时性能诊断 | 本 SOP 解决「空间在哪」 |
| 边界1 | Docker（非 podman） | L4 换 `docker inspect .GraphDriver.Data`，链结构不变 |
| 边界2 | rootless 容器栈 | uid 映射改变 root 视角语义，L3/L4 按 rootless 模型调整 |
| 边界3 | 诊断目标是增长源而非存量 | 静态 du 仅快照，需配合 `podman events` / 文件级监控 |

## 早期预警信号（≥5个）

| 信号 | 判定阈值 | 含义 |
|------|---------|------|
| `podman system df` 容器 SIZE >10GB | 可写层异常 | 进 L1 |
| df 用量 > 用户 du 求和 ×2 | 权限遮蔽 | 直接进 L3 |
| 镜像清单总量 < 磁盘用量 ×0.5 | 悬空层/可写层大头 | 跳过清单对账 |
| `podman exec` 无响应但 ps 显示 running | 主进程死亡 | 放弃客体侧，走 L4 |
| vhdx 增速 > 挂载内容增速 | 可写层隐形写入 | 全链诊断 |

## 关联文档

- 方法论文档：[nested-disk-blindspot-diagnosis.md](nested-disk-blindspot-diagnosis.md)（本 SOP 的模式来源，含跨场景迁移表）
- 复盘报告：[retrospective-c-drive-vhdx-recovery-20260828](../../reports/environment-setup/retrospective-c-drive-vhdx-recovery-20260828/README.md)
- 诊断后治理：[vhdx-two-phase-recovery-sop.md](vhdx-two-phase-recovery-sop.md) / [nested-engine-storage-externalize.md](nested-engine-storage-externalize.md)
