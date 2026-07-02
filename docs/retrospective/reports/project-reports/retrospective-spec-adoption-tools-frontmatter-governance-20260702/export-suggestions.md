---
id: "retrospective-spec-adoption-tools-20260702-export"
title: "规范度量工具与Frontmatter治理复盘导出建议"
source: "session:spec-adoption-tools-frontmatter"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-spec-adoption-tools-frontmatter-governance-20260702/export-suggestions.toml"
---
# 导出建议

## 导出清单

### 核心交付物

| 文件 | 类型 | 导出目标 |
|------|------|---------|
| [README.md](README.md) | 复盘索引 | 项目报告库归档 |
| [execution-retrospective.md](execution-retrospective.md) | 执行过程复盘 | 项目报告库归档 |
| [insight-extraction.md](insight-extraction.md) | 洞察萃取报告 | 项目报告库归档 |

### 需要更新的关联资产

| 资产 | 更新内容 | 优先级 |
|------|---------|--------|
| [gitignore-validation.md](file:///d:/spaces/SpecWeave/docs/retrospective/patterns/code-patterns/gitignore-validation.md) | 补充.pytest_cache/案例和"新工具引入Checklist" | P0 |
| [cross-platform-encoding-enforcement.md](file:///d:/spaces/SpecWeave/docs/retrospective/patterns/code-patterns/cross-platform-encoding-enforcement.md) | 补充Python stdin-bytes修复方案 | P1 |
| [check-spec-adoption.py](file:///d:/spaces/SpecWeave/.agents/scripts/check-spec-adoption.py) | 添加--profile参数支持目录类型自适应权重 | P0 |
| project-reports/README.md | 添加本次复盘索引 | P2 |

## 行动项追踪

| # | 行动项 | 负责人 | 验收标准 | 建议完成时间 |
|---|--------|--------|---------|-------------|
| 1 | 增强check-spec-adoption.py添加--profile参数 | AI | --profile docs/specs/code可用，权重自动调整 | 下次度量前 |
| 2 | 更新gitignore-validation模式补充新工具Checklist | AI | 模式文档包含新增工具→检查产出物→更新.gitignore流程 | 下次工具引入前 |
| 3 | 更新cross-platform-encoding模式补充stdin-bytes方案 | AI | 模式文档包含Python subprocess stdin-bytes代码示例 | 下次Windows提交时 |
| 4 | 增强add-agents-frontmatter.py添加格式校验 | AI | 自动检测TOML/YAML混合语法并报错 | 下次批量补全时 |

## 模式沉淀建议

本次复盘中的洞察1（度量工具排除机制）和洞察4（指标目录自适应权重）具有较高的模式价值，建议沉淀为tools-automation类新模式：

- **工作名**：metric-tool-exclusion-profiling（度量工具排除与配置画像）
- **成熟度**：L1（已有一次实践验证）
- **核心问题**：递归扫描类工具如何处理非目标文件和目录类型差异
- **解决方案**：内置exclude参数+按目录类型预设配置画像（profile）

建议在下一次复盘周期完成模式入库。
