# Facts: MobilePA-Bench（基准项目页仓库）
> 信源根：external/libs/tools/Tongyi-MAI/MobilePA-Bench

## F-001 仓库为基准的项目页/Paper 资产，非实现代码仓
- 位置: README.md（L39）；仓库根目录文件清单
- 内容: README「News」原文记载："2026-08-25: The project repository was opened with an interactive project page, leaderboard, and a private-evaluation link"。仓库根目录经 Glob 全量核查仅含 `README.md`、`LICENSE`、`.gitignore`、`github-pages/`（纯静态站点）与 `.github/`（CI 脚本与 workflow），不存在任何基准任务数据、评测 harness、模型或智能体实现代码目录；基准本体以 arXiv 论文（arXiv:2608.23035）形式发布。

## F-002 基准一句话定义
- 位置: README.md（L21）
- 内容: 原文定义："MobilePA-Bench is an interactive, stateful, and tool-centric benchmark for evaluating the tool-calling and planning capabilities of mobile planner agents. It moves beyond static function matching by executing agent actions in a mutable mobile environment and checking both the action trace and the resulting state."

## F-003 Highlights 五条要点
- 位置: README.md（L29-35）
- 内容: 逐条字面要点：①Executable and stateful（应用数据、权限与设备状态随每次动作演化）；②Broad mobile coverage（1,705 任务、212 工具、13 域、89 子类）；③Four capability dimensions（Tool Use、Memory Usage、Skill Usage、Sub-agent Collaboration）；④Evidence-based evaluation（固定策略验证工具选择、落地参数、执行顺序、最终环境状态与智能体行为）；⑤Realistic failure modes（工具依赖、权限边界、冲突请求、运行时错误、不完整用户上下文）。

## F-004 规模数字（README 与页面一致）
- 位置: README.md（L32）；github-pages/index.html（L237-238）
- 内容: 1,705 个评估任务、212 个 realistic tools、13 个 functional domains、89 个子类别（level-2 subcategories）。README 与站点 Benchmark Statistics 副标题数字一致。

## F-005 四能力维度定义表
- 位置: README.md（L52-59）
- 内容: 表格四行字面定义——Tool Use: "Grounded tool selection, argument construction, ordered execution, recovery, and safe refusal"；Memory: "Retrieval and application of user profiles, preferences, routines, history, and situational context"；Skills: "Selection and execution of reusable composite procedures instead of rebuilding every workflow from scratch"；Sub-agent: "Task decomposition, contextual handoff, and coordination with GUI, search, image, and other specialized agents"。每行附站点锚点链接（#tool-use-examples / #memory-examples / #skill-examples / #sub-agent-examples）。

## F-006 News 时间线
- 位置: README.md（L37-40）
- 内容: 2026-08-24 论文上 arXiv（arxiv.org/abs/2608.23035）；2026-08-25 项目仓库开放（项目页 + leaderboard + private-evaluation 链接）。

## F-007 Overview 建模与评测方式描述
- 位置: README.md（L42-46）
- 内容: 原文：移动规划智能体被建模为通过 structured tools、reusable skills、persistent memory 和 specialized sub-agents 进行操作的决策器；环境执行每个动作、更新状态并返回观察或运行时错误。评测器为每个任务分配固定验证策略（fixed verification policy），成功可要求"an exact tool call, a target state transition, a prescribed action order, or a valid collaboration pattern"。

## F-008 Private Evaluation 提交要求
- 位置: README.md（L62-64）
- 内容: 面向 hosted mobile planner agents 的保密评测通道：提交 HTTPS、OpenAI-compatible、支持 tool-calling 的 endpoint，将在 Tool Use、Memory Usage、Skill Usage、Sub-agent Collaboration 四维评测。入口为 secure submission portal（116.62.42.171/login?next=/submit）。

## F-009 Private Evaluation 四条特性
- 位置: README.md（L66-69）
- 内容: 字面四条——①Confidential by design（提交直达专用评测服务器，API 凭据不经 GitHub Pages）；②Hidden-test integrity（基准查询、ground truth、judge 凭据与被测模型隔离）；③Reviewed results（每次运行在发布前经人工检查）；④Expected turnaround（通常 3 个工作日内返回报告，每账户每 7 天允许 1 次请求）。

