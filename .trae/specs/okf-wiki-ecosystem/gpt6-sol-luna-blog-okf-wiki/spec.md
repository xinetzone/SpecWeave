---
type: spec
title: "GPT-6 Sol 与 GPT-6 Luna：低成本 Agent 模型选型"
source: "https://mp.weixin.qq.com/s/1190GW6WFZIzZ8YkDD44eg?from=industrynews&color_scheme=light#rd"
status: completed
generated: "2026-09-23"
---

# GPT-6 Sol 与 GPT-6 Luna 博文转 OKF Wiki 规范记录

## 内容敏感度预检

源 URL 为公开微信公众号文章，无访问控制参数，判定为公开内容。按标准工作流执行：spec 位于 `.trae/specs/`，bundle 位于 `projects/awesome-okf-xs/doc/bundles/`。

## 七概念编排

- 场景：知识沉淀
- 链路：R → I → E → V
- G1：将文章事实、厂商声明、第三方实测和作者判断分层登记。
- G2：围绕“价格下降、能力分层、任务成本”形成现象—证据—边界—建议洞察。
- G3：抽取“按任务成本而非单价选模型”的可迁移选型模式。
- V：用 OpenAI、DeepSeek 官方资料核验价格、模型定位、上下文与能力声明。

## 骨架判定

文章提供大量比较数字，但没有可复现的安装、配置、输入输出和版本化实测流程；因此不创建 `examples/`，采用技术综述/选型分析骨架：

`index.md` + `concepts/` + `references/` + `log.md`

## 归属位置

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/` 直挂束 | 选定 | 主线是 GPT-6 Sol/Luna 的模型定位、价格与 Agent 任务选型；该分组已有 GPT-6 Astra 相关 bundle，可形成同主题互链 |
| `jishu/ai/deepseek/` | 排除 | DeepSeek 只是价格对照对象，不是文章主线 |
| 新建顶级分组 | 排除 | 单篇文章不新建分组 |

## 知识地图

1. `00-model-lineup-and-pricing.md`：Astra/Sol/Luna 分工、API 价格与缓存机制。
2. `01-agent-task-economics.md`：专业工作、编程、计算机操作与“每任务成本”视角。
3. `02-selection-boundaries-and-competition.md`：与 DeepSeek 的价格对照、证据边界、选型建议。

## 验收标准

- bundle frontmatter 含博文、OpenAI 官方和 DeepSeek 官方信源。
- `facts.md` 与 `references/article-source.md` 的 F 编号集合一致且连续。
- benchmark、第三方实测和内部用量数字全部标注来源层级，不把厂商自述写成独立事实。
- 所有 index 文件含 toctree，父级 AI 索引和总索引计数同步。
