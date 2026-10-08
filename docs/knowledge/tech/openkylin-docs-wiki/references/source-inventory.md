# 附录 A：信源台账（S01–S35）

> 信源采集日期：S01–S26 为 **2026-09-29**；S27–S32 为 **2026-09-30** Desktop WSL 专项追加；S33 为 **2026-10-08** Desktop WSL 落机实测追加（见 A.7）；S34 为 **2026-10-08** Kylin AI SDK 文字识别落机 POC 追加（见 A.8）；S35 为 **2026-10-08** AI 子系统与显示双栈源码架构专项追加（本机只读核验＋上游源码审阅，见 A.9）。网络请求统一携带 `User-Agent: Mozilla/5.0` 头（Gitee raw/API 对无 UA 请求返回异常；Gitee tree/raw 网页有反爬验证，S35 改以 `git clone --depth 1` 本地取证）。文档站是 docsify 对 Gitee 仓库 `openkylin/docs` master 分支的实时渲染，故同一文件存在"文档站路径"与"Gitee raw 路径"两种形态，下表一并给出。
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
| S26 | WSL 本机实测指南（同包伴生文档） | [wsl-install-sparse-vhd-guide.md](wsl-install-sparse-vhd-guide.md)（原 `tech/openkylin/wsl-install-sparse-vhd-guide.md`，2026-09-29 合并迁入） | 本机 Win10.0.19044 + WSL 2.9.3.0 实测：`.wsl` 为 gzip tar、E_UNEXPECTED/E_ABORT 排障、内存门槛、稀疏 VHD 命令 |
| S32 | 本机磁盘余量快照（2026-09-30） | PowerShell `Get-PSDrive` 实测：C: 剩 2.3 GB、D: 剩 4.8 GB | Desktop WSL 导入未实测的直接约束（最小候选占用 >20 GiB）；已存在发行版 `openKylin-3.0`（位于 `d:\AI\.chaos\envs\openKylin-3.0`）；`D:\WSL` 为 podman machine 数据目录，不可占用/删除 |

## A.5 采集过程中的无效/弃用路径（避免后人重复踩坑）

| 尝试 | 结果 | 替代方案 |
|---|---|---|
| `https://docs.openkylin.top/_sidebar.md`、`/zh/_sidebar.md` | 返回 docsify"未找到"页（404 语义） | 弃用，改 S03 直接解析仓库树 |
| Gitee MCP `get_file_content`（README.md、zh/_sidebar.md） | 返回空数组 `[]` | 弃用 MCP，用 S03/S04 + raw URL |
| WebFetch 访问 gitee API URL | Failed to fetch | PowerShell Invoke-RestMethod + UA 头 |

## A.6 2026-09-30 Desktop WSL 专项远程信源（S27–S31）

> 对应方法论编排 session `sc-20260930-openkylin-desktop-wsl`（R→I→E→V→C，standard），全部产出集中于 [wsl-dual-image-selection.md](wsl-dual-image-selection.md)。受 S32 磁盘约束，本批信源**只覆盖文件级远程事实**，不含导入运行时实测。

| 键 | 信源 | URL / 位置 | 采集方式 | 支撑事实 |
|---|---|---|---|---|
| S27 | openKylin 官方下载中心（含页内 `md5ById` 校验值映射） | https://www.openkylin.top/downloads/index-cn.html | curl 抓 HTML，正则提取页内 JS 数据 | 两 WSL 条目（id=126 最小 / id=127 Desktop）、展示体积 336M/6.1G、构建日期 2026-08-28、MD5：最小 `3c5717cf...`、桌面 `df559de7...`；仅 AMD64 |
| S28 | 下载跳转与 CDN 元数据 | `https://www.openkylin.top/downloads/download-smp.php?id=126\|127`（302）→ `https://cdimage.openkylin.top/3.0/openKylin-3.0[-desktop]-wsl-amd64.wsl` | `curl.exe -sIL` 跟随重定向 | 真实 CDN 文件名、精确 Content-Length（352,431,812 / 6,592,986,686 字节）、支持 Range（Accept-Ranges: bytes） |
| S29 | CDN Range 二进制核验（未下载全量，流量 <25 MiB） | 同 S28 的两个 CDN URL | `curl -r` 头 4 字节落盘 `Format-Hex`；尾 4 字节读 gzip ISIZE（`BitConverter.ToUInt32`）；前 20 MiB 经 .NET GzipStream 流式解压后 `tar -tf` 列目 | 两镜像魔数同为 `1F 8B 08 00`；桌面 ISIZE=103,258,112（已 4 GiB 回绕）；头部条目同为标准 rootfs（`./dev ./bin ./run/systemd`） |
| S30 | 官方《openKylin-WSL版本安装》重读（master） | Gitee Contents API：`1入门与参与/1_3系统下载与安装指南/05_openKylin-WSL版本安装.md`（路径 URL 编码） | Gitee API v5 取全文（S08 的 2026-09-30 重读） | 桌面镜像导入名 `openKylin-desktop`、默认账号 `openkylin/openkylin`、`ip addr show eth0` 取 IPv4、mstsc 连 `<IP>:3390`、Session 选 xorg、xrdp 默认自启、WSL 重启 IP 可能变；官方 FAQ 仅 2 条，无磁盘/内存门槛、包数、VHD、稀疏 VHD、导入失败排障 |
| S31 | 社区实测负证据 | bbs.openkylin.top 站内检索 + 公开搜索引擎（2026-09-30） | 关键词组合检索 | 未见桌面 WSL 镜像用户实测帖（桌面安装讨论为 ISO/虚拟机路径）；官方文档是唯一公开一手操作信源。检索覆盖受限，不等同"全网不存在" |

