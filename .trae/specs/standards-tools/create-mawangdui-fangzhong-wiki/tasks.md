# Tasks — create-mawangdui-fangzhong-wiki

> 依赖顺序：T1 → T2/T3/T4/T5（可并行）→ T6 → T7 → T8
> 实施目录：`projects/awesome-okf-xs/doc/bundles/think/sexology/mawangdui-fangzhong-reading/`
> 前置必读：`projects/awesome-okf-xs/.agents/rules/frontmatter.md`（OKF v0.2 frontmatter 规范）+ `think/sexology/classics-reading/` 全套文件作为模板参照

- [x] Task 1: R 阶段事实采集与洞察（七概念 R→I）
  - [x] SubTask 1.1: 读取 awesome-okf-xs frontmatter 规范与 classics-reading 模板（index/facts/insights/log + 各子目录 index）
  - [x] SubTask 1.2: 系统调研马王堆房中简帛：出土背景、文本群（十问/合阴阳/天下至道谈/养生方/房内记/胎产书）、核心概念（七损八益/十动十节等）、整理出版史（1974 小组→2014 集成→2024 修订本）、研究著作（李零/周贻谋/朱越利/李建民/海外汉学），产出 ≥80 条带信源事实，存 `.temp/mawangdui-fangzhong-facts.md`
  - [x] SubTask 1.3: G1 质量门检查：事实无因果推断词（"因为/导致/所以"），纯客观描述；争议条目（墓主身份/房内记分合/拟题问题/周贻谋版次/海外丛书范围）标【待核验】
  - [x] SubTask 1.4: I 阶段产出 ≥4 条四元组洞察（现象+根因+影响+建议），G2 质量门检查
- [x] Task 2: 创建 bundle 根与工作文档
  - [x] SubTask 2.1: 创建 `index.md`（OKF v0.2 frontmatter：type OKF、generated agent:seven-concepts-r-i-e、status draft、stale_after 2027；📚快速导航 + 🚀分读者路径 + 🎯定位对比表（与 classics-reading 分工）+ 📖学习路径；文末 toctree 引 concepts/index、examples/index、references/index、facts、insights、log）
  - [x] SubTask 2.2: 创建 `facts.md`（≥80 条事实按板块分组制表，【待核验】显式标注）
  - [x] SubTask 2.3: 创建 `insights.md`（≥4 条四元组洞察 + 知识地图）
  - [x] SubTask 2.4: 创建 `log.md`（创建日志：日期、结构清单、调研来源）
- [x] Task 3: 创建 concepts/ 概念文档（9 篇含 index）
  - [x] SubTask 3.1: `concepts/index.md`（导航表 + hidden toctree 全 8 篇）
  - [x] SubTask 3.2: `00-excavation-background.md`（发掘史 1972-1974、三号墓下葬前 168 年、五十余种简帛总览、四种养生房中简书定位）
  - [x] SubTask 3.3: `01-text-corpus.md`（三种竹简 + 养生方/房内记/胎产书的形制、篇题由来、内容结构）
  - [x] SubTask 3.4: `02-seven-losses-eight-benefits.md`（天下至道谈七损八益 + 与《素问》悬案对照）
  - [x] SubTask 3.5: `03-he-yin-yang-techniques.md`（合阴阳术语体系：戏道/十动/十节/十修/八动/十已之征，学术界定口径）
  - [x] SubTask 3.6: `04-shiwen-dialogue.md`（十问问答结构、已佚古房中书线索、气-精-神-神明递进）
  - [x] SubTask 3.7: `05-theoretical-framework.md`（气论主干/精气论/阴阳学说/天人相参，学术综述口径）
  - [x] SubTask 3.8: `06-editorial-history.md`（1974 整理小组→2014 集成初版→2024 修订本：重写篇目/近千处修订/新缀残片）
  - [x] SubTask 3.9: `07-research-landscape.md`（李零《中国方术考》第七章、周贻谋、朱越利、李建民、Harper 与日本译注丛书；入门路径建议）
- [x] Task 4: 创建 examples/ 实践示例（4 篇含 index）
  - [x] SubTask 4.1: `examples/index.md`（导航表 + toctree）
  - [x] SubTask 4.2: `01-first-book.md`（零基础第一本书实操：从集成修订本/周贻谋释译本入手的选择指南）
  - [x] SubTask 4.3: `02-close-reading-demo.md`（精读示范：以《天下至道谈》七损八益段为例演示"释文→注释→研究对照"三步法，学术引介尺度）
  - [x] SubTask 4.4: `03-reading-plan.md`（分阶段阅读计划：背景→文本→理论→研究史四阶）
- [x] Task 5: 创建 references/ 信源文档（5 篇含 index）
  - [x] SubTask 5.1: `references/index.md`（信源登记表 + toctree）
  - [x] SubTask 5.2: `excavation-sources.md`（湖南博物院马王堆专题页、复旦出土文献中心、50 周年研讨会报道等 URL）
  - [x] SubTask 5.3: `editorial-sources.md`（《长沙马王堆汉墓简帛集成》初版/修订本出版信息、中华书局/复旦资讯中心 URL）
  - [x] SubTask 5.4: `research-sources.md`（李零《中国方术考》、周贻谋著作、朱越利论文、李建民中研院页、海外译注丛书等条目）
  - [x] SubTask 5.5: `cross-references.md`（关联 bundle 交叉引用：sexology/classics-reading、laozi/boshu-reading、yangsheng 等）
- [x] Task 6: 更新导航索引与登记
  - [x] SubTask 6.1: `think/sexology/index.md`：导航表加行、toctree 加 `mawangdui-fangzhong-reading/index`
  - [x] SubTask 6.2: `bundles/index.md`：计数 289→290、think "8 束 · 5 组"→"9 束 · 5 组"、sexology 行说明更新
  - [x] SubTask 6.3: `classics-reading/concepts/01-ancient-china.md` 马王堆节末加交叉引用链接
  - [x] SubTask 6.4: `.trae/specs/README.md` 与 `standards-tools/README.md` 登记本 spec
- [x] Task 7: 质量门验证
  - [x] SubTask 7.1: 在 `projects/awesome-okf-xs` 运行 `invoke gates.toctrees`（bundle 级零断链零孤立；全树 20 处问题均属并行会话的 `think/medicine/ishinpo-reading`，与本 bundle 无关）
  - [x] SubTask 7.2: 运行 `invoke gates.utf8`（bundle 22 文件 + 全树 5922 文件均通过）
  - [x] SubTask 7.3: 运行 `invoke build`（读取阶段 100% 完成零警告，本 bundle 22 文件全部解析通过；写入阶段 5922 文件耗时长，脱离会话后台继续运行作最终确认，日志 `.temp/gate-build2.txt`）
- [x] Task 8: V 阶段独立评审与修复
  - [x] SubTask 8.1: 委托新鲜上下文 general_purpose_task 只读四视角评审，结果写入本 spec 目录 `review.md`
  - [x] SubTask 8.2: 评审结果 0 fail / 0 warn，无需修复；质量门复验结果见 Task 7
  - [x] SubTask 8.3: 清理 `.temp/` 中间产物（mawangdui-fangzhong-facts/insights.md + 3 个辅助脚本已删），收尾总结（不执行 git commit）

# Task Dependencies

- Task 1 是全部任务的前置（事实底座）
- Task 2/3/4/5 依赖 Task 1，相互可并行
- Task 6 依赖 Task 2-5 全部文件就位
- Task 7 依赖 Task 6
- Task 8 依赖 Task 7