---
id: "logical-delete-physical-reclaim-gap"
title: "声明-回收鸿沟模式（Logical Delete ≠ Physical Reclaim）"
type: "methodology-pattern"
category: "tools-automation"
maturity: "L1-实验性"
maturity_note: "案例1（完整复盘）：vhdx治理 20260828（删除21GB→fstrim归还0.1GB→compact回收20.4GB全链条实证）；迁移参照（业界公知）：PostgreSQL VACUUM、git gc、JVM GC、SQLite VACUUM。1个完整验证+多领域已知同构案例"
created: "2026-08-28"
last_updated: "2026-08-28"
source:
  - "retrospective-c-drive-vhdx-recovery-20260828（洞察I-3：删除数据只是元数据操作）"
related_patterns:
  - "../../process-patterns/vhdx-two-phase-recovery-sop.md"
  - "../governance-strategy/mutual-exclusion-composability-precheck.md"
tags: ["logical-delete", "physical-reclaim", "gc", "vacuum", "trim", "capacity-planning", "observability", "storage"]
validation_count: 1
---

# 声明-回收鸿沟模式（Logical Delete ≠ Physical Reclaim）

## 触发场景

- 删除/释放操作执行后，容量监控指标（磁盘、内存、配额）**没有下降**
- 系统提供「删除」与「回收/整理」两个**分离的命令**（delete + vacuum/gc/compact/trim）
- 按配额规划容量时，需要知道「声明已删但未物理归还」的灰区大小
- 面试/告警中出现的经典困惑：「我明明删了 20GB，为什么 df 没变？」

**适用于**：所有采用「标记后回收」两阶段设计的系统——文件系统（TRIM/compact）、数据库（DELETE/VACUUM）、版本控制（branch删除/git gc）、内存（free()/GC）。

**不适用于**：即时回收语义的系统（如 tmpfs 删除即释放）；只关心逻辑视图不关心物理占用的场景（容量充裕）。

## 问题本质

为保性能与原子性，大量系统把「删除」实现为**元数据记账**（inode 释放、位图标记、版本指针摘除），物理回收被推迟给独立的低优先级机制（GC/TRIM/compaction）。由此产生三重认知鸿沟：

1. **声明与归还脱钩**：`trimmed 967GiB` 是文件系统视角的声明，宿主实际归还 0.1GB——两个数字来自不同层，语义完全不同
2. **记账的一次性**：删除时机的 TRIM 已把块记为未映射，重复 fstrim 无事可做（F-033）——「再跑一次」直觉失效
3. **容量观测的双标准**：`df` 显示逻辑用量，监控/计费看物理占用，两者差值 = 灰区，且灰区**不会自动收敛**

设计动机是合理的（每次删除同步物理回收代价不可承受），但运维者若不知道鸿沟存在，就会在「删了没变」时误判为故障或反复无效操作。

## 核心步骤（识别与治理）

1. **识别回收模型**：查目标系统的文档——删除是即时回收还是两阶段？第二阶段命令是什么（VACUUM/gc/compact/trim）？触发方式（手动/自动/阈值）？
2. **测灰区**：对比逻辑用量（df/`SHOW TABLE STATUS`/逻辑统计）与物理占用（文件大小/表空间/监控值），差值即待回收量
3. **显式回收**：执行该系统的第二阶段命令（注意频率与代价——VACUUM FULL 锁表、compact 需停机、GC stop-the-world）
4. **闭环验收**：回收后逻辑≈物理（本案例 vhdx 11.93GB = 内部 df 11.93GB 完全闭合，F-028）

## 反模式

| 反模式 | 后果 | 实证 |
|--------|------|------|
| ❌ 删除后盯 df 等待空间回来 | 永远等不到，误判系统故障 | F-016→F-020 |
| ❌ 重复执行回收命令（"再跑一次试试"） | 记账一次性，二次执行空转 | F-033 |
| ❌ 把 trimmed/GC 声明量当作实际归还量 | 容量规划系统性偏差（967GiB vs 0.1GB） | F-020 |
| ❌ 按逻辑用量规划物理容量 | 灰区持续累积，配额提前击穿 | F-004（三vhdx 92GB中约30GB灰区） |
| ❌ 无视回收命令的代价属性（锁/停机/STW） | 高峰期 VACUUM FULL/compact 造成生产事故 | 业界公知 |

