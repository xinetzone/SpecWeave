---
type: Reference
id: "openkylin-docs-wiki"
title: "openKylin 官方文档平台学习教程（OKF Wiki）：237 篇社区文档的逆向导读"
category: "tech"
tags:
  - openkylin
  - linux-distro
  - docsify
  - documentation-map
  - community-governance
  - ukui
  - ai-sdk
  - risc-v
date: "2026-09-29"
last_updated: "2026-09-30"
status: "verified"
author: "SpecWeave Agent（方法论编排 session sc-20260929-openkylin-docs-wiki）"
summary: "以七概念方法论（R→I→E→V→C，standard）系统学习 openKylin 官方文档平台 docs.openkylin.top：递归解析 Gitee 源仓库 3181 条目/237 篇中文文档、精读 35 篇代表性文档、提取 44 条客观事实，形成 4 条四元组洞察与 1 个 L1 可迁移模式（逆序文档学习法）。教程按学习者问题域重组为平台地图、版本生命周期、安装路径、桌面使用、AI 三层体系、开发者基础设施、社区治理 7 个概念页，附信源台账与完整文档分类地图。"
security_level: "public"
knowledge_type: "conditional"
validation_status: "verified"
reuse_count: "0"
integrity: "unchecked"
source: "一手信源：openKylin 文档平台 https://docs.openkylin.top/zh/home 与其 Gitee 源仓库 https://gitee.com/openkylin/docs（master 分支，采集于 2026-09-29，含 Gitee API v5 文件树与提交记录）；精读文档路径见 references/source-inventory.md。本机交叉验证：Windows 10.0.19044 + WSL 2.9.3 上的 openKylin 3.0 WSL 安装实测（见 references/wsl-install-sparse-vhd-guide.md）。"
---

# openKylin 官方文档平台学习教程

> 一句话摘要：openKylin 官方文档平台（docs.openkylin.top）不是一本与版本同步的官方手册，而是一个由 docs SIG 与社区贡献者滚动维护的 **237 篇中文文档知识库**——用户教程密度极高（77% 在入门板块）、工程基础设施手册完整、但新旧内容并存且入口页偏旧。本教程不逐页转写，而是先逆向解析文档库的真实结构，再按学习者的问题域重组为 7 张知识地图，所有结论可回溯到源文件。

- **编排 session**：`sc-20260929-openkylin-docs-wiki`
- **场景与链路**：场景 4 知识沉淀，`R→I→E→V→C（入库）`，depth=standard
- **采集时点**：2026-09-29（仓库最近提交为 2026-09-28）
- **同包伴生文档**：[openKylin 全面调研：从桌面根社区到 Agent OS](references/project-overview.md)（62 条事实，信源为官网新闻）回答"openKylin 是什么"；[WSL 安装与稀疏 VHD 实操指南](references/wsl-install-sparse-vhd-guide.md)（Windows 10 本机实测）回答"最小镜像怎么装、踩坑怎么办"；[双 WSL 镜像对照与选型参考](references/wsl-dual-image-selection.md)（2026-09-30 追加远程核验、**2026-10-08 完成落机实测**）回答"6.1G Desktop WSL 镜像与最小镜像差在哪、要占多少盘、怎么选"。本教程以**文档平台**为信源回答"官方文档怎么读、怎么用、怎么参与"，四篇事实互证、视角互补（2026-09-29 由原独立目录 `docs/knowledge/tech/openkylin/` 合并入本知识包）。

---

## 0. 快速导航：按你的问题出发

| 我想…… | 去读哪一篇 |
|---|---|
| 一分钟看清文档平台有什么、质量如何分布 | [01 平台与源仓库地图](concepts/01-platform-and-repository.md) |
| 确认该装哪个版本、LTS 与创新版怎么选、代号什么意思 | [02 版本发布与生命周期](concepts/02-release-lifecycle.md) |
| 选安装路径（物理机 / 虚拟机 / WSL / ARM / RISC-V） | [03 安装路径全景与选型](concepts/03-install-paths.md) |
| 装完后上手桌面、装软件、查 FAQ | [04 桌面环境与基础使用](concepts/04-desktop-usage.md) |
| 用本地/云端大模型、了解 AI SDK 能力 | [05 AI 三层体系：使用、配置、开发](concepts/05-ai-stack.md) |
| 签 CLA、编译软件包、构建定制镜像、提交代码 | [06 开发者基础设施](concepts/06-developer-infrastructure.md) |
| 加入 SIG、理解治理组织、做软硬件适配认证 | [07 社区治理与贡献路径](concepts/07-community-and-contribution.md) |
| 核查本教程每条结论的出处 | [信源台账](references/source-inventory.md) ／ [237 篇文档完整分类地图](references/full-catalog.md) |
| 先了解 openKylin 项目本身（版本时间线、版图界定、选型建议） | [项目全面调研](references/project-overview.md) ／ [WSL 本机实测](references/wsl-install-sparse-vhd-guide.md) |
| 比较 336M 最小 WSL 与 6.1G Desktop WSL 两个镜像、规划磁盘 | [双 WSL 镜像对照与选型参考](references/wsl-dual-image-selection.md)（桌面镜像已于 2026-10-08 落机实测：51.6 秒导入、1900 包、VHD 13.0 GiB、同盘峰值 19.2 GiB） |
| 已装好 Desktop WSL，想知道**每天怎么打开桌面/一键启动器/黑屏怎么办** | [openKylin 桌面启动与日常使用教程](references/wsl-desktop-startup-tutorial.md)（2026-10-08 实测：双击启动器→xorg 登录→关闭语义→FAQ） |
| 评估产品/硬件/智能体适配 openKylin 3.0 的工作量与风险 | [openKylin 3.0 架构适配评估草案](references/openkylin-v3-adaptation-assessment.md)（v0.1 纸面预评估，待 POC 验证） |

---

## 1. R 阶段：客观事实清单（F-001 ~ F-044）

> G1 已通过：全部为可验证客观陈述，无因果推断词；数字、URL、文件路径、日期完整记录；官方文档原文的自我标注（如"需要更新""失效文档"）以引号显式保留。来源键 [Sxx] 对应[信源台账](references/source-inventory.md)。

