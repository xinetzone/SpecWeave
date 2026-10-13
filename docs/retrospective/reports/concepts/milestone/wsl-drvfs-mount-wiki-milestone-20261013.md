---
id: wsl-drvfs-mount-wiki-milestone-20261013
title: WSL DrvFs 挂载「教程沉淀→实战挂载→fstab 持久化」一日闭环里程碑复盘报告（2026-10-13）
date: 2026-10-13
type: retrospective
source: 七概念方法论 R→I→E→V→A→C（场景1·里程碑复盘，standard；含场景4知识沉淀前置链与场景实操轻量链 I→V）
category: milestone
maturity: L1
tags: [方法论, 七概念, 里程碑复盘, WSL, drvfs, 网络共享, fstab, OKF-Wiki, Skill, 冷启动验证]
---

# WSL DrvFs 挂载「教程沉淀→实战挂载→fstab 持久化」一日闭环里程碑复盘报告

> **周期**：2026-10-13 下午（知识沉淀 → 实战 → 持久化 → 复盘，同日闭环）| **方法**：七概念 R→I→E→V→A→C（场景1 里程碑复盘，depth=standard）| **对象**：OKF 教程束 `docs/knowledge/tech/wsl-drvfs-mount-wiki/`（commit `13715e5c0`）+ `\\10.16.11.3\ai` 挂载实战 + fstab 持久化 + 项目 Skill `wsl-drvfs-mount` | **数据**：git 实测 + WSL 命令实测 + 本会话操作记录

---

## 一、事实（R · 复盘 · 纯客观，无判断词）

### 1.1 阶段 A：知识沉淀（教程提交，git 实测 `13715e5c0`）

| 项 | 数值/内容 | 验证方式 |
|----|----------|---------|
| 提交哈希 | `13715e5c065333a003ea5845b272e0c5b3edc343` | `git show` |
| 提交时间 | 2026-10-13 15:27:07 +0800 | `git show --format=%ad` |
| 变更规模 | 14 文件，+994 行（13 新增 + 索引 1 行） | `git show --stat` |
| 教程目录 | `docs/knowledge/tech/wsl-drvfs-mount-wiki/`（index/concepts 6 篇/references 3 篇/log 等 13 个 md，共 750 行） | 文件实测 |
| F-005（流程事实） | R 阶段登记 36 条编号事实（F-001～F-036），A/B/C 置信度分级，评论区单源内容隔离标注 | 教程 references/01-fact-ledger.md |
| F-006（流程事实） | I 阶段产出 4 条四元组洞察（drvfs 的设备是路径名 / 权限位是显示语义 / 凭据边界在 Windows 侧 / 能力曾与 build 绑定） | 教程概念篇交叉引用 |
| F-007（流程事实） | V 阶段 4 视角 8 条意见，采纳 5 条；含「2017 博文对 2026 读者时代错位」，据此补抓 wsl.conf、`wsl --mount`、跨文件系统指南 3 篇现行官方文档，新增 concepts/05 现代演进对照 | references/02-adversarial-review.md |
| 链接验证 | 85/85 本地引用有效，4 条外链均为微软官方域 | check-links.py 输出 |
| 注册 | `docs/knowledge/tech/index.md` toctree 增加 1 行 | `git show` |
| 提交编码 | 经 `git-commit-utf8.py` bytes 通道提交，`git cat-file -p HEAD` 验证中文无乱码，未推送 | 命令实测 |

### 1.2 阶段 B：实战挂载（\\10.16.11.3\ai → /mnt/ai）

| # | 事实 | 验证方式 |
|---|------|---------|
| F-011 | 目标 `\\10.16.11.3\ai`：TCP 445 在 3s 超时内 OPEN，ICMP ping 返回 True | TcpClient/Test-Connection |
| F-012 | `net view \\10.16.11.3` 返回 `Alg server (Samba, Ubuntu)`，共享清单含 ai/media/shared，ai 行 `Used as S:`，Comment 为 Home | net.exe 输出 |
| F-013 | net view 以当前 Windows 身份直接返回清单（exit 0），过程中无凭据提示 | 命令实测 |
| F-014 | `wsl -l -v`：openKylin-3.0（默认，WSL 2，Running）、podman-machine-default（WSL 2，Stopped） | wsl.exe 输出 |
| F-015 | 挂载以 root 执行：`mkdir -p /mnt/ai` 与 `mount -t drvfs S: /mnt/ai`，无报错 | wsl 命令实测 |
| F-016 | 挂载表条目：`S: on /mnt/ai type 9p (rw,relatime,aname=drvfs;path=S:;symlinkroot=/mnt/,cache=0x5,...)`，选项中无 uid/gid 映射 | `mount` 输出 |
| F-017 | `ls /mnt/ai` 输出 13 个条目（AGENTS.md、README.md、models、workspace、llm-distill、notebook 等） | `ls` 输出 |
| F-018 | root 身份 `touch /mnt/ai/.wsl-mount-probe` 成功并 rm，输出 WRITE_OK | 写探针实测 |
| F-019 | PowerShell 中裸名 `net.exe` 返回「术语不会被识别」（PATH 裁剪），改用 `$env:WINDIR\System32\net.exe` 全路径成功 | 错误输出+成功输出对照 |