## A.7 2026-10-08 Desktop WSL 落机实测信源（S33）

> 对应方法论编排 session `sc-20261008-openkylin-desktop-wsl-install`（R→I→F→V→C，standard）。S27–S31 的文件级事实于同日复核未变（字节数/MD5 一致）；本信源是**导入、容器/xrdp 服务级与交互式 UKUI 桌面的全链路运行时实测**，把对照文档 §7 验收清单 8 项实测项闭环（第 9 项卸载用户选择不执行）。原始命令与输出对账集中于 [wsl-dual-image-selection.md](wsl-dual-image-selection.md) §4–§7 与黑屏排障 §5.1。

| 键 | 信源 | 环境 / 位置 | 采集方式 | 支撑事实（F-051 ~ F-057） |
|---|---|---|---|---|
| S33 | 本机落机实测：下载→校验→导入→容器验收→xrdp 服务链路→**交互登录黑屏排障与重登验证** | Win10 26220 / WSL 3.0.2.0 / 内核 6.18.40.1-1 / 31.5 GiB 内存（导入前空闲 11.94）；镜像 `D:\WSL\openKylin-3.0-desktop-wsl-amd64.wsl`、VHD `D:\WSL\openKylin-3.0-desktop\ext4.vhdx`，发行版名 `openKylin-3.0-desktop`；用户级修复文件 `~/.xsession`（备份 `.xsession.bak-20261008`） | curl 断点续传下载（约 3 分钟）；`Get-FileHash`/`Format-Hex` 校验；`Measure-Command` + `wsl --import`；容器内 `dpkg-query`/`df -B1`/`systemctl`/`ss`/`ip`；宿主 `GetCompressedFileSizeW`、`Test-NetConnection 127.0.0.1:3390`、`wsl -l -v`；磁盘用 `Get-CimInstance Win32_LogicalDisk` 独立通道对账；黑屏阶段取 `xrdp-sesman.log`/`ukuismserver.log`/`.xsession-errors`/`.xorgxrdp.10.log` + `ps`/`pgrep -x`/父进程链 + `/proc/<pid>/environ` | 下载/MD5 精确匹配；流式导入 51.6 秒零失败；1900 包（+1495）；ext4 有效数据 13,380,390,912 字节（k=3 夹逼）；VHD 13.01 GiB（系数 1.044）；同盘峰值 19.2 GiB；默认用户 openkylin/UID1000、sudo 口令 openkylin；xrdp+sesman enabled/active、`*:3390` LISTEN、localhost 转发通、eth0 172.25.189.68；唯一失败单元 systemd-binfmt（良性+自恢复 drop-in）；默认星标不变；**首登黑屏根因=startwm.sh `unset XDG_RUNTIME_DIR` 致 KWin 冷启动不驻留，用户级 ~/.xsession 修复后重登进入完整 UKUI（父进程链/环境变量证实）**；未覆盖：内存失败下界、`--shutdown` 后 IP 漂移、unregister 回收 |

## A.8 2026-10-08 Kylin AI SDK 文字识别（OCR）落机 POC 信源（S34）

