# Facts: Qwen-UI-Agent 网站仓 + MAI-UI-blog 博客站
> 信源根 A：external/libs/tools/Tongyi-MAI/Qwen-UI-Agent（Next.js 技术报告网站仓）
> 信源根 B：external/libs/tools/Tongyi-MAI/MAI-UI-blog（模型家族发布博客站）

# A 部分：Qwen-UI-Agent（信源根 A，F-001~F-024）

## F-001 仓库为网站源码，非实现代码仓（README 原文引证）
- 位置: README.md（L3-21）
- 内容: README 顶部 IMPORTANT 块原文："**Website source only — this is not the Qwen-UI-Agent implementation repository.** This repository contains only the source code and static assets for the Qwen-UI-Agent project website ... It does **not** contain the model, training code, or agent implementation."；中文段原文："**本仓库仅为网站源码，并非 Qwen-UI-Agent 的项目实现代码仓。** ... 不包含模型、训练代码或智能体实现代码"。

## F-002 官方实现代码仓指向 Tongyi-MAI/MAI-UI
- 位置: README.md（L11-12、20-21）
- 内容: README 明确写 "Looking for the Qwen-UI-Agent code? Visit the official project repository: **Tongyi-MAI/MAI-UI**"（英文/中文两处重复）。网站地址为 https://tongyi-mai.github.io/Qwen-UI-Agent/。

## F-003 站点定位与主流程
- 位置: README.md（L23-25、86-87）
- 内容: 原文："This repository powers the bilingual Qwen-UI-Agent technical report website. The site presents real-world capabilities, benchmark results, broader general and agentic capabilities, playable demos, and release materials."；主流程原文 "The primary flow is Capabilities → Performance (including Broader Capabilities) → Demos → Citation."

## F-004 package.json 包名与脚本
- 位置: package.json（全文）
- 内容: name `qwen-ui-agent-tech-report`，version 0.1.0，private，`"type": "module"`，engines `node >=22.13.0`。scripts：`dev`/`build`/`start` 均调用 `vinext`（带 `WRANGLER_LOG_PATH=.wrangler/wrangler.log`）；`build:pages` = `next build`；`test` = `npm run build && node --test tests/rendered-html.test.mjs`；`lint` = eslint；`db:generate` = `drizzle-kit generate`；另有 `validate:pages`（node scripts/validate-pages-prefix.mjs）与 `export:review`（node scripts/export-self-contained.mjs）。

## F-005 依赖清单（技术栈）
- 位置: package.json（L19-42）
- 内容: dependencies：next 16.2.6、react 19.2.6、react-dom 19.2.6、drizzle-orm 0.45.2。devDependencies：vite 8.0.13、vinext 0.0.50、wrangler 4.92.0、@cloudflare/vite-plugin 1.37.1、@vitejs/plugin-rsc 0.5.26、tailwindcss 4.2.1（及 @tailwindcss/postcss）、typescript 5.9.3、drizzle-kit 0.31.10、eslint 9.39.4、react-server-dom-webpack 19.2.6。

## F-006 双构建轨道：vinext（Cloudflare）与 next build（GitHub Pages）
- 位置: package.json（L9-14）；build/sites-vite-plugin.ts
- 内容: 同一源码存在两条构建路径：`vinext dev/build/start` + wrangler（Cloudflare 运行时）与 `next build`（`build:pages`，产出 GitHub Pages 静态站）。`build/sites-vite-plugin.ts` 定义名为 "sites" 的 Vite 插件（`apply: "build"`），在 `closeBundle` 时把 `.openai/hosting.json` 与 `drizzle/` 迁移目录复制到 `dist/.openai/`（注释原文 "Packages Sites metadata and migrations after Vite finishes compiling."）。

## F-007 next.config.ts 静态导出配置
- 位置: next.config.ts（全文）
- 内容: `output: "export"`（注释原文 "Keep the site fully static so the same source can be exported for GitHub Pages."）、`trailingSlash: true`、`basePath` 取自环境变量 `NEXT_PUBLIC_SITE_BASE_PATH`、`images: { unoptimized: true }`。