### 1.3 阶段 C：fstab 持久化与冷启动实证

| # | 事实 | 验证方式 |
|---|------|---------|
| F-020 | 写入前 `/etc/fstab` 仅有占位行 `# UNCONFIGURED FSTAB FOR BASE SYSTEM`；`grep /mnt/ai` 无命中 | cat/grep 实测 |
| F-021 | `/etc/wsl.conf` 含 `[user] default = openkylin` 与 `[boot] systemd=true`，无 `[automount]` 段 | cat 实测 |
| F-022 | 写入前备份为 `/etc/fstab.bak.20261013`、`/etc/wsl.conf.bak.20261013` | cp 命令记录 |
| F-023 | fstab 追加 `S: /mnt/ai drvfs defaults,nofail 0 0`；命令带 `grep -qE` 幂等守卫 | 写入后 cat |
| F-024 | wsl.conf 追加 `[automount]` 段：`enabled=true`、`mountFsTab=true`，同样带段存在性守卫 | 写入后 cat |
| F-025 | `findmnt --verify --verbose`：`0 parse errors, 0 errors, 4 warnings`（unreachable source S: / drvfs seems unsupported by the current kernel / cannot detect on-disk filesystem type / systemd 旧版本提示） | findmnt 输出 |
| F-026 | `wsl --terminate openKylin-3.0` 返回操作成功，`wsl -l -v` 显示 Stopped；随后冷启动命令返回 BOOT_OK | wsl.exe 输出 |
| F-027 | 冷启动后挂载表自动出现 `S: on /mnt/ai type 9p (...)`；`C:\ on /mnt/c`、`D:\ on /mnt/d` 两条既有自动挂载同时存在 | `mount \| grep` |
| F-028 | 冷启动后以默认用户 openkylin（`id -un` 实测）执行 touch/rm 写探针成功 | 同 shell 实测 |
| F-029 | 当晚复盘前复测：挂载表 /mnt/ai 计数 1、fstab /mnt/ai 行数 1、`ls /mnt/ai` 条目数 13，三项均保持 | grep -c/wc 实测 |

### 1.4 工具链与流程事实

| # | 事实 | 验证方式 |
|---|------|---------|
| F-030 | `git-commit-utf8.py` 以目录为位置参数时 FAIL（「git add 后暂存区文件与指定列表不一致」，脚本按展开后文件逐项比对）；改为先显式 `git add` 再走「已暂存直接提交」分支成功 | 失败+成功双记录 |
| F-031 | 本会话全程 git 固定使用 `D:\Program Files\Git\mingw64\bin\git.exe`（PATH 前置），wsl 使用 `$env:WINDIR\System32\wsl.exe` 全路径并设 `WSL_UTF8=1` | 命令记录 |
| F-032 | WSL 内 apt/系统类命令统一 `export LC_ALL=C LANGUAGE=C`；本里程碑挂载命令不涉及 apt | 命令记录 |
| F-033 | 阶段 B 操作前先执行只读探测（wsl -l -v、TCP 445、ICMP、net view），未安装任何软件、未修改 WSL 内任何文件 | 操作序列 |
| F-034 | fstab/wsl.conf 写入合并在单次 root bash 调用内完成（备份+守卫+追加+回显），无中间半写状态 | 命令记录 |
| F-035 | 复盘时点检测：`.trae/skills/wsl-drvfs-mount` 不存在（无同名 Skill）；教程 13 文件 750 行 | Test-Path/行数统计 |
| F-036 | 主仓库工作区在教程提交后干净；fstab/wsl.conf 变更位于发行版 ext4.vhdx 内部，不产生主仓库 diff | git status |

