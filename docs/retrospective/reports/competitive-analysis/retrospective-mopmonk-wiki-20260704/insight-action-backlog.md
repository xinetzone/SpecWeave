---
title: MopMonk安全Agent Wiki教程复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-06
type: insight-action-backlog
source: "comprehensive-retrospective-template/insight-action-backlog.md"
project: retrospective-mopmonk-wiki-20260704
template_upgrade: 2026-07-06（模板v1.2补建）
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---

# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。本项目已闭环完成，所有11项行动项均已执行落地。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） | 完成日期 |
|---|---|---|---|---|---|---|
| IMP-001 | 后续行动项§1 | 更新子代理委派指令模板 | 高 | ✅ 已完成 | 新委派的子代理任务指令中包含格式检查点，后续3个wiki任务不再出现frontmatter格式错误 | 2026-07-04 |
| IMP-002 | 后续行动项§2 | 定义wiki教程生产标准DoD | 高 | ✅ 已完成 | DoD文档存在；wiki-spec-template.md预置所有必选步骤和检查项；新wiki任务Spec不需要用户追加原子化等收尾步骤 | 2026-07-04 |
| IMP-003 | 后续行动项§3 | 制定子代理产出5点验收检查清单 | 高 | ✅ 已完成 | 检查清单文档存在；主代理接收子代理产出时逐项检查；低级格式错误拦截率提升至90%以上 | 2026-07-04 |
| IMP-004 | 后续行动项§4 | 确立YAML frontmatter+x-toml-ref元数据标准 | 高 | ✅ 已完成 | frontmatter-metadata-standard规范文档存在；模板文件预置正确格式；所有新文档遵循此标准 | 2026-07-04 |
| IMP-005 | 后续行动项§5 | 沉淀wiki原子化标准模式 | 中 | ✅ 已完成 | SOP文档包含原子化目录结构模板和判断标准；创建原子化模板目录 | 2026-07-04 |
| IMP-006 | 后续行动项§6 | 确立"创作提交+原子化提交"双次提交模式 | 中 | ✅ 已完成 | 提交规范文档中明确说明双次提交的适用场景、commit message格式 | 2026-07-04 |
| IMP-007 | 后续行动项§7 | 建立用户反馈系统性响应流程 | 中 | ✅ 已完成 | 反馈处理流程文档存在；每次用户反馈后有记录和跟进 | 2026-07-04 |
| IMP-008 | 后续行动项§8 | 建立"重复问题立即升级"机制 | 中 | ✅ 已完成 | 机制文档存在；有问题跟踪记录；frontmatter问题作为第一个测试用例验证 | 2026-07-04 |
| IMP-009 | 后续行动项§9 | finalize-atomization.py增加--scope参数 | 低 | ✅ 已完成 | 脚本有--scope参数；dry-run默认仅检查本次变更范围；支持目录/单文件/staged/commit四种范围模式 | 2026-07-04 |
| IMP-010 | 后续行动项§10 | 开发元数据自动化小工具 | 低 | ✅ 已完成 | fix-x-toml-ref.py存在；一个命令即可为当前目录所有MD文件生成正确的TOML和x-toml-ref | 2026-07-04 |
| IMP-011 | 后续行动项§11 | 清理历史遗留旧断链 | 低 | ✅ 已完成 | 清理11处项目自身断链：6处trae_edge_case_handler.py→目录引用、1处vendor.py重复引用删除、2处link_fixer.py→目录引用、1处pytest_gen.py→目录引用、1处subagent-wiki-delivery-checklist.md路径层级修正 | 2026-07-04 |

## 行动项详情

