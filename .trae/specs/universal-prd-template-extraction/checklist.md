# 通用PRD/项目Spec模板萃取 - 验收检查清单

## Task 0: 参考Spec深度解构检查
- [x] 解构分析覆盖参考Spec的所有章节（frontmatter + 10个正文章节）
- [x] 每个章节都明确回答了"核心功能"（为什么需要这个章节）
- [x] 清晰区分了本质要素（8个）与项目特定要素（7个）
- [x] 分析了参考Spec从v1.0到v1.1的演进逻辑
- [x] 识别了6个优秀设计决策
- [x] 识别了2个可改进点（追溯矩阵缺失、风险应对缺失）
- [x] deconstruction-analysis.md符合文件规范（frontmatter、kebab-case、<500行）

## Task 1: Frontmatter元数据规范检查
- [x] 必填字段已明确（7个：id/title/source/created_at/status/theme/version）
- [x] 推荐字段已明确（9个，不超过10个）
- [x] 每个字段都有含义说明、取值规范和填写时机
- [x] status状态机完整覆盖项目生命周期（candidate→planning→in-progress→completed→archived）
- [x] frontmatter-specification.md符合文件规范

## Task 2: PRD正文结构指南检查
- [x] 覆盖所有核心章节（11个含版本历史）
- [x] 每个章节都有核心目的说明
- [x] 每个章节都有必填要素清单
- [x] 至少5个章节有正反示例对比
- [x] 每个章节都有明确的检查要点
- [x] 明确了Goals→FR→NFR→AC之间的追溯关系
- [x] prd-structure-guide.md符合文件规范

## Task 3: 格式选择与最佳实践检查
- [x] 明确了PRD Spec与Change Spec各自的适用场景
- [x] 格式选择决策树包含3个判断维度
- [x] 5个测试场景用决策树能得出明确结论
- [x] 列出了12个常见陷阱，每个都有反面示例和正确做法
- [x] 质量自检清单包含15个检查项
- [x] 引用了6个已有相关模式
- [x] format-selection-guide.md符合文件规范
- [x] best-practices.md符合文件规范

## Task 4: 通用模板文件检查
- [x] 模板包含所有必填frontmatter字段
- [x] 模板包含所有核心正文章节
- [x] 每个部分都有清晰的填写提示
- [x] 模板核心内容（不含注释示例）152行（≤200行）
- [x] 文件名符合kebab-case规范
- [x] YAML frontmatter格式正确
- [x] 文件归档至正确位置（patterns/methodology-patterns/spec-workflow/）

## Task 5: 规范体系整合检查
- [x] spec-writing-guide已更新（新增08/09章节）
- [x] spec-writing-guide包含格式选择决策框架
- [x] spec-workflow目录有README索引文件
- [x] 所有内部链接通过check-links验证（无断链）
- [x] 现有Change Spec格式的规范内容完整保留，未被破坏
- [x] 双向导航链接建立（模板↔指南↔规则↔模式目录）

## Task 6: Dogfooding自验证检查
- [x] 已用新模板对照检查本项目Spec
- [x] Dogfooding过程中发现的15个问题已记录
- [x] 合理的改进建议已纳入模板v1.1优化
- [x] Dogfooding验证过程有明确记录（在deconstruction-analysis.md第七章）
- [x] 本项目Spec能被新模板完整覆盖（识别出的是格式问题，非要素缺失）

## Task 7: 全局文件规范检查
- [x] check-filename-convention.py验证通过（无中文文件名、kebab-case正确，exit code 0）
- [x] check-frontmatter.py验证通过（所有YAML格式正确）
- [x] check-links.py验证通过（无断链）
- [x] 所有单文件≤500行
- [x] 无文件放置在项目根目录
- [x] 所有文件使用标准Markdown格式

## Task 8: 项目收尾检查
- [x] 项目复盘完成，Dogfooding过程包含自我审视
- [x] 所有文档status更新为completed
- [x] frontmatter补充completed_at、version、total_files、patterns_extracted等完成字段
- [x] 识别了"Dogfooding自验证"作为关键方法论洞察
- [x] 准备好原子提交信息（docs: add universal PRD template and spec writing standards）

## 全局质量门
- [x] 所有Task 0-8的检查项均已通过
- [x] 模板具备通用性：能适配研究类、开发类、文档类、工具类等不同项目类型
- [x] 模板具备实用性：每个章节有明确的写作指导，不是空泛原则
- [x] 模板与现有工具链兼容，无需修改检查脚本即可使用
- [x] 设计决策均有依据（来自参考Spec实践或第一性原理分析）
