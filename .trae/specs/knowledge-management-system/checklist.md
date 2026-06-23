# Checklist

## 目录结构
- [x] `docs/knowledge/` 目录存在，包含 operations/、platform/、troubleshooting/、decisions/、best-practices/、scripts/ 子目录
- [x] 各分类目录包含 `.gitkeep` 文件

## 模板
- [x] `docs/knowledge/template.md` 存在，包含完整的 YAML frontmatter 字段和正文结构说明
- [x] 模板包含 title、category、tags、date、status、author、summary 七个字段

## 索引脚本
- [x] `docs/knowledge/scripts/generate_index.py` 可正常运行
- [x] 脚本正确解析 YAML frontmatter
- [x] 脚本排除 template.md 和 README.md
- [x] 缺失元数据时输出警告但不中断
- [x] 空知识库时生成占位提示

## README.md 索引
- [x] 包含统计摘要（总条目数、各类别数量）
- [x] 包含按类别分组的条目列表（表格含标题、摘要、日期、标签、链接）
- [x] 包含按标签聚合的关键词索引
- [x] 包含最近更新条目列表
- [x] 包含自动生成时间戳
- [x] 包含使用指南章节
- [x] 包含相关资源链接（复盘报告、任务总结）

## 示例条目
- [x] `operations/windows-powershell-heredoc.md` 存在，内容完整
- [x] `troubleshooting/move-item-access-denied.md` 存在，内容完整
- [x] `decisions/libs-rename-to-vendor.md` 存在，内容完整
- [x] 所有示例条目包含正确的 YAML frontmatter

## AGENTS.md 集成
- [x] AGENTS.md 全局核心规则包含"查阅知识库"条款
- [x] developer 角色定义包含查阅 troubleshooting/ 条款
- [x] architect 角色定义包含查阅 decisions/ 条款
- [x] reviewer 角色定义包含查阅 best-practices/ 条款

## 验证
- [x] 运行 generate_index.py 后 README.md 正确更新
- [x] 新建和修改的条目在索引中正确反映
- [x] 现有知识资产（复盘报告、任务总结）在 README 中正确链接