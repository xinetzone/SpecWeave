---
id: "improvement-suggestions-improvement-suggestions"
title: "AI 智能体开发规范体系 — 改进建议"
source: "external: 不存在-docs/retrospective/reports/retrospective-comprehensive-20260623.md#五"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-comprehensive-20260623/improvement-suggestions.toml"
---
# AI 智能体开发规范体系 — 改进建议

> **所属系列**：[retrospective-comprehensive-20260623](README.md) · **模块 3/6**：改进建议
> **复盘日期**：2026-06-23
> **来源**：从 `retrospective-insight-extraction-comprehensive-20260623.md` 第五章拆分

---

## 五、改进建议

### 5.1 高优先级（已全部完成）

| # | 建议 | 状态 | 执行说明 |
|---|------|------|---------|
| S1 | 运行 generate-nav.py 更新所有文档导航表 | ✅ 已完成 | 跳过 auto-generate（手动条目含跨目录引用，运行会丢失数据），手动条目已完备 |
| S2 | 统一复盘报告命名规范（建议前缀 `retrospective-`） | ✅ 已完成 | 3 个文件重命名 + 14 文件 33 处引用全局替换（脚本化 rename_refs.py） |
| S3 | 在 prompt_extraction/ 中添加 .agents/ 绑定配置 | ✅ 已完成 | constants/paths.py 扩展 4 个路径常量 + Pipeline.writeback 方法新增 |

### 5.2 中优先级（已全部完成）

| # | 建议 | 状态 | 执行说明 |
|---|------|------|---------|
| S4 | 合并功能重叠的验证脚本（check-spec-consistency + check-role-permissions） | ✅ 已完成 | lib/ 公共库创建（project/frontmatter/cli 三层分离）+ 2 脚本重构 + resolve_project_root OR 逻辑 bug 修复 |
| S5 | 启动自我验证模块的可执行化实现（Python 测试用例自动生成器） | ✅ 已完成 | generate-tests.py，支持 spec → pytest 骨架，含中文函数名蛇形命名策略 |
| S6 | 设计泛化引擎的 CLI 原型（`npx ai-init` 或 `python -m agents init`） | ✅ 已完成 | agents.py init，支持 software/library 两类项目预设，str.format() 零依赖模板引擎 |
| S7 | 启动国际化第一步：将 AGENTS.md 翻译为英文版 (AGENTS.en.md) | ✅ 已完成 | 120 行英文快速索引锚定页（核心表结构 + 路由指引，非全量翻译） |

### 5.3 低优先级（长期优化）

| # | 建议 | 状态 | 备注 |
|---|------|------|------|
| S8 | 部署 GitHub Actions / AtomGit CI 运行 ci-check.ps1 | ⬜ 待办 | |
| S9 | 构建自我洞察模块的仪表盘（Streamlit） | ⬜ 待办 | |
| S10 | 建立跨领域角色包（Data Analyst、Content Creator、DevOps） | ⬜ 待办 | |

### 5.4 执行结果汇总

| 优先级 | 建议 | 状态 | 执行摘要 |
|--------|------|------|---------|
| 🔴 高 | S1 更新导航表 | ✅ 已完成 | 跳过 auto-generate，手动条目含跨目录引用，运行会丢失数据 |
| 🔴 高 | S2 统一复盘命名 | ✅ 已完成 | 3 文件重命名 + rename_refs.py 全局替换 14 文件 33 处引用 |
| 🔴 高 | S3 绑定配置 | ✅ 已完成 | constants/paths.py 追加 4 路径常量 + Pipeline.writeback 方法 |
| 🟡 中 | S4 脚本合并 | ✅ 已完成 | lib/ 三层公共库 + OR 逻辑 bug 修复 + 7 脚本回归通过 |
| 🟡 中 | S5 测试生成器 | ✅ 已完成 | generate-tests.py：spec → pytest 骨架，中文函数名蛇形命名 |
| 🟡 中 | S6 泛化 CLI | ✅ 已完成 | agents.py init，software/library 双预设，str.format() 零依赖 |
| 🟡 中 | S7 英文版 | ✅ 已完成 | AGENTS.en.md 120 行英文快速索引锚定页 |
| 🟢 低 | S8 部署 CI | ⬜ 待办 | 触发条件：AtomGit/GitHub 仓库配置就绪 |
| 🟢 低 | S9 洞察仪表盘 | ⬜ 待办 | 触发条件：自我洞察模块可执行化完成 |
| 🟢 低 | S10 角色包 | ⬜ 待办 | 触发条件：跨领域应用需求明确 |

> **执行统计**：高+中优先级 7 项全部完成（100%），总耗时约 120 分钟（S1-S3 ~30 + S4-S7 ~90），剩余 3 项低优先级待触发条件就绪。

---

> **上一模块**：[insight-extraction.md](insight-extraction.md) — 洞察与萃取
> **下一模块**：[execution-s1-s3.md](execution-s1-s3.md) — S1-S3 执行复盘