## F-008 sitePath.ts 的站点 URL 与 basePath 机制
- 位置: app/sitePath.ts（全文）
- 内容: `SITE_BASE_PATH` 读自 `NEXT_PUBLIC_SITE_BASE_PATH`（去尾斜杠，默认空串）；`PUBLIC_SITE_URL = "https://tongyi-mai.github.io/Qwen-UI-Agent/"` 硬编码；导出 `siteAsset()`（为以 `/` 开头的路径补 basePath 前缀）与 `absoluteSiteUrl()`（拼出绝对 URL）。

## F-009 layout.tsx 的站点 metadata
- 位置: app/layout.tsx（全文）
- 内容: metadata：title "Qwen-UI-Agent — Technical Report"；description "Qwen-UI-Agent is Alibaba's next-generation real-world-centric GUI agent for mobile, computer use, web browsers, and cross-platform workflows."；applicationName "Qwen-UI-Agent"；authors `[{ name: "MAI-UI Team" }]`；openGraph 图 og.png（1536x1024）；viewport themeColor "#ffffff"、colorScheme "light"；根节点 `<html lang="en">`（语言属性固定英文，双语由内容层处理）。

## F-010 首页仅渲染 ReportPage 组件
- 位置: app/page.tsx（全文 5 行）
- 内容: 默认导出 `Home()` 返回 `<ReportPage />`（来自 `./components/ReportPage`）。README 编辑指南对应原文 "Edit page structure in `app/components/ReportPage.tsx`"、"Edit the visual system and responsive layout in `app/globals.css`"。

## F-011 双语机制：Language / LocalizedText / localize
- 位置: app/siteContent.ts（L1-6、1723）
- 内容: `export type Language = "en" | "zh"`；`LocalizedText = { en: string; zh: string }`；文件末尾导出 `localize(text: LocalizedText, language: Language)` 函数。所有站点文案以 en/zh 双字段成对维护。

## F-012 SITE_COPY 导航与关键文案
- 位置: app/siteContent.ts（L8-109）
- 内容: en.nav 为 `["Capabilities", "Performance", "Demos", "Citation"]`（zh 对应「智能体能力/性能指标/演示/引用」）；subtitle en "Towards Next-Generation Real-World Centric Foundation GUI Agent" / zh "阿里巴巴集团的新一代真实场景 GUI 智能体"；性能表列名 `baseColumn: "Qwen3.5-27B"`、`oursColumn: "Qwen-UI-Agent"`；`sourceNote` 原文 "Content and metrics are distilled from the current LaTeX draft. Values may change before release."（zh：「内容与指标来自当前 LaTeX 草稿，正式发布前仍可能调整」）；`groundingFootnote` 与 `generalProtocolNote` 均声明分数由作者在自有评测环境独立复现。

## F-013 APPLICATIONS 六卡片与视觉类型
- 位置: app/siteContent.ts（L111-149 起）；README.md（L53-57）
- 内容: `APPLICATIONS` 数组元素 `kind` 枚举为 "mobile" | "computer" | "gui-cli" | "browser" | "research" | "proactive" 六种；`visual` 类型联合为 `mobile-ui`（CSS 绘制手机场景）/ `video`（本地循环视频）/ `gui-cli` / `browser-capture`（三帧动画浏览器序列）/ `research-flow` / `proactive-flow` / `image`。README 原文："`APPLICATIONS` controls the six visual slides in the interactive 'what it can do' carousel."

## F-014 METHOD_STEPS 四阶段方法流水线
- 位置: app/siteContent.ts（L983-1025）
- 内容: 四步字面：01 Environment infrastructure（stat "≈10K concurrent"，覆盖手机、电脑、网页与 DeepSearch 沙箱 + 真实设备运行时）；02 Agent-driven data flywheel（stat "≈10K task-verifier pairs"，Agent 构造任务、环境、verifier、失败诊断与迭代计划）；03 SFT + ActionRL + Online RL（stat "100+ step trajectories"）；04 Proactive harness（stat "Mobile + Desktop + Search"，通知驱动主动服务、共享状态、跨平台规划、用户确认边界）。

## F-015 PERFORMANCE_BENCHMARKS 代表分数
- 位置: app/siteContent.ts（L544-588）
- 内容: MobileWorld 条目（metric "GUI-Only Success rate (%)"）：Qwen-UI-Agent 27B 82.1（access "ours"）、Seed 2.1 Pro 73.2、GPT-5.6 Sol 70.1、Claude Opus 4.8 67.5、Qwen 3.7 Plus 62.3、Gemini 3.1 Pro 58.1。MobileWorld-Real 条目（真实手机）：Qwen-UI-Agent 27B 92.2、Seed 2.1 Pro 88.7、Gemini 3.1 Pro 86.2，并带 `href: "/mobileworld-real/"` 链接。

