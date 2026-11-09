# 事实清单（Spec Mode · facts.md）

> 第二轮源码级事实。**双份登记**：`references/source-code-map.md` 与本文件 F 编号集合必须完全一致、连续无跳号。
> 首轮事实（F-001~F-057）见 [../wechat-intelligence-hub-blog-okf-wiki/facts.md](../wechat-intelligence-hub-blog-okf-wiki/facts.md)，本轮**续编** F-058~F-101。
> 类型：`O`=客观代码事实，`D`=由代码推导的确定性结论。核验级：P0/P1。结论：✅ 源码坐实 ｜ ⚠️ 与首轮存在漂移 ｜ ➖ 纯代码事实。

## A. 信源基线与仓库规模

| F编号 | 类型 | 声明 | 核验级 | 结论 |
|-------|------|------|--------|------|
|F-058| O | 本地源码副本 remote 为 `git@github.com:Rion-Wu-tech/wechat-intelligence-hub.git`，与首轮确认的主线仓库一致 | P0 | ✅ |
|F-059| O | 固定 commit 为 `fb6a42c34160d2ffa66ed5f114f8d8cdabe7f5f9`，提交信息「Fix contact discovery, scoped promises and multi-project follow-ups」，提交时间 2026-10-17 03:53:01 +0800 | P0 | ✅ |
|F-060| O | 仓库唯一 tag 为 `v0.9.2-preview.2`，指向 commit `6b73940a2286b20e51badbba7e0d4be633d24f61`（2026-09-04 22:55:07 +0800），**HEAD 领先该 tag 13 个提交**；tag 之后无新 tag | P0 | ⚠️ 首轮「当前版本 = v0.9.2-preview.2」需补范围限定 |
|F-061| O | HEAD 与 tag 之间差异为 64 个文件、+5569 / −202 行；新增 `docs/USAGE.md`（317 行）、`SECURITY.md`、`projects/rion-wechat-reader/rion_wechat_access.py`（954 行）、`projects/wechat-intelligence-hub/report_security.py`（96 行）、`providers/wxkey/` 候选工具目录 | P0 | ⚠️ 首轮核验的「README 快照」不含这些文件 |
|F-062| O | HEAD 口径跟踪文件共 **126** 个：43 个 `.md`、38 个 `.py`、12 个 `.sh`、8 个 `.png`、5 个 `.json`、2 个 `.yml`、2 个 `.yaml`、2 个 `.html`、2 个 `.txt` 等 | P1 | ➖ |
|F-063| O | Python 文件 38 个：非测试 **18** 个、测试 **20** 个；非测试代码 **16,007** 行、测试代码 **5,582** 行 | P1 | ➖ |
|F-064| O | 工作区 `git status` 为空（无未提交改动），源码副本与 commit 完全一致 | P0 | ✅ |
|F-065| O | 仓库顶层 6 个目录/文件族：`projects/`（两个子项目）、`skills/`（两个 Skill）、`providers/`（候选接入工具）、`docs/`、`scripts/`、`README.md` 等根文件 | P1 | ➖ |
|F-066| O | `projects/rion-wechat-reader/` 为只读 Reader 核心（`rion_wechat_reader.py` 3,465 行、`rion_wechat_access.py` 954 行、`scripts/` 下 `capability_gap.py`、`live_parity.py`） | P1 | ➖ |
|F-067| O | `projects/wechat-intelligence-hub/` 为上层情报产品（`wechat_intelligence_hub.py` 7,361 行、`intelligence_views.py`、`report_bundle_flagship.py`、`report_bundle_html.py`、`report_security.py`、`message_identity.py`、`message_time.py`、`opportunity_store.py`、`wechat_deal_radar.py`、`maintenance.py`） | P1 | ➖ |
|F-068| O | `skills/` 下两个 Skill：`wechat-cli`（Reader 侧，含 `access-onboarding.md`/`access-troubleshooting.md`/`experimental-access.md`/`windows-access.md`）与 `wechat-intelligence-hub`（含 `commands.md`/`delivery.md`/`group-editorial.md`/`onboarding.md`/`reply-style.md`/`signal-rules.md`） | P0 | ✅ 首轮「一个产品两个 Skill」坐实 |
|F-069| O | `rion_wechat_reader.py` 中 `TOOL_SPECS` 为 `dict[str, dict[str, Any]]`，**含 30 个工具条目** | P0 | ⚠️ 首轮 README 口径为 29 项 |
|F-070| O | 30 个工具的 `properties` 列表元素数之和为 **266**；去重后不同属性名为 **87** 个；其中 `stats`、`cache-status`、`cache-rebuild` 三个工具属性数为 0 | P0 | ✅ 266 与 README 口径一致；工具数存在 1 项差异 |
|F-071| O | 30 个工具名依次为：access-plan、sessions、contacts、resolve-chat、timeline、history、context、search、search-context、tail、unread、stats、members、schema、agent、cache-status、cache-refresh、cache-rebuild、export、announcements、sql、media、transfers、red-packets、forward-history、favorites、sns-feed、sns-search、sns-notifications、notifications | P1 | ➖ |
|F-072| O | 全部 30 个工具的 `aliases` 列表元素数之和为 **35** | P2 | ➖ |
|F-073| D | `tools_catalog()` 与 `tool_schema()` 两处均以字面量 `"read_only": True` 为**全部工具统一置位**（列表推导式内，无逐项开关）→ 只读是**结构性保证**，不存在某个工具可写 | P0 | ⚠️ 首轮「只读」仅为文档级断言，现为代码级结论 |
|F-074| O | Reader 源码中不存在任何 `send_message` / `send_text` / `post_message` / `write_*` 写入型函数 | P0 | ✅ 只读边界坐实 |
|F-075| O | 数据库快照以只读模式打开：`sqlite3.connect(f"file:{snapshot}?mode=ro", uri=True)`；`Snapshot` 上下文管理器对快照创建失败抛出「无法创建只读快照」 | P0 | ✅ |
|F-076| O | Reader CLI（`build_parser`）含 **36** 个 `add_parser` 子命令：version、tools、tool-schema、self-test、status、doctor、access-plan、setup、announcements、sql、media、transfers、red-packets、forward-history、favorites、sns-notifications、discover、import-access、init、sessions、contacts、resolve-chat、context、search、search-context、tail、unread、stats、members、schema、agent、cache-status、cache-refresh、cache-rebuild、export、notifications | P1 | ➖ |
|F-077| O | 36 个 CLI 子命令与 30 个工具的差集：仅 CLI 有 10 个（version、tools、tool-schema、self-test、status、doctor、access-plan、setup、discover、import-access、init 中的管理类）；仅工具有 4 个（history、timeline、sns-feed、sns-search，通过通用调度而非独立子命令暴露） | P1 | ➖ |
|F-078| O | 情报产品 CLI（`wechat_intelligence_hub.py` 的 `build_parser`）含 **37** 个子命令：profile-init、profile-status、compat-check、scan、vault-status、vault-scan、wechat-scan、wechat-labels、prioritize、daily、reactivation、group-daily、render-report、render-bundle、chat-history、common-groups、chat-search、db-index、db-search、db-status、cleanup、home、person、reply、topic、brief、contact-daily、today、inbox、triage、opportunities、opportunity-maintain、opportunity-sync、opportunity-update、feedback-add、feedback-list、db-links | P1 | ➖ |
|F-079| D | 两层 CLI 合计 **73** 个子命令，但二者角色不同：Reader CLI 面向**只读取数**，情报产品 CLI 面向**生成情报**；「36 / 37 / 30 / 73」是四个不同口径，不可互相换算 | P0 | ⚠️ 首轮未区分，计数易被误引 |
|F-080| O | `report_bundle_flagship.py` 的 `PAGE_SPECS` 为 4 元组列表，**含 4 条**：route=overview/file=index.md/title=综合行动报告/nav=综合行动；route=groups/file=groups.md/title=群聊日报/nav=群聊日报；route=contacts/file=contacts.md/title=重点联系人/nav=重点联系人；route=radar/file=radar.md/title=商单信号雷达/nav=信号雷达 | P0 | ⚠️ 首轮四入口名为「图注单源」，现为代码常量 |
|F-081| O | `report_bundle_flagship.py` 的 `SOURCE_RULES` 为 5 元组列表，**含 11 条**（含 5 条 kind=`internal` 的 collapsed 折叠项） | P1 | ➖ |
|F-082| O | `report_bundle_html.py` 另有**独立**的 `SOURCE_RULES`，**含 8 条**，kind 集合为 overview/groups/contacts/actions/links/evidence/audit，与旗舰渲染器的 11 条不同 | P1 | ⚠️ 「11 条」仅对旗舰渲染器成立，不可泛化 |
|F-083| O | 移动端导航由 `<nav class="mobile-routes" aria-label="移动端报告目录">` 承载，内容由 `mobile_nav_html` 按 `page.route`/`page.nav_label` 逐页生成；CSS 在 `@media` 断点下将 `.mobile-routes` 由 `display:none` 切换为 sticky 横向滚动条 | P0 | ⚠️ 首轮移动端为「图注单源」，现为实现级证据 |
|F-084| O | 明暗主题为**可运行机制**：工具栏 `#theme-button`（title「切换明暗主题」）点击切换 `document.documentElement.dataset.theme` 在 `dark`/`light` 间切换，并写入 `localStorage['wechat-flagship-theme']`；页面加载时读取该键恢复；`html[data-theme="dark"]` 定义整套 CSS 变量 | P0 | ⚠️ 首轮明暗主题为「图注单源」，现为实现级证据 |
|F-085| O | 打印与下载为独立按钮：`#print-button` 触发 `window.print()`，`#download-button` 下载当前分区 Markdown；`@media print` 规则隐藏侧栏、定位栏、移动端导航与底部导航 | P1 | ✅ 首轮「打印/导出当前分区」坐实 |
|F-086| O | 群聊页视图切换由 `view-switcher`（`role="tablist"`，`aria-label="群聊日报阅读方式"`）承担，视图状态存于 `localStorage['wechat-group-view']`，默认值 `topics` | P0 | ⚠️ 首轮「四视图」实为「群聊页三视图 + 四个顶层入口」 |
|F-087| O | `projects/wechat-intelligence-hub/docs/style-previews/` 含 **10** 个文件：style-a.png ~ style-d.png 四张风格预览图，加 flagship-preview.html、report-style-preview.html、flagship-today.png、flagship-today-mobile.png、flagship-topic.png、flagship-relationship.png | P1 | ➖ |
|F-088| D | 对 `style-previews/` 全目录做跨仓库引用检索（`--include=*.py --include=*.sh --include=*.md`），**无任何运行时代码引用该目录** → 10 个文件均为**设计期资产**，非运行时可选主题 | P0 | ⚠️ 首轮「四种视图风格」若被理解为运行时四套主题则**不成立** |
|F-089| O | 四套风格 A（静默情报台）/ B（情报编辑部）/ C（信号雷达）/ D（知识库导航）的定义出自 `projects/wechat-intelligence-hub/docs/report-redesign-research-2026-08-28.md` 的「四套待选视觉风格」章节，原文结论为「采用 **A 作为主框架**，B 作为群聊话题和项目详情的阅读风格，D 作为未来历史档案/开源文档层」，并注明「明暗模式是颜色模式，不作为另一套风格」 | P0 | ⚠️ 首轮「四种视图风格」为设计候选，非运行时能力 |
|F-090| O | `report_bundle_flagship.py` 内嵌字符串逐字写明「交互 HTML 只保留综合行动、群聊日报、重点联系人和商单信号雷达四个入口」与「群聊日报可切换话题视角和重点群视角」 | P0 | ✅ 四入口与群聊切换双源坐实 |
|F-091| O | `SECURITY.md` 明确「The Reader and Intelligence Hub are read-only with respect to WeChat: they do not send messages or automate replies」，并明确「The separate experimental `rion-wechat-access` helper is **not** read-only」，其可在 macOS 管理员授权下调用外部本地提供者，可能重启微信、调试进程并重签名影子副本 | P0 | ⚠️ 首轮 #9「不重签名」范围勘误被官方文档**逐字坐实** |
|F-092| O | `SECURITY.md` 规定报告渲染安全策略：Pandoc 禁用原始 HTML、用显式 nh3 白名单净化转换片段、以基于哈希的 CSP 限制脚本、禁用外部图片与自动网络请求、已知报告链接转本地导航、未知文件链接禁用、HTTP(S) 源链接保持手动导航 | P0 | ➖ |
|F-093| O | `report_security.py` 共 96 行、4 个函数：`require_sanitizer`、`safe_href`、`sanitize_fragment`、`protect_document`；HTML 生成在缺少 nh3 时**失败关闭**（不降级为未净化页面） | P0 | ➖ |
|F-094| O | HTML 依赖固定版本 `nh3==0.3.7`（`requirements-html.txt`），安装在 Hub 自有 `.venv`，不修改全局 Python；另需本机 Pandoc | P0 | ➖ |
|F-095| O | `intelligence_views.py` 含 **26** 个顶层函数，含 `home_report`、`person_report`、`topic_report`、`brief_report`、`reply_report`、`open_promise_rows`、`_reply_draft`、`_reply_intent`、`_summarize_reply_style`、`_global_reply_style`、`_current_chat_reply_style` 等 | P1 | ➖ |
|F-096| O | `_reply_draft` 的输出由 `intent` 关键词匹配的**确定性模板字典**生成，共 6 类：settlement（结算）、review（反馈）、quote（报价）、brief（需求）、schedule（进度）、general（通用），并按关系远近（close）选用不同措辞 | P0 | ⚠️ 首轮「回复草稿」为「图注单源」，现补充「模板非模型自由生成」的实现事实 |
|F-097| O | 情报产品 CLI 的 `reply` 子命令 help 为「根据联系人上下文生成只读回复建议，不发送微信」，并提供 `--style-days` 参数覆盖 Profile 中的本人私聊风格窗口天数 | P0 | ✅ 只读坐实 |
|F-098| O | `skills/wechat-intelligence-hub/references/reply-style.md` 规定：个人语言习惯取自安装者最近 **30 天**跨联系人私聊聚合特征，当前会话称呼/语气/关系证据优先于全局习惯，未配置本人昵称或样本不足时使用中性草稿；技能包不得包含任何姓名、联系人、绝对路径、聊天原文、个人统计、关系标签或学习结果 | P0 | ➖ |
|F-099| O | `docs/USAGE.md` 明确回复能力边界：「不能。整个项目坚持微信只读，回复能力只生成草稿」，且「系统只生成本地草稿，不会发送微信。金额、日期、报价和承诺必须由使用者核对」 | P0 | ✅ 坐实 |
|F-100| O | `docs/USAGE.md` 第 4 章「按信息、人、物、标签或事件定向查找」列出 **5 个**子类型：某条信息、某个人、某个产品或事物、某个微信标签、某个项目或事件；文中「物」可指产品、工具、课程、公司、品牌、文件、链接等，名称歧义时系统应先列候选范围 | P0 | ⚠️ 首轮「检索五维度」为「图注单源」，现为官方文档逐字坐实 |
|F-101| D | 综合 F-060~F-101：首轮 22 项 P0/P1 的 8 项 ⚠️ 中，**5 项（#16 四入口名、#18 明暗主题、#19 移动端、#20 重点联系人与回复草稿、#17 检索五维度）被源码或官方文档坐实或修正**；**#9 不重签名范围被官方 `SECURITY.md` 逐字坐实**；**#5 星标数与 #6「5 天」窗口维持 ⚠️**（源码无法提供 star 时序数据）；此外**新增 3 项源码级发现**（工具数 29→30、四视图为设计候选、HEAD 领先 tag 13 提交） | P0 | ⚠️ 首轮结论需定向修订 |

## 编号自检

- **本文件 F 编号范围**：F-058 ~ F-101，共 **44** 条
- **连续性**：✅ 连续无跳号
- **与首轮衔接**：首轮 F-001~F-057，本轮自 F-058 起，**零重叠**
- **双份登记**：`references/source-code-map.md` ↔ 本文件，编号集合相等（由 `verify_facts.py` 核验）
