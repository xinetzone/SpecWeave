---
type: spec
title: "腾讯开源 WeKnora 文章转 OKF Wiki"
source: "https://mp.weixin.qq.com/s/rfeZV_I7BgXaHDLsRM0YNw"
status: completed
---

# 腾讯开源 WeKnora 文章转 OKF Wiki

## 内容敏感度预检

源 URL 为公开微信公众号文章，无 `code`、`token` 或登录访问控制参数，按公开内容执行。规范事实基准保存在本目录 `facts.md`，公开知识包产出位于 `projects/awesome-okf-xs/doc/bundles/`。

## 场景与链路

- 方法论场景：知识沉淀
- 七概念链路：`R→I→E→V`
- `G1`：事实登记与作者观点分层
- `G2`：三层洞察结构完整
- `G3`：概念可迁移到其他知识库平台评估
- `V`：官方仓库与 API 文档核验，执行结构、事实、读者可用性和时效审查

## 骨架判定

| 判定问题 | 结论 |
|---|---|
| 文章是否提供读者可照做的安装、配置、代码或实测步骤？ | 否 |
| 这些步骤是否具备版本、输入输出和顺序明确的可复现性？ | 否 |

因此本 bundle 为技术综述/选型观察，不设 `examples/`。

## 归属位置

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/tencent/` | 选定 | 文章主线是腾讯开源 WeKnora，既有腾讯开源生态分组可承载非源码资讯 |
| `jishu/ai/ai-agent/` | 排除 | 文章不以 Agent 框架源码或通用运行时为主线 |
| 新建分组 | 排除 | 单篇文章新建分组违反最小变更原则 |

## 知识地图

1. `00-weknora-capability-foundation`：AI、数据接入、知识管理三项基础能力及官方边界。
2. `01-integrated-knowledge-system`：从数据汇聚到知识维护再到 RAG/Agent/Wiki 的组合机制。
3. `02-open-source-knowledge-base-selection`：作者观点与可迁移的选型维度，明确非官方竞争结论。

## 验收标准

- [x] F-001~F-018 连续登记，博文事实与官方核验事实分层。
- [x] 作者判断标注为“作者观点”，不伪装成官方表态。
- [x] 官方 README 与 API 文档列入 `sources` 并用于 P0/P1 核验。
- [x] bundle 根、子目录 index、references、concepts 和 log 均可由 toctree 到达。
- [x] 无 `file:///` 绝对路径，文档使用相对链接。
