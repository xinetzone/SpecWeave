# 网易有道开源生态 OKF Wiki 教程 - 实施计划

> **执行顺序原则**：先完成 G0 信源稳定性门（无稳定信源不开始 R 阶段），再按"单仓库 R→I→E 闭环、V 阶段统一验证"推进。各仓库 R/I/E 任务相互独立，可并行委派子代理；QAnything、LobsterAI 规模较大，R 阶段按子系统拆分。所有实现任务通过子代理委派执行。

---

## 阶段零：G0 信源稳定性门（前置强制）

- [x] Task 1: vendor 子模块迁移基线记录与迁移执行
  - [x] SubTask 1.1: 记录 6 个仓库的 HEAD commit、主分支、远程 URL、LICENSE 作为迁移基线，写入本 spec 目录 `migration-baseline.md`（勘察值与实际值全部一致）
  - [x] SubTask 1.2: 验证 6 个目录未被主仓库 git 跟踪且工作树干净；确认无指向旧临时克隆目录的现存引用（GATE-SPS 预扫描，2 处预期命中均为本计划文本，已语义裁决）
  - [x] SubTask 1.3: 在 `vendor/netease-youdao/` 下执行 `git submodule add` 添加 6 个子模块（SSH URL），检出到各自固定 commit（固定决策：EmotiVoice/QAnything HEAD 分别超前 v0.3/v2.0.0 共 17/69 commits，按基线 pin 勘察 HEAD commit，LobsterAI HEAD 恰为 tag 2026.9.4 指向 commit）
  - [x] SubTask 1.4: 更新 vendor 元数据：`vendor/AGENTS.md` 路由表、`vendor/README.md` 依赖清单、`vendor/VERSION.md` 版本记录（含 tag/commit hash/许可证/日期）
  - [x] SubTask 1.5: 运行 `python .agents/scripts/check-vendor.py --deep` 合规检测；运行 GATE-SPS 确认零引用后删除旧临时克隆目录（netease-youdao 全部通过；rc=1 仅因迁移前已存在的 podman-* 未初始化）
  - [x] SubTask 1.6: 验证既有子模块（flexloop、ark-cli、awesome-okf、knowledge-catalog 等）未受影响（11 个既有子模块 hash 逐一比对与基线一致）

## 阶段一：R 阶段事实采集（6 仓库并行）

- [x] Task 2: BCEmbedding 事实采集——阅读 `BCEmbedding/` 包（models、utils）、setup.py、README，提取 Embedding/Reranker 模型接口、参数、数据流事实，写入 references 事实清单（F-bc-xxx）
- [x] Task 3: Confucius4-TTS 事实采集——阅读 confuciusts/（flow、llm）、external/bigvgan、server.py、webui.py、example.py、训练配置 yaml，提取 TTS 推理/训练链路事实（F-c4t-xxx）
- [x] Task 4: EmotiVoice 事实采集——阅读 inference_tts.py、frontend*.py、models/hifigan、text/、mfa/、训练脚本，提取多音色情感控制推理链路事实（F-ev-xxx）
- [x] Task 5: LobsterAI 事实采集（按子系统拆分）——阅读 src/main（im/、libs/、mcp/、skills/、skins/、agentManager 等）、src/renderer、src/shared、src/scheduledTask、SKILLs/，提取 Electron 主进程/渲染进程/IM 网关/MCP 运行时/协作协议事实（F-la-xxx）
- [x] Task 6: QAnything 事实采集（按子系统拆分）——阅读 qanything_kernel、scripts/、front_end/、API 文档，提取 RAG 内核、检索链路、API 接口事实（F-qa-xxx）
- [x] Task 7: ScholarClaw 事实采集——阅读 server/（config、index、types）、scripts/、SKILL.md、examples/，提取学术搜索 Agent 服务与脚本事实（F-sc-xxx）

## 阶段二：I 阶段架构洞察（依赖对应 R 任务）

- [x] Task 8: 六个仓库洞察提炼与知识地图——每仓库 3-5 个四元组洞察（陈述+证据 F-xxx+反常识+行动），设计各 bundle concepts/ 编号文档清单与学习路径，写入各 bundle references/insights 文件

## 阶段三：E 阶段批量生成（信源先行，index 最后写）

