---
type: Reference
id: "openeuler-vs-openkylin"
title: "openEuler 与 openKylin 系统性对比：后端根社区与桌面根社区的分工、治理、生命周期与选型"
category: "tech"
tags:
  - openeuler
  - openkylin
  - linux-distro
  - root-community
  - openatom
  - server-os
  - desktop-os
  - release-lifecycle
  - rpm
  - deb
  - china-opensource
date: "2026-09-30"
last_updated: "2026-09-30"
status: "verified"
author: "SpecWeave Agent（方法论编排 session sc-20260930-openeuler-vs-openkylin）"
summary: "以七概念方法论（R→I→E→V→C，standard）系统对比 openEuler 与 openKylin：新采集 openEuler 侧 35 条带来源客观事实（O-001~O-035，2010 EulerOS 起源至 2026-09 装机 2000 万口径与 24.03 LTS SP4），以 12 条锚点（K-001~K-012）引用本地 openKylin 知识包 62 条事实，形成 5 条四元组洞察与 1 个 L1-draft 可迁移模式（场景区间选型法）。核心结论：两者不是直接竞品，而是同一开放原子基金会体系内后端基础设施根社区与桌面/AI 终端根社区的产业分工，麒麟软件同时为两边参与者且其服务器/桌面商业版分别以两者为上游。知识包按问题域拆为画像、定位场景、治理生态、版本生命周期、技术栈、选型指南 6 个概念页，附信源台账与对抗审查记录。"
security_level: "public"
knowledge_type: "conditional"
validation_status: "verified"
reuse_count: "0"
integrity: "unchecked"
source: "openEuler 侧公开网络信源：openeuler.org 官网（下载页/生命周期页/repo 目录/软件中心/官方文档）、华为官网新闻、人民邮电报（中新网转载）、太平洋科技/快科技、新华网、openEuler 社区介绍 PDF、dev 邮件列表、麒麟软件官网产品手册；openKylin 侧不重新联网，全部引用同目录既有知识包 openkylin-docs-wiki（references/project-overview.md 的 F-001~F-062 与 index.md 的 F-001~F-044）。采集时点 2026-09-30，完整 URL 见 references/source-inventory.md。"
---

# openEuler 与 openKylin 系统性对比

> 一句话摘要：openEuler 与 openKylin 不是同一赛道的两个竞品，而是开放原子开源基金会体系内分工明确的两个**根社区**——openEuler 面向服务器、云、边缘、嵌入式的数字基础设施（RPM/dnf、LTS 4 年间隔、6—8 年维护、25 家 OSV、2000 万装机口径），openKylin 面向桌面与 AI 终端（dpkg/apt、UKUI 原生、3 年 LTS 加 1 年创新版双轨、四架构同源）；麒麟软件同时参与两边，其服务器商业版基于 openEuler、桌面商业版以 openKylin 为上游。选型的第一问不是"谁更好"，而是"工作负载落在哪一侧"。

- **编排 session**：`sc-20260930-openeuler-vs-openkylin`
- **场景与链路**：场景 4 知识沉淀，`R→I→E→V→C（入库）`，depth=standard
- **采集时点**：2026-09-30（openEuler 侧为新采集；openKylin 侧引用 2026-09-29 既有知识包，见下）
- **信源分工**：openEuler 侧事实编号 **O-001~O-035**，来源键 [S01]~[S17] 见[信源台账](references/source-inventory.md)；openKylin 侧不重复采集，以 **K-001~K-012** 锚点引用本地知识包 [openKylin 全面调研](../openkylin-docs-wiki/references/project-overview.md)（F-001~F-062）与[官方文档平台教程](../openkylin-docs-wiki/index.md)（F-001~F-044）。

---

## 0. 快速导航：按你的问题出发

| 我想…… | 去读哪一篇 |
|---|---|
| 一分钟看清两者各是什么、六个相近名字（EulerOS/欧拉/openEuler/银河麒麟/openKylin/优麒麟）怎么区分 | [00 双像对照与名称辨析](concepts/00-overview.md) |
| 搞清两者各自面向什么场景、为什么不是竞品 | [01 定位与场景分工](concepts/01-positioning-and-scenarios.md) |
| 对比治理结构、捐赠人、SIG、OSV、装机量（含口径警示） | [02 治理与生态形状](concepts/02-governance-and-ecosystem.md) |
| 对比版本制度：4 年间隔 6—8 年生命周期 vs 3 年 LTS 加年度创新版 | [03 版本与生命周期](concepts/03-release-lifecycle.md) |
| 对比包管理、桌面、架构、虚拟化/容器、标志性技术与 AI 落点 | [04 技术栈分叉](concepts/04-technology-stack.md) |
| 拿到"我该选谁"的五问决策流程、商业版路径与反模式清单 | [05 场景区间选型法](concepts/05-selection-guide.md) |
| 核查每条事实出处、URL 与口径分级 | [信源台账](references/source-inventory.md) |
| 了解本对比经受了哪些攻击、哪些结论被修正 | [V 对抗审查记录](references/adversarial-review.md) |

