---
id: "capability-registry-scripts"
title: "脚本索引"
source: "capability-registry.md#01-scripts"
x-toml-ref: "../../.meta/toml/.agents/capability-registry/01-scripts.toml"
---
# 脚本索引


### ✅ 检查/验证类（Check & Validate）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| check-links.py | Markdown链接有效性校验与自动修复（本地文件+外部URL） | "检查链接"、"修复链接"、"断链" | 读+修复 | ✅ | [scripts/check-links.py](../scripts/check-links.py) |
| check-skill-quality.py | Skill质量检查：验证SKILL.md是否符合五要素模型规范 | "检查Skill"、"验证Skill质量"、"五要素检查" | 只读 | ✅ | [scripts/check-skill-quality.py](../scripts/check-skill-quality.py) |
| check-stage-guardrails.py | 阶段守卫日志离线分析：检测SG-LOG/PDR-LOG的拦截/跳转/缺失异常 | "分析阶段守卫日志"、"SG日志分析"、"检查SG-LOG" | 只读 | ✅ | [scripts/check-stage-guardrails.py](../scripts/check-stage-guardrails.py) |
| check-stage-guardrail-runtime.py | 阶段守卫运行时强制执行与拦截演示 | "阶段守卫运行时"、"SG运行时检查" | 只读 | ✅ | [scripts/check-stage-guardrail-runtime.py](../scripts/check-stage-guardrail-runtime.py) |
| check-source-traceability.py | 派生产物溯源检查：扫描frontmatter的source字段，建立反向索引 | "溯源检查"、"派生产物检查"、"source字段检查" | 只读 | ✅ | [scripts/check-source-traceability.py](../scripts/check-source-traceability.py) |
| check-move.py | 文件移动路径迁移工具：移动文件后批量修正引用路径 | "移动文件"、"迁移路径"、"修复引用路径" | 写 | ✅ | [scripts/check-move.py](../scripts/check-move.py) |
| check-duplication.py | 跨文件重复代码检测 | "检查重复代码"、"重复检测" | 只读 | ✅ | [scripts/check-duplication.py](../scripts/check-duplication.py) |
| check-action-items.py | 扫描复盘报告中的行动计划表，提取待办清单 | "检查行动项"、"待办清单"、"行动项状态" | 只读 | ✅ | [scripts/check-action-items.py](../scripts/check-action-items.py) |
| check-atomization-coverage.py | 原子化前置检查：搜索模式库判断新洞察是否已被覆盖 | "原子化检查"、"模式覆盖检查"、"创建模式前检查" | 只读 | ✅ | [scripts/check-atomization-coverage.py](../scripts/check-atomization-coverage.py) |
| check-atomization-duplication.py | 原子化后内容一致性检查：检测源文件残留的深度分析内容 | "原子化一致性检查"、"残留内容检查" | 只读 | ✅ | [scripts/check-atomization-duplication.py](../scripts/check-atomization-duplication.py) |
| check-pattern-quality.py | 方法论模式文档质量检查 | "模式质量检查"、"验证模式文档" | 只读 | ✅ | [scripts/check-pattern-quality.py](../scripts/check-pattern-quality.py) |
| check-report-categorization.py | 复盘报告归类验证：检查reports/下未归类报告 | "报告归类"、"检查报告分类" | 只读 | ✅ | [scripts/check-report-categorization.py](../scripts/check-report-categorization.py) |
| check-retrospective-index.py | Retrospective体系索引一致性检查 | "索引一致性"、"检查复盘索引" | 只读 | ✅ | [scripts/check-retrospective-index.py](../scripts/check-retrospective-index.py) |
| check-raci-compliance.py | RACI责任分配矩阵合规性检查（A唯一性、R≠A分离、角色列完整性） | "检查RACI"、"RACI合规"、"责任分配矩阵" | 只读 | ✅ | [scripts/check-raci-compliance.py](../scripts/check-raci-compliance.py) |
| check-hardcode.py | Python代码硬编码检测（基于AST，支持8类硬编码：URL/路径/字符串/数值/配置/编码/正则/样式） | "硬编码检查"、"检测硬编码"、"hardcode" | 只读 | ✅ | [scripts/check-hardcode.py](../scripts/check-hardcode.py) |
| repo-check.py | 综合检查统一入口（整合filename/gitignore/mermaid/vendor/roles五项检查） | "综合检查"、"多项目检查" | 只读 | ✅ | [scripts/repo-check.py](../scripts/repo-check.py) |
| spec-tool.py | Spec工具统一入口（整合check/format两项检查） | "Spec检查"、"Spec格式" | 只读 | ✅ | [scripts/spec-tool.py](../scripts/spec-tool.py) |

