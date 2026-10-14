---
title: "附录 C：Q-1~Q-8 待验证清单首轮核验记录（2026-10-14）"
id: openkylin-evaluation-20261014-verification-q1-q8
date: 2026-10-14
type: appendix-c
security_level: public
report: retrospective-openkylin-evaluation-20261014
method: "七概念场景4 R→I→E→V→C 之 V 后缺口复核（Q-Gate Round 1）"
session: sc-20261014-openkylin-evaluation
tags: [openkylin, verification, q-gate, lts-eol, distrowatch, openrank, gitee, security-evaluation, upgrade-path, kylin-ai]
---

# 附录 C：Q-1~Q-8 待验证清单首轮核验记录

> 核验日期：2026-10-14（与主报告同日，Q 门复核窗口提前执行）。方法：4 路独立公开网络调研（官方站点/政府公告/公开 API/第三方报告）+ 本机 okw WSL 发行版只读实测。每条事实附来源 URL；口径标注：【官方】openKylin/开放原子自有渠道、【厂商】麒麟软件、【政府】测评机构/部委、【第三方】独立平台/媒体/研究者、【一手实测】本机 okw 实测。负证据一律写明检索路径。

## 一、核验总览

| Q | 待验证项 | 本轮结论 | 关键新事实 | 复核窗口变化 |
|---|---|---|---|---|
| Q-1 | 社区版 LTS/EOL 与补丁政策 | **部分推翻原报告**：成文政策存在（2024 版 1+1；2026-04-09 TC 改为 LTS 2+3），但无逐版本 EOL 日期表、1.0 已无公告停维、新旧口径互相冲突 | VF-01~VF-11 | 90 天窗口保留（观察 3.0 维护节奏与 2029 口径是否修正） |
| Q-2 | 2.0/SP1→SP2/3.0 原地升级 | **定性完成、实测未做**：升级器在仓；官方明示 SP1 及更早→SP2「暂时无法妥善升级」；3.0 公告只提供全新安装/Beta 更新，无 2.0→3.0 路径 | VF-41~VF-45 | 待导入 2.0 SPx WSL 镜像后实测 |
| Q-3 | DistroWatch 排名与独立横评 | DistroWatch **已取得**（6 个月 #107、HPD 132；3 个月 #64）；独立第三方性能横评经 7 条路径仍未找到 | VF-20~VF-23 | 横评维持持续检索 |
| Q-4 | 2400 万套/用户数独立审计 | **结论强化为「仅厂商单源、外部全部转引」**：引用链追到 2025-06 CCF 鉴定自报材料；基金会 2025 年报刻意不列该数；另取得独立行为指标（OpenRank 3,180.90） | VF-24~VF-30 | 关闭（再开放需新审计源出现） |
| Q-5 | Gitee Star/OpenRank/下载量/第三方贡献占比 | 三项取得/部分取得、一项确认不存在：官方看板 5,112 仓/440 万提交/29,870 贡献者；麒麟占单位归属 PR **85.2%**、Issue 96.1%；镜像下载量确认无公开口径 | VF-31~VF-37 | 全量 Star 待 Gitee API 恢复或带凭证；OpenRank 2026 数据待 OpenDigger 更新 |
| Q-6 | 社区版等保/安可记录 | **证伪**：2023-2026 共 9 份安可公告零「openKylin/开放麒麟」在列；等保对象在制度上不含发行版产品 | VF-38~VF-40 | 关闭（季度抽查新公告即可） |
| Q-7 | 3.0 四个日期的事件指代 | **已闭环**：08-29 基金会公告／09-05 首批正式 ISO／09-18 ISO 刷新＋中文页更新；**08-22 查无任何官方事件**（Beta 实为 08-07 构建、08-10 起公测） | VF-12~VF-19 | 关闭 |
| Q-8 | Gen2 Kylin AI SDK 与 MCP 桌面能力 | **包级证实、功能待实测**：huanghe 仓库含 27 个 kylin-ai 包（libkylin-ai-base2 2.0、runtime、subsystem、aiassistant 5.0）；MCP 为 3.0 官方特性但无同名包，GUI/账号/硬件链路未验证 | VF-46~VF-49 | 下一迭代：GUI 切片内装 kylin-ai-subsystem 实测 |

## 二、核验事实（VF-01~VF-49）

