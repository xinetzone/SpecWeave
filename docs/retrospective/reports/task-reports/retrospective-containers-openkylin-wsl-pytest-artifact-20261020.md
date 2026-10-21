---
id: retrospective-containers-openkylin-wsl-pytest-artifact-20261020
title: ".temp/openkylin-wsl-pytest 产物目录存续价值复盘与保守档简化"
type: task-retrospective
date: 2026-10-20
updated: 2026-10-20
revision: r1
status: final
methodology: seven-concepts (R-I-E-C-A-F-V)
scenario: composite (knowledge-sedimentation + refactor-optimization)
scenario_chain: "R → I → E → F → A → V → C"
depth: standard
session: sc-20261020-openkylin-wsl-pytest-artifact
related_report: retrospective-containers-openkylin-wsl-pytest-20261019
source:
  - "/mnt/ai/.temp/openkylin-wsl-pytest/（Linux 侧 /media/pc/data/ai/.temp/openkylin-wsl-pytest/，UNC \\10.16.11.3\ai\.temp\openkylin-wsl-pytest）"
  - "/mnt/ai/.temp/openkylin-wsl-pytest/wsl-test-logs/{env.sh,r4_full.sh,setup_venv.sh,setup_venv.log,install_deps.sh,deps_prepare.sh,download.sh}"
  - "/mnt/ai/.temp/openkylin-wsl-pytest/wsl-venv314/{pyvenv.cfg,.gitignore,bin/python3.14}"
  - "/mnt/ai/.temp/_index.md"
  - "/mnt/ai/.temp/_tools/driver-rewritten-list.txt"
  - ".trae/specs/validate-containers-openkylin-wsl/{spec.md,checklist.md}"
path_migration: "本报告证据路径的整理台账见 .temp/_index.md；wsl-* 条目已于 2026-10-19 整体下移至 .temp/openkylin-wsl-pytest/，正文按复核时的现状路径书写"
evidence_path_migration: "同 2026-10-19 报告：/mnt/ai/.temp/wsl-* → /mnt/ai/.temp/openkylin-wsl-pytest/wsl-*"
tags:
  - temp-directory
  - artifact-governance
  - minimal-reproducible-set
  - supply-chain-collapse
  - venv
  - pycache
  - offline-rebuild
  - assertive-fs-ops
---

# .temp/openkylin-wsl-pytest 产物目录存续价值复盘与保守档简化

> 报告定位：本轮聚焦「**产物目录的存续价值与形态冗余**」，与 2026-10-19 的[权威测试复盘报告](retrospective-containers-openkylin-wsl-pytest-20261019.md)（聚焦「四成员 pytest 在 9p/drvfs 上的可跑通性」）**并列互补、不覆盖**。前者回答「这套测试能不能跑通」，本报告回答「跑通之后留下的这堆东西，哪些必须留、哪些该坍缩」。
>
> 场景链路：`R → I → E → F → A → V → C`（知识沉淀 R→I→E 与重构优化 I→F→A→V→C 的复合；V 强制）。

---

## 一、任务概览