- [x] Task 9: 创建 `doc/bundles/jishu/ai/netease-youdao/` 分组骨架——group index.md（okf_version frontmatter + 生态关系概述 + 6 束导航）；6 个 bundle 目录结构（concepts/examples/references 空 index 占位除外，index 最后写）
- [x] Task 10: 生成 6 个 bundle 的 references/ 信源文件（含 facts/insights 归档与 sources 登记），先于一切 concepts/examples
- [x] Task 11: 小束生成（ScholarClaw、Confucius4-TTS、BCEmbedding）——每束 concepts/ 分批生成（每批 ≤7），再 examples/，附 F-xxx 事实编号（2026-09-09 子代理执行注记：3 束 concepts 18 篇 + examples 8 篇全部落盘，九字段 frontmatter 齐全、F 编号零越界、未写任何 index.md）
- [x] Task 12: 大束生成（EmotiVoice、QAnything、LobsterAI）——每束 concepts/ 分批生成（每批 ≤7），再 examples/，附 F-xxx 事实编号（2026-09-09 子代理执行注记：3 束 concepts 21 篇 + examples 13 篇全部落盘，LobsterAI 11 篇 concepts 与 QAnything 8 篇均分两批 ≤7 执行，九字段 frontmatter 齐全、F 编号零越界、未写任何 index.md）
- [x] Task 13: 统一书写各级 index.md（根 index + concepts/index + examples/index + references/index），每个含 `{toctree}` 块收录本目录全部内容文档（最后写）（2026-09-09 子代理执行注记：6 束 × 4 级共 25 个 index 全部完成，toctree 共 95 条目 Glob 核验零悬空；type 大小写定夺：保留小写，分组 index 已注明规范大小写不敏感及理由；分组 index status 维持 draft 待 V 通过后随 Task 15 转 stable）

## 阶段四：V 阶段独立验证

- [x] Task 14: 逐 bundle 验证——frontmatter 完整性、sources 指向存在、链接无断裂（`/` 开头 bundle-relative）、零虚构 API（Grep vendor 源码验证每个类名/方法名）、计数断言比对（Glob/Grep 独立复核"X个/Y处"类陈述）（2026-09-09 执行注记：六束 V 验证汇总——bcembedding/confucius4-tts/emotivoice/scholarclaw/lobsterai 五束 PASS，qanything 首验 FAIL 后经修复回合（子代理执行 E1-E4 修复 + 11 篇文档 status 升 stable）达标；累计修复断链 1 处、frontmatter 缺字段若干、计数/命名/编号类事实错误 30+ 处（emotivoice 2 处 tn_chinese 条件分流描述、lobsterai 10 文件 18 处含 agents 表 20 列/slice 21 个 .ts/测试 38 顶层 43 递归/方法全名/order 分段等，均经主流程对照 vendor 源码逐一复核）；任务书所注 `d:\AI\.chaos\libs\` 路径不存在，实际信源为 `vendor/netease-youdao/` 子模块，修复代理已按实际源码为准并注明）
- [x] Task 15: 导航与规范验证——`python scripts/check-toctrees.py`（awesome-okf-xs 内）toctree 链完整；子目录 index 无 frontmatter；根 index 含 okf_version；输出验证报告并修复全部问题（2026-09-09 执行注记：首跑 rc=1 报 113 处问题——111 处系 `jishu/ai/index.md` toctree 漏收 `netease-youdao/index` 导致整棵子树不可达（补 toctree 条目 + 域内分组导航表行后消除），另 2 处为预存在的 domestic-model-token-export references/index.md 缺 toctree 块（顺带修复）；复跑 rc=0「全部 index.md 引用有效，所有内容文档均可达」；子目录 index 无 frontmatter、分组/束根 index frontmatter 完整均经 Grep/Read 核验；分组 index status 已 draft→stable）

## 阶段五：C 阶段模式沉淀

- [x] Task 16: 模式萃取与原子提交——回顾五阶段执行顺利点/问题点，新反模式或改进点回写 source-code-to-okf-wiki 相关模式文档；全部变更按 Conventional Commits（中文主体、单一职责）原子提交

# Task Dependencies

- Task 2~7（R 阶段）依赖 Task 1（G0 完成，信源就位）
- Task 8 依赖 Task 2~7（各仓库 R 完成）
- Task 10 依赖 Task 8（洞察与信源内容定稿）；Task 9 可与 Task 10 并行
- Task 11、Task 12 依赖 Task 10（信源先行）
- Task 13 依赖 Task 11、Task 12（内容定稿后最后写 index）
- Task 14、Task 15 依赖 Task 13
- Task 16 依赖 Task 14、Task 15（V 阶段通过后收尾）