> 事实计数：**30 条独立编号事实**（阶段 A 10 项表内事实按 F-005/F-006/F-007 等流程编号合并表述；阶段 B 9 条 F-011～F-019；阶段 C 10 条 F-020～F-029；工具链 7 条 F-030～F-036），全部附验证方式。

---

## 二、洞察（I · 四元组）

### 洞察 1：挂载网络共享的主要成本在凭据，而凭据常已在 Windows 侧闭合

- **陈述**：WSL drvfs 挂载 SMB 共享的潜在失败点集中于凭据；但 Windows 侧既有认证会话（持久映射盘、Credential Manager、域身份）是可直接复用的资产，挂载前一次只读探测即可把「配置凭据」整段跳过。
- **证据**：F-012（net view 显示 `Used as S:`）、F-013（当前身份直接通过）、F-015（挂载命令不含任何凭据参数）；教程 F 系列「凭据边界在 Windows 侧」在同日实战命中。
- **反常识**：直觉路径是「找用户名密码 → 研究 mount 凭据选项」；实战中凭据自始至终没有出现在 WSL 侧，挂载退化为一条命令。
- **行动**：挂载类任务第一步固定为只读探测既有会话（`net view`/`net use`/445 端口）；凭据配置仅在探测返回认证错误时启动。

### 洞察 2：挂载类操作的完成判据是三层独立证据，退出码零只覆盖第一层

- **陈述**：网络 drvfs 的错误常在首次 I/O 时暴露（延迟错误），`mount` 退出 0 后必须经「内核挂载表 → 目录列举非空 → 业务用户写探针」三层证据才算完成；持久化复验时第三层应换业务用户执行以覆盖权限语义。
- **证据**：F-016/F-017/F-018（手动挂载三层）；F-027/F-028（冷启动后三层重跑，写探针由 root 换为默认用户 openkylin）；F-016 挂载选项无 uid/gid 映射，使「root 能写≠业务用户能写」成为真实风险点。
- **反常识**：「命令没报错」通常被当作完成；本里程碑把成功标准提高到「默认用户对真实共享写入非空探针」。
- **行动**：所有挂载/映射类 SOP 固化三层验证；持久化场景强制补「terminate 冷启动后重跑三层」。

### 洞察 3：跨抽象层静态校验必然产生类型盲区噪音，验收权威必须切换到真实生命周期

- **陈述**：`findmnt --verify` 按内核块设备模型校验 fstab，对 WSL init 在用户态解析的 drvfs 源必报 unreachable/unsupported 类警告；此时判据是两行计数（parse errors=0、errors=0）+ 警告归类，最终权威是与生产同路径的冷启动实测，而非试图消除全部警告。
- **证据**：F-025（0/0/4 warnings 原文）；F-026/F-027（冷启动自动挂载成立且 C:/D: 既有挂载无回归）；教程 05 节已登记 drvfs 经 9p 用户态桥的实现事实。
- **反常识**：看到 warning 的本能是排查或改配置；任何「让 findmnt 满意」的改法（换内核设备名）都会把可用配置改坏。
- **行动**：使用静态校验器前先识别其对象模型；不匹配层的告警按已知清单降级并记录理由；终审证据选真实生命周期（terminate→冷启动）。

### 洞察 4：知识生产与消费的同日闭环是模式质量最快的检验回路

- **陈述**：上午按七概念沉淀的 drvfs 教程，下午即在真实挂载任务中被消费（凭据边界、权限显示语义均命中），实战又反向暴露出教程可补的示例与工具真实行为偏差；「沉淀→使用→反哺」在一日内闭环，使模式错漏暴露周期从周级缩到小时级。
- **证据**：F-005～F-007（教程的事实/洞察/修正结构）；F-012/F-015（实战直接复用教程结论，无凭据分支）；F-030（git-commit 工具「目录参数」行为与直觉不符，属待反哺的操作知识）。
- **反常识**：知识沉淀常被视为慢资产、价值在长期；本案例显示其首要当天价值是强制把操作假设显性化（探测先行、三层验证），直接改变了下午的操作序列。
- **行动**：每次知识沉淀后主动安排一次同域实弹任务；实战偏差当轮回写——本次以项目 Skill 承载 SOP，教程 examples 反哺登记为行动项 A-1。

---

## 三、对抗审查（V · 四视角）

