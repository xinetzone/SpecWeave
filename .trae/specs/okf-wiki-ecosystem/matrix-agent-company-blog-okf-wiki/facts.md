# 事实登记簿（facts.md）— Matrix "0人公司" 博文转化

> 信源：《这个AI工具真的疯了！它可以帮你开一家"0人公司"，只需要一个想法，Agent就能自己去赚钱》
> 公众号：智潮笔记 | 发布：2026-07-04 08:00 | URL: https://mp.weixin.qq.com/s/C5clrnoai50eneYvgP1nLw
> 登记规则：F-001 起编号；作者观点显式标注"作者观点"；核验补充事实续编号并注明来源。
> 信源距离预判：**第三方自媒体转述 + 厂商自宣浓度高**（博文核心成效数字均来自 Matrix 官网宣称）。厂商自宣类所有成效数字默认 P0 必核验。

## 一、博文元信息

| 编号 | 事实 | 级别 |
|------|------|------|
| F-001 | 博文标题《这个AI工具真的疯了！它可以帮你开一家"0人公司"，只需要一个想法，Agent就能自己去赚钱》 | P2 |
| F-002 | 公众号"智潮笔记"，发布于 2026-07-04 08:00，作者署名"智潮笔记" | P2 |
| F-003 | 博文性质：第三方自媒体产品介绍/评论文章，非 Matrix 官方发布 | P2 |

## 二、产品定位与接入（博文叙述）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-004 | Matrix 官网 slogan 为"让你的第一家Agent公司活起来"（博文转述） | P1 |
| F-005 | 博文认为 Matrix 定位不是又一个 Coding Agent，与 Claude Code、Codex、Cursor 不是竞争关系，反而可接入当"员工"用 | 作者观点 |
| F-006 | Matrix 内置 Neo Agent，原生接入 Claude Code、Codex、ChatGPT、Gemini，以及国产的 GLM、DeepSeek、Kimi、Qwen | P0 |
| F-007 | 还可用 OpenRouter key 或自己的 Claude Max/Pro 账号登录后接入 | P1 |
| F-008 | 博文认为 Matrix 的野心是做"一家公司的操作系统" | 作者观点 |
| F-018 | 博文称 Matrix 主要是一个 macOS 桌面应用，Web 端还没上线 | P1 |
| F-019 | 博文文末称可去 matrix.build 看看，目前 Web 版还没上，只有 macOS 版本 | P1 |

## 三、Agent 公司架构与机制（博文叙述）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-009 | 博文示例：给 Matrix 一个目标（如"做一个短剧频道并且赚到钱"），内部会像一家真正的公司那样开始运转 | P1 |
| F-010 | 有一个 CEO Office 级别的 Agent 统筹全局，下面分出调研、工程、创意、增长、安全、运营这些部门 | P0 |
| F-011 | 每个部门有自己的领队 Agent，领队再判断是自己干，还是派给协作 Agent 干 | P0 |
| F-012 | 每个 Agent 都有自己的浏览器、工具、文件和记忆 | P0 |
| F-013 | Agent 会自己拆任务、自己推进、自己处理卡点，最后给出一个可以验证的结果 | P0 |
| F-014 | 记忆靠 durable work memory：每个目标、决策、交接、卡点和结果都留存在公司里 | P0 |
| F-015 | 协作靠统一的文件系统和跨 Agent 通信 | P0 |
| F-016 | 反馈靠 proof 机制：每个 Agent 必须交付可验证的结果，比如文件、截图、上线的页面、收入或者流量 | P0 |
| F-017 | 博文总结：分工（部门化和领队路由）、记忆（durable work memory）、协作（统一文件系统）、反馈（proof 机制）四件事被工程化 | 作者总结 |

