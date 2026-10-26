# Spec —— Designer-RSI 程序记忆演化 OKF Wiki

## 1. 目标

把微信公众号「符智汇」2026-09-25 的论文解读《Designer-RSI：用外部程序记忆，把“缺技能”和“常失败”变成可回放验证的改进》转化为可溯源、可教学、可审计的 OKF v0.2 知识包。

产出根目录：`projects/awesome-okf-xs/doc/bundles/`。

## 2. 信源与敏感度

| 项 | 结论 |
|---|---|
| 主源文 | https://mp.weixin.qq.com/s/XsUBelItpT4LnC_ETSv_Vw |
| 访问控制 | 公开文章，无 token / 邀请码 / 内部域名 → 标准工作流 |
| 内容性质 | 二手论文解读（作者一手阅读论文后的转述与评论），非厂商自宣 |
| 信源距离 | 第三方综述（作者转述 arXiv 论文） |
| 权威核验源 | arXiv:2609.22086 abs 页 + HTML 全文（CC BY 4.0） |

## 3. 骨架判定（操作可复现性两问）

1. 文章是否给出读者可照做的安装/配置/代码/调用/实测流程？**否**——全文是对论文机制与实验的分析，无命令、无代码、无参数配置。
2. 这些流程是否经作者实测、具备可复现性？**否**——论文本身亦未公开数据与代码（F-104）。

结论：**不设 `examples/`**。骨架为 `index + concepts/ + references/ + log`，description 标注“非操作教程”。

## 4. 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/practice` | ✅ 采用 | 该分类已有 24 束“工程实践、方法论与行业洞察”，含 agent-self-evolution-evaluation、ai-engineering-methodology 等论文/方法论解读束，语义吻合 |
| `jishu/ai/frameworks` | ❌ | 该分类是框架与代码库源码教程；本束无代码仓 |
| `jishu/ai/models` | ❌ | 该分类是基础模型能力；本束主体是外部程序记忆与演化闭环，不是模型能力 |
| `jishu/ai/learning` | ❌ | 该分类是学习路径与上手教程；本束不是课程 |
| 新建分组 | ❌ | 单篇博文禁止新建分组 |

## 5. 三层知识拆分

| 层 | 内容 | 落点 |
|---|---|---|
| 事实层（What/When/Who） | 论文元信息、问题设定、系统四角色、技能库与冷启动 | concepts/00、01 |
| 机制层（How） | 两阶段检索、Widening、Deepening、Replay Gate、Graphic-Eval | concepts/02–05 |
| 证据层（How well） | 五轮演化动力学、通用 T2I、专业设计、消融、非单调回退 | concepts/06 |
| 边界层（What not） | 六类局限、失败模式、治理前提、迁移条件 | concepts/07 |

## 6. 质量门计划

| 门 | 判据 | 计划验证方式 |
|---|---|---|
| G1 | 事实无推断词，观点显式标注 | facts.md 逐条核对信源定位与口径类型 |
| G2 | P0 逐项过勘误四清单（日期版本/成效溯源/口径对照/引文逐字） | 15 项核验记录写入 references/verification.md |
| G3 | 信源先行、F 编号引用、index 最后写 | 生成顺序 references → concepts → index |
| G4 | 双份 F 编号一致、计数同步、链接可达、UTF-8 严格 | 脚本机械校验 + log.md 记录 |

## 7. 预期产物

```
projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/designer-rsi-procedural-memory/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-overview.md
│   ├── 01-procedural-memory.md
│   ├── 02-retrieval-and-injection.md
│   ├── 03-evolution-widening-deepening.md
│   ├── 04-replay-gate.md
│   ├── 05-graphic-eval.md
│   ├── 06-results.md
│   └── 07-limits-and-adoption.md
└── references/
    ├── index.md
    ├── article-source.md
    ├── verification.md
    └── glossary.md
```

## 8. 非目标

- 不复现论文实验（无数据、无代码、无 GPU 环境）。
- 不评价 Adobe 产品路线，不构成采购或部署建议。
- 不把论文结论外推为“通用 Agent 自我进化已解决”。