> **向后兼容包装脚本**（以下脚本为薄包装层，转发到 repo-check.py / spec-tool.py 对应子命令）：
> - `check-gitignore.py` → `repo-check.py gitignore`
> - `check-vendor.py` → `repo-check.py vendor`
> - `check-filename-convention.py` → `repo-check.py filename`
> - `check-mermaid.py` → `repo-check.py mermaid`
> - `check-role-permissions.py` → `repo-check.py roles`
> - `check-spec-consistency.py` → `spec-tool.py check`
> - `check-spec-format.py` → `spec-tool.py format`

#### 核心治理脚本用法示例

**check-raci-compliance.py** — RACI责任分配矩阵合规性检查

```bash
# 扫描目录（检查目录下所有含RACI矩阵的Markdown文件）
python .agents/scripts/check-raci-compliance.py --path .agents/rules
python .agents/scripts/check-raci-compliance.py --path .agents/commands

# 检查单个文件
python .agents/scripts/check-raci-compliance.py -f .agents/commands/file-creation.md

# 显示通过项详情（verbose模式）
python .agents/scripts/check-raci-compliance.py --path .agents/commands -v

# JSON格式输出（供自动化工具消费）
python .agents/scripts/check-raci-compliance.py --path .agents/rules --json

# 自定义评分阈值（低于阈值返回exit code 1，默认80）
python .agents/scripts/check-raci-compliance.py --path .agents/commands --threshold 90
```

检查项包括：A唯一性（每行有且仅有一个A）、R≠A分离（执行者不能自审批）、角色列完整性（6个标准角色列：orchestrator/architect/developer/reviewer/tester/co-founder）、co-founder审批范围合理性。质量分满分100，error扣分，warn仅提示。

**check-hardcode.py** — Python代码硬编码检测（基于AST）

```bash
# 扫描目录（递归扫描目录下所有.py文件）
python .agents/scripts/check-hardcode.py --path .agents/scripts

# 检查单个文件
python .agents/scripts/check-hardcode.py -f .agents/scripts/forum-bot.py

# 详细模式（显示所有issue包括info级别的提示）
python .agents/scripts/check-hardcode.py --path .agents/scripts -v

# JSON格式输出（供CI/自动化工具消费）
python .agents/scripts/check-hardcode.py --path .agents/scripts --json

# 自定义评分阈值（低于阈值返回exit code 1，默认70）
python .agents/scripts/check-hardcode.py --path .agents/scripts --threshold 60
```

检测覆盖8类硬编码：HARD-URL（外部URL端点）、HARD-PATH（绝对文件路径）、HARD-CFG（超时/重试/端口等配置参数）、HARD-STR（raise中的中文消息）、HARD-NUM（魔数）、HARD-ENC（非标准编码）、HARD-MIME（硬编码MIME类型）、HARD-REGEX（硬编码正则）。自动过滤：docstring、argparse帮助文本、test_函数、localhost/127.0.0.1本地URL、utf-8标准编码、HTTP状态码、哨兵值(-1/0/1)、User-Agent字符串、f-string路径片段、项目相对路径。误报规则自动从 `.agents/config/false-positive-rules.toml` 加载。

