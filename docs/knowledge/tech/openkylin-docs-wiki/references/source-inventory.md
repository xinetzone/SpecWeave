# 附录 A：信源台账（S01–S26）

> 全部信源采集日期：**2026-09-29**。网络请求统一携带 `User-Agent: Mozilla/5.0` 头（Gitee raw/API 对无 UA 请求返回异常）。文档站是 docsify 对 Gitee 仓库 `openkylin/docs` master 分支的实时渲染，故同一文件存在"文档站路径"与"Gitee raw 路径"两种形态，下表一并给出。
>
> raw URL 构造模式：`https://gitee.com/openkylin/docs/raw/master/<URL 编码后的相对路径>`；文档站路径模式：`https://docs.openkylin.top/zh/#/<相对路径（不带 .md）>`（docsify 哈希路由，以站内实际链接为准）。

## A.1 平台与仓库级信源

| 键 | 信源 | URL / 位置 | 采集方式 | 支撑事实 |
|---|---|---|---|---|
| S01 | openKylin 文档平台首页 | https://docs.openkylin.top/zh/home | WebFetch | F-001、文档贡献规范、CC BY-SA 4.0、无 BOM UTF-8、图片规格 |
| S02 | Gitee 源仓库页 | https://gitee.com/openkylin/docs | WebFetch | F-002（Star 92 / Watch 28 / Issues 6 / PR 1，master 分支） |
| S03 | Gitee Git Trees API（递归） | https://gitee.com/api/v5/repos/openkylin/docs/git/trees/master?recursive=1 | PowerShell Invoke-RestMethod | F-003/F-004：3181 条目、truncated=false、237 中文 md 与全部板块分布（[full-catalog.md](full-catalog.md) 数据源） |
| S04 | Gitee Commits API | https://gitee.com/api/v5/repos/openkylin/docs/commits | PowerShell | F-014：最近提交 2026-09-10～09-28（GPU/文件 FAQ、SDK 指南 !517/!520/!522、FAQ 分支修正 !518） |

## A.2 精读文档（文档站原始 Markdown）

路径列均相对于仓库根；raw 链接按 A.0 模式拼接。

| 键 | 文件相对路径 | 支撑事实 |
|---|---|---|
| S05 | `3版本规划与发布/3_1版本规划/2_openKylin版本发布规划.md` | F-006～F-010：双轨版本制（LTS 3 年/2+3、创新版 1 年/12 月被动）、2.0=Nile/2024-08-08/Linux 6.6、3.0=Huanghe/Linux 7.0、组件 GCC 15.2/LLVM 22/glibc 2.42/Mesa 26.0/OpenSSL 3.5、RISC-V RVA23、2026-04-09 TC 表决 |
| S06 | `1入门与参与/1_5基础设施平台指南/OKBS软件包编译平台使用说明.md` | F-027：OKBS 平台、PPA/SSH/PGP/dput、sftp 端口 2121、dput-logs、changelog 代号 yangtze |
| S07 | `1入门与参与/1_5基础设施平台指南/openKylin版本构建平台使用说明.md` | F-028：factory 平台、livebuild、软件源快照、live/iso 包列表、hooks/includes/packages 目录语义、代号 nile |
| S08 | `1入门与参与/1_3系统下载与安装指南/05_openKylin-WSL版本安装.md` | F-020/F-021：Win10 19041 门槛、两镜像、import 命令、默认账号密码 openkylin、xrdp 3390、xorg |
| S09 | `1入门与参与/1_1新手入门/05_openKylin.md` | F-018：1.0 时代特性页（UKUI 4.0、KMRE 等），用于时效对照 |
| S10 | `1入门与参与/1_4基础操作/openKylin新手使用指南.md` | F-017：最小命令集（apt update/install/remove、wget、dpkg -i） |
| S11 | `1入门与参与/1_4基础操作/常用软件安装.md` | F-019：deb 安装国产软件路径（微信/腾讯会议/ToDesk 等） |
| S12 | `1入门与参与/1_4基础操作/AI模型管理/端侧AI模型管理.md` | F-022：kylin-ai-model-manager、nlp 1/speech 5/搜索 2、modelscope.cn、完整性校验 |
| S13 | `1入门与参与/1_4基础操作/AI模型管理/基于openKylin本地部署并运行DeepSeek-R1开源模型.md` | F-023：ollama 安装三方式、serve/run、六档 1.5b–70b（Qwen/Llama） |
| S14 | `1入门与参与/1_6常见问题/FAQ.md` | F-026：约 20 条目（包管理/硬件自查/磐石架构装包/root 密码等） |
| S15 | `4开发与设计/4_10AISDK设计/OpenKylin AI SDK 开发手册.md` | F-024：137519 字符/4929 行、8 章能力域、会话生命周期接口模式、错误码章 |
| S16 | `4开发与设计/4_8开发指南/2_openKylin维护模式.md` | F-025：开机 logo 临时维护模式、`sudo mm-cli` 永久切换、4 条 FAQ |
| S17 | `1入门与参与/1_5基础设施平台指南/社区CLA介绍/CLA签署说明.md` | F-032：cla.openkylin.top、个人/员工/企业三类 CLA |
| S18 | `1入门与参与/1_2社区贡献/10_openKylin社区贡献角色.md` | F-033：Contributor/Maintainer/Owner 三级、权责限 SIG 内、2/3 票数 |
| S19 | `1入门与参与/1_2社区贡献/09_openKylin贡献攻略.md` | F-034：贡献入口与流程 |
| S20 | `1入门与参与/1_2社区贡献/13_openKylin社区AI辅助贡献守则.md` | F-035：2026-08-01、9 节、披露模板（AI usage/Assisted-by + 人类 Signed-off-by）、禁 Bot/编造/敏感上传 |
| S21 | `1入门与参与/1_2社区贡献/12_非代码贡献指南.md` | F-036：文档/翻译/设计/测试等非代码贡献路径 |
| S22 | `7关于社区/7_2社区组织架构/4_社区治理组织架构.md` | F-037：理事会/秘书处/TC/咨询委员会/生态委员会五组织 |
| S23 | `5适配与上架/5_3系统适配/1_软件适配.md` | F-039：软件适配六步流程（官网支持→兼容适配→腾讯文档→百度网盘 pwd=1357→7 工作日→证书公示） |
| S24 | `5适配与上架/5_3系统适配/2_硬件适配.md` | F-040：硬件适配同构流程、1080p+ MP4/AVI 视频要求、旧路径链接（`/zh/01_安装升级指南/...`） |