## 失败案例（20260828 真实实证，防成功偏误）

| # | 失败尝试 | 现象 | 教训 |
|---|---------|------|------|
| 1 | 容器内删 21GB 后观察宿主 | C盘空间纹丝不动 | 删除仅是 ext4 元数据操作，需触发回收链 |
| 2 | sparse 转换后 fstrim | 仅归还 0.1GB | 记账一次性；sparse 只对**此后新产生**的 TRIM 生效 |
| 3 | sparse 状态下二次 fstrim | trimmed 1GB / 实际 0.1GB | 二次执行空转，「再试一次」直觉彻底失效 |
| 4 | 信任 trimmed 字节数 | 声明 967GiB 与实际 0.1GB 差 4 个数量级 | 各层数字语义不同，必须分层观测 |

> 四次失败共同结构：把「声明」当「归还」。最终 compact 一次回收 20.4GB（F-026），验证了鸿沟确实存在且可显式跨越。

## 不适用/反目标/边界场景（≥3类，防确认偏误）

| 类别 | 场景 | 不适用原因 |
|------|------|-----------|
| 反目标1 | 即时回收系统（tmpfs、大多数应用层数据结构） | 删除即物理释放，无鸿沟可治理 |
| 反目标2 | 容量充裕、无配额压力 | 灰区无害，显式回收的代价（停机/锁）反而是净损失 |
| 反目标3 | 逻辑视图即业务口径（报表按逻辑行数） | 业务语义上「删了就是删了」，物理占用无关 |
| 边界1 | 自动化回收系统（JVM GC、自愈型存储） | 鸿沟存在但自动收敛，人工干预仅限调优阈值 |
| 边界2 | 回收代价与写入速率同量级 | 高写入系统频繁 compact 得不偿失，应按频率-代价曲线定节奏 |
| 边界3 | 回收不可在线执行（需停机/锁） | 与维护窗口规划耦合，参照姊妹 SOP 的在线/离线二相决策 |

## 早期预警信号（≥5个）

| 信号 | 判定阈值 | 含义 |
|------|---------|------|
| 逻辑用量持续 < 物理占用且差值扩大 | 灰区 >15% | 存在待回收堆积 |
| 删除操作后容量指标零变化 | 确认即触发 | 系统采用两阶段回收 |
| 回收命令的声明量与指标变化不符 | 差 >2倍 | 声明≠归还，需物理层验证 |
| 监控告警容量击穿但 df 正常 | 双标准冲突 | 按 df 规划了物理容量 |
| 回收命令执行后物理占用快速回升 | 一轮写入-回收周期 | 回收节奏追不上写入速率，需治理写入源 |

## 跨场景迁移

| 系统 | 逻辑删除 | 物理回收 | 鸿沟代价 |
|------|---------|---------|---------|
| PostgreSQL | DELETE/UPDATE（标记死元组） | VACUUM / VACUUM FULL | 表膨胀、查询计划劣化 |
| git | branch -d / reflog 过期 | git gc --prune | .git 体积膨胀 |
| SQLite | DELETE | VACUUM | 文件不缩小（ freelists） |
| JVM/Python | 对象不可达 | GC mark-sweep/compaction | 内存占用高位、碎片 |
| Linux 内存 | free() | 页归还内核（madvise/allocator 触发） | RSS 不降 |
| WSL vhdx（本案例） | 客体内 rm | fstrim + compact | vhdx 单调膨胀 |

**本质**：任何「为性能把物理回收与逻辑删除解耦」的系统都内建了这条鸿沟。运维三问——**删除是记账吗？记账何时兑现？兑现的代价是什么？** 答不出这三问的容量规划都是赌博。

## 关联文档

- 复盘报告：[retrospective-c-drive-vhdx-recovery-20260828](../../../reports/environment-setup/retrospective-c-drive-vhdx-recovery-20260828/README.md)（洞察 I-3）
- 操作层实例（本模式案例1的完整 SOP）：[vhdx-two-phase-recovery-sop](../../process-patterns/vhdx-two-phase-recovery-sop.md)（含回收时机与代价的在线/离线二相决策）
- 姊妹模式：[mutual-exclusion-composability-precheck](../governance-strategy/mutual-exclusion-composability-precheck.md)（回收路径选择的互斥约束）
