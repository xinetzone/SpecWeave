# LangChain-AI OKF Wiki 教程生成 - Checklist

## 分组结构

- [x] `bundles/langchain-ai/index.md` 存在且含 `okf_version: "0.2"` frontmatter
- [x] `bundles/index.md` 包含 langchain-ai 分组条目，groups 更新为 17
- [x] `bundles/index.md` 的 total_bundles 更新为 130

## 核心框架 bundle（4 个）

- [x] langchain bundle：index.md + concepts/（≥10）+ examples/（≥3）+ references/（≥4）+ spec/facts.md + spec/insights.md
- [x] langgraph bundle：index.md + concepts/（≥8）+ examples/（≥2）+ references/（≥3）+ spec/facts.md + spec/insights.md
- [x] langchainjs bundle：index.md + concepts/（≥8）+ examples/（≥2）+ references/（≥3）+ spec/facts.md + spec/insights.md
- [x] langgraphjs bundle：index.md + concepts/（≥6）+ examples/（≥2）+ references/（≥2）+ spec/facts.md + spec/insights.md

## 关键组件 bundle（9 个）

- [x] langchain-google bundle：concepts/（≥3）+ examples/（≥1）+ references/ 完整
- [x] langchain-mongodb bundle：concepts/（≥3）+ examples/（≥1）+ references/ 完整
- [x] langsmith-sdk bundle：concepts/（≥4）+ examples/（≥1）+ references/ 完整
- [x] langsmith-cli bundle：concepts/（≥3）+ examples/（≥1）+ references/ 完整
- [x] deepagents bundle：concepts/（≥4）+ examples/（≥1）+ references/ 完整，lca-deepagents 内容已整合
- [x] deepagentsjs bundle：concepts/（≥3）+ examples/（≥1）+ references/ 完整
- [x] open-swe bundle：concepts/（≥4）+ examples/（≥1）+ references/ 完整
- [x] openevals bundle：concepts/（≥3）+ examples/（≥1）+ references/ 完整
- [x] openwiki bundle：concepts/（≥3）+ examples/（≥1）+ references/ 完整

## 轻量与参考 bundle（7 个）

- [x] openwork bundle：index.md + concepts/（≥1）+ references/（≥1）+ log.md
- [x] chat-langchain bundle：index.md + concepts/（≥1）+ references/（≥1）+ log.md
- [x] social-media-agent bundle：index.md + concepts/（≥1）+ references/（≥1）+ log.md
- [x] docs bundle：index.md + references/ 信源索引 + log.md
- [x] helm bundle：index.md + references/ 信源索引 + log.md
- [x] terraform bundle：index.md + references/ 信源索引 + log.md

## OKF 规范与质量

- [x] 所有非保留 .md 文件 frontmatter 字段完整（type/title/description/tags/generated/verified/status/stale_after/sources）
- [x] 子目录 index.md 不含 frontmatter，根 index.md 含 okf_version
- [x] 全部交叉链接无断链
- [x] 所有引用的类名/方法名/API 经 Grep 源码验证存在，零虚构
- [x] 文件名 kebab-case，正文中文，交叉链接使用 / 开头路径
- [x] 每个 bundle 根 index.md 提供学习路径推荐