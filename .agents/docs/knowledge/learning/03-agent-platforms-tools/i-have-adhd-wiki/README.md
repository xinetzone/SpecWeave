---
id: "i-have-adhd-wiki-readme"
title: "i-have-adhd Wiki 目录索引"
source: "external/libs/i-have-adhd 知识沉淀"
---
# i-have-adhd Wiki 目录索引

## 一、简介

i-have-adhd 是一个跨AI编程助手的Agent Skills插件，基于ADHD认知原理设计输出规范，让AI回复"行动优先、步骤清晰、无冗余客套"。本Wiki系统梳理i-have-adhd的设计理念、核心规则、安装配置、评估体系与自定义开发方法，为Agent Skills开发者提供可复用的设计范式参考。

**源项目地址**：[file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/)

## 二、章节导航

| 编号 | 文件 | 标题 | 内容简介 |
|------|------|------|---------|
| 00 | [00-overview.md](file:///d:/spaces/SpecWeave/.agents/docs/knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/00-overview.md) | 一、概述 | 项目介绍、核心理念、适用人群、Before/After效果对比、文档结构索引 |
| 01 | 01-design-philosophy.md | 二、设计理念 | ADHD认知科学基础、五条核心事实、《The Adult ADHD Tool Kit》理论溯源、输出设计思路 |
| 02 | 02-core-rules.md | 三、核心规则 | 10条输出规则逐条详解、正反示例对比、Pre-send检查清单、适用边界说明 |
| 03 | 03-exception-scenarios.md | 四、例外场景 | 6种可以打破规则的场景：解释请求、危险操作、调试死循环、需求歧义、规则冲突、宿主约束 |
| 04 | 04-installation-guide.md | 五、安装指南 | Claude Code/Codex/其他主流客户端安装方法、命令行操作步骤、支持客户端列表 |
| 05 | 05-persistence-mechanism.md | 六、持久化机制 | Session级生效原理、关闭指令、always-on自动加载配置、多平台持久化方案 |
| 06 | 06-evaluation-framework.md | 七、评估框架 | evals评估体系、cases.jsonl测试用例设计、rubric评分标准、run_evals.py执行脚本 |
| 07 | 07-custom-development.md | 八、自定义开发 | Fork修改流程、SKILL.md定制方法、私有插件市场部署、跨平台适配 |
| 08 | 08-pattern-extraction.md | 九、模式萃取 | 可复用输出设计模式提炼、SpecWeave技能体系集成思考、反模式识别与避坑指南 |
| 09 | 09-faq.md | 十、FAQ | 常见问题解答、使用技巧、故障排查、与其他输出风格Skill的对比 |

## 三、核心特色速览

| 特性 | 说明 |
|------|------|
| **行动优先** | 第一行就是可执行的动作，而非上下文铺垫或客套话 |
| **编号步骤** | 多步骤任务使用编号列表，每个步骤是单一可界定的动作 |
| **明确收尾** | 以一个2分钟内可完成的具体下一步结束，而非模糊的"有问题再问" |
| **抑制离题** | 一次只解决一个问题，次要问题作为独立问题另行提出 |
| **状态重述** | 每轮对话重述当前进度（"第3步共5步已完成"），降低工作记忆负担 |
| **具体时间估计** | 使用"约15分钟"而非"一点工作"，给出可感知的时间预期 |
| **成果可见** | 明确展示已完成的工作成果，用可验证的方式呈现 |
| **客观错误表述** | 直接陈述错误原因和修复方案，不使用"哎呀"、"糟糕"等情绪化表达 |
| **列表上限** | 单个列表不超过5项，超过则拆分为"立即做/以后做"或"必须/可选" |
| **无冗余客套** | 禁止开场白、总结回顾、结束语，直接开始和结束回答 |

## 四、适用人群

- **ADHD用户**：输出结构适配ADHD认知特点，减少注意力分散
- **效率导向开发者**：行动优先的输出风格节省阅读时间，快速进入执行
- **Agent Skills学习者**：优秀的Skill设计范例，学习基于认知科学设计输出规范
- **AI工具重度用户**：简洁直接的回复风格，无需滚动跳过冗长客套话

## 五、学习建议

### 推荐阅读顺序

**快速了解（15分钟）**：
1. [00-overview.md](file:///d:/spaces/SpecWeave/.agents/docs/knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/00-overview.md) - 了解项目定位和效果对比
2. 02-core-rules.md - 掌握10条核心规则（待填充）
3. 04-installation-guide.md - 安装到自己的AI编程助手体验（待填充）

**深入研究（2小时）**：
```
00-overview.md
  → 01-design-philosophy.md（理解认知科学基础）
  → 02-core-rules.md（逐条掌握规则）
  → 03-exception-scenarios.md（学会灵活运用）
  → 05-persistence-mechanism.md（配置持久化）
  → 06-evaluation-framework.md（理解质量评估）
  → 07-custom-development.md（自定义修改）
  → 08-pattern-extraction.md（模式萃取复用）
  → 09-faq.md（问题解答）
```

### 实践建议

1. **先体验再研究**：先安装到Claude Code/Codex中实际使用，感受输出风格差异
2. **规则不是教条**：理解6条例外场景，在合适的时候灵活调整
3. **从简单定制开始**：可以先Fork项目微调规则，再考虑深度定制
4. **关注评估体系**：修改规则后用evals框架验证输出质量
5. **萃取可复用模式**：将i-have-adhd的设计思路应用到自己的Skill开发中