**对象**：`\\10.16.11.3\ai\.temp\openkylin-wsl-pytest\`（5,149 文件 / 413 目录 / 435,754,689 字节）。

**任务五项**：全面复盘 + 萃取 + 洞察 + 导出报告 + 简化（保守档）。

**结论一句话**：该目录的 435.8 MB 中，**96.6% 是「同一资产的多形态冗余」或纯派生缓存**；以「再生依赖图 + 最小可复现集（支配集）」为单位坍缩后，删除与权威复跑路径无关的 venv 死路分支与全部编译缓存，回收 **93,298,489 字节（约 93.3 MB）**，「即时复跑」与「离线重建」两套能力均完整保留，零误删。

---

## 二、场景识别与链路裁决

| 候选场景 | 是否命中 | 依据 |
|---|---|---|
| 里程碑复盘（R→I→E→A→C） | 部分 | 有事实盘点与洞察萃取，但不止于沉淀 |
| 知识沉淀（R→I→E→V→C） | 命中 | 需把「产物形态坍缩」提炼为可复用模式并入库 |
| **重构优化（I→F→A→V→C）** | **命中** | 需对产物目录做「存续价值取舍」的简化，V 强制 |

**裁决**：复合场景，合并链路 = `R → I → E → F → A → V → C`，**V 门强制**。不强行添加创新突破的 F→V→I→C 分支，因为本任务无「造新东西」诉求；F 仅作为「取舍标准的第一性推导」出现。

---

## 三、事实清单（R / G1）

> ≥20 条客观事实，不含因果词。删除前态数据在同一次 PowerShell 会话内一次性冻结（F-003），删除后态为执行后实测（F-031）。

| 编号 | 事实 |
|---|---|
| F-001 | 目标目录位于 UNC `\\10.16.11.3\ai\.temp\openkylin-wsl-pytest`，Linux 侧对应 `/mnt/ai/.temp/openkylin-wsl-pytest` |
| F-002 | 删除前含 7 个一级条目：`wsl-py314`、`wsl-spk`、`wsl-test-logs`、`wsl-tmp`、`wsl-venv314`、`wsl-wheels`、`verify_xc_kernel.py` |
| F-003 | 删除前全量：文件 **5,149** / 目录 **413** / 字节 **435,754,689** |
| F-004 | 全部条目 mtime 落于 2026-10-19 13:24–21:29（单日区间） |
| F-005 | `wsl-py314` 删除前 4,051 文件 / 261,797,547 字节（占 60.1%） |
| F-006 | `wsl-tmp` 20 项 / 75,506,139 字节，其中 `cpython314.tar.gz` 为 75,066,232 字节 |
| F-007 | `wsl-venv314` = 3 文件 + 6 目录，合计 78,298,359 字节 |
| F-008 | `wsl-venv314` 文件构成：`.gitignore`(69) + `pyvenv.cfg`(338) + `bin/python3.14`(78,297,952) |
| F-009 | `wsl-venv314` 的 6 个目录：`bin`、`include`、`lib`、`lib64`、`lib/python3.14`、`lib/python3.14/site-packages` |
| F-010 | `wsl-venv314/lib/python3.14/site-packages` 目录内文件数 = 0 |
| F-011 | `pyvenv.cfg` 记录：`home = .../wsl-py314/python/bin`、`include-system-site-packages = false`、`version = 3.14.8` |
| F-012 | `setup_venv.log` L2 记录 `Errno 1] Operation not permitted: '.../wsl-venv314/bin/python3.14'` |
| F-013 | `setup_venv.log` L4/L6/L8 记录 `.../wsl-venv314/bin/python: No such file or directory` |
| F-014 | `env.sh` 中 `PYBIN=/mnt/ai/.temp/openkylin-wsl-pytest/wsl-py314/python/bin/python3.14`，`PYTHONPATH` 含 `wsl-spk` |
| F-015 | `r4_full.sh` 中 `PYBIN=wsl-py314/python/bin/python3.14`，`PYTHONPATH` 含 `wsl-spk` |
| F-016 | `_tools/driver-rewritten-list.txt` 共 54 行，第 54 行 = `.../wsl-venv314/pyvenv.cfg` |
| F-017 | `venv314` 文本命中：`.temp` 内 10 行、`.trae` 内 5 行；`.agents` 与 `docs/` 内 0 行 |
| F-018 | `__pycache__`：113 目录 / 816 文件 / **15,000,130** 字节；非 `.pyc` 文件数 = 0 |
| F-019 | `__pycache__` 分布：`wsl-py314` 74/534/10,337,133；`wsl-spk` 38/281/4,660,592；`wsl-test-logs` 1/1/2,405 |
| F-020 | `__pycache__` 无任何指向本目录实例的外部悬空引用（`.agents` 仅 `census.sh:55` 的排除模式） |
| F-021 | `wsl-wheels` 14 个 wheel / 3,302,750 字节（certifi、charset_normalizer、idna、iniconfig、invoke、packaging、pluggy、podman、Pygments、pytest、python_dotenv、pyyaml、requests、urllib3） |
| F-022 | `wsl-spk` 删除前 942 文件 / 16,205,396 字节（wheel 解包安装树） |
| F-023 | `wsl-test-logs` 删除前 118 文件 / 642,997 字节（原版复跑脚本与轮次日志） |
| F-024 | 再生关系一：`cpython314.tar.gz` 经 `download.sh`（`tar -xzf`）产出 `wsl-py314` |
| F-025 | 再生关系二：`wsl-wheels/*.whl` 经 `deps_prepare.sh`（`zipfile.extractall`）产出 `wsl-spk` |
| F-026 | 2026-10-19 报告 A-08 的保护集 = {`wsl-py314`, `wsl-test-logs`, `wsl-tmp`}，不含 `wsl-venv314`/`wsl-spk`/`wsl-wheels` |
| F-027 | 2026-10-19 报告末注链路 = R→I→E→V→C，模式 = `constrained-fs-test-supply`（L1） |
| F-028 | `.temp/_index.md` L41 登记 `wsl-venv314 → openkylin-wsl-pytest/wsl-venv314`，体量记为 78,298,524 |
| F-029 | `.temp/_index.md` L7 载明「任何删除动作需人类批准」 |
| F-030 | `/media/pc/data` 卷 15T 已用，剩余 345G（约 98% 占用） |
| F-031 | 删除后全量：文件 **4,330** / 目录 **293** / 字节 **342,456,200** |
| F-032 | 删除动作实测输出：`PYCACHE_DELETED=113`、`PYCACHE_FAIL=0`、`VENV_DELETED=OK` |
| F-033 | 删除后保留集实测：`wsl-py314` 3517/251,460,414；`wsl-spk` 661/11,544,804；`wsl-test-logs` 117/640,592；`wsl-tmp` 20/75,506,139；`wsl-wheels` 14/3,302,750；`verify_xc_kernel.py` 1/1,501 |
| F-034 | 字节差额核验：435,754,689 − (15,000,130 + 78,298,359) = **342,456,200**，与 F-031 实测精确相等 |
| F-035 | 删除后入口存在性：`wsl-py314/python/bin/python3.14` = True；`wsl-test-logs/env.sh` = True；`wsl-test-logs/r4_full.sh` = True；`wsl-tmp/cpython314.tar.gz` = True |
| F-036 | 删除后 `setup_venv.sh`、`install_deps.sh` 仍存在 |
| F-037 | 删除方式：PowerShell `[System.IO.Directory]::Delete(path, $true)`（不经回收站） |
| F-038 | 该挂载 9p/drvfs 语义（前序已证）：`chmod`/`utime`/`symlink` 返回 `Errno 1`；权限位读回恒 `0o777`；普通文件读写增删正常 |

**G1 判定：通过**（38 条 ≥ 20；清单内剔除因果词，因果留给第四节洞察）。

---

## 四、洞察（I / G2）

> 四元组格式：**陈述 / 证据 / 反常识 / 行动**。≥3 条。

### I-01：解释器三形态并存，其中两个形态对本目录用途毫无贡献

- **陈述**：同一份 CPython 3.14 在目录中以三形态并存，且存在一个已废弃的死路形态。
- **证据**：源归档 `wsl-tmp/cpython314.tar.gz`(75,066,232) + 解包树 `wsl-py314`(261,797,547) + `venv --copies` 副本 `wsl-venv314`(78,298,359) = 415,162,138 字节（F-005/F-006/F-007）；其中 `wsl-venv314` 的 `site-packages` 为空（F-010），`setup_venv.log` 留有创建失败证据（F-012/F-013），权威路径 `env.sh`/`r4_full.sh` 均不引用它（F-014/F-015）。
- **反常识**：直觉上「多一份更保险」；实际 `wsl-venv314` 既不提供依赖（空 site-packages）、也不被任何活跃脚本引用，是**纯粹的体量成本**。78.3 MB 里 99.999% 只是一个被复制出来的解释器二进制。
- **行动**：删除 `wsl-venv314`（理由为「无消费者 + 死路分支」，而非「可再生」）。

### I-02：派生形态的可再生关系散落在脚本里，磁盘上没有关系标记

- **陈述**：`wsl-py314`←`cpython314.tar.gz`、`wsl-spk`←`wsl-wheels` 两条再生关系只存在于 `download.sh`/`deps_prepare.sh` 的代码里，目录本身无任何机器可读的「源→命令→派生」标注。
- **证据**：F-024/F-025 的再生关系需阅读脚本才能发现；`wsl-wheels`（3.1 MB）与 `wsl-spk`（11.0 MB）并列堆在同一层（F-021/F-022），无来源说明。
- **反常识**：人们以为「东西都在一个目录里当然看得懂」；实际面对 5,149 个文件时，**没有关系标记就等于不可裁决**——这正是需要先做再生依赖图的原因。
- **行动**：在产物目录落盘契约中要求登记「源 → 命令 → 派生」三元组（本报告与模式 ARTIFACT-COLLAPSE-001 已承担此角色）。

### I-03：证据/驱动与运行时解包树混放，使「敢不敢动」变成猜谜

- **陈述**：`wsl-test-logs/`（脚本+日志，类证据）与 `wsl-py314`/`wsl-spk`（运行时解包树）平级混放，导致清理时必须先弄清「哪些是证据、哪些是运行时」。
- **证据**：F-002 的 7 个一级条目中，证据（`wsl-test-logs`）与运行时（`wsl-py314`、`wsl-spk`）同层；`driver-rewritten-list.txt`（F-016）单独放在 `.temp/_tools/`，与产物本体分离。
- **反常识**：混放看似「东西集中好找」；实际它**抬高了删除决策的不确定性**——因为删运行时可能连带影响证据的可复跑性解读。
- **行动**：试管场景下把「证据层」与「运行时层」显式分层或加命名前缀；证据层不参与再生图（模式第6步）。

### I-04：产物目录缺「形态与最小可复现集」的文件，空间回收被误判为「风险动作」

- **陈述**：因为目录没有一张「哪些是源、哪些是派生、删派生后靠什么恢复」的清单，任何清理都被默认当作高风险而推迟。
- **证据**：`.temp/_index.md` L89-96 把 `__pycache__`（15,000,130 字节，F-018，纯可再生）与 `cpython314.tar.gz`（离线唯一副本）**并列登记为「未批准，仅登记」候选**（F-028 同区），并注明删除需人类批准（F-029）。
- **反常识**：直觉认为「谨慎就是都不动」；实际**把高可再生项与不可再生项并列搁置，等于用同一套高门槛对待两类完全不同的资产**，结果是可回收的长期压着不回收（F-030：卷已 98%）。
- **行动**：引入「最小可复现集」判据，把「派生层（可删）」与「唯一副本（必保）」分档，前者不再套用人工批准的高门槛。

### I-05：离线复现能力与体量呈张力，但张力点其实只在「源」而非「派生」

- **陈述**：目录同时承载「即时复跑」与「离线重建」两种能力；张力看似是「体积 vs 能力」，实际只在少数源文件上。
- **证据**：即时复跑依赖 `wsl-py314`+`wsl-spk`+`wsl-test-logs`（F-014/F-015/F-035）；离线重建依赖 `cpython314.tar.gz`+`wsl-wheels`+驱动器（F-024/F-025）。删除的 `wsl-venv314`/`__pycache__` 不在任何一套最小集中。
- **反常识**：以为「省空间就要牺牲离线能力」；实际两套能力的最小集交叠很小，**真正不可碰的只有源归档与 wheel 集**，其余派生形态完全可以坍缩。
- **行动**：以「删除后两套最小集至少一套完整」为无损上界执行坍缩（本报告第七节 ACT-01/ACT-02）。

**G2 判定：通过**（5 条 ≥ 3，均为完整四元组）。

---

## 五、萃取（E / G3）

### 5.1 提炼的模式

| 项 | 内容 |
|---|---|
| 模式名 | **同源产物形态坍缩法**（`artifact-form-collapse` / `ARTIFACT-COLLAPSE-001`） |
| 落盘位置 | [artifact-form-collapse.md](../../patterns/methodology-patterns/governance-strategy/artifact-form-collapse.md) |
| 索引登记 | `patterns/methodology-patterns/governance-strategy/index.md`（字母序，位于 `architecture-over-algorithm` 与 `asset-reuse-last-mile-integration-guide` 之间） |
| 成熟度 | L1-draft（单案例；validation_count=1） |
| 核心 | 处置单位从「条目」上升到「形态」，从「分类」上升到「再生关系」：再生依赖图 + 最小可复现集（支配集） |

**模式要点（六步）**：① 全量普查只记事实 → ② 逐子树体量定位「大形态」→ ③ 标注可再生物（登记再生命令）→ ④ 识别唯一副本与死路分支 → ⑤ 构建再生依赖图求支配集（隐式区分「即时复跑集 / 离线重建源集」）→ ⑥ 按源层/派生层/证据层/死路层分层处置 + 断言式执行验收。

### 5.2 反模式（6 条，均入库）

| 编号 | 反模式 | 本案例对应 |
|---|---|---|
| AP-01 | 同一资产多形态并存而不标注关系 | `cpython314.tar.gz`/`wsl-py314`/`wsl-venv314` 三形态无标注 |
| AP-02 | 把派生形态当独立条目逐一分诊 | 5,149 文件若逐条裁决则不可行 |
| AP-03 | 把「可再生」当作「可删」的充分条件 | 离线时 `cpython314.tar.gz` 可「被远程重下」但代价高，属必保 |
| AP-04 | 把可再生缓存纳入存量盘点/交付 | `__pycache__` 15,000,130 字节被混入总账 |
| AP-05 | 证据与驱动混放于运行时目录 | `wsl-test-logs` 与 `wsl-py314`/`wsl-spk` 同层 |
| AP-06 | 删除前不做最小可复现集判定与唯一副本检查 | `.temp/_index.md` 曾把可再生的 `__pycache__` 与唯一副本并列搁置 |

### 5.3 与既有模式的划界（防重复，已逐条核验）

| 既有模式 | 判定 | 划界论据 |
|---|---|---|
| `temp-directory-recoverability-triage`（TEMP-TRIAGE-001） | **不重复，互补可串联** | 它是**条目型横向分诊**（条目间无关系假设，逐条按可再生方式分 A–D 组 + E 裁决组）；本模式是**关系型纵向坍缩**（单位是一个逻辑资产跨多形态，做再生依赖图 + 支配集）。串联：先用 TEMP-TRIAGE 分可删/在途组，再用本模式在「同资产多形态」内部坍缩 |
| `knowledge-lifecycle-extract-archive-delete` | 不重复 | 处理「有知识价值目录的画转」，非「形态冗余坍缩」；可作上下游串联 |
| `no-touch-list` | 不重复 | 「哪些不改」的横向边界，无形态/再生视角 |
| `net-value-four-questions` | 不重复 | 外部机会净收益三缺口，无关 |
| `large-scale-duplication-elimination` | 不重复 | 代码级重复文本消除，非产物多形态 |
| `classification-disposition-decision-tree` | 不重复 | 文档结构治理四类处置 |
| `provenance-self-contained` | 不重复，可作 related | bundle-relative 溯源自包含；本模式引用其思想 |
| `reversibility-guarantee` | 不重复，可作 related | 可逆性四层级；本模式「派生层可删」以其「可逆变换」为支撑 |

**与 2026-10-19 报告模式 `constrained-fs-test-supply` 的分工**：该模式是**受限文件系统下的测试供给链**（venv 在 9p 不可行 ⇒ 改用 wheel 解包 + PYTHONPATH 供给依赖），属「怎么跑通」；本模式是「跑通后的产物怎么收」，属「怎么坍缩」。二者正交，可串联。

**G3 判定：通过**（模式名 8 字；触发场景含适用于/不适用于；六步在 3–7 区间；反模式 6 条 ≥ 3；含检验标准、跨域迁移表、显式划界；单案例标 L1；frontmatter 完整且 `id` 唯一）。

---

## 六、第一性原理（F）

**这个目录的第一个问题**：它存在的**唯一目的**是什么？

> 本目录存在的目的 = 为「openKylin-3.0 WSL 上、以 9p/drvfs 挂载访问源码的前提下，跑通 apps/containers 四成员 pytest」提供**可复跑的环境**与**不可再生的证据**。

由此推出两条第一性取舍标准：

1. **取舍标准 A（可复现性守恒）**：一件资产可去，当且仅当「它可由目录内已有的确定性命令再生」**且**「它不被消费者引用为唯一副本」。删除后须保证「即时复跑集」或「离线重建源集」至少一套完整。
2. **取舍标准 B（死路可去）**：一件资产即使**不可再生**，若它「由已废弃路线产生、且无任何消费者」，它同样可去——因为保留一个谁都够不着的死路分支，只增加认知成本与体量成本，不增加任何能力。

**张力裁决**：2026-10-19 报告 A-08 曾声明「`/mnt/ai` 侧暂不清理」（F-026）。本轮「简化」需求与之表面冲突。第一性裁决结果：A-08 的保护对象是「可复跑能力」，而非「目录里的每一个字节」。因此**只要保留 {`wsl-py314`, `wsl-spk`, `wsl-test-logs`}（即时复跑）与 {`cpython314.tar.gz`, `wsl-wheels`, `wsl-test-logs`}（离线重建），简化即不与 A-08 冲突**。据此选定「保守档」：仅删**脱离权威路径的死路 venv** 与**纯再生编译缓存**，不碰任何源与最小集成员。

**F 判定：通过**（目的明确；两条取舍标准可判可验；张力已显式裁决）。

---

## 七、原子化（A / G4）

> 动作编号用 `ACT-` 前缀，与 2026-10-19 报告的 `A-01…A-10` 区分。每条含单一职责、验证方式、验收口径。

| 编号 | 动作 | 类型 | 单一职责 | 验证方式 | 状态 |
|---|---|---|---|---|---|
| ACT-01 | 删除全部 `__pycache__`（113 目录 / 816 文件 / 15,000,130 字节） | 删除·派生层 | 仅清理编译缓存 | 后置普查：`PYCACHE_LEFT=0`；字节差含 15,000,130 | ✅ 已执行 |
| ACT-02 | 删除 `wsl-venv314`（3 文件 / 6 目录 / 78,298,359 字节） | 删除·死路层 | 仅移除死路 venv | 后置普查：`VENV_EXISTS=False`；字节差含 78,298,359 | ✅ 已执行 |
| ACT-03 | 保留即时复跑集 {`wsl-py314`, `wsl-spk`, `wsl-test-logs`} | 保留·源/运行时层 | 维持即时复跑能力 | `python3.14`、`env.sh`、`r4_full.sh` 存在性 = True | ✅ 已核验 |
| ACT-04 | 保留离线重建源集 {`cpython314.tar.gz`, `wsl-wheels`} | 保留·源层 | 维持离线重建能力 | `wsl-tmp/cpython314.tar.gz` = True；`wsl-wheels` 14 文件 | ✅ 已核验 |
| ACT-05 | 台账同步：`.temp/_index.md` L41 登记 `wsl-venv314` 已删（附理由） | 台账 | 仅更新登记 | L41 含「已删 2026-10-20」注记 | ✅ 已执行 |
| ACT-06 | 台账登记：`driver-rewritten-list.txt:54` 指向路径已删（**不改历史正文**） | 台账 | 仅登记悬空 | `_index.md` 新增说明条目 | ✅ 已执行 |
| ACT-07 | 规格侧注记：`.trae/specs/validate-containers-openkylin-wsl/checklist.md` 增补删除事实 | 台账 | 仅补一条状态 | checklist 含 2026-10-20 注记 | ✅ 已执行 |
| ACT-08 | 不删 `setup_venv.sh`/`install_deps.sh`（保留为历史证据，登记为「孤儿脚本」） | 保留·裁决 | 保留历史留痕 | 台账列出孤儿脚本清单 | ✅ 已登记 |

**三重不变式验收**：文件数 5149→4330（差 819 = 816+3 ✓）；目录数 413→293（差 120 = 113+7 ✓）；字节和 435,754,689→342,456,200（差 93,298,489 = 15,000,130+78,298,359 ✓）。

**G4 判定：通过**（8 个动作单一职责、可独立验证、有验收口径）。

---

## 八、对抗审查（V / 强制门）

> 四视角、7 个具体攻击点，采纳 4 条修正、接受 2 项已知风险。

### 8.1 攻击点与处置

| # | 视角 | 攻击点 | 处置 |
|---|---|---|---|
| ATK-1 | 魔鬼 | 「不引用 venv」这个前提是否被穷尽验证？若有历史脚本硬编码 venv 路径，删除会静默破坏 | **采纳**（见修正 V-1）：执行前已完成全工作区 `venv314` 命中核验（F-017），确认仅 4 处台账/规格 + 自身文件 + 废弃脚本，无活跃消费者 |
| ATK-2 | 魔鬼 | `driver-rewritten-list.txt:54` 是指向你自产的**证据清单**；删 venv 后该行悬空，清单不再完整 | **采纳**（V-2）：不改历史正文（保历史真实），在 `_index.md` 显式登记该行已悬空及原因 |
| ATK-3 | 魔鬼 | `setup_venv.sh`/`install_deps.sh` 将变成只指向已删目录的孤儿脚本，是否比删掉更误导后人 | **部分采纳**（V-3）：保留脚本（历史留痕价值 > 整洁价值），但登记为「孤儿脚本清单」并在报告中点名 |
| ATK-4 | 魔鬼 | `__pycache__` 是否真有隐性消费者（如冷启动基线测量） | **采纳**：`r4_full.sh` 使用 `-p no:cacheprovider`，`env.sh` 不引用 pycache，`.pyc` 为纯再生（F-020）；确认无消费者 |
| ATK-5 | 新人 | 2026-10-19 报告 A-08 保护集不含 `wsl-spk`/`wsl-wheels`，后人若照 A-08 清理会不会误删最小集成员 | **采纳**（V-4）：本报告显式给出**修订后的最小可复现集**（即时复跑集 + 离线重建源集），补齐 A-08 未覆盖的两项 |
| ATK-6 | 老板 | 回收 93 MB 对 345G 剩余（98%）几无意义，投入这多分析不值 | **接受风险**：本次简化为复盘顺带产物，边际成本低；且**模式沉淀（ARTIFACT-COLLAPSE-001）的价值独立于本次回收量** |
| ATK-7 | 未来 | 半年后有人想重建 venv 路线，发现脚本在而目录已删，且不知为何删 | **采纳**（V-2/V-3）：`_index.md` 登记删除理由（「无消费者 + 9p 不可行的死路分支」），报告留档 |

### 8.2 已采纳的修正

- **V-1**：执行删除前，重新完成引用面核验（`venv314` 全工作区命中），确认无输入型引用——已完成（F-017）。
- **V-2**：删除后不静默——在 `_index.md` 登记删除动作、理由与 `driver-rewritten-list.txt:54` 悬空事实。
- **V-3**：不删历史脚本，改为在台账列「孤儿脚本清单」（`setup_venv.sh`、`install_deps.sh`），避免历史失真。
- **V-4**：修订保护集口径——把 A-08 的 {`wsl-py314`, `wsl-test-logs`, `wsl-tmp`} 升级为显式的「即时复跑集 + 离线重建源集」，补齐 `wsl-spk`/`wsl-wheels`。

### 8.3 接受的已知风险

- **R-1（ROI）**：93 MB 回收相对 345G 剩余空间量级偏小；收益主要由模式沉淀承担。
- **R-2（历史真实 vs 整洁）**：`driver-rewritten-list.txt` 与两个孤儿脚本保留原样，代价是「清单存在悬空行、脚本指向已删目录」，以台账注记补偿。

**V 判定：通过**（四视角覆盖；7 攻击点 ≥ 5；采纳 4 条 ≥ 2）。

---

## 九、执行交付（C）

### 9.1 断言式简化（assertive-fs-ops 五段式）

| 段 | 内容 |
|---|---|
| 前置断言 | 重新普查，`PRE_FILES=5149`、`PRE_DIRS=413`，与固化快照一致方继续；`__pycache__` 数 = 113、`wsl-venv314` 存在，否则中止 |
| 记录前态 | 冻结 `5,149 / 413 / 435,754,689`（F-003） |
| 执行 | `[System.IO.Directory]::Delete(path, $true)` 逐个删 113 个 `__pycache__`，再删 `wsl-venv314` 树（F-037） |
| 后置验证 | `POST_FILES=4330`、`POST_DIRS=293`、`POST_BYTES=342,456,200`、`VENV_EXISTS=False`、`PYCACHE_LEFT=0` |
| 差异归因 | 文件 −819 = 816+3；目录 −120 = 113+7；字节 −93,298,489 = 15,000,130+78,298,359（F-034） |

### 9.2 实测结果

```
PRE_FILES=5149   PRE_DIRS=413
PYCACHE_DELETED=113   PYCACHE_FAIL=0   VENV_DELETED=OK
POST_FILES=4330  POST_DIRS=293  POST_BYTES=342456200
VENV_EXISTS=False   PYCACHE_LEFT=0
--- 保留集 ---
wsl-py314 files=3517 bytes=251460414
wsl-spk   files=661  bytes=11544804
wsl-test-logs files=117 bytes=640592
wsl-tmp   files=20   bytes=75506139
wsl-wheels files=14  bytes=3302750
verify_xc_kernel.py bytes=1501
pybin_exists=True  env_sh=True  r4_full=True  tmp_targz=True
```

**回收 93,298,489 字节 ≈ 93.3 MB；零误删；最小可复现集双套完整。**

### 9.3 产物与影响面

- 新增模式文件：`patterns/methodology-patterns/governance-strategy/artifact-form-collapse.md`
- `governance-strategy/index.md`：字母序插入一行
- 本报告：`reports/task-reports/retrospective-containers-openkylin-wsl-pytest-artifact-20261020.md`
- `task-reports/index.md`：扁平命名段插入一行
- `.temp/_index.md`：L41 登记 `wsl-venv314` 已删；新增本轮简化登记段（含孤儿脚本清单、`driver-rewritten-list.txt:54` 悬空说明）
- `.trae/specs/validate-containers-openkylin-wsl/checklist.md`：补 2026-10-20 删除注记

### 9.4 已知缺口

- **`.meta/toml` 伴生目录不可解析**：新增模式按既有体例写入了 `x-toml-ref: ../../../../../.meta/toml/.../artifact-form-collapse.toml`，但该物理路径在本 UNC 工作区经 `Glob`/`LS` 探测均不存在（与既有模式声明一致但不落地）。**本报告不承诺创建该 toml**；若仓库要求 toml 伴生，需另立任务补齐。
- **孤儿脚本**：`wsl-test-logs/setup_venv.sh`、`install_deps.sh` 现只指向已删的 `wsl-venv314`；保留为历史证据，已在台账登记。
- **历史悬空行**：`_tools/driver-rewritten-list.txt:54` 指向已删路径，按 V-2 保留原文并在台账注记。

**C 判定：通过**（单一职责、可独立验证、有 Owner（本任务）、有验收；断言式三不变式全通过）。

---

## 十、大白话总结

1. 这个目录有 435.8 MB，但**真资产不多**：一个解释器被存了三遍（源包 + 解包树 + 一个复制出来的 venv），依赖也是包 + 解包两遍，再加 14 MB 编译缓存。
2. 那个复制出来的 venv（78 MB）其实是**死路**——它空得连 pip 都没有，正式复跑脚本根本不看它；当初在 9p 挂载上创建它还失败了（日志留着）。
3. 所以本轮只做**保守简化**：删掉这个死路 venv + 全部编译缓存，共 **93.3 MB**。解释器的源包和解包树、依赖的 wheel 和解包树、所有脚本和日志，**一个没动**。
4. 结果：即时能跑、离线能重建，两套能力都还在；目录从 5,149 文件降到 4,330 文件，字节数分毫不差地对上了账。
5. 顺手把这套做法沉淀成一个可复用模式——**「同源产物形态坍缩法」**：遇到「同一个东西存了好几遍」的目录，不要逐个文件纠结，而是画出「谁是源、谁能从谁再生」的图，只保留能再生的源头，其余整体坍缩。

---

## 附录：与既有报告的关系

| 报告 | 视角 | 链路 | 模式 |
|---|---|---|---|
| [retrospective-containers-openkylin-wsl-pytest-20261019](retrospective-containers-openkylin-wsl-pytest-20261019.md) | 四成员 pytest 在 9p 上的**可跑通性** | R→I→E→V→C | `constrained-fs-test-supply`（L1） |
| **本报告（2026-10-20）** | 跑通后产物目录的**存续价值与形态坍缩** | R→I→E→F→A→V→C | `artifact-form-collapse`（L1） |

> 本报告**不覆盖**前述报告；两者的证据路径引用同一 `.temp/openkylin-wsl-pytest` 主题，映射台账见 `.temp/_index.md`。

> 敏感度：公开。本轮未 git commit、未 push；`.temp/` 本身不纳入版本控制。