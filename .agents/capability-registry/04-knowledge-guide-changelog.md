---
id: "capability-registry-knowledge-guide"
title: "知识参考、快速查找指南与更新说明"
source: "capability-registry.md#04-knowledge-guide-changelog"
x-toml-ref: "../../.meta/toml/.agents/capability-registry/04-knowledge-guide-changelog.toml"
---
# 知识参考、快速查找指南与更新说明

## 知识参考索引（.agents/docs/）

| 知识库 | 用途 | 触发关键词 | 安全等级 | 路径 |
|--------|------|-----------|---------|------|
| 技术知识库（knowledge） | 操作指南、排障经验、最佳实践、VENDOR集成方案 | "知识库"、"最佳实践"、"怎么操作"、"排障" | 只读 | [../docs/knowledge/README.md](../docs/knowledge/README.md) |
| 复盘模式库（patterns） | 可复用架构/代码/方法论模式、资产清单 | "模式库"、"复用模式"、"有没有现成方案" | 只读 | [../docs/retrospective/patterns/README.md](../docs/retrospective/patterns/README.md) |
| 开发规范（standards） | 代码风格、提交规范、Markdown规范、测试要求 | "开发规范"、"代码风格"、"提交规范"、"测试要求" | 只读 | [../docs/development-standards.md](../docs/development-standards.md) |
| 复盘体系（retrospective） | 复盘报告、洞察报告、经验萃取 | "复盘报告"、"经验总结"、"回顾文档" | 只读 | [../docs/retrospective/README.md](../docs/retrospective/README.md) |

---


## 快速查找指南

按场景快速定位：

```
我要...
├─ 检查链接是否有效/修复断链 → link-check-cmd Skill → check-links.py --fix
├─ 提交前做CI全量检查 → ci-check-cmd Skill → ci-check.ps1 / ci-check.sh
├─ 快速检查（仅关键阻断项） → ci-check-cmd Skill §5.2 快速模式
├─ 把大文档拆成小文件 → atomization-cmd Skill → finalize-atomization.py收尾
├─ 原子化后一键收尾 → atomization-finalize-cmd Skill（断链+导航+看板）
├─ 更新文档导航/看板/应用清单 → docgen-cmd Skill → docgen.py (nav/dashboard/apps/all)
├─ 检查脚本重复代码/提取共享库 → check-duplication-cmd Skill → check-duplication.py
├─ 检查RACI矩阵合规性（A唯一性/R≠A分离） → check-raci-compliance.py --path <dir>
├─ 检测Python硬编码（URL/路径/配置/魔数） → check-hardcode.py --path <dir>
├─ 创建一个新Skill → 读skill-development.md + vendor skill-creator
├─ 创建新文件（遵守三步前置检查） → file-creation命令集
├─ 操作论坛帖子 → forum-posting Skill
├─ 控制智能家居设备 → home-assistant Skill
├─ 做项目复盘 → retrospective-cmd Skill
├─ 从执行中萃取洞察 → insight-cmd Skill
├─ 从洞察/复盘中沉淀可复用模式 → pattern-extraction-cmd Skill
├─ 导出正式报告 → export-report-cmd Skill
├─ 原子化Git提交 → atomic-commit-cmd Skill
├─ 创建/检查/修复Mermaid图表 → mermaid-cmd Skill → mermaid命令集
├─ Mermaid复杂架构图协作 → team-mermaid专项团队
├─ 生成测试用例 → generate-tests.py
├─ 检查Skill是否符合五要素 → check-skill-quality.py
├─ 分析阶段守卫日志 → check-stage-guardrails.py / generate-sg-dashboard.py
├─ 查知识库/最佳实践 → .agents/docs/knowledge/
├─ 查可复用模式 → .agents/docs/retrospective/patterns/
├─ 查开发规范 → .agents/docs/development-standards.md
└─ 了解有哪些角色/模块/协议 → 读AGENTS.md索引表
```

---


## 更新说明

- **v1.8** (2026-07-01): 新增pattern-extraction-cmd命令集门面Skill（第14个Skill），基于markdown-as-interface五要素模型，封装从复盘/洞察中萃取可复用模式的标准化流程，整合3个模式相关脚本（pattern-maturity.py/check-pattern-quality.py/pattern-maturity-stats.py）；新增pattern-extraction命令集（第9个命令）；快速查找指南补充模式沉淀入口。
- **v1.7** (2026-07-01): 为check-raci-compliance.py和check-hardcode.py新增核心治理脚本用法示例区块，包含完整CLI参数说明和5种典型用法示例；快速查找指南补充RACI合规检查和硬编码检测入口。
- **v1.6** (2026-07-01): 新增2个规范合规检查脚本：check-raci-compliance.py（RACI矩阵A唯一性/R≠A分离/角色列完整性检查）、check-hardcode.py（Python AST硬编码检测，覆盖8类硬编码）；补充遗漏的raci-governance-standards.md规则条目，rules计数从7修正为8；scripts计数从30更新为32。
- **v1.5** (2026-07-01): 补充命令集索引遗漏的2个命令（file-creation文件创建、home-assistant智能家居集成），命令集计数从6修正为8；与commands/README.md指令集清单保持一致。
- **v1.4** (2026-06-30): 完成第一批5个高频脚本Skill化，Skill索引从7个增至13个。新增：link-check-cmd（链接检查/修复）、atomization-finalize-cmd（原子化一键收尾）、docgen-cmd（文档导航/看板生成）、ci-check-cmd（CI综合检查）、check-duplication-cmd（重复代码检测）。Skill分类扩展为三类（完整Skill/命令集门面/脚本命令门面）；补充遗漏的home-assistant完整Skill；更新脚本dry-run标注和安全等级（docgen/finalize-atomization/ci-check标注Git-based预览机制）；快速查找指南全面更新为Skill路由模式。
- **v1.3** (2026-06-30): 新增Mermaid图表管理能力注册：mermaid-cmd Skill（命令门面）、mermaid命令集、team-mermaid专项团队；更新计数（skills:7, commands:6）；快速查找指南补充Mermaid相关条目。
- **v1.2** (2026-06-30): 新增知识参考索引区块（.agents/docs/knowledge、.agents/docs/retrospective/patterns、.agents/docs/development-standards、.agents/docs/retrospective），完善L0→L1引用链；快速查找指南补充知识库入口。
- **v1.1** (2026-06-30): 添加三层架构声明，明确本文件为L1索引层；新增会话启动协议条目；修正计数（protocols: 7, rules: 7）。
- **v1.0** (2026-06-29): 初始版本，手动创建。基于实际目录扫描整理，覆盖scripts/skills/commands/workflows四大类能力。
- **待实现**：`generate-capability-registry.py` 自动生成脚本，将在后续版本中实现自动扫描与本文件更新。


---

## 相关模式


← 上一章: [命令集、工作流、协议、规则索引](03-commands-workflows-protocols-rules.md) | **[返回索引](../capability-registry.md)**
