# F 编号事实登记 —— CreatorHub（博文 + 官方仓库核验）

> **本表不含推断。** 每条均为博文（下称“源文”）明示内容的逐字登记，或经官方仓库/README/API 核验的外部事实。
> 类型枚举：`O`=客观事实，`V`=作者观点/评价，`S`=项目方（README/仓库）自述。
> 核验标记：`✅` 官方一致 ｜ `⚠️` 口径/时效差异（详见 verification.md）｜ `❌` 不成立 ｜ `—` 无需外部核验。
> 本表与 bundle `references/article-source.md` **双份登记**，编号集合必须逐字一致、连续无跳号。

- **主源文 URL**：https://mp.weixin.qq.com/s/Y5AvYGtyj2t9xPJIXuSYBA
- **主源文标题**：发现一个自媒体效率神器：CreatorHub，一个本地面板，把抖音小红书快手视频号全管了
- **发布方**：微信公众号「明见如是」（个人号）
- **发布时间**：2026-08-28 17:02
- **正文长度**：1761 字
- **采集时间**：2026-10-26
- **采集通道**：browser 提取 `#js_content` innerText
- **核验源**：GitHub REST API、main 分支 README（26,355 字节）、requirements.txt、CHANGELOG.md、git tree、根目录 contents API

---

## 一、博文元信息与核心叙述（F-001 ~ F-019）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-001 | O | 源文标题为《发现一个自媒体效率神器：CreatorHub，一个本地面板，把抖音小红书快手视频号全管了》 | 源文标题 | ✅ |
| F-002 | O | 源文由微信公众号「明见如是」于 2026-08-28 17:02 发布，正文 1761 字 | 源文页头与正文提取 | ✅ |
| F-003 | O | 源文 URL 为 https://mp.weixin.qq.com/s/Y5AvYGtyj2t9xPJIXuSYBA | 源文地址 | ✅ |
| F-004 | O | 源文描述多平台运营痛点：一个作品四个后台各传一遍、评论散落四个 App、评论三天后才看到、播放量要逐个 App 刷新 | 源文开头段 | — |
| F-005 | O | 源文将 CreatorHub 概括为“一个本地跑的 Web 面板”，把抖音、小红书、快手、视频号的管理从四个后台切换变成一个界面 | 源文“它是什么”段 | ⚠️ F-064 |
| F-006 | O | 源文给出的 GitHub 地址为 github.com/3441293738/creatorhub | 源文正文 | ✅ F-020 |
| F-007 | O | 源文称项目“1.7k star，Python 写的”，主打动作三个：监控、采集、搬运 | 源文项目介绍段 | ⚠️ F-061 |
| F-008 | O | 源文称作品/评论监控可告知关注账号的新内容，并把评论区汇总到一处查看 | 源文“作品/评论监控”段 | ⚠️ F-064 |
| F-009 | O | 源文称看到好的内容可直接下载，做好的内容可在面板里“统一发到多个平台” | 源文“内容下载与发布”段 | ⚠️ F-066 |
| F-010 | O | 源文称评论来了能自动响应，重要消息推送通知 | 源文“自动回复 + 通知”段 | ✅ F-043/F-046 |
| F-011 | O | 源文称面板本地运行、数据存本地、登录态留在本地，且“开源，能自己部署” | 源文“最戳我的一点”段 | ⚠️/❌ F-032/F-065 |
| F-012 | O | 源文称账号密码不经过第三方服务，内容版权归属清楚 | 源文“这意味着什么”段 | ⚠️ F-067 |
| F-013 | O | 源文称项目基础是 Python + FastAPI + Playwright | 源文“技术选型”段 | ⚠️ F-062 |
| F-014 | O | 源文称 Playwright 是浏览器自动化框架，纯 HTTP 难模拟完整用户行为，驱动真实浏览器是“目前最稳的方案之一” | 源文“重点说说 Playwright”段 | ✅ F-068（判断属 V） |
| F-015 | O | 源文称 FastAPI 把采集内容、监控结果、发布任务组织成 Web 面板，用户浏览器点选即可，不用碰代码 | 源文“FastAPI 负责”段 | ✅ F-029 |
| F-016 | O | 源文称整套是“浏览器自动化 + 本地 Web 服务”，不依赖外部数据库服务，部署门槛低 | 源文“整套东西”段 | ✅ F-032/F-054 |
| F-017 | O | 源文列出四个典型场景：矩阵号运营、竞品监控、私信/评论自动响应、内容备份 | 源文“它能帮你省下什么”列表 | — |
| F-018 | O | 源文列三点局限：需装浏览器内核“不是双击就完事”、平台风控变化要修脚本、自动发布建议先小规模试 | 源文“说点实话”列表 | ⚠️ F-063 |
| F-019 | V | 源文核心观点：“做多平台运营，最贵的从来不是工具，是你的注意力”“AI 负责提速，工具负责截断，你负责品味” | 源文结尾段 | — |