### 1.1 A 组：文档平台与源仓库元信息

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | 文档平台地址为 https://docs.openkylin.top/zh/home ，首页标注由 openKylin 社区 docs SIG（文档兴趣小组）负责维护，工作内容为收集问题、书写教程与答疑文档 | [S01] |
| F-002 | 文档源仓库为 Gitee `openkylin/docs`（https://gitee.com/openkylin/docs），仓库描述为"openKylin文档平台所有文档存放地址"；采集时点 Star 92、Watch 28、开放 Issues 6、开放 PR 1 | [S02] |
| F-003 | master 分支根目录含 8 个编号中文目录（1入门与参与、2标准与规范、3版本规划与发布、4开发与设计、5适配与上架、6社区活动、7关于社区、8最新动向）、`en` 英文目录、`home.md`、1 篇根级虚拟机安装指南与 1 个 docx 文件 | [S03] |
| F-004 | 经 Gitee Git Trees API 递归统计，仓库总条目 3181（truncated=false）；剔除 `en/` 与 `assets` 图片资源后，中文区共 237 个 Markdown 文件 | [S03] |
| F-005 | 237 篇文档的板块分布：1入门与参与 183 篇（下分 1_4基础操作 68、1_5基础设施平台指南 61、1_3系统下载与安装指南 21、1_2社区贡献 23、1_1新手入门 5、1_6常见问题 5）；2标准与规范 4；3版本规划与发布 3；4开发与设计 26（其中 4_9桌面设计 22）；5适配与上架 2；6社区活动 2；7关于社区 14；8最新动向 1；根目录散置 2 | [S03] |
| F-006 | 站点呈 docsify 形态：URL 直接指向 `.md` 文件（如 `/zh/07_关于社区/社区简介.md`），请求 `/_sidebar.md` 与 `/zh/_sidebar.md` 均返回站点"未找到"页；根目录 `home.md` 为首页正文 | [S01][S03] |
| F-007 | 首页"关于许可证"声明：仓库默认使用 CC BY-SA 4.0 许可证，贡献者可在自己文档下标明其他 CC 许可证版本；文档末尾插入许可声明后页面自动生成许可证标识 | [S01] |
| F-008 | 首页公布的文档贡献内容要求包括：文件用无 BOM 的 UTF-8 编码、`.md` 后缀；含标题、作者与创建时间；图片建议 PNG、高度约 640px、宽度不超过 820px、大小不超过 150K，统一放同级资源目录；仓库内跳转用相对路径；主分支不接受 dev 以外分支的 PR 与直接推送；禁止任何分支强制推送 | [S01] |
| F-009 | docs SIG 通信渠道为邮件列表 docs@lists.openkylin.top（含订阅页面）；首页列出 4 名成员：陌生人、chipo、AICloudOpser、delong1998 | [S01] |
| F-010 | 仓库最近 12 条提交时间范围为 2026-09-10 至 2026-09-28，内容集中于 GPU/文件操作 FAQ 更新、openkylin SDK 开发指南新增（!517/!515）、FAQ 文档贡献指南分支说明修正（!518）、i18n 规范英文文档更新（!515）；提交信息携带 Gitee 合并请求编号 | [S04] |

### 1.2 B 组：版本制度与代号

| 编号 | 事实 | 来源 |
|---|---|---|
| F-011 | 《openKylin 操作系统版本规划》文首标注"2026年4月9日 TC 表决通过"，确立"稳定 LTS + 前沿创新"双轨并行发行策略 | [S05] |
| F-012 | 制度规定：LTS 每 3 年发布一个主版本，维护周期 2+3 年（24 个月主动维护 + 36 个月被动维护）；创新版本每 1 年发布一个，维护周期 12 个月（仅被动维护），定位为"新技术的试验田和验证平台" | [S05] |
| F-013 | 版本规划列出：openKylin 2.0 LTS 代号 Nile，2024-08-08 发布，Linux 6.6 LTS，主动维护 24 个月 + 被动维护 36 个月，服务终止约 2029 年 8 月；openKylin 3.0 创新版代号 Huanghe，计划 2026 年发布，Linux 7.0，被动维护 12 个月 | [S05] |
| F-014 | 3.0 规划页列出的组件版本：GCC 15.2、LLVM 22、glibc 2.42、Mesa 26.0、OpenSSL 3.5；另列强化 RISC-V RVA23 支持、AI 推理框架端侧优化两项方向 | [S05] |
| F-015 | 工程平台文档中的系列代号：OKBS 说明里源码包 changelog 示例代号为 yangtze；版本构建平台说明写明 1.0 软件源代号 yangtze、2.0 软件源代号 nile | [S06][S07] |

### 1.3 C 组：安装文档矩阵

| 编号 | 事实 | 来源 |
|---|---|---|
| F-016 | 1_3 安装板块 21 篇文档分 4 簇：通用 x86 安装 7 篇（物理机安装简记/通用安装指南两版/MacOS/Hyper-V/virt-manager/2.0 SP2 虚拟机新手指南）、ARM 设备 6 篇（双椒派、coolpi、树莓派、飞腾派、香橙派 AIpro 与总览）、RISC-V 7 篇（LicheePi4A、Milk-V Pioneer、RuyiBook、SpacemiT K1、UR-DP1000、qemu 上的 RVA23 版本与总览）、WSL 1 篇 | [S03] |
| F-017 | 《openKylin-WSL版本安装》要求 Windows 10 2004（内部版本 19041）及以上或 Windows 11；提供两个镜像——基础镜像 `openKylin-3.0-wsl-amd64.wsl` 与可选桌面镜像 `openKylin-3.0-desktop-wsl-amd64.wsl`；导入命令为 `wsl --import openKylin .\openKylin <镜像> --version 2` | [S08] |
| F-018 | WSL 指南写明镜像预置默认用户，用户名与密码均为 `openkylin`；桌面镜像通过 xrdp 远程桌面访问，默认端口 3390，Windows 远程桌面连接时 Session 选择 xorg，WSL 重启后内网 IP 可能变化需重新获取 | [S08] |
| F-019 | 1_1 新手入门的《05_openKylin》特性页章节为：版本特性、多架构支持、UKUI 4.0 桌面环境、应用生态、分级冻结机制、互联互通、KMRE 移动兼容运行环境、VirtIO-GPU 硬件视频加速、自研开发者套件、虚拟键盘；1_1 的 5 篇中 4 篇文件名带"（需要更新）"标注 | [S03][S09] |

### 1.4 D 组：桌面使用、FAQ 与 AI 实操

