---
title: forum-bot.py浏览器自动化工具开发与日志增强复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-bot-logging-20260629/insight-action-backlog.toml"
project: retrospective-forum-bot-logging-20260629
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本次项目已完成forum-bot.py开发和日志增强，剩余改进项待后续执行。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 项目交付 | forum-bot.py v2开发完成 | 高 | ✅ 已完成 | ~580行Playwright脚本，分级日志+Bug修复 | 2026-06-29 |
| IMP-002 | 改进§5 | 知识库文件统一kebab-case命名 | 高 | ✅ 已完成 | 中文文件名重命名为kebab-case | 2026-06-29 |
| IMP-003 | 改进§6 | spec和forum-automation.md引用更新 | 高 | ✅ 已完成 | 所有中文文件名引用统一更新 | 2026-06-29 |
| IMP-004 | 知识库更新 | forum-automation.md文件引用更新 | 高 | ✅ 已完成 | 引用更新为kebab-case文件名 | 2026-06-29 |
| IMP-005 | 知识库更新 | discourse-api-research.md重命名 | 高 | ✅ 已完成 | 从中文文件名重命名为kebab-case | 2026-06-29 |
| IMP-006 | 知识库更新 | knowledge/README.md索引更新 | 高 | ✅ 已完成 | 更新文档索引表，补充摘要和标签 | 2026-06-29 |
| IMP-007 | 改进§1 | 首次运行自动检测未登录状态 | 中 | ⏳ 待规划 | 首次运行提示用户执行login | - |
| IMP-008 | 改进§2 | @discourse/mcp长期方案接入 | 低 | ⏳ 待规划 | 配置User API Key，验证MCP工具可用性 | - |
| IMP-009 | 改进§3 | DOM选择器提取为配置文件 | 中 | ⏳ 待规划 | 选择器配置化，页面改版只需改配置 | - |
| IMP-010 | 改进§4 | 参数化FORUM_URL支持多站点 | 低 | ⏳ 待规划 | 支持多个Discourse站点 | - |
| IMP-011 | 行动§高 | 萃取分级日志双轨输出模式 | 高 | ⏳ 待萃取 | dual-channel-tiered-logging入库code-patterns/ | - |
| IMP-012 | 行动§高 | 萃取检查函数状态恢复模式 | 高 | ⏳ 待萃取 | check-and-restore入库code-patterns/ | - |
| IMP-013 | 行动§中 | 萃取浏览器自动化三级决策模型 | 中 | ⏳ 待萃取 | 架构模式入库 | - |
| IMP-014 | 行动§中 | 添加edit/reply/clean-drafts端到端测试 | 中 | ⏳ 待规划 | 下次使用时补充验证测试 | - |
| IMP-015 | 模式建议 | 萃取多信号组合检测模式 | 中 | ⏳ 待萃取 | multi-signal-detection入库tools-automation/ | - |
| IMP-016 | 模式建议 | 萃取Early Return公共初始化防护模式 | 低 | ⏳ 待萃取 | L1模式入库tools-automation/ | - |

## 行动项详情

### IMP-001: forum-bot.py v2开发完成
- **优先级**: 高
- **执行结果**: ~580行Playwright脚本完成，含分级日志系统（控制台INFO+文件DEBUG）、7个核心分支日志覆盖、4个Bug修复
- **产出物**: [forum-bot.py](../../../../../../.agents/scripts/forum-bot.py)

---

### IMP-002~006: 知识库修复与更新（已完成）
- **IMP-002**: 知识库文件统一kebab-case命名
- **IMP-003**: spec和forum-automation.md引用更新
- **IMP-004**: [forum-automation.md](../../../../../knowledge/operations/forum-automation.md)
- **IMP-005**: [discourse-api-research.md](../../../../../knowledge/operations/discourse-api-research.md)
- **IMP-006**: [knowledge/README.md](../../../../../knowledge/)

---

### IMP-007: 首次运行自动检测未登录状态
- **优先级**: 中
- **状态**: ⏳ 待规划
- **验收标准**: 首次运行时自动检测未登录状态，提示用户执行login

---

### IMP-008: @discourse/mcp长期方案接入
- **优先级**: 低
- **状态**: ⏳ 待规划
- **验收标准**: 配置User API Key，验证MCP工具可用性，替代浏览器自动化

---

### IMP-009: DOM选择器提取为配置文件
- **优先级**: 中
- **状态**: ⏳ 待规划
- **验收标准**: DOM选择器提取为配置文件，页面改版时只需改配置

---

### IMP-010: 参数化FORUM_URL支持多站点
- **优先级**: 低
- **状态**: ⏳ 待规划
- **验收标准**: 参数化FORUM_URL，支持多个Discourse站点

---

### IMP-011~016: 模式萃取（待执行）
- **IMP-011**: 分级日志双轨输出模式（dual-channel-tiered-logging，L2）
- **IMP-012**: 检查函数状态恢复模式（check-and-restore，L2）
- **IMP-013**: 浏览器自动化三级决策模型（架构模式）
- **IMP-014**: edit/reply/clean-drafts端到端验证测试
- **IMP-015**: 多信号组合检测模式（multi-signal-detection，L2）
- **IMP-016**: Early Return公共初始化防护模式（L1）

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~006 | 2026-06-29 | 本次交付 | forum-bot.py开发+日志增强+知识库命名修复完成 |
| IMP-007~016 | - | - | 待后续规划执行/萃取 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件（6项已完成，10项待规划/待萃取）