## 二、官方仓库身份与版本（F-020 ~ F-028）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-020 | O | 仓库 3441293738/creatorhub 存在，公开，创建于 2026-07-03T08:43:10Z，默认分支 main，最近推送 2026-10-26T01:53:09Z | GitHub API | ✅ |
| F-021 | O | 2026-10-26 快照：Star 2,562、Fork 472、开放 Issue 14 | GitHub API | ✅ |
| F-022 | O | 主语言为 Python；topics 含 automation、content-monitoring、crawler、douyin、fastapi、kuaishou、playwright、python、rednote、tiktok、web-scraping、xiaohongshu | GitHub API | ✅ |
| F-023 | O | 仓库 license 字段为 null，根目录无 LICENSE 文件 | GitHub API + 根目录 contents | ✅ |
| F-024 | O | 共 6 个正式 Release：v0.1.0（2026-09-10）、v0.2.0（09-14）、v0.2.1（09-16）、v0.2.2（09-18）、v0.2.3（09-20）、v0.2.4（10-16） | GitHub Releases API | ✅ |
| F-025 | O | 官方主页 https://3441293738.github.io/creatorhub/ 提供在线预览，使用脱敏示例数据，仅展示界面；登录、抓取、下载、发布仍需本地运行 | README 顶部 | ✅ |
| F-026 | O | 仓库一句话描述为“多平台内容监控·采集·搬运 一个 Web 面板管起抖音 / 小红书 / 快手”，未含视频号 | GitHub API description | ✅ |
| F-027 | O | README 自我定位为“本地运行的多平台内容管理面板，支持抖音 / 小红书 / 快手 / 视频号” | README 首行 | ✅ |
| F-028 | O | 仓库体积 12,977 KB，2026-10-26 仍在高频推送 | GitHub API | ✅ |

## 三、官方架构与技术栈（F-029 ~ F-035）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-029 | O | CreatorHub 使用 Python + FastAPI 提供统一 Web 界面，用于管理账号、监控作品与评论、下载内容、发布作品与接收通知 | README 架构段 | ✅ |
| F-030 | O | 浏览器交互按平台使用系统 Chrome CDP 或开源 Patchright，业务层统一使用兼容的 Playwright API；每个账号使用独立浏览器 Profile，Cookie、缓存、本地存储互不共享 | README 架构段 | ✅ |
| F-031 | O | requirements.txt 固定 fastapi==0.115.6、uvicorn==0.34.0、httpx[socks]==0.28.1、sqlmodel==0.0.22、patchright==1.61.2、xhshow>=0.2.0、curl_cffi>=0.15.0、yt-dlp>=2025.1.15 等，无 playwright 包 | requirements.txt | ✅ |
| F-032 | O | 数据目录为 `data/`：creatorhub.db（SQLite）、media/（下载内容）、profiles/（账号浏览器配置与登录态）；config.yaml、数据库、登录态、媒体默认不提交 Git | README 数据目录与配置段 | ✅ |
| F-033 | O | 代码分层：app/main.py（492,518 字节）、app/engine/monitor.py（259,513 字节）、app/browser/（CDP/登录/抓取/代理/身份）、app/platforms/{douyin,xhs,kuaishou,channels}/、app/web/（app.js 486,951 字节、workbench.js 328,125 字节） | git tree | ✅ |
| F-034 | O | 仓库含 selftest.py、tests/ 目录与 pytest.ini，提供自检与测试入口 | git tree + README 手动安装 | ✅ |
| F-035 | O | 首次运行自动创建虚拟环境、安装依赖和 Chromium、生成 config.yaml，随后打开 http://127.0.0.1:8000 | README 一键启动 | ✅ |