---

## 1. R 阶段：客观事实清单

> G1 已通过：O 组 35 条全部为可验证客观陈述，无"因为/所以/导致/从而"等因果推断词；数字、日期、URL 按信源原文记录并标注时点；厂商大会口径、第三方机构口径、官网实时统计口径分别标注，互相矛盾或时点不同的数据显式并列。K 组为本地既有知识包事实的引用锚点，正文不复制采集过程。

### 1.1 A 组：openEuler 起源与治理（O-001 ~ O-010）

| 编号 | 事实 | 来源 |
|---|---|---|
| O-001 | openEuler 前身为华为内部 EulerOS，起源于高性能计算项目，2010—2012 年首次发布，基于 CentOS 编译开发；EulerOS 1.x 于 2013—2016 年商用 | [S08][S09] |
| O-002 | 2019-09-19 华为全联接大会宣布 EulerOS 开源、openEuler 社区成立（内测阶段）；2019-12-31 openEuler 源代码正式上线，社区发行版推出 | [S08] |
| O-003 | 2020-03-27 openEuler 20.03 LTS 作为首个 LTS 版本发布；同日麒麟软件、普华基础软件、统信软件、中科院软件所 4 家发布基于 openEuler 的商业发行版（麒麟服务器操作系统、普华服务器操作系统鲲鹏版、deepinEuler V1.0、傲徕操作系统）；早期规划为每两年一次 LTS、每 6 个月一个创新版本，坚持 Upstream First | [S09] |
| O-004 | 2021-09 华为宣布欧拉定位从服务器操作系统升级为"数字基础设施操作系统"，覆盖 IT、CT、OT，场景含服务器、云计算、边缘、嵌入式 | [S07][S10] |
| O-005 | 2021-11-09 华为将 openEuler 全量代码、品牌商标、社区基础设施捐赠给开放原子开源基金会；捐赠仪式官方披露欧拉商用累计规模突破 60 万套 | [S07] |
| O-006 | 社区治理架构为 openEuler 委员会（下设常务委员会、顾问专家委员会、技术委员会、品牌委员会、用户委员会）— SIG（Maintainer、Committer、贡献者三级角色）— 子项目；另设项目群办公室与执行总监 | [S02] |
| O-007 | openEuler 官网首页实时统计（2026-09-30 采集，页面动态变化，两次抓取数值有差异）：贡献者约 29,297—29,342 名、代码仓库 12,459—12,462 个、SIG 112 个、社区用户约 9,986,120—10,029,760、商用 OSV 25 家 | [S03] |
| O-008 | 2025 年新增捐赠人含海光信息、AMD、浪潮云、神州数码；Intel、Arm、AMD 三家芯片企业均列入捐赠人名单 | [S01][S10] |
| O-009 | 截至 2026 年 4—5 月公开报道，社区单位成员 2100 余家、贡献者约 2.7 万名；社区联合 18 所高校成立学术与教育委员会 | [S01][S04] |
| O-010 | 社区介绍材料披露其托管与孵化的基础软件创新项目超过 500 个 | [S02] |

### 1.2 B 组：装机规模与市场口径（O-011 ~ O-014）

> ⚠️ 本组数字全部为**官方或第三方机构口径的转引**，统计对象（新增装机/累计装机/注册用户/出货套数）与时点各不相同，禁止跨口径直接比较，详见 [02 治理与生态](concepts/02-governance-and-ecosystem.md)的口径警示。

