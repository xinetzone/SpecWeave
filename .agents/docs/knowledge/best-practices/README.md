---
id: "best-practices-index"
title: "团队最佳实践库"
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/best-practices/README.toml"
category: "best-practices"
date: "2026-07-09"
---
# 团队最佳实践库

## 🎯 八维检查法核心概念

> **八维检查法**是并发代码安全审查的结构化检查框架，源自并发安全检查器开发实战，将并发安全检查从"凭经验排查"升级为"按维度系统扫描"。

### 三级严重度分级

| 级别 | 维度 | 数量 | 说明 |
|------|------|------|------|
| 🔴 error | TIMEOUT / IDEMPOTENT / DEADLOCK / LEAK | 4个 | 必须修复，否则存在生产事故风险 |
| 🟡 warn | BOUNDARY / DEFENSIVE / CONFIG | 3个 | 建议修复，影响健壮性与可维护性 |
| 🟢 info | I18N | 1个 | 可选优化，涉及国际化场景时关注 |

### 核心原则

> **"测试通过是最低标准，不是完成标准"**
>
> 行覆盖率100% ≠ 路径覆盖完整。并发/分布式系统的Bug往往出现在异常路径和边界条件，测试通过只能证明"测试覆盖到的路径正确"，不能证明"所有路径正确"。

### 反模式检测覆盖

共覆盖 **12类并发反模式** 检测，包括但不限于：无超时锁、非幂等操作、循环等待死锁、资源泄漏、N≥3边界缺失、外部可变引用、硬编码阈值、中英文分词问题等。

---

## 📋 关键应用场景

| 场景 | 说明 |
|------|------|
| 🔍 并发模块代码审查 | 锁/资源分配/多参与者状态机类代码的结构化审查Checklist |
| 🪝 pre-commit 钩子自动化检查 | 集成到CI/CD流水线，提交前自动扫描并发反模式 |
| 📊 调度/负载均衡类模块N-scaling测试矩阵设计 | N=0/1/2/3/5/10六档测试规模，N=3为关键边界 |
| ✅ 通用代码审查Checklist | 八维框架可扩展至非并发模块的防御性编程审查 |

---

## 🚀 5分钟快速上手

1. **Step 1**: 阅读本README了解全貌（2分钟）
2. **Step 2**: 按需选择对应文档深入阅读（根据下方「快速导航」按场景选择）
3. **Step 3**: 结合具体任务参考实践指南（Checklist/模板直接套用）
4. **Step 4**: 自动化工具集成（pre-commit链、check脚本接入流水线）

---

## 📚 最佳实践文档索引

