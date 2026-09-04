# Caffe 全面复盘+洞察+萃取+导出 Spec

## Why

Caffe Protobuf 最小化包装项目（`external/chaos/caffe/`）已完成全部核心功能开发（protobuf 库、TVM 算子桥接、模型标准化工具链、架构深度分析），并已生成一份全面的复盘报告（`task-summary-caffe-proto-20260722.md`，10章约5000字）。但该报告当前存放在项目内部的 `.agents/` 目录，尚未按照 SpecWeave 标准复盘报告格式导出到 `docs/retrospective/reports/` 归档目录，也未完成洞察萃取和导出建议的原子化拆分。

## What Changes

- 将现有 `task-summary-caffe-proto-20260722.md` 复盘报告按标准格式导出到 `docs/retrospective/reports/task-reports/retrospective-caffe-proto-20260722/`
- 按 SpecWeave 复盘报告三件套标准拆分：`README.md`（主报告）+ `insight-extraction.md`（洞察萃取）+ `export-suggestions.md`（导出建议）
- 对报告中已提炼的 3 个方法论和 4 个最佳实践进行洞察萃取，补充反模式、边界条件、可迁移性验证
- 提供后续改进行动项的导出建议（优先级排序、风险预警、工具推荐）
- 更新 `docs/retrospective/reports/task-reports/README.md` 索引

## Impact

- Affected specs: 无（新建归档任务）
- Affected code: 无代码变更，纯文档操作
- 涉及文件：
  - 源文件：`external/chaos/caffe/.agents/task-summary-caffe-proto-20260722.md`
  - 目标目录：`.agents/docs/retrospective/reports/task-reports/retrospective-caffe-proto-20260722/`
  - 索引文件：`.agents/docs/retrospective/reports/task-reports/README.md`

## ADDED Requirements

### Requirement: 复盘报告导出
系统 SHALL 将 Caffe 项目的全面复盘报告从项目内部 `.agents/` 目录导出到 SpecWeave 标准复盘报告归档目录，按三件套格式拆分。

#### Scenario: 成功导出三件套
- **WHEN** 执行导出流程
- **THEN** 在目标目录生成 `README.md`（主报告）、`insight-extraction.md`（洞察萃取）、`export-suggestions.md`（导出建议）三个文件
- **THEN** 主报告保留原有 10 章结构，补充 frontmatter 元数据
- **THEN** 洞察萃取文件从主报告第9章提炼≥3个方法论模式，每个含反模式、边界条件、可迁移性验证
- **THEN** 导出建议文件从主报告第10章提炼优先级排序、风险矩阵、工具推荐

### Requirement: 索引同步
系统 SHALL 在导出完成后更新 `docs/retrospective/reports/task-reports/README.md` 索引，添加新报告的条目。

#### Scenario: 索引更新
- **WHEN** 导出完成
- **THEN** 索引文件中新增 retrosp-spective-caffe-proto-20260722 条目
- **THEN** 条目包含报告名称、日期、简要说明和链接

### Requirement: 链接验证
系统 SHALL 确保导出文件中的所有交叉引用链接有效，无断链。

#### Scenario: 链接有效性
- **WHEN** 导出完成后执行链接检查
- **THEN** 所有内部链接（相对路径）指向存在的文件
- **THEN** 无 `file:///` 绝对路径格式的链接

## REMOVED Requirements

无

## MODIFIED Requirements

无