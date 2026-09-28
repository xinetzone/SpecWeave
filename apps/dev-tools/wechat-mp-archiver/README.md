# wechat-mp-archiver

微信公众号全量内容归档工具：通过**私有部署的开源采集服务**（R2 主路线）获取指定公众号的历史文章列表，由本 Python 管线完成正文/富媒体下载、元数据管理、断点续采与增量更新，产出三种形态：

- **离线归档**：原始 HTML 快照 + 本地化图片 + Markdown，按 `archive/<账号>/<年>/<日期_标题>/` 组织；
- **RAG 语料**：带 YAML frontmatter 的 Markdown 导出；
- **分析报表**：更新趋势、失败/对账清单。

技术选型与合规边界见 [技术方案文档](../../../docs/knowledge/operations/wechat-mp-full-archive-solution.md)。
**仅供个人学习研究与本地存档使用，请勿商用或公开再分发归档内容**；完整条款见 [docs/05-compliance.md](docs/05-compliance.md)。

## 架构

采集服务承载微信登录态、向管线提供文章列表接口（仅回环 `127.0.0.1:5000`）；管线只通过回环地址取列表，正文与媒体下载由管线直连 `mp.weixin.qq.com` 完成（剥离采集服务 Token），数据全部落地本机。派生产物（RAG/报表）为纯离线任务，不触网。完整架构图见 [docs/00-overview.md](docs/00-overview.md)。

## 快速开始

安装（Python ≥ 3.14）：进入 `apps/dev-tools/wechat-mp-archiver` 建虚拟环境后 `pip install -e ".[dev]"`，逐步命令见 [docs/01-quickstart.md](docs/01-quickstart.md)。

1. 准备**采集专用微信订阅号**（个人主体即可），由管理员本人扫码授权（前提见 [deploy/README.md](deploy/README.md) 第 1–3 节）。
2. 部署采集服务：`cd deploy && docker compose up -d`（仅绑 `127.0.0.1:5000`），浏览器打开 <http://127.0.0.1:5000/login.html> 扫码确认（完整步骤见 deploy/README.md 第 1–3、6 节）。
3. 配置管线：`copy .env.example .env`（PowerShell；bash 用 `cp`）。**凭证只走环境变量/.env，`.env` 已被 gitignore。**
4. `mp-archiver init-db && mp-archiver doctor`（预期「采集服务在线」）。
5. 小批量试跑：`mp-archiver list -a 意识食谱 --max-pages 2` → `mp-archiver fetch -a 意识食谱 --limit 1`。
6. 转入日常：每日 `mp-archiver sync -a 意识食谱`（增量、幂等）；每周至多一次 `mp-archiver run -a 意识食谱 --full`（全量回溯+下架对账）。计划任务配置见 deploy/README.md 第 12 节。

## 命令速查

```bash
mp-archiver doctor          # 环境自检
mp-archiver init-db         # 初始化 SQLite 元数据库
mp-archiver sync -a <账号>   # 日常增量：列表追平 + 归档新文章（幂等）
mp-archiver run -a <账号> --full   # 全量回溯：完整翻页 + 下架对账 + 归档
mp-archiver fetch -a <账号> [--limit N] [--include-failed]   # 仅归档正文
mp-archiver list -a <账号> [--max-pages N]                    # 仅同步列表
mp-archiver export-rag      # 离线导出 RAG JSONL 语料（→ exports/rag.jsonl）
mp-archiver report          # 离线生成分析报表（→ exports/report/）
```

全部命令、`sync`/`run` 编排语义、退出码契约与导出字段说明见 [docs/02-commands.md](docs/02-commands.md)。默认限速、故障处置与断点续跑、故障排查速查见 [docs/03-operations.md](docs/03-operations.md)。

## 文档与规范

| 面向 | 入口 | 说明 |
|---|---|---|
| 人类读者 | [docs/README.md](docs/README.md) | 文档索引（定位/快速开始/命令/运维/存储/合规 6 篇） |
| AI 协作者 | [AGENTS.md](AGENTS.md) | 应用级路由入口（启动协议 + P0 约束速览） |
| AI 协作者 | [.agents/README.md](.agents/README.md) | AI 资产容器索引（归档管线硬约束规则 + 变更日志） |

## 合规声明

1. **个人学习与存档限定**；2. **不绕付费与权限**；3. **尊重版权**；4. **频率自律**（默认保守限速）；5. **凭证与数据安全**（仅管理员本人扫码、凭证只存 `.env`）；6. **24 小时删除义务**（收到权利人主张后 24 小时内删除对应本地归档）。完整条款见 [docs/05-compliance.md](docs/05-compliance.md)。

## 存储布局

```text
apps/dev-tools/wechat-mp-archiver/
├── .env                         # 凭证与运行配置（gitignore，从 .env.example 复制）
├── data/                        # archive.db 五表 + official_api_quota.json
├── archive/<账号>/<YYYY>/<YYYY-MM-DD_标题>/   # article.html / article.md / metadata.json / images/ / media/
├── exports/                     # 派生产物（gitignore）：rag.jsonl、report/report.{html,csv}
├── deploy/                      # 采集服务私有部署（docker-compose + README）
├── docs/                        # 本应用人类可读文档（索引见 docs/README.md）
└── logs/                        # 定时任务运行日志
```

完整存储布局与源码结构见 [docs/04-storage-and-layout.md](docs/04-storage-and-layout.md)。