| 编号 | 事实 | 来源 |
|---|---|---|
| F-020 | 《openKylin新手使用指南》覆盖：系统更新、触摸板指针速度调节、系统快捷键与截图快捷键、开启 SSH 登录、apt 安装/卸载/更新命令、wget 下载、dpkg 安装、命令行打开控制面板 | [S10] |
| F-021 | 《常用软件安装》收录 360 浏览器、Google Chrome（apt 源方式）与微信、腾讯会议、腾讯文档、ToDesk、EasyConnect、Notepad--（DEB 包方式）及 PyCharm（其他/编译方式） | [S11] |
| F-022 | 《端侧 AI 模型管理》写明麒麟模型管理工具包名为 `kylin-ai-model-manager`（新系统默认集成，可 `sudo apt install` 补装）；模型分三类：nlp 1 个、speech 5 个、搜索 2 个；下载需访问 modelscope.cn（魔搭社区） | [S12] |
| F-023 | 《基于openKylin本地部署并运行DeepSeek-R1开源模型》基于 ollama：三种安装方式（官方 install.sh、GitHub release v0.5.7 手动解压、公众号网盘），`ollama serve` 启动服务，`ollama run deepseek-r1:<规格>` 支持 1.5b/7b/8b/14b/32b/70b 六种蒸馏模型规格 | [S13] |
| F-024 | AI 模型配置指南系列共 7 篇，按 AI 子系统版本分线：1.3.0.0 系列的公有云模型接入、局域网文本类模型接入、本地文本类模型包构建；1.0.0.0–1.2.0.0 系列的云端模型与自选模型接入；另有 openKylin 免费 token 接入指南与 Qwen2.5-3B 上架说明 | [S03] |
| F-025 | 总览 FAQ 含约 20 个条目：apt 依赖关系修复、apt 文件冲突导致安装失败、显示器信息查看、apk 包安装、版本升级、USB 3.0 检查、CPU/大小核/虚拟化/内存/硬盘/电池/声卡/主板 BIOS 信息查看、终端补全忽略大小写、root 密码设置、默认终端更改、OBS Studio 安装、磐石架构手动安装软件包、"当前模式禁止执行 unpack 操作"报错 | [S14] |
| F-026 | 另有三个专题 FAQ：GPU 常见问题、文件操作常见问题、网卡常见问题；《无线网卡支持》11252 字符，按制造商/版本/网卡组织并翻译自 Ubuntu WifiDocs；《从NVIDIA官网安装闭源显卡驱动》5721 字符，含远程服务器命令行安装方式 | [S03] |

### 1.5 E 组：开发者基础设施与工程文档

| 编号 | 事实 | 来源 |
|---|---|---|
| F-027 | 两大工程平台有独立操作手册：OKBS 软件包编译平台 https://build.openkylin.top/ （注册账户、创建 PPA、上传 SSH 与 PGP 公钥、配置 dput 经 sftp 上传至 upload.build.openkylin.top:2121、在 archive.build.openkylin.top/dput-logs/ 查处理结果）；版本构建平台 https://factory.openkylin.top/ （需 openKylin ID 并申请权限，创建 livebuild 类型任务、选择或继承软件源快照、配置 live/iso 包列表、经 hooks/includes/packages 等目录上传定制文件） | [S06][S07] |
| F-028 | 1_5 下"开发者开发指南"约 30 篇，含 openKylin+SDK 开发指南、开发环境配置、打包指南、源码包 git 工作流、源码自主选型构建流程（15013 字符，含选型策略、软件分级与兼容性原则、debian 打包目录制作）、ISO 定制、输入法适配、三类应用移植（Windows/移动/其他发行版）、签名认证、编译构建、调试追踪、软件包维护、软件协议规范、nodejs 环境、本地编译 Pytorch、RISC-V Arduino IDE 等 | [S03] |
| F-029 | 《OpenKylin AI SDK 开发手册》137519 字符、4929 行，一级章节为 8 个能力域：1 文字识别、2 音频处理、3 向量化、4 文本生成、5 图像生成、6 主体分割、7 通用分割、8 通用错误码；接口形态含会话创建/初始化/销毁、结果回调函数、模型配置（模型名称与部署类型）等 | [S15] |
| F-030 | 4开发与设计另含：openkylin SDK 开发指南（4_11，2026-09 新增）、《openKylin 维护模式进入与退出操作手册》（`mm-cli` 命令、临时/永久模式、开机菜单入口与 4 条常见问题）；4_9 桌面设计 22 篇为 UKUI 专题（UKUI3 框架、UKUI4 设计理念与色彩/布局/图标/对话框/指针/触控手势/界面用语/空状态等设计指南） | [S03][S16] |
| F-031 | 《CLA签署说明》定义 CLA（Contributor License Agreement）约束版权归属、专利授权与法律声明三部分；签署入口 https://cla.openkylin.top ，按身份分个人 CLA、员工 CLA、企业 CLA | [S17] |
| F-032 | 《openKylin社区贡献角色》定义三级角色且权责限于各自 SIG 内：Contributor（参与贡献、响应任务，以超过 2/3 票数参与 SIG 重大决策，可提名核心成员选举）、Maintainer（评审 PR、维护软件包版本、跟踪安全问题、与上游社区协作）、Owner（确定技术路线与发布计划、代表 SIG 参与技术委员会、紧急决策、选举/撤销核心成员） | [S18] |

### 1.6 F 组：治理、贡献路径与适配认证