### Q-1：LTS/EOL 与补丁政策

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-01 | 【官方】论坛「系统公告」2024-08-19《openKylin版本策略升级！》载技术委员会决议：创新版本每年 1 个、提供 1 年被动更新支持；LTS 每 3 年 1 个、提供 1 年主动更新+1 年被动更新支持（2024 版政策，1+1）。 | https://bbs.openkylin.top/t/topic/171502 | 2026-10-14 |
| VF-02 | 【官方】《OpenAtom openKylin 社区技术全景案例集 2024》「1.4 版本管理」载有同一表述（创新版 1 年被动；LTS 每 3 年、1 主动+1 被动；主版本生命周期内仅回合特性/补丁）。 | https://www.openkylin.top/public/pdf/OpenAtom_openKylin_Community_Technical_Panorama_Case_Collection_2024.pdf | 2026-10-14 |
| VF-03 | 【官方】docs.openkylin.top《openKylin 操作系统版本规划》文首标注「2026 年 4 月 9 日 TC 表决通过」：LTS 每 3 年一个主版本，维护周期「2+3 年（2 年主动维护+3 年被动维护）」；创新版每年 1 个、被动维护 1 年；主动维护含月/季更新、高危安全补丁与增强合入，被动维护仅修严重稳定性问题与高危严重漏洞。 | https://docs.openkylin.top/zh/3%E7%89%88%E6%9C%AC%E8%A7%84%E5%88%92%E4%B8%8E%E5%8F%91%E5%B8%83/3_1%E7%89%88%E6%9C%AC%E8%A7%84%E5%88%92/2_openKylin%E7%89%88%E6%9C%AC%E5%8F%91%E5%B8%83%E8%A7%84%E5%88%92 | 2026-10-14 |
| VF-04 | 【官方】同一规划文档：openKylin 2.0 被追溯定性为「openKylin 2.0 LTS (Nile)」，主动 24 个月+被动 36 个月，「服务终止时间约 2029 年 8 月」（为约数非精确日期）；3.0 定性为「3.0 创新版 (Huanghe)」，被动维护 12 个月，未给 EOL 具体日期。 | 同 VF-03（文档 5.1/5.2 节） | 2026-10-14 |
| VF-05 | 【官方】《openKylin 社区 2026 年 4 月运营报告》载：经技术委员会表决通过，将 LTS 系列维护周期延长为「2+3」年；同月发布 openKylin 2.0 SP2 第三次更新推送。 | https://www.openkylin.top/news/4014-cn.html | 2026-10-14 |
| VF-06 | 【官方·冲突】2026 年 4 月 TC 会议流出的路线图甘特图中，2.0 条带仍画到 2026 年止（旧 1+1 口径），与同月文字页「2+3、约 2029 年 8 月」并存，未见官方解释。 | https://bbs.openkylin.top/t/topic/173144 ；https://bbs.openkylin.top/t/topic/173145 | 2026-10-14 |
| VF-07 | 【一手实测+官方旁证】openKylin 1.0（yangtze）软件仓库 yangtze-updates/yangtze-security 的 Release 时间冻结在 2023-10-20（阿里云镜像目录实测）；2026-05-25 安全公告 OKSA-202605-0002 影响版本仅列「2.0 SP1、2.0 SP2」，不含 1.0——1.0 已不再获得安全补丁，且从未发布过带日期的 EOL 公告。 | https://mirrors.aliyun.com/openkylin/dists/yangtze-security/Release ；https://www.openkylin.top/support/patch-cn.html | 2026-10-14 |
| VF-08 | 【官方】2.0/SP2 与 3.0 当前在维护：nile-security 套件 Release 实测 2026-05-25 仍更新；SP2 桌面 ISO 有 20260407/20260730/20260813 三批刷新，2026-08-07 发布第四次更新新闻；huanghe 套件 base Release=2026-08-28；2026-10-09 推送 3.0 首次更新（近 150 项缺陷修复）。 | https://www.openkylin.top/news/4079-cn.html ；https://www.openkylin.top/news/4165-cn.html | 2026-10-14 |
| VF-09 | 【官方】存在《openKylin 安全漏洞管理规范 v1.0》（Security Governance SIG），规定分级响应时效（0day 24 小时内缓解措施、低危 7 个工作日确认）与 OKSA 公告机制；补丁公告列表共 44 条，最新为 2026-05-25。 | https://www.openkylin.top/support/patch_management-cn.html ；https://www.openkylin.top/support/patch-cn.html | 2026-10-14 |
| VF-10 | 【官方缺口】0.7/0.9/1.0 从未发布带日期的 EOL 公告（docs 仓库 3,181 文件树、release-management 仓库、新闻栏目、论坛全站检索均无）；第三方 eol.wiki 将 0.7/0.9.5/1.0 列「EOL，日期未公布」、2.0 列 Active（第三方口径，数据源仅官方下载页）。负证据检索路径：docs 仓库按「版本/发行/LTS/EOL/生命周期/周期/维护/支持」过滤；bbs 全站搜索 LTS/EOL/维护周期。 | https://eol.wiki/openkylin | 2026-10-14 |
| VF-11 | 【官方】KARE 不是支持周期/维护项目，而是磐石架构三组件之一的「KARE 兼容环境」（不可变系统＋KARE＋开明包，用于历史/Windows 应用生态兼容），同时也是软件组件名（OKSA-202509-0001 为 kare 组件提权漏洞）。 | https://www.openkylin.top/news/3848-en.html | 2026-10-14 |

