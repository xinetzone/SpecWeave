---
type: Report
title: "WSL DrvFs 挂载「教程沉淀→实战挂载→fstab 持久化」一日闭环里程碑复盘"
date: 2026-10-13
archived: 2026-10-13
scenario: milestone
methodology: seven-concepts R→I→E→V→A→C
session: sc-20261013-wsl-drvfs-mount
scope: task
status: archived
topic: wsl-drvfs-mount
version: v1.0
---

# WSL DrvFs 挂载「教程沉淀→实战挂载→fstab 持久化」一日闭环里程碑复盘

## 执行摘要

2026-10-13 一个工作日内，围绕 WSL 跨文件系统访问完成三个阶段的闭环：

1. **知识沉淀**：基于微软官方 2017 年归档博文（Windows Insider build 16176）按七概念场景 4 链路生成 OKF 教程束（13 篇 / 750 行，commit `13715e5c0`，+994 行）；V 阶段补入三篇现行官方文档，将历史史实与现代 WSL 行为分离。
2. **实战挂载**：下午即用教程结论把 Samba 共享 `\\10.16.11.3\ai` 挂入 openKylin-3.0（WSL 2）。一次只读探测发现该共享在 Windows 侧早已认证并映射为 S: 盘，凭据段整段跳过，挂载退化为一条命令。
3. **持久化**：fstab 幂等写入（备份 + grep 守卫 + `nofail`）+ wsl.conf 显式 automount 段，`findmnt --verify` 以「0 parse errors / 0 errors」判过（4 条警告确认为跨抽象层噪音），`wsl --terminate` 冷启动实证自动挂载、业务用户读写、既有 C:/D: 挂载全部正常。

同步产出：方法论模式 **WSL-DRVFS-MOUNT-001**（L1-draft，完成模式库四处登记）与项目级 Skill `wsl-drvfs-mount`。

| 指标 | 值 |
|---|---|
| 教程提交 | `13715e5c0`，14 文件 +994 行，13 篇 md / 750 行 |
| 教程方法论数据 | 36 条编号事实、4 条洞察、V 阶段 8 意见采纳 5 |
| 挂载目标 | `\\10.16.11.3\ai`（Samba on Ubuntu）→ `/mnt/ai`，13 个条目 |
| 持久化 | fstab 1 行 + wsl.conf 3 行；冷启动实证通过 |
| 本报告事实 | 30 条（F-005～F-036 口径，三阶段分组） |
| 核心洞察 | 4 条（四元组完整） |
| 对抗审查 | 4 视角 7 条意见，采纳 5 条 |
| 可复用模式 | 1 个 L1-draft（6 反模式、4 迁移场景） |
| 质量门 | G1✅ G2✅ G3✅ G4✅ V门✅ |

---

## 1. 客观事实清单（R 阶段）

> G1 门：以下事实均为工具输出或本会话操作记录，推断性表述统一移至第 2 节。

### 1.1 阶段 A：知识沉淀（git 实测 `13715e5c0`）

| # | 事实 |
|---|---|
| F-001 | 提交 `13715e5c0`，时间 2026-10-13 15:27:07 +0800，14 文件 +994 行（13 新增 + tech 索引 1 行） |
| F-002 | 新目录 `docs/knowledge/tech/wsl-drvfs-mount-wiki/`，13 个 md 共 750 行（index、concepts 6 篇、references 3 篇、log 等） |
| F-003 | 信源为微软官方归档博文（2017-04，build 16176）；V 阶段补抓 wsl.conf、`wsl --mount`、跨文件系统指南三篇现行官方文档 |
| F-005 | R 阶段 36 条编号事实，A/B/C 置信度分级，博客评论区单源内容隔离标注 |
| F-006 | I 阶段 4 条洞察：drvfs 的设备是路径名、权限位是显示语义、凭据边界在 Windows 侧、能力曾与 Insider build 强绑定 |
| F-007 | V 阶段 8 条意见采纳 5 条；「2017 博文时代错位」修正落地为 concepts/05 现代演进对照 |
| F-008 | 链接检查 85/85 本地引用有效，4 条外链均为微软官方域 |
| F-009 | `docs/knowledge/tech/index.md` toctree 注册 1 行；提交经 UTF-8 bytes 通道，cat-file 验证无乱码，未推送 |

### 1.2 阶段 B：实战挂载