| 编号 | 事实 | 来源 |
|---|---|---|
| F-033 | 《openKylin贡献攻略》列出 5 条贡献路径：测试、提交或解决 Issue（issue 集合在 gitee.com/openkylin/community/issues）、软件拓展建议（发邮件 contact@openkylin.top，文中写"3天内审核、尽量2周内完成适配上架"）、贡献代码/工具（在 gitee.com/openkylin 组织提交 PR）、非代码贡献 | [S19] |
| F-034 | SIG 治理文档共 12 篇：新 SIG 申请、加入、贡献、运营、撤销、会议管理、活跃奖惩、会议议题模板、基本信息变更、章程、章程模板、Owner 增选与撤销；新 SIG 流程为"Gitee 项目页申请 → 技术委员会审核 → 创建邮件列表等基础设施 → 开始运作" | [S03][S19] |
| F-035 | 《openKylin社区AI辅助贡献守则》文档属性日期为 2026-08-01，共 9 节：允许 AI 辅助理解/草稿/补全/润色/翻译/排查，但贡献者负完整责任；实质性 AI 内容须按模板披露（AI usage/Tool·model/Usage/Human review，或提交信息加 Assisted-by 与人类 Signed-off-by）；禁止不验证直接复制、提交无法解释的内容、批量低质 PR/Issue、编造测试与性能数据、未经批准的 AI Bot 自动操作；禁止向外部 AI 服务上传未公开代码、隐私、漏洞细节、API Key/Token/密码/证书/私钥 | [S20] |
| F-036 | 《非代码贡献指南》定义志愿者四组：核心组织者、城市站/高校站、媒体组（B 站/抖音视频、公众号技术博文、KOL 合作）、设计组；权益含实践证书、内推、定制周边等；加入方式为发邮件至 contact@openkylin.top | [S21] |
| F-037 | 《社区治理组织架构》列 5 个治理组织：理事会（指导发展方向与长期规划）、秘书处（日常办事、执行理事会决议）、技术委员会（决策技术方向、管理 SIG 组）、咨询委员会（政策/技术趋势/开源规则顾问）、生态委员会（构建生态与品牌影响力） | [S22] |
| F-038 | 软件适配与硬件适配两篇指南流程同构：官网"支持→兼容适配"入口 → 腾讯文档在线申请表 → 百度网盘下载适配报告模板 → 编制并提交测试报告（硬件适配另要求 1080p 以上 MP4/AVI 视频，含安装过程、AI 助手/UKUI 功能与兼容性演示）→ 7 个工作日内技术团队审核 → 颁发产品兼容证书并在官网公示，优秀案例入选技术全景案例集 | [S23][S24] |
| F-039 | 7关于社区板块含《关于 openKylin 社区》（正文为 27 张图片、无文字段落）、组织架构 6 篇（技术委员会/理事会/秘书处/治理架构总览/生态委员会/咨询委员会）、政策与规则 7 篇（安全策略、贡献者协议、TC 委员增选、免责声明、成员守则、社区管理规范、issue 报告规范） | [S03] |
| F-040 | 文档库存在多处时效性自标注：8最新动向仅 1 篇 419 字符的运营报告索引页；3_3版本历史发布仅 SP1 一篇；1_1 新手入门 5 篇中 4 篇标题含"（需要更新）"；1_4 中设有"失效文档"子目录（收录《【过时】源服务器的地址更换兰州大学镜像》） | [S03] |
| F-041 | 6社区活动板块含《openKylin用户组（OKUG）介绍》与《openKylin开发者大赛活动介绍》各 1 篇；2标准与规范含个人开发者参与指南（正文 166 字符）、需求管理规范、i18n SIG 规范中英文各一篇 | [S03] |
| F-042 | 部分文档保留历史编号路径与占位链接：硬件适配指南中的安装教程链接指向 `/zh/01_安装升级指南/...`，与当前仓库 `1入门与参与/1_3系统下载与安装指南/` 的实际目录不一致；《贡献攻略》中多处链接为空括号占位或被 HTML 注释包起的 TODO | [S19][S24] |

### 1.7 G 组：与本仓既有知识的交叉验证

| 编号 | 事实 | 来源 |
|---|---|---|
| F-043 | 同知识包 references/ 收录两份同会话伴生产出：project-overview.md（openKylin 项目全面调研，62 条事实，信源以 openkylin.top 官网新闻为主；原独立目录 `docs/knowledge/tech/openkylin/index.md`，2026-09-29 C 阶段合并迁入）与 wsl-install-sparse-vhd-guide.md（3.0 WSL 镜像本机安装实测，同日迁入） | [S25][S26] |
| F-044 | 本机实测环境为 Windows 10.0.19044 + WSL 2.9.3.0，满足官方指南 19041 门槛；实测记录中 `wsl --import`/`--install --from-file` 出现过 `RegisterDistro/E_UNEXPECTED` 与 `CreateVm/E_ABORT` 报错，报错时点空闲物理内存记录值一度为 0.8GB，内存充裕（≥4GB）并解压为纯 tar 后导入成功；官方 WSL 指南的常见问题仅覆盖"WSL2 内核未安装"与"远程桌面连接失败"两项 | [S08][S26] |

### 1.8 H 组：Desktop WSL 双形态远程核验（2026-09-30，F-045 ~ F-050）＋落机实测（2026-10-08，F-051 ~ F-057）

> G1 已通过（专项 session `sc-20260930-openkylin-desktop-wsl`，22 条会话内事实的索引级摘要；完整记录与命令见 [双 WSL 镜像对照与选型参考](references/wsl-dual-image-selection.md)）。F-045～F-050 除 F-050 外均为**文件级远程事实**；**F-047/F-050 的运行时未知项已由 2026-10-08 落机 session `sc-20261008-openkylin-desktop-wsl-install`（信源 S33）闭环，新增 F-051～F-057 为运行时实测事实**：导入/容器/VHD/xrdp 服务与**交互 UKUI 桌面全链路**均实测通过，首登黑屏根因与修复见 F-057（仅余 `--shutdown` IP 漂移等长期观察项）。

