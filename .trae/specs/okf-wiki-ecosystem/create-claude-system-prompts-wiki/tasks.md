# Tasks

- [x] Task 1: R阶段——信源探测与事实采集
  - [x] SubTask 1.1: 确认 zh-CN/en URL 结构与子页面清单（`/overview` 是否拆页、`.md` 原文端点可用性），确定采集批次
    - 实测：overview 为卡片导航页 + 18 个模型子页；en `.md` 端点 curl 可直连（间歇地域拦截，8 轮退避重试全拿下）；zh-CN 稳定受限，以 en 为基线
  - [x] SubTask 1.2: 按升级链采集 16 模型 × 28 条目内容，以 F-xxx 编号登记至 spec 目录 `facts.md`
    - 实测修正：实际为 **18 模型 × 30 条目**（含 2026-09-01 上线的 Fable 5.1），61 条 F 编号（F-OV 6 + F-3X 15 + F-40 13 + F-45 13 + F-46 14），登记于 facts-overview.md + facts-era-*.md 四文件
  - [x] SubTask 1.3: V前置抽查——随机抽 ≥5 个条目的关键句与官方原文逐字比对
    - 6/6 通过（more than a mere tool、fable_safeguards_routing、responding_to_mistakes_and_criticism、1929 版权线、end of January 2025、Sonic 案引文）
- [x] Task 2: I阶段——演进洞察提炼
  - [x] SubTask 2.1: 产出 insights.md（7 条"现象/证据/根因/影响"四元组）
- [x] Task 3: E阶段——束生成（concepts）
  - [x] SubTask 3.1: 束骨架 index.md + concepts/index.md + log.md
  - [x] SubTask 3.2: concepts/00-overview.md + 01-lineage-matrix.md
  - [x] SubTask 3.3: concepts/02-era-3x.md + 03-era-4x-launch.md
  - [x] SubTask 3.4: concepts/04-era-45.md + 05-era-fixed-snapshot.md
  - [x] SubTask 3.5: concepts/06-evolution.md（基于 insights.md）
- [x] Task 4: E阶段——references 与索引注册
  - [x] SubTask 4.1: references/{index,source-index,entry-registry}.md
  - [x] SubTask 4.2: 组索引 anthropic/{index,log}.md 更新
  - [x] SubTask 4.3: 域索引 jishu/ai/index.md 与总索引 doc/bundles/index.md 注册（束计数 127→128、jishu 310→311、总数 410→411，全部与目录树地面真值一致）
- [x] Task 5: 质量门与对抗审查
  - [x] SubTask 5.1: gates.utf8 ✅（8109 文件）/ gates.toctrees / gates.bundles / sphinx build
    - 结论：**本束零问题**——toctrees 138 处与 bundles 6 处失败全部来自并行会话在途束（wigolo、jishu/gui、sheke/finance、sheke/marketing、ai-app-survival 缺 index.md/未注册），无一条涉及 system-prompts；按"不代他方补齐在途工作"纪律不越界修复
    - sphinx build 经用户指示跳过（构建太慢）
  - [x] SubTask 5.2: V阶段对抗审查（7 项审查，发现 2 ERROR + 2 WARNING，已全部修复并终验：01-lineage L49 校验算式、Opus 4.6 行数 158→128 传播链 5 处、entry-registry 链接、facts 基线 3 处）——修复过程遭遇同文件并行 Edit 竞态（与项目备忘"共享索引 Edit 静默丢失竞态"同型），改串行应用后全部落地
- [x] Task 6: 收尾报告
  - [x] SubTask 6.1: 汇总产出与变更清单；**未自动 commit**（用户可用 atomic-commit-cmd 提交）

# Task Dependencies

- Task 2 依赖 Task 1（洞察必须基于已采集事实）
- Task 3 依赖 Task 1/2；Task 3.2~3.5 内部各文件相互独立、可并行
- Task 4.1 可与 Task 3 并行（文件互不重叠）；Task 4.2/4.3 依赖 Task 3 完成后才能确定统计数字
- Task 5 依赖 Task 4；Task 6 依赖 Task 5