| # | 事实 |
|---|---|
| F-011 | TCP 445 对 10.16.11.3 在 3s 内 OPEN；ICMP ping True |
| F-012 | `net view` 返回 `Alg server (Samba, Ubuntu)`，共享 ai/media/shared；ai 行标注 `Used as S:`、Comment 为 Home |
| F-013 | net view 以当前 Windows 身份直接成功（exit 0），无凭据提示 |
| F-014 | WSL 形态：openKylin-3.0（默认，WSL 2，Running）、podman-machine-default（Stopped） |
| F-015 | root 执行 `mkdir -p /mnt/ai` 与 `mount -t drvfs S: /mnt/ai`，无报错，命令不含凭据参数 |
| F-016 | 挂载表：`S: on /mnt/ai type 9p (rw,relatime,aname=drvfs;path=S:;...)`，选项无 uid/gid 映射 |
| F-017 | `ls /mnt/ai` 输出 13 条目（AGENTS.md、models、workspace、llm-distill、notebook 等） |
| F-018 | root 写探针 touch+rm 成功（WRITE_OK） |
| F-019 | 裸名 `net.exe` 在受管 PowerShell 不可识别（PATH 裁剪），`$env:WINDIR\System32\net.exe` 全路径成功 |

### 1.3 阶段 C：fstab 持久化与冷启动实证

| # | 事实 |
|---|---|
| F-020 | 写入前 fstab 仅占位注释；grep `/mnt/ai` 无命中（查重通过） |
| F-021 | wsl.conf 原有 `[user] default=openkylin`、`[boot] systemd=true`，无 `[automount]` 段 |
| F-022 | 写入前备份 `/etc/fstab.bak.20261013`、`/etc/wsl.conf.bak.20261013` |
| F-023 | fstab 追加 `S: /mnt/ai drvfs defaults,nofail 0 0`，带 grep 幂等守卫 |
| F-024 | wsl.conf 追加 `[automount] enabled=true / mountFsTab=true`，带段存在性守卫 |
| F-025 | `findmnt --verify`：0 parse errors、0 errors、4 warnings（源不可达/内核不识别 drvfs/探测不到盘类型/systemd 旧版提示） |
| F-026 | `wsl --terminate openKylin-3.0` 后 Stopped，冷启动返回 BOOT_OK |
| F-027 | 冷启动后挂载表自动出现 /mnt/ai 条目，且 /mnt/c、/mnt/d 既有自动挂载并存（无回归） |
| F-028 | 冷启动后以默认用户 openkylin（`id -un` 实测）touch/rm 探针成功 |
| F-029 | 当晚复测：挂载表计数 1、fstab 行数 1、目录条目数 13，均保持 |
| F-030 | `git-commit-utf8.py` 传目录参数时暂存区一致性校验 FAIL；先显式 git add 再走暂存区分支成功 |
| F-033 | 阶段 B 先做四项只读探测再挂载，未安装软件、未改文件；F-034 fstab/wsl.conf 写入在单次 root 调用内原子完成；F-036 系统文件变更在 ext4.vhdx 内，主仓库无 diff |

---

## 2. 核心洞察（I 阶段，四元组）

### 洞察 1：挂载网络共享的主要成本在凭据，而凭据常已在 Windows 侧闭合

- **证据**：F-012（已映射 S:）、F-013（当前身份直接通过）、F-015（挂载无凭据参数）；同日上午教程的「凭据边界在 Windows 侧」结论下午即命中。
- **反常识**：直觉是先找用户名密码与挂载凭据选项；实战中凭据从未出现在 WSL 侧。
- **建议**：挂载类任务第一步固定为只读探测既有会话；凭据配置仅在认证错误时启动。

### 洞察 2：完成判据是三层独立证据，退出码零只覆盖第一层

- **证据**：F-016/F-017/F-018（手动挂载三层）；F-027/F-028（冷启动重跑且换业务用户写）；F-016 无 uid/gid 映射使 root 可写不代表业务用户可写。
- **反常识**：「没报错」常被当作完成；网络文件系统错误延迟到首次 I/O，断开映射会静默呈现空目录。
- **建议**：固化「挂载表 → 目录非空 → 业务用户写读回」三段验证；持久化必须 terminate 冷启动后重跑。

### 洞察 3：跨抽象层静态校验必然产生类型盲区噪音

- **证据**：F-025（findmnt 0/0/4）；F-026/F-027（冷启动证明配置有效）。findmnt 按内核块设备模型工作，drvfs 源由 WSL init 用户态解析。
- **反常识**：看到 warning 就想消除；任何迎合校验器的改名都会破坏可用配置。
- **建议**：只认两行计数 + 警告按已知三类清单归类；终审选与生产同路径的冷启动证据。