| 编号 | 事实 | 来源 |
|---|---|---|
| F-045 | 下载中心 3.0 x86 有两个 WSL 条目（id=126 最小 / id=127 Desktop），构建日期均为 2026-08-28、仅 AMD64；CDN 真实文件分别为 `openKylin-3.0-wsl-amd64.wsl`（352,431,812 字节，MD5 `3c5717cfde5c032c69122fb14fa8e2fa`）与 `openKylin-3.0-desktop-wsl-amd64.wsl`（**6,592,986,686 字节 = 6.14 GiB**，MD5 `df559de7155ef7c6fe088b2168035c5a`，官网展示"6.1G"） | [S27][S28] |
| F-046 | 两镜像 Range 取头 4 字节魔数均为 `1F 8B 08 00`（gzip）；桌面前 20 MiB 流式解压后 tar 列目为标准 rootfs 结构（`./dev`、`./bin`、`./sbin`、`./run/systemd`），与最小镜像同构，导入机制相同 | [S29] |
| F-047 | 桌面镜像 gzip 尾部 ISIZE=103,258,112 字节（98.5 MiB），小于压缩体积，已发生 4 GiB 回绕；真实解压 tar 为候选序列 8.1 / 12.1 / 16.1 / 20.1 GiB（k=2~5，k≥6 不排除）；最小镜像实测压缩比 3.36× 仅提供"真值倾向不高于该倍数"的方向性参考，现有证据不足以在候选间排序、不给点估，~~未消歧~~**已于 2026-10-08 经 F-053 落机消歧为 k=3（12.1 GiB，1.97×）**；最小镜像 ISIZE=1,182,607,360 字节未回绕，与实测一致 | [S29][S33] |
| F-048 | 官方文档桌面分支：`wsl --import openKylin-desktop .\openKylin-desktop <镜像> --version 2`；启动后 `ip addr show eth0` 取 IPv4，mstsc 连 `<IP>:3390`，Session 选 **xorg**，账号密码同为 `openkylin`；xrdp 默认自启，WSL 重启 IP 可能变 | [S30] |
| F-049 | 官方文档对桌面镜像未提供磁盘/内存门槛、软件包数、VHD 实大、稀疏 VHD、导入失败排障（FAQ 仍仅 2 条）；bbs.openkylin.top 站内检索与公开搜索引擎（2026-09-30）未见桌面 WSL 用户实测帖，官方文档是唯一公开一手操作信源（负证据，覆盖受限） | [S30][S31] |
| F-050 | 2026-09-30 本机 C: 剩 2.3 GB、D: 剩 4.8 GB，任何候选占用下均不具备桌面镜像导入条件，故当时全部运行时项登记为待实测；~~待实测清单~~**已于 2026-10-08（C: 61.2/D: 54.9 GiB 空闲）由 F-051～F-056 闭环 8/9 项**，残留交互桌面观感 | [S32][S33] |
| F-051 | 2026-10-08 落机下载与校验：curl 断点续传约 3 分钟下完 6.14 GiB；字节数 6,592,986,686 与 MD5 `df559de7155ef7c6fe088b2168035c5a` 精确一致，魔数 `1F 8B 08 00`；镜像自 2026-08-28 构建后至该日未更新 | [S33] |
| F-052 | 落机导入：Win10 26220 + WSL 3.0.2.0（内核 6.18.40.1-1），`wsl --import openKylin-3.0-desktop` 直接喂 gzip `.wsl`，**51.6 秒一次成功零失败**（导入前空闲内存 11.94 GiB）；磁盘差值对账证实**流式写入、不落临时 tar**；导入不改变默认发行版星标（前后均为 podman-machine-default） | [S33] |
| F-053 | 容器验收：openKylin 3.0 (huanghe)，默认用户 openkylin UID 1000（sudo 接受 openkylin 口令），wsl.conf 含 default=openkylin 与 systemd=true；软件包 **1900**（最小镜像 405，桌面增量 +1495，逐包包含关系未 diff）；`df -B1 /` 有效数据 13,380,390,912 字节（12.46 GiB），双向夹逼把 F-047 候选定档 **k=3（tar≈12.1 GiB，1.97×）** | [S33] |
| F-054 | VHD 实测：`ext4.vhdx` 逻辑大小＝真实占用（非稀疏）13,971,226,624 字节＝**13.01 GiB**；VHD/ext4 有效数据=**1.044**、VHD/tar(k=3)≈1.075——修正最小镜像单点外推的 1.17 系数（非常数）；同盘标准路径峰值实测 **19.2 GiB**（D: 54.88→35.73 GiB，＝.wsl 6.14＋VHD 13.01），事前 20/25/30 GiB 建议线全部安全 | [S33] |
| F-055 | xrdp 服务链路开箱可用：`xrdp`/`xrdp-sesman` 均 enabled+active、`ss -lnt` 见 `*:3390` LISTEN；eth0 IPv4=172.25.189.68，`--terminate` 后未漂移；Windows 侧 `Test-NetConnection 127.0.0.1 -Port 3390` 成功，**`mstsc /v:localhost:3390` 可用、绕开 IP 漂移**（官方文档只给 `<IP>:3390`）；**交互桌面实测：mstsc→xorg→openkylin 可进入完整 UKUI（壁纸/任务栏/开始菜单/图标齐全）**；首登命中纯黑屏，经 F-057 修复后重登验证通过 | [S30][S33] |
| F-056 | systemd 失败面：`systemctl --failed` 全机仅 1 个失败单元 `systemd-binfmt`——WSL 宿主预置 WSLInterop binfmt 注册致重复注册退出 1，单元自带 generator drop-in 在失败后重注册 `:WSLInterop:M::MZ::/init:FP`（良性且有自恢复证据）；未见 acpid/蓝牙/电源等硬件相关服务失败；未执行稀疏化（全新系统逻辑＝真实占用、无洞可回收）与 unregister（用户保留发行版） | [S33] |
| F-057 | **首登纯黑屏根因与修复（2026-10-08 实测闭环，详见双镜像文档 §5.1）**：openKylin 3.0 UKUI 4.x 的 WM 是 **KWin**（`kwin-x11` 已预装，非旧 ukwm）；`/etc/xrdp/startwm.sh` 里 `unset XDG_RUNTIME_DIR`，ukui-session 经 ukuismserver 在 Xorg ready ~1 秒后拉起 kwin，因运行时目录缺失（回退无效 `/var/tmp/runtime-openkylin`）冷启动不驻留、会话不重试 → 无合成器黑屏（ukui-panel/peony 等其余组件正常）。修复：用户级 `~/.xsession` 补 `export XDG_RUNTIME_DIR=/run/user/$(id -u)` + 前 15 秒幂等 WM 看门狗（原文件备份 `.xsession.bak-20261008`，不改系统文件/不装包）；重登后存活 kwin 父进程链 `kwin_x11←ukuismserver←ukui-session←xrdp-sesexec`、环境变量正确，证明决定性修复是补环境变量、看门狗仅兜底 | [S33] |

---

## 2. I 阶段：核心洞察（四元组）

> G2 已通过：每条含 **陈述 / 证据（F 编号）/ 反常识 / 行动**，四个维度（库结构、时效性、AI 证据链、工程治理）互不重叠。

### I-1　文档库呈"倒金字塔"：77% 是用户教程，规范性文档稀疏且含占位页

