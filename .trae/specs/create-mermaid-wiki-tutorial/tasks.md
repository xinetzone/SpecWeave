# Tasks: Mermaid 官方文档 Wiki 教程

> 按七概念方法论 R→I→E→V→C 链路组织；Phase 3 各章节可并行编写，每个任务对应一次原子提交。

## Phase 1: R（复盘）— 学习与事实采集

- [x] Task 1: 学习 Mermaid 官方文档（mermaid.js.org）
  - [x] 1.1 浏览文档总览，记录图表类型清单与文档结构
  - [x] 1.2 重点学习 flowchart、sequenceDiagram 语法细节
  - [x] 1.3 学习 classDiagram、stateDiagram-v2、erDiagram 语法
  - [x] 1.4 学习 gantt、pie、journey、timeline、sankey、quadrantChart 语法
  - [x] 1.5 学习 gitGraph、requirementDiagram、mindmap、C4、block、zenuml 语法
  - [x] 1.6 学习配置（Configuration）与主题（Theming）部分
  - [x] 1.7 提取集成与生态（mermaid-cli、mermaid.live、渲染器）信息

- [x] Task 2: 实操 mermaid.live 在线编辑器（mermaid.live/edit）
  - [x] 2.1 打开 mermaid.live/edit，验证各图表类型实时渲染
  - [x] 2.2 验证语法高亮、实时预览、代码分享、图片导出功能
  - [x] 2.3 记录版本信息与在线编辑器特有功能

## Phase 2: I（洞察）— 知识组织与结构设计

- [x] Task 3: 整理学习笔记，设计 wiki 结构
  - [x] 3.1 汇总两来源学习笔记，提取共性知识主题
  - [x] 3.2 设计 10 章原子化文档结构，定义每章核心内容
  - [x] 3.3 确定章节间交叉引用关系与目录命名

## Phase 3: E（萃取）— 编写 Wiki 教程

- [x] Task 4: 编写 00-overview.md（教程总览与导航）
  - [x] 4.1 教程简介与目标读者
  - [x] 4.2 10 章导航表
  - [x] 4.3 Mermaid 图表类型总览图（Mermaid）
  - [x] 4.4 阅读路径建议 + 与 mermaid-guide.md / mermaid-cmd 关联指引

- [x] Task 5: 编写 01-introduction-quickstart.md（入门与快速开始）
  - [x] 5.1 Mermaid 核心概念与工作原理
  - [x] 5.2 快速开始（mermaid.live 实操）
  - [x] 5.3 在线编辑器功能详解
  - [x] 5.4 本地集成方式概览

- [x] Task 6: 编写 02-flowchart.md（基础图表：流程图）
  - [x] 6.1 节点形状与连线类型
  - [x] 6.2 节点文本、标签与 subgraph
  - [x] 6.3 direction 方向设置
  - [x] 6.4 样式（style/classDef）与链接交互

- [x] Task 7: 编写 03-sequence-diagram.md（时序图）
  - [x] 7.1 participant 参与者声明
  - [x] 7.2 消息类型与激活/去激活
  - [x] 7.3 loop/alt/opt/par 结构
  - [x] 7.4 Note 注释与自动序号

- [x] Task 8: 编写 04-class-state-er.md（结构型图表）
  - [x] 8.1 classDiagram 类/属性/方法/关系
  - [x] 8.2 stateDiagram-v2 状态/迁移/复合状态
  - [x] 8.3 erDiagram 实体/属性/关系/基数

- [x] Task 9: 编写 05-aggregate-diagrams.md（可视化图表）
  - [x] 9.1 gantt 甘特图
  - [x] 9.2 pie 饼图
  - [x] 9.3 journey 用户旅程
  - [x] 9.4 timeline / sankey / quadrantChart

- [x] Task 10: 编写 06-advanced-diagrams.md（进阶图表）
  - [x] 10.1 gitGraph Git 图
  - [x] 10.2 requirementDiagram 需求图
  - [x] 10.3 mindmap 思维导图
  - [x] 10.4 C4 / block / zenuml

- [x] Task 11: 编写 07-configuration-theming.md（配置与主题）
  - [x] 11.1 全局配置 Configuration
  - [x] 11.2 主题 Theme/ThemeVariables
  - [x] 11.3 字体/颜色/安全级别
  - [x] 11.4 mermaid.initialize 与常用配置示例

- [x] Task 12: 编写 08-integrations-ecosystem.md（集成与生态）
  - [x] 12.1 mermaid-cli（mmdc 命令行渲染）
  - [x] 12.2 mermaid.live 在线编辑器
  - [x] 12.3 Markdown/渲染器集成（GitHub/飞书/VS Code）
  - [x] 12.4 mermaid.js 库 API 与生态工具对比

- [x] Task 13: 编写 09-faq-best-practices.md（常见问题与最佳实践）
  - [x] 13.1 不少于 8 个常见问题及解决方案
  - [x] 13.2 最佳实践建议
  - [x] 13.3 与项目安全编码六规则的对接说明

- [x] Task 14: 编写 10-cheatsheet.md（命令速查表）
  - [x] 14.1 按图表类型分类的语法速查表
  - [x] 14.2 常用配置速查
  - [x] 14.3 mermaid.live 使用速查

- [x] Task 15: 更新 04-docs-markup-tooling/README.md 子目录导航
  - [x] 15.1 追加 mermaid-wiki 子目录条目

## Phase 4: V（对抗审查）— 质量验证

- [x] Task 16: 运行 check-mermaid.py 校验所有示例图表
  - [x] 16.1 运行 `python .agents/scripts/check-mermaid.py --path docs/knowledge/learning/04-docs-markup-tooling/mermaid-wiki`
  - [x] 16.2 修复所有 error 级问题，确保 0 错误
  - [x] 16.3 核查 YAML frontmatter、相对路径引用、kebab-case 命名

## Phase 5: C（原子提交）— 交付

- [ ] Task 17: 原子化提交所有文档
  - [ ] 17.1 每个 Task（4-15）独立提交，提交信息遵循 Conventional Commits 规范（`docs(mermaid-wiki): <subject>` 中文描述"为什么"）
  - [ ] 17.2 README 导航更新单独提交

# Task Dependencies

- Task 3 依赖 Task 1-2（学习完成后才能设计结构）
- Task 4-15 依赖 Task 3（结构设计完成后才能编写）
- Task 4-15 之间无强依赖，可并行编写
- Task 16 依赖 Task 4-15（所有文档编写完成后才能校验）
- Task 17 依赖 Task 16（校验通过后才能提交）