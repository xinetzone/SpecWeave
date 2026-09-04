# 竹简悟道文档结构重组 - 验证检查清单

## 目录结构验证
- [x] `.agents/docs/` 下存在4个主题子目录：product/、insights/、reviews/、knowledge-transfer/
- [x] 旧目录 `superpowers/specs/` 已删除
- [x] 旧目录 `superpowers/` 已删除（如为空）
- [x] `.agents/docs/` 根目录存在 README.md 索引导航
- [x] `.agents/docs/` 根目录存在 restructure-comparison.md 对比文档

## 文件迁移验证
- [x] `product/2026-06-17-product-spec.md` 存在（原spec.md）
- [x] `insights/2026-06-17-insights-01-30.md` 存在（原insights-01-30.md）
- [x] `insights/2026-06-17-insights-31-65.md` 存在（原insights-31-65.md）
- [x] `reviews/2026-06-17-project-review.md` 存在（原review.md）
- [x] `reviews/2026-06-17-registration-review.md` 存在（原registration-review.md）
- [x] `knowledge-transfer/2026-06-17-transferable-methods.md` 存在（原transferable-methods.md）
- [x] `knowledge-transfer/2026-06-17-transferable-patterns.md` 存在（原transferable-patterns.md）

## 文件完整性验证
- [x] 所有7个迁移文件大小与原始一致（路径替换的微小差异除外）
- [x] 文件原始内容100%保留，除路径引用外无其他修改
- [x] 洞察编号连续（1-68）无缺失
- [x] Markdown格式正确，标题层级无误

## 内部引用验证
- [x] product-spec.md 中对洞察文件的引用路径正确（`../insights/...`）
- [x] insights-01-30.md 中对spec和insights-31的引用路径正确
- [x] insights-31-65.md 中对spec和insights-01的引用路径正确
- [x] project-review.md 中对spec、insights、transferable的引用路径正确
- [x] 同文件内锚点链接（`#Lxxx`）保持正确
- [x] 无旧路径 `superpowers/specs/` 在任何文档内部残留（对比文档除外）
- [x] 无旧文件名 `zhujian-wudao-*` 在交叉引用中残留（对比文档除外）

## 外部引用验证
- [x] AGENTS.md 文件地图树状目录路径更新为新结构
- [x] AGENTS.md 路由索引表路径更新为新结构
- [x] conventions.md 设计文档存放路径说明已更新
- [x] conventions.md 交叉引用格式示例路径已更新
- [x] project.md 文件清单表格路径已更新
- [x] git.md 作用域说明已更新
- [x] roles/philosopher.md references路径已更新
- [x] skills/zhujian-insight-writer/SKILL.md 参考文件路径已更新
- [x] skills/zhujian-insight-writer/references/insight-structure.md 示例路径已更新
- [x] 全项目搜索无 `superpowers/specs` 字符串残留（对比文档除外）

## 索引导航验证（README.md）
- [x] README 包含完整的目录树结构
- [x] README 包含每个文件的用途说明
- [x] README 包含文件统计信息（行数、洞察数等）
- [x] README 包含快速查找表（按需求场景索引）
- [x] README 包含新增文档归类指南
- [x] README 中所有链接路径正确

## 对比文档验证（restructure-comparison.md）
- [x] 包含重组前完整目录结构
- [x] 包含重组后完整目录结构
- [x] 包含7个文件的迁移映射表（原→新）
- [x] 包含重命名对照说明
- [x] 包含引用变更统计（共48处）
- [x] 包含重组日期和执行人信息

## 链接校验
- [x] 链接校验完成（36个本地链接，0个断链）
- [x] product/ 目录内链接全部有效
- [x] insights/ 目录内链接全部有效
- [x] reviews/ 目录内链接全部有效
- [x] knowledge-transfer/ 目录内链接全部有效
- [x] 跨目录链接全部有效
- [x] AGENTS.md 中的链接全部有效
- [x] conventions.md 中的链接全部有效
- [x] 额外发现的3处断链已修复（HTML路径、角色引用）

## 可扩展性验证
- [x] 新增产品规格文档可自然放入 product/ 目录
- [x] 新增洞察文件可自然放入 insights/ 目录
- [x] 新增复盘报告可自然放入 reviews/ 目录
- [x] 新增可迁移方法论可自然放入 knowledge-transfer/ 目录
- [x] 目录命名清晰，无歧义
- [x] 命名规则一致，新文件命名可遵循现有模式