> 对应方法论编排 session `sc-20261008-openkylin-ai-poc`（R→I→F→V→C），在 S33 落机的同一台 openKylin-3.0-desktop WSL（发行版名 `openKylin-3.0-desktop`）内实施。本信源是对主教程 I-3 自登记"最小 POC"缺口的运行时闭环，完整过程、C++ 源码与逐条证据集中于 [ai-sdk-ocr-poc.md](ai-sdk-ocr-poc.md)。

| 键 | 信源 | 环境 / 位置 | 采集方式 | 支撑事实（F-058 ~ F-066） |
|---|---|---|---|---|
| S34 | 本机 POC：镜像 AI 组件盘点 → apt 装 SDK → 读头文件 → g++ 编译 → OCR 识别中英文图 → 本地/云后端三路区分 → 配置 API 一致性核查 | openKylin-3.0-desktop WSL（huanghe，WSL 3.0.2.0/内核 6.18.40，g++ 15.2.0，16 GiB，/dev/dxg 在但 GPU 为 Microsoft Basic Render Driver 半虚拟化，CPU 推理）；开发包 `libkylin-ai-base-dev 2.0.0.0-ok1.0`（sudo 口令 openkylin）；工程目录在 WSL 挂载点 `/mnt/c/Users/xinzo/ai-poc/`（不入库，仅供复现） | 容器内 `dpkg-query -W`/`apt-cache show`/`Depends`、`systemctl status`、`apt-get install --no-install-recommends`；`ls/cat /usr/include/kylin-ai/*.h` 与 `ai-base/*.h`；`g++ *.cpp -lkylin-ai-base` 编译运行；`ldd libkylin-ai-base.so.2`；`gsettings/dconf read org.openkylin.aisdk.vision`；`tesseract --version` 与 CLI 同轴对比；Pillow 造 720×220 中英文测试图；宿主 `fsutil sparse queryflag`/文件 Attributes 复核 VHD（14.36 GiB，非稀疏非压缩） | 预装 kytensor-llm/server/client、llm-backend(llamacpp) 而无模型无服务；SDK/runtime/model-manager 未预装可装、ollama 不在官方源；安装下载 39.1MB/新增 4 包、tesseract 5.3.4-ok4+chi_sim/eng/osd 4.1.0、VHD +约1.35GiB；OCR 同步三函数+NLP 异步回调+三能力三策略枚举；config.h 裸 enum 无 typedef 致 gcc 失败/g++ 通过；四判据全满足、识别可用精度中等（形近误识）；ldd 直链 libtesseract+liblept、gsettings 权威 LOCAL、CLI 同源误识字不同三源钉死本地离线；get/set_deploy_policy 返回值与 dconf 错位（如实登记不强行归因）；8 域仅 OCR 闭环、其余 7 域与错误码成文未验证，NLP 需自备 GGUF 或云密钥 |

## A.9 2026-10-08 AI 子系统与显示双栈源码架构信源（S35）

> 对应方法论编排 session `sc-20261008-openkylin-source-deepdive`（R→I→V→C，depth=deep），在 S33/S34 同一台 openKylin-3.0-desktop WSL（发行版名 `openKylin-3.0-desktop`，huanghe）内实施。范围经用户拍板**严格限定 openKylin 3（huanghe）**：一切结论以本机 huanghe 源已装/候选包与本机文件为准，上游 `openkylin/nile*` 分支仅在其源码被 huanghe 二进制实际采用时作旁证。取证全程只读：**未安装任何新包、未启动服务、未下载模型**；源码探针为浅克隆副本，留本机 `.temp/source-probe/` 不入库。完整证据见 [ai-subsystem-source-architecture.md](ai-subsystem-source-architecture.md)（F-067～F-077）与 [kylin-wayland-compositor-architecture.md](kylin-wayland-compositor-architecture.md)（F-078～F-086）。