### Q-7：3.0 与 2.0 SP2 发布日期事件定性

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-12 | 【官方】3.0 Beta ISO 构建日为 2026-08-07（镜像站实存 openKylin-Desktop-V3.0-Beta-20260807-x86_64.iso，下载页 Timeline 同载「8 月 7 日 openKylin 3.0 Beta」）；Beta 公测活动期 2026-08-10—08-25，论坛两篇官方镜像帖创建于 08-10。 | https://cdimage.openkylin.top/3.0/ ；https://www.openkylin.top/news/4083-cn.html ；https://bbs.openkylin.top/t/topic/173453 | 2026-10-14 |
| VF-13 | 【负证据】「2026-08-22＝论坛 Beta 公测」证伪：论坛系统公告板块 7—9 月全量清单无 8/22 主题；官网新闻 8 月条目无 8 月 22 日文章；网页检索「openKylin 3.0 8 月 22 日 Beta」无相关结果。8-22 落在公测活动期内，疑为活动期二手转述或误记，该日期原始出处仍未获取。 | https://bbs.openkylin.top/c/系统公告 ；https://www.openkylin.top/news/list-5-cn.html | 2026-10-14 |
| VF-14 | 【官方】2026-08-29＝开放原子开源基金会官网「3.0 正式发布」公告刊发时间（页内时间戳 2026-08-29 08:36:46，《内核跃迁，智能原生｜openKylin 3.0 正式发布》），早于 openKylin 官网中文新闻。 | https://openatom.cn/journalism/detail/K5Fe0TZfSWLH | 2026-10-14 |
| VF-15 | 【官方】2026-09-05＝首批正式版桌面 ISO 构建日（openkylin3_0-20260905，x86/arm/loong 与 AgentOS），下载页 Timeline 采为「9 月 5 日 openKylin 3.0」，英文下载页实测 Release date 2026-09-05。 | https://www.openkylin.top/downloads/ ；https://www.openkylin.top/downloads/os-en.html | 2026-10-14 |
| VF-16 | 【官方】2026-09-18＝桌面 ISO 第二次构建刷新（下载链接 302 跳转到 openKylin-Desktop-V3.0-20260918-{x86_64,arm64,loong64}.iso）＋中文下载页头部更新日期，不是独立发布事件；英文页存在 9-05/9-18 来回编辑痕迹（搜索引擎快照与实测不一致）；Server x86 另有 2026-09-16 刷新。 | https://www.openkylin.top/downloads/index-cn.html | 2026-10-14 |
| VF-17 | 【官方·数据卫生】官网新闻时间戳存在批量重导：Beta 新闻 4083 与正式发布新闻 4098 页内时间戳均被改为 2026-09-07（4094-4098 等一批文章同标 9-07），4014 四月报页时间戳为 2026-10-10；新闻页时间戳不能等同于事件实际发生日。 | https://www.openkylin.top/news/4098-cn.html ；https://www.openkylin.top/news/4083-cn.html | 2026-10-14 |
| VF-18 | 【官方】2.0 SP2「三日期」实为四事件：2025-08-26＝GA 正式发布日（Gitee 发行说明原文「于 2025 年 8 月 26 日正式发布」＋Timeline）；2025-08-31＝英文公告刊发日；2025-12-16＝中文旗舰新闻稿刊发日（Timeline 链此稿却标 8-26，自相矛盾）；2026-08-13＝ISO 滚动刷新日（前有 20260407/20260730 两批）。SP2 Beta 公测为 2025-06-26—07-13。 | https://gitee.com/openkylin/release-management/blob/master/openKylin-2.0-sp2/openKylin-2.0-SP2%E7%89%88%E6%9C%AC%E5%8F%91%E8%A1%8C%E8%AF%B4%E6%98%8E.md ；https://www.openkylin.top/news/3844-cn.html ；https://www.openkylin.top/news/3848-en.html | 2026-10-14 |
| VF-19 | 【官方缺口】20260905 桌面 ISO 已从 cdimage/3.0 目录移除（被 20260918 替代），未找到本次刷新的 changelog/刷新说明，是否含实质修复不可知。 | https://cdimage.openkylin.top/3.0/ | 2026-10-14 |

### Q-3：DistroWatch 与独立第三方横评

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-20 | 【第三方】DistroWatch openKylin 条目存在且事实活跃：table.php 实测 HTTP 200（76,458 字节，此前 403 为本网络环境问题，换浏览器 UA 后可访问）；条目最新截图版本 openkylin-3.0-ukui；Last Update 2026-09-30；DistroWatch 于 2026-08-29 发布《Distribution Release: openKylin 3.0》（文章号 12938）；访客评分 8.1/10（14 条评论，弱信号）。 | https://distrowatch.com/table.php?distribution=openkylin | 2026-10-14 |
| VF-21 | 【第三方】DistroWatch 流行度（Hits Per Day，页面点击口径，非装机量/市占率）：12 个月 #120（日均 112）、**6 个月 #107（132）**、3 个月 #64（190）、4 周 #151（113）、1 周 #120（130）——3.0 发布窗口点击热度短期上行，长期排名仍在百名开外。 | https://distrowatch.com/dwres.php?resource=popularity | 2026-10-14 |
| VF-22 | 【负证据】独立第三方性能横评经 7 条路径未找到：Phoronix 无任何 openKylin 基准文章（仅一条硬件短讯口头提及）；OpenBenchmarking.org 站内索引 0 条（检出的含麒麟结果均为银河麒麟商业版 V10）；Geekbench Browser 仅 3 条用户自提交单机记录（openKylin 1.0/2.0/2.0 SP1 各 1，不构成横评）；中英文多轮检索命中的性能数字全部来自官方新闻或转述媒体（凤凰网/人民邮电报）；社区论坛仅有个人内核编译跑分帖。此为高强度负证据而非穷尽证明（Phoronix/OB 站内搜索端点对本网络 403，结论基于搜索引擎索引替代路径）。 | https://www.phoronix.com/news/DC-ROMA-RISC-V-Laptop-II ；https://browser.geekbench.com/v6/cpu/9374680 | 2026-10-14 |
| VF-23 | 【第三方·弱】巴西 ResetHub（2026-10-10）在 RTX 5070 上实测 Deepin 25 与 openKylin：对 openKylin 记录频繁崩溃、翻译不全、Steam 着色器编译失败，全文无基准数据，属定性体验证据。 | https://resethub.com.br/2026/10/10/reset-testa-sistemas-operacionais-chineses-uma-nova-forma-de-usar-linux/ | 2026-10-14 |

