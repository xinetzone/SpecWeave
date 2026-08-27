# Tasks

> 依据 `source-code-to-okf-wiki` 五阶段链路（R→I→E→V→C）与 OKF v0.2 规范执行。
> 每个项目的 R（facts.md）与 I（insights.md）由 I 阶段完成后写入 `bundles/datawhale/<project>/spec/` 目录（参考 deepseek/lplb 的 spec 子目录模式），以「信源先行」原则保证可追溯。

## 批次划分

- **第一批（代码框架类，2 个）**：torch-rechub、deepagents —— 走完整源码级 R→I→E→V→C
- **第二批（教程类核心，5 个）**：base-llm、happy-llm、hello-agents、all-in-rag、easy-vecdb
- **第三批（教程类，5 个）**：easy-vibe、handy-n8n、handy-ollama、key-book、pumpkin-book
- **第四批（教程类，6 个）**：tiny-universe、vibe-vibe、code-your-own-llm、Agent-Learning-Hub、deepagents-in-action、members-visualization

---

- [x] Task 1: 建立 datawhale 分组骨架
  - [x] 创建 `bundles/datawhale/` 目录
  - [x] 生成 `bundles/datawhale/index.md`（含 `type: group`、`okf_version: "0.2"`、`total_bundles: 18`、分类导航）
  - [x] 初始 frontmatter 含 `generated`/`verified`/`status: stable`（全部 bundle 完成后改为 stable）

- [x] Task 2: 生成 torch-rechub 知识束（代码框架类·源码级深挖）
  - [x] R：阅读 `torch_rechub/` 源码（basic/models/trainers/utils），产出 `spec/facts.md`（230条事实）
  - [x] I：提炼核心洞察（特征描述符契约/四类Trainer/双塔mode切换/ONNX桥接/多任务专家门控），产出 `spec/insights.md`
  - [x] E：生成 concepts/（7个）、examples/（2个）、references/（5个）
  - [x] V：Grep 验证 60+类名、40+方法名在源码中存在

- [x] Task 3: 生成 deepagents 知识束（代码框架类·源码级深挖）
  - [x] R：阅读 `libs/`（acp/cli/code/evals/talon）+ `AGENTS.md`，产出 `spec/facts.md`（81条事实）
  - [x] I：提炼核心洞察（三层栈定位/Monorepo独立版本化/Code TUI工程/ACP桥接/评估驱动），产出 `spec/insights.md`
  - [x] E：生成 concepts/（7个）、examples/（6个）、references/（13个）
  - [x] V：Grep 验证关键符号与模块存在性

- [x] Task 4: 生成 base-llm 知识束（教程类·章节转译）
  - [x] R：梳理 docs/ 六大部分章节结构，产出 `spec/facts.md`（100+条事实）
  - [x] I：提炼5个核心洞察，产出 `spec/insights.md`
  - [x] E：生成 concepts/（8个）、examples/（登记12组代码）、references/（登记46节）
  - [x] V：章节标题与_sidebar.md逐节核对一致

- [x] Task 5: 生成 happy-llm 知识束（教程类）
  - [x] R/I：梳理 8 章 + Extra-Chapter 结构，产出 facts（25条）/insights（4个）
  - [x] E：生成 concepts/（7个）、examples/（4个）、references/（8章）
  - [x] V：8章标题与_sidebar.md一致

- [x] Task 6: 生成 hello-agents 知识束（教程类·16 章深挖）
  - [x] R/I：梳理 16 章 + 13篇社区精选结构，产出 facts/insights（5个）
  - [x] E：生成 concepts/（8个）、examples/（4个）、references/（17章）
  - [x] V：16章H1标题与_sidebar.md完全一致

- [x] Task 7: 生成 all-in-rag 知识束（教程类）
  - [x] R/I：梳理 10 章 + 项目实战结构，产出 facts（27条）/insights（4个）
  - [x] E：生成 concepts/（7个）、examples/（2个C8/C9实战）、references/（10章）
  - [x] V：10章reference标题与_sidebar.md逐字一致

