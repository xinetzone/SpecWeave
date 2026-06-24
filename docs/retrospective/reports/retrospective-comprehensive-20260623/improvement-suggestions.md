# AI 智能体开发规范体系 — 改进建议

> **所属系列**：[retrospective-comprehensive-20260623](README.md) · **模块 3/6**：改进建议
> **复盘日期**：2026-06-23
> **来源**：从 `retrospective-insight-extraction-comprehensive-20260623.md` 第五章拆分

---

## 五、改进建议

### 5.1 高优先级（立即执行）

| # | 建议 | 针对问题 | 预期效果 |
|---|------|---------|---------|
| S1 | 运行 generate-nav.py 更新所有文档导航表 | 文档导航可能过时 | 确保新旧文档均有导航入口 |
| S2 | 统一复盘报告命名规范（建议前缀 `retrospective-`） | 复盘报告命名不统一 | 提升知识资产可发现性 |
| S3 | 在 prompt_extraction/ 中添加 .agents/ 绑定配置 | prompt_extraction/ 与规范体系耦合松散 | 打通两个系统 |

### 5.2 中优先级（近期规划）

| # | 建议 | 针对问题 | 预期效果 |
|---|------|---------|---------|
| S4 | 合并功能重叠的验证脚本（check-spec-consistency + check-role-permissions） | 工具熵增 | 减少 30% 维护成本 |
| S5 | 启动自我验证模块的可执行化实现（Python 测试用例自动生成器） | 八模块未可执行化 | 实现"规范→代码"的跨越 |
| S6 | 设计泛化引擎的 CLI 原型（`npx ai-init` 或 `python -m agents init`） | 泛化路径停留在概念层面 | 降低新项目采用门槛 |
| S7 | 启动国际化第一步：将 AGENTS.md 翻译为英文版 (AGENTS.en.md) | P0 优先级未启动 | 扩大受众到英文社区 |

### 5.3 低优先级（长期优化）

| # | 建议 | 针对问题 | 预期效果 |
|---|------|---------|---------|
| S8 | 部署 GitHub Actions / AtomGit CI 运行 ci-check.ps1 | CI 管道未实际运行 | 每次 PR 自动验证 |
| S9 | 构建自我洞察模块的仪表盘（Streamlit） | 八模块未可执行化 | 实时监控系统状态 |
| S10 | 建立跨领域角色包（Data Analyst、Content Creator、DevOps） | 角色体系可扩展 | 拓宽应用领域 |

### 5.4 后续行动计划

| 优先级 | 行动项 | 具体措施 | 建议时间 |
|--------|--------|---------|---------|
| 🔴 高 | S1 更新导航表 | 运行 `python .agents/scripts/generate-nav.py` | 立即 |
| 🔴 高 | S2 统一复盘命名 | Grep 搜索 `retrospective-report-*` 和 `retrospective-insight-*`，重命名为统一前缀 | 本周 |
| 🔴 高 | S3 绑定配置 | 在 prompt_extraction/config.py 中添加 `.agents/` 路径配置 | 本周 |
| 🟡 中 | S4 脚本合并 | 分析 check-spec-consistency.py 和 check-role-permissions.py 的重叠逻辑，提取公共库 | 2周内 |
| 🟡 中 | S6 泛化 CLI | 设计 `ai init` 命令的原型：选择项目类型→填充模板→验证配置 | 1月内 |
| 🟡 中 | S7 英文版 | 翻译 AGENTS.md 为英文版 | 1月内 |
| 🟢 低 | S8 部署 CI | 在 atomgit 仓库配置 CI 流水线 | 2月内 |

---

> **上一模块**：[insight-extraction.md](insight-extraction.md) — 洞察与萃取
> **下一模块**：[execution-s1-s3.md](execution-s1-s3.md) — S1-S3 执行复盘
