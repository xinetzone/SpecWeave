# macro（macro.md）

## 核心判断
2026年5月国家网信办等三部门发布《智能体规范应用与创新发展实施意见》，是中国首部面向 AI 智能体的系统性政策文件，明确将"日常办公"列为低风险领域实行合规自测与行业自律，并把"终端应用"（电脑、手机等终端设备协同）列为重点场景[1]。叠加《网络数据安全管理条例》对境内收集产生的重要数据和个人信息的本地化与出境评估要求[3][4]，以及 OpenClaw 为代表的开源本地优先 Agent 框架在 2025 年底至 2026 年初的爆发式增长[5]，桌面级 Agent（如 LobsterAI）面临的政策环境总体方向是"鼓励创新、合规托底"：办公场景获低风险治理便利，数据本地化与供应链安全构成实质合规门槛，开源生态获政策明确支持。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [智能体规范应用与创新发展实施意见](https://www.cac.gov.cn/2026-05/08/c_1779979789523320.htm) — 中国网信网，2026年5月8日
3. [网络数据安全管理条例](https://xzfg.moj.gov.cn/front/law/detail?LawID=1734) — 司法部（国务院令第790号），2024年9月24日公布，2025年1月1日施行
4. [《促进和规范数据跨境流动规定》实施两周年 数据出境安全管理工作再上新台阶](https://www.cac.gov.cn/2026-03/23/c_1775999628849905.htm) — 中国网信网，2026年3月23日
5. [重构与崛起：OpenClaw时代的中国Agent产业生态报告](https://hulianhutongshequ.cn/upload/tank/report/2026/202605/1/052f47521f244da5b094c1ce334a933d.pdf) — 易观分析，2026年4月

# market（market.md）

## 核心判断
中国桌面级 AI Agent / AI 办公智能体市场处于规模化落地早期。据多家机构联合白皮书测算，2026 年国内 AI Agent 市场规模约 449 亿元，较 2025 年的约 212 亿元同比增长超 110%[1]。硬件侧，Canalys 数据显示 2025 年第一季度中国大陆 AI PC 占 PC 出货量比重已达 36%[2]；IDC 预测 GenAI PC 至 2029 年将占整体 PC 市场 36.5%[3]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [大厂All in AI办公：从"聊天框"到"替你干活"的入口战争](https://m.sohu.com/a/1065817249_121804985/) — 闪闻深读（搜狐），2026-08-21（转引多家机构联合白皮书、易观分析）
2. [联想不相信AI PC泡沫](https://m.36kr.com/p/3655983654679047) — 市象（36氪），2026-01-26（转引Canalys）
3. [IDC：2026年中国PC市场预计同比下降0.8% GenAI PC逆势爆发同比增长146.5%](https://finance.sina.com.cn/stock/hkstock/ggscyd/2025-11-27/doc-infyvnye0147883.shtml) — 智通财经网（新浪财经转载），2025-11-27（转引IDC）

# AI Agent 产业链与 LobsterAI 位置（chain.md）

## 核心判断
AI Agent 产业链在桌面场景下呈现"上游模型—中游框架/运行时—工具连接器—下游桌面应用"四层结构；LobsterAI 处于下游桌面应用层并向中游延伸，其关键价值在于把 OpenClaw 框架封装成可直接操作本地文件、终端与浏览器的桌面产品，但对上游大模型提供商与 OpenClaw 运行时存在硬依赖，模型成本与框架稳定性直接决定用户体验与商用化节奏 [1][2][3]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [netease-youdao/LobsterAI — GitHub](https://github.com/netease-youdao/LobsterAI) — 网易有道，仓库 README 原文，2026 年 9 月（最近提交 Sep 4, 2026）
2. [OpenClaw 2.0 Releases with Simplified Setup and Collaborative Agents — InfoQ](https://www.infoq.com/news/2026/09/openclaw-2-release/) — Daniel Dominguez / InfoQ，2026-09-01
3. [OpenClaw Documentation — Overview](https://docs.openclaw.ai/) — OpenClaw Foundation，日期不详

# competition（competition.md）

## 核心判断
桌面级 AI Agent 市场已形成"海外开源定义技术标准、国内大厂推动产品化落地"的基本格局，竞争沿开源/闭源、国内/海外、本地执行/云端执行三条主线展开；LobsterAI 凭借国内大厂首个 100% 开源桌面 Agent、GUI 产品化与本地优先架构，在国内办公 Agent"四强格局"中占据差异化位置，但面临社区生态成熟度不足与大厂战略绑定的双重约束。

## 关键证据
桌面级 AI Agent 的竞争发生在"可连接本地文件、终端、浏览器与项目的桌面端智能体"这一市场。据中国信通院数据，截至 2026 年 2 月，国内 AI 智能体相关服务商已突破 300 家[5]。从技术标准看，海外开源项目 OpenClaw 与 Hermes 率先定义了"桌面上的 AI 同事"范式——不依附协同办公平台，直接接管操作系统层面的任务调度，覆盖本地部署、云端调用与行业定制多个版本，被清华北航联合报告《2026 智能体工具大全》定位为个人与中小企业落地的首选载体[1]。
按执行位置可分为本地原生与云端沙箱两类。Lapu AI 对比七款桌面 Agent 后指出，真正在用户本机运行并操作真实文件的仅 Lapu AI、goose 与（部分）Manus；Bytebot 运行于自托管容器化 Linux 桌面，Manus 大部分任务在云端沙箱 VM 中执行，OpenAI Operator（已并入 ChatGPT agent）运行于 OpenAI 服务器，Anthropic computer use 仅为开发者 API 能力而非消费级应用[2]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [桌面办公Agent卡位战：谁先占领你的电脑？](https://view.inews.qq.com/a/20260812A05QMZ00) — 钛媒体（科技新知），2026-08-12
2. [Best Desktop AI Agents 2026: Computer Use AI Agents Compared](https://lapu.ai/blog/desktop-computer-use-agents-compared) — Lapu AI Team，2026-05-31（更新 2026-08-11）
5. [国产桌面Agent工具怎么选：从"接指令 → 拆解 → 动手 → 核对"这条链路看差异](https://www.cnblogs.com/vibe234/p/22431499) — 博客园（引自中国信通院），2026-08-12

# companies（companies.md）

## 核心判断
网易有道以 LobsterAI 切入桌面级 Agent 赛道，定位为"国内大厂首个开源桌面级 Agent"，采用「个人端开源免费 + 企业端私有化交付」的双轨商业化路径 [1][2]。截至 2026-09-09，LobsterAI 开源仓库累计 3,882 次提交、71 个发布版本、422 个 Issue，最新版本 2026.9.4，8—9 月保持几乎每周发版的高频迭代节奏 [3][4]。其技术底座明确基于 OpenClaw 框架生态：Cowork 为产品会话层，OpenClaw 为底层运行时与网关，仓库内专设 `openclaw-extensions` 目录并在 `package.json` 中锁定 OpenClaw 版本 [3]。有道正从教育科技公司向 AI 科技企业转型，CEO 周枫将 AI 产品划分为"聊天 AI—思考 AI—行动 AI"三代际，全力布局第三代"行动的 AI"；2025 年有道 AI 订阅销售额接近 4 亿元，验证了"能力 + 订阅"模式的付费意愿 [5]。

桌面级 Agent 竞争格局已形成"大厂闭源生态绑定 + 开源框架生态"双线并行结构。国内闭源阵营以豆包专业版（字节）、WorkBuddy（腾讯）、QoderWork（阿里）为代表，均绑定自有模型与办公生态、采用积分或订阅计费 [6]；海外闭源阵营以 Manus、ChatGPT Agent 为代表，走通用 Agent 路线。LobsterAI 的差异化在于 100% 代码开源、支持 10+ 主流模型与本地 Ollama 部署、深度适配 Windows 生态，并依托有道 OCR、翻译、子曰大模型等能力底座 [1][2]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [LobsterAI 有道龙虾官网](https://lobsterai.youdao.com/) — 网易有道，日期不详
2. [LobsterAI 企业版](https://ai.youdao.com/new/lobsterai) — 网易有道智云，日期不详
3. [netease-youdao/LobsterAI GitHub 仓库](https://github.com/netease-youdao/LobsterAI/) — NetEase Youdao，2026-09-04（最新提交）
4. [LobsterAI Releases](https://github.com/netease-youdao/LobsterAI/releases) — NetEase Youdao，2026-09-04（最新版本）
5. [「OpenClaw之父点赞」终结百虾大战？一场升级版的AI原生革命上演](https://post.m.smzdm.com/p/a035rqdr/) — 新智元（引自知乎），2026-04-07
6. [豆包、WorkBuddy、QoderWork怎么选？我用8个真实办公任务把三家桌面Agent测明白了](https://m.huxiu.com/article/4875072.html?type=text) — 夕小瑶科技说（虎嗅转载），2026-07-14