- [x] Task 8: 生成 easy-vecdb 知识束（教程类）
  - [x] R/I：梳理六大部分40+章节结构，产出 facts（56条）/insights（5个）
  - [x] E：生成 concepts/（6个）、examples/（3个）、references/（2个）
  - [x] V：frontmatter完整，30处交叉链接有效

- [x] Task 9: 生成 easy-vibe 知识束（教程类）
  - [x] R/I/E/V：梳理10语言文档站结构，产出 facts（19组）/insights（3个），3 concepts + 1 example + 1 reference

- [x] Task 10: 生成 handy-n8n 知识束（教程类）
  - [x] R/I/E/V：梳理 c01-c06 章节，产出 facts（20条）/insights（3个），5 concepts + 4 examples + 6 references

- [x] Task 11: 生成 handy-ollama 知识束（教程类）
  - [x] R/I/E/V：梳理 docs/ 7章25节结构，产出 facts/insights（3个），5 concepts + 3 examples + 7 references

- [x] Task 12: 生成 key-book 知识束（教程类·理论书籍）
  - [x] R/I：梳理 8 章 + 附录结构，产出 facts/insights（4个）
  - [x] E：生成 concepts/（7大理论支柱）、examples/（3个推导案例）、references/（9个）
  - [x] V：90个交叉链接全部通过

- [x] Task 13: 生成 pumpkin-book 知识束（教程类）
  - [x] R/I：梳理 16 章结构与 errata，产出 facts（30条）/insights（3个）
  - [x] E：生成 concepts/（6个）、examples/（3个推导）、references/（8个）
  - [x] V：45处交叉链接有效

- [x] Task 14: 生成 tiny-universe 知识束（教程类·README 白盒指南）
  - [x] R/I：基于 README 梳理 8主体+1探索模块，产出 facts/insights（3个）
  - [x] E：生成 concepts/（5个）、examples/（1个路线图）、references/（3个）
  - [x] V：模块名拼写与README一致

- [x] Task 15: 生成 vibe-vibe 知识束（教程类）
  - [x] R/I/E/V：梳理 docs/ 双语结构，产出 facts（18组）/insights（3个），3 concepts + 1 example + 1 reference

- [x] Task 16: 生成 code-your-own-llm 知识束（教程类·精简便签）
  - [x] R/I/E/V：基于 README + AGENTS.md，产出 facts（13条）/insights（2个），2 concepts + 1 reference

- [x] Task 17: 生成 Agent-Learning-Hub 知识束（教程类·精简便签）
  - [x] R/I/E/V：基于 README + index.html，产出 facts（10条）/insights（2个），2 concepts + 1 reference

- [x] Task 18: 生成 deepagents-in-action 知识束（教程类·精简便签）
  - [x] R/I/E/V：基于 README，产出 facts（13条）/insights（2个），2 concepts + 1 reference

- [x] Task 19: 生成 members-visualization 知识束（占位收录）
  - [x] E：基于 .npmrc/仓库信息，生成极简 index.md + log.md + concepts/examples/references 空索引

- [x] Task 20: 更新总索引并收尾
  - [x] 更新 `bundles/datawhale/index.md`：status 置为 stable
  - [x] 更新 `bundles/index.md`：新增 datawhale 分组行，更新 groups/total_bundles 计数
  - [x] 结构验证：18个bundle三层结构完整，frontmatter字段齐全
  - [x] C 阶段：模式沉淀（教程类/框架类/占位类三种bundle生成模式）

# Task Dependencies

- Task 2-19（各 bundle 生成）依赖 Task 1（分组骨架）
- Task 20（收尾）依赖 Task 2-19 全部完成
- Task 2-19 之间相互独立，可分四批并行委派（每批 ≤5 个 sub-agent）