## 四、平台能力矩阵与功能边界（F-036 ~ F-046）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-036 | O | 登录方式：抖音支持扫码/创作者/Cookie；小红书支持扫码/创作者；快手支持扫码/创作者；视频号仅扫码 | README 平台能力表 | ✅ |
| F-037 | O | 关键词批量采集：抖音、小红书支持作品/笔记、评论、媒体；一次最多输入 20 个关键词，可设每词作品数、采集深度、排序、发布时间、类型、互动门槛、每作品评论数、二级评论与媒体下载；支持编辑续跑去重与 Excel 导出 | README 基本使用 | ✅ |
| F-038 | O | 作品监控：添加创作者主页、作品链接、短链或平台 ID，发现新作品自动入库；抖音、小红书、快手支持不同执行账号分别订阅同一主页，同账号同主页仅允许一条任务 | README 基本使用 | ✅ |
| F-039 | O | 评论监控：可订阅单条作品，也可监控账号近期作品评论 | README 基本使用 | ✅ |
| F-040 | O | 短视频弹幕监控：抖音支持播放页/创作中心，独立于评论区，按视频时间轴渐进探测并排序，支持时间范围、关键词、文本长度、点赞数、容量上限过滤，持久化到 SQLite | README 平台能力表与基本使用 | ✅ |
| F-041 | O | 内容下载支持断点续传与失败重试；抖音可选画质，小红书支持图集和视频；多任务下载同一媒体至同一路径时串行写入并复用已有文件 | README 基本使用 | ✅ |
| F-042 | O | 发布：小红书支持图集、视频和定时发布；抖音、快手、视频号通过对应创作平台发布；已下载的抖音作品可转发到小红书或视频号，小红书作品可转发到抖音，发布前可改标题、正文、话题 | README 发布与转发 | ✅ |
| F-043 | O | 自动评论/回复：支持关键词、排除词、多模板、回复冷却、最大消息年龄；默认生成待审核草稿，免审核模式仍受活跃时段、统一写间隔、小时/每日上限与风险冷却约束 | README 本账号与通知 | ✅ |
| F-044 | O | 本账号管理：抖音支持作品/关注/粉丝/私信，小红书支持作品/关注/粉丝/私信，快手支持作品/关注/粉丝，视频号支持作品/数据/评论 | README 平台能力表 | ✅ |
| F-045 | O | 视频号只支持创作者助手中的本账号数据，不支持监控或下载他人作品 | README 平台能力表注 | ✅ |
| F-046 | O | 通知渠道支持 Bark、钉钉、Telegram；可启用作品健康监控，对零播放、违规或下架状态发送提醒 | README 本账号与通知 | ✅ |