| 编号 | 事实 | 来源 |
|---|---|---|
| O-011 | 2023-12 官方口径累计装机超过 610 万套；IDC 口径 openEuler 2023 年在中国服务器操作系统市场份额为 36.8%，列新增市场第一 | [S08] |
| O-012 | 沙利文联合头豹研究院《2025年中国服务器操作系统行业发展白皮书》（经人民邮电报、太平洋科技转引）口径：2025 年全年新增装机 448 万套，openEuler 系份额 57.3%；2025 年累计装机突破 1600 万套 | [S01][S04] |
| O-013 | 2026-09-18 华为全联接大会，华为常务董事汪涛宣布 openEuler 累计装机量突破 2000 万套、登顶中国服务器操作系统市场份额第一（厂商大会口径） | [S04] |
| O-014 | 同场公布的鲲鹏生态关联数据：全球开发者超过 416 万、生态伙伴 7200 余家（鲲鹏口径，非 openEuler 社区直接统计） | [S04] |

### 1.3 C 组：版本、生命周期与架构支持（O-015 ~ O-022）

| 编号 | 事实 | 来源 |
|---|---|---|
| O-015 | 现行生命周期规范（技术委员会与 Release SIG 公示，2025-08 起生效）：LTS 发布间隔 4 年、社区支持 4 年；LTS 全版本生命周期 6 年（4 年社区支持加 2 年延长支持），可申请延长至 8 年；偶数年 3 月发布新一代 LTS 首版；偶数年 12 月与奇数年 12 月发布 SP，奇数年 6 月可选择性发布 SP；6 月小 SP 维护 9 个月，12 月大 SP 维护 24 个月；创新版每 12 个月发布一个（9 月），支持期 6 个月 | [S05] |
| O-016 | 当前主力长期版本为 openEuler 24.03 LTS，基于 Linux 6.6 内核 | [S05][S06] |
| O-017 | repo.openeuler.org 目录实测版本序列：20.03 LTS（2020-03）及 SP1—SP4；创新版 20.09、21.03、21.09、22.09、23.03、23.09、24.09、25.03、25.09；22.03 LTS（2022-04，捐赠后首个社区共建版本、首个全场景长周期版本）及 SP1—SP4 与 22.03-LTS-64kb 变体；24.03 LTS 及 SP1—SP4 | [S06] |
| O-018 | 24.03 LTS 各 SP 时点（官方发布日期与仓库/下载页日期并列保留）：SP1 为 2025-01-24；SP2 为 2025-06-30；SP3 仓库目录日期 2026-03-06、官方口径 2025-12-30 社区上线，定位为面向超节点的操作系统；SP4 仓库目录日期 2026-09-08、官方发布日 2026-06-30，下载页 Planned EOL 标注 2027/03 | [S03][S06] |
| O-019 | 24.03 LTS SP4 特性清单：Linux 6.6 内核、灵衢超节点可靠性与易用性、NPU 算力切分、推理服务快速恢复、E2B 沙箱、智能诊断/调优/运维、编译器增强、机密虚拟机 | [S03] |
| O-020 | openEuler Embedded 26.03（仓库目录日期 2026-04-17）基于 IB-Robot 具身智能全栈架构，面向 hi3403、hi3591 等板卡，组件含 EmbodiedClaw、ROS 2 Driver、tensormsg、VLA 大模型推理、MoveIt 2 | [S03] |
| O-021 | 官方支持架构：x86_64、aarch64、ARM32、LoongArch64、RISC-V；社区介绍材料另列 SW-64（申威）与 Power 的支持口径 | [S03][S02] |
| O-022 | 版本更新按周公示：Release SIG、QA SIG、CICD SIG 发布 update 邮件（如 update_20260513），内容含 CVE 清单与缺陷清单，20.03-SP4、22.03-SP4、24.03 等多分支并行维护 | [S15] |

### 1.4 D 组：包管理、镜像与桌面（O-023 ~ O-026）

| 编号 | 事实 | 来源 |
|---|---|---|
| O-023 | 软件包体系为 RPM/dnf；openEuler 软件中心（easysoftware）页面显示 213,330 个软件包、325 个应用镜像；25.09 创新版起引入 epkg 包格式，支持多环境多版本；软件分类含 OEPKG、CONDA 等 | [S11] |
| O-024 | 安装镜像形态含 Offline Standard ISO（24.03 LTS SP4 x86_64 约 4.5 GiB）、Everything（约 26.6 GiB）、Network Install（约 1.3 GiB）；场景标签覆盖服务器、边缘、云、嵌入式、DevStation | [S03][S02] |
| O-025 | 系统获取渠道含公有云镜像（华为云、腾讯云、AWS、Azure、阿里云）、容器镜像、EulerLauncher、WSL、MacOS | [S03][S02] |
| O-026 | 桌面环境不在主线介质内：官方文档提供 DDE（统信团队维护，`dnf install dde`）与 UKUI（麒麟团队维护，`dnf install ukui`）两份装后安装指南；DDE 指南示例内置普通用户 openeuler（密码 openeuler），root 不能直接登录图形桌面 | [S12][S13] |

