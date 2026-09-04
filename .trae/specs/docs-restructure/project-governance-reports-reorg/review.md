---
version: "1.0"
date: "2026-06-26"
x-toml-ref: "../../../../.meta/toml/.trae/specs/docs-restructure/project-governance-reports-reorg/checklist.toml"
---
# project-governance 复盘报告系统性重组 - Verification Checklist

## 目录结构完整性

- [ ] 5 个主题子目录（comprehensive-reviews/, documentation-governance/, tools-and-automation/, process-and-compliance/, archiving-and-migration/）全部创建成功
- [ ] 18 个报告目录全部迁移至对应主题子目录，无遗漏
- [ ] reports-duplication-optimization-report.md 独立文件迁移至 documentation-governance/
- [ ] project-governance 根目录下无遗留的平铺报告（仅保留 5 个主题子目录和 README.md）
- [ ] 迁移后的文件总数与迁移前一致（无文件丢失）

## 主题分类准确性

- [ ] comprehensive-reviews/ 包含 3 份综合复盘报告（20260623、20260625、20260626 三个时间节点的全面复盘）
- [ ] documentation-governance/ 包含 6 份文档体系治理报告（重复优化、系统规划、品牌命名、洞察重组、链接修复、Mermaid修复）
- [ ] tools-and-automation/ 包含 2 份工具治理报告（工具熵优化、Code Wiki生成）
- [ ] process-and-compliance/ 包含 3 份流程合规报告（apps目录创建、建议执行、启动协议违反）
- [ ] archiving-and-migration/ 包含 4 份归档迁移报告（导出卡片、竹简悟道归档、xinet归档、Demo流程）
- [ ] 每份报告归入正确主题，分类符合 MECE 原则（无遗漏、无重叠）

## 文件内容完整性

- [ ] 所有 Markdown 文件的正文内容未被修改（仅路径引用相关行变更）
- [ ] 所有 TOML frontmatter 保持完整、格式正确
- [ ] Mermaid 代码块内容未被修改
- [ ] 原子化四件套结构（README.md + execution-retrospective.md + insight-extraction.md + export-suggestions.md）保持完整

## 链接有效性

- [ ] project-governance/ 目录内链接检查：`python .agents/scripts/check-links.py --path docs/retrospective/reports/project-governance/` 结果为 0 断链
- [ ] 报告内部子模块互链有效（README.md → execution/insight/export）
- [ ] 同主题内跨报告引用路径正确
- [ ] 跨主题报告引用路径正确（增加了一层 `../` 深度）
- [ ] 指向上层 patterns/concepts/frameworks/ 的引用路径正确
- [ ] 指向上层 docs/retrospective/README.md 的路径正确
- [ ] 全项目链接检查：`python .agents/scripts/check-links.py --path .` 结果为 0 断链

## 索引文档质量

- [ ] project-governance/README.md 已创建，包含 TOML frontmatter
- [ ] 主索引包含主题分类总览表（主题名称、定义、报告数量）
- [ ] 主索引包含 Mermaid 主题关系图，遵循安全编码五规则（无空行、文本加引号、subgraph英文ID、边标签格式正确）
- [ ] 主索引包含各主题详细报告清单与一句话简介
- [ ] 主索引包含目录结构树
- [ ] 主索引包含快速导航指南
- [ ] 5 个主题子目录均有 README.md
- [ ] 每个主题 README.md 包含主题定义、报告列表表格（含日期、简介、子模块链接）
- [ ] 每个主题 README.md 包含返回上级索引的链接
- [ ] 所有索引文档中的链接指向正确的新路径

## 上层文档同步

- [ ] docs/retrospective/README.md 目录树已更新，反映 5 个二级主题子目录
- [ ] docs/retrospective/README.md 报告计数从"12 份 + 1 独立报告"更新为"19 份（5主题分类）"
- [ ] docs/retrospective/README.md "项目治理系列"部分按主题分组重写
- [ ] docs/retrospective/README.md 中所有 project-governance 下报告的链接指向新路径
- [ ] 其他主题目录（atomization/insight-extraction/spec-system等）的内容未被破坏

## Mermaid 语法验证

- [ ] `python .agents/scripts/check-mermaid.py` 结果为 0 错误 0 警告
- [ ] 新增的 Mermaid 图表无空行
- [ ] 新增的 Mermaid 图表中文/特殊字符文本用双引号包裹
- [ ] 新增的 Mermaid 图表 subgraph 使用英文 ID + 引号包裹中文标题
- [ ] 新增的 Mermaid 图表边标签使用 `-->|"标签"|` 格式

## 全局一致性检查

- [ ] 无文件引用 project-governance/ 下报告的旧平铺路径
- [ ] AGENTS.md 上下文路由表中如有相关路径引用已同步更新（如适用）
- [ ] 所有文件名保持 kebab-case 命名规范
- [ ] 未引入任何 `file:///` 绝对路径
- [ ] reports-duplication-optimization-report.md 迁移后其内部引用路径正确
