# Checklist

## 目录结构
- [ ] Wiki目录 `animejs-threejs-adapter-wiki/` 已创建在正确路径（`.agents/docs/knowledge/learning/05-ai-multimodal-content/`）
- [ ] 包含10个文件：README.md、00-overview.md、01-quickstart.md、02-core-concepts.md、03-five-features.md、04-practical-examples.md、05-best-practices.md、06-faq.md、07-resources.md
- [ ] 所有文件名遵循两位数前缀命名规范（00-、01-、02-...）

## 文档格式规范
- [ ] 每个.md文件包含完整的YAML frontmatter（id、title、x-toml-ref、source、category、tags、date、status、author、summary）
- [ ] 标题层级正确（# 一级标题、## 二级、### 三级）
- [ ] 使用标准现代汉语，专业术语标注英文原文
- [ ] 代码块使用正确的语言标识（javascript）
- [ ] 表格格式规范，对齐整齐

## 内容完整性
- [ ] 00-overview.md包含教程简介、章节导航表格、目标读者、阅读路径建议
- [ ] 00-overview.md包含"知识落地判断"章节，明确给出应用结论
- [ ] 01-quickstart.md包含环境准备、多种安装方式、Hello World完整示例
- [ ] 02-core-concepts.md讲解适配器模式、关注点分离、API扁平化设计理念
- [ ] 03-five-features.md完整覆盖5大特性：属性扁平化、Extended transforms、材质uniforms、InstancedMesh、3D stagger
- [ ] 03-five-features.md每个特性包含原生写法vs适配器写法代码对比
- [ ] 04-practical-examples.md包含至少3个完整实战案例
- [ ] 05-best-practices.md包含性能优化、调试技巧、常见陷阱
- [ ] 06-faq.md包含不少于8个常见问题及明确解答
- [ ] 07-resources.md包含官方资源、学习推荐、不少于10个术语的术语表

## LAV模式合规性
- [ ] 首次出现代码示例处有"⚠️ API参考提示"标注
- [ ] 代码示例以官方文档为权威事实源，无基于"常识"的API推测
- [ ] "知识落地判断"给出三种明确结论之一（可直接应用/未来适用/暂不适用）并说明原因
- [ ] 遵循路径规范：沉淀文档位置正确，spec目录仅保留规划三文件

## 链接与索引
- [ ] 文档间交叉链接使用相对路径，格式正确
- [ ] 00-overview.md章节导航表格中的链接全部指向存在的文件
- [ ] README.md包含教程简介和快速导航
- [ ] 知识库索引已更新，新增本wiki教程条目且链接路径正确
- [ ] 07-resources.md包含项目内相关wiki的交叉引用

## 质量验证
- [ ] 代码示例语法正确，注释清晰
- [ ] 内容无错别字，术语统一
- [ ] 每个章节聚焦单一主题，长度适中
- [ ] 实战案例覆盖不同特性组合，非单一特性演示
- [ ] checklist所有检查项已通过验证