### 1.5 E 组：标志性技术与商业生态（O-027 ~ O-033）

| 编号 | 事实 | 来源 |
|---|---|---|
| O-027 | 社区标志性基础设施软件项目：StratoVirt 轻量虚拟化、iSula 轻量容器、A-Tune 智能优化、Gazelle 用户态协议栈、SysMaster、SysCare 热补丁、A-OPS 智能运维、Kmesh 服务网格、KubeOS、Rubik 在离线混布 | [S02] |
| O-028 | 安全与工具链项目：SecGear 机密计算、secPaver、毕昇 JDK 与毕昇编译器、EulerFS、etMem、Gala、Uniproton 实时内核；架构层有榫卯（全栈原子化解耦）与 Soft Bus（与 OpenHarmony 生态互通） | [S02] |
| O-029 | 2026 年 AgentOS 方向公开内容：系统智能中枢、JiuwenClaw 等 Agent 接入；ODD 2026 演示四能力为智慧中枢多模态、eBPF 加行为分析主动防御、Conch 沙箱引擎（百毫秒级启动）、Token 能效（官方口径推理效率提升 20%—30%）；另有 SkillHub 站点 skillhub.openeuler.org | [S01] |
| O-030 | openEuler Developer Day 2026（2026-04-25，长沙）现场 450 余人、109 个 SIG 参与研讨，八大方向：Kernel 与基础服务、AI 生态、超节点、具身智能与嵌入式、AI 时代开发与包管理、全场景与 Agent Infra、RISC-V、AI 使能安全 | [S01] |
| O-031 | 官网列出 25 家商用 OSV；银河麒麟高级服务器操作系统 V10 SP3 产品手册明确表述其"直接面向 kernel 根社区、基于 openEuler 社区构建"，V10 内核主版本 4.19 在生命周期内保持不变、融合 openEuler 各 LTS/SP 特性；麒麟白皮书表述其在 openEuler 社区贡献排名第二 | [S14] |
| O-032 | 官网用户案例集中行业为金融（工商银行、农业银行、山西证券、三湘银行）、运营商、能源、物流、高校科研、云计算 | [S03] |
| O-033 | 代码托管平台为 AtomGit/GitCode（src-openeuler 组织）与 release-management 仓库；openeuler.org 与 openeuler.openatom.cn 双域名并存 | [S03][S15] |

### 1.6 F 组：时点数据对照与媒体分工口径（O-034 ~ O-035）

| 编号 | 事实 | 来源 |
|---|---|---|
| O-034 | 社区介绍 PDF 披露较早时点数据：409 万用户、累计装机 1000 万、110 个 SIG、2055 家成员单位、22424 名贡献者；与官网首页实时统计（O-007）在口径与时点上均不同，并列保留、不互相替换 | [S02][S03] |
| O-035 | 媒体综述中的分工表述：界面新闻 2026-04-09 文章与凤凰网 2026-09-04 openKylin 3.0 报道分别使用"openEuler 深耕服务器、桌面能力偏弱""openKylin 承担前沿技术预研、成熟技术反哺商业版"等表述（媒体定性评价，非量化事实） | [S16][S17] |

### 1.7 openKylin 侧引用锚点（K-001 ~ K-012，引自本地知识包）