### 洞察 4：知识生产与消费的同日闭环是模式质量最快的检验回路

- **证据**：F-005～F-007 的教程结构；F-012/F-015 的当天复用；F-030 暴露出教程之外的工具行为偏差。
- **反常识**：知识沉淀被视为慢资产；其当天价值在于强制假设显性化（探测先行、三层验证），直接改变下午操作序列。
- **建议**：每次沉淀后主动安排同域实弹；偏差当轮回写（本次以 Skill 承载，教程 examples 登记为 A-1）。

---

## 3. 对抗审查（V 阶段，四视角）

| # | 视角 | 攻击点 | 处置 |
|---|------|--------|------|
| V1 | 魔鬼代言人 | S: 可能是断开的按需映射，nofail 会把失败静默为空目录 | 采纳：条目数 >0 设硬闸口，UNC 为备选 |
| V2 | 魔鬼代言人 | root + 空文件探针不能代表业务用户与真实写权限 | 采纳：冷启动已换 openkylin；探针升级为非空写读回 |
| V3 | 新人 | 盘符 fstab 不可移植，复现文档应给 UNC 形式 | 采纳：决策表 + references 两形态并列 |
| V4 | 老板 | 「预期噪音」无机器化判别规则会被泛化滥用 | 采纳：两行计数 + 三类已知警告清单 |
| V5 | 未来 | WSL 演进可致 SOP 漂移 | 采纳：标注环境基线、不适用边界、4 个升级场景 |
| V6 | 未来 | /etc 内 .bak 长期残留 | 记录：A-3，稳定一月后删除复测 |
| V7 | 老板 | 是否过度生产 | 不采纳：三类资产对应三轮显式用户请求，逐轮单一意图 |

V 门：7 条 ≥5，采纳 5 条 ≥2。

---

## 4. 模式萃取：WSL-DRVFS-MOUNT-001（L1-draft）

**五阶段 SOP**：① 只读探测（445/ICMP/net view 既有会话/挂载点查重）→ ② 源形态决策（持久盘符 / UNC 单引号 / NTFS 文件夹卷）→ ③ 挂载 + 三层验证（表/非空/业务用户写读回）→ ④ 幂等持久化（备份 + grep 守卫 + nofail + 显式 automount）→ ⑤ terminate 冷启动实证与既有挂载回归。

**6 条反模式**：上来在 WSL 侧找凭据；退出码 0 即收工；fstab 无 nofail 无守卫；迎合 findmnt 消除全部警告；用 reboot/重启 Windows 代替发行版冷启动；把网络 drvfs 当 POSIX 文件系统放权限敏感负载。

**L1→L2 升级场景**：UNC 直挂、需凭据分支、断开/失败路径、跨发行版，任一独立案例补齐即升级。

模式全文：[wsl-network-share-drvfs-mount](../../patterns/methodology-patterns/tools-automation/wsl-network-share-drvfs-mount.md)
配套教程：[wsl-drvfs-mount-wiki](../../../knowledge/tech/wsl-drvfs-mount-wiki/index.md)
完整报告（含 30 条事实验证方式与交付清单）：[里程碑归档版](../concepts/milestone/wsl-drvfs-mount-wiki-milestone-20261013.md)

---

## 5. 行动项与质量门

| # | 优先级 | 行动 | 状态 |
|---|:---:|------|:---:|
| A-1 | 中 | 实战案例反哺教程 examples（含 UNC 备选），与 Skill 交叉链接 | 待办（独立提交） |
| A-2 | 高 | Skill 落地 V1/V2 修正（条目数闸口/业务用户探针/盘符-UNC 决策表） | ✅ 随本里程碑交付 |
| A-3 | 低 | 稳定一月后删除两个 .bak.20261013 并冷启动复测 | 待触发 |
| A-4 | 中 | 补第二个独立案例推动模式升 L2 | 待触发 |

| 门 | 结果 |
|:--:|:--:|
| G1 事实 ≥20 无因果词、可验证 | ✅ 30 条 |
| G2 四元组洞察 ≥3 | ✅ 4 条 |
| G3 模式含触发/步骤/6 反模式/检验/迁移，四处登记 | ✅ L1-draft |
| G4 行动项单一职责可验证 | ✅ 4 项 |
| V 门 ≥5 意见、4 视角、采纳 ≥2 | ✅ 7 条 / 采纳 5 |

---

> 导出说明：本文件为独立可发布版（v1.0），由里程碑归档报告导出，事实与数据同源；系统文件变更位于 openKylin-3.0 的 ext4.vhdx 内部，仓库侧仅新增文档类资产。
