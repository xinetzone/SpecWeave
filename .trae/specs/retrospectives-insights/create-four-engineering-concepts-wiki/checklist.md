# Checklist

## 文档创建与格式规范
- [x] wiki 文档已创建于 docs/knowledge/learning/four-engineering-concepts-wiki.md
- [x] 文件名符合 kebab-case 纯英文规范（four-engineering-concepts-wiki.md）
- [x] YAML frontmatter 使用 --- 包裹，包含 title/source/date/tags 字段
- [x] YAML frontmatter 包含 x-toml-ref 字段引用外部 TOML 元数据文件
- [x] 对应的 TOML 元数据文件已创建于 .meta/toml/docs/knowledge/learning/ 目录
- [x] 文档格式符合项目 MDI v1.0 规范

## 目录导航
- [x] 文档顶部包含完整的目录导航系统
- [x] 目录导航使用 Markdown 锚点链接，可点击跳转
- [x] 目录覆盖所有章节（核心论点、四站解析、关系总结、关键人物、实践启示、FAQ、资源）

## 内容完整性
- [x] 核心论点章节阐述"瓶颈外移"规律与"四个路标"反直觉观点
- [x] Prompt Engineering 章节包含模型本质、提示词配方六要素、适用边界
- [x] Context Engineering 章节包含上下文窗口、context rot、渐进式披露、给得准而非多
- [x] Harness Engineering 章节（重点）包含 Mitchell Hashimoto 定义、复利效应、Agent=模型+Harness 公式、关键一跃内涵
- [x] Loop Engineering 章节包含回合制→循环转变、三位点响者观点、loop 是 harness 延伸
- [x] 四者关系总结章节阐明层层包含（Prompt ⊂ Context ⊂ Harness）与瓶颈终点
- [x] 关键人物章节准确引用四位人物原话并标注身份
- [x] 实践启示章节萃取至少 3 条可执行启示并标注为延伸思考
- [x] FAQ 章节覆盖常见问题
- [x] 资源链接章节包含原文链接与相关资料

## 引用准确性
- [x] Mitchell Hashimoto（Terraform 作者）原话引用准确
- [x] Peter Steinberger（OpenClaw 作者）原话引用准确
- [x] Addy Osmani（Google AI 总监）原话引用准确
- [x] Boris Cherny（Claude Code 创始人）原话引用准确
- [x] Anthropic context rot 概念引用准确
- [x] Anthropic Agent Skills 渐进式披露概念引用准确
- [x] Agent = 模型 + Harness 公式引用准确

## 客观性与边界
- [x] 文档客观转述原文观点，不添加未在原文中出现的信息
- [x] 延伸思考部分（实践启示）已明确标注为"基于原文的延伸思考"
- [x] 不评判原文观点对错，保持中立整理立场

## 索引与联动
- [x] docs/knowledge/README.md 学习分类中新增本教程条目
- [x] 索引条目包含标题、摘要、日期和标签，遵循现有索引格式
- [x] 资源链接章节中的外部链接格式正确

## 子智能体交付验收 5 点检查（强制！）
- [x] frontmatter 格式为 YAML（---包裹），不是 TOML（+++包裹）
- [x] 文件路径为 docs/knowledge/learning/，不是项目根目录
- [x] 文件命名为 kebab-case 纯英文，无中文字符
- [x] 引用原话时使用引用块（>）并标注人物身份
- [x] 章节逻辑递进，四站解析顺序为 Prompt → Context → Harness → Loop