| 文档 | 一句话摘要 | 适用场景标签 |
|------|-----------|-------------|
| [concurrent-code-safety-review.md](concurrent-code-safety-review.md) | 并发代码安全审查与Bug修复闭环指南（含六维检查法、N-scaling测试矩阵、1+N+1闭环公式） | `concurrency` `code-review` `bug-fix` `checklist` |
| [eight-dimensions-concurrent-safety-spec.md](eight-dimensions-concurrent-safety-spec.md) | 并发安全八维检查法技术规格（12类反模式检测规则与消歧策略） | `concurrency` `static-analysis` `specification` `anti-pattern` |
| [ast-static-analysis-disambiguation.md](ast-static-analysis-disambiguation.md) | Python AST静态分析五类消歧法（降低误报的核心策略） | `AST` `static-analysis` `python` `false-positive` |
| [cli-setup-in-agent-environment.md](cli-setup-in-agent-environment.md) | IDE Agent环境下CLI工具配置四步法（安装验证→沙箱预判→非交互认证→配置验证） | `cli` `setup` `agent-environment` `sandbox` `newbie-guide` |
| [mermaid-guide.md](mermaid-guide.md) | Mermaid图表一站式操作手册（安全编码六规则+自动检查工具） | `mermaid` `visualization` `ci` `安全编码` |
| [multi-file-edit-reliability.md](multi-file-edit-reliability.md) | 多文件编辑操作可靠性指南（级联编号成本/Edit工具陷阱/串行vs并行策略） | `edit` `multi-file` `reliability` `tool-pitfalls` |
| [parser-complexity-budget.md](parser-complexity-budget.md) | Parser复杂度预算Checklist（三层架构/20+边界case测试/时间预算预估） | `parser` `complexity-budget` `TDD` `semi-structured-parsing` |
| [pattern-validation-v3-template-batch-upgrade.md](pattern-validation-v3-template-batch-upgrade.md) | 方法论模式验证报告（分类处置决策树+三阶段渐进推广验证） | `pattern-validation` `governance` `batch-upgrade` `phased-rollout` |
| [git-hook-chain-architecture.md](git-hook-chain-architecture.md) | 链式pre-commit钩子架构实践（跨平台Shell入口+Python链式主入口模式） | `git-hooks` `pre-commit` `architecture` `cross-platform` `automation` |
| [b2b-product-info-collection-sop.md](b2b-product-info-collection-sop.md) | B2B/旗舰产品信息源分层采集规范（五层信息源优先级策略） | `信息采集` `B2B` `SOP` `多源验证` `Defuddle` |
| [ai-anthropomorphic-crisis-intervention-implementation.md](ai-anthropomorphic-crisis-intervention-implementation.md) | AI拟人化互动服务极端情绪干预机制技术实施方案（合规方案） | `合规` `安全` `AI安全` `危机干预` |
| [symbol-visibility-control.md](symbol-visibility-control.md) | C/C++共享库符号可见性控制最佳实践（--exclude-libs,ALL精确控制、静态注册保护、5大反模式） | `C/C++` `linker` `symbol-visibility` `shared-library` `LLVM` `TVM` `CMake` |
| [trae-agent-sandbox-guide.md](trae-agent-sandbox-guide.md) | TRAE Agent 沙箱配置与使用最佳实践指南（运行模式选择、白名单策略、sandbox.json模板、网络控制、场景实践） | `sandbox` `security` `agent-environment` `configuration` `trae` `newbie-guide` |
| [python-version-upgrade-compatibility-check.md](python-version-upgrade-compatibility-check.md) | Python大版本升级破坏性变更检查清单（multiprocessing默认行为变更、弃用/移除模块、AST节点变更、checklist） | `Python` `version-upgrade` `compatibility` `multiprocessing` `breaking-changes` |
| [compiled-package-data-file-lifecycle.md](compiled-package-data-file-lifecycle.md) | 编译型Python包数据文件生命周期管理（Nuitka/Cython数据文件复制、wheel验证、运行时环境变量设置） | `Python` `Nuitka` `Cython` `wheel` `data-files` `packaging` `TVM` |
| [docker-declarative-first-principle.md](docker-declarative-first-principle.md) | Docker镜像更新的声明式优先原则（Dockerfile vs docker commit对比、显式ENTRYPOINT/CMD设置、构建决策指南） | `Docker` `Dockerfile` `declarative` `image-build` `containerization` |
| [wrapper-script-injection-pattern.md](wrapper-script-injection-pattern.md) | Wrapper脚本注入模式（编译型包运行时兼容性修复、runpy.run_path透明转交、过渡性修复策略） | `Python` `wrapper` `runpy` `compiled-package` `runtime-patch` `compatibility` |

---

## 🧭 快速导航（按场景分组）

| 场景分类 | 推荐阅读路径 |
|---------|-------------|
| 🔧 工具链/环境配置 | [cli-setup-in-agent-environment.md](cli-setup-in-agent-environment.md) → [trae-agent-sandbox-guide.md](trae-agent-sandbox-guide.md) |
| 🧵 并发编程 | [concurrent-code-safety-review.md](concurrent-code-safety-review.md) → [eight-dimensions-concurrent-safety-spec.md](eight-dimensions-concurrent-safety-spec.md) → [ast-static-analysis-disambiguation.md](ast-static-analysis-disambiguation.md) |
| 📊 文档/可视化 | [mermaid-guide.md](mermaid-guide.md) |
| ✏️ 编辑/重构 | [multi-file-edit-reliability.md](multi-file-edit-reliability.md) |
| 🔍 Parser开发 | [parser-complexity-budget.md](parser-complexity-budget.md) |
| 🪝 Git钩子 | [git-hook-chain-architecture.md](git-hook-chain-architecture.md) |
| 📋 信息采集 | [b2b-product-info-collection-sop.md](b2b-product-info-collection-sop.md) |
| 🛡️ 合规安全 | [ai-anthropomorphic-crisis-intervention-implementation.md](ai-anthropomorphic-crisis-intervention-implementation.md) |
| 📐 方法论治理 | [pattern-validation-v3-template-batch-upgrade.md](pattern-validation-v3-template-batch-upgrade.md) |
| 🐍 Python升级 | [python-version-upgrade-compatibility-check.md](python-version-upgrade-compatibility-check.md) |
| 📦 编译包管理 | [compiled-package-data-file-lifecycle.md](compiled-package-data-file-lifecycle.md) |
| 🐳 Docker构建 | [docker-declarative-first-principle.md](docker-declarative-first-principle.md) |
| 🧩 兼容性修复 | [wrapper-script-injection-pattern.md](wrapper-script-injection-pattern.md) |

---

## 🔗 相关资源

- [📁 复盘报告目录](../../retrospective/reports/README.md) - 最佳实践的原始复盘来源
- [📁 可复用模式库](../../retrospective/patterns/README.md) - 提炼后的可复用架构/代码/方法论模式
- [🏠 知识库首页](../README.md) - 返回知识库总入口
