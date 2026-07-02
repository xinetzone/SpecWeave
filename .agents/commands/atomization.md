---
id: "atomization"
title: "原子化指令集"
source: "AGENTS.md#原子化指令"
x-toml-ref: "../../.meta/toml/.agents/commands/atomization.toml"
---
# 原子化指令集

## 触发条件

- 文档内容过多，需要拆分
- 代码文件过大，职责不单一
- 新功能开发前的架构设计
- 重构现有代码或文档结构
- 自我萃取模块识别到可拆分内容

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| target_type | string | 是 | 目标类型：`document`/`code`/`config` |
| source_path | string | 是 | 源文件路径 |
| split_strategy | string | 否 | 拆分策略：`topic`/`function`/`module`/`component` |
| max_size | number | 否 | 最大文件大小（字符数），默认 5000 |
| min_size | number | 否 | 最小文件大小（字符数），默认 500 |
| preserve_links | boolean | 否 | 是否保留链接引用，默认 `true` |

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，拥有最终决策权，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| 原子化核心活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 触发原子化与目标确认 | **R/A** | C | C | C | C | I |
| 源文件分析（步骤1） | R | **A** | C | C | I | I |
| 拆分方案制定（步骤2） | R | **A** | C | C | I | I |
| 执行拆分（步骤3） | I | C | **R** | **A** | I | I |
| 引用更新（步骤4） | I | C | **R** | **A** | I | I |
| 完整性验证与收尾脚本（步骤5） | C | I | R | **A** | C | I |
| 归档与通知（步骤6） | **R/A** | I | C | I | I | I |
| 原子化质量验收 | C | C | I | **R/A** | I | I |
| 跨模块原子化审批（常规） | R | C | I | **A** | I | I |
| 跨模块原子化审批（重大架构调整） | R | C | I | C | I | **A** |

### 审批权限边界

- **文档原子化（单目录内）**：architect审批拆分方案，reviewer负责质量验收
- **代码原子化**：architect审批拆分方案，reviewer+architect双重验收（架构+质量）
- **跨模块/跨目录原子化**：常规由reviewer审批；涉及重大架构调整时升级至co-founder审批
- **过度拆分审查**：reviewer负责判断是否碎片化，architect提供架构合理性输入
- **收尾脚本执行异常**：developer负责排查，architect参与技术问题定位，orchestrator协调

## 执行步骤

### 步骤 1：分析源文件

- 识别文件的核心主题与职责
- 分析内容结构与依赖关系
- 评估文件大小与复杂度
- 识别可拆分的独立单元

### 步骤 2：制定拆分方案

- 确定拆分策略与拆分点
- 规划新文件的命名与路径
- 设计文件间的引用关系
- 制定链接更新方案

### 步骤 3：执行拆分

- 创建新的原子文件
- 迁移对应内容至新文件
- 添加必要的 frontmatter
- 更新文件间的交叉引用

### 步骤 4：更新引用

- 更新源文件中的内部链接
- 更新其他文件对源文件的引用
- 维护目录索引与导航表
- 更新知识资产索引

### 步骤 5：验证完整性

- 检查所有链接是否有效
- 验证内容无丢失或重复
- 确认文件命名符合规范
- 运行相关测试确保功能正常
- **运行一键收尾脚本**：执行 `python .agents/scripts/finalize-atomization.py` 自动修复断链、更新导航表与 Spec 看板

```bash
# 预览收尾操作（不修改文件）
python .agents/scripts/finalize-atomization.py --dry-run

# 执行完整收尾（自动修复断链、更新导航与看板）
python .agents/scripts/finalize-atomization.py
```

### 步骤 6：归档与通知

- 归档拆分记录至变更日志
- 通知相关角色变更内容
- 同步至自我萃取模块
- 更新系统状态

## 输出规范

| 产出物 | 格式 | 存储位置 |
|--------|------|---------|
| 原子化文件 | Markdown / Code | 按拆分方案的目标路径 |
| 拆分记录 | Markdown | `docs/retrospective/changes/` |
| 更新后的引用 | Markdown | 相关文件 |
| 验证报告 | Markdown | 临时文件 |

## 质量验收

- 每个原子文件只包含单一主题或功能
- 文件大小在合理范围内（500-5000 字符）
- 所有链接有效，无死链
- 内容无丢失，无重复
- 功能测试通过（代码原子化）

## 约束条件

- 拆分后文件必须保持语义完整性
- 避免过度拆分导致文件碎片化
- 代码拆分需保持接口兼容性
- 文档拆分需保持逻辑连贯性
- 拆分操作不影响现有功能

## 原子化原则

### 文档原子化

- 每个文档只讨论一个主题
- 标题层级清晰，结构合理
- 避免超长文档（建议 ≤ 5000 字符）
- 相关主题通过链接关联

### 代码原子化

- 每个函数/类只负责一个功能
- 文件大小控制在合理范围
- 模块职责单一，高内聚低耦合
- 接口设计清晰，易于理解

## 关联资源

- [自我萃取模块](../modules/self-extraction.md)
- [自我迭代模块](../modules/self-iteration.md)
- [文件命名规范](../rules/file-naming-convention.md)