### 🔧 生成/构建类（Generate & Build）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| docgen.py | 文档索引与看板生成统一工具（nav/dashboard/apps/all 子命令），标记区域覆盖，幂等 | "生成导航"、"生成看板"、"生成应用索引"、"更新文档索引"、"docgen" | 写（标记区域） | ✅ Git-based预览 | [scripts/docgen.py](../scripts/docgen.py) |
| finalize-atomization.py | 原子化一键收尾：断链修复+导航更新+看板刷新，支持dry-run | "收尾原子化"、"原子化完成"、"断链修复导航更新" | 写 | ✅ | [scripts/finalize-atomization.py](../scripts/finalize-atomization.py) |
| generate-tests.py | 测试骨架自动生成 | "生成测试"、"测试骨架" | 写 | ✅ | [scripts/generate-tests.py](../scripts/generate-tests.py) |
| generate-sg-dashboard.py | 阶段守卫日志聚合可视化仪表盘（HTML输出） | "SG仪表盘"、"日志可视化"、"阶段守卫仪表盘" | 写 | ✅ | [scripts/generate-sg-dashboard.py](../scripts/generate-sg-dashboard.py) |
| build-ref-index.py | 构建文件引用反向索引：{目标文件: [引用文件列表]} | "引用索引"、"反向索引"、"谁引用了这个文件" | 只读 | ✅ | [scripts/build-ref-index.py](../scripts/build-ref-index.py) |
| agents.py | 新项目脚手架初始化工具（init子命令） | "初始化项目"、"项目脚手架" | 写 | ❌ | [scripts/agents.py](../scripts/agents.py) |

> **向后兼容包装脚本**（已整合进 docgen.py）：
> - `generate-nav.py` → `docgen.py nav`
> - `generate-dashboard.py` → `docgen.py dashboard`
> - `generate-apps-index.py` → `docgen.py apps`

### 📊 统计/分析类（Stats & Analysis）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| pattern-maturity.py | 模式成熟度管理（verify/upgrade/batch-upgrade子命令） | "模式成熟度"、"升级成熟度" | 只读+建议 | ✅ | [scripts/pattern-maturity.py](../scripts/pattern-maturity.py) |
| pattern-maturity-stats.py | 模式成熟度统计报告 | "成熟度统计"、"模式统计" | 只读 | ✅ | [scripts/pattern-maturity-stats.py](../scripts/pattern-maturity-stats.py) |
| scan-maturity-upgrades.py | 扫描可升级成熟度的模式 | "扫描升级"、"成熟度扫描" | 只读 | ✅ | [scripts/scan-maturity-upgrades.py](../scripts/scan-maturity-upgrades.py) |

### 🤖 自动化操作类（Automation）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| forum-bot.py | Discourse论坛（forum.trae.cn）自动化脚本 | "论坛脚本"、"forum-bot"、"发帖脚本" | 读+写 | ✅ | [scripts/forum-bot.py](../scripts/forum-bot.py) |
| trae_edge_case_handler/ | Trae IDE边界情况处理（论坛/工具链/Work等） | "Trae边界处理"、"edge case" | 读+写 | ✅ | [scripts/trae_edge_case_handler/](../scripts/trae_edge_case_handler/README.md) |

### 🔧 工具/一次性修复类（Utilities）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| fix-flexloop-reverse-links.py | 修复flexloop子模块反向链接（一次性工具） | "修复flexloop链接" | 写 | ❌ | [scripts/fix-flexloop-reverse-links.py](../scripts/fix-flexloop-reverse-links.py) |

### 🚀 CI/流水线

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| ci-check.ps1 | Windows CI综合检查脚本（8步流水线：检查+文档生成） | "CI检查"、"提交前检查"、"全量检查"、"pre-commit" | 读+写（标记区域） | ✅ Git-based预览 | [scripts/ci-check.ps1](../scripts/ci-check.ps1) |
| ci-check.sh | Linux/Mac CI综合检查脚本（8步流水线） | "CI检查"、"提交前检查"、"全量检查" | 读+写（标记区域） | ✅ Git-based预览 | [scripts/ci-check.sh](../scripts/ci-check.sh) |

> **共享库**（非直接执行脚本，被其他脚本import）：
> - `lib/` — 共享工具库（CLI输出、frontmatter解析、Markdown处理、链接修复、模式扫描等）
> - `constants.py` — 脚本共用常量定义
> - `config/false-positive-rules.toml` — 误报规则配置

---


---

## 相关模式


**[返回索引](../capability-registry.md)** | 下一章 → [Skill索引](02-skills.md)