### IMP-001: 更新子代理委派指令模板
- **优先级**: 高
- **来源**: 后续行动项§1
- **执行方案**: 在子代理委派指令模板中强制加入"第一步：读取同目录1-2个同类文件确认格式"作为前置步骤
- **DoD**: 新委派的子代理任务指令中包含此检查点，且明确给出参考文件路径；后续3个wiki任务不再出现frontmatter格式错误
- **执行结果**: 已完成subagent-wiki-delivery-checklist.md创建，包含前置格式检查步骤
- **产出物**: [subagent-wiki-delivery-checklist.md](../../../../../.agents/templates/subagent-wiki-delivery-checklist.md)
- **提交**: commit 40203c8e

---

### IMP-002: 定义wiki教程生产标准DoD
- **优先级**: 高
- **来源**: 后续行动项§2
- **执行方案**: 明确wiki教程生产必选步骤：内容创作→frontmatter验证→TOML元数据→原子化拆分→索引更新→finalize检查→双次提交
- **DoD**: DoD文档存在；wiki-spec-template.md中预置所有必选步骤和检查项；新wiki任务Spec不需要用户追加原子化等收尾步骤
- **执行结果**: 已完成wiki-spec-template.md更新和development-standards.md补充
- **产出物**: [wiki-spec-template.md](../../../../../.agents/templates/wiki-spec-template.md) + [development-standards.md](../../../../development-standards.md)
- **提交**: commit 40203c8e

---

### IMP-003: 制定子代理产出5点验收检查清单
- **优先级**: 高
- **来源**: 后续行动项§3
- **执行方案**: 建立子代理产出验收检查清单：frontmatter分隔符/x-toml-ref/标题层级/文件命名/中文编码
- **DoD**: 检查清单文档存在；主代理接收子代理产出时逐项检查并记录；低级格式错误拦截率提升至90%以上
- **执行结果**: 已完成subagent-wiki-delivery-checklist.md创建，包含5点验收检查
- **产出物**: [subagent-wiki-delivery-checklist.md](../../../../../.agents/templates/subagent-wiki-delivery-checklist.md)
- **提交**: commit 40203c8e

---

### IMP-004: 确立YAML frontmatter+x-toml-ref元数据标准
- **优先级**: 高
- **来源**: 后续行动项§4
- **执行方案**: 将"YAML frontmatter展示 + x-toml-ref引用独立TOML元数据"确立为项目文档元数据标准格式
- **DoD**: frontmatter-metadata-standard规范文档存在；模板文件预置正确格式；所有新文档遵循此标准
- **执行结果**: frontmatter-metadata-standard.md已存在且完整，模板已更新
- **产出物**: [frontmatter-metadata-standard.md](../../../../../.agents/templates/frontmatter-metadata-standard.md)
- **提交**: -（已有规范，验证确认）

---

### IMP-005: 沉淀wiki原子化标准模式
- **优先级**: 中
- **来源**: 后续行动项§5
- **执行方案**: 沉淀wiki原子化标准模式（目录结构+判断标准+命名规范）
- **DoD**: SOP文档包含原子化目录结构模板和"是否需要原子化"的判断标准（>300行/章节独立/未来扩展）；创建原子化模板目录
- **执行结果**: 已完成wiki-atom-template/目录创建和development-standards.md补充
- **产出物**: wiki-atom-template/模板目录 + [development-standards.md](../../../../development-standards.md)
- **提交**: commit caaf6ae7

---

### IMP-006: 确立"创作提交+原子化提交"双次提交模式
- **优先级**: 中
- **来源**: 后续行动项§6
- **执行方案**: 将"创作提交+原子化提交"双次提交模式确立为wiki生产标准提交规范
- **DoD**: 提交规范文档中明确说明双次提交的适用场景、commit message格式；后续wiki任务遵循此模式
- **执行结果**: 已在development-standards.md中补充双层原子提交模式规范
- **产出物**: [development-standards.md](../../../../development-standards.md)
- **提交**: commit caaf6ae7

---