## F-010 评测服务 URL 由 site_config.js 统一注入
- 位置: github-pages/static/js/site_config.js（L4-10）
- 内容: `evaluationServiceUrl = "https://116.62.42.171"`，挂载到 `window.MobilePABenchConfig`；脚本遍历所有带 `data-evaluation-path` 属性的链接，把 href 改写为服务地址 + path。index.html 中 Evaluation login 按钮即带 `data-evaluation-path="/login"`（L29-30）、私有评测按钮带 `/login?next=/submit`（L71-72）。

## F-011 leaderboard 数据文件头部注释声明版本与权重公式
- 位置: github-pages/static/js/leaderboard_data.js（L1-3）
- 内容: 原文注释："// MobilePA-Bench v1.5 leaderboard data (from paper_v5 Table 1, tab:main_results)"、 "// Overall = 0.5*Tool + 0.2*Memory + 0.2*Skills + 0.1*SubAgent"、 "// info: org used only for optional grouping/badges"。

## F-012 leaderboard 收录 13 个模型及分数
- 位置: github-pages/static/js/leaderboard_data.js（L4-18）
- 内容: `LEADERBOARD_DATA` 数组 13 条，每条字段 model/org/overall/basic/subagent/memory/skills/costPer1k。前三名：Claude-Opus-5（Anthropic，overall 75.52，basic 83.85）、Claude-Fable-5（Anthropic，75.31）、Kimi-K3（Moonshot，73.01）；其后为 Qwen-3.8-Max（Alibaba，72.51）、Gemini-3.6-Flash（Google，71.21）、Gemini-3.1-Pro（71.18）、GLM-5.2（Zhipu，67.71）、Claude-Opus-4.8（65.52）、Qwen-3.7-Max（64.71）、Seed-2.1-Pro（ByteDance，63.65）、GPT-5.6-Sol（OpenAI，62.68）、GPT-5.5（61.44）、Kimi-2.6（55.63）。列名 basic 对应 Tool Use 维度。

## F-013 页面 Overall 权重表述
- 位置: github-pages/index.html（L107-109）
- 内容: Leaderboard 章节副标题原文："Overall = 50% Tool Use + 20% Memory + 20% Skills + 10% Sub-agent."；"Best value per column is highlighted"。

## F-014 Cost/1K 口径说明
- 位置: github-pages/index.html（L112-115）
- 内容: 原文："All capability values are percentages (%). Overall is reported only for models with complete coverage of all four dimensions."；"Cost/1K Tasks is estimated from visible output tokens only; input, cached, and hidden reasoning tokens are excluded."

## F-015 页面章节结构（6 个锚点 section + 1 个评测入口横幅）
- 位置: github-pages/index.html（L18-33、57、84、104、120、199、231、289）
- 内容: 粘性导航链接依次为 #intro（Introduction）、#leaderboard（Leaderboard）、#demo（Demo）、#cases（Task Examples）、#benchmark（Benchmark）、#citation（Citation）与外部 Evaluation login；另有不带锚点的 evaluation-entry section（"Confidential evaluation for hosted models"）。hero 区作者署名 "MAI Team, Alibaba Token Hub, Alibaba Group"（L44）。

## F-016 Task Examples 四个维度锚点
- 位置: github-pages/index.html（L206-223）
- 内容: 四个 case tab 按钮分别携带 `data-anchor` 属性：basic→tool-use-examples、memory→memory-examples、skills→skill-examples、subagent→sub-agent-examples，各标 "3" 个案例计数。

## F-017 Benchmark Statistics 六项统计
- 位置: github-pages/index.html（L236-246）
- 内容: 六个 pill：1,705 Evaluation Tasks；212 Realistic Tools；13 Functional Domains；89 Subcategories；N=15 Candidate Recall；T=15 Max Steps。

## F-018 四维度任务分布
- 位置: github-pages/index.html（L248-256）
- 内容: Tasks per capability dimension：Tool Use 1,040；Memory Usage 376；Skill Usage 200；Sub-agent Collaboration 89（四项合计 1,705）。

## F-019 13 个工具域及工具数
- 位置: github-pages/index.html（L265-282）
- 内容: 域-工具数表：Audio & Entertainment 25；Apps & Storage 23；Display & Sound 22；System Settings 22；Time Management 16；AI Assistant 16；Calls & Communication 15；Network & Connectivity 14；Travel & Lifestyle 13；Devices & Cross-device 13；Input & Interaction 12；Utilities & Productivity 11；Security & Privacy 10。