## 五、任务队列、风控与账号隔离（F-047 ~ F-053）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-047 | O | Web 面板「任务队列」统一展示采集、发布、自动评论、账号动作、下载任务，支持按平台、队列类型、状态、关键词筛选；所有平台操作经过持久化调度与风控检查 | README 任务队列 | ✅ |
| F-048 | O | 默认 `risk_control.mode: conservative`：同账号评论/账号动作/私信/发布共享写操作间隔与额度，立即执行不绕过冷却；同一网络出口账号串行访问；写间隔、小时/每日额度、同出口并发为不可放宽保护线，配置 0 表示沿用保护线 | README 默认策略 | ✅ |
| F-049 | O | 命中 403/429/461/471、验证码或明确风控提示后按阶梯进入冷却；被额度、时段、代理状态或冷却拦下的任务保持 pending，重启后恢复；登录态失效时任务保留等待重新登录；冷却结束后先间隔式轻量探测，连续成功再逐级恢复 | README 默认策略 | ✅ |
| F-050 | O | 账号代理支持 HTTP、HTTPS、SOCKS5 与账号密码认证；代理不可连接或认证失败时按失败关闭处理，不静默改走本机直连；建议同账号长期保持稳定出口 | README 浏览器环境 | ✅ |
| F-051 | O | 小红书 `xhs_browser_mode` 支持 auto（默认，系统 Chrome CDP）/cdp（严格）/patchright；旧值 playwright 自动迁移为 patchright；每个小红书账号独立 Profile 并长期复用 | README 小红书系统 Chrome CDP | ✅ |
| F-052 | O | 非小红书平台可选开源 fingerprint-chromium 作为可插拔内核；小红书拒绝第三方指纹内核与既有 Profile 混用；新指纹 Profile 首次会打开 browserscan.net 体检页，该第三方站点可见出口 IP 与浏览器特征 | README Fingerprint Chromium | ✅ |
| F-053 | O | 每个账号 Profile 有跨进程占用保护；同一出口下多账号集中触发风险时启用出口组熔断；风控中心展示正常/冷却/渐进恢复/登录失效/代理异常/网络熔断账号及事件时间线 | README 风控中心 | ✅ |

