# Harness Engineering（驾驭工程）系统性学习Wiki - Quality Checklist

## 格式规范
- [ ] frontmatter使用YAML（---）格式，不使用+++（TOML）
- [ ] 所有文件包含id/title/source/x-toml-ref四个必填字段
- [ ] x-toml-ref路径层级计算正确（4层上级../../../../.meta/toml/...）
- [ ] 链接使用相对路径，无file:///绝对路径
- [ ] 文件名符合kebab-case规范，纯英文无中文
- [ ] 原子文件编号正确（00-到09-，两位数字前缀）
- [ ] 标题层级从h1开始，无跳级（# → ## → ###）

## 内容完整性
- [ ] 核心公式"Agent = Model + Harness"准确记录
- [ ] 三代范式演进（Prompt→Context→Harness）完整阐述，含对比表格
- [ ] "模型是CPU，Harness是操作系统"类比包含在内
- [ ] 四条反直觉铁律全部记录，每条含"本能反应vs Harness真相"对比
- [ ] 六大工程模式全部记录，每个模式含核心问题/做法/案例三要素
- [ ] 悟空AI招聘案例完整：第一版问题、第二版架构、五条铁律落点、六维度对比表、三条血泪经验
- [ ] 三层硬护栏（白名单工具/Linter/Agent审稿）描述清晰
- [ ] 行业标杆地图五个案例全部包含，对比表格完整
- [ ] 四大未来趋势记录完整，每条含可证伪条件
- [ ] 六条心法表格准确
- [ ] "为野马造高速公路"核心隐喻包含在结语中

## 关键数据准确性
- [ ] LangChain Terminal Bench数据准确：30→5名，52.8→66.5分，标注来源[2]
- [ ] 悟空案例"Agent数量不超过3个"经验法则记录
- [ ] RPA事务边界lock文件机制描述准确
- [ ] 数据来源标注清晰：[1]Mitchell Hashimoto、[2]LangChain官方、[3]专家博客
- [ ] "小团队×大代码量"数字已软化处理，不作为确定性引用

## 批判性思考章节
- [ ] 来源可信度评估客观（阿里技术背书+一手引用）
- [ ] 准确性评估区分一手数据vs内部实测vs公认事实
- [ ] 权威性评估包含作者背景、引用来源级别
- [ ] 时效性评估说明Harness Engineering是2026年当前热点
- [ ] 局限性分析诚实：无公开基准对比、缺失败案例、缺框架深度对比
- [ ] 与SpecWeave本项目的关联映射具体可落地（AGENTS.md/阶段守卫/.agents/scripts/Workspace/多角色）

## 结构完整性
- [ ] 原子化决策已在spec.md明确记录：需要拆分，10个原子文件
- [ ] 索引页harness-engineering-wiki.md存在且有完整导航表
- [ ] 00-overview.md包含背景、学习目标（5条）、前置知识、导航表
- [ ] 术语表包含至少15个关键术语的中英文对照与解释
- [ ] FAQ覆盖8-10个读者常见问题，答案简明准确
- [ ] 资源链接分类清晰：原始资源、一手参考资料、延伸阅读、本项目相关wiki
- [ ] 本项目相关wiki链接使用相对路径且有效

## 子代理产出验收5点检查（强制！每个文件都要验证）
- [ ] ✅ **frontmatter分隔符正确**：使用`---`（YAML），不是`+++`（TOML）
- [ ] ✅ **x-toml-ref存在且路径正确**：指向.meta/toml/镜像路径，相对层级计算正确
- [ ] ✅ **标题层级从h1开始**：文件第一行是`# 标题`，无跳级
- [ ] ✅ **文件名合规**：kebab-case、纯英文、数字前缀正确（原子文件两位数字）
- [ ] ✅ **source溯源字段存在**：派生产物标注原始来源URL

## 元数据验证
- [ ] tags分类准确（包含Harness Engineering/Agent Engineering/Prompt Engineering/Context Engineering/AI Agent等）
- [ ] date字段正确（2026-07-04）
- [ ] status标记正确（draft）
- [ ] x-toml-ref路径全部正确（可通过fix-x-toml-ref.py验证）
- [ ] .meta/toml/镜像路径下TOML文件全部创建（共11个：索引+10个原子文件）

## 自动化验证（必须通过）
- [ ] `python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/harness-engineering-wiki/ --write --create-toml` 执行成功
- [ ] `python .agents/scripts/check-filename-convention.py docs/knowledge/learning/harness-engineering-wiki/` 检查通过
- [ ] `python .agents/scripts/check-links.py docs/knowledge/learning/harness-engineering-wiki/ --check-external` 链接检查通过
- [ ] 索引页文件名规范检查通过
- [ ] docs/knowledge/README.md已更新，添加了新条目

## 提交验证
- [ ] git status确认只有wiki相关文件被添加，无无关文件混入
- [ ] commit message符合Conventional Commits规范：`docs(knowledge): 新增Harness Engineering（驾驭工程）系统性学习Wiki...`
- [ ] 提交单一职责，只包含本次wiki内容
- [ ] 工作区无临时文件、无备份文件遗留