## F-016 第二路由页 mobileworld-real
- 位置: app/mobileworld-real/page.tsx（全文）；app/components/MobileWorldRealPage.tsx
- 内容: 路由 `/mobileworld-real/` 渲染 `MobileWorldRealPage`；metadata 描述原文："MobileWorld-Real is a real-device benchmark with human-written mobile tasks across live Android apps, accounts, content, and networks."；openGraph 描述 "everyday mobile GUI work across 409 tasks and 104 live Android apps"。

## F-017 数据库 schema 故意留空
- 位置: db/schema.ts（全文 4 行）
- 内容: 原文注释："// Intentionally empty by default. // Add Drizzle tables here when the site actually needs a database. // See examples/d1/db/schema.ts for an opt-in example."，文件仅 `export {}`。即当前站点无任何数据表定义。

## F-018 drizzle.config.ts 配置
- 位置: drizzle.config.ts（全文）
- 内容: `defineConfig({ out: "./drizzle", schema: "./db/schema.ts", dialect: "sqlite" })`。

## F-019 GitHub Pages 部署 workflow
- 位置: .github/workflows/deploy-pages.yml（全文）
- 内容: workflow 名 "Deploy GitHub Pages"，push main 或手动触发；Node 22 + `npm ci`；构建环境变量 `NEXT_PUBLIC_SITE_BASE_PATH: /Qwen-UI-Agent` 下执行 `npm run build:pages`，随后 `npm run validate:pages` 校验部署路径，上传 `./out` 至 deploy-pages@v4。

## F-020 测试与自检脚本
- 位置: tests/rendered-html.test.mjs；scripts/validate-pages-prefix.mjs；scripts/export-self-contained.mjs
- 内容: 三文件均存在；`npm test` 流程为先完整构建再用 Node 内置 test runner 对"构建产物 HTML"跑测试（package.json L15）；`validate:pages` 校验 Pages 前缀路径；`export:review` 产出自包含审阅导出。

## F-021 Demo explorer 五大域与指令来源语言标注
- 位置: README.md（L64-81）；app/siteContent.ts（L1115-1196，DEMO_CATEGORIES/DEMO_VIDEOS）
- 内容: README 原文：五个域为 "real-device mobile, computer use, cross-device GUI use, mobile use with Deep Research, and proactive service"；五个真机工作流与两个 Computer Use 完整工作流托管于 `public/demos/source/`（720p H.264）；Deep Research 域内嵌两个官方 Bilibili 演示；"Every `DEMO_VIDEOS` entry records its original instruction language in `instructionSourceLanguage`. The opposite-language interface automatically marks the instruction as `translated from Chinese` or `翻译自英文指令`."

## F-022 MODEL_ORGANIZATIONS 与本地化品牌 logo
- 位置: README.md（L58-59、97-101）；app/siteContent.ts（L361 起）
- 内容: README 原文："`MODEL_ORGANIZATIONS` maps each benchmark entry to its visible publisher label and local asset in `public/brand-logos/`"；"The compact benchmark logos are stored locally so the charts do not depend on third-party requests. Most SVGs come from Lobe Icons 1.94.0; Gemini and Anthropic use the supplied reference icons, and the Apodex avatar comes from its official Hugging Face organization."

## F-023 GENERAL_CAPABILITY_GROUPS 与 open-sourced 专才键
- 位置: README.md（L60-61）；app/siteContent.ts（L853-855）
- 内容: README 原文："`GENERAL_CAPABILITY_GROUPS` is rendered inside Performance as the 'Broader Capabilities' subsection; it is not a standalone page section."；`SpecialistKey` 类型字面量为 `"guiOwl" | "uiVenus" | "openCUA"` 三个专才模型键。

## F-024 站点当前状态声明
- 位置: README.md（L83-95）
- 内容: 原文："Replace the `Coming soon` resource cards with the final technical report, code, and checkpoint URLs at release time."；"External reference embeds remain explicitly labeled as temporary samples."；"Result figures that conflict across the current draft are intentionally omitted until the technical-report values are frozen."；导航/基准域/演示类目等所有可见文案须提供英文与完全本地化中文，"Model and benchmark proper names remain unchanged."