## F-020 案例数据按四维度组织，每维 3 案例
- 位置: github-pages/static/js/case_studies_data.js（L1-2 及全文）
- 内容: 文件头注释 "// Representative task traces across the four MobilePA-Bench capability dimensions."；`window.TASK_EXAMPLES_DATA.dimensions` 含 basic（title "Tool Use"）、memory（"Memory Usage"）、skills（"Skill Usage"）、subagent（"Sub-agent Collaboration"）四键，每键 cases 数组 3 条，每条含 id/title/query/checker/subtype/interactions/finalResponse 字段。

## F-021 验证策略 checker 类型字面量
- 位置: github-pages/static/js/case_studies_data.js（全文 Grep "checker"）
- 内容: 出现的 checker 字面量：Strict tool + arguments；Behavior judge；Final DB state；DB state + retrieval；Behavior judge + retrieval；Skill routing + execution。Tool Use 维度 3 案例分别对应三种 checker；Memory 维度案例用 DB state + retrieval / Behavior judge + retrieval；Skills 维度 3 案例均为 Skill routing + execution；Sub-agent 维度 3 案例均为 Behavior judge。

## F-022 案例 subtype 与代表案例
- 位置: github-pages/static/js/case_studies_data.js（L9-51、26-35、55-100）
- 内容: Tool Use 案例含 BTU-204（"Payment sequence under real state changes"，subtype Ordered execution，interactions 依次调用 control_flashlight/open_app/manage_nfc）、BTU-622（"Conflicting network goals"，subtype Conflict intent，模型判定关流量与 4K 流播冲突后反问用户）、BTU-863（subtype Compound state change，dark mode + repeat one + 30 分钟倒计时三连调用）。Memory 案例含 MEM-0043（subtype Memory update，把睡前单词 App 从 Anki 改为 Quizlet）、MEM-0054（Multi-memory composition）、MEM-MT0421（Multi-turn memory，Bluetooth 发送会议纪要到 MacBook Pro）。

## F-023 交互式 replay 演示的场景与 policy 字面量
- 位置: github-pages/static/js/replay_demo_data.js（L4-69）；github-pages/index.html（L120-196）
- 内容: `window.MobilePAReplayScenarios` 场景含 id "tool"（tab "Exact Tool Call"，policy "tool_acc"，policyLabel "Exact tool + arguments"，示例为 manage_alarm 创建 7:30 Morning run 闹钟，checks 列 Tool name/Argument fields/Grounded values）与 id "state"（tab "Stateful Completion"，policy "task_db_acc"，policyLabel "Final environment state"，示例为杭州周六行程计划，capabilities 标注 basic/memory/skills 三维）。Demo 区三栏分别为 Interaction（User & Agent）、Execution trace（Planner & Environment）、Fixed policy（Evidence Checker），底部注明 "Illustrative public examples; hidden evaluation tasks and ground truth remain private."（L194）。

## F-024 静态站依赖全部本地化，不依赖外部 CDN
- 位置: github-pages/index.html（L9-14）；github-pages/static/vendor/ 目录
- 内容: HTML 注释原文 "Local UI dependencies keep the static site independent of external CDNs."；vendor 目录含 bulma.min.css、fontawesome（css/all.min.css + webfonts）、tabulator.min.js/css、jquery.min.js；页面样式版本号带查询串（style.css?v=compact-intro-20260819、replay-demo.css?v=20260817-icons）。github-pages/ 根有 `.nojekyll` 文件。

## F-025 leaderboard 截图由 Playwright 脚本自动生成
- 位置: .github/scripts/capture-leaderboard.mjs（全文）
- 内容: 脚本用 `playwright` 的 `chromium.launch({ headless: true })` 打开 `http://127.0.0.1:4180/#leaderboard`（viewport 1440x1000，deviceScaleFactor 1），等待 `#leaderboard > .inner` 可见，隐藏 nav 元素后对该区块截图保存为 `github-pages/static/images/leaderboard.jpg`（jpeg quality 92，animations disabled）。该截图即 README 顶部展示图。

## F-026 GitHub Pages 部署 workflow
- 位置: .github/workflows/deploy-pages.yml（全文）
- 内容: workflow 名 "Deploy public benchmark site"，push 到 main 且 paths 命中 `github-pages/**` 或 workflow 本身时触发，另有 workflow_dispatch；permissions 为 contents: read / pages: write / id-token: write；concurrency group "pages"（cancel-in-progress）；部署步骤为 checkout@v4 → configure-pages@v5 → upload-pages-artifact@v3（path: github-pages）→ deploy-pages@v4。无构建步骤，直接上传静态目录。

