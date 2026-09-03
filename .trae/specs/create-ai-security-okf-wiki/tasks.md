# Tasks — create-ai-security-okf-wiki

> 方法论链路：R（T1）→ I（T2）→ E（T3/T4）→ V（T5）→ C（T6）。T3 内部三个束可并行。
> 实现期须加载 Skill：`source-code-to-okf-wiki`（OKF 生成防护机制：信源先行、Grep 级 API 验证、计数断言）。
> ✅ 全部完成：提交 72467fe3（awesome-okf-xs 子模块，30 文件 3455 行，未推送）。

- [x] T1: R 阶段——三仓库事实采集（可并行 3 个子代理）
  - [x] T1.1: 采集 CL4R1T4S 事实 → `facts-cl4r1t4s.md`（70 条 F-C4-001~070，26 厂商目录/73 文件，15 文件抽样深读）
  - [x] T1.2: 采集 L1B3RT4S 事实 → `facts-l1b3rt4s.md`（55 条 F-L1-001~055，34 厂商 .mkd，全程仅 git show 只读，工作树 D 状态未触碰）
  - [x] T1.3: 采集 OBLITERATUS 事实 → `facts-obliteratus.md`（66 条 F-OB-001~066，19 CLI 子命令全部源码定位，15 分析模块全部核验，6 处 README 漂移标注）
- [x] T2: I 阶段——跨仓库洞察
  - [x] T2.1: `insights.md` 7 条洞察（超出 ≥3 要求），每条四元组完整、证据 5-8 个 F 编号（G2 通过）
- [x] T3: E 阶段——生成 ai-security 分组与三束
  - [x] T3.1: 分组 `ai-security/index.md`（4118 字符，双入口学习路径 + 用途限定声明）
  - [x] T3.2: `cl4r1t4s/` 束（8 文件，F-C4 全 70 条被消费，4 Mermaid + 20+ 表格）
  - [x] T3.3: `l1b3rt4s/` 束（7 文件，T1-T10 四族十类分类学，两轮 grep 载荷零命中）
  - [x] T3.4: `obliteratus/` 束（11 文件，63/66 F 编号消费，勘误表落 novel-techniques）
- [x] T4: 索引注册与计数更新
  - [x] T4.1: `jishu/ai/index.md` 分组导航行 + toctree `ai-security/index`
  - [x] T4.2: `jishu/index.md`（ai 行 127→128 树真值、关键词、正文 16 组、gui 注册）
  - [x] T4.3: `bundles/index.md`（frontmatter 413/52、mermaid、域节标题 313 束·16 组、ai 行 128、gui 行）——计数全程以 gates 重算为准，经历 3 轮并行会话树漂移收敛（410→411→413）
- [x] T5: V 阶段——对抗审查（depth=deep）
  - [x] T5.1: 事实核对 37 处（含 facts 未登记的 5 组源码补验），OBLITERATUS 六处勘误全数以源码值为准
  - [x] T5.2: 伦理边界检查——载荷标记零命中、用途限定齐备（报告见 `review.md`）
  - [x] T5.3: 格式扫描 27/27 YAML 解析通过；定向 sphinx dummy 构建 30 文件成功（0 error；29 警告均来自并行会话文件）；4 视角意见 11 处全部采纳修正（10 文件 13 处）
- [x] T6: C 阶段——质量门与原子提交
  - [x] T6.1: `gates.utf8` 全绿（8081 文件）；`gates.bundles`/`gates.toctrees` 己方注册面零问题（残留失败项均为他会话在建目录：sheke/finance、sheke/marketing 0 束无组索引，不可代注册）
  - [x] T6.2: 原子提交 72467fe3——add 与 commit 分离、暂存集精确 30 文件、暂存 blob 关键行核验（413/52/128/ai-security/toctree）、Conventional Commits 中文；未推送（待全树三门绿）

# Task Dependencies

- T2 依赖 T1（洞察必须引用事实编号）
- T3 依赖 T1 + T2；T3.2/T3.3/T3.4 之间并行
- T4 依赖 T3.1（分组存在后才注册）；定稿依赖 T3 全部束生成后的 gates 重算
- T5 依赖 T3 + T4；T6 依赖 T5
- T1.1/T1.2/T1.3 三者并行
