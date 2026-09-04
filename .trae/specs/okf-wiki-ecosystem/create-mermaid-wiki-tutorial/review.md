# Checklist: Mermaid 官方文档 Wiki 教程

## 七概念方法论质量门（G1-G4 + V）

### G1：事实无因果词（R 阶段）

- [x] 学习笔记中无主观因果推断词，纯客观记录官方文档内容
- [x] 两个来源（mermaid.js.org 官方文档、mermaid.live/edit）的关键信息均已覆盖

### G2：洞察四元组完整（I 阶段）

- [x] wiki 结构设计包含：知识点识别（从两来源中提取的共性主题）+ 组织结构（10 章划分理由）+ 关联关系（章节间交叉引用）+ 应用场景（每章在项目中的定位）

### G3：模式可迁移（E 阶段）

- [x] 每个章节独立可读，不依赖其他章节的上下文
- [x] 图表示例完整可复现，用户可直接复制到 mermaid.live 渲染
- [x] 教程内容可迁移至其他文本即图表工具的教程场景

### V 门：对抗审查有实质内容

- [x] 所有图表示例经 check-mermaid.py 校验，0 error
- [x] 示例图表在 mermaid.live 中可正确渲染
- [x] 内容与项目 mermaid-guide.md 安全编码六规则一致，无冲突

### G4：行动项原子化（C 阶段）

- [ ] 每次提交仅包含单一文档文件（单一职责）
- [ ] 提交信息遵循 Conventional Commits 规范（`docs(mermaid-wiki): <subject>`）
- [ ] 提交历史清晰可追溯，每个提交对应一个独立的章节

## 文档质量检查

### 00-overview.md
- [x] 包含教程简介和目标读者说明
- [x] 包含 10 章导航表
- [x] 包含 Mermaid 图表类型总览图（Mermaid）
- [x] 包含阅读路径建议
- [x] 包含与 mermaid-guide.md / mermaid-cmd 的关联指引

### 01-introduction-quickstart.md
- [x] 覆盖 Mermaid 核心概念与工作原理
- [x] 覆盖快速开始（mermaid.live 实操路径）
- [x] 覆盖在线编辑器功能（语法高亮/实时预览/分享/导出）
- [x] 覆盖本地集成方式概览

### 02-flowchart.md
- [x] 覆盖节点形状（矩形/圆角/菱形/圆形/体育场等）
- [x] 覆盖连线类型（箭头/虚线/粗线）
- [x] 覆盖 subgraph 分组与 direction 方向
- [x] 覆盖 style/classDef 样式与链接交互

### 03-sequence-diagram.md
- [x] 覆盖 participant 参与者声明
- [x] 覆盖消息类型（实线/虚线/响应）
- [x] 覆盖 activate/deactivate 激活
- [x] 覆盖 loop/alt/opt/par 结构与 Note 注释

### 04-class-state-er.md
- [x] 覆盖 classDiagram（类/属性/方法/关系）
- [x] 覆盖 stateDiagram-v2（状态/迁移/复合状态）
- [x] 覆盖 erDiagram（实体/属性/关系/基数）

### 05-aggregate-diagrams.md
- [x] 覆盖 gantt、pie、journey、timeline、sankey、quadrantChart 全部六种

### 06-advanced-diagrams.md
- [x] 覆盖 gitGraph、requirementDiagram、mindmap、C4、block、zenuml 全部六种

### 07-configuration-theming.md
- [x] 覆盖 Configuration 全局配置
- [x] 覆盖主题 Theme/ThemeVariables
- [x] 覆盖安全级别 securityLevel
- [x] 覆盖 mermaid.initialize 与常用配置示例

### 08-integrations-ecosystem.md
- [x] 覆盖 mermaid-cli（mmdc）
- [x] 覆盖 mermaid.live 在线编辑器
- [x] 覆盖 Markdown/渲染器集成（GitHub/飞书/VS Code）
- [x] 覆盖 mermaid.js 库 API 与生态工具对比

### 09-faq-best-practices.md
- [x] 不少于 8 个常见问题，每个含现象描述和解决方案
- [x] 覆盖语法错误、渲染失败、版本差异、中文乱码等
- [x] 包含最佳实践建议
- [x] 包含与项目安全编码六规则的对接说明

### 10-cheatsheet.md
- [x] 包含按图表类型分类的语法速查表
- [x] 覆盖全部 17 种图表类型（flowchart/sequence/class/state/er/gantt/pie/journey/timeline/sankey/quadrant/gitgraph/requirement/mindmap/C4/block/zenuml）
- [x] 包含常用配置速查与 mermaid.live 使用速查

## 文件规范性检查

- [x] 所有文件使用 YAML frontmatter（含 `source` 字段）
- [x] 文档间交叉引用使用相对路径
- [x] 无 `file:///` 绝对路径断链
- [x] 文件命名使用 kebab-case
- [x] 目录结构符合项目 wiki 规范（`04-docs-markup-tooling/mermaid-wiki/`）
- [x] 04-docs-markup-tooling/README.md 已更新 mermaid-wiki 子目录导航
- [x] 所有 Mermaid 示例通过 `check-mermaid.py` 校验（0 error）