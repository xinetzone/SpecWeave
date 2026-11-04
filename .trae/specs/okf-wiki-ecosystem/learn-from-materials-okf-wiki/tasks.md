# Tasks：learn-from-materials OKF 知识包

## T1 内容获取与事实采集

- [x] T1.1 敏感度预检（公开博文，标准工作流）
- [x] T1.2 获取博文全文（标题/公众号/发布时间/正文/标签，来自 `.temp/blog-article-MUvHmFc4ItWfN57tuNjZkQ.md`）
- [x] T1.3 内容性质判定：开源工具教程（跨 Agent 学习 Skill）→ 完整骨架含 examples/
- [x] T1.4 归属判定：`jishu/ai/frameworks/ai-agent/`（`### 📰 产品资讯` 段），Bundle 名 `learn-from-materials`
- [x] T1.5 facts.md 落盘（F-001~F-041，共41条）

## T2 P0 核验（R 阶段）

- [x] T2.1 仓库 `dmoshehun-prog/learn-from-materials` 存在性 / MIT / Python / 时点 star-fork ✅（GitHub API）
- [x] T2.2 版本 1.1.0 ✅（官方 badge 与章节）
- [x] T2.3 支持格式清单 ✅（README EN/CN 双份一致，且宽于原文列举）
- [x] T2.4 宿主清单与用户级安装目录表 ✅（README EN/CN 双份一致；topics 含 workbuddy 侧证）
- [x] T2.5 两种深度 / 六板块 / 三主题 ✅（README）
- [x] T2.6 Python 3.10+ 与 Node.js 可选 ✅（README badge + 运行要求）
- [x] T2.7 豆包工作具备技能安装机制 ✅（豆包工作官方文档 + 开放平台 skill-integration-guide + 第三方实践）
- [x] T2.8 ⚠️ 口径差异登记：文章宿主「豆包工作」vs README 宿主清单未列豆包工作（双源并列，不判定文章有误）
- [x] T2.9 verification.md 核验报告落盘（9✅ + 1⚠️ 口径差异 + 4项单源登记）

## T3 I 阶段拆分

- [x] T3.1 骨架判定（操作可复现性两问）：Q1 有可照做流程=是；Q2 可复现（三步顺序 + 逐字提示词 + 官方 1.1.0 版本与安装表补全）=是 → 设 examples/
- [x] T3.2 concepts 4 篇：项目概览 / 材料→学习网页机制 / 两种深度与方法论库 / 宿主集成与边界
- [x] T3.3 examples 2 篇：安装与三步实操 / 产出与分享

## T4 E 阶段生成

- [x] T4.1 references/article-source.md + references/verification.md（信源先行）
- [x] T4.2 concepts/index.md + 4 篇概念文档
- [x] T4.3 examples/index.md + 2 篇实战文档
- [x] T4.4 references/index.md
- [x] T4.5 index.md（含 mermaid 机制图、分层导航、信任与生命周期、已知边界）
- [x] T4.6 log.md

## T5 索引更新（⏸️ 登记延后）

> 共享索引（`doc/bundles/index.md`、`doc/index.md`、`README.md`、`jishu/**/index.md`）已被并发的在途会话改写为 710 系，并含其 5 个未跟踪新束的 toctree 引用。经用户裁决采用**隔离策略**：本次仅交付包体，不改写共享索引（避免回滚他会话未提交变更）。下列目标值以 HEAD（3a6b6280）干净基线为准：**树 704 + 本包 1 = 705**；`jishu 515`、`ai 281`、`frameworks 93`、`ai-agent 60`。

- [ ] T5.1 `ai-agent/index.md`：`total_bundles` 59→60、`### 📰 产品资讯` 表格追加行、toctree 追加 `learn-from-materials/index`、"内容统计"59→60
- [ ] T5.2 `frameworks/index.md`：描述与正文 `ai-agent（59 束）`→60、类总 `92`→`93`、束导航表 ai-agent 行 59→60
- [ ] T5.3 `jishu/ai/index.md`：描述与正文 →281、六大类表 frameworks `92`→`93`
- [ ] T5.4 `doc/bundles/index.md`：`total_bundles`→705、正文"705 个知识包"、mermaid jishu→515、jishu 节标题→515、ai 行→281（并顺带修复 HEAD 自身的 +1 漂移：703→704）
- [ ] T5.5 `jishu/index.md`：AI 与大模型行 →281 束

## T6 V 阶段验证

- [x] T6.1 UTF-8 严格解码 roundtrip 通过（13 文件，无 BOM）
- [x] T6.2 无 `file:///` 绝对路径链接
- [x] T6.3 内部相对链接全部有效（修复 `concepts/00-project-overview.md` 跨束互链 `../`→`../../`，涉及 claude-vision-skill / book-to-skill / show-me-skill）
- [x] T6.4 各 `index.md` 均含 `{toctree}` 块（bundle 内 4 个 index.md：根/concepts/examples/references）
- [ ] T6.5 索引计数五级同步 —— ⏸️ 随 T5 一并延后（包内计数与结构已自洽，外部计数待会话统一处理）
- [x] T6.6 双份 F 编号正则比对（spec `facts.md` 41 条 = bundle `references/article-source.md` 41 条，集合一致且连续 F-001~F-041）
- [x] T6.7 门禁复跑与归因（见下）

### T6.7 门禁复跑结果（如实记录）

| 门禁 | 结果 | 归因 |
|------|------|------|
| `check-utf8.py` | ✅ 通过（12842 文件全部有效 UTF-8） | — |
| `check-toctrees.py` | ❌ 14 处 | **均为登记延后所致**：本包 13 文件不可达 + `ai-agent/index.md` 未收录 `learn-from-materials/index`（T5.1 待办） |
| `check-bundles-index.py` | 未生效 | 本包未登记（T5 待办），且共享索引被他会话占用；**未宣称通过** |
| `check-asset-baseline.py` | 未执行 | 同上，共享索引三处（`doc/bundles/index.md`/`doc/index.md`/`README.md`）本轮不触碰 |

> 说明：`check-toctrees.py` 的失败在「仅交付包体」裁决下属**已知且预期**的登记债，非包体内容缺陷；包内三级导航结构本身完整（T6.4 已验证）。

## T7 C 阶段原子提交

- [ ] T7.1 子模块 `projects/awesome-okf-xs` 内提交（显式文件列表）
- [ ] T7.2 主仓库提交 spec 四件套
- [ ] T7.3 主仓库更新子模块指针（不 push）
