# Spec —— Claude 模型选型 OKF Wiki

## 1. 目标

把 claude.dev 开发者博客 2026-11-09 的《Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku》（作者 Addy Osmani）转化为可溯源、可教学、可审计的 OKF v0.2 知识包，回答三个问题：选哪个模型、花多少钱、如何混用与迁移。

产出根目录：`projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/`。

## 2. 信源与敏感度

| 项 | 结论 |
|---|---|
| 主源文 | https://claude.dev/blog/which-claude-model-should-you-build-with/ |
| 备用正文 | https://claude.dev/blog/which-claude-model-should-you-build-with.md（官方 Markdown 版，28,987 字符） |
| 访问控制 | 公开页面，无 token / 邀请码 / 内部域名 → 标准工作流 |
| 内容性质 | 模型厂商官方开发者博客，属“官方发布 + 作者方法论建议”混合体 |
| 信源距离 | 官方发布（一手），但 benchmark 与内部实验为厂商自述 |
| 权威核验源 | anthropic.com 四个模型页 + Fable 5.2 发布文 + code.claude.com model-config 文档 |
| 核验受限 | platform.claude.com 在核验环境返回 “App unavailable in region”，API 细节只能单源登记 |

## 3. 骨架判定（操作可复现性两问）

1. 文章是否给出读者可照做的安装/配置/代码/调用/实测流程？**是**——给出 `.claude/agents/log-reader.md` 完整定义、`model: haiku`/`model: sonnet` 配置、`/model`、`/compact`、`/usage`、`/effort` 操作，以及一套四步自测流程。
2. 这些流程是否经作者实测、具备可复现性？**是（部分）**——子代理配置文件格式与别名解析有官方文档兜底；对比实验给出可执行的步骤顺序与产出形态（得分-花费图），但未附完整脚本与数据集。

结论：**设 `examples/`**，收录 2 篇可复现实践（Haiku 日志子代理、双模型成本对比）。同时保留“厂商 benchmark 不复算”的边界声明。

## 4. 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/practice` | ✅ 采用 | 该分类即“工程实践、方法论与行业洞察”，已含 gpt6-sol-luna-cost-efficiency、fable5-cost-optimization 两个同型选型/成本束，语义与先例同时吻合 |
| `jishu/ai/models` | ❌ | 该分类是基础模型能力与多模态发布解读；本束主体是“怎么选、怎么配、怎么测”，不是模型能力 |
| `jishu/ai/ecosystems/anthropic` | ❌ | 该目录是 Anthropic 官方仓库与文档教程（claude-code、cookbooks 等）；本束是跨模型的选型方法论 |
| `jishu/ai/learning` | ❌ | 该分类是学习路径与上手课程；本束是决策手册而非课程体系 |
| 新建分组 | ❌ | 单篇博文禁止新建分组 |

## 5. 三层知识拆分

| 层 | 内容 | 落点 |
|---|---|---|
| 事实层（What/How much） | 四模型阵容、价格、缓存价、上下文/输出上限、thinking 与 effort 默认值、fast mode | concepts/00 |
| 决策层（Which） | 按任务选型矩阵、effort 优先原则、升级顺序、延迟与准确率权衡 | concepts/01 |
| 经济层（Why） | 每 token 价 vs 每完成任务成本、最难任务占大头、缓存与上下文、Haiku 分档计价、低 effort + 失败重跑 | concepts/02 |
| 编排层（Mix） | 切换断点、thinking 兼容、子代理、advisor、批量委派、多智能体编排 | concepts/03 |
| 迁移层（Migrate） | preserved thinking 400、thinking 强制、tool_choice、computer use、Haiku 4.5→5.5、安全回退、多模型请求纪律 | concepts/04 |
| 验证层（Measure） | 四步自测闭环、得分-花费图、影子流量、快速对比 | concepts/05 + examples/01 |
| 操作层（Do） | Haiku 日志读取子代理、双模型成本对比 | examples/00、01 |

## 6. 质量门计划

| 门 | 检查项 | 通过标准 |
|---|---|---|
| G1 | 事实无因果推断 | facts.md 只登记源文明示内容与方法论建议，作者观点显式标注 |
| G2 | 洞察四元组 | 每个 concept 有现象、机制、影响、适用边界 |
| G3 | 模式可迁移 | 选型矩阵、升级顺序、自测闭环可迁移到其他模型家族 |
| G4 | 行动项原子化 | examples 每篇单一目标、可独立验证、有预期输出 |

## 7. 交付物

1. bundle：`jishu/ai/practice/claude-model-selection/`（index + concepts×6 + examples×2 + references×3 + log）
2. 索引接入：practice/index.md、jishu/ai/index.md、jishu/index.md、bundles/index.md 计数同步
3. 门禁：check-utf8.py、check-toctrees.py、check-frontmatter.py
4. 双份 F 编号：本 spec `facts.md` 与 bundle `references/article-source.md` 集合一致

## 8. 已知边界

- 价格与版本为 2026-11-10 快照，`stale_after` 设为 2026-12-31。
- platform.claude.com 文档在核验环境区域受限，API 默认 effort、advisor、preserved thinking 细节为博文单源。
- Sonnet 5.5 缓存读取价（博文 $0.10）与官方“最多 90% 缓存节省”口径存在冲突，正文按冲突披露。
