# Papi酱关闭公司回归个人IP：创业趋势观察Wiki教程 - 质量检查清单

## 格式规范
- [ ] frontmatter使用YAML（---）格式分隔，不是+++（TOML）
- [ ] 所有文件frontmatter包含id/title/source/x-toml-ref四个必填字段
- [ ] x-toml-ref路径正确，相对层级计算准确（原子文件为../../../../.meta/toml/...）
- [ ] 所有内部链接使用相对路径，无file:///绝对路径，无断链
- [ ] 文件名符合kebab-case规范，纯英文无中文
- [ ] 原子文件编号正确（00-, 01-, ..., 08-）

## 内容质量
- [ ] Papi酱十年时间线完整（2015-2026所有关键节点）
- [ ] 关键数据准确：1200万融资、2200万广告、1.2亿A轮、6家公司注销、7人团队
- [ ] 网传17.57亿收入已明确标注为"网传流水，发布者已定性为假消息"
- [ ] 5大核心观点完整阐述，无遗漏
- [ ] 行业观察包含至少4个案例（Papi酱/罗永浩/李子柒/李佳琦）
- [ ] 超级个人IP vs 平台机构对比表格维度全面（至少6个维度）
- [ ] 创业启示实践要点具体可操作，至少5条
- [ ] FAQ包含至少6个常见问题，答案基于原文内容
- [ ] 内容客观中立，不评判创业者选择的对错
- [ ] 关键信息有原文依据，不编造未提及的内容

## 结构完整性
- [ ] 原子化决策已明确记录在spec.md中（决策为"需要拆分"，理由充分）
- [ ] 索引页存在（papi-jiang-solo-ip-trend-wiki.md），包含完整导航表格
- [ ] 原子目录存在（papi-jiang-solo-ip-trend-wiki/），包含所有章节文件
- [ ] 9个章节齐全：00-overview/01-case-timeline/02-core-viewpoints/03-industry-trend/04-model-comparison/05-entrepreneurship-insights/06-summary/07-faq/08-resources
- [ ] 每个原子文件标题层级从h1开始，无跳级
- [ ] 导航表格链接与实际文件一一对应
- [ ] 资源链接包含原文URL和文章中提到的3篇相关阅读

## 子代理产出验收5点检查（强制！）
- [ ] ✅ **frontmatter分隔符正确**：使用`---`（YAML），不是`+++`（TOML）
- [ ] ✅ **x-toml-ref存在且路径正确**：指向.meta/toml/镜像路径，相对层级计算正确（原子文件需4层../）
- [ ] ✅ **标题层级从h1开始**：每个文件第一行是`# 标题`，无跳级（h1→h2→h3）
- [ ] ✅ **文件名合规**：kebab-case、纯英文、原子文件使用两位数字前缀（00-08）
- [ ] ✅ **source溯源字段存在**：frontmatter中包含source字段指向原始URL或父文件

## 元数据配套
- [ ] 所有文件都有对应的TOML元数据文件在.meta/toml/镜像路径
- [ ] TOML文件包含id/title/category/date等基本字段
- [ ] tags分类准确，包含"个人IP"、"内容创业"、"创业趋势"等标签
- [ ] date字段使用2026-07-04（当前日期）
- [ ] status标记为draft（初稿）

## 知识库集成
- [ ] docs/knowledge/README.md已更新，在学习分类中添加本教程条目
- [ ] README条目格式与现有条目一致（标题、摘要、日期、标签）
- [ ] 条目链接指向索引页papi-jiang-solo-ip-trend-wiki.md

## 自动化验证
- [ ] 运行fix-x-toml-ref.py --write --create-toml无错误
- [ ] 运行check-links.py无断链报告
- [ ] 运行check-filename-convention.py所有文件名通过检查
- [ ] 工作区无临时文件、备份文件或无关文件混入

## 提交规范
- [ ] 第一次提交：内容创作提交，仅包含wiki文档和README更新
- [ ] 第二次提交：元数据修复提交，包含TOML文件和路径修复
- [ ] 提交信息遵循Conventional Commits格式（docs(knowledge): ...）
- [ ] 提交主体使用中文描述
- [ ] 每次提交单一职责，不混入无关变更
