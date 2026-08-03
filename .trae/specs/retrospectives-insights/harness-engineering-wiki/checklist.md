# Harness Engineering（驾驭工程）系统性学习Wiki - Quality Checklist

## 格式规范
- [x] frontmatter使用YAML（---）格式，不使用+++（TOML）
- [x] 所有文件包含id/title/source/x-toml-ref四个必填字段
- [x] x-toml-ref路径层级计算正确（4层上级../../../../.meta/toml/...）
- [x] 链接使用相对路径，无file:///绝对路径
- [x] 文件名符合kebab-case规范，纯英文无中文
- [x] 原子文件编号正确（00-到09-，两位数字前缀）
- [x] 标题层级从h1开始，无跳级（# → ## → ###）

## 内容完整性
- [x] 核心公式"Agent = Model + Harness"准确记录
- [x] 三代范式演进（Prompt→Context→Harness）完整阐述，含对比表格
- [x] "模型是CPU，Harness是操作系统"类比包含在内
- [x] 四条反直觉铁律全部记录，每条含"本能反应vs Harness真相"对比
- [x] 六大工程模式全部记录，每个模式含核心问题/做法/案例三要素
- [x] 悟空AI招聘案例完整：第一版问题、第二版架构、五条铁律落点、六维度对比表、三条血泪经验
- [x] 三层硬护栏（白名单工具/Linter/Agent审稿）描述清晰
- [x] 行业标杆地图五个案例全部包含，对比表格完整
- [x] 四大未来趋势记录完整，每条含可证伪条件
- [x] 六条心法表格准确
- [x] "为野马造高速公路"核心隐喻包含在结语中

## 关键数据准确性
- [x] LangChain Terminal Bench数据准确：30→5名，52.8→66.5分，标注来源[2]
- [x] 悟空案例"Agent数量不超过3个"经验法则记录
- [x] RPA事务边界lock文件机制描述准确
- [x] 数据来源标注清晰：[1]Mitchell Hashimoto、[2]LangChain官方、[3]专家博客
- [x] "小团队×大代码量"数字已软化处理，不作为确定性引用

## 批判性思考章节
- [x] 来源可信度评估客观（阿里技术背书+一手引用）
- [x] 准确性评估区分一手数据vs内部实测vs公认事实
- [x] 权威性评估包含作者背景、引用来源级别
- [x] 时效性评估说明Harness Engineering是2026年当前热点
- [x] 局限性分析诚实：无公开基准对比、缺失败案例、缺框架深度对比
- [x] 与SpecWeave本项目的关联映射具体可落地（AGENTS.md/阶段守卫/.agents/scripts/Workspace/多角色）

## 结构完整性
- [x] 原子化决策已在spec.md明确记录：需要拆分，10个原子文件
- [x] 索引页harness-engineering-wiki.md存在且有完整导航表
- [x] 00-overview.md包含背景、学习目标（5条）、前置知识、导航表
- [x] 术语表包含至少15个关键术语的中英文对照与解释
- [x] FAQ覆盖8-10个读者常见问题，答案简明准确
- [x] 资源链接分类清晰：原始资源、一手参考资料、延伸阅读、本项目相关wiki
- [x] 本项目相关wiki链接使用相对路径且有效

## 子代理产出验收5点检查（强制！每个文件都要验证）
- [x] ✅ **frontmatter分隔符正确**：使用`---`（YAML），不是`+++`（TOML）
- [x] ✅ **x-toml-ref存在且路径正确**：指向.meta/toml/镜像路径，相对层级计算正确
- [x] ✅ **标题层级从h1开始**：文件第一行是`# 标题`，无跳级
- [x] ✅ **文件名合规**：kebab-case、纯英文、数字前缀正确（原子文件两位数字）
- [x] ✅ **source溯源字段存在**：派生产物标注原始来源URL

## 元数据验证
- [x] tags分类准确（包含Harness Engineering/Agent Engineering/Prompt Engineering/Context Engineering/AI Agent等）
- [x] date字段正确（2026-07-04）
- [x] status标记正确（draft）
- [x] x-toml-ref路径全部正确（可通过fix-x-toml-ref.py验证）
- [x] .meta/toml/镜像路径下TOML文件全部创建（共11个：索引+10个原子文件）

## 自动化验证（必须通过）
- [x] `python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/harness-engineering-wiki/ --write --create-toml` 执行成功
- [x] `python .agents/scripts/check-filename-convention.py docs/knowledge/learning/harness-engineering-wiki/` 检查通过
- [x] `python .agents/scripts/check-links.py docs/knowledge/learning/harness-engineering-wiki/ --check-external` 链接检查通过
- [x] 索引页文件名规范检查通过
- [x] docs/knowledge/README.md已更新，添加了新条目

## 提交验证
- [x] git status确认只有wiki相关文件被添加，无无关文件混入
- [x] commit message符合Conventional Commits规范：`docs(learning): 新增Harness Engineering（驾驭工程）系统性学习Wiki...`
- [x] 提交单一职责，只包含本次wiki内容
- [x] 工作区无临时文件、无备份文件遗留

---

## 验证结果记录

### 自动化检查结果
- **frontmatter检查**：0错误，10警告（YAML字段category/date建议迁移到TOML元数据文件，不影响验收通过）
- **文件名规范检查**：✅ 通过，所有10个原子文件+索引页命名合规
- **链接检查**：初始发现1个断链（zleap-agent-harness-learning-analysis.md不存在），修复后最终0断链
- **TOML文件生成**：11个TOML文件全部创建成功（索引页+10个原子文件）
- **知识库索引更新**：docgen自动完成，无需手动编辑，docs/knowledge/README.md更新1行

### 子代理一次性生成验证
- 10个原子文件一次性生成完成
- 5点验收检查全部通过
- frontmatter分隔符、x-toml-ref路径、标题层级、文件名规范、source字段均符合要求

### 网页提取方式
- 原始网页使用defuddle工具提取（WebFetch失败后切换到defuddle）
- 内容提取完整，无信息丢失

### 修复记录汇总
1. 09-resources.md断链修复（移除不存在的zleap-agent-harness-learning-analysis.md引用）
2. 09-resources.md内部wiki链接路径修正（从指向子目录原子文件改为指向父目录wiki索引页）