| 锚点 | 事实 | 引用位置 |
|---|---|---|
| K-001 | 2022-06-24 麒麟软件联合 13 家单位发起 openKylin，官方表述"中国首个桌面操作系统根社区" | [project-overview F-003](../openkylin-docs-wiki/references/project-overview.md) |
| K-002 | 2024-09-25 openKylin 捐赠开放原子开源基金会，官方表述"我国首例央企开源捐赠" | F-005 |
| K-003 | 截至 2026-07-31：社区用户超 247 万、会员超 2210 家、开发者超 2.4 万、SIG 158 个 | F-007/F-008 |
| K-004 | 版本双轨制（2026-04-09 TC 表决）：LTS 每 3 年一个、2 年主动加 3 年被动共 5 年；创新版每年一个、12 个月被动维护，定位"新技术试验田" | F-011/F-012 |
| K-005 | openKylin 2.0 LTS（代号 Nile）2024-08-08 发布，Linux 6.6，180+ 核心组件自主选型 | F-013/F-018 |
| K-006 | openKylin 3.0（创新版，代号 Huanghe）2026 年 9 月发布，内核跨代至 Linux 7.0，集成 NIST 三项后量子密码标准、内核支持 Rust for Linux | F-024/F-025/F-026/F-027 |
| K-007 | 软件包体系为 apt/dpkg（Debian 系） | F-035 |
| K-008 | 桌面侧自研组件：开明（Kaiming）包、基于 OSTree 的不可变系统、wlcom Wayland 合成器、磐石架构（不可变系统+KARE+开明包） | F-036/F-037/F-038/F-039 |
| K-009 | UKUI 为默认桌面（Qt 技术栈），3.0 搭载 UKUI 4.24 | F-029/F-040 |
| K-010 | X86、ARM、LoongArch、RISC-V 四架构同源发版；RISC-V 侧有统一镜像、RVA23/RVV 对齐与多款开发板支持 | F-020/F-030 |
| K-011 | 3.0 智能体开放底座：智能体经 MCP 协议调用桌面能力，提供统一 AI SDK、Token 中心，衍生镜像分 AgentOS、Claw Box OS、行业定制三类 | F-047/F-048 |
| K-012 | openKylin 是银河麒麟桌面商业版的上游社区；麒麟"1+2+3+M+N"体系中"1 个技术源头"为开放麒麟社区 | F-051 |

---

## 2. I 阶段：核心洞察（四元组）

> G2 已通过：5 条洞察各含 **陈述 / 证据（编号）/ 反常识 / 行动**，五个维度（产业分工、治理生态、版本哲学、技术路线、AI 落点）互不重叠。

### I-1　两者不是竞品，而是同一基金会体系内"后端根社区 vs 桌面根社区"的产业分工

- **陈述**：openEuler 的官方定位与版本、镜像、案例、OSV 体系全部围绕数字基础设施展开（服务器/云/边缘/嵌入式，2021 年起的定位表述覆盖 IT/CT/OT）；openKylin 的发起表述即为"桌面操作系统根社区"，介质、UKUI、硬件适配与智能体方向围绕桌面与 AI 终端。麒麟软件同时出现在两边：其服务器商业版产品手册写明"基于 openEuler 社区构建"，桌面商业版产品手册写明 openKylin 是其上游社区。
- **证据**：O-004（定位升级）、O-024/O-032（镜像标签与案例行业）、O-031（麒麟服务器版基于 openEuler）、O-035（媒体分工表述）；K-001（桌面根社区表述）、K-012（桌面商业版上游）；本地包 F-058（前后端分工并列）。
- **反常识**：两个名字都带"麒麟/欧拉"色彩、同在开放原子基金会、都提供 UKUI、都发布 AgentOS，直观上像同场竞技的对手；商业产品层面的真实结构是**同一家公司两条产品线各有一个社区上游**，两者在社区治理层还有共同参与者（麒麟软件为 openEuler 发起者之一、openKylin 主导发起方）。"谁替代谁"是一个错误的问题。
- **行动**：任何对比先做场景切分——工作负载是"后台基础设施"还是"人机交互终端"；禁止用一侧的市场数字（如服务器装机量）论证另一侧（桌面可用性）的结论。

### I-2　治理同构但发起方产业位置不同，刻画出两种生态形状

- **陈述**：两者都完成了向开放原子基金会的捐赠（openEuler 2021-11，openKylin 2024-09），治理上都采用委员会加 SIG 结构；但发起方的产业资源禀赋不同：华为带入场的是云、鲲鹏、运营商与金融客户体系，生态形状为 25 家 OSV 的多点下游与大规模服务器装机；麒麟软件带入场的是 CEC 体系下的党政桌面渠道与整机厂商关系，生态形状为单一最大商业下游加海量软硬件适配汇聚（其官网口径累计硬件适配超 106 万项、软件适配超 748 万项）。
- **证据**：O-005/O-008（捐赠人与芯片企业）、O-007（112 SIG、25 OSV）、O-031（OSV 与麒麟角色）、O-013（装机口径）；K-002（央企捐赠）、K-003（158 SIG）、K-001（13 家发起单位名单）；本地包 F-011/F-054。
- **反常识**："捐赠入基金会"常被理解为项目同质化、中立化后生态逻辑趋同；实际证据显示中立治理是**汇聚生态的手段**，不抹平发起方的产业位置——多点 OSV 下游与单一下游加适配汇聚地是两种不同形状，且两者的社区规模指标（SIG 数、用户数、贡献者数）统计口径不同，不能直接比大小。
- **行动**：评估根社区生态健康度用三组结构指标——下游商业发行版数量与多样性、非发起方企业主导的 SIG/特性名单、硬件适配汇聚的厂商名单；引用规模数字时同时引用统计口径与时点。

