---
type: spec
title: "《2026年，搭建自动赚钱系统的三个新方向》OKF Wiki"
source: "https://mp.weixin.qq.com/s/IWGzMXG3s-x0AE73gov4sQ"
status: completed
---

# 任务规格

## 内容敏感度预检

- 来源为公开微信公众号文章，无 `share?code=`、`token` 或企业内部域名信号。
- 判定：公开内容。
- 工作流：`.trae/specs/` 记录规划，知识包落入 `projects/awesome-okf-xs/doc/bundles/`。

## 七概念编排

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20260923-auto-money-system | msg=公开文章转OKF Wiki | ctx={"scenario":"knowledge","topic":"自动赚钱系统三个新方向","depth":"deep"}
```

- 场景：知识沉淀。
- 链路：`R → I → E → V`。
- G1：原文事实、作者观点、作者建议和算术示例分层。
- G2：每个洞察包含现象、机制解释、边界与行动建议。
- G3：模式包含触发条件、步骤、反模式和迁移验证。
- V：事实溯源、结构、读者可用性、时效边界四视角审查。
- C：本次不执行 Git 提交，等待用户明确提交请求。

## 骨架判定

文章提供的是方向判断和轻量建议，没有版本、安装、输入输出、代码或经实测的完整操作顺序。两问结论：

1. 没有可直接复现的安装/配置/调用流程。
2. 建议没有给出可审计的版本、输入、输出和实验记录。

因此采用商业分析/战略资讯骨架：`index + concepts + references + log`，不创建 `examples/`。

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/industry/auto-money-system/` | ✅ | 主线是 AI 商业化、个人 IP 与轻交付产品的自动化变现系统，属于行业与商业趋势。 |
| `sheke/industry/ai-one-person-micro-product/` | △ | 有个人 IP 与轻产品交集，但本文同时覆盖 AI 应用层和内容层，单一微产品不是唯一主线。 |
| `jishu/ai/` | ❌ | 文章没有提供 AI 技术实现教程或 API 级操作。 |
| 新建顶级分组 | ❌ | 单篇文章不应新建分组。 |

## 知识地图

| 层级 | 产出 |
|---|---|
| 事实层 | `references/article-source.md`、`references/verification.md` |
| 机制层 | `concepts/00-three-directions.md` |
| 组织层 | `concepts/01-system-layers-and-automation.md` |
| 落地边界层 | `concepts/02-validation-and-boundaries.md` |

## 事实登记

事实唯一登记见 [`facts.md`](facts.md)，F-001 至 F-017 连续。原文没有外部脚注；原文数字和建议均不升级为独立市场事实。

## 验收标准

- [x] bundle frontmatter 含 OKF v0.2 必填字段与 `status: flagged`。
- [x] 所有正文中的模型名、数字、日期和建议回指 F 编号。
- [x] `article-source.md` 与本 spec 的 F 编号集合一致。
- [x] 每个目录 index 含隐藏 toctree。
- [x] 不创建 `examples/`，并在根索引说明原因。
- [x] 完成四视角 V 审查和手动等效门禁。
