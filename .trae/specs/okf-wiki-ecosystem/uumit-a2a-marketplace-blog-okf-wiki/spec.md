---
id: "uumit-a2a-marketplace-blog-okf-wiki"
version: "0.1.0"
scenario: knowledge
topic: UUMit A2A 能力交易平台一手体验
url: https://mp.weixin.qq.com/s/uhp0Fn0YaFVmbC0eYzi-oA
author: 阿超（公众号「阿超数字抽屉」）
published: 2026-08-20
status: pending
---

# 规格：UUMit A2A 能力交易平台博文 → OKF 知识包

## 内容敏感度预检

- URL：`mp.weixin.qq.com` 公开文章，无 `share?code=`/`token=`/邀请码等访问控制参数 → **公开内容（Public）**
- 工作流：标准博文转化工作流（spec 位于 `.trae/specs/okf-wiki-ecosystem/`，bundle 产出位于 `projects/awesome-okf-xs/doc/bundles/`）
- 信源获取：微信反爬，按 Skill 纪律直接使用 browser_use 提取 `#js_content`（实测 2426 字，节点正确）

## 信源距离预判

- 博文性质：**作者一手实测**（第三方体验者，非厂商主体；作者内测期试用、公测期撰文）
- 风险特征：博文本身**零外链、零信源**；核心论点（"Skill 易复制、背后按次调用资产才值钱"）与官方掘金号叙事高度同构；平台规模/成效类数字只可能来自厂商自宣 → 全部按 P0/⚠️ 处理，index 顶部加"厂商自述数据"提示
- 核验手段：官网 uumit.com 实测（WebFetch）+ 官方掘金号 + 两个独立第三方（腾讯云社区、CSDN 实测复盘）

## 骨架判定（操作可复现性两问）

| 问题 | 答案 |
|------|------|
| ① 是否有读者可照做的安装/配置/代码/调用/实测流程？ | 弱"是"：注册问卷、天赋解析、在 Agent 中发指令上架写作 Skill |
| ② 是否经作者实测且具备可复现性（版本、输入输出、步骤顺序）？ | **否**：无版本、无具体输入输出（Skill 内容/定价/交付物均未呈现）、平台公测期快速迭代、纯 UI 点击叙述（任务数 730→731 瞬时即变） |
| 判定 | 任一为"否" → **不设 examples/**，技术产品实测/资讯骨架（index + concepts/ + references/ + log），description 标注"非操作教程" |

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/uumit-a2a-marketplace/`（选定，直挂束） | ✅ | ① 主线实体 UUMit 是 AI Agent 能力交易平台，属 ai 域；② 同分组已有微信/知乎博文转化直挂束先例（mattpocock-skills、free-llm-api-roundup、token-economy-explosion）；③ mattpocock-skills 同为 Agent Skills 生态主题，可互链 |
| `jishu/ai/agent-platform-notes/` | ❌ | 散篇聚合束，承载"独立成束不足的小主题"；本篇有完整一手实测+三层知识，足以独立成束 |
| `jishu/ai/agent-industry-research/` | ❌ | 行业研究文章集合束，本篇是单平台产品实测而非多源行业研究 |
| `sheke/industry/` | ❌ | 商业趋势快照分组；本篇核心是 AI 平台机制一手实测，技术域先例更近 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

## 知识拆分规划（三层）

| 层次 | 文件 | 核心内容 |
|------|------|---------|
| 事件/产品事实层（What/When） | concepts/00-platform-and-timeline.md | UUMit 是什么、内测→开放时间线、官网模块地图、UT 货币体系、UUMit Skill 接入方式 |
| 机制/驱动层（How/Why） | concepts/01-marketplace-mechanism.md | 平台三件事、双边市场与 A2A 交易层（MCP 调用层 vs A2A 交易层·厂商观点）、"Skill 背后资产论"（作者观点与官方 per-call 叙事对照） |
| 格局/生态层（趋势/风险） | concepts/02-agent-economy-landscape.md | A2A 经济叙事与营销数字甄别、第三方冷现实（5 天负 ROI 实测、四点质疑）、疑似仿冒站 uumit.org 风险、普通人/开发者启示 |

## 质量门

- G1：facts.md 事实无因果词、观点显式标注（📝 观点 / 厂商自述 / 第三方实测）
- G2：概念文档现象+机制+影响+建议分层完整
- G3：信源先行（references 先于 concepts，index 最后写），所有具体声明带 F 编号
- G4：双份 F 编号集合一致、三级 toctree 完整、计数同步（ai 187→188、jishu 406→407、total 539→540）

## 参考先例

- [mattpocock-skills/](../../projects/awesome-okf-xs/doc/bundles/jishu/ai/mattpocock-skills/index.md)（微信博文→bundle，零❌/4⚠️，无 examples 骨架）
- L2 模式：[blog-article-to-okf-bundle.md](../../docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md)
