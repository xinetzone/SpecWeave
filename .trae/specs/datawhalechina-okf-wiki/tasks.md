# Tasks

> 依据 `source-code-to-okf-wiki` 五阶段链路（R→I→E→V→C）与 OKF v0.2 规范执行。
> 每个项目的 R（facts.md）与 I（insights.md）由 I 阶段完成后写入 `bundles/datawhale/<project>/spec/` 目录（参考 deepseek/lplb 的 spec 子目录模式），以「信源先行」原则保证可追溯。

## 批次划分

- **第一批（代码框架类，2 个）**：torch-rechub、deepagents —— 走完整源码级 R→I→E→V→C
- **第二批（教程类核心，5 个）**：base-llm、happy-llm、hello-agents、all-in-rag、easy-vecdb
- **第三批（教程类，5 个）**：easy-vibe、handy-n8n、handy-ollama、key-book、pumpkin-book
- **第四批（教程类，6 个）**：tiny-universe、vibe-vibe、code-your-own-llm、Agent-Learning-Hub、deepagents-in-action、members-visualization

---

- [ ] Task 1: 建立 datawhale 分组骨架
  - [ ] 创建 `bundles/datawhale/` 目录
  - [ ] 生成 `bundles/datawhale/index.md`（含 `type: category`、`okf_version: "0.2"`、`total_bundles: 18`、分类导航）
  - [ ] 初始 frontmatter 含 `generated`/`verified`/`status: draft` 占位（全部 bundle 完成后改为 stable）

- [ ] Task 2: 生成 torch-rechub 知识束（代码框架类·源码级深挖）
  - [ ] R：阅读 `torch_rechub/` 源码（basic/models/trainers/utils），产出 `spec/facts.md`
  - [ ] I：提炼核心洞察（模型分层/三类 Trainer/ONNX 导出），产出 `spec/insights.md`
  - [ ] E：生成 concepts/（模型体系、feature、trainer、data、onnx 导出）、examples/、references/
  - [ ] V：Grep 验证 DSSM/DeepFM/DIN/MMoE 等类名与方法在源码中存在

- [ ] Task 3: 生成 deepagents 知识束（代码框架类·源码级深挖）
  - [ ] R：阅读 `libs/`（acp/cli/code/evals/talon）+ `AGENTS.md`，产出 `spec/facts.md`
  - [ ] I：提炼核心洞察（monorepo 结构/模块边界/Agent 运行时），产出 `spec/insights.md`
  - [ ] E：生成 concepts/、examples/、references/
  - [ ] V：Grep 验证模块与关键符号存在性

- [ ] Task 4: 生成 base-llm 知识束（教程类·章节转译）
  - [ ] R：梳理 docs/ 六大部分章节结构，产出 `spec/facts.md`
  - [ ] I：提炼核心洞察，产出 `spec/insights.md`
  - [ ] E：生成 concepts/（NLP→Transformer→预训练→微调→部署→安全多模态）、examples/、references/
  - [ ] V：章节链接与概念覆盖校验

- [ ] Task 5: 生成 happy-llm 知识束（教程类）
  - [ ] R/I：梳理 8 章 + Extra-Chapter 结构，产出 facts/insights
  - [ ] E：生成 concepts/（Transformer/PLM/LLaMA2 手写/训练/GRPO/RAG/Agent）、examples/、references/
  - [ ] V：校验

- [ ] Task 6: 生成 hello-agents 知识束（教程类·16 章深挖）
  - [ ] R/I：梳理 16 章 + 社区精选结构，产出 facts/insights
  - [ ] E：生成 concepts/（智能体范式/框架开发/记忆/上下文工程/通信协议/Agentic-RL/评估）、examples/、references/
  - [ ] V：校验

- [ ] Task 7: 生成 all-in-rag 知识束（教程类）
  - [ ] R/I：梳理 10 章 + 项目实战结构，产出 facts/insights
  - [ ] E：生成 concepts/（数据准备/索引构建/检索进阶/生成评估/实战）、examples/、references/
  - [ ] V：校验

- [ ] Task 8: 生成 easy-vecdb 知识束（教程类）
  - [ ] R/I：梳理 Base/Annoy/Faiss/Milvus/项目六部分结构，产出 facts/insights
  - [ ] E：生成 concepts/（向量检索/ANN 算法/Annoy/Faiss/Milvus）、examples/、references/
  - [ ] V：校验

- [ ] Task 9: 生成 easy-vibe 知识束（教程类）
  - [ ] R/I/E/V：梳理多语言文档站结构，生成精简 concepts/examples/references

- [ ] Task 10: 生成 handy-n8n 知识束（教程类）
  - [ ] R/I/E/V：梳理 c01-c06 章节，生成 concepts/examples/references

- [ ] Task 11: 生成 handy-ollama 知识束（教程类）
  - [ ] R/I/E/V：梳理 docs/ 结构，生成 concepts/examples/references

- [ ] Task 12: 生成 key-book 知识束（教程类·理论书籍）
  - [ ] R/I：梳理 8 章 + 附录结构，产出 facts/insights
  - [ ] E：生成 concepts/（可学性/复杂度/泛化界/稳定性/一致性/收敛率/遗憾界）、examples/、references/
  - [ ] V：校验

- [ ] Task 13: 生成 pumpkin-book 知识束（教程类）
  - [ ] R/I：梳理 docs/ 结构与 errata，产出 facts/insights
  - [ ] E：生成 concepts/（西瓜书公式推导专题）、examples/、references/
  - [ ] V：校验

- [ ] Task 14: 生成 tiny-universe 知识束（教程类·README 白盒指南）
  - [ ] R/I：基于 README 梳理 Tiny 系列模块（TinyDiffusion/TinyRAG/TinyAgent 等），产出 facts/insights
  - [ ] E：生成 concepts/examples/references
  - [ ] V：校验

- [ ] Task 15: 生成 vibe-vibe 知识束（教程类）
  - [ ] R/I/E/V：梳理 docs/ 多语言结构，生成 concepts/examples/references

- [ ] Task 16: 生成 code-your-own-llm 知识束（教程类·精简便签）
  - [ ] R/I/E/V：基于 README + AGENTS.md + index.html，生成精简 concepts/examples/references

- [ ] Task 17: 生成 Agent-Learning-Hub 知识束（教程类·精简便签）
  - [ ] R/I/E/V：基于 README + index.html，生成精简 concepts/examples/references

- [ ] Task 18: 生成 deepagents-in-action 知识束（教程类·精简便签）
  - [ ] R/I/E/V：基于 README，生成精简 concepts/examples/references

- [ ] Task 19: 生成 members-visualization 知识束（占位收录）
  - [ ] E：基于 .npmrc/仓库信息，生成极简 index.md（说明为占位收录，无实源码）

- [ ] Task 20: 更新总索引并收尾
  - [ ] 更新 `bundles/datawhale/index.md`：全部 bundle 完成后 `status: stable`，补充统计与学习路径
  - [ ] 更新 `bundles/index.md`：新增 datawhale 分组行，`groups` 16→17、`total_bundles` 110→128
  - [ ] 全量链接检查（`/` 开头 bundle-relative 路径无断裂）
  - [ ] C 阶段：萃取可复用模式沉淀至 `docs/retrospective/patterns/`

# Task Dependencies

- Task 2-19（各 bundle 生成）依赖 Task 1（分组骨架）
- Task 20（收尾）依赖 Task 2-19 全部完成
- Task 2-19 之间相互独立，可分四批并行委派（每批 ≤5 个 sub-agent）