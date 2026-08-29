# EPUB 转 Markdown 转换方案调研 - The Implementation Plan

> 方法论编排：场景4 知识沉淀（R→I→E→V→C）。R=事实采集，I=洞察，E=萃取推荐方案，V=对抗审查，C=报告入库交付。

## [x] Task 0: 需求界定与资料清单
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 明确调研范围：工具清单（pandoc、calibre/ebook-convert、mupdf、pypandoc、ebooklib、其他），复杂元素维度（图片/表格/公式/代码块/目录/样式），场景维度
  - 收集各工具官方文档、版本信息、许可证、维护活跃度
  - 设计对比维度评分表格框架
- **Acceptance Criteria Addressed**: 需求覆盖完整
- **Test Requirements**:
  - TR-0.1: 工具清单≥5个，覆盖 CLI、Python 库两种形态
  - TR-0.2: 对比维度涵盖功能/元素/性能/兼容性/优缺点
- **Notes**: 遵循 G1 事实无因果词——本任务仅收集客观资料，不做判断

## [x] Task 1: R 阶段——工具客观事实采集
- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 逐工具采集客观规格：支持格式、核心命令、输出 markdown 扩展（GFM/CommonMark/Pandoc AST）、跨平台、许可证、维护活跃度（star/更新频率）
  - pandoc：以 markdown 格式输出能力（gfm/commonmark/panflute 过滤器），MathML→LaTeX 公式
  - calibre：ebook-convert 支持 epub→md 吗？实际为 epub→其他 → 澄清其到 Markdown 的真实能力（常经 md writer 或缺省）
  - Python 生态：pypandoc（pandoc 包装）、ebooklib（解析 EPUB→OPF/content）、epub2txt、html2text（XHTML→MD）、markdownify 等
  - 采集版本号、命令示例、链接（官方文档 URL）
- **Acceptance Criteria Addressed**: R 输出事实清单，满足 G1
- **Test Requirements**:
  - TR-1.1: 事实清单≥20条客观条目，每条含来源
  - TR-1.2: 无"因为/所以/导致/更好/更差"等判断词，纯客观描述
- **Notes**: 使用 WebSearch/WebFetch 采集官方文档与公开资料；记录 URL 供溯源

## [x] Task 2: 复杂元素保真对比调研
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 调研各工具对图片（外链/OEBPS 本地资源/{data-uri}）、表格、公式（MathML/LaTeX/OMML）、代码块（语法高亮标注）、多级目录（nav/toc）、样式（CSS 内联/class）的处理策略
  - 补充实测（若环境可用）：准备代表性 EPUB 样例，运行对比输出
  - 若本环境无法实测，则基于官方行为描述与社区报告归纳，并明确标注"基于文档/社区，未经本地实测"
- **Acceptance Criteria Addressed**: G1 事实 + 元素维度覆盖
- **Test Requirements**:
  - TR-2.1: 每种元素均有各工具处理策略说明
  - TR-2.2: 事实来源可溯源，区分"实测结论"与"文档推断"
- **Notes**: 诚实标注证据强度，避免过度引申（G1 反模式）

## [x] Task 3: I 阶段——洞察提取（四元组）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 基于事实清单提炼≥3条核心洞察，每条含完整四元组：陈述、证据（引用事实编号）、反常识、行动
  - 洞察维度独立不重叠，例如：命令行工具 vs Python 库的复杂度权衡；公式/表格保真是最大分化点；批量处理与定制化的取舍
- **Acceptance Criteria Addressed**: G2 洞察四元组完整
- **Test Requirements**:
  - TR-3.1: 洞察≥3条，每条含四元组
  - TR-3.2: 每条洞察的反常识点挑战了默认假设（如"最流行的不等于最合适"）
- **Notes**: 洞察必须引用事实编号（F-xxx），避免正确废话

## [x] Task 4: E 阶段——推荐方案与适用场景矩阵
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 设计「工具 × 典型场景」适用矩阵：普通文本书、技术/代码书、学术公式书、画册/图片密集、批量处理、需要深度定制
  - 为每个场景明确：推荐主工具+备选、理由、推荐理由的证据链、操作命令/代码步骤、已知局限与规避
  - 提炼可选"复用模式"候选（如"EPUB→MD 三角色选型认知"）供后续沉淀
- **Acceptance Criteria Addressed**: G3 模式可迁移、推荐可执行
- **Test Requirements**:
  - TR-4.1: 每个典型场景有明确推荐、操作步骤、注意事项
  - TR-4.2: 矩阵6类维度×≥5工具可读性良好
- **Notes**: E 阶段产物为报告核心章节，须可直接执行

## [x] Task 5: V 阶段——对抗审查推荐结论
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 对推荐结论与报告草案执行 4 视角对抗审查：魔鬼代言人、新人、老板、未来
  - 魔鬼代言人：推荐是否最优？数据是否"最优场景"偏差？是否会踩流行陷阱？
  - 新人：术语是否解释？步骤是否缺前置条件？不同平台是否一致？
  - 老板：学习成本 vs 收益？批量/生产可用？风险与最坏情况？
  - 未来：工具是否会失维护？格式趋势变化结论是否仍成立？
  - 汇总审查意见≥5条，采纳≥2条修正报告
- **Acceptance Criteria Addressed**: V门
- **Test Requirements**:
  - TR-5.1: 审查意见≥5条，每条有具体攻击点（非客套）
  - TR-5.2: 至少采纳2条意见并落实到报告修改
- **Notes**: V 必须在 E 之后；禁止表演式审查

## [x] Task 6: 自研方案评估与代码骨架
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 评估 Python 自研方案：ebooklib（读取 EPUB 资源+逻辑结构）→ 提取 content.opf / chapter HTML → html2text / markdownify / 自写遍历转换
  - pypandoc 包装方案；BeautifulSoup 抽取表格/公式方案
  - 提供最小可运行代码骨架（函数级示意），注明依赖与运行环境
  - 与成熟工具的成本/收益对比，给出"何时自研、何时用现成"判据
- **Acceptance Criteria Addressed**: 自研可行性评估
- **Test Requirements**:
  - TR-6.1: 提供≥1个可行技术路线与代码骨架
  - TR-6.2: 明确自研 vs 现成工具的适用边界
- **Notes**: 代码骨架为报告章节示意，不要求在本 spec 内落地为生产模块

## [x] Task 7: 报告汇聚与原子交付
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Description**:
  - 汇聚全部调研结论，撰写完整对比分析报告（Markdown），路径：`docs/knowledge/operations/epub-to-markdown-conversion-research.md`（若该分类不合适则按知识库结构调整）
  - 报告结构：执行摘要、工具概述对比表、复杂元素对比、问题与方案、性能对比、编程自研方案、推荐与适用场景矩阵、操作步骤、来源附录
  - 报告 frontmatter 标注 source 溯源
  - 原子交付（C 阶段）：遵循 Conventional Commits 提交
- **Acceptance Criteria Addressed**: 完整报告交付
- **Test Requirements**:
  - TR-7.1: 报告含全部调研章节，内部链接用相对路径
  - TR-7.2: 结论与事实/洞察/对抗审查结果一致，无未消除的过强断言
  - TR-7.3: 提交信息符合 Conventional Commits，中文描述为什么
- **Notes**: C 阶段通过 atomic-commit-cmd 执行原子提交

# Task Dependencies
- Task 1、2 依赖 Task 0；Task 3 依赖 Task 1、2（可并行采集后合并）
- Task 4 依赖 Task 3；Task 5 依赖 Task 4
- Task 6 依赖 Task 4（可与 Task 5 并行）
- Task 7 依赖 Task 5、6