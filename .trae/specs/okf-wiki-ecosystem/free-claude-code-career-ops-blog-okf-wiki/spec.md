---
type: specification
title: "free-claude-code 与 career-ops 博文转 OKF Wiki"
source: "https://mp.weixin.qq.com/s/yEmCTdlwaKyj_h9eQRBsJg"
status: completed
---

# free-claude-code 与 career-ops 博文转 OKF Wiki

## 内容敏感度预检

微信公众号文章为公开页面，无 `share?code=`、`token` 或企业内部访问控制参数，按公开工作流处理。Spec 位于 `.trae/specs/`，最终 bundle 位于 `projects/awesome-okf-xs/doc/bundles/`。

## 场景与链路

本任务是知识沉淀场景，按七概念方法论编排 `R → I → E → V`：先提取事实，再拆解机制，生成知识包，最后进行对抗审查与机械验证。文章转化专用流程补充信源距离预判、P0 核验、双份 F 编号对拍和索引收尾。

## 骨架判定

文章介绍两个开源项目，但明确将完整安装步骤留给各自 README，正文没有固定版本、完整输入输出和可复现操作顺序。因此操作可复现性两问中至少一问为“否”，本 bundle 不创建 `examples/`，定位为“开源项目资讯与组合机制综述，非操作教程”。

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/agent-platform-notes/` | ✅ | 主线是多个 Agent 工具的组合与使用门槛，现有分组已收录独立 Agent 平台和资讯型条目 |
| `jishu/ai/anthropic/` | ❌ | free-claude-code 明确不是 Anthropic 官方项目，career-ops 也不是 Anthropic 产品 |
| 新建分组 | ❌ | 单篇博文不新建分组，避免目录碎片化 |

## 知识地图

1. `00-project-facts.md`：两个项目的事实、边界和证据等级。
2. `01-combination-loop.md`：代理层、模型层、任务层的组合闭环。
3. `02-access-and-risk-boundaries.md`：免费额度、隐私、合规、人工确认和时效边界。

## 验收标准

- 所有数字、项目名、协议和能力声明均可回溯到 `F-xxx`。
- 博文事实与官方 README 的差异在 `verification.md` 中显式记录。
- bundle 根索引与子目录索引均含 `{toctree}`。
- 不创建未经文章支持的安装教程、性能承诺或生产建议。
- `facts.md` 与 `references/article-source.md` 的 F 编号集合连续且一致。
