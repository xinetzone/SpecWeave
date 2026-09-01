# Tasks — create-eastern-western-classics-wiki

> 依赖顺序：T1 → T2/T3/T4/T5（可并行）→ T6 → T7 → T8
> 实施目录：`projects/awesome-okf-xs/doc/bundles/think/sexology/eastern-western-classics-reading/`
> 前置必读：`projects/awesome-okf-xs/.agents/rules/frontmatter.md`（OKF v0.2 frontmatter 规范）+ `think/sexology/classics-reading/` 全套文件作为模板参照（尤其 `concepts/02-eastern-western-classics.md` 的既有概览与对照表）

- [ ] Task 1: R 阶段事实采集与洞察（七概念 R→I）
  - [ ] SubTask 1.1: 读取 awesome-okf-xs frontmatter 规范与 classics-reading 模板（index/facts/insights/log + 各子目录 index），并读取 `concepts/02-eastern-western-classics.md` 与 facts.md F-WEST-033/034 作为基准事实底座
  - [ ] SubTask 1.2: 系统调研《欲经》：kama-shastra 传统与人生三目的、署名与成书年代（3-5 世纪区间）、七品结构、注疏传统、1883 伯顿英译与 Kama Shastra Society、Doniger & Kakar 2002 学术译本、中译状况；产出事实存 `.temp/eastern-western-classics-research/kamasutra-facts.md`
  - [ ] SubTask 1.3: 系统调研《爱经》：奥维德生平定位、哀歌体教谕诗诗学、三卷结构、约前 2 年出版讨论、公元 8 年放逐与"一首诗和一个错误"公案、中世纪禁毁与抄本流传、近代重估、戴望舒等中译；产出事实存 `.temp/eastern-western-classics-research/ars-amatoria-facts.md`
  - [ ] SubTask 1.4: 合并事实 ≥60 条带信源编号，G1 质量门检查（无因果推断词、纯客观描述）；争议条目（成书年代/署名/伯顿参与者/出版年/放逐原因/中译信息）标【待核验】
  - [ ] SubTask 1.5: I 阶段产出 ≥4 条四元组洞察（现象+根因+影响+建议），G2 质量门检查
- [ ] Task 2: 创建 bundle 根与工作文档
  - [ ] SubTask 2.1: 创建 `index.md`（OKF v0.2 frontmatter：type OKF、generated agent:seven-concepts-r-i-e、status draft、stale_after 2027；📚快速导航 + 🚀分读者路径 + 🎯定位对比表（与 classics-reading 通览教程分工）+ 📖学习路径；文末 toctree 引 concepts/index、examples/index、references/index、facts、insights、log）
  - [ ] SubTask 2.2: 创建 `facts.md`（≥60 条事实按五板块分组制表：《欲经》文本/《欲经》译介/《爱经》文本/《爱经》接受/三方对照，【待核验】显式标注）
  - [ ] SubTask 2.3: 创建 `insights.md`（≥4 条四元组洞察 + 知识地图）
  - [ ] SubTask 2.4: 创建 `log.md`（创建日志：日期、结构清单、调研来源）
- [ ] Task 3: 创建 concepts/ 概念文档（9 篇含 index）
  - [ ] SubTask 3.1: `concepts/index.md`（导航表 + hidden toctree 全 8 篇）
  - [ ] SubTask 3.2: `00-kama-shastra-background.md`（人生三目的、kama-shastra 文献谱系、经书体定位）
  - [ ] SubTask 3.3: `01-kamasutra-text.md`（署名与成书年代区间、七品结构、生活百科性质）
  - [ ] SubTask 3.4: `02-kamasutra-commentary.md`（注疏传统与印度本土接受）
  - [ ] SubTask 3.5: `03-kamasutra-translation.md`（1883 伯顿英译 → 20 世纪诸译本 → Doniger & Kakar 2002 → 中译状况）
  - [ ] SubTask 3.6: `04-ovid-context.md`（奥维德生平定位、哀歌体教谕诗诗学、作品序列位置）
  - [ ] SubTask 3.7: `05-ars-amatoria-text.md`（三卷结构、反讽语调、罗马城市细节、出版年代讨论）
  - [ ] SubTask 3.8: `06-ars-amatoria-reception.md`（放逐公案、中世纪禁毁、近代重估、中译）
  - [ ] SubTask 3.9: `07-comparative-reading.md`（三方四维对照表扩展 + 方法论收束）