## 六、安装、配置与运维（F-054 ~ F-060）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-054 | O | Windows 安装版：从 Releases 下载 `CreatorHub-Setup-版本-windows-x64.exe`，双击安装，桌面快捷方式启动，无需自装 Python；适用于 Windows 10/11 x64；缺少 WebView2 时安装器联网安装；首次启动自动下载浏览器组件 | README 快速开始 | ✅ |
| F-055 | O | 源码运行要求 Python 3.10+、桌面环境（扫码登录需弹窗）、Google Chrome（小红书扫码建议）、Node.js 18+（仅小红书 api 发布兼容模式）、系统 ffmpeg（可选）；Windows 用 `.\start.cmd`，macOS/Linux 用 `./start.sh` | README 环境要求 | ✅ |
| F-056 | O | 手动安装命令：创建 venv、`pip install -r requirements.txt`、`python -m patchright install chromium`、复制 config.example.yaml 为 config.yaml、`python selftest.py`、`python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | README 手动安装 | ✅ |
| F-057 | O | 分享链接命令行：`python -m app.engine.share_downloader --links-only "完整分享文案或链接"` 仅解析不联网；加 `-o` 与 `-q` 下载内容 | README 分享链接命令行下载 | ✅ |
| F-058 | O | 常用配置项：engine.scan_interval_seconds=300、monitor_initial_backfill_count=0、worker_pool_size=2、scan_concurrency=2、account_check_interval_seconds=1800、media_dir=./data/media、work_health_enabled=false、storage.db_path=./data/creatorhub.db | README 配置示例 | ✅ |
| F-059 | O | README 使用须知：项目用于技术学习和个人内容管理，不提供账号、Cookie、代理或平台数据；使用时须遵守目标平台规则及所在地法律法规，尊重内容版权和个人隐私；备份项目建议一并备份 config.yaml 与 data/ | README 使用须知 | ✅ |
| F-060 | O | README 赞助商区展示 IPWO 住宅代理（含推广码），说明其用于公开数据采集、接口调试、自动化测试与多地区访问验证等合规场景 | README 赞助商 | ✅ |

## 七、核验差异与勘误事实（F-061 ~ F-068）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-061 | O | Star 数差异：源文 2026-08-28 口径 1.7k；官方 2026-10-26 快照 2,562。源文为发文时点动态值，无法回溯逐字验证，正文采用官方现值并标注时点 | 源文 vs GitHub API | ⚠️ |
| F-062 | O | 技术栈差异：源文称 Playwright；官方 requirements 使用 patchright==1.61.2（Playwright 兼容分支），浏览器后端为系统 Chrome CDP 或 Patchright，业务层 API 兼容 Playwright | 源文 vs requirements/README | ⚠️ |
| F-063 | O | 部署方式时效差异：源文称“不是双击就完事”（2026-08-28，当时无 Release）；v0.2.0（2026-09-14）起提供 Windows 安装版，Windows 10/11 x64 可双击安装；源码运行仍需 Python 与浏览器组件 | 源文 vs CHANGELOG/README | ⚠️ |
| F-064 | O | 视频号能力差异：源文标题与正文暗示四平台“全管”；官方口径为视频号仅支持创作者助手本账号数据，不支持监控或下载他人作品，无关键词采集、无自动评论 | 源文 vs README 平台能力表 | ❌ |
| F-065 | O | 许可状态差异：源文称“开源”；仓库公开但无 LICENSE 文件、GitHub license 字段为 null，默认版权保留（source-available），不构成 OSI 认可的开源许可，二次分发/商用需作者授权 | 源文 vs 仓库根目录/API | ❌ |
| F-066 | O | 发布口径差异：源文称“统一发到多个平台”；官方流程为各平台分别发布（抖音/快手/视频号走对应创作平台，小红书面板内发布），并提供下载后跨平台转发（抖音→小红书/视频号、小红书→抖音），README 未声明一次提交自动分发全平台 | 源文 vs README 发布与转发 | ⚠️ |
| F-067 | O | 账号凭据边界：架构上账号登录态存本地 Profile，不经作者服务器；但未检索到公开的独立安全审计，且 README 展示第三方住宅代理赞助商，平台流量仍经平台与所选代理，不能据此推断“零第三方接触” | 源文 vs README/架构 | ⚠️ |
| F-068 | O | 源文举例 MediaCrawler 同样使用 Playwright 驱动浏览器：外部核验其 README 明示“基于 Playwright 浏览器自动化框架登录保存登录态”，仓库 68,576 Star（2026-10-26 快照） | MediaCrawler README/API | ✅ |

## 八、补充核验（F-069 ~ F-072）

| 编号 | 类型 | 事实 | 信源定位 | 核验 |
|---|---|---|---|---|
| F-069 | O | 作品、评论、弹幕监控的新建/编辑支持秒级预设或自定义输入，范围 1–86400 秒；分钟可填小数（如 1.5 分钟=90 秒），换算后须为整秒；全局扫描间隔也支持直接输入秒数 | README 基本使用 | ✅ |
| F-070 | O | README 常见问题表列多类处理：macOS clang++ 失败删旧 .venv 重装；Patchright 找不到浏览器执行 `python -m patchright install chromium`；扫码无弹窗确认桌面环境/抖音用 Cookie；Windows Patchright 子进程错误用单 worker；抓不到作品检查登录态与频率；小红书解析失败重取含 xsec_token 链接；音视频异常更新依赖或用系统 ffmpeg | README 常见问题 | ✅ |
| F-071 | O | CHANGELOG 记录：v0.2.0 Windows 安装版/中文安装/一键更新；v0.2.1 抖音 API 与浏览器双通道；v0.2.2 秒级与自定义监控频率、多账号同主页监控；v0.2.3 抖音粉丝/关注/私信与 Windows 升级；v0.2.4 统一采集、小红书收藏夹、账号工作台、事件中心、Webhook 出站与 HMAC-SHA256 签名 | CHANGELOG.md | ✅ |
| F-072 | O | 小红书扫码登录只获取主站读取态；需要发布时须再使用独立的「创作者登录」入口；添加笔记或创作者监控建议使用包含 `xsec_token` 的完整链接；“页面可见但详情媒体未读取到”通常是访问参数或页面结构不兼容，不应单凭该错误判定账号失效 | README 基本使用 | ✅ |
