---
id: "i-have-adhd-wiki-overview"
title: "一、概述"
source: "external/libs/i-have-adhd 源码分析"
---
# 一、概述

## 1.1 什么是 i-have-adhd？

i-have-adhd 是一个**跨AI编程助手的Agent Skills插件**，采用MIT许可协议开源，基于ADHD（注意力缺陷多动障碍）认知原理设计输出规范，帮助AI编程助手生成更适合ADHD用户阅读和执行的响应内容。

**项目位置**：[file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/)

**核心定位**：阻止AI助手把答案藏在冗长的客套文字中，让输出直接面向行动。它不是简单的"精简回复"，而是根据ADHD大脑的认知特点重新塑造输出结构，降低从"理解"到"执行"的摩擦成本。

**核心理念（Slogan）**：ADHD-friendly outputs. No ADHD diagnosis needed!（对ADHD友好的输出，无需确诊ADHD！）

## 1.2 效果对比示例

<table>
<tr>
<td width="50%">

### Before（默认输出风格）

> 问得好！让我想一想。你的身份验证流程包含几个环节：中间件、令牌验证和 Cookie 处理。查看 `src/auth.ts` 后，`verifyToken` 函数（大约第 42–58 行）似乎使用了旧版 `jsonwebtoken` API。一种做法是升级这个包并重写该函数。完成修改后，你需要运行身份验证测试，确认没有破坏任何功能。顺便一提，你可能还想整体检查一下依赖版本。希望这能帮到你！如果你想进一步研究，请告诉我。

</td>

<td width="50%">

### After（i-have-adhd 输出风格）

> 运行 `npm install jsonwebtoken@latest`，然后编辑 `src/auth.ts:42`。
>
> 1. 打开 `src/auth.ts`
> 2. 将 `verifyToken`（第 42–58 行）替换为下面的代码片段
> 3. 运行 `npm test -- auth.spec.ts`
>
> 下一步：如果有测试失败，请粘贴第一行报错。

</td>
</tr>
</table>

（详细规则解析见后续「核心规则」章节）

## 1.3 核心理念

i-have-adhd 的设计基于ADHD认知科学的五个核心事实，这也是其10条规则的理论基础：

1. **工作记忆容量有限**：屏幕外的信息容易被遗忘，不要求读者"记住X"
2. **知道不等于做到**："理解了"和"做完了"之间的摩擦是工作停滞的主要原因
3. **启动是最难的一步**：第一个行动必须明显、微小、可以立刻执行
4. **时间估计模糊化**："一点工作"和"几小时"在感知上没有区别，模糊估计无效
5. **多巴胺稀缺**：可见的进度至关重要，被埋没的成果无法被感知

## 1.4 适用人群

| 人群类型 | 受益点 |
|---------|-------|
| **ADHD用户** | 输出结构适配ADHD认知特点，减少注意力分散，降低启动门槛 |
| **效率导向开发者** | 行动优先的输出风格节省阅读时间，直接进入执行环节 |
| **Agent Skills学习者** | 优秀的Skill设计范例，学习如何基于认知科学设计输出规范 |
| **所有AI助手用户** | 简洁直接的回复风格适合快速获取信息，无需滚动跳过客套话 |

## 1.5 本Wiki文档结构

本Wiki将从多个维度系统解析i-have-adhd项目：

| 章节 | 文件 | 内容简介 |
|------|------|---------|
| 一、概述 | [00-overview.md](file:///d:/spaces/SpecWeave/.agents/docs/knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/00-overview.md) | 项目介绍、核心理念、适用人群、文档索引 |
| 二、设计理念 | 01-design-philosophy.md | ADHD认知原理、五条核心事实、设计思路溯源 |
| 三、核心规则 | 02-core-rules.md | 10条输出规则详解、正反示例、适用边界 |
| 四、例外场景与自检清单 | 03-exceptions-and-checklist.md | 何时可以打破规则、6种例外情况处理、Pre-send检查清单 |
| 五、安装指南 | 04-installation-guide.md | Claude Code/Codex/其他客户端安装方法、持久化配置 |
| 六、持久化机制详解 | 05-always-on-mechanism.md | Session级生效机制、关闭方式、always-on配置 |
| 七、评估框架 | 06-evaluation-framework.md | evals评估体系、测试用例、rubric评分标准 |
| 八、自定义开发与故障排查 | 07-customization-and-troubleshooting.md | Fork自定义、SKILL.md修改、私有版本部署、常见问题排查 |
| 九、可复用模式萃取 | 08-patterns-extracted.md | 可复用模式提炼、SpecWeave集成思考、反模式识别 |
| 十、FAQ与资源汇总 | 09-faq-and-resources.md | 常见问题解答、使用技巧、资源汇总 |
| 目录索引 | [README.md](file:///d:/spaces/SpecWeave/.agents/docs/knowledge/learning/03-agent-platforms-tools/i-have-adhd-wiki/README.md) | 完整章节列表与快速导航 |