- **陈述**：237 篇中文文档中 183 篇集中在"1入门与参与"（77%），其中基础操作 68 篇、基础设施 61 篇；而"2标准与规范"仅 4 篇、"3版本规划与发布"仅 3 篇，且个人开发者参与指南（166 字符）、文档平台使用指南（159 字符）、社区项目地图（155 字符）等为占位性短页。
- **证据**：F-004/F-005（数量分布）、F-040（占位与"需要更新"自标注）、F-006（docsify 形态）、F-041（规范与活动板块篇数）。
- **反常识**：直觉上"官方文档平台"应是一本结构完整、权威统一的手册；实际形态更接近**社区贡献者滚动维护的知识库**——遇到什么问题补什么教程，操作类内容快速增厚，制度类内容依赖少量正式文件且更新不勤。
- **行动**：使用该站时采用"三分法"——**找操作步骤去文档站、查制度与版本事实去仓库正式文件与 TC 记录、追最新动态去官网新闻与提交记录**；引用任何条目之前先核对页面时效标记与适用版本，不把文档站当作单一权威源。

### I-2　时效性两极分化：新人入口最旧，治理与 AI 板块最新

- **陈述**：文档库同时存在两个年代层——2026 年层包括版本规划（2026-04 TC 表决）、AI 辅助贡献守则（2026-08）、3.0 WSL 指南、9 月仍在更新的 GPU/文件 FAQ 与 SDK 指南；旧层包括特性仍写 UKUI 4.0/KMRE 的 1.0 时代新手页（4/5 标注"需要更新"）、"失效文档"目录、旧编号路径链接与空 TODO 链接。
- **证据**：F-010（最近提交）、F-011（版本规划日期）、F-019（新手页内容与更新标注）、F-040（失效与占位）、F-042（旧路径与死链）、F-035（AI 守则日期）。
- **反常识**："官方文档与最新版本同步"在此不成立；更反直觉的是**最旧的内容恰好位于新人入口**（1_1 新手入门），首次接触者被陈旧信息误导的概率最高。
- **行动**：学习顺序改为"**从新版本规划页倒推**"——先用 [02 版本发布与生命周期](concepts/02-release-lifecycle.md)确认代号与代际，再读教程；教程页若无版本标注，就用其中出现的组件版本（UKUI 大版本、内核版本、子系统版本号）推断其适用代际；发现旧路径/死链时回源仓库按文件树重定位。

### I-3　AI 能力在文档站留下"三层成文"证据链，比发布会特性更硬

- **陈述**：AI 内容在文档库分三层且均有可操作文档：用户层（`kylin-ai-model-manager` 工具与 ollama 跑 DeepSeek-R1 六档规格）、配置层（按 AI 子系统 1.0–1.3 版本分线的 7 篇模型接入指南与免费 token 指南）、开发层（137K 字符/4929 行的 AI SDK 手册，覆盖文字识别、音频、向量化、文本/图像生成、分割与错误码 8 个能力域）；治理层另有 AI 辅助贡献守则。
- **证据**：F-022（端侧工具与包名）、F-023（ollama 实操）、F-024（配置层分版文档）、F-029（SDK 能力域与规模）、F-035（治理守则）。
- **反常识**：判断一个操作系统是否"AI 原生"，发布会特性表属于营销叙事；文档站给出的是**别人能否照着做出来的证据**——apt 包名、模型托管站点、会话接口与错误码齐备，意味着能力已进入可复用的平台阶段。新闻里的"智能体底座"是声明，SDK 手册是证据。
- **行动**：评估任何 OS 的 AI 能力用"三层成文度"清单——有无一键本地工具？有无按版本维护的模型接入文档？有无带错误码的开发者 API 手册？有无配套贡献治理规则？四层齐备可将其能力从"特性宣传"升级为"平台级候选"。
- **证据边界（V 审查补充）**："成文度"是必要条件而非充分条件：本教程未实机安装 AI SDK 开发包、未逐接口跑通 8 个能力域、未核验各模型文件在 modelscope 的当前可下载性；文档规模与接口形态只能证明"能力被设计并文档化"，不能证明"在任何硬件上当下可用"。最终采信仍需一次最小 POC（装包→调通一个文字识别或文本生成接口）。

### I-4　开发者板块实为供应链基础设施操作手册，是"根社区"独立性的操作层证据

- **陈述**：访客最容易忽略的 1_5 板块（61 篇）包含 CLA 三类签署、OKBS 编译平台（PPA/SSH/PGP/dput）、factory 版本构建平台（软件源快照、live/iso 包列表、hooks/includes/packages 定制目录）、源码自主选型构建流程与 ISO 定制；制度层还有 TC 表决通过的双轨版本制、12 篇 SIG 治理文件、7 工作日审核的适配认证流程。
- **证据**：F-027（两大平台手册）、F-028（约 30 篇开发指南与选型流程）、F-031（CLA）、F-034（SIG 制度）、F-037（治理五组织）、F-038（适配认证）、F-011（版本制 TC 表决）、F-032（三级角色）。
- **反常识**：社区文档站常被定位为"给用户看的说明书"，但这里高密度的开发者文档实际是**供应链能否被外部复现的操作手册**；它从操作层支撑了姊妹篇调研中"根社区实质是供应链三自主"的结论——自主选型不仅是发布稿措辞，仓库里有逐命令的构建流程。
- **行动**：考察开源社区工程独立性时，在代码仓库之外增加"文档站四查"——是否自含软件包编译平台手册？镜像/版本构建平台手册？成员法律协议（CLA）签署入口？经技术委员会表决的版本制度文本？四项齐全说明第三方可按文档复现其供应链，而非只能接受成品镜像。

> **2026-09-30 专项追加**：Desktop WSL 双形态对照形成另外 3 条四元组洞察——①两按钮机制同源、差异仅在载荷规模，选型回归"要不要完整桌面会话"；②6.1G 是下载体积而非磁盘规划值，且 >4 GiB 后 gzip ISIZE 估算法静默回绕；③文件级事实可远程证伪、运行时事实只能本机证伪，同页两按钮证据等级不同。完整四元组见 [双镜像对照 §8](references/wsl-dual-image-selection.md)。

---

## 3. E 阶段：可迁移模式（G3）

> 本模式已于 2026-09-30 独立沉淀入方法论模式库，通用版（六步抽象、5 个反模式、跨领域迁移、与 RIEV 等模式的层级关系）见 [逆序文档学习法](../../../retrospective/patterns/methodology-patterns/research-knowledge/reverse-order-doc-learning.md)；本节保留本案例版摘要。

### 模式：逆序文档学习法（L1-draft，单案例待验证）

**一句话**：学习百篇级、多人贡献、时效不均的社区文档站时，不按官方目录顺读，而是先用版本控制接口还原"文档库真实结构与时效地图"，再按自己的问题域重组学习路径，并与外部信源交叉验证。