| # | 视角 | 攻击点 | 处置 |
|---|------|--------|------|
| V1 | 魔鬼代言人 | S: 持久映射的证据只有一次 net view 快照；若该映射是登录时「断开的按需恢复」状态，冷启动后 drvfs 可能挂到空盘，而 nofail 把失败静默成空目录 | **采纳** → Skill 与模式卡把「ls 条目数 > 0」设为硬闸口，UNC 直挂列为备选；行动项 A-1 覆盖 |
| V2 | 魔鬼代言人 | 写探针仅 touch 空文件，无法暴露 SMB 级只读或「可创建不可写内容」的权限语义；root 探针更无法代表业务用户 | **采纳（一半当场已做）** → 冷启动复验已换默认用户 openkylin；Skill 升级探针为「业务用户写非空内容再读回」 |
| V3 | 新人视角 | fstab 写 `S:` 盘符不可移植，换机器/无映射盘即失效；给他人复现的文档答案应是 UNC 形式 | **采纳** → Skill 决策树写明盘符 vs UNC 选择条件，references 两形态并列；模式卡第2阶段成表 |
| V4 | 老板视角 | 「4 warnings 是预期噪音」若无机器化判别规则，后人会把真错误一并忽略 | **采纳** → 模式卡给出判别规则：只认两行计数 + 警告逐条核对三类已知 drvfs 抽象层项 |
| V5 | 未来视角 | WSL 版本演进（`wsl --mount`、systemd 接管挂载、mountFsTab 默认值变化）会使 SOP 漂移，需标注环境基线与漂移信号 | **采纳** → Skill 与模式卡标注基线（WSL 2/openKylin-3.0/systemd=true/2026-10-13）、不适用边界与 4 项升级验证场景 |
| V6 | 未来视角 | `/etc/*.bak.20261013` 备份长期残留于 /etc，成为垃圾且可能被配置扫描器误读 | 记录 → 行动项 A-3（稳定一个月后删除并复测） |
| V7 | 老板视角 | 用户只要「挂载」，是否过度生产了教程+报告+Skill 三类资产 | **不采纳**：三类资产分别来自用户三轮显式请求（生成 OKF 教程；挂载并追加 fstab 重启验证；里程碑复盘+导出文档+生成 Skill），每轮单一意图、范围未外溢；理由留痕 |

> V 门：意见 **7 条**（≥5），覆盖 4 视角，**采纳 5 条**（V1/V2/V3/V4/V5，其中 V2 的用户切换在阶段 C 已先行落地），满足「≥5 条且采纳 ≥2」。

---

## 四、模式萃取（E · 可迁移模式，L1-draft）

### 模式：WSL 网络共享 drvfs 挂载三段验证与幂等持久化法（WSL-DRVFS-MOUNT-001）

- **入库位置**：[tools-automation/wsl-network-share-drvfs-mount.md](../../../patterns/methodology-patterns/tools-automation/wsl-network-share-drvfs-mount.md)（伴生 TOML + 域 toctree + 主索引总表四处登记齐全）
- **触发场景**：WSL 2 访问 Windows 盘符/SMB 共享；共享在 Windows 侧已可访问；需要一次性挂载或 fstab 持久化。不适用于物理裸盘（`wsl --mount`）、NFS/对象存储、容器卷、WSL 1。
- **核心步骤（五阶段）**：① 环境冻结与只读探测（445/ICMP/net view 既有会话/挂载点查重）→ ② 源形态决策（持久盘符 vs UNC 单引号 vs NTFS 文件夹卷）→ ③ 挂载 + 三层验证（挂载表/目录非空/业务用户写读回）→ ④ 幂等持久化（备份 + grep 守卫 + `nofail` + 显式 automount 段）→ ⑤ terminate 冷启动实证 + 既有挂载回归。
- **反模式（6 条）**：上来在 WSL 侧找凭据；退出码 0 即宣布完成；fstab 无 nofail 且无守卫；试图消除 findmnt 全部 drvfs 警告；用 reboot/重启 Windows 代替发行版冷启动；把网络 drvfs 当 POSIX 文件系统放权限敏感负载。
- **检验标准**：7 项（探测留痕、三层证据、业务用户探针、nofail+守卫+备份、冷启动新旧挂载齐验、findmnt 计数判据、无凭据明文/无仓库污染）。
- **跨场景迁移**：CI 挂载对象存储（实例角色探测→list/read/写探针→干净 runner 复跑）、数据库客户端（.pgpass/SSO 探测）、容器对接宿主 daemon、OAuth 刷新令牌复用，共 4 个结构化推演场景。
- **成熟度**：**L1-draft**（单案例：本次 Samba 共享盘符路径）；升级 L2 的 4 个独立案例：UNC 直挂、需凭据分支、失败/断开路径、跨发行版。
- **关联模式**：验证探针语义收敛（三层探针的上位约束）、自动化幂等四要素、dry-run-first（只读探测即挂载前 dry-run）、能力前提配对搬运。