### I-3　版本节奏哲学相反：超长稳定服务基础设施，双轨制承担前沿预研

- **陈述**：openEuler 现行规范把 LTS 间隔拉长到 4 年、全版本生命周期 6 年并可申请 8 年，12 月大 SP 维护 24 个月，多分支并行按周公示 CVE；openKylin 采用 3 年 LTS（5 年维护）加每年创新版（12 个月）的双轨制，并在 2026 年的创新版 3.0 上先于多数发行版跨代到 Linux 7.0、引入 Rust for Linux 与后量子密码。
- **证据**：O-015（生命周期规范全文要点）、O-017/O-018（版本序列与 SP 时点）、O-022（按周 update 与多分支维护）；K-004（双轨制 TC 表决）、K-005/K-006（Nile 6.6 与 Huanghe 7.0）。
- **反常识**：成立更晚的桌面社区（2022）比老牌服务器社区（2019）更快采用全新内核，表面是"激进 vs 保守"的风格差异；按工作负载定价看则是理性分工——基础设施客户为"不变"付费（回归风险成本极高），桌面与新硬件用户为"新"付费（新外设、新 AI 能力需要新内核），创新版的制度功能是替商业版承担预研与回归暴露。
- **行动**：按变更容忍度选版本线——关键生产锁 LTS 加大 SP 并跟踪周度 CVE 公示；新硬件验证、AI/具身智能预研走创新版且明确其 6—12 个月支持期；不要把创新版部署到要求长周期支持的环境。

### I-4　真正的技术分叉在包管理与系统架构层，"都有 UKUI"不等于桌面能力同质

- **陈述**：两侧最硬的技术路线差异是软件包体系：openEuler 为 RPM/dnf（并在创新版试 epkg），openKylin 为 dpkg/apt（Debian 系）；桌面在 openEuler 是装后可选仓库组件（DDE 或 UKUI，官方文档另有 root 不能登录图形桌面等说明），在 openKylin 是默认产品本体（UKUI 版本与发行版同步、wlcom/开明/OSTree 磐石构成系统架构特性）。基础设施侧 openEuler 有 StratoVirt、iSula、SysCare、Kmesh 等一长串服务器栈项目；openKylin 的自研密度集中在桌面与端侧。
- **证据**：O-023（RPM/dnf、21 万包口径、epkg）、O-026（DDE/UKUI 可选安装）、O-027/O-028（服务器技术清单）；K-007（apt/dpkg）、K-008/K-009（桌面自研组件与 UKUI 同步）、本地包 F-019/F-022。
- **反常识**：特性表对照会让人产生"两边都是全场景 Linux、能力趋同"的错觉；包格式与桌面在系统中的地位决定了软件生态存量、运维技能栈与迁移成本——CentOS 停服后的平滑路径落在 RPM 系 openEuler，桌面软件与外设适配的存量在 openKylin 侧更厚。"`dnf install ukui` 能装上"与"桌面是一等产品"之间隔着默认体验、适配广度与维护响应的完整差距。
- **行动**：技术评估第四问盘点团队技能栈（RPM 系还是 Debian 系）与存量软件格式；桌面工作负载要求基于实际介质的默认环境实测，不把"仓库里有桌面组件"当作桌面就绪证据。

### I-5　AI 化方向互相呼应但落点不同：集群侧 AgentOS 与端侧智能体底座同名不同层

- **陈述**：openEuler 2026 年 AgentOS 叙事的组件落在集群与基础设施侧：灵衢超节点、NPU 算力切分、推理服务快恢、Conch 沙箱、eBPF 主动防御、智能运维与 Token 能效；openKylin 3.0 的智能体开放底座落在端侧：模型/记忆/工具/权限与桌面能力统一架构，智能体经 MCP 直接调用桌面，配套 AI SDK、技能仓库与 Token 中心，并有 AgentOS/Claw Box OS 衍生镜像。
- **证据**：O-018/O-019/O-029/O-030（超节点、NPU 切分、AgentOS 四能力、八大方向）；K-011（端侧 MCP 底座与衍生镜像）。
- **反常识**：两边都使用"AgentOS"这一名称，容易被当作同一赛道的对标产品；一个指"智能体调度与运维数据中心"，一个指"智能体作为原住民操作个人桌面"，名称相同而所处层次不同，评估清单也不通用。
- **行动**：AI 能力评估按落点分两份清单——基础设施侧问算力切分、混布、可观测与能效；终端侧问协议开放性（MCP 类）、第三方智能体权限对等性、技能签名审计与本地模型替换。两边结论互不借用。

