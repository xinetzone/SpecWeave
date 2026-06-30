---
version: "2.0"
last_updated: "2026-06-30"
schema: "specweave-onboarding-v2"
layer: "L0"
---

# SpecWeave Agent Onboarding

> ⚠️ **本文件是L0入口层**（<100行），遵循[渐进式披露三层架构](capabilities/ARCHITECTURE.md)：
> - L0：本文件（身份+能力速查+路由表，<30秒读完）
> - L1：[capability-registry.md](capability-registry.md)（全量能力索引，1-3分钟读完）
> - L2：[protocols/](protocols/)（完整协议规范，按需阅读）
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
| **操作论坛**（发帖/编辑/回复/草稿） | forum-posting Skill | [skills/forum-posting/SKILL.md](skills/forum-posting/SKILL.md) |
| **浏览器自动化**（网页交互/截图/测试） | integrated_browser MCP | MCP工具（系统内置） |
| **提交前全量检查** | ci-check 脚本 | [scripts/ci-check.ps1](scripts/ci-check.ps1) |
| **查阅技术知识库**（操作/排障/最佳实践） | docs/knowledge/ | [docs/knowledge/README.md](../docs/knowledge/README.md) |
| **查阅复盘模式库**（可复用方法论/模式） | docs/retrospective/patterns/ | [docs/retrospective/patterns/README.md](../docs/retrospective/patterns/README.md) |
| **查阅开发规范**（代码风格/提交/测试） | docs/development-standards.md | [docs/development-standards.md](../docs/development-standards.md) |

> 💡 完整能力索引（30+脚本、6个Skill、3个工作流、7份协议、7条规则）见 [capability-registry.md](capability-registry.md)

---

## 必知 vs 按需

| 文档 | 何时读 | 优先级 |
|------|--------|--------|
| [AGENTS.md](../AGENTS.md) | **每个会话必读**（全局规则+启动协议） | 🔴 必须 |
| [capability-registry.md](capability-registry.md) | **每个会话必读**（全量能力索引） | 🔴 必须 |
| [capabilities/ARCHITECTURE.md](capabilities/ARCHITECTURE.md) | 了解三层架构设计原则 | 🟡 首次必读 |
| 具体Skill/命令/协议文档 | 执行对应任务时 | 🟢 按需 |
| docs/knowledge/ 或 docs/retrospective/patterns/ | 需要领域知识或模式参考时 | 🟢 按需 |

---

## 任务路由决策树

```
收到用户任务 →
├─ 复盘/回顾/总结 → retrospective-cmd
├─ 洞察/分析/根因 → insight-cmd
├─ 导出/生成报告 → export-report-cmd
├─ 拆分/原子化文档 → atomization-cmd
├─ 提交/commit → atomic-commit-cmd
├─ 发帖/论坛/Discourse → forum-posting Skill
├─ 创建/优化Skill → skill-development规则 + vendor skill-creator
├─ 浏览器/网页/截图 → integrated_browser MCP
├─ 跨项目/vendor子模块 → VENDOR-INTEGRATION + vendor/AGENTS.md
├─ 检查/验证 → ci-check（全量）或查REGISTRY找对应脚本
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

> 完整会话启动协议（设计理由、与PDR协议关系、上下文恢复策略）见L2文档 [protocols/onboarding-protocol.md](protocols/onboarding-protocol.md)