| 要素 | 内容 |
|---|---|
| **适用于** | 百篇以上、多人滚动贡献、页面无统一版本标注的社区/Git 托管文档站（docsify、Wiki、`docs/` 仓库形态） |
| **不适用于** | 单一作者的小型文档集；与产品版本严格对齐、有统一发布周期的商业文档（顺读即可） |
| **核心步骤** | ① 取文件树而非翻首页：用 Git 托管方 API 递归拉树，统计板块-文件分布，先量化"内容重心在哪"；② 骨架扫描：批量抓取标题行，识别占位页、高密度页与翻译页；③ 元信息定年：读最近提交记录与文件 frontmatter 日期，绘制新旧分层；④ 问题域重组：按"选型→安装→使用→开发→贡献"的学习者路径重组，不沿用官方目录顺序；⑤ 交叉验证：文档站与官网新闻、本机实测三方对照，冲突点与失效链接显式标注；⑥ 原子化产出：concepts 按问题域成篇、references 独立维护信源台账，每条结论可回溯 |
| **检验标准** | 读者不回源站即可完成关键路径决策；每篇教程的事实都能在信源台账定位到具体文件；陈旧内容与最新内容的边界对读者可见 |
| **反模式** | ① 从首页顺读（首页最可能营销化且最旧，本案例 F-019/F-040 证实）；② 把官方文档当均质权威、不做时效甄别（本案例新旧两层并存）；③ 全文转写式"翻译"（复制官方目录结构等于复制它的结构缺陷）；④ 只读正文不读元信息（文件树与提交记录恰恰暴露真实重心与活跃度） |
| **跨域迁移** | 可迁移至任意 Git 托管文档体系：学习 Apache/CNCF 项目文档时先拉仓库树统计、读 release 文档定年；厂商文档中心可用 sitemap + 更新日期替代 Git 元信息完成步骤①③ |
| **成熟度** | **L1-draft（单案例待验证）**：本次 openKylin 文档站为首次完整应用；步骤⑤的"本机实测交叉验证"有姊妹篇 WSL 实测（F-044）提供半个第二案例支撑。入库二次校验按模式库等级表维持 L1-draft：升级 L1.5 需第二个非同谱系文档站（非 docsify/Gitee 形态）完整应用，升级 L2-validated 另需本团队一次真实学习任务实战，通用版见[方法论模式库](../../../retrospective/patterns/methodology-patterns/research-knowledge/reverse-order-doc-learning.md) |

---

## 4. V 阶段：4 视角对抗审查

> 审查在教程初稿完成后执行，问题清单与采纳修正详见 [V 审查记录](references/adversarial-review.md)。V 门结论：4 视角全覆盖、意见 7 条（≥5）、采纳修正 6 条（≥2），**通过**。

---

## 5. 质量门与编排记录

| 门 | 标准 | 结果 |
|---|---|---|
| G1 | 事实 ≥20、无因果词、可溯源、数字/URL 完整 | PASS（44 条，分 7 组；自我标注内容保留引号） |
| G2 | 洞察 ≥3 且四元组完整、维度独立、含反常识与行动 | PASS（I-1~I-4：结构/时效/AI/工程治理） |
| G3 | 模式含适用边界、步骤、≥3 反模式、检验标准、跨域迁移、成熟度标注 | PASS（逆序文档学习法，L1-draft，案例版 4 反模式；2026-09-30 入库版扩为 5 反模式并登记[模式库](../../../retrospective/patterns/methodology-patterns/research-knowledge/reverse-order-doc-learning.md)） |
| V 门 | 4 视角、意见 ≥5 且具体、采纳 ≥2 并回归确认 | PASS（7 条意见，6 条采纳修正，1 条登记为局限） |
| G4 | 产出原子化：单一职责文件、可独立验证、链接与命名规范 | PASS（14 个原子文件：index + concepts 索引 1 + 概念页 7 + references 5；同日 C 阶段将原 `tech/openkylin/` 两篇伴生文档合并入 references/，toctree 经本 index 统一登记，链接与文件名检查通过） |
| **2026-09-30 专项**（session `sc-20260930-openkylin-desktop-wsl`，链路 R→I→E→V→C） | | |
| G1/G2 | 事实客观可溯源 ≥20；洞察四元组 ≥3 | PASS（会话内 22 条事实，索引摘要 F-045~F-050；3 条洞察见双镜像文档 §8） |
| G3 | 模式含边界/步骤/≥3 反模式/检验/迁移/成熟度 | PASS（[大归档零下载远程预检法](../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md)，L1 单案例，5 反模式，与 pretrained-model-download-validation 互补） |
| V 门 | 4 视角、意见 ≥5、采纳 ≥2 | PASS（4 视角 11 条意见全部采纳：候选区间保留 k≥6、包包含关系降级为推断、GiB/GB 双口径、同名冲突、WSLg 替代、弱口令红线、镜像时效） |
| G4 | 原子化产出 | PASS（新建参考文档 1 + 模式 1；更新 index/03-install-paths/wsl 指南/信源台账/模式 toctree 共 5 处；桌面镜像运行时项明确登记待实测，不伪造实测结论） |
| **2026-10-08 专项**（session `sc-20261008-openkylin-desktop-wsl-install`，落机安装链路 R→I→F→V→C） | | |
| G1/G2 | 实测事实客观可溯源、洞察四元组对账 | PASS（F-051~F-057 共 7 条运行时事实，信源 S33；双镜像文档 §4 增实测对账，I-2 更新为真值落定） |
| V 门 | 实测不夸大：服务级 vs 交互桌面级分开；事前推断逐条对账；黑屏先取证后修复 | PASS（五轮回填：4 项推断 3 证实 1 修正；六轮实战：首登黑屏以四类日志+父进程链定位 KWin/XDG_RUNTIME_DIR 根因，用户级修复重登验证，新增 §5.1） |
| G4 | 原子化产出 | PASS（更新 5 文件：wsl-dual-image-selection、wsl-install-sparse-vhd-guide 范围声明、03-install-paths、本 index、信源台账 S33；未新建文件；修复落在发行版用户家目录 `~/.xsession`，备份可回滚） |

