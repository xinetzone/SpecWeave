---
type: spec
title: "AgentGit：面向 Agent Session 的版本化协作"
source: "https://mp.weixin.qq.com/s/A8Dm2FSpfNmqpUf4nqCcHg?from=industrynews&color_scheme=light#rd"
status: completed
generated: "2026-09-23"
---

# AgentGit 博文转 OKF Wiki 规范记录

## 内容敏感度预检

源 URL 为公开微信公众号文章，无 `share?code=`、`token` 或其他访问控制信号，判定为公开内容。按标准工作流执行：本 spec 位于 `.trae/specs/`，最终 bundle 位于 `projects/awesome-okf-xs/doc/bundles/`。

## 七概念编排

- 场景：知识沉淀
- 链路：R → I → E → V
- G1：事实清单与作者观点分离，无因果推断
- G2：洞察按现象、根因、影响、建议组织
- G3：抽取可迁移的“Session 版本化协作”模式
- V：官方产品资料对日期、功能、运行时、分享与安全边界进行核验

## 骨架判定

文章没有完整的安装、配置、输入输出和版本化实测步骤，不能构成可复现教程。因此不创建 `examples/`，采用商业/产品分析类骨架：

`index.md` + `concepts/` + `references/` + `log.md`

## 归属位置

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `zhexue/methodology/` | 选定 | 文章主线是 AI 时代软件协作范式与隐性知识沉淀，现有分组已收录思维模型和可迁移方法论 |
| `jishu/ai/` | 排除 | 文章没有源码、API 或可复现实验，技术产品属性不是主要知识层 |
| 新建分组 | 排除 | 单篇文章不新建分组 |

## 知识地图

1. `00-agentgit-session-model.md`：AgentGit 的产品定位、Session/Context 对象模型与 Git 类比。
2. `01-context-handoff-and-knowledge-network.md`：会话交接、跨 Agent 继续工作与团队隐性知识网络。
3. `02-security-and-operational-boundaries.md`：分享、Remote Control、数据存储和敏感信息边界。

## 验收标准

- bundle frontmatter 完整，含博文和官方资料双重信源。
- `facts.md` 与 `references/article-source.md` 的 F 编号集合一致且连续。
- 核验失败的安全扫描声明在 `verification.md` 中明确标注，并在正文改写为官方可证实的安全边界。
- 所有 index 文件包含 toctree，新增链接可达。