| 键 | 信源 | 环境 / 位置 | 采集方式 | 支撑事实（F-067 ~ F-086） |
|---|---|---|---|---|
| S35 | 本机只读核验（AI 两代 SDK/运行时/服务面 ＋ kywc/KWin 双栈包/会话/设备面）＋ 8 个 Gitee 上游源码仓浅克隆审阅 | 容器：openKylin-3.0-desktop WSL（huanghe，WSL 3.0.2.0/内核 6.18.40，源 `archive.build.openkylin.top/openkylin huanghe`）；源码仓：`kylin-ai-subsystem`（分支 `openkylin/huanghe` 与 `upstream`）、`kylin-ai-engine`、`kysdk-ai-common`、`libkysdk-genai-nlp`、`libkysdk-genai-vision`、`kylin-ondevice-nlp-engine`（默认 `openkylin/nile`）、`libkylin-ai-base`（`upstream`，无 huanghe 分支）、`kylin-wayland-compositor`（`openkylin/huanghe`，1.3.1-ok33 世代） | 容器内 `dpkg-query -W/-s/-L`、`apt-cache policy/show`（含 Depends）、`ls/cat` 头文件与 `/usr/share/{wayland-sessions,xsessions}`、`systemctl list-unit-files` 与 user 单元、`ls /dev`、`/mnt/wslg/weston.log`、`ldd`；Gitee tree/raw 网页触发反爬验证，改用宿主 `git ls-remote --heads` + `git clone --depth 1 [--branch]` 后本地 Read/Grep 取证（genainlpserver.cpp 第 5-7 行、aiengine.h、nlp/llm.h、backend.c、wrapper.c、docs/PROTOCOLS.md、debian/control） | **AI（F-067～F-077）**：Gen1/Gen2 两代 SDK 同机并存与版本清单；Gen2 per-uid 私有 socket gdbus IPC（源码常量）与纯代理 Depends；AbstractAiEngine 插件 ABI 与 7 引擎头；ondevice-nlp-engine=Triton 客户端（:8000/:8001/llama.cpp 参数）；本地 NLP 包级链路（修正 F-066）；huanghe 源可装未装/无候选矩阵；元包 huanghe control 全栈且不含 Gen1、repos.md 仅 nile-sp2；服务面仅 kytensor enabled；Gen1 源码-二进制分叉。**显示（F-078～F-086）**：kywc 1.3.1-ok33 与 kwin-x11 5.24.4 双栈同装；两个会话描述符与用户单元位置；后端三级策略（嵌套/DRM/fbdev）；wrapper→systemd user target 链路；标准+KDE+UKUI+kywc 协议矩阵；WSL 无 dri/fb 仅 dxg、WSLg weston rdprail-shell、实际 xrdp→Xorg→KWin；嵌套未实测；F-057 修复不可跨栈套用 |

## A.10 引用可靠性分级

1. **制度级**（S05 版本规划、S17 CLA、S18 角色、S20 AI 守则、SIG 章程）：TC 表决或社区政策文件，最高可信；
2. **操作手册级**（S06/S07/S08/S12/S13/S15/S23/S24/S30）：平台/操作文档，2026-09 多篇仍有提交，需连同适配版本号一起引用；
3. **导航/短页级**（版本发布动态、社区项目地图、文档平台使用指南等）：内容短、可能为占位，只作入口不作事实源；
4. **时效存疑级**：4 篇"（需要更新）"、"失效文档"目录、S09 等 1.0 时代文章、含旧编号路径的链接——引用时必须标注时效风险；
5. **本仓实测级**（S26、S32、S33、S34、S35）：单机实测，环境明确（S26/S32 为 Win10.0.19044/WSL 2.9.3.0；S33/S34/S35 为 Win10 26220/WSL 3.0.2.0 上的 openKylin-3.0-desktop），换环境结论可能不同；S33 已覆盖服务级与**交互桌面级**（含一次黑屏故障的根因与用户级修复），跨 openKylin/WSL 版本复用前需按其判别步骤重新取证；S34 覆盖 **AI SDK OCR 一域的运行时 POC**（同机 CPU 离线 tesseract 路径），仅证明该版本包/头文件/本地后端当下可用，其余 7 能力域与识别精度的跨版本表现须各自重新取证；S35 为**本机只读核验＋上游源码审阅级**（未装包/未启服务/未跑运行时链路）：包/版本/设备节点/单元位置为本机事实，socket 地址/接口名、引擎 ABI、后端策略等为**源码级事实**（文件路径与行号已锚定），运行时连通性、kywc 嵌套 WSLg 出图、ABI 与候选二进制逐字一致性均未验证，且结论限定 huanghe、nile 内容仅旁证；
6. **远程核验级**（S27/S28/S29）：仅覆盖文件级属性（URL、字节数、MD5、魔数、ISIZE、头部条目），可复现但**不包含运行时可用性结论**（该批事实 2026-10-08 经 S33 导入实测间接验证）；S31 为负证据，随时间可能失效。