**局限声明**：① 237 篇中精读 35 篇（含全部板块代表性文档与全部短占位页），其余以标题骨架覆盖，可能遗漏个别长尾操作细节；② 文档站内容随社区提交持续变化，本教程事实时点为 2026-09-29；③ 图片型页面（如 27 图版《关于社区》）未做 OCR，其信息以治理组织架构文字版互证；④ 未对 en 英文目录做对照统计；⑤ 本教程定位为"文档平台导读"，不对 openKylin 的生产环境适用性（稳定性、性能、硬件兼容、供应链合规）作独立验证结论——相关表述来自官方文档或姊妹调研口径，实际采用前须自行完成 POC（V 审查 O7 登记）；⑥ 2026-09-30 追加的 Desktop WSL 文件级事实（字节数/MD5/魔数/ISIZE/结构）为**远程核验级**，2026-10-08 已补充落机实测（F-051~F-057/S33：解压真值 k=3、流式导入 51.6 秒、1900 包、VHD 13.01 GiB、同盘峰值 19.2 GiB、xrdp 服务与交互 UKUI 桌面全链路可用）；首登黑屏（XDG_RUNTIME_DIR 致 KWin 不驻留）已实测定位并用户级修复（F-057，单次首登+一次重登验证，跨版本需重新取证）；引用规划值时须与实测值区分，**残留观察项**仅限：内存失败阈值下界（未测到失败）、整机 `--shutdown` 后 IP 漂移（localhost 接入可规避）、unregister 物理回收验证。

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20260929-openkylin-docs-wiki | msg=知识沉淀链路R→I→E→V→C | ctx={"chain":"R-I-E-V-C","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20260929-openkylin-docs-wiki | msg=44事实/4洞察/1模式(L1)/4视角7意见/14原子文件 | ctx={"gates":["G1","G2","G3","V","G4"],"deliverable":"docs/knowledge/tech/openkylin-docs-wiki/"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C2 | event=REFACTOR_MERGE | session=sc-20260929-openkylin-docs-wiki | msg=目录合并：tech/openkylin/ 两篇迁入 references/（project-overview/wsl-guide），包内7处+包外8处入链同步，toctree 收敛，旧目录删除 | ctx={"scenario":"refactor","chain":"A→V→C","inbound_links_fixed":15}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20260930-openkylin-wiki-pattern | msg=模式沉淀：逆序文档学习法入库方法论模式库（研究知识区） | ctx={"scenario":"knowledge","chain":"R-I-E-V-C"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20260930-openkylin-wiki-pattern | msg=新建模式文档+TOML，更新3处索引，回写本知识包，L1-draft/5反模式 | ctx={"gates":["G3","V"],"deliverable":"docs/retrospective/patterns/methodology-patterns/research-knowledge/reverse-order-doc-learning.md"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20260930-openkylin-desktop-wsl | msg=Desktop WSL 双形态知识沉淀：文档级调研+待实测清单，体积区间+保守规划值 | ctx={"scenario":"knowledge","chain":"R-I-E-V-C","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R9 | event=GATE_PASSED | session=sc-20260930-openkylin-desktop-wsl | msg=22事实纯客观：CDN HEAD/Range远程核验+官方文档重读+BBS负证据+本机磁盘快照 | ctx={"sources":"S27-S32","traffic_mib":25}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20260930-openkylin-desktop-wsl | msg=22事实/3洞察/1新模式(L1,5反模式)/4视角11意见/2新建+5更新；桌面运行时待实测 | ctx={"gates":["G1","G2","G3","V","G4"],"new_files":["references/wsl-dual-image-selection.md","../../../../retrospective/patterns/code-patterns/large-archive-remote-preflight.md"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V10 | event=REVISION_USER_DRIVEN | session=sc-20260930-openkylin-desktop-wsl | msg=二轮措辞修正：磁盘规划由≥45GiB单值改为三档分层（跨盘20/同盘25-30/排障45-50），补流式写入未实测假设说明，4文件同步 | ctx={"scope":"storage-planning-wording","files":4}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V11 | event=REVISION_USER_DRIVEN | session=sc-20260930-openkylin-desktop-wsl | msg=三轮措辞修正：选型倾向显性化，WSLg行改优先、新增「桌面镜像不是更好的WSL而是带桌面会话的WSL」定性，概念页同步 | ctx={"scope":"selection-bias-wording","files":2}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V12 | event=REVISION_USER_DRIVEN | session=sc-20260930-openkylin-desktop-wsl | msg=四轮措辞修正：候选区间去点估，删除16.1GiB「最可能」定性，§4.1改非概率排序、§4.2建议线改覆盖口径，F-047/概念页/局限⑥同步 | ctx={"scope":"candidate-point-estimate","files":3}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261008-openkylin-desktop-wsl-install | msg=Desktop WSL 落机安装：执行§7待实测清单 | ctx={"scenario":"problem","chain":"R-I-F-V-C","depth":"standard"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R9 | event=GATE_PASSED | session=sc-20261008-openkylin-desktop-wsl-install | msg=预检：D:54.88GiB/内存13.05GiB/WSL3.0.2.0；远程事实复核未变 | ctx={"sources":"S27-S28-S33"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C2 | event=IMPORT_OK | session=sc-20261008-openkylin-desktop-wsl-install | msg=下载约3分钟+MD5精确匹配；流式导入51.6秒零失败；1900包；k=3夹逼；VHD13.01GiB；峰值19.2GiB | ctx={"distro":"openKylin-3.0-desktop"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V9 | event=GATE_PASSED | session=sc-20261008-openkylin-desktop-wsl-install | msg=五轮回填：4项事前推断对账(3证实1修正)，F-051~F-056入库，5文件同步，唯一待实测=GUI观感
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261008-openkylin-desktop-wsl-install | msg=§7清单8/9闭环；新增事实6条；零新建文件 | ctx={"gates":["G1","G2","V","G4"],"files_updated":5}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=ROOTCAUSE_FOUND | session=sc-20261008-openkylin-desktop-wsl-install | msg=首登黑屏=XDG_RUNTIME_DIR被unset致KWin冷启动不驻留(非GL/安装) | ctx={"evidence":"4类日志+父进程链","fact":"F-057"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C3 | event=FIX_VERIFIED | session=sc-20261008-openkylin-desktop-wsl-install | msg=~/.xsession补环境变量+WM看门狗(备份)，重登进入完整UKUI；新增F-057与§5.1
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261008-openkylin-desktop-wsl-install | msg=桌面链路服务→交互全通，无遗留未决故障；事实7条(F-051~F-057) | ctx={"gates":["G1","G2","V","G4"]}
```
