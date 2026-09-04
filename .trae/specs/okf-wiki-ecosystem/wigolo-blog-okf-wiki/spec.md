# Spec：wigolo 博文 → OKF 知识包

## 目标

将微信公众号「极客之家」wigolo 推荐文转化为 OKF v0.2 知识包，归属 `jishu/ai/ai-agent/` 分组，bundle 名 `wigolo`。

## 骨架判定（两问）

1. 有可照做流程？✅（init/doctor/verify/serve/CLI/curl/env 配置，官方 getting-started 提供完整输入输出）
2. 作者一手实测 + 可复现？✅（作者自述安装/接线/n8n 实践；官方文档版本/步骤/输出齐备）
→ **技术教程/选型类，含 examples/**

## 内容结构（信源先行）

| 层 | 文件 | 内容 |
|----|------|------|
| references | article-source.md | F-001~F-052 双份事实登记（与 facts.md 集合一致） |
| references | verification.md | P0 核验报告（0❌/2⚠️）、勘误四张清单、信源距离 |
| concepts/00 | product-overview.md | 发布事实层：定位、10 工具地图、选型对比（Firecrawl/Tavily/Exa）、维护与许可 |
| concepts/01 | evidence-contract.md | 机制层：18 引擎融合+ML 重排、字节级证据契约、诚实输出、fetch 三级路由 |
| concepts/02 | local-first-architecture.md | 架构层：本地数据面、keyless/LLM 边界、四种接入表面、隐私模型与已知边界 |
| examples/00 | install-and-doctor.md | 安装初始化、init 变体、doctor/verify/warmup、卸载清理 |
| examples/01 | connect-agents.md | --agents 一键接线、手动 MCP 配置、LLM provider 配置（Gemini/Ollama） |
| examples/02 | ten-tools-hands-on.md | 十工具 CLI 实战（search/fetch/crawl/extract/cache/find_similar/research/agent/diff/watch） |
| examples/03 | rest-sdk-integration.md | serve REST + curl/n8n、TS/Python SDK、框架集成包 |

## 质量门

- G1：事实句无因果词（"因为/所以/导致"），全部 F 编号可溯
- G2：概念层四元组（现象→机制→边界→信源）
- G3：examples 全部命令来自官方 README/docs，可照做
- G4：mermaid 遵循安全编码六规则（无括号特殊字符问题、节点 ID 规范）
- 机械门禁：toctree 完整、相对链接可达、UTF-8、三级索引计数更新（bundles 398→399 / jishu 301→302 / ai 121→122 / ai-agent 35→36）

## 配图

seedream 生成 1 张本地优先概念横幅 → `wigolo/images/wigolo-banner.png`，index.md 相对路径引用。