### Q-6：等保与安全可靠测评

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-38 | 【政府】中国信息安全测评中心「安全可靠测评结果公告」共 9 份（2023 年第 1 号、2024 年 2 份、2025 年 3 份、2026 年 3 份）已全部抓取全文逐条检索：「开放麒麟/openKylin」**零命中**；「麒麟」命中仅三类——海思麒麟芯片、麒麟软件商业版「银河麒麟」、湖南麒麟信安（另一家公司）。 | http://www.itsec.gov.cn/aqkkcp/cpgg/ | 2026-10-14 |
| VF-39 | 【政府/制度】等保（网络安全等级保护）对象为信息系统、通信网络设施与数据资源，制度上不面向发行版产品（公安部等保 2.0 解读、GB/T 22240-2020 定级指南）；操作系统产品对应的是 GB/T 20272 等产品评价与安全可靠测评，后者由送测单位为商业产品申报（名单均为麒麟软件等商业主体）。openKylin 社区官方从未主张任何等保/安可资质（官网仅有 OKSA 补丁公告、国密/可信计算 SIG 工作与 OpenChain 合规评估）。 | https://www.mps.gov.cn/n6557563/c7369073/content.html | 2026-10-14 |
| VF-40 | 【厂商】麒麟软件《银河麒麟桌面 V10 SP1 产品手册》原文界定：「openKylin 是银河麒麟商业版的上游社区……银河麒麟桌面操作系统作为 openKylin 的商业发行版」；GB/T 20272-2019 第四级认证持有主体为商业版银河麒麟 V10 SP1。 | https://product.kylinos.cn/static/qilin/res/230727/79b7f680aa717fd9c5a31a660c160890.pdf | 2026-10-14 |

### Q-4：2400 万套/用户数独立审计核验

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-24 | 【厂商·溯源】「2400 万套」可考最早源头为 2025-06-07 CCF 科技成果鉴定会中麒麟软件/国防科大/开放原子联合体的自报研制材料（CCF 官网载鉴定流程为听取研制报告、审阅测试报告；研制报告原件不公开，此为强推断而非直接见件）。 | https://www.ccf.org.cn/STAEC/news/2026-04-17/893133.shtml | 2026-10-14 |
| VF-25 | 【转引链】外部出现全部为转引：科技日报 2025-09-23 获奖特稿（无信源标注、配图存麒麟 doubaocdn CDN 标「受访者供图」）、中国高新技术产业导报 2025-09-29 同题稿；界面新闻 2026-06-26 稿与麒麟官网通稿段落/配图逐段同构；界面 2026-09-10 上合稿文末明确标注「[商讯]」（付费商情）；CCF 官网 2026-04-17「优秀成果介绍」为完成单位自撰材料。 | http://www.stdaily.com/web/gdxw/2025-09/23/content_405866.html ；http://www.chinahightech.com/2025-09/29/content_409971.html ；https://m.jiemian.com/article/14651628.html ；https://www.jiemian.com/article/15076441.html | 2026-10-14 |
| VF-26 | 【官方】《开放原子开源基金会 2025 年度报告》（2026-02-06）给 openEuler 列「成员单位超 2100 家、贡献者超 2.4 万人、累计装机量突破 1600 万套」，给 OpenLoong 列注册用户 2 万；**对 openKylin 仅写「社区生态各项指标显著增长、海外用户组遍布 24 个一带一路国家」，全文不采用任何用户/部署数字**（67MB 原件全文检索）。 | https://file.oafimg.cn/official/55199610f4805522182038118697dded.pdf | 2026-10-14 |
| VF-27 | 【第三方/机构】信通院对 openKylin 的背书为「2022/2024 年度先进级可信开源社区」「2024 可信开源-OpenChain 双评估」「2025 年度可信开源项目」，评估体系聚焦安全、合规、持续、健康（治理成熟度/OpenChain），指标中无装机量/用户数审计项；信通院白皮书库未检出对 2400 万/240 万的引用。 | https://www.openkylin.top/community/ ；https://service.caict.ac.cn/ywjs/202011/t20201130_1648.html | 2026-10-14 |
| VF-28 | 【第三方·独立行为指标】开源社/X-lab《中国开源年度报告 2025》（OpenDigger 独立抓取 GitHub/Gitee）：openKylin 作为组织账户列中国 OpenRank 第 14 位，OpenRank 3,180.90（同比 −922.31），活跃开发者约 1,283 人；2024 报告称其「表现相对平稳」。两版年报均无用户/装机量数字。该口径度量仓库协作行为，与厂商「2 万+开发者/200+万用户」定义不同，不能互证也不能互斥。 | https://kaiyuanshe.github.io/2025-China-Open-Source-Report/data | 2026-10-14 |
| VF-29 | 【负证据与口径漂移】新华社（1.0 发布稿等）、央广网原创稿、人民网/天津日报、新华网均未采用「2400 万套」；人民日报 2025-11-27 的 1600 万套属于 openEuler；ccgp.gov.cn 仅见银河麒麟商业版逐笔合同（openKylin 免费不入集采），无法加总验证；赛迪公开口径仅商业 OS 市占率排名。同一「2400 万」至少六种定义（openKylin 系发行版全球部署量／开源版+商业发行版／衍生版本／社区部署量／麒麟 OS「下载及部署量」合计等）；2026-09-24 麒麟官网稿主体已悄然换成「麒麟操作系统累计下载及部署量超 2400 万套、服务国内客户超 21 万家」。 | https://www.kylinos.cn/about/news/2102931591735119874.html ；http://www.news.cn/2023-07/06/c_1129735470.htm ；http://www.cnr.cn/bj/sijh/20260630/t20260630_527684297.shtml | 2026-10-14 |
| VF-30 | 【负证据】外交部《上合组织成果清单（2025—2026）》仅列项目名无数字；CCF 鉴定为技术成果评价（依据自报材料）；国家工信安全中心仅与社区联合评选 29 个应用案例（评选非统计）。未发现任何一方对 openKylin 用户数或部署量做过独立统计、核实或背书。 | https://www.mfa.gov.cn/ziliao_674904/1179_674909/202609/t20260902_12014338.shtml | 2026-10-14 |

