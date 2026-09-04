# 旋元佑英语语法 OKF Wiki 教程 - Verification Checklist

## R阶段质量门（G1：事实无推断）
- [ ] facts.md 包含所有30个源文件的完整清单（路径、主题分类、字数估计）
- [ ] 事实表述纯客观，无"用于"/"目的是"/"设计为"等因果推断词
- [ ] guide.md 内容已读取，定位明确（导读/使用指南/其他）
- [ ] appendix/terminology.md 内容已读取，定位明确（概念/参考/其他）
- [ ] 所有25章正文+序+引言+指南+术语表共计30个文件全部盘点

## I阶段质量门（G2：洞察四元组完整）
- [ ] insights.md 包含3-5个核心洞察，每个洞察具备陈述+证据+反常识+行动四元组
- [ ] 知识地图分组逻辑合理（入门/基础/进阶/高级/附录）
- [ ] 学习路径设计清晰，建议按原书01-25章节顺序
- [ ] 文件名编号规则确定（NN-topic-name.md），所有文件分配编号
- [ ] 章末「相关概念」交叉链接策略明确

## E阶段质量门（G3：信源先行+分批生成+Index最后）
- [ ] references/ 目录和信源文件**先于** concepts/ 生成（信源先行原则）
- [ ] references/ 包含每个原始文件的信源登记，元数据准确（路径/作者/来源）
- [ ] references/facts.md 和 references/insights.md 已就位
- [ ] references/index.md 无 frontmatter
- [ ] 每批生成≤7个文档，未出现单批>7文件情况
- [ ] 所有概念文档包含完整frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）
- [ ] 所有概念文档 sources 字段指向有效 references/ 文件
- [ ] MyST语法全部转换：无 {toctree}、{note}、```{ 等残留指令
- [ ] {note} admonition 转换为标准 Markdown 引用块或粗体提示
- [ ] 代码块标注语言（如有）
- [ ] 表格、列表、例句、下划线强调等格式完整保留
- [ ] examples/ 目录已创建，examples/index.md 无 frontmatter
- [ ] examples/extensive-reading-materials.md（广读材料推荐示例）
- [ ] **Index最后写**：根index.md和concepts/index.md在所有内容文档完成后才生成
- [ ] concepts/index.md 无 frontmatter，列出所有概念文档
- [ ] 根 index.md 包含 okf_version: "0.2" frontmatter
- [ ] 根 index.md 按学习路径分组导航（基础→进阶→高级）
- [ ] log.md 记录创建时间、来源、转换方法

## V阶段质量门（G4：验证无虚构+链接完整）
- [ ] 目录结构完整：index.md、log.md、concepts/、examples/、references/ 齐全
- [ ] 各子目录（concepts/examples/references）均有 index.md
- [ ] Grep检查：无 {toctree 残留 → 0命中
- [ ] Grep检查：无 {note 残留 → 0命中
- [ ] Grep检查：无 ```{ 开头的代码块 → 0命中
- [ ] 所有交叉链接使用 `/` 开头的 bundle-relative 路径
- [ ] Grep检查：无 `../` 相对路径链接 → 0命中
- [ ] 所有 `/` 开头链接的目标文件实际存在
- [ ] 每个概念文档结尾有「## 相关概念」章节
- [ ] 抽样检查（3-5个文件）：内容与原始文档一致，无遗漏段落/例句/表格
- [ ] 无虚构内容（所有内容均可溯源到原始文档）
- [ ] 英文术语首次出现保留原文括号注释（与原文一致）
- [ ] 文档主体为中文，与原文一致

## C阶段收尾验证
- [ ] 总文件数核对：约30+内容文件+索引+日志，无缺失无多余
- [ ] 根index.md中列出的所有文档都实际存在
- [ ] concepts/index.md中列出的所有概念文件都实际存在
- [ ] log.md最终状态已更新
- [ ] Bundle路径位于 bundles/chaos/english-grammar/（与现有bundle组织一致）
- [ ] vendor/flexloop/ 内原始文件未被修改
