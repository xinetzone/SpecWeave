---
type: facts
title: "public-apis 事实登记"
source: "https://mp.weixin.qq.com/s/rCCa5Y_UpWB_HKL4VCORvA"
status: flagged
---

# public-apis 事实登记

| 编号 | 声明 | 来源 | 状态与限制 |
|---|---|---|---|
| F-001 | 微信文章标题为“471k+ Stars！1700个免费的开源 API 随便调用，超牛！”，作者为小知，公众号为 AI开源无界，发布时间显示为 2026-08-27 09:05。 | W | 页面元信息已读 |
| F-002 | 文章将 `public-apis` 定位为 GitHub 上的开源公共 API 清单，仓库地址为 `public-apis/public-apis`。 | W | 文章事实 |
| F-003 | README 的项目简介为 “A collective list of free APIs”。 | W、O1 | 官方 README 与文章一致 |
| F-004 | 文章声称 README 有 51 个分类。 | W | 当前 raw README 读取仍统计为 51，已核验 |
| F-005 | 文章声称表格条目合计 1700 多个；2026-09-20 读取当前 raw README 的 Markdown 条目行约 1850 条。 | W、O2 | 数量随仓库变化，文章为过时快照 |
| F-006 | 文章声称项目约有 4.7 万 Star。 | W | 与当前 GitHub API 返回的 267955（API 快照陈旧）及其他页面快照不一致，核心数字 flagged |
| F-007 | 仓库 LICENSE 文件声明 MIT License。 | W、O3 | 官方仓库元数据与 LICENSE 一致 |
| F-008 | 每条目录记录使用 `Description`、`Auth`、`HTTPS`、`CORS` 等字段。 | W、O2 | 官方 README 结构可见 |
| F-009 | `Auth` 用于提示是否需要认证，文章举例包括 `apiKey` 与 `OAuth`。 | W | 目录字段说明；各 API 条款需单独核对 |
| F-010 | 文章列举动物、艺术设计、金融、汇率/加密货币、天气、美食、新闻、游戏、动漫、交通、机器学习、书籍、测试数据、娱乐/语录等类别。 | W | 代表性分类，不是完整列表 |
| F-011 | 文章把 `Auth=No`、`HTTPS=Yes`、`CORS=Yes` 视为前端练习时较省事的筛选组合。 | W | 作者经验/推导，不是安全或可用性保证 |
| F-012 | 贡献指南要求条目有正式文档、描述简短、分类正确，并不鼓励明显推广付费服务的条目。 | W、O4 | 官方贡献规则需以当前仓库为准 |
| F-013 | `public-apis` 本身是目录，不负责统一调用目录中的第三方 API；使用者仍需进入每个服务的官方文档。 | W、O2 | 结构事实与使用边界 |
| F-014 | 配套仓库 `davemachado/public-api` 的 README 将服务描述为 `public-apis` 项目的官方公共 API。 | W、O5 | 配套项目自述 |
| F-015 | 配套 API 基础地址为 `https://api.publicapis.org/`，文档声明无需鉴权、支持 HTTPS 和 CORS。 | W、O5 | 官方项目 README 自述，未做生产 SLA 验证 |
| F-016 | 配套 API 文档列出 `GET /entries`，支持按 title、description、auth、https、cors、category 查询参数筛选。 | W、O5 | 官方接口文档 |
| F-017 | 配套 API 文档列出 `GET /random`、`GET /categories`、`GET /health`。 | W、O5 | 官方接口文档 |
| F-018 | GitHub API 将主仓库描述为 “A collective list of free APIs”，license key 为 `mit`，默认分支为 `master`。 | O2、O3 | 官方 API 快照，快照字段可能滞后 |
| F-019 | GitHub API 返回主仓库 `archived=false`、`disabled=false`。 | O2 | 官方 API 快照 |
| F-020 | “免费”在文章中被解释为可能存在免费入口或免费额度；是否商用、额度、稳定性、数据来源和合规要求由每个服务自行规定。 | W | 作者边界声明，适合作为使用警示 |