### Q-5：Gitee/OpenRank/镜像/贡献占比硬数据（抓取时间窗 2026-10-14 13:22—14:25 CST）

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-31 | 【第三方】Gitee 组织 openkylin（id=8380244，显示名「openKylin（孵化期）」）关注者 1,771；匿名 API `/orgs/openkylin/repos` 在 1 小时内 8 次以上多参数重试均稳定 HTTP 500（响应头额度 60/小时、剩余 59→7，非限速）；匿名搜索接口恒返回空数组。 | https://gitee.com/api/v5/orgs/openkylin | 2026-10-14 |
| VF-32 | 【第三方·子集口径】经网站项目页 824 次关键词分片请求，枚举到 3,978 个去重公开仓库（网站分页容量 4,920、官方看板口径 5,112，覆盖率 77.8%；最近更新的 400 个仓库 100% 在集合内）：子集合计 Star 6,952、Fork 7,810。Star 前五：community 167★/575🍴、docs 94/183、x-kernel 61/49、freewb 47/10、linux 44/187（linux 描述注明维护已迁至 GitCode）。精确全量总数因服务端 500 未取得。 | https://gitee.com/organizations/openkylin/projects ；https://gitee.com/api/v5/repos/openkylin/community | 2026-10-14 |
| VF-33 | 【官方】官网「数字看板」及其免鉴权后端实时值：commit 4,404,248、contributor 29,870、PR 29,028、issue 20,660、SIG 158、member 2,532（前端展示 +13＝2,545）、warehouse 5,112。口径提示：contributor（累计代码贡献者）与厂商宣传的「开发者」（含注册/CLA/生态开发者）定义不同，29,870 与官网英文页快照 29,513 接近但不可混用。 | https://datastat.openkylin.top/ ；https://dashboard-api.openkylin.top/api/data/overview | 2026-10-14 |
| VF-34 | 【官方·集中度量化】看板企业 PR 归属榜（70 家单位、合计 20,150 个有单位归属 PR）：**麒麟软件 17,158 个＝85.2%，非麒麟单位合计 2,992＝14.8%**（北航网安 736、北邮网安 539、上海交大网安 356、上海兆芯 179、武汉大学 143、海河实验室 111、元心 83、飞腾 71、广州视睿 65、龙芯中科 62、英特尔 59 等）；对照全社区 PR 29,028：麒麟 59.1%、有归属非麒麟 10.3%、未归属个人/学生 30.6%。Issue 企业归属（29 家/10,066）麒麟 9,669＝96.1%。 | https://dashboard-api.openkylin.top/api/data/member/pr?since=all&top=all | 2026-10-14 |
| VF-35 | 【第三方】openrank.io 官网已变为通用落地页（旧数据域名 oss.openrank.io DNS 不解析），**不存在 openKylin 组织级单一 OpenRank 分值**（OpenDigger 的 org/label 聚合文件均 404）；仓库级 Gitee 年度序列（截至 2025-12，2026 年数据缺失）：community 2021/22/23/24/25＝1/220.21/335.59/281.09/155.96，qa 2025＝294.43（抽样最高），linux 2025＝124.71，docs 2025＝43.70；community 活跃度 2023＝1206.95→2025＝625.22。GitHub 镜像组织 3,923 仓、合计仅 45★/22🍴（6 个归档，组织更新停在 2025-04-18），为无互动镜像。 | https://oss.open-digger.cn/gitee/openkylin/community/openrank.json ；https://api.github.com/orgs/openkylin | 2026-10-14 |
| VF-36 | 【第三方·确认性缺失】各镜像站均不公开下载计数：中科院软件所镜像已下线 openKylin（/openkylin/ 404、syncstatus.json 无条目）；中科大从未收录；清华 TUNA 本次出口 403 未能独立核实，但官网现行镜像清单已不含 TUNA/USTC/ISCAS；阿里云/上海交大/南京大学/163 等均为标准目录索引无计数字段；官网下载按钮走服务端跳转不展示计数。不存在可引用的公开镜像下载量数字（非抓取失败，是口径不存在）。 | https://mirrors.aliyun.com/openkylin/ ；https://www.openkylin.top/downloads/mirrors-cn.html | 2026-10-14 |
| VF-37 | 【第三方·仓库级】Gitee contributors 接口匿名可用：community 仓库 337 人/8,671 次提交，其中 79.5% 为 Gitee noreply 聚合桶（网聚/合并提交，归属不可判别）；剔除该桶后麒麟系邮箱（@kylinos.cn/@ubuntukylin.com/@yhkylin.cn）占 74.6%（严格仅计 @kylinos 为 69.6%），按人头计麒麟系 57.9%；linux 仓库为上游内核导入镜像（麒麟仅占 3.5%），不代表社区构成；docs 仓库存在单人 2,085 次批量导入异常值。 | https://gitee.com/api/v5/repos/openkylin/community/contributors | 2026-10-14 |

