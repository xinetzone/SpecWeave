---
id: "wechat-mp-archiver-docs-storage-layout"
title: "wechat-mp-archiver 存储布局与源码结构"
source: "../README.md#存储布局"
---
# wechat-mp-archiver 存储布局与源码结构

## 存储布局

```text
apps/dev-tools/wechat-mp-archiver/
├── .env                         # 凭证与运行配置（gitignore，从 .env.example 复制）
├── data/
│   ├── archive.db               # SQLite 元数据库：articles/media/comments/metrics/sync_state 五表
│   └── official_api_quota.json  # 官方接口日配额计数（按 UTC 日滚动，自动生成）
├── archive/<账号别名>/<YYYY>/<YYYY-MM-DD_标题>/
│   ├── article.html             # 正文快照：图片本地化、链接相对化，可离线打开
│   ├── article.md               # 正文 Markdown（标题/列表/代码/引用结构保留）
│   ├── metadata.json            # 文章元数据 + 媒体下载清单（含失败例外表）
│   ├── images/                  # 正文图片（含懒加载 data-src）
│   └── media/                   # 语音/视频等富媒体（已迁移视频号的内容只登记外链）
├── exports/                     # 派生产物（gitignore）：rag.jsonl、report/report.{html,csv}
└── logs/                        # 定时任务运行日志（调度脚本自动创建）
```

采集服务侧的登录凭证不在本目录，持久化在 Docker 命名卷 `mp_archiver_collector_data`（备份/迁移见 [deploy/README.md](../deploy/README.md) 第 6 节）。

> **注意**：`.gitignore` 会排除 `.env`、`data/`、`archive/`、`exports/`、`logs/`。若在其他部署位置使用，归档根目录、数据库路径、导出根目录均可经环境变量调整（见 [03-operations.md](03-operations.md)）。

## 源码结构

```text
src/mp_archiver/
├── config.py          # pydantic-settings 配置（MP_ARCHIVER_ 前缀）
├── models.py          # 采集状态枚举与文章模型
├── logging_utils.py   # 凭证脱敏日志
├── naming.py          # 跨平台安全文件名
├── http_client.py     # 保守限速 + 指数退避 HTTP 客户端
├── db/                # SQLite 五表（articles/media/comments/metrics/sync_state）
├── adapters/          # 采集源适配器（采集服务 R2 / 官方接口）
├── core/              # 列表同步、正文/富媒体/互动归档、pipeline 统一编排
└── exporters/         # 派生产物导出（RAG JSONL：rag.py；分析报表：report.py；提取清洗：core/text_extract.py）
```

## 仓库内其他目录

| 目录 | 说明 |
|---|---|
| `deploy/` | 采集服务私有部署（`docker-compose.yml`、`collector.env.example`、`sync-incremental.ps1`、[deploy/README.md](../deploy/README.md)） |
| `tests/` | pytest 测试集（含验收、故障注入、CLI、导出与适配器用例） |
| `docs/` | 本应用人类可读文档（[索引](README.md)） |
| `.agents/` | 本应用 AI 协作者资产（[索引](../.agents/README.md)） |

## 相关文档

- [文档索引](README.md)
- [命令参考](02-commands.md)
- [定位与架构](00-overview.md)