# B 部分：MAI-UI-blog（信源根 B，F-025~F-040）

## F-025 站点标题与论文链接
- 位置: site/index.html（L7、113-115、158）
- 内容: `<title>MAI-UI: Real-World Centric Foundation GUI Agents</title>`；h1 同文；Paper 按钮指向 https://arxiv.org/abs/2512.22047。

## F-026 作者与机构署名
- 位置: site/index.html（L116-153）
- 内容: 作者列表含 Hanzhang Zhou*、Xu Zhang*、Panrong Tong、Jianan Zhang、Liangyu Chen、Quyu Kong、Chenglin Cai、Chen Liu、Yue Wang†、Jingren Zhou、Steven HOI（* Lead contributors，† 通讯 yue.w@alibaba-inc.com，"All authors are core contributors"）；机构署名 "Tongyi Lab, Alibaba Group"。

## F-027 资源链接矩阵与双语切换
- 位置: site/index.html（L105、156-205）
- 内容: 链接按钮：Paper（arXiv 2512.22047）、Code（github.com/Tongyi-MAI/MAI-UI）、HuggingFace（huggingface.co/collections/Tongyi-MAI/mai-ui）、ModelScope（modelscope.cn/organization/Tongyi-MAI）、MobileWorld（tongyi-mai.github.io/MobileWorld/）、Cite；导航栏提供 `<a href="index_zh_cn.html">中文版</a>` 实现英文↔中文切换，中文版 `site/index_zh_cn.html` 与英文版同构（title 相同，六个 section id 一致）。

## F-028 模型家族声明
- 位置: site/index.html（L214-216、259-261）
- 内容: promotion 文案原文："MAI-UI is a family of foundational GUI agent models from Tongyi-MAI Lab, ranging from 2B to 235B."；Technical Highlights 段原文："For the first time, MAI-UI natively integrates three core capabilities—user interaction, MCP tool calling, and device-cloud collaboration—into a unified architecture through autonomous evolution data pipelines and large-scale online reinforcement learning technology. (Currently, 2B and 8B models are open-sourced.)"；hero 区嵌 Bilibili iframe（BV15EvpBGEJy）。

## F-029 Technical Highlights 四卡
- 位置: site/index.html（L262-291）
- 内容: 四张高亮卡字面：MCP Tool Usage（"Model Context Protocol tools for enhanced functionality."）、User Interaction（"Advanced user interaction capabilities in real-world scenarios."）、Online Reinforcement Learning（"Large-scale online RL for continuous model improvement and adaptation."）、Device-Cloud Collaboration（"Efficient collaboration between device and cloud for balanced performance."）。

## F-030 站点章节结构
- 位置: site/index.html（Grep section id 全量）
- 内容: 七个 `<section id>`：overall_performance（"Overall Performance."，展示 asset/SOTA_Performance.png，figcaption 声明 "MAI-UI achieves SOTA performance across 5 GUI grounding benchmarks and navigation benchmarks (AndroidWorld, MobileWorld)"）、highlights、demo（"Real-World Demos"）、mobileworld（"Evaluating in Real-World MobileWorld"）、grounding（"GUI Grounding Performance"）、navigation（"GUI Navigation Performance"）、citation。asset 目录含 grounding_pipeline.png、navigation_pipeline.png、rl_framework.png、mcp.png、device_cloud.png、rollout.png 等图。

## F-031 Demo 视频清单
- 位置: site/index.html（L294-364）；site/asset/ 目录
- 内容: 四个场景视频：office_v2.mp4（Office Scenario）、life.mp4（Daily Life Scenario）、shopping.mp4（Shopping Scenario）、go_out.mp4（Travel Scenario）；Device-Cloud Collaboration 小节两视频：device_only.mp4（"Simple Tasks"）与 device_cloud.mp4（"Complex Tasks"）。

## F-032 MobileWorld 基准四特性
- 位置: site/index.html（L368-403）
- 内容: 特性卡字面：Broad Real-World Coverage（"201 carefully curated tasks across 20 mobile applications"）、Long-Horizon Tasks（"Multi-step reasoning and cross-app workflows"）、Agent-User Interaction（"Novel tasks requiring dynamic human-agent collaboration"）、MCP-Augmented Tasks（"Support Model Context Protocol (MCP) to evaluate hybrid tool usage"）；正文声明 MobileWorld 与 AndroidWorld 同级严谨可复现、新增四特性；配图 compare_to_aw.png 的 figcaption 声明 MobileWorld 任务更难（more steps、more cross-app workflows、lower SOTA accuracy）。