### Q-2：跨版本原地升级（网络核验部分）

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-41 | 【官方】跨版本升级工具 kylin-revision-manager 自 1.0→2.0 时期即存在：官网《openKylin 跨版本升级教程》指导 1.0 用户经 apt 安装该工具升级；2.0/SP1 发布公告均让「1.0 系列用户走跨版本升级工具、2.0 用户走系统设置更新」。 | https://www.openkylin.top/news/3566-cn.html ；https://www.openkylin.top/news/3605-cn.html ；https://openatom.cn/journalism/detail/wz0ZVCzcnOav | 2026-10-14 |
| VF-42 | 【官方】2.0 SP2 发布公告明示：「由于本次默认搭载磐石架构，系统底层结构变化较大，**暂时无法从 openKylin 2.0 SP1 及更早版本妥善升级到 SP2（SP2 Beta 可以）**，目前社区开发者们正在加急开发和验证升级方案」——SP1→SP2 原地升级路径官方确认断裂。 | https://www.openkylin.top/news/3844-cn.html | 2026-10-14 |
| VF-43 | 【官方】3.0 正式发布公告安装方式仅三种：全新镜像安装（新用户/重装）、系统设置更新（**仅适用已装 3.0 Beta 用户**）、终端 apt upgrade（开发者）——**未提供任何 2.0/2.0 SPx→3.0 的原地升级路径**。 | https://www.openkylin.top/news/4098-cn.html | 2026-10-14 |
| VF-44 | 【一手实测】本机 okw 发行版 openKylin-3.0（huanghe）官方仓库内升级器组件齐备：kylin-revision-manager 1.0.3.0-1ok3（描述「Upgrade from an old os to a new os」）、kylin-background-upgrade 1.3.2.10、kylin-update-frontend-immutable 2.0.0.0-ok36.9（ukcc 升级 UI，存在两个候选版本）。 | 实测命令见本附录第六节 | 2026-10-14 |
| VF-45 | 【实测缺口】2.0→SP2/3.0 的升级器实跑本轮未执行：本机仅有 openKylin-3.0 与 podman-machine-default 两个发行版，无 2.0/SPx 旧版；okw 不下载镜像，需先从官网获取 2.0 SPx WSL rootfs 并导入，再在副本上演练（避免污染默认发行版）。 | okw list（2026-10-14） | 2026-10-14 |

### Q-8：Gen2 Kylin AI SDK 与 MCP（本地只读实测部分）

| 编号 | 事实（含口径） | 来源 | 访问日期 |
|---|---|---|---|
| VF-46 | 【一手实测】huanghe 官方仓库共含 27 个 kylin-ai* 软件包，Gen2 AI 栈包级可得：libkylin-ai-base2 2.0.0.0-ok1.0（描述「Kylin AI SDK」，libkylin-ai-base-dev 候选版本同为 2.0.0.0-ok1.0）、kylin-ai-runtime 1.1.0.1（46 MB）、kylin-ai-subsystem 1.3.0.0（元包）、kylin-aiassistant 5.0.0.0（30 MB）、kylin-ai-engine-plugins、kylin-ai-model-manager 0.0.0.1-ok7（默认已安装，从 ModelScope 下载端侧模型）、kylin-ai-vector-engine（Milvus Lite fork）、document-qa/knowledge-base/business-framework 等服务包。 | 实测命令见本附录第六节；仓库 archive.build.openkylin.top huanghe/main | 2026-10-14 |
| VF-47 | 【一手实测】全部 kylin-ai 包描述中 grep「mcp」零命中；仓库内无 MCP 同名软件包（apt-cache search mcp 命中的 dotmcp 为 s3d 组件、其余为 xdmcp/mcpp 等无关包）；默认安装仅含 kylin-ai-model-manager，Gen2 运行时/子系统/助手默认未装。 | 实测命令见本附录第六节 | 2026-10-14 |
| VF-48 | 【官方】MCP 为 3.0 正式特性：公告称「智能体通过 MCP 协议直接调用桌面能力，无需模拟点击」，KylinBot、WorkBuddy、OpenClaw、Raccoon Work 均可完整运行；开发者经统一 AI SDK 开发智能技能并提交至 openKylin-skills 仓库；系统预装「Token 中心」（签到领额度）。MCP 能力随 kylin-ai 栈交付而非独立包，其功能链路（智能体连接、桌面调用、模型/Token 账号）需 GUI 与网络账号实测。 | https://www.openkylin.top/news/4098-cn.html | 2026-10-14 |
| VF-49 | 【一手实测】原 LOC-05 关于 Gen1 的结论维持：okw ai 走 Gen1 libkylin-ai-base-dev＋tesseract 薄 IPC 代理路径；本轮新增结论为 Gen2 SDK 在 3.0 仓库**包级已可得但默认未装、功能未验证**，7.6 节「Gen2 在切片内不可得」的表述据此收窄为「Gen2 功能链路在切片内未验证」。 | 同 VF-46/47 | 2026-10-14 |

