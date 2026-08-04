# Anthropic Financial Services 金融Agent仓库 Wiki教程 - Quality Checklist

## 格式规范
- [ ] frontmatter使用YAML（---）格式分隔，而非+++（TOML）
- [ ] frontmatter包含title/source/date/tags四个核心字段
- [ ] fix-x-toml-ref.py执行后x-toml-ref字段正确添加，路径层级准确
- [ ] 文件名使用kebab-case：anthropic-financial-services-wiki.md，纯英文无中文
- [ ] 标题层级从h1开始，无跳级（# → ## → ###）
- [ ] 代码块标注正确语言（bash等）
- [ ] 所有内部链接使用相对路径

## 内容完整性
- [ ] 包含11个章节：概述/架构/10大功能/快速上手/源码结构/定制化/法律免责/评估/见解/FAQ/资源
- [ ] 核心观点完整保留：四层架构设计、10大功能模块无遗漏
- [ ] GitHub 3.2万Star数据准确
- [ ] 四层架构（Agent/Skill/Slash Command/MCP Connector）每层都有清晰解释
- [ ] 10大功能模块每个都有独立小节，价值和适用场景说明清楚
- [ ] 金融专业术语（DCF/LBO/comps/KYC/GL Reconciler等）都有通俗解释
- [ ] /debug-model的具体错误示例（WACC硬编码/Exit Multiple共用单元格/债务余额未回链）完整保留

## 快速上手与实操
- [ ] 插件市场添加命令正确：claude plugin marketplace add anthropics/financial-services
- [ ] 核心插件安装命令正确：financial-analysis@claude-for-financial-services
- [ ] 明确建议"先装financial-analysis，再按场景加垂直插件"，不要一上来全装
- [ ] 明确提醒"MCP连接器是企业集成路线图，不是个人开发者白嫖数据包"
- [ ] 5种企业定制化方法（换数据连接器/加公司上下文/用自己的模板/调整代理范围/加自定义工作流）每种都有说明

## 法律合规与客观性
- [ ] 法律免责声明位置显眼，不一笔带过
- [ ] 明确说明"不构成投资、法律、税务或会计建议"
- [ ] 明确强调"所有输出只是draft，必须经过合格专业人士审核签字"
- [ ] 明确说明"仓库是模板不是成品，需要投入定制化和对接"
- [ ] 没有夸大功能或做不实承诺
- [ ] 客观说明个人开发者使用限制（付费数据源问题）

## 子代理产出验收5点检查（强制！）
- [ ] ✅ frontmatter分隔符正确：使用`---`（YAML），不是`+++`（TOML）
- [ ] ✅ x-toml-ref存在且路径正确：指向.meta/toml/镜像路径，相对层级计算正确（运行fix-x-toml-ref.py验证）
- [ ] ✅ 标题层级从h1开始：文件第一行是`# 标题`，无跳级
- [ ] ✅ 文件名合规：kebab-case、纯英文、无中文
- [ ] ✅ source溯源字段存在：派生产物标注原始来源URL（微信公众号文章+GitHub仓库）

## 知识库索引
- [ ] docs/knowledge/README.md中learning分类已添加本Wiki条目
- [ ] 条目格式与现有条目一致（标题/摘要/日期/标签）
- [ ] 标签分类准确（anthropic、financial-services、ai-agent、claude、mcp、vertical-industry、fintech等）

## 自动化验证
- [ ] python .agents/scripts/check-filename-convention.py 通过
- [ ] python .agents/scripts/check-links.py 通过（含内部锚点链接）
- [ ] python .agents/scripts/fix-x-toml-ref.py --file docs/knowledge/learning/anthropic-financial-services-wiki.md --write --create-toml 执行成功
- [ ] git status确认无临时文件（.temp/目录内容不提交）

## 原子提交
- [ ] commit message符合Conventional Commits：docs(knowledge): 新增Anthropic Financial Services金融Agent仓库学习Wiki教程
- [ ] 单次提交单一职责，只包含本Wiki相关文件
- [ ] 提交包含：新Wiki文件 + README.md索引更新 + TOML元数据文件