## F-033 AndroidWorld 成功率表（GUI Navigation）
- 位置: site/index.html（L938-1065）
- 内容: AndroidWorld 表（Model/Paras./Success Rate）关键行：Qwen3-VL-2B 36.4；UI-Tars-1.5-7B 30.0；UI-Venus-7B 49.1；GUI-Owl-7B 66.4；Step-GUI-8B 67.7；Qwen3-VL-8B 47.6；Qwen3-VL-32B 57.3；UI-Venus-72B 65.9；Qwen3-VL-235B-A22B 63.7；UI-Tars-1.5 64.2；Gemini-2.5-Pro 69.7；Seed1.8 70.7；UI-Tars-2（230B）73.3；Ours：MAI-UI-2B 49.1、MAI-UI-8B 70.7、MAI-UI-32B 73.3、MAI-UI-235B-A22B 76.7（加粗，全表最高）。部分基线行（ScaleCUA-3B、Ferret-UI Lite-3B、UI-Tars-7B、UI-Tars-SFT-72B、Seed1.5-VL）以 HTML 注释形式被注释掉未展示。

## F-034 MobileWorld 成功率表
- 位置: site/index.html（L1067-1189）
- 内容: MobileWorld 表列（GUI-Only (116) / User-Int. (45) / MCP (40) / Overall）分三组：Agentic Framework——GPT-5 + UI-Ins-7B overall 51.7、Gemini-3-Pro + UI-Ins-7B 46.3、Claude-4.5-Sonnet + UI-Ins-7B 43.8；End-to-End Model——Doubao-1.5-UI-TARS 20.9、UI-Venus-72B 10.4、Qwen3-VL-235B-A22B 9.5 等；Ours——MAI-UI-8B overall 24.9、MAI-UI-32B 37.3、MAI-UI-235B-A22B 41.7（GUI-Only 39.7 / User-Int. 51.1 / MCP 37.5 均加粗为列最高）。

## F-035 ScreenSpot-Pro 定位表（部分）
- 位置: site/index.html（L407-469 起）
- 内容: ScreenSpot-Pro 表（Model/Avg）已读部分：Gemini-3-Pro 72.7、Seed1.8 73.1、GTA1-7B 50.1、UI-Venus-7B 50.8、GUI-Owl-7B 54.9、GUI-Owl-32B 58.0、GTA1-32B 63.6、UI-Venus-72B 61.9；Ours：MAI-UI-2B 57.4、+ Zoom-In 62.8（子行）。

## F-036 Grounding-Blog 页面为 Notion 重定向 stub
- 位置: site/Grounding-Blog/index.html（全文 14 行）
- 内容: 文件不含博客正文，仅含三重重定向：`<meta http-equiv="refresh" content="0; URL=https://galvanized-jump-79a.notion.site/Why-your-AI-Agent-keeps-misclicking-A-Practical-Grounding-Guide-for-Frontier-Models-32630d140ad8808e895de98994dddb93">`、`<link rel="canonical">` 同 URL、`window.location.replace(...)`。Notion URL 字面即博客标题 "Why your AI Agent keeps misclicking: A Practical Grounding Guide for Frontier Models"。该 Notion 页面为 JS 渲染，本任务抓取失败，正文内容未采集（零推测，不补写）。

## F-037 MobileWorld-Blog-Post 页面同为 Notion 重定向 stub
- 位置: site/MobileWorld-Blog-Post/index.html（全文 14 行）
- 内容: 同为 meta refresh + canonical + JS replace 三重重定向，目标 `https://galvanized-jump-79a.notion.site/MobileWorld-Update-Can-Frontier-Models-Really-Control-Your-Phone-Evaluating-End-to-End-Mobile-Use--32630d140ad880faa6a8cd5f49661759?pvs=73`，URL 字面即标题 "MobileWorld Update: Can Frontier Models Really Control Your Phone? Evaluating End-to-End Mobile Use"。正文未采集（同 F-036）。