## 三、对原 12 缺口 / 12 冲突的核销对照

| 原编号 | 原内容 | 本轮处置 | 替代事实 |
|---|---|---|---|
| CMP G-01 / ECO G-01 | DistroWatch 排名取不到（403） | **核销·已取得** | VF-20/VF-21（6 个月 #107、HPD 132） |
| CMP G-02 | 独立第三方性能横评 | 维持缺口，升级为**高强度负证据**（7 路径） | VF-22/VF-23 |
| ECO G-02 | 规模数字独立审计 | **核销·确认为单源**（外部全部转引、基金会刻意不列） | VF-24~VF-30 |
| ECO G-03 | Gitee Star | **部分核销**（子集 6,952★，全量受 API 500 阻塞） | VF-31/VF-32 |
| ECO G-04 | OpenRank 分值 | **部分核销**（无组织单值；取得 X-lab 组织值 3,180.90/#14 与仓库级序列） | VF-28/VF-35 |
| ECO G-05 | 镜像下载量 | **核销·口径不存在**（各站不公开，ISCAS 已下线） | VF-36 |
| ECO G-06 | 第三方贡献占比 | **核销·已取得**（麒麟 85.2%/96.1%） | VF-34/VF-37 |
| ECO G-07/G-08 | 社区版等保/安可记录 | **核销·证伪**（9 份公告零在列＋制度不含产品） | VF-38~VF-40 |
| CMP C-01 | 2.0 SP2 日期三说 | **核销·事件不同**（GA 8-26/英文稿 8-31/中文稿 12-16/ISO 刷新 2026-08-13） | VF-18 |
| CMP C-02 / ECO C-06 | 3.0 日期两说/三说 | **核销·事件不同**（公告 8-29/ISO 9-05/刷新 9-18；8-22 查无事件） | VF-12~VF-17 |
| CMP C-05 | 2.0→SP2 原地升级两说 | **核销·官方明示断裂**，且新发现 2.0→3.0 同样无路径 | VF-42/VF-43 |
| ECO C-01~C-05 | 用户/开发者/会员/SIG 多数值冲突 | 维持并强化：全部厂商谱系，转引链已坐实；新增独立行为指标仅供口径对照 | VF-24~VF-29/VF-33 |
| ECO C-07 | 官网首页两套指标 | 维持（看板口径 VF-33 可作第三方对照，不消除冲突） | VF-33 |

## 四、本轮新登记冲突（NC）

| 编号 | 冲突 | 各方口径 | 处置 |
|---|---|---|---|
| NC-01 | LTS 政策新旧三文本不一致 | 2024-08 论坛公告：LTS 1+1；2026-04-09 TC 文档：LTS 2+3、2.0 终止「约 2029 年 8 月」；2026-04 TC 会议路线图甘特图：2.0 条带仍止于 2026 | 并陈不裁决；列入 90 天复核；结论不押注 2029 具体日期 |
| NC-02 | 3.0 ISO 刷新与页面时间线不透明 | 20260905 桌面 ISO 被悄悄替换为 20260918 且无 changelog；英文下载页 Release date 在 9-05/9-18 间被来回编辑；官网新闻时间戳批量重导（均改标 9-07） | 并陈；引用一律以事件源（基金会公告/Gitee 发行说明/ISO 文件名）为准，不以网页时间戳为准 |

## 五、评分影响（Q 门复核修正，2026-10-14）

- **7.2 生命周期与升级保障：2 → 3**。上调依据：成文 LTS 政策客观存在（VF-01~VF-05，2026-04 起 LTS 总窗口 5 年、2.0 在维护至 2026-05 仍有安全补丁、有 OKSA 响应规范）；不上调至 4 的依据：政策 2026-04 才成文且三文本冲突（NC-01）、1.0 已无公告事实停维（VF-07）、3.0 仅 12 个月被动维护、跨版本升级连续两次断裂（VF-42/VF-43）、无版本完整走完过生命周期。
- **加权总分：70 → 73/100**（仅 7.2 维度 +1：4×0.20＋3×0.15＋4×0.20＋3×0.20＋4×0.15＋4×0.10＝3.65/5）。
- 7.4 治理分维持 3：负分被硬数据坐实（85.2%/96.1%、OpenRank 同比 −922.31），同时新增公开数据看板、14.8% 非麒麟单位 PR 与 DistroWatch 短期上行等正反证据，两相抵消。
- 7.6 本地可落地性维持 4：Gen2 由「不可得」更正为「包级可得、功能未验证」（VF-46~VF-49），不构成加分实测。

