# Tasks

- [x] Task 1: R 阶段——源码事实采集
  - [x] SubTask 1.1: 通读 `agentskills/docs/specification.mdx`（权威格式规范），提取 frontmatter 字段、命名规则、目录约定等格式要求事实
  - [x] SubTask 1.2: 通读 `agentskills/docs/skill-creation/` 5 篇 mdx 与 `clients.mdx`、`client-implementation/adding-skills-support.mdx`，提取创作指南与客户端生态事实
  - [x] SubTask 1.3: 通读 `skills-ref/src/skills_ref/` 6 模块（parser/validator/prompt/models/cli/errors）与 `tests/` 3 个测试文件，提取函数签名、校验规则、CLI 命令事实
  - [x] SubTask 1.4: 全部事实编号 F-xxx 写入 `.trae/specs/okf-wiki-ecosystem/agentskills-okf-wiki/facts.md`，通过 G1 门（零推断性表述）

- [x] Task 2: I 阶段——架构洞察与知识地图
  - [x] SubTask 2.1: 基于 facts.md 提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组）
  - [x] SubTask 2.2: 设计知识地图（入门→核心→高级学习路径），确定每篇概念文档覆盖的 F-xxx 事实
  - [x] SubTask 2.3: 写入 `.trae/specs/okf-wiki-ecosystem/agentskills-okf-wiki/insights.md`，通过 G2 门

- [x] Task 3: E 阶段——OKF 文档批量生成（信源先行）
  - [x] SubTask 3.1: 创建 `doc/bundles/ai/ai-agent/agent-skills-spec/` 目录结构，先生成 references/（≥2 篇信源登记：规范文档 + skills-ref 源码）
  - [x] SubTask 3.2: 分批生成 concepts/（每批 ≤7 文件，共 8 篇：技能解剖/渐进式披露/frontmatter 字段/创作原则/eval 驱动迭代/description 优化/客户端集成/skills-ref 实现）
  - [x] SubTask 3.3: 生成 examples/（2 篇：创建第一个 Skill、skills-ref CLI 实战）
  - [x] SubTask 3.4: 最后生成根 index.md（含 okf_version: "0.2"）+ 子目录 index.md（无 frontmatter、含 toctree 块）+ log.md，通过 G3 门

- [x] Task 4: V 阶段——独立验证与修复
  - [x] SubTask 4.1: Frontmatter 完整性 + 交叉链接（`/` 开头 bundle-relative）+ Index 完整性检查（V 阶段发现并修复 7 项问题：wikilink 不可构建/断链/嵌套围栏/测试计数 41→40/500 行断言/错别字/分组 toctree 注册）
  - [x] SubTask 4.2: Grep 级 API 验证：文档引用的函数名/类名/CLI 命令在 skills-ref 源码中存在（全部通过，零虚构 API）；规范条款与 specification.mdx 一致性抽查 9 条全部一致
  - [x] SubTask 4.3: 运行 `invoke gates.all`（UTF-8 + toctrees），通过 G4 门

- [x] Task 5: 导航索引更新
  - [x] SubTask 5.1: 更新 `ai/ai-agent/index.md`：total_bundles 30→31、"技能规范"类新增 agent-skills-spec 行、toctree 追加
  - [x] SubTask 5.2: 更新 `bundles/index.md` 总索引统计（282→283 束，ai 域 109→110，ai-agent 30→31）

- [x] Task 6: C 阶段——原子提交
  - [x] SubTask 6.1: 子模块 awesome-okf-xs 原子提交（新 bundle 17 文件 + 两处索引更新，commit `b3c3c118`，19 files +1738/-8）
  - [x] SubTask 6.2: 主仓库 SpecWeave 原子提交（spec 五件套 + 子模块指针推进，commit `41642cb7e`，6 files）；是否 push 等待用户指令

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 2（信源先行是 Task 3 内部第一步）
- Task 4 depends on Task 3
- Task 5 depends on Task 4（索引统计需以验证后的最终文档数为准）
- Task 6 depends on Task 5