---

## 3. E 阶段：可迁移模式（G3）

### 模式：场景区间选型法（L1-draft）

> 本模式已于 2026-09-30 独立沉淀入方法论模式库，通用版（抽象步骤、跨域迁移、与选型类模式关系）见 [场景区间选型法](../../../retrospective/patterns/methodology-patterns/governance-strategy/scenario-interval-selection.md)；本节保留本案例版摘要，完整操作版仍以 [05 概念页](concepts/05-selection-guide.md)为准。

**一句话**：面对同一治理体系内两个相邻根社区（或基础软件分支），不按知名度与总量指标选型，而按"工作负载形态 → 商业下游与合规 → 生命周期偏好 → 包管理与生态存量 → 硬件架构"五问依次收敛，每问把选项推向不同区间，最后以最小实测完成验证。

| 要素 | 内容 |
|---|---|
| **适用于** | 存在明确工作负载形态分叉的两个根社区/基础软件选型；候选对象治理同源或高度相似、特性表大面积重叠、舆论常混为一谈的场合（本案例为 openEuler 与 openKylin） |
| **不适用于** | 同一场景内的直接竞品比较（如两款桌面 OS 比功能与性能）；纯个人偏好选择；已被商业合同、等保测评或既有认证锁定的采购决策；两边均无对应成熟下游的全新场景 |
| **核心步骤** | ① **问工作负载形态**：后端基础设施（服务器/云/边缘/嵌入式）入 openEuler 区间，人机交互终端（桌面/AI PC/开发板）入 openKylin 区间；② **问商业下游与合规**：生产需 SLA、等保/可靠测评与售后的，立即转商业发行版路径（openEuler 侧 25 家 OSV，openKylin 侧银河麒麟桌面商业版），社区版定位为评估与预研；③ **问生命周期与变更容忍**：追求 6—8 年不变选 openEuler LTS/大 SP；接受双轨、要用新内核新特性走 openKylin LTS/创新版；④ **问包管理与生态/技能存量**：RPM/CentOS 系存量与运维技能偏向 openEuler；Debian/Ubuntu 桌面软件与外设存量偏向 openKylin；⑤ **问硬件架构**：国产 X86/ARM 两边均支持，RISC-V 桌面与开发板优先核查 openKylin 镜像与 SIG，服务器/嵌入式板卡核查 openEuler Embedded；⑥ **最小实测收口**：社区版介质在目标硬件与目标负载上 POC，生产部署回到带合同的商业版 |
| **检验标准** | 五问每题有书面答案且可被第三人复核；最终选择至少附一条工作负载证据而非知名度证据；商业路径写明 OSV 名称、产品版本与测评编号；POC 记录可复现 |
| **反模式** | ① 按知名度/装机量跨场景选（2000 万服务器装机不能证明桌面可用，247 万桌面用户不能证明服务器可运维）；② 把"同基金会、都有 UKUI、都发 AgentOS"当作同质化证据；③ 忽视社区版与商业版的 SLA/测评主体差异，社区版直接上关键生产；④ 六名混谈（EulerOS/欧拉/openEuler/银河麒麟/openKylin/优麒麟）导致张冠李戴；⑤ 用厂商大会口径数字（57.3%、2000 万套等）做精确采购测算 |
| **跨域迁移** | 可迁移至同基金会多根社区选型（如服务器侧 openEuler 与龙蜥 Anolis 的区间判定需改用"合规/存量/云厂商绑定"维度）、数据库 OLTP/HTAP 分工选型、Kubernetes 商业发行版选型；步骤①"先分工作负载形态"对任何"听起来差不多"的二选一基础软件决策通用 |
| **成熟度** | **L1-draft**：基于单对比主题与双侧多信源首次成型；步骤①—④有本案例双侧事实支撑，步骤⑤⑥迁移自[最小充分脚手架选型法](../../../retrospective/patterns/methodology-patterns/governance-strategy/minimal-sufficient-scaffold-selection.md)的"真实任务验证"原则。升级 L2 条件：在第二个独立双根社区场景（数据库或云原生方向）完成一次完整五问应用并回填修订记录 |