## 四、案例与成效数字（博文叙述，厂商自宣浓度高）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-020 | 官网案例 AI 视频工作室 aivideopro.io：从定位、报价页面、作品展示、创作者流程，到 Stripe 收款、付费套餐、客户 brief intake，整条链路都接通 | P0 |
| F-021 | 生产端交付了 100 多条定制视频 | P0 |
| F-022 | 分发端有自动化 YouTube 频道，最高的短视频跑到 700k+ 播放 | P0 |
| F-023 | 有用户分享用 Matrix 跑通了能收到客户钱的广告服务流程；作者明确表示"没法验证具体细节，但这种模式本身是合理的" | P0（含作者免责声明） |
| F-024 | Agent Revenue 模块把 Stripe 收款、付费套餐、客户 intake 这些链路都接通，从技术上可以完成"收到钱"这个动作 | P0 |
| F-025 | GDPval-Bench 它跑出了 95.45%，超过 Codex CLI 的 84.9% 和 Claude Opus 4.7 的 80.3% | P0 |
| F-026 | 博文解读：这说明 Matrix 的 harness 工程很强，同样的模型放进它的系统里能发挥出更强的干活水平 | 作者解读 |

## 五、作者观点与叙事（显式分层）

| 编号 | 内容 | 级别 |
|------|------|------|
| F-027 | 博文开篇独立开发者故事：朋友用 Claude Code 一个周末做了小工具，GitHub star 不到 20，无人使用——"用 AI 做东西这件事，技术上已经没难度了。但把做出来的东西卖出去，这就太难了"（作者转述朋友吐槽） | P2（背景叙事） |
| F-028 | 博文论点：问题不是 AI 不够强，是 AI 只会帮你"造"，不会帮你"卖" | 作者观点 |
| F-029 | 博文认为 Matrix 把分工、记忆、协作和反馈四件事都工程化了，一家公司可以在没有人类员工的情况下运转 | 作者观点 |
| F-030 | 博文"泼冷水"：现在的 Matrix 远没到"躺着赚钱"的程度；能跑出什么结果很大程度上取决于目标是否清晰、懂不懂这门生意 | 作者观点 |
| F-031 | 博文认为这些赚到钱的人本身不是小白，懂社区、懂获客、懂客户心理；Matrix 帮他们干"费时间但不需要顶级创意"的脏活累活（持续生产内容、自动发布、跟进邮件、跑数据） | 作者观点 |
| F-032 | 博文认为真正的判断、审美还在人手里 | 作者观点 |
| F-033 | 博文"AI 三阶段论"：第一阶段 AI 能回答问题；第二阶段 AI 能帮你写代码、做东西；第三阶段 AI 能帮你把东西卖出去，跑通一门生意 | 作者观点 |
| F-034 | 博文论点：当 AI 把"造"的成本打到接近零，真正的竞争会转移到"运营"和"商业判断"上 | 作者观点 |
| F-035 | 博文认为 Matrix 让一个人拥有 7×24 不知疲倦的执行团队，但公司能否赚钱取决于坐在 CEO 位置上的人 | 作者观点 |
| F-036 | 博文认为可能的方向不是 AI 替代某个岗位，而是 AI 替代一整个公司的结构 | 作者观点 |
| F-037 | 博文对照：过去开公司需要租办公室、招人、发工资、跑注册、开银行账号；现在只需要一个想法和一台能跑 Matrix 的 Mac | 作者表述 |
| F-038 | 博文结论："0人公司"能否成为主流不知道，但确定 AI 不会只停留在帮造东西，迟早进入帮做生意、赚钱的阶段 | 作者观点 |

