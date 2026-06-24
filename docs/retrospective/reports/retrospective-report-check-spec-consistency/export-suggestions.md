+++
id = "retrospective-report-check-spec-consistency-export"
date = "2026-06-23"
type = "export-suggestions"
source = "docs/retrospective/reports/retrospective-report-check-spec-consistency.md#四、导出环节"
+++

# 导出建议

## 4.1 改进建议

### 4.1.1 针对存在问题的改进措施

| 存在问题                     | 改进措施                                                                                     | 预期效果                           |
| ---------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------- |
| 正则解析的边界 case 脆弱性   | 添加解析器单元测试，覆盖边界 case（格式变体、特殊字符、空文件等）；考虑引入 `mistune` 作为 fallback | 提升解析器鲁棒性，格式变更时快速发现 |
| 复盘语境检测的误判风险       | ✅ 已于 v1.2 解决：`detect_meta_document()` 实现显式标记 + 关键词兜底，消除假阳性/假阴性 | 检测准确率 100%（显式标记），向后兼容 |
| 路径前缀白名单的维护成本     | 从项目根目录自动发现顶级目录列表，动态生成 `PROJECT_ROOT_PREFIXES`                             | 消除手动维护，项目结构变更时自动适配 |
| 需求变更检测功能未实现       | 实现 `check_requirement_changes()` 函数，通过 `git diff` 对比两个版本的 spec.md                | 补齐 spec 中定义的全部需求          |
| 语义匹配的精度局限           | 调研轻量级中文词向量模型（如 `text2vec-base-chinese`），评估引入可行性与成本                    | 从"关键词匹配"升级为"语义匹配"      |

### 4.1.2 流程优化建议

1. **引入"检查结果基线"机制**：将首次检查结果保存为基线，后续检查与基线对比，仅报告增量变化。避免每次检查都输出大量已知的警告。
2. **引入"严重级别"分类**：在当前的"通过/警告/错误"三级基础上，增加"严重级别"（如严重错误→阻塞合并，一般错误→建议修复，警告→知情即可），支持 CI 中的差异化门禁策略。
3. **建立 spec 模板规范**：在 `.agents/templates/` 中提供 spec.md、tasks.md、checklist.md 的标准化模板，明确命名约定（如 Requirement 标题格式、Task 标题格式），减少解析器的格式兼容负担。

### 4.1.3 工具链完善建议

1. **开发 spec 初始化脚手架**：`scaffold-spec.ps1` 脚本，一键创建 `.trae/specs/<name>/` 目录并生成 spec.md、tasks.md、checklist.md 的模板文件。
2. **开发 spec 健康仪表盘**：收集所有 spec 目录的检查结果，生成 HTML 仪表盘，可视化每个 spec 的一致性状态。
3. **与 pre-commit hook 集成**：在现有 `pre-commit` hook 中增加 `check-spec-consistency.py` 调用，在提交前自动检查规格文档一致性。

## 4.2 行动计划

| 优先级 | 改进项                    | 具体措施                                                                                              | 责任方 | 建议时间节点 | 状态     |
| ------ | ------------------------- | ----------------------------------------------------------------------------------------------------- | ------ | ------------ | -------- |
| 高     | 需求变更检测功能实现      | 实现 `check_requirement_changes()` 函数，支持 `--diff` 参数，通过 `git diff` 检测变更                   | 开发者 | 1 周内       | 未开始    |
| 高     | 复盘语境标记显式化        | 为 `retrospective-agents-spec-system/spec.md` 添加 `type: retrospective` 标记，修改检测逻辑优先使用显式标记 | 架构师 | 1 周内       | ✅ 已完成   |
| 高     | CI/CD 集成                | 将 `check-spec-consistency.py` 集成到 pre-commit hook 或 CI 流水线中                                   | 开发者 | 1 周内       | 未开始    |
| 中     | 路径前缀自动发现          | 实现 `discover_project_dirs()` 函数，从项目根目录自动生成前缀白名单，与手动白名单合并使用                 | 开发者 | 2 周内       | 未开始    |
| 中     | 解析器单元测试            | 为 `parse_spec()`、`parse_tasks()`、`parse_checklist()` 添加单元测试，覆盖正常 case 和边界 case          | 开发者 | 2 周内       | 未开始    |
| 中     | 检查结果基线机制          | 支持 `--baseline` 参数，保存/加载基线，仅报告增量变化                                                  | 开发者 | 2 周内       | 未开始    |
| 低     | 语义匹配升级调研          | 调研 `text2vec-base-chinese` 等中文词向量模型，评估引入的复杂度、性能、准确率收益                        | 架构师 | 1 个月内     | 未开始    |
| 低     | spec 初始化脚手架         | 开发 `scaffold-spec.ps1` 脚本，一键创建 spec 目录和模板文件                                            | 开发者 | 1 个月内     | 未开始    |
| 低     | spec 健康仪表盘           | 开发 HTML 仪表盘生成脚本，收集所有 spec 的检查结果并可视化                                              | 开发者 | 1 个月内     | 未开始    |

### 已完成条目说明

**复盘语境标记显式化**已于 v1.2 中完成，核心变更如下：

- 用 `detect_meta_document()` 替代 `is_retrospective_context()`，实现"显式标记优先 + 关键词兜底"双层识别策略
- 支持 `<!-- meta_type: retrospective -->` HTML 注释作为显式标记（零误判）
- 关键词列表扩展至 14 个（复盘、回顾、审计、评审、评估、对比分析、迁移方案等），保持向后兼容
- 为 `retrospective-agents-spec-system/spec.md` 添加显式标记
- 警告消息从"疑似引用被复盘项目数据"调整为"疑似引用外部项目数据（元文档）"
- 对 4 个 spec 目录回归验证，行为与 v1.1 一致，无新增误报

## 4.3 后续优化方向

### 4.3.1 中长期优化路线图

```mermaid
flowchart TD