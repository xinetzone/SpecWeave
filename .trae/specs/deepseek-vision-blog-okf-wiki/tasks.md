# Tasks

> 方法论链路：R（事实采集）→ I（结构洞察）→ E（萃取为 bundle）→ V（对抗审查）→ 索引收尾 → 模式沉淀

- [ ] Task 1: R 阶段——博文事实采集登记
  - [ ] SubTask 1.1: 从博文内容提取全部可验证事实，按 F-001 起编号（模型发布信息、API 传图方式、5 类选型推荐及价格、双模型管线模式、总结口诀），登记于 `references/article-source.md`（草稿）
  - [ ] SubTask 1.2: 轻量核验关键声明（DeepSeek-V4-Flash-Vision-Exp 存在性、GLM-4.6V-Flash 免费政策），可核验则补充官方信源，不可核验则标注"仅博文单源"
- [ ] Task 2: I 阶段——知识结构洞察
  - [ ] SubTask 2.1: 分析博文知识结构，确认三层拆分：模型发布事实层 / 选型矩阵层 / 管线架构模式层，映射到 4 篇 concepts + 3 篇 examples
- [ ] Task 3: E 阶段——生成 OKF bundle
  - [ ] SubTask 3.1: 创建 `ai/deepseek/vision-model-selection/` 目录结构及 `index.md`（frontmatter 含 sources 指向微信博文 URL、status、stale_after、已知边界声明）
  - [ ] SubTask 3.2: 编写 concepts/ 4 篇文档（00-deepseek-vision-exp / 01-selection-landscape / 02-scenario-matrix / 03-vision-reasoning-pipeline）+ index.md，事实引用 F 编号，交叉引用 deepseek-ocr2 bundle
  - [ ] SubTask 3.3: 编写 examples/ 3 篇文档（cost-scenario-walkthrough / pipeline-output-structure / selection-decision-tree）+ index.md
  - [ ] SubTask 3.4: 定稿 references/（article-source.md + index.md）
  - [ ] SubTask 3.5: 编写 log.md（生成日志）
- [ ] Task 4: V 阶段——对抗审查
  - [ ] SubTask 4.1: 多视角审查：①事实视角（文档中所有模型名/价格是否均有 F 编号溯源，无虚构）②结构视角（是否符合 OKF v0.2 bundle 结构与 frontmatter 规范）③读者视角（选型决策是否可独立follow）④时效视角（Exp 模型与价格时效性声明是否到位）
  - [ ] SubTask 4.2: 修复审查发现的问题
- [ ] Task 5: 索引收尾与验证
  - [ ] SubTask 5.1: 更新 `ai/deepseek/index.md`（新增导航条目，束数 12→13，toctree 追加）
  - [ ] SubTask 5.2: 更新 `bundles/index.md`（total_bundles 268→269，DeepSeek 分组 12→13）
  - [ ] SubTask 5.3: 运行链接检查（check-links.py 或等效方式）验证新增文档内部链接与交叉引用有效
- [ ] Task 6: 模式沉淀——博文类文章→OKF 知识包转化模式（主任务完成后执行）
  - [ ] SubTask 6.1: 编写 `.agents/docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md`：frontmatter 遵循模式库规范（id: pattern-blog-article-to-okf-bundle, maturity: draft, validation_count: 1），结构含触发场景/核心步骤（敏感度预检→归属判定决策树→事实采集→三层拆分→bundle 生成→索引更新）/反模式/迁移验证
  - [ ] SubTask 6.2: 在模式文档中以本次 vision-model-selection bundle 为首个演示案例（demo），完整走一遍模式的步骤对照
  - [ ] SubTask 6.3: 更新 `documentation-patterns/README.md` 登记新模式条目（如该分类索引存在登记惯例）

# Task Dependencies

- Task 2 depends on Task 1（事实先于洞察）
- Task 3 depends on Task 2（结构先于生成）
- Task 4 depends on Task 3（审查已有产出）
- Task 5 depends on Task 4（审查通过后收尾）
- Task 6 depends on Task 5（主任务闭环后沉淀模式）