## 六、核验补充事实（R 阶段 WebSearch，2026-09-01）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-039 | Matrix 产品真实存在：多个第三方 AI 工具导航站收录——aigjdh.com（描述"专为超长周期自主运行而生的主动式多智能体协作平台"）、hotools.com（2026-06-23 收录，"agentic runtime for long-term autonomous operation / 0-person company"）、aitoolnet.com（"multi-layer agentic runtime"），定位描述与博文一致 | https://aigjdh.com/sites/2669.html；https://hotools.com/item/matrix；https://www.aitoolnet.com/matrix |
| F-040 | 第三方转录的官方架构描述与博文一致：CEO Office → OKR 记忆系统 → 并行部门（Research/Product/Growth/Engineering，另有 SEO 实验室等场景部门）→ Lead Agent（durable memory）→ Worker Agent（disposable）；Agential OKR 分层循环；共享文件系统跨部门交接；proof 机制（work 未验证不算完成，verifiable artifacts：文件/测试/截图/转录） | https://www.aitoolnet.com/matrix；https://aigjdh.com/sites/2669.html |
| F-041 | 模型接入列表与博文一致：Neo（自研）、Claude Code、Codex、ChatGPT、Gemini、GLM、DeepSeek、Kimi、Qwen——aitoolnet 与 hotools 两方转录一致；aigjdh 另提及"原生集成 Claude Code、Codex 以及自研的 Neo Intelligence Harness" | https://www.aitoolnet.com/matrix；https://hotools.com/item/matrix |
| F-042 | 商业基建与 Revenue 能力与博文一致：预置域名部署（matrix.site 子域名）、Stripe 支付、Agent 钱包、邮件收发（Gmail 等）、广告账户、GitHub/Vercel/Docker 集成，绕过实体注册与银行开户；另发现博文未提的官方经济指标 VPTD（Value per Token-Dollar，衡量每 token 成本产出的业务价值） | https://www.aitoolnet.com/matrix；https://hotools.com/item/matrix；https://aigjdh.com/sites/2669.html |
| F-043 | GDPval-Bench 95.45% 仅见于厂商自述（aitoolnet 转录官方文案 "The system achieves 95.45% on GDPval-Bench"），未找到独立第三方评测可溯源；对照数字中 Codex CLI 84.9% 与第三方评测（danilchenko.dev 2026-06-12）中 GPT-5.5 的 GDPval 84.9% 数值吻合，但 Matrix 官网口径与对照表无法确认；Claude Opus 4.7 GDPval 80.3% 无法独立溯源（Anthropic 官方口径 GDPval-AA 为 Elo 制，如 Opus 4.6=1606，与百分比口径不同） | https://www.aitoolnet.com/matrix；https://www.danilchenko.dev/posts/gpt-5-5-review/ |
| F-044 | aivideopro.io 案例数字（100+ 定制视频、700k+ 播放，aitoolnet 转录另含 $3,000+ 收入）仅厂商自述；aigjdh 转述"已累计产生超过 70 万次真实播放"与 700k+ 一致；无独立第三方验证 | https://www.aitoolnet.com/matrix；https://aigjdh.com/sites/2669.html |
| F-045 | 同名产品排除：OpenAI 官网收录的 Hebbia "Matrix" 为金融/法律多智能体研究平台（o3-mini/o1/GPT-4o），与本产品无关；GitHub matrix-agent-neo/matrix-core（fork 仓库）与 NeoLabs-Systems/NeoAgent（自托管开源 Agent）均非本产品；撰写时须防同名混淆 | https://openai.com/index/hebbia/ |
| F-046 | macOS 桌面应用、Web 端未上线：三家第三方工具站均未提及平台形态，该声明仅博文单源，引用时需提示读者甄别 | 仅博文 |

## 七、勘误四张清单过筛记录

| 清单 | 过筛结论 |
|------|---------|
| ① 日期/版本表 | 博文发布 2026-07-04，产品收录记录（hotools 2026-06-23）时间线自洽；未发现版本/日期硬错误 |
| ② 成效数字溯源表 | 95.45%（F-043）、100+视频/700k+播放（F-044）均无独立出处 → 全部标"厂商/客户自述"，index 顶部加提示块；无 ❌ 硬性证伪 |
| ③ 口径对照表 | GDPval 口径风险：Anthropic 官方用 GDPval-AA Elo 制，百分比口径见于第三方评测——95.45% 与 80.3%/84.9% 的对照表无法验证，须在正文标注口径不确定性 |
| ④ 引文逐字核对表 | 官网 slogan"让你的第一家Agent公司活起来"为博文转述，第三方转录为"launch a 0-person company"——语义一致但非逐字确认，正文标注转述层级 |

## 八、核验结论汇总

- **P0 核验 6 项：2 ✅（产品存在与架构/模型列表/商业基建）、3 ⚠️（GDPval 数字、案例数字、slogan 逐字）、1 单源（macOS/Web 形态）**
- 无 ❌ 硬性错误，博文核心叙事（"AI 从造到卖的转移 + Agent 公司操作系统方向"）未被证伪 → bundle `status: stable`
- 成效数字全部标注"厂商/客户自述"，index.md 顶部加"厂商自述数据"提示块
