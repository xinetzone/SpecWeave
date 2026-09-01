# Tasks — create-sexology-classics-wiki

> 依赖顺序：T1 → T2/T3（可并行）→ T4 → T5 → T6 → T7 → T8
> 实施目录：`projects/awesome-okf-xs/doc/bundles/think/sexology/`

- [x] Task 1: 创建 sexology 分组入口
  - [x] SubTask 1.1: 创建 `think/sexology/index.md`（仿 laozi/index.md：分组简介表 + hidden toctree 含 `classics-reading/index`）
- [x] Task 2: 创建 bundle 根与工作文档
  - [x] SubTask 2.1: 创建 `classics-reading/index.md`（OKF v0.2 frontmatter：type OKF、generated agent:seven-concepts-r-i-e、verified process:seven-concepts-v、status draft→stable、stale_after 2027；📚快速导航 + 🚀分读者路径 + 🎯定位对比表 + 📖学习路径；文末 toctree 引 concepts/index、examples/index、references/index、facts、insights、log）
  - [x] SubTask 2.2: 创建 `facts.md`（104 条事实按 F-ANCIENT/F-WEST/F-CHINA-MODERN 分组制表，【待核验】条目显式标注，含已核验纠正项说明）
  - [x] SubTask 2.3: 创建 `insights.md`（4 条四元组洞察：范式入口/出土-辑佚-回收-重建链条/译本门槛/权力共构 + 知识地图）
  - [x] SubTask 2.4: 创建 `log.md`（创建日志，记录日期、结构清单、调研来源）
- [x] Task 3: 创建 concepts/ 概念文档（9 篇）
  - [x] SubTask 3.1: `concepts/index.md`（分节导航表：入门/范式板块/方法视角 + hidden toctree 全 9 篇）
  - [x] SubTask 3.2: `00-reading-map.md`（四大范式入口 + 读者自测 + 阅读顺序建议）
  - [x] SubTask 3.3: `01-ancient-china.md`（马王堆房中简帛、汉志八家、医心方辑佚、素女经/洞玄子/玉房秘诀、双梅景闇丛书、房中医学化、明清小说性书写；成书年代仅区间表述）
  - [x] SubTask 3.4: `02-eastern-western-classics.md`（《欲经》与奥维德《爱经》提要）
  - [x] SubTask 3.5: `03-foundations.md`（克拉夫特-埃宾、蔼理士、弗洛伊德、赫希菲尔德、1933 焚书；《性精神病态》译本状况如实说明）
  - [x] SubTask 3.6: `04-modern-science.md`（金赛、马斯特斯与约翰逊、《人类性功能障碍》；版权著作仅提要）
  - [x] SubTask 3.7: `05-feminism-construction.md`（OBOS、米利特、福柯、鲁宾、巴特勒；鲁宾中译状况如实标注）
  - [x] SubTask 3.8: `06-china-modern.md`（潘光旦译注、1955《性的知识》、吴阶平、阮芳赋《性知识手册》、刘达临与博物馆沿革、潘绥铭、李银河、学科建制；争议年份按 spec 要求处理）
  - [x] SubTask 3.9: `07-translations.md`（译本与版本选择指南，含《性学三论》多译本提醒）
  - [x] SubTask 3.10: `08-censorship-power.md`（禁书史视角：1933 焚书、张竞生、审查与学科化）
- [x] Task 4: 创建 examples/ 实践示例（3 篇）
  - [x] SubTask 4.1: `examples/index.md`（导航表 + toctree）
  - [x] SubTask 4.2: `01-entry-path.md`（零基础第一本书实操：从 00-reading-map 到选定第一本著作）
  - [x] SubTask 4.3: `02-ancient-text-reading.md`（古典文献对照阅读示例：以《素女经》佚文为例演示"提要看门→原文节选→现代解读"三步法）
  - [x] SubTask 4.4: `03-reading-plan.md`（六板块分阶段阅读计划）
- [x] Task 5: 创建 references/ 信源文档（5 篇）
  - [x] SubTask 5.1: `references/index.md`（信源登记表 + toctree）
  - [x] SubTask 5.2: `ancient-china-sources.md`（湖南博物院马王堆页、复旦简帛集成、林富士、孙孝忠、李零等 URL）
  - [x] SubTask 5.3: `western-classics-sources.md`（金赛研究所所史、德国联邦档案馆、伦敦大屠杀纪念馆、OBOS 官方、法兰西公学院福柯书目等 URL）
  - [x] SubTask 5.4: `china-modern-sources.md`（上海大学刘达临页、中国性学会、中国新闻周刊潘绥铭、北大期刊导航、教育部纲要、UNESCO ITGSE、WAS 等 URL）
  - [x] SubTask 5.5: `institutions-journals.md`（机构/期刊/学会专题信源）
  - [x] SubTask 5.6: `further-reading.md`（延伸阅读与关联 bundle 交叉引用）
- [x] Task 6: 更新导航索引
  - [x] SubTask 6.1: `think/index.md`：导航表加 sexology 行、toctree 加 `sexology/index`
  - [x] SubTask 6.2: `bundles/index.md`：计数 286→287、32→33、think "5 束 · 2 组"→"6 束 · 3 组"、表格加行
  - [x] SubTask 6.3: `.trae/specs/README.md` 主题看板登记本 spec
- [x] Task 7: 质量门验证
  - [x] SubTask 7.1: 在 `projects/awesome-okf-xs` 运行 `invoke gates.toctrees`（零断链零孤立）
  - [x] SubTask 7.2: 运行 `invoke gates.utf8`
  - [x] SubTask 7.3: 运行 `invoke build`（Sphinx 构建成功）
- [x] Task 8: V 阶段独立评审与修复
  - [x] SubTask 8.1: 委托新鲜上下文 general_purpose_task 只读四视角评审，结果写入本 spec 目录 `review.md`
  - [x] SubTask 8.2: 修复评审 fail 项（如有），复跑 Task 7 质量门
  - [x] SubTask 8.3: 收尾总结（不执行 git commit）
- [x] Task 9: 交付后沉淀（2026-08-31 回写）
  - [x] SubTask 9.1: 里程碑复盘报告入库 `.agents/docs/retrospective/reports/concepts/milestone/retrospective-sexology-classics-wiki-20260830.md`（2026-08-30，随主仓库提交）
  - [x] SubTask 9.2: 复盘模式 1/2 沉淀为 patterns/ 文档：`documentation-patterns/source-trace-consistency-check.md`、`documentation-patterns/version-discrepancy-arbitration.md`（均 L1/draft，validation_count=1）
  - [x] SubTask 9.3: 洞察 I-3 沉淀为 `code-patterns/submodule-detached-head-ff-only-landing.md`（L2，validation_count=3，三会话案例），主仓库提交 `83c9a58e0`

# Task Dependencies

- Task 1 → Task 2、Task 3、Task 4、Task 5 依赖 Task 1 的分组目录
- Task 2/3/4/5 相互可并行
- Task 6 依赖 Task 1-5 全部文件就位
- Task 7 依赖 Task 6
- Task 8 依赖 Task 7
- Task 9 为交付后回写任务（沉淀记录），不参与 T1-T8 执行顺序
