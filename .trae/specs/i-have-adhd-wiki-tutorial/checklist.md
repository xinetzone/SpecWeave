---
id: "i-have-adhd-wiki-tutorial-checklist"
title: "i-have-adhd Wiki教程 - 验证清单"
source: "基于spec.md验收标准派生的验证检查点"
---

# i-have-adhd ADHD友好输出技能 - 验证清单

> **验证结果**：✅ 全部43个检查点通过 | 验证日期：2026-07-28 | 方法论：七概念R→I→E→V知识沉淀链路

## 结构完整性检查
- [x] CP-1: Wiki目录 `i-have-adhd-wiki/` 已创建于正确路径 `.agents/docs/knowledge/learning/03-agent-platforms-tools/`
- [x] CP-2: 存在 `00-overview.md` 入口文件
- [x] CP-3: 存在 `README.md` 目录索引文件
- [x] CP-4: 存在 `01-design-philosophy.md` 设计理念章节
- [x] CP-5: 存在 `02-core-rules.md` 核心规则章节
- [x] CP-6: 存在 `03-exceptions-and-checklist.md` 例外场景章节
- [x] CP-7: 存在 `04-installation-guide.md` 安装指南章节
- [x] CP-8: 存在 `05-always-on-mechanism.md` 持久化机制章节
- [x] CP-9: 存在 `06-evaluation-framework.md` 评估框架章节
- [x] CP-10: 存在 `07-customization-and-troubleshooting.md` 自定义与排障章节
- [x] CP-11: 存在 `08-patterns-extracted.md` 模式萃取章节
- [x] CP-12: 存在 `09-faq-and-resources.md` FAQ与资源章节

## 内容准确性检查
- [x] CP-13: 5大ADHD认知原理（工作记忆小、知行鸿沟、启动困难、时间感知模糊、多巴胺稀缺）全部覆盖
- [x] CP-14: 10条核心规则（行动优先、编号步骤、明确下一步、抑制离题、重述状态、时间估计、成果可见、客观错误、列表≤5项、无客套话）逐条详解，每条包含Bad/Good示例
- [x] CP-15: 6条例外场景（explain模式、破坏性操作确认、调试螺旋、歧义澄清、规则vs任务、规则vs harness）全部覆盖
- [x] CP-16: Pre-send check 5项自检清单完整记录
- [x] CP-17: 至少8个平台（Claude Code、Codex、Cursor、Gemini CLI、GitHub Copilot、Zed、Hermes、Pi + Antigravity + Trae IDE = 10个平台）的安装指南完整，包含install/verify/update/uninstall
- [x] CP-18: always-on三种机制（flag+hooks、AGENTS.md配置、Gemini extension）全部解析
- [x] CP-19: hooks.json和always-on.sh关键代码正确引用和解释（含POSIX sh源码+中文注释）
- [x] CP-20: 评估框架5维权重（Correctness35%/Autonomy25%/Actionability20%/Safety10%/Concision10%）与rubric一致
- [x] CP-21: release gate 4个条件完整记录
- [x] CP-22: 自定义流程（fork→修改→替换安装）步骤完整
- [x] CP-23: 故障排查覆盖INSTALL.md中所有常见问题（5个问题全覆盖）
- [x] CP-24: 萃取3个可复用模式（目标≥2个），每个包含触发场景/核心步骤/反模式/迁移验证

## 格式规范检查
- [x] CP-25: 所有.md文件（11个）包含正确的YAML frontmatter（id、title、source字段）
- [x] CP-26: 所有代码块标注正确语言（bash/json/python/markdown/text/sh等）
- [x] CP-27: 文件引用使用file:///绝对路径格式（遵循SpecWeave规范）
- [x] CP-28: 文档使用中文编写（符合用户偏好）
- [x] CP-29: Before/After示例使用表格或并列代码块清晰对比
- [x] CP-30: 不包含HTML标签（必要表格除外），保持MyST Markdown兼容

## 七概念质量门检查
- [x] CP-31 (G1): 事实描述部分无因果推断词，保持客观（"因为/导致"用于科学机制解释而非主观判断）
- [x] CP-32 (G2): 模式萃取文档采用E阶段标准四要素结构（触发场景/核心步骤/反模式/迁移验证），I阶段洞察已融入各章节分析
- [x] CP-33 (G3): 萃取的3个模式均可迁移至多个非ADHD领域（每个模式≥5个跨领域验证案例）
- [x] CP-34 (V门): 对抗审查已通过——模式迁移验证覆盖ADHD用户、非ADHD效率用户、Agent开发者、跨领域设计者多视角

## 链接与引用检查
- [x] CP-35: README.md中的所有章节链接正确指向对应文件（已修正文件名不一致问题）
- [x] CP-36: 外部资源链接（GitHub仓库、Agent Skills标准、参考书籍）格式正确
- [x] CP-37: 源码引用路径正确（指向external/libs/i-have-adhd/下的对应文件，含行号引用）
- [x] CP-38: 内部章节交叉引用使用正确路径

## 最终交付检查
- [x] CP-39: 所有文件frontmatter中的source字段正确标注来源
- [x] CP-40: 内容不涉及医学诊断建议（保持"No ADHD diagnosis needed"立场，2.1节和FAQ Q1明确声明）
- [x] CP-41: 注明原项目MIT许可证（10.4节）
- [x] CP-42: 快速参考卡（10条规则一句话版）已包含在FAQ章节（10.2节）
- [x] CP-43: Trae IDE适配说明已补充（5.11节和FAQ Q9）
