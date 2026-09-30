# 附录 A：信源台账（S01–S17）与本地知识包引用

> openEuler 侧信源采集日期为 **2026-09-30**，方式为 WebSearch 定位加 WebFetch 精读与 repo 目录实测；openKylin 侧不重新联网，全部引用 2026-09-29 已完成 G1 核验的本地知识包。所有市场份额、装机量与性能数字的口径见 A.3。

## A.1 openEuler 侧信源

| 键 | 信源 | URL / 位置 | 支撑事实 |
|---|---|---|---|
| S01 | 人民邮电报（中新网知识库转载）：openEuler Developer Day 2026 在长沙举办（2026-05-06） | https://www.zgxwzk.chinanews.com/observe/2026-05-06/30068.shtml | O-008（捐赠人）、O-009（成员/高校）、O-012（448 万/57.3%/1600 万转引）、O-029（AgentOS 四能力、SkillHub）、O-030（ODD 2026） |
| S02 | openEuler 开源社区介绍 PDF（官网白皮书目录） | http://openeuler.org/whitepaper/openEuler%20%E5%BC%80%E6%BA%90%E7%A4%BE%E5%8C%BA%E4%BB%8B%E7%BB%8D.pdf | O-006（治理架构）、O-010（500+ 项目）、O-021（架构含 SW-64/Power 口径）、O-024/O-025（场景与获取）、O-027/O-028（技术清单）、O-034（早时点数据） |
| S03 | openEuler 官网下载页 | https://www.openeuler.org/zh/download/ | O-007（实时统计）、O-018（SP 日期/EOL 标注）、O-019（SP4 特性）、O-020（Embedded）、O-021（架构）、O-024（镜像体积与标签）、O-025（渠道）、O-032（案例行业）、O-033（双域名） |
| S04 | 太平洋科技转快科技：openEuler 装机量破 2000 万套（2026-09-18） | https://g.pconline.com.cn/x/2182/21822689.html | O-009、O-012、O-013（2000 万/份额第一，厂商大会口径）、O-014（鲲鹏关联数据） |
| S05 | openEuler 生命周期页（WebFetch 精读全文） | https://www.openeuler.org/zh/other/lifecycle/ | O-015（现行生命周期规范全文要点）、O-016（24.03/6.6） |
| S06 | repo.openeuler.org 目录索引（实测目录列表） | https://repo.openeuler.org/ | O-016、O-017（版本序列）、O-018（仓库目录日期） |
| S07 | 华为官网：华为捐赠欧拉（2021-11-09） | https://www.huawei.com/cn/news/2021/11/huawei-openeuler-openatom-foundation | O-004（数字基础设施 OS 表述关联）、O-005（捐赠与 60 万套） |
| S08 | 头条百科："欧拉"词条（三级信源，仅时间线交叉） | https://m.baike.com/wiki/欧拉/7009558050113721603 | O-001（EulerOS 时间线交叉）、O-002、O-011（610 万/36.8% 交叉） |
| S09 | 华为官网：4 家 OS 厂商基于 openEuler 发布商业发行版（2020-03-28） | https://www.huawei.com/cn/news/2020/3/openeuler-lts-open-source-operating-system/ | O-001、O-003（首个 LTS、4 家 OSV、早期节奏与 Upstream First） |
| S10 | 新华网/经济参考报：国产操作系统布局算力超节点时代（2025-11-24） | http://www.news.cn/tech/20251124/7ebe3cee3a0c45c4be71019f65a024be/c.html | O-004、O-008（芯片企业捐赠人） |
| S11 | openEuler 软件中心 easysoftware | https://easysoftware.openeuler.openatom.cn/zh/ | O-023（213,330 包/325 镜像/epkg/分类） |
| S12 | openEuler 官方文档：在 openEuler 上安装 DDE（24.03 LTS SP1） | https://docs.openeuler.org/zh/docs/24.03_LTS_SP1/docs/desktop/安装DDE.html | O-026（DDE 可选安装、openeuler 用户、root 限制） |
| S13 | openEuler 官方文档 UKUI 用户指南与论坛 UKUI 安装帖 | https://forum.openeuler.org/t/topic/19309 | O-026（UKUI 可选安装） |
| S14 | 银河麒麟高级服务器 V10 SP3 产品页与交易增强版白皮书 PDF | https://www.kylinos.cn/productMobile/server/serverMain/index.html ；https://product.kylinos.cn/static/img/2024/12/ffe59f66d43c538f3d779dbf5b43fd19.pdf | O-031（基于 openEuler 构建、4.19 内核策略、贡献排名第二） |
| S15 | openEuler dev 邮件列表：update_20260513 公示 | https://mailweb.openeuler.org/archives/list/dev@openeuler.org/thread/XQMNJ7NHDCH5QYZQK6UPJEIJ2BVCRK6S/ | O-022（周度 update、CVE/缺陷、多分支）、O-033（托管与邮件域名） |
| S16 | 界面新闻：主流国产操作系统发展与应用解析（2026-04-09） | https://www.jiemian.com/article/14229209.html | O-035（"深耕服务器、桌面能力偏弱"媒体定性） |
| S17 | 凤凰网：openKylin 3.0 相关报道（2026-09-04） | 检索词「凤凰网 openKylin 3.0 2026-09」可得的报道页 | O-035（"前沿预研、反哺商业版"媒体定性） |