---

## 五、行动项（A · 原子化）

| # | 优先级 | 行动 | 验收标准 | Owner | 状态 |
|---|:---:|------|---------|-------|:---:|
| A-1 | 中 | 把本实战（S: 会话探测→三段验证→fstab 冷启动）补写为教程束 examples 页，并与 Skill 交叉链接；UNC 直挂作为无映射盘备选同页给出 | 教程新增 1 篇 example，链接检查通过，引用模式卡与 Skill | 维护者 | 待办（需独立一次提交） |
| A-2 | 高 | Skill v1.0 落地 V1/V2 修正：条目数硬闸口、业务用户非空写读回探针、盘符/UNC 决策表 | `.trae/skills/wsl-drvfs-mount/SKILL.md` 含三项且 references 命令签名完整 | 本任务 | ✅ 随里程碑交付 |
| A-3 | 低 | openKylin-3.0 稳定运行约一个月后删除 `/etc/fstab.bak.20261013`、`/etc/wsl.conf.bak.20261013` | 两备份不存在；terminate 冷启动后 /mnt/ai 自动挂载仍成立 | 维护者 | 待触发（2026-11 中旬） |
| A-4 | 中 | 模式 L1→L2：在 UNC 直挂/需凭据/断开失败/跨发行版四场景中补齐任一独立案例 | 第二个案例有完整三层证据并回写模式卡 Changelog | 维护者 | 待触发 |

---

## 六、质量门记录

| 门 | 检查项 | 结果 |
|:--:|--------|:--:|
| G1 | 事实无因果/判断词、数量 ≥20、逐条可验证 | ✅ 30 条（F-005～F-036 口径），全部附验证方式 |
| G2 | 洞察四元组完整（陈述/证据/反常识/行动）、数量 ≥3 | ✅ 4 条 |
| G3 | 模式含触发/步骤/≥3 反模式/检验/迁移，标注成熟度且四处登记 | ✅ 1 个 L1-draft（6 反模式、4 迁移场景） |
| G4 | 行动项单一职责/可验证/有 Owner/可独立交付 | ✅ 4 项（A-2 本次闭环，其余带触发条件） |
| V 门 | 意见 ≥5、覆盖 4 视角、采纳 ≥2 且有修正痕迹 | ✅ 7 条 / 采纳 5 条，修正落入模式卡与 Skill |

---

## 七、交付物清单（本次复盘伴随产出）

| 交付物 | 路径 | 形态 |
|---|---|---|
| 本报告 | `docs/retrospective/reports/concepts/milestone/wsl-drvfs-mount-wiki-milestone-20261013.md` | 里程碑复盘 |
| 方法论模式卡 | `docs/retrospective/patterns/methodology-patterns/tools-automation/wsl-network-share-drvfs-mount.md`（+ 伴生 TOML + 两处索引） | L1-draft 模式 |
| 独立可发布版 | `docs/retrospective/reports/exported/wsl-drvfs-mount-wiki-milestone-retrospective-20261013-v1.0.md`（+ manifest） | 导出报告 |
| 项目 Skill | `.trae/skills/wsl-drvfs-mount/SKILL.md` + `references/command-map.md` | 可触发 SOP |
| 前置知识资产 | `docs/knowledge/tech/wsl-drvfs-mount-wiki/`（commit `13715e5c0`，已于当日下午提交） | OKF 教程 |

---

> **报告编制**：本文档由七概念方法论 R→I→E→V→A→C 链路生成；事实均标注验证命令或来源文件，结论可追溯至事实编号；系统文件变更（fstab/wsl.conf）位于 openKylin-3.0 发行版内部，主仓库仅新增文档类资产。
> **链路**：R（30 条三阶段实测事实）→ I（4 四元组洞察）→ V（4 视角 7 意见采纳 5）→ E（WSL-DRVFS-MOUNT-001，L1-draft，四处登记）→ A（4 行动项，A-2 随交付闭环）→ C（待用户指令后原子提交）。