> 本模式完整操作版（决策表、我该装谁、商业版路径）见 [05 场景区间选型法](concepts/05-selection-guide.md)。与既有模式[根社区—商业发行版双轮](../../../retrospective/patterns/methodology-patterns/product-growth/root-community-commercial-distro-flywheel.md)互补：后者解释"社区—商业"两轮如何转动，本模式解决"两个社区之间站在哪边"。

---

## 4. V 阶段：4 视角对抗审查

> 审查在初稿完成后执行，完整问题清单、裁定与回归确认见 [V 审查记录](references/adversarial-review.md)。V 门结论：4 视角全覆盖、意见 8 条（≥5）、采纳 7 条并部分采纳 1 条（≥2），**通过**。主要修正：全部装机/份额数字加口径标注、社区规模跨社区比较被禁止、媒体定性句降格引用、补六名辨析与术语表、补商业版合规路径、设置两个年度复查触发器。

---

## 5. 质量门与编排记录

| 门 | 标准 | 结果 |
|---|---|---|
| G1 | 事实 ≥20、无因果词、可溯源、数字/URL 完整、口径差异显式标注 | PASS（openEuler 侧 O-001~O-035 共 35 条 + openKylin 侧 K-001~K-012 引用锚点；时点/口径不一致数据并列保留） |
| G2 | 洞察 ≥3 且四元组完整、维度独立、含反常识与行动 | PASS（I-1~I-5：产业分工/治理生态/版本哲学/技术路线/AI 落点） |
| G3 | 模式含适用与不适用边界、3—7 步骤、≥3 反模式、检验标准、跨域迁移、成熟度标注 | PASS（场景区间选型法，六步五反模式，L1-draft，附升级条件） |
| V 门 | 4 视角、意见 ≥5 且具体、采纳 ≥2 并回归确认 | PASS（8 条意见，7 采纳 1 部分采纳，全部回归关闭） |
| G4 | 产出原子化：单一职责文件、可独立验证、链接与命名规范、toctree 登记 | PASS（9 个原子文件：index + 概念页 6 + references 2；toctree 经本 index 统一登记，文件名与链接检查通过） |

**局限声明**：① openEuler 侧信源以官网、华为系新闻与行业媒体转引为主，缺少独立第三方性能/稳定性实测；沙利文白皮书原文未获取，57.3% 等数字为转引口径。② 官网首页统计为动态页面数据，两次抓取即有差异，只作数量级参考。③ openKylin 侧事实冻结在本地知识包 2026-09-29 采集时点，未因本次对比重新联网核验。④ 两侧 2026 年 9 月均处于新版本窗口（openEuler 24.03 SP4、openKylin 3.0），部分镜像与文档在分阶段上架，结论的一年期有效性需按 V 审查设置的触发器复查。⑤ 本知识包不构成采购建议，生产采用前须自行完成商业版尽调与 POC。

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20260930-openeuler-vs-openkylin | msg=方法论编排开始：openEuler vs openKylin 系统性对比 | ctx={"scenario":"knowledge","topic":"openeuler-vs-openkylin","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20260930-openeuler-vs-openkylin | msg=知识沉淀链路R→I→E→V→C | ctx={"chain":"R-I-E-V-C","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20260930-openeuler-vs-openkylin | msg=35条O组事实+12条K锚点，无因果词，口径差异并列保留 | ctx={"facts":"O-001~O-035,K-001~K-012"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20260930-openeuler-vs-openkylin | msg=5条四元组洞察，维度互相独立 | ctx={"insights":["I-1","I-2","I-3","I-4","I-5"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20260930-openeuler-vs-openkylin | msg=场景区间选型法L1-draft，六步五反模式，附升级条件 | ctx={"pattern":"scenario-interval-selection"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=GATE_PASSED | session=sc-20260930-openeuler-vs-openkylin | msg=4视角8意见，7采纳1部分采纳，回归关闭 | ctx={"adopted":7,"partial":1}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20260930-openeuler-vs-openkylin | msg=35事实/12锚点/5洞察/1模式(L1-draft)/4视角8意见/9原子文件 | ctx={"gates":["G1","G2","G3","V","G4"],"deliverable":"docs/knowledge/tech/openeuler-vs-openkylin/"}
```

```{toctree}
:maxdepth: 1
:hidden:

concepts/00-overview
concepts/01-positioning-and-scenarios
concepts/02-governance-and-ecosystem
concepts/03-release-lifecycle
concepts/04-technology-stack
concepts/05-selection-guide
references/source-inventory
references/adversarial-review
```
