---
id: "i-have-adhd-wiki-tutorial-checklist"
title: "i-have-adhd Wiki教程 - 验证清单"
source: "基于spec.md验收标准派生的验证检查点"
---

# i-have-adhd ADHD友好输出技能 - 验证清单

## 结构完整性检查
- [ ] CP-1: Wiki目录 `i-have-adhd-wiki/` 已创建于正确路径 `.agents/docs/knowledge/learning/03-agent-platforms-tools/`
- [ ] CP-2: 存在 `00-overview.md` 入口文件
- [ ] CP-3: 存在 `README.md` 目录索引文件
- [ ] CP-4: 存在 `01-design-philosophy.md` 设计理念章节
- [ ] CP-5: 存在 `02-core-rules.md` 核心规则章节
- [ ] CP-6: 存在 `03-exceptions-and-checklist.md` 例外场景章节
- [ ] CP-7: 存在 `04-installation-guide.md` 安装指南章节
- [ ] CP-8: 存在 `05-always-on-mechanism.md` 持久化机制章节
- [ ] CP-9: 存在 `06-evaluation-framework.md` 评估框架章节
- [ ] CP-10: 存在 `07-customization-and-troubleshooting.md` 自定义与排障章节
- [ ] CP-11: 存在 `08-patterns-extracted.md` 模式萃取章节
- [ ] CP-12: 存在 `09-faq-and-resources.md` FAQ与资源章节

## 内容准确性检查
- [ ] CP-13: 5大ADHD认知原理（工作记忆小、知行鸿沟、启动困难、时间感知模糊、多巴胺稀缺）全部覆盖
- [ ] CP-14: 10条核心规则（行动优先、编号步骤、明确下一步、抑制离题、重述状态、时间估计、成果可见、客观错误、列表≤5项、无客套话）逐条详解，每条包含Bad/Good示例
- [ ] CP-15: 6条例外场景（explain模式、破坏性操作确认、调试螺旋、歧义澄清、规则vs任务、规则vs harness）全部覆盖
- [ ] CP-16: Pre-send check 5项自检清单完整记录
- [ ] CP-17: 至少8个平台（Claude Code、Codex、Cursor、Gemini CLI、GitHub Copilot、Zed、Hermes、Pi）的安装指南完整，包含install/verify/update/uninstall
- [ ] CP-18: always-on三种机制（flag+hooks、AGENTS.md配置、Gemini extension）全部解析
- [ ] CP-19: hooks.json和always-on.sh关键代码正确引用和解释
- [ ] CP-20: 评估框架5维权重（Correctness35%/Autonomy25%/Actionability20%/Safety10%/Concision10%）与rubric一致
- [ ] CP-21: release gate 4个条件完整记录
- [ ] CP-22: 自定义流程（fork→修改→替换安装）步骤完整
- [ ] CP-23: 故障排查覆盖INSTALL.md中所有常见问题
- [ ] CP-24: 至少萃取2个可复用模式（目标3个），每个包含触发场景/核心步骤/反模式/迁移验证

## 格式规范检查
- [ ] CP-25: 所有.md文件包含正确的YAML frontmatter（id、title、source字段）
- [ ] CP-26: 所有代码块标注正确语言（bash/json/python/markdown/text等）
- [ ] CP-27: 文件引用使用file:///绝对路径格式（遵循SpecWeave规范）
- [ ] CP-28: 文档使用中文编写（符合用户偏好）
- [ ] CP-29: Before/After示例使用表格或并列代码块清晰对比
- [ ] CP-30: 不包含HTML标签（必要时除外），保持MyST Markdown兼容

## 七概念质量门检查
- [ ] CP-31 (G1): 事实描述部分无因果推断词（"因为"、"导致"、"所以"等判断词），保持客观
- [ ] CP-32 (G2): 洞察/分析部分包含四元组：现象描述、证据引用、本质分析、应用建议
- [ ] CP-33 (G3): 萃取的模式可迁移至非ADHD领域（技术文档写作、API设计、客服话术等至少1个场景验证）
- [ ] CP-34 (V门): 对抗审查已执行——从"ADHD用户视角"、"非ADHD用户视角"、"Agent开发者视角"、"极简主义者视角"四个角度验证规则合理性

## 链接与引用检查
- [ ] CP-35: README.md中的所有章节链接正确指向对应文件
- [ ] CP-36: 外部资源链接（GitHub仓库等）格式正确
- [ ] CP-37: 源码引用路径正确（指向external/libs/i-have-adhd/下的对应文件）
- [ ] CP-38: 内部章节交叉引用使用正确的相对路径

## 最终交付检查
- [ ] CP-39: 所有文件frontmatter中的source字段正确标注来源
- [ ] CP-40: 内容不涉及医学诊断建议（保持"No ADHD diagnosis needed"立场）
- [ ] CP-41: 注明原项目MIT许可证
- [ ] CP-42: 快速参考卡（10条规则一句话版）已包含在FAQ章节
- [ ] CP-43: Trae IDE适配说明已补充
