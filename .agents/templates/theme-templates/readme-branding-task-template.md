---
id: "templates-theme-templates-readme-branding-task-template"
title: "Tasks"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/theme-templates/readme-branding-task-template.toml"
---
# Tasks

> 主题：readme-branding（README 与品牌定位）
> 适用场景：修改 README.md 内容、品牌定位、蓝图规划、对外展示材料

- [ ] Task 0: 内容规划
  - [ ] SubTask 0.1: 明确要添加/修改的内容类型（新增章节/更新段落/添加图表/修复链接/调整措辞）
  - [ ] SubTask 0.2: 确定内容在 README 中的位置，理解前后文逻辑
  - [ ] SubTask 0.3: 准备素材（数据、Mermaid 图表结构、引用来源、项目亮点）
  - [ ] SubTask 0.4: 确认品牌定位和用词风格一致（使用 SpecWeave 等既定术语，不随意更改品牌名）
  - [ ] SubTask 0.5: 确认内容面向外部读者（避免过度使用内部 jargon 或智能体术语）
  - [ ] SubTask 0.6: 草稿文字内容（先在其他地方写好，不要直接在 README 上边写边改）

- [ ] Task 1: 文案撰写与编辑
  - [ ] SubTask 1.1: 将草稿内容写入 README.md 的正确位置
  - [ ] SubTask 1.2: 确保语言简洁、面向人类读者（技术内容适度，重点突出项目价值）
  - [ ] SubTask 1.3: 如包含 Mermaid 图表，验证语法正确（可在 Mermaid Live Editor 预检查）
  - [ ] SubTask 1.4: 所有链接使用相对路径，不使用绝对路径
  - [ ] SubTask 1.5: 保持与现有内容风格一致（标题层级、表格格式、加粗规则等）
  - [ ] SubTask 1.6: 检查中英文混排格式（中英文间加空格，标点使用正确）

- [ ] Task 2: 一致性与质量检查
  - [ ] SubTask 2.1: 检查新内容与现有内容无重复或矛盾
  - [ ] SubTask 2.2: 检查术语使用与项目既定术语一致（SpecWeave、原子化、自我演进等）
  - [ ] SubTask 2.3: 检查目录结构/链接与实际文件一致
  - [ ] SubTask 2.4: 运行 check-links.py 验证所有链接有效
  - [ ] SubTask 2.5: 检查 Markdown 渲染：标题层级正确（不跳级，如 H2 下直接 H4）
  - [ ] SubTask 2.6: 检查表格列分隔符与列数一致
  - [ ] SubTask 2.7: 通读文案，确保无错别字、语病、不通顺之处

- [ ] Task 3: 收尾
  - [ ] SubTask 3.1: 如涉及 AGENTS.md 路由表或索引变更，同步触发 sync 任务或手动更新
  - [ ] SubTask 3.2: 确认没有破坏 README 中的 Mermaid 图表渲染
  - [ ] SubTask 3.3: 在对应主题 README.md 的执行看板中登记完成状态

# Task Dependencies

- Task 0 必须最先执行（README 是项目门面，规划不周会影响品牌形象）
- Task 1 依赖 Task 0 完成
- Task 2 依赖 Task 1 完成（内容写入后才能检查）
- Task 3 依赖 Task 2 完成
