---
id: "nested-disk-blindspot-diagnosis"
title: "嵌套容器磁盘盲区诊断模式（Nested Disk Blindspot Diagnosis）"
type: "process-pattern"
maturity: "L1-实验性"
maturity_note: "案例1：C盘治理 20260828，四层诊断链（system df → machine df/du 矛盾 → root du → UpperDir diff）定位 21GB 嵌套存储，单案例待验证"
created: "2026-08-28"
last_updated: "2026-08-28"
source:
  - "retrospective-c-drive-vhdx-recovery-20260828（洞察I-1：嵌套容器可写层是宿主磁盘的隐形黑洞）"
related_patterns:
  - "nested-engine-storage-externalize.md"
  - "vhdx-two-phase-recovery-sop.md"
  - "monorepo-ci-blindspot-detection.md"
tags: ["nested-containers", "disk-usage", "observability", "permission-shadowing", "overlay-upperdir", "diagnosis", "du", "podman"]
validation_count: 1
---

# 嵌套容器磁盘盲区诊断模式（Nested Disk Blindspot Diagnosis）

## 触发场景

- 宿主磁盘（或 vhdx）占用异常，但常规排查手段（镜像清单、`docker stats`、挂载卷内容）对不上账
- 容器内运行嵌套引擎（podman-in-podman / dinod）或存在 root-only 大目录
- `podman system df` 显示某容器可写层远超预期（>10GB），但不知道里面是什么
- 容器疑似僵尸态（`ps` 显示 running 但 `exec` 无响应）

**适用于**：多层虚拟化栈（宿主→WSL→podman machine→容器→嵌套引擎）的磁盘占用定位；权限遮蔽环境（普通用户视角缺失 root-only 目录）。

**不适用于**：单层容器简单排查（`podman inspect .SizeRootfs` 即够）；运行时性能问题（CPU/内存瓶颈，非空间问题）。

## 问题本质（双重不可见）

嵌套架构下磁盘占用存在**两个正交的观测盲区**，任意单一视角都会严重低估：

1. **宿主侧盲区**：`podman system df` 只显示容器可写层总量（22.76GB），不显示内部构成——「总量可见、构成不可见」
2. **客体内盲区**：普通用户 `du` 因权限无法统计 root-only 目录（7.3GB vs root 实测 32GB，**低估 4 倍**）——「权限可见性 ≠ 物理真实性」

直觉假设「容器内看一眼 du 就知道占了多少」在嵌套 + 权限遮蔽下双重失效。诊断必须**分层下钻**且每层用对工具（正确权限 + 正确视角）。

## 核心步骤（四层下钻诊断链）

```
L1 宿主层  → L2 机器层矛盾 → L3 提权核实 → L4 可写层解剖
```

1. **L1 宿主总量预警**：`podman system df` / `podman ps -s`——发现哪个容器可写层异常（本案例 22.76GB）
2. **L2 机器层矛盾检测**：发行版内 `df -h /` 用量 vs 普通用户 `du -xh /` 求和——**两者差 >2 倍即为盲区信号**（本案例 df 31GB vs du 7.3GB）
3. **L3 提权核实**：`wsl -d <distro> -u root -- du -xh --max-depth=2 /`——root 视路还原真实分布（本案例定位 `/var/lib` 24GB）
4. **L4 可写层解剖**（定位到具体容器后）：
   ```bash
   # 宿主侧获取 overlay upperdir（僵尸容器唯一可行路径）
   podman inspect <容器> --format {{.GraphDriver.Data.UpperDir}}
   # root 视角深挖构成
   du -xh --max-depth=3 <UpperDir> | sort -rh | head
   ```
5. **交叉验证**：诊断结论须能解释全链条数字（本案例：UpperDir diff 21GB 嵌套存储 ≈ system df 可写层 22.76GB − 基础层 ≈ machine /var/lib 24GB 主项）

## 反模式

| 反模式 | 后果 | 实证 |
|--------|------|------|
| ❌ 用普通用户 du 评估容器/机器占用 | 低估 4 倍（7.3 vs 32GB），排查方向全错 | F-006 |
| ❌ 僵尸容器内 exec 排查 | 主进程已死 exec 必失败，浪费时间 | F-021 前置 |
| ❌ 只看 `podman images` 对账 | 镜像清单总量与磁盘用量不匹配时束手无策（悬空层/可写层不在清单） | F-010 |
| ❌ 逐层手工猜（不按 L1→L4 链下钻） | 在 91 个镜像里逐个排查，无法收敛 | F-010 |
| ❌ 停在 L2 矛盾直接下结论 | 「df 虚报」错误归因，错过真实 24GB | F-006→F-007 |

