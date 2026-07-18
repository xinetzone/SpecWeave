---
id: "harness-engineering-wiki-09"
title: "资源链接"
source: "https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/02-agent-engineering-methodology/harness-engineering-wiki/09-resources.toml"
date: "2026-07-04"
category: "learning"
---
# 资源链接

## 原始资源

**微信公众号原文**：
- https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw?from=industrynews&color_scheme=light#rd
- 作者：涅羽（阿里技术/钉钉悟空团队）

---

## 一手参考资料（文章明确引用）

| 编号 | 资料 | 链接/说明 |
|------|------|----------|
| [1] | Mitchell Hashimoto《My AI Adoption Journey》 | Mitchell Hashimoto个人博客，讲述他在Ghostty项目中实践Agent工程的经验，提出AGENTS.md宪法、规则来自真实失败等核心理念 |
| [2] | LangChain官方博客《Improving Deep Agents with Harness Engineering》 | https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering<br>LangChain官方文章，详细介绍如何通过优化Harness（不换模型）将Terminal Bench从第30名提升到第5名 |
| [3] | 《Enterprise Agent Runtime Five-Layer Architecture》 | 专家博客，提出Agent五层运行时架构：User Interaction → Orchestration → Capabilities → Execution → MCP |

---

## 延伸阅读方向（文章提及未引用）

| 方向 | 说明 |
|------|------|
| Mitchell Hashimoto个人博客 | https://mitchellh.com<br>Terraform创始人，持续分享AI Agent工程实践，是Harness Engineering理念的重要先驱 |
| Anthropic Claude Code技术文章 | Anthropic官方关于Claude Code双阶段架构、Workspace持久化的技术分享 |
| OpenAI内部Agent实践 | OpenAI工程团队公开发言中关于内部Agent架构、反馈回路、护栏设计的经验 |
| MCP协议规范 | https://modelcontextprotocol.io<br>Model Context Protocol官方文档，Agent与工具交互的标准协议 |
| A2A协议演进 | Agent-to-Agent协议相关讨论和草案，关注Agent间协作标准化进展 |

---

## 本项目内相关Wiki

| Wiki | 路径 | 关联点 |
|------|------|--------|
| Agent通信协议 | [agent-communication-protocols](../../01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) | MCP/A2A协议相关，对应Harness的MCP层和未来趋势二 |
| Agent Skills开放标准 | [agent-skills-open-standard-wiki](../../01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md) | Skill开发规范，对应"Agent昂贵Skill廉价"原则和模式2工具签名即文档 |
| Loop Engineering | [longcat-agent-learning-wiki](../longcat-agent-learning-wiki.md) | LongCat Agent实测中的循环工程，对应模式4反馈回路 |
| 多Agent安全护栏 | [mopmonk-security-agent-wiki](../../03-agent-platforms-tools/mopmonk-security-agent-wiki.md) | 多Agent系统的安全护栏设计，对应悟空案例三层硬护栏 |