## 六、本地实测命令记录（Q-2/Q-8，一手证据）

环境：Windows + WSL2，发行版 openKylin-3.0（WSL2，Stopped→按需启动），经 okw（Python 3.14.7，`python -m okw exec openKylin-3.0 -- bash -lc …`，非交互只读），时间 2026-10-14。

```bash
cat /etc/os-release            # openKylin 3.0 (huanghe)，ID=openkylin
apt-cache policy libkylin-ai-base-dev   # Candidate: 2.0.0.0-ok1.0（huanghe/main + huanghe-proposed）
apt-cache search kylin-ai      # 27 个包（libkylin-ai-base2/kylin-ai-runtime/kylin-ai-subsystem/kylin-aiassistant 等）
apt-cache show kylin-ai-runtime kylin-ai-subsystem kylin-aiassistant libkylin-ai-base2 kylin-ai-engine-plugins
dpkg -l | grep -i kylin-ai     # 仅 kylin-ai-model-manager 0.0.0.1-ok7 默认安装
for p in $(apt-cache pkgnames | grep -i kylin-ai); do apt-cache show $p | grep -i mcp; done   # 零命中
apt-cache search kylin | grep -iE 'upgrade|update-manager|release'
# kylin-revision-manager 1.0.3.0-1ok3 / kylin-background-upgrade 1.3.2.10 / kylin-update-frontend-immutable 2.0.0.0-ok36.9
dpkg -L kylin-ai-model-manager # /usr/bin/kylin-ai-model-manager、download.py；/usr/share/kylin-ai/ondevice/
```

下一步实测（需用户授权写入与镜像下载）：①导入 openKylin 2.0 SP2 WSL rootfs 为独立发行版副本；②副本内 apt 安装/运行 kylin-revision-manager 观察 3.0 升级通道是否开放；③3.0 内 apt install kylin-ai-subsystem 后经 GUI（xrdp 3390）验证 AI 助手、MCP 智能体连接与 Token 中心。

## 七、本轮新增信源（S36 起，接续附录 A/B 编号）

| 编号 | 信源 | 口径 | URL |
|---|---|---|---|
| S36 | openKylin 论坛（2024 版本策略公告 topic 171502；TC 会议 173144/173145；Beta 帖 173453/173455） | 官方 | https://bbs.openkylin.top/ |
| S37 | docs.openkylin.top《openKylin 版本发布规划》（2026-04-09 TC） | 官方 | https://docs.openkylin.top/zh/3版本规划与发布/ |
| S38 | openKylin 下载中心（中英文、Timeline、镜像清单、cdimage） | 官方 | https://www.openkylin.top/downloads/ |
| S39 | 开放原子开源基金会（3.0 发布稿 K5Fe0TZfSWLH；2.0 发布稿 wz0ZVCzcnOav） | 官方 | https://openatom.cn/ |
| S40 | Gitee openkylin（release-management/docs/community；API v5） | 官方/平台 | https://gitee.com/openkylin |
| S41 | openKylin 数字看板与 dashboard-api（overview/member PR/Issue） | 官方 | https://datastat.openkylin.top/ |
| S42 | OpenDigger 开放数据（仓库级 OpenRank/Activity 序列） | 第三方研究 | https://oss.open-digger.cn/ |
| S43 | 开源社/X-lab《中国开源年度报告 2025》 | 第三方研究 | https://kaiyuanshe.github.io/2025-China-Open-Source-Report/data |
| S44 | DistroWatch（openKylin 条目与流行榜；浏览器 UA 可达，HTTP 200） | 第三方平台 | https://distrowatch.com/table.php?distribution=openkylin |
| S45 | 开放原子开源基金会 2025 年度报告 PDF | 官方 | https://file.oafimg.cn/official/55199610f4805522182038118697dded.pdf |
| S46 | 中国信息安全测评中心（9 份安全可靠测评公告全文） | 政府 | http://www.itsec.gov.cn/aqkkcp/cpgg/ |
| S47 | 公安部等保 2.0 解读 / GB/T 22240-2020 | 政府 | https://www.mps.gov.cn/n6557563/c7369073/content.html |
| S48 | 科技日报/中国高新技术产业导报/界面新闻（2400 万转引链样本） | 媒体（转引/商讯） | 见 VF-25 |
| S49 | 阿里云 openKylin 镜像（套件 Release 元数据） | 第三方镜像 | https://mirrors.aliyun.com/openkylin/ |
| S50 | 本机 okw 发行版 openKylin-3.0（apt-cache/dpkg 只读实测） | 一手实测 | 本附录第六节 |

---

*核验执行：4 路并行公开信源调研（Q-1/Q-7、Q-3/Q-6、Q-4、Q-5）＋本机 okw 只读实测（Q-2/Q-8）。所有网络事实访问日期 2026-10-14；负证据均附检索路径。本轮不新增对外强结论，评分修正仅 7.2 一个维度（70→73）。*