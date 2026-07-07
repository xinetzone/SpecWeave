---
id: "open-code-review-wiki-10"
title: "资源与参考链接"
source: "../open-code-review-wiki.md#资源与参考链接"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/10-resources.toml"
---
# 资源与参考链接

> 本章节汇总 Open Code Review 学习过程中相关的原始资源、官方资源、论文、数据集及相关学习材料，方便读者深入探索。

---

## 原始资源

- [微信公众号文章《阿里开源 AI 代码评审工具 Open Code Review》](https://mp.weixin.qq.com/s/WSicyyMEIXnNVDoWuz0jrw) - 本教程的内容来源，由阿里工程师李峥峰撰写，基于个人技术实践与独立思考分享 Open Code Review 的设计理念、技术实现与评测数据。

---

## 官方资源

- [Open Code Review GitHub 仓库](https://github.com/alibaba/open-code-review) - 项目源代码和文档，包含完整实现、安装说明、使用示例和配置指南
- [规则文档](https://github.com/alibaba/open-code-review/tree/main/internal/config/rules/rule_docs) - 内置 13 套语言/文件类型专属评审规则文档，涵盖 Java、TypeScript/React、C、MyBatis XML、Maven/Gradle 等主流场景
- [GitHub Issues](https://github.com/alibaba/open-code-review/issues) - 问题反馈和讨论，欢迎提交使用体验问题或更好的想法，官方团队会跟进回复

---

## 论文资源

- [反思模型论文](https://arxiv.org/pdf/2602.20166v1) - Qwen3-30B-A3B 反思模型的训练细节，详细介绍了如何从噪声数据（用户反馈中的"采纳"、"误报"、"忽略"）中通过混合不同噪声比例的扰动数据集训练多个差异化模型进行协同标注，最终将误报拦截率从 30.09% 提升到 52.63%
- [AACR-Bench 论文](https://arxiv.org/abs/2601.19494) - 行业基准评测体系，由南京大学与阿里巴巴 TRE 联合推出，采用"AI 辅助 + 人类专家校验"标注流水线，覆盖 10 种编程语言、200 个真实 PR、80+ 位资深工程师交叉标注，问题覆盖率提升 285%

---

## 数据集资源

- [AACR-Bench GitHub](https://github.com/alibaba/aacr-bench) - 评测数据集和代码，可用于复现评测结果或评估自定义 ACR 工具的效果
- [HuggingFace 数据集](https://huggingface.co/datasets/Alibaba-Aone/aacr-bench) - 在线数据集，方便直接加载使用，包含完整的仓库级依赖上下文

---

## 相关学习资源

### Claude Code 相关

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code) - Anthropic 官方 CLI 编码工具文档，Open Code Review 提供了对 Claude Code 的原生集成（Command 和 Skills 两种接入方式）
- Claude Code 的 `/code-review` 命令 - Open Code Review 在 AACR-Bench 评测中的主要对比对象之一

### AI 代码评审相关概念

- **ACR（AI Code Review）**：AI 驱动的代码评审任务，AACR-Bench 重新定义了其评估标准
- **Agent 工具集设计**：基于 tool-call traces 蒸馏的场景化工具集，比通用 Agent 工具包更稳定可预测
- **分治策略**：将代码变更拆分为独立子任务并发评审，各自维护独立对话上下文，Token 消耗线性可控
- **反思模型（Reflection Model）**：作为过滤器拦截误报，降低"告警疲劳"
- **三层递进式定位**：Hunk-based 文本匹配 → 全文件扫描 → LLM 重定位，保证 97%+ 位置准确率

### OpenTelemetry 文档

- [OpenTelemetry 官方文档](https://opentelemetry.io/docs/) - Open Code Review 内置 OpenTelemetry 支持，可上报评审过程的 spans 和 metrics，便于监控和调优
- 配置示例：
  ```bash
  ocr config set telemetry.enabled true
  ocr config set telemetry.exporter otlp
  ocr config set telemetry.otlp_endpoint localhost:4317
  ocr config set telemetry.content_logging true  # 可选：包含 LLM prompt 内容
  ```

### CI/CD 集成相关

- [GitHub Actions 文档](https://docs.github.com/en/actions) - Open Code Review 提供 GitHub Actions 集成示例（`examples/` 目录）
- [GitLab CI 文档](https://docs.gitlab.com/ee/ci/) - Open Code Review 提供 GitLab CI 集成示例，支持 MR 创建时自动触发，评审结果通过 GitLab Discussions API 以行级讨论形式回写

---

## 本项目内相关 Wiki

本项目（d:\AI\docs\knowledge\learning\）内包含多个 AI Agent 学习教程，与 Open Code Review 主题相关的 wiki 包括：

- **Agent 通信协议系列**：
  - `agent-communication-protocols/` - MCP、ACP、A2A、ANP 等协议对比（Open Code Review 未来规划包含 MCP 集成）
  - `agent-skills-wiki/` - Agent Skills 开放标准（Open Code Review 支持 Claude Code Skills 接入方式）
- **Agent 接口深度剖析**：
  - `agent-interface-deep-dive/` - Agent Interface、API、ABI、Protocol 对比
  - `interface-api-abi-protocol-wiki/` - 接口、API、ABI、协议概念解析
- **其他 AI 工具学习教程**：
  - `mopmonk-security-agent-wiki/` - MopMonk 安全 Agent 学习教程（AI 安全领域的另一个案例）
  - `longcat-agent-learning-wiki/` - LongCat Agent 学习教程（国产大模型在 Agent 编程中的应用）
  - `karpathy-llm-coding-guidelines/` - Karpathy LLM 编码指南（AI 编码的最佳实践）
  - `rainman-translate-book-wiki/` - Rainman 翻译书籍 Wiki（另一个 AI 工具应用案例）

---

## 参考链接索引

原始文章中引用的参考链接汇总：

| 编号 | 链接 | 说明 |
|------|------|------|
| [1] | https://github.com/alibaba/open-code-review | Open Code Review GitHub 仓库 |
| [2] | https://arxiv.org/pdf/2602.20166v1 | 反思模型论文 |
| [3] | https://github.com/alibaba/open-code-review/tree/main/internal/config/rules/rule_docs | 规则文档 |
| [4] | https://github.com/alibaba/open-code-review/issues | GitHub Issues |
| — | https://github.com/alibaba/aacr-bench | AACR-Bench GitHub |
| — | https://arxiv.org/abs/2601.19494 | AACR-Bench 论文 |
| — | https://huggingface.co/datasets/Alibaba-Aone/aacr-bench | HuggingFace 数据集 |
