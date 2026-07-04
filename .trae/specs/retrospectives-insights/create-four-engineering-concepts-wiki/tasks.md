# Tasks

- [ ] Task 1: 网页内容提取与结构化理解
  - [x] SubTask 1.1: 使用 defuddle 提取原文完整 Markdown 内容（已完成初版提取）
  - [x] SubTask 1.2: 识别文章核心结构（开篇引子 + 四站解析 + 关系总结 + 结尾升华）
  - [x] SubTask 1.3: 提取关键原话引用（Mitchell Hashimoto / Peter Steinberger / Addy Osmani / Boris Cherny）
  - [x] SubTask 1.4: 提取关键概念术语（context rot / 渐进式披露 / harness / loop / 瓶颈外移）

- [ ] Task 2: 创建 wiki 文档骨架与目录导航
  - [x] SubTask 2.1: 在 docs/knowledge/learning/ 目录下创建 four-engineering-concepts-wiki.md
  - [x] SubTask 2.2: 编写 YAML frontmatter（title/source/date/tags），使用 x-toml-ref 引用外部 TOML 元数据
  - [x] SubTask 2.3: 创建对应的 TOML 元数据文件于 .meta/toml/docs/knowledge/learning/ 目录
  - [x] SubTask 2.4: 编写完整的目录导航系统（Markdown 锚点链接）

- [ ] Task 3: 编写核心论点章节
  - [x] SubTask 3.1: 阐述"瓶颈外移"核心规律（模型变强→瓶颈外移一层）
  - [x] SubTask 3.2: 阐述"四个路标而非四个赛道"的反直觉观点
  - [x] SubTask 3.3: 预告四站路径（怎么说→给什么→干活环境→你自己）

- [ ] Task 4: 编写 Prompt Engineering 章节（第一站）
  - [x] SubTask 4.1: 解析模型本质（预测下一个字而非思考）
  - [x] SubTask 4.2: 解析"把话说明白"的提示词配方六要素
  - [x] SubTask 4.3: 说明适用边界（短链路一问一答）与瓶颈顶到下一层的触发条件

- [ ] Task 5: 编写 Context Engineering 章节（第二站）
  - [x] SubTask 5.1: 解析 Agent 火起后从"回答问题"到"干活"的转变
  - [x] SubTask 5.2: 解析上下文窗口与短期记忆容量限制
  - [x] SubTask 5.3: 解析 Anthropic 的 context rot（上下文腐化）现象
  - [x] SubTask 5.4: 解析"渐进式披露"理念与"给得准而非给得多"的核心要义

- [ ] Task 6: 编写 Harness Engineering 章节（第三站·重点）
  - [x] SubTask 6.1: 解析长链路任务跑偏问题（计划偏/结果理解错/忘记目标）
  - [x] SubTask 6.2: 阐述 harness 词源（马具/缰绳）与 Mitchell Hashimoto 的定义原话
  - [x] SubTask 6.3: 解析"复利效应"机制（每犯一错环境强一点→更少犯错→更快改进）
  - [x] SubTask 6.4: 阐述 Agent = 模型 + Harness 公式及其人话翻译
  - [x] SubTask 6.5: 阐明"关键一跃"内涵（从输入侧转向模型外部世界）与同模型差几倍现象的解释
  - [x] SubTask 6.6: 说明层层包含关系（Prompt ⊂ Context ⊂ Harness）

- [ ] Task 7: 编写 Loop Engineering 章节（第四站）
  - [x] SubTask 7.1: 解析最后一环瓶颈（人肉驱动按回车）
  - [x] SubTask 7.2: 阐述"松手"理念（设计循环而非手动 prompt）
  - [x] SubTask 7.3: 引用三位点响者观点（Peter Steinberger / Addy Osmani / Boris Cherny）
  - [x] SubTask 7.4: 阐明 loop 是 harness 逻辑的自然延伸（连"按回车的你"也设计进世界）
  - [x] SubTask 7.5: 解析瓶颈移到人身上的真相（loop 改变工作但未删除人，harness 假设会过期）

- [ ] Task 8: 编写四者关系总结章节
  - [x] SubTask 8.1: 图示化"层层包含"关系（Prompt ⊂ Context ⊂ Harness）
  - [x] SubTask 8.2: 总结瓶颈外移的终点（你自己）与后续判断（人的主战场）
  - [x] SubTask 8.3: 提炼核心结论（模型决定上限，harness/loop/人的判断决定落地）

- [ ] Task 9: 编写关键人物与原话引用章节
  - [x] SubTask 9.1: 整理 Mitchell Hashimoto（Terraform 作者）原话与身份
  - [x] SubTask 9.2: 整理 Peter Steinberger（OpenClaw 作者）原话与身份
  - [x] SubTask 9.3: 整理 Addy Osmani（Google AI 总监）原话与身份
  - [x] SubTask 9.4: 整理 Boris Cherny（Claude Code 创始人）原话与身份

- [ ] Task 10: 编写实践启示章节
  - [x] SubTask 10.1: 萃取"复利式修补"启示（每次犯错永久修进环境）
  - [x] SubTask 10.2: 萃取"环境沉淀而非脑内记忆"启示
  - [x] SubTask 10.3: 萃取"持续修环境+盯模型边界"启示（harness 假设会过期）
  - [x] SubTask 10.4: 萃取"人的判断仍是主战场"启示
  - [x] SubTask 10.5: 明确标注此章节为"基于原文的延伸思考"

- [ ] Task 11: 编写 FAQ 与相关资源章节
  - [x] SubTask 11.1: 编写 FAQ（覆盖四者关系、harness 落地、loop 与自动化的区别等常见问题）
  - [x] SubTask 11.2: 编写相关资源链接（原文、Anthropic Agent Skills、引用人物相关资料）

- [ ] Task 12: 更新知识库索引与元数据
  - [x] SubTask 12.1: 更新 docs/knowledge/README.md 在学习分类中新增本教程条目
  - [x] SubTask 12.2: 验证 TOML 元数据文件与 YAML frontmatter 的 x-toml-ref 引用正确
  - [x] SubTask 12.3: 验证文件命名符合 kebab-case 纯英文规范

# Task Dependencies
- [Task 2] depends on [Task 1]（需先理解内容才能搭建骨架）
- [Task 3]-[Task 11] depend on [Task 2]（需先创建文档骨架）
- [Task 12] depends on [Task 11]（需文档完成后才更新索引）
- [Task 3]-[Task 11] 之间无强依赖，可按章节顺序串行撰写以保证逻辑连贯