## F-038 site/leaderboard.json 结构
- 位置: site/leaderboard.json（全文 118 行）
- 内容: 顶层字段：`columns: ["Category", "Model", "Max Steps", "Overall", "GUI-Only", "User-Int.", "MCP"]`；`task_counts: { "GUI-Only": 116, "User-Int.": 45, "MCP": 40 }`；`results` 数组 13 条，每条含 category/model/max_steps/overall/gui_only/user_int/mcp，max_steps 均 50。Category 分 "Agentic"（3 条）与 "End-to-End"（10 条）。

## F-039 leaderboard.json 代表条目与与 HTML 表的差异
- 位置: site/leaderboard.json（L8-117）；site/index.html（L1080-1186）
- 内容: json 中最高分条目为 Agentic 组 "GPT-5 + UI-Ins-7B"（overall 51.7，user_int 62.2）；End-to-End 组最高为 "Doubao-1.5-UI-TARS"（overall 20.9）。客观差异：该 json 的 results 中不存在任何 MAI-UI 系列条目，而 index.html 的 MobileWorld 表含 MAI-UI-8B/32B/235B-A22B 三行（overall 24.9/37.3/41.7）且 HTML 表末组 "Ours" 高于 json 全部条目——两信源收录范围不一致（json 为无 MAI-UI 的对照数据，HTML 表含 Ours 组），数据快照版本可能不同，引用时须注明出处文件。

## F-040 MobileWorld 轨迹视频资产
- 位置: site/MobileWorld/trajs/ 目录
- 内容: 17 个 mp4 轨迹视频，文件名即模型标识：claude-opus-4.6/4.7、gemini-3.1-pro-preview、gpt-5.5、gpt-5.6-sol、kimi-k2.5/k2.6/k3、qwen3_vl_8b（两个时间戳）、qwen3.5-122b-a10b、qwen3.5-397b-a17b、qwen-ui-agent、memgui（两个）、magicgui、seed-2.0-pro。asset/ 目录另有 mcp.png、device_cloud.png/jpg、cloud_device.png/jpg、user_interaction.png、SOTA_Performance.png 等配图。

## 模块覆盖核对表

| 模块/信源 | 已读文件 | 对应事实 | 覆盖说明 |
| --- | --- | --- | --- |
| A-README | Qwen-UI-Agent/README.md（全文 101 行） | F-001~F-003、F-010、F-013、F-021~F-024 | 全文已读 |
| A-构建配置 | package.json、next.config.ts、drizzle.config.ts、build/sites-vite-plugin.ts、.github/workflows/deploy-pages.yml（均全文） | F-004~F-007、F-018、F-019 | 全文已读 |
| A-app 层 | app/layout.tsx、app/page.tsx、app/sitePath.ts、app/mobileworld-real/page.tsx（全文）；app/siteContent.ts（前 150 行 + 关键导出 Grep 全量 + L544-588、L983-1025） | F-008~F-016 | siteContent.ts 为 1700+ 行长文，结构由导出声明 Grep 全量定位，代表条目细读 |
| A-数据层 | db/schema.ts（全文）；tests/、scripts/ 文件存在性 | F-017、F-020 | schema 全文 4 行 |
| B-英文主站 | MAI-UI-blog/site/index.html（L105-280、280-469、929-1250 全部关键段 + section/h1/h3 Grep 全量） | F-025~F-035 | 1200+ 行长 HTML，章节结构 Grep 全量 + 关键表/文案细读 |
| B-中文主站 | site/index_zh_cn.html（section 结构 Grep） | F-027 | 与英文版同构（section id 一致），正文逐段未读 |
| B-两篇博客 | site/Grounding-Blog/index.html、site/MobileWorld-Blog-Post/index.html（均全文 14 行）；Notion 目标页 WebFetch 一次（失败） | F-036、F-037 | 本地仅 stub；Notion 为 JS 渲染页抓取失败，正文未采集 |
| B-leaderboard | site/leaderboard.json（全文 118 行） | F-038、F-039 | 全文已读 |
| B-媒体资产 | site/asset/、site/MobileWorld/trajs/ 目录清单 | F-040、F-030、F-031 | 仅文件名清单，未读二进制 |
| 未覆盖项 | public/ 下 pdf/svg 图片、drizzle/ 迁移目录、examples/d1/ 细节、app/components/*.tsx 正文、site/style.css | — | 按任务指示跳过 |