- [ ] Task 4: 创建 examples/ 实践示例（4 篇含 index）
  - [ ] SubTask 4.1: `examples/index.md`（导航表 + toctree）
  - [ ] SubTask 4.2: `01-first-book.md`（零基础第一本书实操：Doniger & Kakar 译本 vs 伯顿译本 vs 中译的选择指南）
  - [ ] SubTask 4.3: `02-close-reading-demo.md`（精读示范：以《欲经》第一品总论或《爱经》卷一开篇为例演示"原文→译本→研究对照"三步法，学术引介尺度）
  - [ ] SubTask 4.4: `03-reading-plan.md`（分阶段阅读计划：背景→文本→译介/接受→对照四阶）
- [ ] Task 5: 创建 references/ 信源文档（5 篇含 index）
  - [ ] SubTask 5.1: `references/index.md`（信源登记表 + toctree）
  - [ ] SubTask 5.2: `kamasutra-sources.md`（Doniger & Kakar 牛津译本、伯顿译本、印度学术机构页等条目与 URL）
  - [ ] SubTask 5.3: `ars-amatoria-sources.md`（拉丁原文校勘本、权威英译/中译条目、奥维德研究资源 URL）
  - [ ] SubTask 5.4: `research-sources.md`（Doniger 研究著作、奥维德接受史研究、比较研究条目）
  - [ ] SubTask 5.5: `cross-references.md`（关联 bundle 交叉引用：sexology/classics-reading 及其 references/western-classics-sources.md、yangsheng 等）
- [ ] Task 6: 更新导航索引与登记
  - [ ] SubTask 6.1: `think/sexology/index.md`：导航表加行、toctree 加 `eastern-western-classics-reading/index`
  - [ ] SubTask 6.2: `bundles/index.md`：以磁盘实际值核对后 `total_bundles` +1、think 域束数 +1（组数不变）、sexology 行束数与说明更新
  - [ ] SubTask 6.3: `classics-reading/concepts/02-eastern-western-classics.md` 《欲经》节与《爱经》节末各加一处交叉引用链接（不改既有事实与结论）
  - [ ] SubTask 6.4: `.trae/specs/README.md` 与 `standards-tools/README.md` 登记本 spec
- [ ] Task 7: 质量门验证
  - [ ] SubTask 7.1: 在 `projects/awesome-okf-xs` 运行 `invoke gates.toctrees`（零断链零孤立）
  - [ ] SubTask 7.2: 运行 `invoke gates.utf8`
  - [ ] SubTask 7.3: 运行 `invoke build`（Sphinx 构建成功；警告仅允许来自其他既有 bundle）
- [ ] Task 8: V 阶段独立评审与修复
  - [ ] SubTask 8.1: 委托新鲜上下文 general_purpose_task 只读四视角评审（事实准确性/新人可入门性/定位与边界/时效与规范），结果写入本 spec 目录 `review.md`
  - [ ] SubTask 8.2: 修复评审 fail 项（如有），复跑 Task 7 质量门
  - [ ] SubTask 8.3: 清理 `.temp/eastern-western-classics-research/` 中间产物，收尾总结（不执行 git commit）

# Task Dependencies

- Task 1 是全部任务的前置（事实底座）
- Task 2/3/4/5 依赖 Task 1，相互可并行
- Task 6 依赖 Task 2-5 全部文件就位
- Task 7 依赖 Task 6
- Task 8 依赖 Task 7