## F-027 存在第二个 leaderboard 预览更新 workflow
- 位置: .github/workflows/update-leaderboard-preview.yml
- 内容: `.github/workflows/` 下除 deploy-pages.yml 外还存在 `update-leaderboard-preview.yml` 文件（本次未展开细读其内容）。

## F-028 README 引用的论文 BibTeX
- 位置: README.md（L71-85）
- 内容: citation key `zhu2026mobilepabench`，标题 "MobilePA-Bench: Benchmarking Mobile Planner Agents on Complex Real-World Tasks"，作者 Zhu, Yi; Wu, Xiongwei; Wang, Qiyi; Qu, Tingyu; Liu, Jiajun; Cao, Sihan; Chen, Long; Sun, Weigao; Zhu, Feida; Zhong, Yiran; Hoi, Steven，journal 为 arXiv preprint arXiv:2608.23035，year 2026，primaryClass cs.AI。

## F-029 页面内 Citation 与 footer
- 位置: github-pages/index.html（L288-303）
- 内容: #citation 章节提供简化版 BibTeX（key `mobilepabench2026`，author "MAI Team, Alibaba Token Hub, Alibaba Group"）。footer 原文 "© 2026 MobilePA-Bench · MAI Team, Alibaba Token Hub, Alibaba Group. Page template inspired by Video-MME"（附 video-mme.github.io 链接）。

## F-030 许可证
- 位置: README.md（L91-93）；LICENSE
- 内容: "Unless otherwise noted, this repository is licensed under the Apache License 2.0"；根目录存在 LICENSE 文件，README 徽章亦标注 License Apache 2.0。

## F-031 Introduction 章节的定位论述
- 位置: github-pages/index.html（L84-101）
- 内容: 原文论述现有评测的缺口："static function-calling benchmarks rarely execute predicted calls against a persistent environment, while GUI-centric benchmarks underrepresent efficient structured APIs, personalized context, reusable procedures, and coordination with specialized agents"；MobilePA-Bench 以 interactive、stateful、tool-centric sandbox 补足，并重申 1,705 tasks / 212 tools / 13 domains 规模与四能力。

## F-032 Sub-agent 维度案例主题
- 位置: github-pages/static/js/case_studies_data.js（L155-193 附近）
- 内容: Sub-agent Collaboration 维度 summary 原文 "Delegation to specialized agents, recovery from tool boundaries, and transparent fallbacks."；三个案例标题分别为 "Recover into a GUI handoff"、"Keep an automation when media is unavailable"、"Delegate open-domain lookup without fabrication"（checker 均为 Behavior judge）。Skill Usage 维度 summary 为 "Loading reusable skills before executing a safe and complete business-tool plan."，三案例 checker 均为 Skill routing + execution。

## 模块覆盖核对表

| 模块/信源 | 已读文件 | 对应事实 | 覆盖说明 |
| --- | --- | --- | --- |
| README 主文档 | README.md（全文 99 行） | F-001~F-009、F-028、F-030 | 全文已读 |
| leaderboard 数据 | github-pages/static/js/leaderboard_data.js（全文 18 行） | F-011、F-012 | 全文已读 |
| 站点配置 | github-pages/static/js/site_config.js（全文 11 行） | F-010 | 全文已读 |
| 案例数据 | github-pages/static/js/case_studies_data.js（前 100 行全文 + Grep title/checker/summary 全量行） | F-020~F-022、F-032 | 结构 + 代表条目 + checker/subtype/title 字面量全量提取 |
| replay 数据 | github-pages/static/js/replay_demo_data.js（前 100 行） | F-023 | 结构 + 前 2 个场景 |
| 页面结构 | github-pages/index.html（L1-308 全文） | F-004、F-013~F-019、F-024、F-029、F-031 | 全文已读（308 行） |
| 部署机制 | .github/scripts/capture-leaderboard.mjs（全文）、.github/workflows/deploy-pages.yml（全文） | F-025、F-026、F-027 | 全文已读 |
| 未覆盖项 | 图片/视频二进制、vendor 压缩库、LICENSE 正文、update-leaderboard-preview.yml 细节 | — | 按任务指示跳过或仅登记存在性 |
