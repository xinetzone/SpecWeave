# AI工程四个路标 Wiki教程 Quality Checklist

## frontmatter规范
- [x] **类型确认**：spec.md中已明确"原子化拆分"决策
- [x] 所有.md文件frontmatter使用YAML（---）格式，没有使用+++（TOML）
- [x] 原子化wiki：frontmatter含id/title/source/x-toml-ref四个字段，无多余字段
- [x] 索引页frontmatter：id/title/source/x-toml-ref四个字段

## 格式规范
- [x] 链接使用相对路径，无死链
- [x] 文件名符合kebab-case规范，纯英文无中文
- [x] 原子文件编号正确（00-到07-）
- [x] 索引页控制在<100行，仅含导航+学习目标

## 内容质量
- [x] 核心观点完整保留（7个主要观点），无重大遗漏
- [x] 关键概念解释清晰（10个概念/术语）
- [x] 四站递进逻辑连贯（Prompt→Context→Harness→Loop）
- [x] "层层包含"关系说明清楚（Prompt⊂Context⊂Harness）
- [x] Harness作为"关键一跃"的论述充分
- [x] 4个可复用认知模型表述清晰（瓶颈外移四层模型、Agent=模型+Harness、复利式环境建设、回合制到循环制）
- [x] 深度洞察部分超越字面内容（行业趋势+市场动态）
- [x] Harness工程化方法论可操作（错误即资产、修补必沉淀、复利积累、结构化防御）
- [x] FAQ覆盖读者可能遇到的问题（5-8个）
- [x] 资源链接有效且相关

## 结构完整性
- [x] 包含8章节结构（00-overview到07-summary-faq-resources）
- [x] 00-overview.md有完整的文档导航表
- [x] 06-insights-patterns.md包含行业趋势+市场动态+认知模型+方法论
- [x] 07-summary-faq-resources.md包含总结+FAQ+资源三部分

## 子代理产出验收9点检查（强制！）
- [x] ✅ **frontmatter分隔符正确**：使用`---`（YAML），不是`+++`（TOML）
- [x] ✅ **frontmatter字段类型正确且无多余**：原子化wiki仅含id/title/source/x-toml-ref
- [x] ✅ **x-toml-ref存在且路径正确**：指向.meta/toml/镜像路径，相对层级计算正确
- [x] ✅ **标题层级从h1开始**：文件第一行是`# 标题`，无跳级
- [x] ✅ **文件名合规**：kebab-case、纯英文、数字前缀正确（两位数字）
- [x] ✅ **source溯源字段存在**：派生产物标注原始来源URL或父文件
- [x] ✅ **内容无工具标签污染**：无`<seed:tool_call>`、`<function`、`TodoWrite`等工具调用标签
- [x] ✅ **索引页精简**：索引页<100行，仅含导航+学习目标，无深度内容
- [x] ✅ **章节逻辑连贯**：四站递进+层层包含关系清晰

## 元数据配套
- [x] .meta/toml/docs/knowledge/learning/ai-engineering-four-milestones-wiki/ 下有8个TOML文件
- [x] fix-x-toml-ref.py通过（0个需修复）

## 自动化验证（提交前必做）
- [x] `python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/ai-engineering-four-milestones-wiki/ --write --create-toml` 通过
- [x] `python .agents/scripts/check-links.py --path docs/knowledge/learning/ai-engineering-four-milestones-wiki/` 通过
- [x] `python .agents/scripts/check-filename-convention.py` 通过

## 知识库索引
- [x] docs/knowledge/README.md 已追加本wiki条目