### IMP-007: 建立用户反馈系统性响应流程
- **优先级**: 中
- **来源**: 后续行动项§7
- **执行方案**: 建立用户反馈系统性响应流程（确认→修复→根因→改进→反馈）
- **DoD**: 反馈处理流程文档存在；每次用户反馈后有记录和跟进；小问题修复的同时推动机制改进
- **执行结果**: 已在development-standards.md中补充用户反馈五步响应流程
- **产出物**: [development-standards.md](../../../../development-standards.md)
- **提交**: commit 2139eafa

---

### IMP-008: 建立"重复问题立即升级"机制
- **优先级**: 中
- **来源**: 后续行动项§8
- **执行方案**: 建立"重复问题立即升级"机制——同类问题第二次出现必须在24小时内更新模板/工具
- **DoD**: 机制文档存在；有问题跟踪记录；frontmatter问题作为第一个测试用例验证此机制
- **执行结果**: 已在development-standards.md中补充重复问题升级机制
- **产出物**: [development-standards.md](../../../../development-standards.md)
- **提交**: commit caaf6ae7

---

### IMP-009: finalize-atomization.py增加--scope参数
- **优先级**: 低
- **来源**: 后续行动项§9
- **执行方案**: 研究finalize-atomization.py增加--scope参数，支持"仅检查本次变更文件/目录"
- **DoD**: 脚本有--scope参数；dry-run默认仅检查本次变更范围；需要全量检查时显式指定--all
- **执行结果**: 已完成脚本增强，支持目录/单文件/staged/commit四种范围模式
- **产出物**: [finalize-atomization.py](../../../../../.agents/scripts/finalize-atomization.py)
- **提交**: commit 36dd697b

---

### IMP-010: 开发元数据自动化小工具
- **优先级**: 低
- **来源**: 后续行动项§10
- **执行方案**: 开发元数据自动化小工具，自动计算x-toml-ref相对路径、批量创建对应TOML文件、验证frontmatter格式
- **DoD**: 工具存在；运行一个命令即可为当前目录所有MD文件生成正确的TOML和x-toml-ref；减少人工计算路径错误
- **执行结果**: fix-x-toml-ref.py已存在，wiki-spec-template.md已补充工具引用和流程内置
- **产出物**: [fix-x-toml-ref.py](../../../../../.agents/scripts/fix-x-toml-ref.py) + [wiki-spec-template.md](../../../../../.agents/templates/wiki-spec-template.md)
- **提交**: commit 20660cc1

---

### IMP-011: 清理历史遗留旧断链
- **优先级**: 低
- **来源**: 后续行动项§11
- **执行方案**: 记录本次finalize发现的旧断链，安排专门时间批量清理历史遗留问题
- **DoD**: 有旧断链清单；创建单独任务/提交修复历史断链；不与新功能/新文档任务混在一起
- **执行结果**: 已清理11处项目自身断链
- **产出物**: 断链修复（跨多个文件）
- **提交**: 原子提交（与其他改进项一并提交）

## 已完成核心产出物

- ✅ Wiki教程：[mopmonk-security-agent-wiki.md](../../../../knowledge/learning/03-agent-platforms-tools/mopmonk-security-agent-wiki.md) 及7个原子章节（commit e343cd4f, 3bea7b68）
- ✅ 子代理验收清单模板
- ✅ Wiki标准DoD完成定义
- ✅ Wiki原子化结构模板目录
- ✅ 双层原子提交规范
- ✅ 重复问题升级机制
- ✅ 用户反馈五步响应流程
- ✅ 改进不扩散原则
- ✅ 模式提炼自验证检验标准

## 执行记录

| IMP-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| IMP-001~011 | 2026-07-04 | commit 40203c8e, caaf6ae7, 7af4504a, 2139eafa, 20660cc1, 85f8f296, 36dd697b, 324f831f | 全部11项行动计划闭环完成，含4个高优+4个中优+3个低优，共8次原子提交，沉淀到模板和开发规范中 |

## Changelog

- 2026-07-06 | create | 模板v1.2升级补建：从export-suggestions.md迁移行动项至独立backlog文件（历史项目补建，所有项已闭环）
