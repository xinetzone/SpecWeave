---
id: "wechat-mp-archiver-docs-commands"
title: "wechat-mp-archiver 命令参考"
source: "../README.md#命令"
---
# wechat-mp-archiver 命令参考

## 命令总览

```bash
mp-archiver doctor     # 环境自检（数据库、归档目录、采集服务连通性）
mp-archiver init-db    # 初始化 SQLite 元数据库
mp-archiver list -a 意识食谱          # 同步指定公众号全量文章列表
mp-archiver list -a 意识食谱 --max-pages 2   # 调试：仅翻 2 页（不做下架对账）
mp-archiver fetch -a 意识食谱         # 归档正文（HTML/Markdown/图片/metadata 四件套）
mp-archiver fetch -a 意识食谱 --limit 10     # 先小批量试跑
mp-archiver fetch -a 意识食谱 --include-failed  # 同时重试此前失败的文章
mp-archiver sync -a 意识食谱          # 日常增量：列表追平 + 归档新文章（幂等，可重复执行）
mp-archiver run -a 意识食谱 --full    # 全量回溯：完整翻页 + 下架对账 + 归档（可加 --include-failed）
mp-archiver sync-official -a 意识食谱  # 可选：自有认证号官方清单交叉补全（见 deploy/README.md 第 11 节）
mp-archiver official-doctor -a 意识食谱  # 官方接口分阶段探针（配置/网络/token/batchget/biz；--network-only 免凭证）
mp-archiver resolve-biz "文章链接"        # 从文章 URL（含 /s/ 短链）解析 __biz，供 MP_ARCHIVER_WECHAT_OFFICIAL_BIZ 使用
mp-archiver export-rag                    # 离线导出 RAG JSONL 语料（全部账号 → exports/rag.jsonl）
mp-archiver export-rag -a 意识食谱 --no-clean --with-raw  # 单账号/不清洗/附清洗前原文对照
mp-archiver report                    # 离线生成分析报表（全部账号 → exports/report/）
mp-archiver report -a 意识食谱 --top 20   # 单账号 + 合集 Top 20
pytest                 # 运行测试
```

## 编排命令：`sync` 与 `run`

`sync` 与 `run` 是统一编排命令，一次完成「列表 → 正文/富媒体 →（可选）互动」：

- **增量模式**（`sync`）从最新页向后翻，遇到整页全已知即停，只下载 pending 新文章；
- **全量模式**（`run --full`）翻到历史尾页并执行下架对账（未显式加 `--full` 不会执行，防止误触发长任务）。

两者均幂等可中断：进程随时终止后重跑，已归档文章按状态自动跳过、失败文章随后续任务补齐，不产生重复文件。

**退出码契约**：

| 退出码 | 含义 |
|---|---|
| `0` | 成功 |
| `1` | 存在失败文章或参数错误 |
| `2` | 登录态失效需重新扫码 |
| `3` | 账号未找到（`sync-official` 路径亦表示 biz 未配置） |
| `4` | 环境/风控异常（采集服务不可达、端点发现失败、R2 列表 biz 不可得，或正文阶段触发熔断——均有现场保留，可按 [03-operations.md](03-operations.md) 的「故障处置与断点续跑」直接重跑） |

每日增量与每周全量的计划任务配置（Windows 任务计划程序 pwsh7 脚本、NAS cron）见 [deploy/README.md 第 12 节](../deploy/README.md)。

## `list`（列表同步）

自动发现采集服务的搜索/历史端点（可由环境变量覆写），翻页采集元数据并幂等入库；完整翻到尾页后执行下架/不可见文章对账，凭证失效时返回退出码 2 并提示重新扫码。

## `fetch`（正文归档）

直连 `mp.weixin.qq.com` 逐篇下载：正文图片（含微信懒加载 `data-src`）全部本地化并改写为相对路径，单图失败保留远程引用并登记进 `metadata.json`；平台明确删除/违规的文章标记 skipped；单篇错误（如单篇 404）标记 failed 并隔离继续。归档产物位于 `archive/<账号>/<YYYY>/<YYYY-MM-DD_标题>/`。

## `export-rag`（RAG 语料导出）

纯派生离线命令（不触网、幂等，临时文件 + 原子覆盖），仅导出 `downloaded` 文章：从本地化 `article.html` 的 `#js_content` 提取段落结构完整的纯文本（块级换行、列表转 `- `、代码块保留缩进、语音转「［音频：标题］」、视频转「［视频：标题］」、音乐转「［音乐：标题］」（无标题时不带冒号）、图片节点移除），默认保守清洗微信排版噪声（文末关注/在看/扫码引导短行、纯装饰行、相邻重复行、文章后半部平台推荐块）。

每行一个 JSON、UTF-8、`ensure_ascii=False`，字段：

| 字段 | 说明 |
|---|---|
| `id` | articles 表行 id |
| `account` | 账号别名（`account_alias`） |
| `title` / `author` / `publish_time` / `url` | 文章元数据（取自 DB） |
| `original` | 是否原创（布尔） |
| `album` / `digest` | 所属合集与摘要 |
| `text` | 清洗后纯文本；加 `--with-raw` 时另附 `text_raw`（清洗前原文，供逐行对照评阅） |

选项：`-a/--account`（默认全部账号）、`-o/--out`（默认 `exports/rag.jsonl`，可用 `MP_ARCHIVER_EXPORT_ROOT` 改根目录）、`--no-clean`（关清洗）、`--with-raw`（附原文对照）、`--limit`（调试限量）。DB 标记 downloaded 但 HTML 缺失/路径越界的单篇计入失败、不阻断其余导出，存在失败时退出码为 1。

## `report`（分析报表）

纯派生离线命令（不触网、幂等，HTML/CSV 均临时文件 + 原子覆盖），产出到 `exports/report/`：

- `report.html` 为单文件报表（内联 CSS，无 JS/外链/CDN，断网可开），含五项统计——①发文量时间序列（年/月）、②星期×时段（0–23 时）发布热力、③原创占比、④合集 Top N、⑤含音频/视频文章占比；
- `report.csv` 为逐篇明细（UTF-8 BOM，Excel 直接打开），含发布时间 UTC 原文与北京时间派生列（年/年月/星期/小时），可自行透视复核。

统计口径在报表页首明确声明：前四项基于**有发布时间的全部文章**（未归档也参与），音视频占比基于**已归档（downloaded）文章**（富媒体仅在正文归档时识别）；所有时间按**北京时间（UTC+8）**聚合（SQL 侧 `strftime(..., '+8 hours')`）。报表页脚附每项数字对应的对账 SQL（`:biz` 为占位参数），可直接在 SQLite 上核对。

选项：`-a/--account`（默认全部账号）、`-o/--out`（输出目录，默认 `exports/report/`）、`--top`（合集 Top N，默认 10）。空库/单篇/无合集等边界渲染空态而非报错；退出码 `0` 成功、`3` 账号未找到。

## 相关文档

- [文档索引](README.md)
- [限速与故障处置](03-operations.md)
- [存储布局与源码结构](04-storage-and-layout.md)