## A.3 SIG 与治理类（1_2 SIG 文件 12 篇、7 板块）

作为 S18/S22 的补充整体采读：`1入门与参与/1_2社区贡献/04_社区兴趣小组（SIG）/` 下 1_新SIG组申请指南～12_SIG组Owner增选撤销规范（支撑 F-038：Gitee 申请→TC 审核→建邮件列表→运作、章程模板、Owner 增选撤销、活跃奖惩）；`7关于社区/7_4社区政策与规则/` 下 1_安全策略指南～7_issue报告规范（安全策略、贡献者协议、TC 委员增选、免责声明、成员守则、管理规范、issue 报告规范）。文件级完整路径见 [full-catalog.md #11–#22、#228–#234](full-catalog.md)。

## A.4 交叉验证信源（本仓内部）

| 键 | 信源 | 位置 | 用途 |
|---|---|---|---|
| S25 | openKylin 项目全面调研（同包伴生文档） | [project-overview.md](project-overview.md)（原 `tech/openkylin/index.md`，2026-09-29 合并迁入） | 官网新闻口径 62 条事实：3.0 发布、智能体底座、MCP、openkylin-skills、衍生版等，与文档站口径互证 |
| S26 | WSL 本机实测指南（同包伴生文档） | [wsl-install-sparse-vhd-guide.md](wsl-install-sparse-vhd-guide.md)（原 `tech/openkylin/wsl-install-sparse-vhd-guide.md`，同日合并迁入） | 本机 Win10.0.19044 + WSL 2.9.3.0 实测：`.wsl` 为 gzip tar、E_UNEXPECTED/E_ABORT 排障、内存门槛、稀疏 VHD 命令 |

## A.5 采集过程中的无效/弃用路径（避免后人重复踩坑）

| 尝试 | 结果 | 替代方案 |
|---|---|---|
| `https://docs.openkylin.top/_sidebar.md`、`/zh/_sidebar.md` | 返回 docsify"未找到"页（404 语义） | 弃用，改 S03 直接解析仓库树 |
| Gitee MCP `get_file_content`（README.md、zh/_sidebar.md） | 返回空数组 `[]` | 弃用 MCP，用 S03/S04 + raw URL |
| WebFetch 访问 gitee API URL | Failed to fetch | PowerShell Invoke-RestMethod + UA 头 |

## A.6 引用可靠性分级

1. **制度级**（S05 版本规划、S17 CLA、S18 角色、S20 AI 守则、SIG 章程）：TC 表决或社区政策文件，最高可信；
2. **操作手册级**（S06/S07/S08/S12/S13/S15/S23/S24）：平台/操作文档，2026-09 多篇仍有提交，需连同适配版本号一起引用；
3. **导航/短页级**（版本发布动态、社区项目地图、文档平台使用指南等）：内容短、可能为占位，只作入口不作事实源；
4. **时效存疑级**：4 篇"（需要更新）"、"失效文档"目录、S09 等 1.0 时代文章、含旧编号路径的链接——引用时必须标注时效风险；
5. **本仓实测级**（S26）：单机实测，环境明确（Win10.0.19044/WSL 2.9.3.0），换环境结论可能不同。
