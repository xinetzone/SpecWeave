# Tasks

> 执行方法：`source-code-to-okf-wiki` Skill R→I→E→V→C 五阶段链路（七概念场景4），事实文件存放于本 spec 目录。

- [x] Task 1: R 阶段——源码事实采集（完成：206 条事实，4 文件）
  - [x] SubTask 1.1: facts-mobile-world.md（80 条）
  - [x] SubTask 1.2: facts-mai-ui.md（54 条）
  - [x] SubTask 1.3: facts-mobilepa-bench.md（32 条）与 facts-websites.md（40 条）
  - [x] SubTask 1.4: G1 门自检通过（零推断词，逐条路径标注）
- [x] Task 2: I 阶段——架构洞察与知识地图（insights.md 332 行，15 个四元组，20 篇 concepts 蓝图）
  - [x] SubTask 2.1 / 2.2 / 2.3
- [x] Task 3: E 阶段——生成 3 个 bundle（45 文件）
  - [x] SubTask 3.1~3.8（references 先行、3 束并行生成、index 最后写、toctree 完整）
- [x] Task 4: V 阶段——独立验证与修复
  - [x] SubTask 4.1: Grep 验证 33 项符号全部对齐源码（修复 AndroidController 35→32 方法数等）
  - [x] SubTask 4.2: 链接/frontmatter/F 编号检查通过（17 处计数偏差已修复）
  - [x] SubTask 4.3: `invoke gates.all` 通过（UTF-8 5806 文件 + toctree 全部可达，exit 0）
  - [x] SubTask 4.4: verification.md 已产出
- [x] Task 5: 索引同步
  - [x] SubTask 5.1: ai-agent 分组索引 31→34 + 新小节 + toctree 3 行
  - [x] SubTask 5.2: 域索引与总索引 total_bundles 283→286、ai 域 110→113；qwen-ui-agent 互链已建立
- [ ] Task 6: C 阶段——原子提交
  - [ ] SubTask 6.1: awesome-okf-xs 子模块原子提交
  - [ ] SubTask 6.2: SpecWeave 主仓库子模块指针提交
  - [ ] SubTask 6.3: G5 门自检

# Task Dependencies

- Task 2 依赖 Task 1（洞察基于事实）
- Task 3 依赖 Task 2（生成基于知识地图；3.1→3.2→3.3~3.6→3.7 串行硬约束）
- Task 3.3 / 3.4 / 3.5 三者可并行（独立 bundle，各自子任务委派 Sub-Agent）
- Task 4 依赖 Task 3；Task 5 依赖 Task 3（5.1/5.2 可与 Task 4 并行准备，但提交需在 Task 4 通过后）
- Task 6 依赖 Task 4 与 Task 5 全部完成
