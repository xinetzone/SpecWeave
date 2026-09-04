# Checklist

## 文件创建
- [x] `d:\AI\.agents\commands\first-principles.md` 文件已创建
- [x] YAML frontmatter 包含 id、title、source、x-toml-ref 四个字段
- [x] id 值为 `first-principles`，source 值为 `AGENTS.md#指令集`
- [x] x-toml-ref 路径指向 `../../.meta/toml/.agents/commands/first-principles.toml`

## 内容完整性
- [x] 包含"触发条件"章节，列出至少 5 类触发场景（实际 6 条）
- [x] 包含"输入规范"章节，定义参数表格（参数、类型、必选、说明）
- [x] 包含"RACI 责任分配矩阵"章节，含 RACI 模型说明与矩阵表格
- [x] 包含"核心原则"章节，阐述第一性原理定义与思维特征
- [x] 包含"执行步骤"章节，覆盖 6 个标准化步骤
- [x] 包含"输出规范"章节，定义产出物格式与存储位置
- [x] 包含"质量验收"章节，列出可执行的验收项
- [x] 包含"约束条件"章节，明确注意事项与适用边界
- [x] 包含"关联资源"章节，链接至相关模块

## 第一性原理内容质量
- [x] 定义清晰区分第一性原理与类比思维/归纳思维
- [x] 实施步骤覆盖：问题识别→假设剥离→要素识别→公理提炼→重构→验证
- [x] 注意事项涵盖：过度拆解、忽视经验价值、为创新而创新、滥用复杂方法等误区
- [x] 提供适用边界判断准则（成本收益 30% 阈值、问题复杂度 1-2 步阈值）

## 格式一致性
- [x] 章节顺序与现有指令集（retrospective/insight/atomization）一致
- [x] 文件命名采用英文小写连字符格式（first-principles.md）
- [x] 文档语言为标准现代汉语，无网络流行语

## README 同步
- [x] `.agents/commands/README.md` 指令集清单表格新增"第一性原理"行
- [x] 新增行包含：指令集名称、ID（first-principles）、用途、关联模块
- [x] 表格其他行内容未被误改（原 8 行 + 新增 1 行 = 9 行）

## 协同关系
- [x] "关联资源"章节链接至自我洞察模块（self-cognition.md 不存在，已改用 self-insight.md 保持链接有效）
- [x] 明确与复盘/洞察/原子化等指令集的协同与边界划分