## A.2 openKylin 侧引用（本地知识包，不重新联网）

| 引用 | 文件 | 用法 |
|---|---|---|
| project-overview F-001~F-062 | [../../openkylin-docs-wiki/references/project-overview.md](../../openkylin-docs-wiki/references/project-overview.md) | K-001~K-012 全部锚点的事实出处；其自带 S01—S30 信源台账与 V-01~V-08 审查记录继续有效 |
| docs-wiki F-001~F-044 | [../../openkylin-docs-wiki/index.md](../../openkylin-docs-wiki/index.md) | 文档平台侧事实（双轨版本制 TC 文本、apt 命令、安装矩阵、AI SDK 文档等） |
| WSL 本机实测 | [../../openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md](../../openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md) | 选型第⑥问"最低成本首轮体验"的实测依据 |

引用纪律：本知识包不复制本地包事实原文，只给锚点映射；openKylin 侧事实时点冻结在 2026-09-29，若本地包后续修订，以本地包最新编号内容为准。

## A.3 信源分级与口径纪律

| 级别 | 信源 | 本知识包的使用纪律 |
|---|---|---|
| 一手官方 | S02/S03/S05/S06/S11/S12/S13/S15 | 版本、生命周期、包格式、镜像、治理结构等事实直接引用；官网动态统计给区间不给点值 |
| 厂商官方 | S07/S09/S14（华为、麒麟产品材料） | 历史事件与产品关系直接引用；性能/份额/排名表述标注"厂商口径" |
| 媒体转引 | S01/S04/S10/S16/S17 | 机构数据（IDC、沙利文加头豹）一律标"转引"，未取得原始报告前不做精确推算；定性句仅作观察不作结论 |
| 三级参考 | S08（百科） | 仅用于时间线交叉，不单独支撑任何结论 |

三条硬纪律：

1. **数字四件套**：引用任何规模数字同时给出统计对象、时点、发布方、原始/转引层级（V 审查 V-01/V-02）。
2. **矛盾并列**：官方发布日、仓库目录日、下载页 EOL 标注不一致时全部保留（O-018），不取均值也不择一。
3. **本地包优先**：openKylin 侧事实以本地知识包为准；媒体对比文章中涉及 openKylin 的数字若与本地包冲突，以本地包及其 V 审查裁定为准。

## A.4 采集缺口登记

- 沙利文加头豹《2025年中国服务器操作系统行业发展白皮书》原文未获取，57.3% 与 448 万套为 S01/S04 转引。
- openEuler 25 家 OSV 的逐家活跃产品线与版本未逐一核验。
- 官网实时统计（O-007）为动态页面，两次抓取即有差异，未做逐日采样。
- openEuler 侧无独立第三方性能/稳定性实测；本知识包未安装 openEuler 介质做本机验证（本机实测仅覆盖 openKylin 3.0 WSL，属另一知识包）。