## 失败案例（20260828 真实实证，防成功偏误）

| # | 失败尝试 | 现象 | 教训 |
|---|---------|------|------|
| 1 | 机器内普通用户 du 排查 | 只见 7.3GB，与 df 31GB 矛盾无法解释 | 必须 root 视角（L3），权限遮蔽是结构性盲区 |
| 2 | 容器内 du（exec 路径） | 容器主进程已死，exec 卡死/失败 | 僵尸态只能宿主侧 UpperDir 解剖（L4） |
| 3 | podman top 确认进程 | 输出正常但实际 `/proc/<pid>` 不存在——running 状态不可信 | 状态字段 ≠ 进程存活，需交叉验证 |
| 4 | 镜像清单对账 | 91 个镜像逐一估算无法收敛到 24GB | 悬空层/可写层不在 images 清单，需 UpperDir diff |

> 教训收敛：每个失败都源于「用错了层的工具」——诊断链的价值就是强制每层用对视角。

## 不适用/反目标/边界场景（≥3类，防确认偏误）

| 类别 | 场景 | 不适用原因 |
|------|------|-----------|
| 反目标1 | 单层容器、无权限遮蔽 | `podman inspect .SizeRootfs/.SizeRw` 一步出数，诊断链过度工程 |
| 反目标2 | 挂载卷内容排查 | bind mount 数据宿主可直接访问，无需进入客体视角 |
| 反目标3 | 运行时性能诊断 | 本模式解决「空间在哪」，不解决 CPU/IO 热点 |
| 边界1 | Docker（非 podman）环境 | L4 命令需替换为 `docker inspect .GraphDriver.Data`（诊断链结构不变） |
| 边界2 | rootless 容器栈 | uid 映射使 root 视角语义变化，L3/L4 需按 rootless 权限模型调整 |
| 边界3 | 诊断目标为实时增长 | 静态 du 只给快照，增长源需配合 `podman events` / 文件级监控 |

## 早期预警信号（≥5个）

| 信号 | 判定阈值 | 含义 |
|------|---------|------|
| `podman system df` 容器 SIZE >10GB | 可写层异常 | 进入 L1，定位具体容器 |
| 发行版 df 用量 > 用户 du 求和 ×2 | 权限遮蔽 | 进入 L3 提权核实 |
| 镜像清单总量 < 磁盘用量 ×0.5 | 悬空层/可写层大头 | 跳过镜像对账，直接 L4 |
| `podman exec` 无响应但 ps 显示 running | 主进程死亡 | 放弃客体侧排查，走宿主 UpperDir |
| vhdx 增速 > 挂载内容增速 | 可写层隐形写入 | 触发全链诊断（L1→L4） |

## 跨场景迁移

| 场景 | 盲区形态 | 诊断链变体 |
|------|---------|-----------|
| Docker Desktop（WSL后端） | com.docker.vhdx 膨胀 | L1 docker system df → L3 wsl root du → L4 docker inspect |
| Kubernetes 节点 | emptyDir/镜像双层叠加 | L1 kubectl describe → L3 节点 root du /var/lib/kubelet |
| Linux 服务器（无容器） | 用户进程写 root 目录 | L2 df vs du 差异 → lsof + /proc/<pid>/fd 定位写入者 |
| 本模式姊妹场景 | — | 见 monorepo-ci-blindspot-detection（同属「盲区检测」家族：CI 盲区 = 测试覆盖盲区） |

**本质**：多层抽象栈中，每一层的「可见性」都只覆盖自己之下的第一层；跨层诊断必须显式切换视角（提权 + 换工具），且结论必须通过全链条数字交叉验证（各层占用量闭合）。

## 关联文档

- 复盘报告：[retrospective-c-drive-vhdx-recovery-20260828](../../reports/environment-setup/retrospective-c-drive-vhdx-recovery-20260828/README.md)（洞察 I-1）
- 预防模式：[nested-engine-storage-externalize.md](nested-engine-storage-externalize.md)（诊断发现黑洞后如何避免复发）
- 治理模式：[vhdx-two-phase-recovery-sop.md](vhdx-two-phase-recovery-sop.md)（诊断定位后如何物理回收）
- 同族模式：[monorepo-ci-blindspot-detection.md](monorepo-ci-blindspot-detection.md)（盲区检测方法论家族）
