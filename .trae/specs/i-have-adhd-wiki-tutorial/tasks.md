---
id: "i-have-adhd-wiki-tutorial-tasks"
title: "i-have-adhd Wiki教程 - 实施计划"
source: "基于spec.md分解的原子化任务清单"
---

# i-have-adhd ADHD友好输出技能 - 实施计划

## [x] Task 1: 创建Wiki目录结构与入口文件
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/` 下创建 `i-have-adhd-wiki/` 目录
  - 创建 `00-overview.md` 入口文件（项目概述、核心理念、目录索引）
  - 创建 `README.md` 目录索引
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录创建成功，包含00-overview.md和README.md
  - `programmatic` TR-1.2: 两个文件均包含正确的YAML frontmatter（id、title、source）
  - `human-judgement` TR-1.3: 00-overview.md清晰概述项目定位、设计理念与文档结构
- **Notes**: 参考 [agent-skills-wiki/00-overview.md](../../../.agents/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/00-overview.md) 格式

## [x] Task 2: 创建认知原理与设计理念章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `01-design-philosophy.md` 设计理念章节
  - 详解5大ADHD认知驱动事实：工作记忆小、知行鸿沟、启动困难、时间感知模糊、多巴胺稀缺
  - 建立"认知原理→设计决策→输出规则"映射关系
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: 5大认知原理全部覆盖，每条有中文解释
  - `human-judgement` TR-2.2: 原理到规则的映射逻辑清晰、可追溯
  - `programmatic` TR-2.3: 文件frontmatter正确，无格式错误
- **Notes**: 核心内容来自 [SKILL.md#what-adhd-changes-about-reading](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/skills/i-have-adhd/SKILL.md#L23-L31)

## [x] Task 3: 创建10条核心规则详解章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建 `02-core-rules.md` 核心规则章节
  - 逐条详解10条输出规则，每条包含：规则编号、中文名称、规则说明、Bad示例、Good示例
  - 添加规则设计原理引用（关联到Task 2的认知原理）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 10条规则完整覆盖（行动优先、编号步骤、明确下一步、抑制离题、重述状态、时间估计、成果可见、客观错误、列表≤5项、无客套话）
  - `human-judgement` TR-3.2: 每条规则的Bad/Good示例对比清晰、有说服力
  - `programmatic` TR-3.3: 代码块标注正确语言（markdown/text用于示例）
- **Notes**: 核心内容来自 [SKILL.md#rules](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/skills/i-have-adhd/SKILL.md#L33-L117)

## [x] Task 4: 创建例外场景与自检清单章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 创建 `03-exceptions-and-checklist.md` 例外场景与自检章节
  - 详解6条例外场景：explain模式、破坏性操作确认、调试螺旋、歧义澄清、规则vs任务冲突、规则vs harness冲突
  - 完整记录Pre-send check发送前5项自检清单
  - 添加"首行+末行"验证法说明
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: 6条例外场景全部覆盖
  - `programmatic` TR-4.2: 5项自检清单条目完整
  - `human-judgement` TR-4.3: 例外场景的边界条件说明清晰，避免误用
- **Notes**: 核心内容来自 [SKILL.md#when-to-break-the-rules](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/skills/i-have-adhd/SKILL.md#L119-L128) 和 [SKILL.md#pre-send-check](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/skills/i-have-adhd/SKILL.md#L130-L142)

## [x] Task 5: 创建跨平台安装与配置章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建 `04-installation-guide.md` 安装指南章节
  - 覆盖8+平台：Claude Code、Codex、Cursor、Gemini CLI、GitHub Copilot、Zed、Hermes、Pi、Antigravity(agy)、通用agent-skills平台
  - 每个平台包含：安装命令、验证方法、更新方法、卸载方法
  - 整理always-on配置为独立小节
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 至少8个平台的安装指南完整
  - `programmatic` TR-5.2: 每个平台都有install/verify/update/uninstall四步
  - `human-judgement` TR-5.3: 命令可直接复制执行，平台差异标注清晰
- **Notes**: 核心内容来自 [INSTALL.md](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/INSTALL.md)

## [x] Task 6: 创建Always-On持久化机制章节
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 创建 `05-always-on-mechanism.md` 持久化机制章节
  - 详解三种always-on方式：flag文件+hooks（Claude Code）、AGENTS.md/SOUL.md配置（其他平台）、Gemini extension
  - 解析hooks.json配置和always-on.sh脚本的POSIX sh实现
  - 说明激活机制的三种状态（未安装、按需调用、always-on）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 三种持久化方式全部覆盖
  - `human-judgement` TR-6.2: hooks脚本工作原理解释清晰（POSIX sh兼容性、YAML frontmatter剥离逻辑）
  - `programmatic` TR-6.3: hooks.json和always-on.sh关键代码片段正确引用
- **Notes**: 核心内容来自 [hooks/hooks.json](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/hooks/hooks.json) 和 [hooks/always-on.sh](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/hooks/always-on.sh)

## [x] Task 7: 创建评估框架与质量保障章节
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建 `06-evaluation-framework.md` 评估体系章节
  - 详解5维评分rubric：Correctness(35%)、Autonomy(25%)、Actionability(20%)、Safety(10%)、Concision(10%)
  - 记录盲评流程（A/B/C标记、blocker判定）
  - 说明release gate通过条件
  - 解析评估脚本隔离性设计（避免配置污染baseline）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 5个评估维度及权重与rubric.md一致
  - `programmatic` TR-7.2: release gate 4个条件完整记录
  - `human-judgement` TR-7.3: 评估方法论解释清晰，体现科学验证思维
- **Notes**: 核心内容来自 [evals/rubric.md](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/evals/rubric.md) 和 [evals/README.md](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/evals/README.md)

## [x] Task 8: 创建自定义开发与故障排查章节
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 创建 `07-customization-and-troubleshooting.md` 自定义与排障章节
  - 提供fork+修改SKILL.md+替换安装的完整自定义流程
  - 列出常见问题：autocomplete不显示、always-on不生效、marketplace add失败、回复仍有开场白、技能安装后缺失
  - 每个问题包含症状、可能原因、解决方案
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-8.1: 自定义流程步骤完整（uninstall→remove marketplace→add fork→install）
  - `human-judgement` TR-8.2: 故障排查覆盖INSTALL.md中列出的所有常见问题
- **Notes**: 核心内容来自 [INSTALL.md#troubleshooting](file:///d:/spaces/SpecWeave/external/libs/i-have-adhd/INSTALL.md#L567-L588)

## [x] Task 9: 萃取可复用模式章节
- **Priority**: high
- **Depends On**: Task 3, Task 6, Task 7
- **Description**: 
  - 创建 `08-patterns-extracted.md` 模式萃取章节
  - 模式1：「认知原理驱动输出规范」模式（认知局限→设计规则→示例验证）
  - 模式2：「跨平台Agent Skill适配」模式（核心SKILL.md + 平台特定配置 + 适配层）
  - 模式3：「输出风格A/B测试验证」模式（基线/候选隔离→盲评→加权评分→release gate）
  - 每个模式包含：触发场景、核心步骤、反模式、迁移验证
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-9.1: 至少2个可复用模式（目标3个）
  - `human-judgement` TR-9.2: 每个模式包含触发场景、核心步骤、反模式、迁移验证四要素（G3质量门）
  - `human-judgement` TR-9.3: 模式可迁移至非ADHD场景（如技术文档写作、API响应设计、客服话术）
- **Notes**: 使用extraction-cmd萃取标准进行验证

## [x] Task 10: 创建FAQ与资源汇总章节
- **Priority**: low
- **Depends On**: Task 8
- **Description**: 
  - 创建 `09-faq-and-resources.md` FAQ与资源章节
  - 整理常见Q&A（适用人群、与简洁输出区别、是否需要ADHD确诊、如何关闭、与其他skill冲突怎么办）
  - 汇总资源链接：原仓库、Agent Skills标准、参考书籍《The Adult ADHD Tool Kit》
  - 添加"快速参考卡"（10条规则一句话版）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-10.1: FAQ覆盖用户可能关心的核心疑问
  - `programmatic` TR-10.2: 资源链接正确可访问
- **Notes**: 补充Trae IDE适配说明（基于Open Question 1的默认回答：兼容Agent Skills标准，可参考Cursor配置）

## [x] Task 11: 完成质量门验证与索引更新
- **Priority**: high
- **Depends On**: Task 1-10
- **Description**: 
  - 运行格式检查：验证所有文件frontmatter、链接、代码块格式
  - G1质量门检查：事实描述无因果推断错误
  - G2质量门检查：洞察四元组完整
  - G3质量门检查：模式可迁移
  - 更新README.md目录索引，确保所有章节正确链接
  - 生成本次知识沉淀的七概念执行日志汇总
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-11.1: 所有文件存在且frontmatter正确
  - `programmatic` TR-11.2: 内部链接无断链（可用link-check验证）
  - `human-judgement` TR-11.3: G1-G3质量门全部通过
  - `human-judgement` TR-11.4: README.md索引完整，与实际文件一致
- **Notes**: 使用link-check-cmd验证链接有效性
