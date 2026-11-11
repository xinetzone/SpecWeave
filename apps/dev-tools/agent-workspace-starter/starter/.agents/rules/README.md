---
id: "rules"
title: "治理规则体系"
source: ".agents/rules/README.md"
---
# 治理规则体系

本目录收录项目的治理规则体系，涵盖内容敏感度预检、AI 编码行为准则、Bug 修复闭环、Spec 文档编写与创建预检。所有开发者和智能体在编写代码、执行任务时，均应参照本规则体系确保开发过程得到系统性约束。

## 规则文档清单

| 文档 | 用途 | 适用阶段 |
|---|---|---|
| [content-sensitivity-precheck.md](content-sensitivity-precheck.md) | 内容敏感度预检：公开/私域两级判定、信号清单、工作流分流决策树 | 任务启动（启动协议步骤 2.3） |
| [ai-coding-guidelines.md](ai-coding-guidelines.md) | AI 编码行为准则：四条核心原则（歧义澄清/简约至上/精确编辑/目标驱动） | 编码、任务沟通 |
| [fix-prevent-close-loop.md](fix-prevent-close-loop.md) | 修复即闭环三阶段强制 SOP：修复→预防→闭环，禁止纯点修复 | Bug 修复、问题解决 |
| [spec-writing-guide.md](spec-writing-guide.md) | Spec 文档编写指南：标准章节结构、必需元素、编写规范 | 编码、规范编写 |
| [spec-creation-precheck.md](spec-creation-precheck.md) | Spec 创建前预检：位置核查 + 格式核查 | 规范创建（创建 spec 前必做） |

## 快速导航

| 场景 | 应查阅的文档 |
|---|---|
| 我不确定内容是公开还是私域？ | [content-sensitivity-precheck.md](content-sensitivity-precheck.md)（就高不就低原则） |
| AI 写代码总是过度设计/乱改/猜需求？ | [ai-coding-guidelines.md](ai-coding-guidelines.md)（四条核心原则 + 速查表） |
| 修 Bug 时怎么防止同类问题再发？ | [fix-prevent-close-loop.md](fix-prevent-close-loop.md)（三阶段 SOP） |
| 我要编写或创建一个新的 spec？ | [spec-writing-guide.md](spec-writing-guide.md) + [spec-creation-precheck.md](spec-creation-precheck.md) |

## 规则维护

- 规则新增或变更应经过评审，并通知所有相关智能体。
- 定期审查规则有效性，根据实际使用反馈调整识别标准与阈值。

> 完整规则体系（阶段守卫、硬编码治理、数据安全等）见 SpecWeave 开源仓库。