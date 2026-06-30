---
version: "2.2"
last_updated: "2026-06-30"
schema: "l0-onboarding-v1"
layer: "L0"
max_lines: 100
---

# SpecWeave Agent Onboarding

> ⚠️ **本文件是L0入口层**（<100行），遵循渐进式披露三层架构：
> - L0：本文件（身份+能力速查+路由表，<30秒读完）
> - L1：[capability-registry.md](capability-registry.md)（全量能力索引，1-3分钟读完）
> - L2：完整规范文档（按需阅读，通过L1索引进入）
>
> 你是 SpecWeave 项目的 AI Agent。本文件帮你在新会话中快速建立上下文，无需盲目遍历目录。

---

## 快速开始（3 步）

```
步骤1：你正在读本文件 ✅
步骤2：读取 capability-registry.md 了解全部能力
步骤3：按下方路由表定位目标能力，按需加载详细文档
```

---

## 能力速查表（核心高频）

| 你要做什么 | 用什么 | 去哪里 |
|-----------|--------|--------|
| **执行复盘**（项目/阶段/事件回顾） | retrospective-cmd Skill | [skills/retrospective-cmd/SKILL.md](skills/retrospective-cmd/SKILL.md) |
| **萃取洞察**（数据分析/问题诊断） | insight-cmd Skill | [skills/insight-cmd/SKILL.md](skills/insight-cmd/SKILL.md) |
| **导出报告**（结构化报告生成） | export-report-cmd Skill | [skills/export-report-cmd/SKILL.md](skills/export-report-cmd/SKILL.md) |
| **原子化文档**（拆分大文件） | atomization-cmd Skill | [skills/atomization-cmd/SKILL.md](skills/atomization-cmd/SKILL.md) |
| **原子化提交**（Git提交规范） | atomic-commit-cmd Skill | [skills/atomic-commit-cmd/SKILL.md](skills/atomic-commit-cmd/SKILL.md) |
| **创建/检查Mermaid图表**（流程图/架构图/时序图） | mermaid-cmd Skill | [skills/mermaid-cmd/SKILL.md](skills/mermaid-cmd/SKILL.md) |
| **CI提交前全量检查**（8步流水线） | ci-check-cmd Skill | [skills/ci-check-cmd/SKILL.md](skills/ci-check-cmd/SKILL.md) |
| **检查/修复链接**（断链/路径错误） | link-check-cmd Skill | [skills/link-check-cmd/SKILL.md](skills/link-check-cmd/SKILL.md) |
| **更新导航/看板**（文档索引生成） | docgen-cmd Skill | [skills/docgen-cmd/SKILL.md](skills/docgen-cmd/SKILL.md) |
| **原子化后一键收尾** | atomization-finalize-cmd Skill | [skills/atomization-finalize-cmd/SKILL.md](skills/atomization-finalize-cmd/SKILL.md) |
| **检查重复代码**（DRY原则） | check-duplication-cmd Skill | [skills/check-duplication-cmd/SKILL.md](skills/check-duplication-cmd/SKILL.md) |
| **操作论坛**（发帖/编辑/回复/草稿） | forum-posting Skill | [skills/forum-posting/SKILL.md](skills/forum-posting/SKILL.md) |
| **浏览器自动化**（网页交互/截图/测试） | integrated_browser MCP | MCP工具（系统内置） |

> 💡 完整能力索引（30+脚本、13个Skill、3个工作流、7份协议、7条规则、知识库与模式库入口）见 [capability-registry.md](capability-registry.md)

---

## 必知 vs 按需

| 文档 | 何时读 | 优先级 |
|------|--------|--------|
| [AGENTS.md](../AGENTS.md) | **每个会话必读**（全局规则+启动协议） | 🔴 必须 |
| [capability-registry.md](capability-registry.md) | **每个会话必读**（全量能力索引） | 🔴 必须 |
| 具体Skill/脚本/协议文档 | 执行对应任务时，通过L1索引进入 | 🟢 按需 |

> 💡 **原则**：不要预读所有文档。先用速查表定位目标能力，再读取该能力的SKILL.md；找不到时查L1注册表。

---

## 任务路由决策树

```
收到用户任务 →
├─ 复盘/回顾/总结 → retrospective-cmd
├─ 洞察/分析/根因 → insight-cmd
├─ 导出/生成报告 → export-report-cmd
├─ 拆分/原子化文档 → atomization-cmd
├─ 原子化后收尾 → atomization-finalize-cmd
├─ 提交/commit → atomic-commit-cmd
├─ Mermaid/流程图/架构图/画图 → mermaid-cmd
├─ CI检查/提交前检查/全量检查 → ci-check-cmd
├─ 链接检查/断链修复 → link-check-cmd
├─ 更新导航/刷新看板/文档索引 → docgen-cmd
├─ 重复代码/提取共享库/DRY检查 → check-duplication-cmd
├─ 发帖/论坛/Discourse → forum-posting Skill
├─ 创建/优化Skill → 查L1注册表定位规范入口
├─ 浏览器/网页/截图 → integrated_browser MCP
├─ 跨项目/vendor子模块 → 查L1注册表定位VENDOR-INTEGRATION
├─ 检查/验证类 → ci-check-cmd（全量）或查L1注册表找对应脚本Skill
└─ 其他/不确定 → capability-registry.md 快速查找指南
```

---

## 新会话启动确认

首次输出中确认：

```
📋 上下文已建立：已读取 AGENTS.md、ONBOARDING.md（L0）、capability-registry.md（L1）
任务类型识别：<复盘/Skill操作/检查/...>
将使用：<对应能力>
```
