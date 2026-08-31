# Chaos 知识包合集

Chaos 分类收录跨领域、多样化的 OKF v0.2 知识包，涵盖 AI 智能体框架、深度学习编译器、IoT 智能家居、人文学术、工具生态五大技术与人文领域。每个知识包均遵循 OKF 规范构建，包含系统梳理的概念文档、实践示例与完整的信源事实登记。

## AI Agent 框架与工具

- [AI Agent Skills 知识包](./ai-agent-skills/index.md) — AI Agent Skills 生态——SKILL.md 标准、MCP 工具协议、人格集合与工程化集成
- [mobile-use 知识包](./mobile-use/index.md) — 基于 LangGraph 的 AI 多智能体移动端自动化框架——Android/iOS 设备自然语言控制
- [veadk-python 知识包](./veadk-python/index.md) — 火山引擎 Agent Development Kit——基于 Google ADK 扩展的全链路 Python Agent 工程化框架

## 编译器与深度学习

- [Apache TVM 深度学习编译器](./apache-tvm/index.md) — Apache TVM 四层栈架构知识包，涵盖 FFI 基础设施、TIR 张量 IR、Relax 图级 IR、Runtime 执行引擎、MetaSchedule 自动调度及 LLM 推理支持
- [tiktoken 源码学习知识包](./tiktoken/index.md) — OpenAI tiktoken v0.14.0 源码学习知识包，涵盖双层架构总览、BPE 分词原理、Encoding 核心 API、Rust 原生内核、注册表与模型映射、词表加载缓存、OpenAI 公开词汇体系及教学模块

## IoT 与智能家居

- [Home Assistant](./home-assistant/index.md) — 开源智能家居平台——核心架构、集成开发、测试与工具链
- [Tuya IoT 知识包](./tuya-iot/index.md) — TuyaOpen 跨平台 IoT SDK——TAL/TKL 双层抽象、组件化构建、全栈 IoT 能力与 AI 开发技能

## 人文学术

- [旋元佑进阶语法](./english-grammar/index.md) — 旋元佑《语法俱乐部》系统知识包，遵循「简单句→复合句→复杂句→简化从句」三层次句法递进框架，涵盖31篇概念文档、事实清单与信源登记
- [《老子》传本源流谱系](./laozi-lineage/index.md) — 系统梳理《老子》（《道德经》）从战国楚简、西汉帛书、汉简到传世本的传本源流谱系，涵盖考古发现、文本异文、校勘方法论等核心概念

## 工具与生态

- [OKF 生态系统知识包](./okf-ecosystem/index.md) — OKF（Open Knowledge Format）生态——Bundle 数据模型、爬取构建流水线、增量同步与桌面阅读器

```{toctree}
:maxdepth: 2

ai-agent-skills/index
apache-tvm/index
english-grammar/index
home-assistant/index
laozi-lineage/index
mobile-use/index
okf-ecosystem/index
tiktoken/index
tuya-iot/index
veadk-python/index
CROSS_BUNDLE_REVIEW
PATTERNS_LESSONS
retrospective-okf-wiki-build
```