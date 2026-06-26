+++
id = "export-suggestions"
source = "retrospective-mermaid-rendering-fix-20260626/README.md"
atomized = true
atomized_date = "2026-06-26"
suggestions_dir = "suggestions/"
+++

# 导出建议：Mermaid 渲染防护体系

> ✅ **原子化归档完成**：本文件可复用资产和优化建议已拆分为 4 个独立原子文件，存放在 [suggestions/](suggestions/) 目录。
>
> 本文件保留为导航索引，改进建议总览、行动计划执行状态和闭环检查清单保留于此，详细可复用资产内容请查阅各原子文件。

---

## 一、改进建议总览

| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| Mermaid 语法错误无法在提交前发现 | 新增 Mermaid 语法检查脚本 | 高 | 提交前自动拦截 Mermaid 渲染问题 | ✅ 已完成 |
| 开发者不了解 Mermaid 编码陷阱 | 将安全规则写入开发规范文档 | 高 | 从源头减少错误 Mermaid 代码 | ✅ 已完成 |
| 项目记忆中 Mermaid 规则不完整 | 更新 project_memory.md 补充完整规则 | 中 | 后续智能体自动遵循安全编码规范 | ✅ 已完成 |
| 全项目历史 Mermaid 代码未经安全审计 | 扫描并修复现有文档中的 Mermaid 问题 | 中 | 消除存量渲染风险 | ✅ 已完成 |

## 二、行动计划执行状态

### 高优先级（立即执行）

| 序号 | 改进项 | 具体措施 | 状态 |
|------|--------|---------|------|
| 1 | Mermaid 安全规则入项目记忆 | 更新 `project_memory.md`，添加「Mermaid 安全编码五规则」和陷阱速查表 | ✅ 已完成 |
| 2 | 开发规范补充 Mermaid 章节 | 在 `docs/development-standards.md` 中增加 Mermaid 编码规范章节 | ✅ 已完成（章节已存在，内容完整） |

### 中优先级（近期迭代）

| 序号 | 改进项 | 具体措施 | 状态 |
|------|--------|---------|------|
| 3 | 新增 Mermaid Lint 脚本 | 在 `.agents/scripts/` 下创建 `check-mermaid.py`，检测空行/未引号节点/裸中文ID/数字点列表触发 | ✅ 已完成 |
| 4 | 全项目 Mermaid 审计 | 运行 lint 脚本扫描全项目 `.md` 文件，修复存量问题 | ✅ 已完成（修复647个文件，0错误0警告） |

### 低优先级（长期优化）

| 序号 | 改进项 | 具体措施 | 状态 |
|------|--------|---------|------|
| 5 | CI 集成 Mermaid 检查 | 将 `check-mermaid.py` 集成到 `ci-check.ps1` / `ci-check.sh` 流水线 | ✅ 已完成 |
| 6 | Mermaid 节点模板 | 在 `.agents/templates/mermaid-templates/` 中创建常用 Mermaid 图表模板，内置安全格式 | ✅ 已完成 |

---

## 三、可复用资产导航

详细可复用资产已原子化拆分至 [suggestions/](suggestions/) 目录：

| 类型 | 原子文件 | 主题 |
|------|---------|------|
| 🆕 新模式候选 | [suggestions/pattern-mermaid-safe-coding-rules.md](suggestions/pattern-mermaid-safe-coding-rules.md) | Mermaid 安全编码五规则（L1） |
| 🆕 新模式候选 | [suggestions/pattern-mermaid-trap-cheatsheet.md](suggestions/pattern-mermaid-trap-cheatsheet.md) | Mermaid 常见陷阱速查表（L1） |
| 🔄 现有模式更新 | [suggestions/existing-pattern-updates.md](suggestions/existing-pattern-updates.md) | mermaid-layered-visualization 补充安全编码章节；root-cause-diagnosis 补充分层错误屏蔽概念 |
| 🔮 未来优化 | [suggestions/future-optimizations.md](suggestions/future-optimizations.md) | 工具链增强/模板化预防/跨渲染器测试/知识传播（4项） |

完整索引见：[suggestions/README.md](suggestions/README.md)

---

## 四、复盘闭环检查

- [x] 事实回顾完整，时间线清晰
- [x] 根因分析深入到知识缺口和工具链层面
- [x] 提炼出可复用的编码规则和排查方法
- [x] 改进建议具体可执行，包含优先级和时间计划
- [x] 识别了可入库的候选模式 → 已原子化至 [suggestions/](suggestions/)
- [x] 项目记忆更新（已完成）
- [x] 开发规范更新（已确认完整）
- [x] Mermaid Lint 脚本创建（已完成）
- [x] 全项目 Mermaid 审计（已完成，647个文件0错误0警告）
- [x] CI 集成 Mermaid 检查（已完成，集成到 ci-check.ps1 和 ci-check.sh）
- [x] Mermaid 节点模板（已完成，.agents/templates/mermaid-templates/ 下5种模板）

---

## 五、原子化说明

- **拆分时间**：2026-06-26
- **拆分策略**：按主题（topic）拆分，可复用资产和优化建议独立成文
- **原子文件数**：4 个建议文件 + 1 个索引文件
- **内容完整性**：行动计划总览和闭环检查保留在本文件，详细可复用资产迁移至 suggestions/
- **链接维护**：所有交叉引用已更新为相对路径

---
*所属报告：[Mermaid 渲染问题修复复盘](README.md)*
