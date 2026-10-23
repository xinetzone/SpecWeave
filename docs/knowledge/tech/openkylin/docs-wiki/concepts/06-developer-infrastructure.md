# 06 开发者基础设施：CLA、Gitee、OKBS、版本构建与定制

> 文档站 1_5 板块（61 篇）的核心价值是把 openKylin 的供应链操作**逐命令文档化**。本文按贡献者的上手顺序串起五个环节：法律前置 → 代码托管 → 软件包编译 → 镜像构建 → 应用移植与桌面开发。

## 6.1 第 0 步：签署 CLA（法律前置）

向任何 openKylin 仓库提交代码前必须先签 CLA（Contributor License Agreement，贡献者许可协议）：

- 入口：https://cla.openkylin.top ；
- 三类身份：**个人 CLA**（个人贡献）、**员工 CLA**（以企业员工身份）、**企业 CLA**（企业主体）；
- 协议约束三件事：版权归属、专利授权、法律声明——既保护项目方也保护贡献者；
- AI 辅助提交时 `Signed-off-by` 只能由人类添加，AI 不能作为签署主体（见 [05 §5.4](05-ai-stack.md#54-治理层ai-辅助贡献守则使用者也应了解)）。

## 6.2 第 1 步：Gitee 协作工作流

- 代码组织在 Gitee `openkylin` 组织下（community、docs、kaiming 等仓库），issue 集合入口 gitee.com/openkylin/community/issues；
- 配套手册：《Gitee使用指南》《Gitee_CI&CD使用指南》《openKylin源码包git工作流》；
- docs 仓库的分支纪律可视为全社区惯例的缩影：SIG 成员建 `dev-名字` 分支，非 SIG 成员先 fork 再从自己仓库 dev 分支提 PR；主分支只收 dev 分支 PR、禁止强推；
- 文档类提交前可读《文档平台使用指南》《翻译平台使用指南》《邮件列表使用指南》（前两者目前为短页，具体规范以首页"文档贡献指南"为准）。

## 6.3 第 2 步：OKBS 软件包编译平台（打包入库）

OKBS（https://build.openkylin.top/）是个人/团队编译软件包并发布到 PPA 的平台，《OKBS软件包编译平台使用说明》的流程：

1. **注册**：邮箱前缀即个人 ID；个人主页创建 PPA（Personal Package Archives）并 Activate；
2. **SSH 公钥**：`ssh-keygen -t rsa` 生成，在平台 Import Public Key；
3. **PGP 公钥**：`gpg --full-gen-key`（默认 RSA 3072、永不过期）→ `gpg --fingerprint` 查看 → 上传到社区 keyserver：
   ```bash
   gpg --keyserver hkp://keyserver.build.openkylin.top:11371 --send-keys <keyid 后8位>
   ```
   再在平台 import key；
4. **配置 dput**（`~/.dput.cf` 或 `/etc/dput.cf`）：
   ```ini
   [okbs]
   fqdn=upload.build.openkylin.top:2121
   method=sftp
   incoming=%(okbs)s
   login=LOGIN
   ```
   需安装 paramiko（`sudo pip3 install paramiko`）；
5. **上传源码包到个人 PPA**：changelog 系列代号设为对应代号（文档示例 `yangtze`；2.0 用 `nile`），执行
   ```bash
   dput okbs:~<你的ID>/ppa <source.changes>
   ```
   结果在 http://archive.build.openkylin.top/dput-logs/ 查；
6. **进入官方源**：新源码包需先向技术委员会申请权限（见 SIG 成员与维护包变更流程），再 `dput okbs:openkylin <source.changes>`。

## 6.4 第 3 步：版本构建平台（从包到 ISO）

factory 平台（https://factory.openkylin.top/）用于制作系统镜像，需 openKylin ID 且联系社区开通权限。《openKylin版本构建平台使用说明》要点：

- **建任务**："我的版本→新建"，填名称版本号、选架构、类型选 `livebuild`；也可**继承**已有版本（推荐——自动沿用软件源快照）；
- **软件源快照**：继承快照 = 与父版本同一时点的包；不继承 = 拉所有源最新包；
- **四步配置**：①设置选项（bootstrap 软件源地址、系列代号 yangtze/nile/…）；②配置软件源（可加个人 PPA，优先级默认 500，需压过官方源时设 1000+）；③配置包列表（**live 列表**=装进系统的包；**iso 列表**=放光盘 pool 的包；用 deb 包名而非源码包名）；④上传额外配置文件（FTP）；
- **定制目录语义**（文档中最实用的一张表）：

| 目录 | 作用 |
|---|---|
| `hooks/` | bash 钩子：`.chroot_early`/`.chroot`（装包阶段）、`.binary`（mkiso 前） |
| `includes.chroot/` | 安装后系统根目录的额外文件（等同 `/`） |
| `includes.binary/` | ISO 内（试用模式）额外文件 |
| `packages.chroot/` | 直接装入 live 系统的 deb（**不自动解决依赖**，依赖包要一起放） |
| `packages.binary/` | 放光盘软件源的额外 deb |
| `archives/` | chroot/binary 阶段的 sources.list.d、preferences.d（勿动 kylin 开头文件） |
| `preseed/` | debconf 预置应答 |
| 其余 | binary_grub（grub 配置）、binary_rootfs/excludes（排除文件）、templates 等 |

提交后在"编译机→任务"看实时状态。

## 6.5 从源码到软件包：自主选型构建流程

15K 字符的《openKylin源码自主选型构建流程》是"根社区"工程独立性的关键文本，主线：

1. **版本选型策略**：软件项目选型策略 → 版本选型原则 → 软件分级与兼容性原则；
2. **获取项目地址与版本情况**：从上游（含 Launchpad 下载源码包、`apt-source`、`dget`，需 devscripts；或项目 ftp/git release）确认来源；去除 gpg 签名信息便于查看；
3. **构建源码包**：下载源码 → 调整目录格式 → 制作 debian 打包目录（区分上游自带 debian 目录与需自制两种情况）。

配合阅读：《openKylin打包指南》《软件包维护指南》《编译与构建指南》《软件协议规范》《openKylin软件包版权协议补充指南》。

## 6.6 其他开发专题索引

| 方向 | 文档 |
|---|---|
| 镜像定制 | 《openKylin系统镜像ISO定制指南》（与 6.4 平台手册互补） |
| 应用移植 | 三个专篇：Windows 应用、移动应用、移植 openKylin 应用到其他发行版；另有《移植GNU Hello软件到openKylin》入门例 |
| 桌面/输入法 | 《桌面环境移植》《openKylin系统输入法适配指南》《语音助手适配说明》 |
| 环境配置 | 《openKylin开发环境配置手册》《在openKylin配置nodejs开发环境》《本地编译Pytorch》 |
| RISC-V 开发 | 《RISC-V版本Arduino_IDE安装》 |
| 系统能力开发 | 《openKylin+SDK开发指南》《openkylin SDK开发指南》（新）、《插件编写指南》《签名认证指南》 |
| 调试与质量 | 《调试与追踪指南》《推荐开发者工具》《编码风格》 |
| UKUI 设计开发 | 4_9 的 22 篇（见 6.7） |
| AI 开发 | 见 [05 AI 三层体系](05-ai-stack.md) |
| 开源协议翻译 | freedesktop 协议翻译系列（XBEL、UTF8、媒体播放器规范等） |
| 社区全景 | 《社区项目地图》（当前为短索引页，实际仓库地图以 Gitee 组织页为准） |

## 6.7 UKUI 桌面设计规范（4_9，22 篇）

面向桌面/应用设计者与 UKUI 贡献者：

- **总览层**：《UKUI介绍》《UKUI3框架介绍》《UKUI4设计理念》《UKUI4_设计风格》；
- **设计指南层**：色彩、布局、主题控件库、图标设计、对话框、工具提示、指针、数据输入、界面用语、空状态、占位符、触控/触摸手势；
- **组件案例层**：录音、便签、天气等组件解析与鼠标指针交互等设计分享。

这组文档给出的是**贡献 UKUI/UKUI 应用时的视觉与交互一致性标准**，自研应用想"看起来像原生 UKUI 应用"应对照此清单。

## 6.8 规范类文件（2标准与规范板块）

- 《openKylin个人开发者参与指南》（2_1，当前为短页，与 4_8 同名文档互补）；
- 《openKylin需求管理规范》（2_2）；
- i18n SIG 规范中英文各一篇（2_3，英文篇在 2026-09-10 有更新）；多语言实操另见开发者指南中的《多语言本地化指南》。

> 上一篇：[05 AI 三层体系](05-ai-stack.md) ｜ 下一篇：[07 社区治理与贡献路径](07-community-and-contribution.md)
