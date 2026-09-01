# Tasks — create-fangzhong-bajia-wiki

> 依赖顺序：T1 → T2 → T3/T4/T5（可并行）→ T6 → T7 → T8
> 实施目录：`projects/awesome-okf-xs/doc/bundles/think/sexology/fangzhong-bajia-reading/`
> 七概念链路：场景4 知识沉淀 R→I→E→V→C（session=sc-20260831-fangzhong-bajia-wiki）

- [x] Task 1: R 阶段——系统性调研与事实采集（G1 质量门）
  - [x] SubTask 1.1: 创建 `.temp/fangzhong-bajia-research/` 中间产物目录（任务完成后清理）
  - [x] SubTask 1.2: 著录原文线：ctext.org 拒绝自动化访问，改用维基文库/颜师古注本/汉书新注/中华文库四信源交叉核对，登记到 `.temp/.../01-catalog-facts.md`（F-001~F-016）
  - [x] SubTask 1.3: 亡佚辑佚线：登记到 `.temp/.../02-fragments-facts.md`（F-017~F-028，原 F-015/F-016 与著录线重复已删除）
  - [x] SubTask 1.4: 出土文献线：登记到 `.temp/.../03-excavated-facts.md`（F-029~F-039）
  - [x] SubTask 1.5: 现代解读线：登记到 `.temp/.../04-interpretation-facts.md`（F-040~F-058）
  - [x] SubTask 1.6: 汇总 58 条带信源编号事实（F-001~F-058），G1 门通过（无因果词/可追溯/关键数据完整），6 处争议条目标【待核验】
- [x] Task 2: I 阶段——跨线洞察（G2 质量门）
  - [x] SubTask 2.1: 提炼 4 条四元组洞察（I-1 托名化石层 / I-2 数字矛盾即流传史 / I-3 亡佚文本双通道回流 / I-4 方技四分定位与两次重分类），登记到 `.temp/.../05-insights.md`，G2 门通过
- [x] Task 3: E 阶段——bundle 根与工作文档（与 T4/T5 可并行）
  - [x] SubTask 3.1: 创建 `fangzhong-bajia-reading/index.md`（OKF v0.2 frontmatter：type OKF、generated agent:seven-concepts-r-i-e、verified process:seven-concepts-v、status draft→stable、stale_after 2027；📚快速导航 + 🚀分读者路径 + 🎯定位对比表（与 classics-reading 通论分工）+ 📖学习路径；文末 toctree 引 concepts/index、examples/index、references/index、facts、insights、log）
  - [x] SubTask 3.2: 创建 `facts.md`（R 阶段全部事实按四条线分组制表，【待核验】条目显式标注）
  - [x] SubTask 3.3: 创建 `insights.md`（I 阶段洞察 + 知识地图）
  - [x] SubTask 3.4: 创建 `log.md`（创建日志：日期、结构清单、调研来源）
- [x] Task 4: E 阶段——concepts/ 概念文档（8 篇，与 T3/T5 可并行）
  - [x] SubTask 4.1: `concepts/index.md`（分节导航表 + hidden toctree 全 8 篇）
  - [x] SubTask 4.2: `00-yiwenzhi-fangji-lue.md`（方技略四分结构、房中类小序、八家在汉代知识图谱中的位置）
  - [x] SubTask 4.3: `01-eight-schools-catalog.md`（八家著录总表：书名/卷数/班固注/存佚 + 著录原文对照）
  - [x] SubTask 4.4: `02-rongcheng-wuyin.md`（容成、务成两家：托名传统、导引之道、务成子传说谱系）
  - [x] SubTask 4.5: `03-huangdi-school.md`（黄帝系诸书：托名现象、著录差异、主题推断并标注推断层级）
  - [x] SubTask 4.6: `04-sanyangban-and-others.md`（三阳班及其他诸家提要，"仅存书目"处理方式）
  - [x] SubTask 4.7: `05-fragments-chain.md`（辑佚链条：《医心方》卷廿八、素女经/玉房秘诀/洞玄子系文献、双梅景闇丛书）
  - [x] SubTask 4.8: `06-excavated-texts.md`（马王堆医书房中类与八家的时代/内容互证）
  - [x] SubTask 4.9: `07-modern-interpretations.md`（现代解读、性质诸说、研读顺序与版本选择）
- [x] Task 5: E 阶段——examples/ 与 references/（与 T3/T4 可并行）
  - [x] SubTask 5.1: `examples/index.md` + `01-first-catalog-reading.md`（零基础首次研读实操：从著录总表到选一家深入）
  - [x] SubTask 5.2: `examples/02-fragment-reading.md`（佚文对照阅读示例：提要→原文节选→现代解读三步法，以《医心方》所引为例）
  - [x] SubTask 5.3: `examples/03-reading-plan.md`（分阶段研读计划：著录→辑佚→出土互证→现代解读）
  - [x] SubTask 5.4: `references/index.md` + 信源文档 ≥4 篇（著录原文信源/辑佚文献信源/出土文献信源/现代研究信源，均带 URL）
- [x] Task 6: 更新导航索引与交叉引用
  - [x] SubTask 6.1: `think/sexology/index.md`：导航表加行、toctree 加 `fangzhong-bajia-reading/index`
  - [x] SubTask 6.2: `bundles/index.md`：计数 289→290、35→36、think "8 束 · 5 组"→"9 束 · 6 组"、sexology 分组行更新
  - [x] SubTask 6.3: `sexology/classics-reading/concepts/01-ancient-china.md` 与 `references/further-reading.md` 各加一处指向新 bundle 的交叉引用（不改既有事实与结论）
  - [x] SubTask 6.4: `.trae/specs/README.md` 与 `.trae/specs/standards-tools/README.md` 看板登记本 spec
- [x] Task 7: 质量门验证
  - [x] SubTask 7.1: 在 `projects/awesome-okf-xs` 运行 `invoke gates.toctrees`（零断链零孤立）
  - [x] SubTask 7.2: 运行 `invoke gates.utf8`
  - [x] SubTask 7.3: 运行 `invoke build`——按用户指示跳过（2026-08-31 用户明确要求"不要构建"）
  - [x] SubTask 7.4: 清理 `.temp/fangzhong-bajia-research/` 中间产物（事实与洞察已并入 bundle 后）
- [x] Task 8: V 阶段独立评审与修复（强制，不可跳过）
  - [x] SubTask 8.1: 委托新鲜上下文 general_purpose_task 只读四视角评审（事实准确性/新人可入门性/定位与边界/时效与规范），结果写入本 spec 目录 `review.md`
  - [x] SubTask 8.2: 修复评审 fail 项（如有），复跑 Task 7 质量门
  - [x] SubTask 8.3: 收尾总结（不执行 git commit，除非用户明确要求）

# Task Dependencies

- Task 2 依赖 Task 1（洞察必须引用事实编号）
- Task 3/4/5 依赖 Task 1、Task 2（内容基于事实与洞察），三者相互可并行
- Task 6 依赖 Task 3/4/5 全部文件就位
- Task 7 依赖 Task 6
- Task 8 依赖 Task 7
