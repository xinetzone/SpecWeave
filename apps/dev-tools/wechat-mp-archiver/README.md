# wechat-mp-archiver

微信公众号全量内容归档工具：通过**私有部署的开源采集服务**（R2 主路线）获取指定公众号的历史文章列表，由本 Python 管线完成正文/富媒体下载、元数据管理、断点续采与增量更新，产出三种形态：

- **离线归档**：原始 HTML 快照 + 本地化图片 + Markdown，按 `archive/<账号>/<年>/<日期_标题>/` 组织；
- **RAG 语料**：带 YAML frontmatter 的 Markdown 导出（Task 10）；
- **分析报表**：更新趋势、失败/对账清单（Task 11）。

技术选型与合规边界见 [技术方案文档](../../../docs/knowledge/operations/wechat-mp-full-archive-solution.md)。
仅供个人学习研究使用，请勿公开再分发归档内容。

## 安装

```bash
cd apps/dev-tools/wechat-mp-archiver
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## 采集服务部署（首次使用必做）

采集服务通过 Docker Compose 私有部署（仅绑定回环地址），扫码登录由账号管理员本人完成，步骤与登录态失效续期见 [deploy/README.md](deploy/README.md)。

## 配置

```bash
copy .env.example .env   # PowerShell；bash: cp .env.example .env
```

`.env` 中至少确认：归档根目录、数据库路径、限速参数；采集服务地址（默认 `http://127.0.0.1:5000`）在采集服务私有部署并扫码后生效。**凭证只走环境变量/.env，`.env` 已被 gitignore。**

## 命令

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
mp-archiver export-rag                    # 离线导出 RAG JSONL 语料（全部账号 → exports/rag.jsonl）
mp-archiver export-rag -a 意识食谱 --no-clean --with-raw  # 单账号/不清洗/附清洗前原文对照
mp-archiver report                    # 离线生成分析报表（全部账号 → exports/report/）
mp-archiver report -a 意识食谱 --top 20   # 单账号 + 合集 Top 20
pytest                 # 运行测试
```

`sync` 与 `run` 是统一编排命令，一次完成「列表 → 正文/富媒体 →（可选）互动」：增量模式从最新页向后翻，遇到整页全已知即停，只下载 pending 新文章；全量模式翻到历史尾页并执行下架对账（未显式加 `--full` 不会执行，防止误触发长任务）。两者均幂等可中断：进程随时终止后重跑，已归档文章按状态自动跳过、失败文章随后续任务补齐，不产生重复文件。退出码：`0` 成功；`1` 存在失败文章或参数错误；`2` 登录态失效需重新扫码；`3` 账号未找到；`4` 环境/风控异常（采集服务不可达、端点发现失败，或正文阶段触发熔断——均有现场保留，可按下方「故障处置与断点续跑」直接重跑）。每日增量与每周全量的计划任务配置（Windows 任务计划程序 pwsh7 脚本、NAS cron）见 [deploy/README.md 第 12 节](deploy/README.md)。

`list` 会自动发现采集服务的搜索/历史端点（可由环境变量覆写），翻页采集元数据并幂等入库；完整翻到尾页后执行下架/不可见文章对账，凭证失效时返回退出码 2 并提示重新扫码。

`fetch` 直连 `mp.weixin.qq.com` 逐篇下载：正文图片（含微信懒加载 `data-src`）全部本地化并改写为相对路径，单图失败保留远程引用并登记进 `metadata.json`；平台明确删除/违规的文章标记 skipped；单篇错误（如单篇 404）标记 failed 并隔离继续。归档产物位于 `archive/<账号>/<YYYY>/<YYYY-MM-DD_标题>/`。

### 故障处置与断点续跑（韧性设计）

归档按故障作用域分流，目标是**退避不猛打、失败可隔离、现场可续跑**：

| 故障 | 行为 | 处置 |
|---|---|---|
| 文章页 403/429（账号或 IP 级风控） | 请求级指数退避（`2/4/8/…` 秒 + 抖动，封顶 60 秒，退避日志可见且只记主机名不记链接参数）用尽后，当前篇置 failed（原因 `risk_abort:` 可查），**立即熔断**：本批后续文章保持 pending、零请求 | 退出码 4；加大限速/更换网络/稍后直接重跑续采 pending，加 `--include-failed` 重试本篇 |
| 验证码/环境异常页（含无正文容器的未知拦截页变体） | 显式判为风控（基于页面结构：正文容器 `#js_content` 缺失或为空，不会误杀正文恰好包含这些词的正常文章），当前篇 failed 并立即熔断，不产生空壳归档 | 同上；确认为正常文章被误判时可用 `--include-failed` 复核重试 |
| 超时/连接错误、文章页 5xx | 单篇先退避重试；重试用尽后置 failed 隔离；**连续 2 篇**（可用 `MP_ARCHIVER_TRANSPORT_ABORT_THRESHOLD` 调整）传输/服务故障才熔断，成功篇或业务失败篇会重置连续计数，偶发抖动不熔断 | 退出码 4；网络/服务恢复后重跑 |
| 单篇 404 / 解析异常 | 不重试，置 failed 并输出失败清单，批次继续，末尾给成功/跳过/失败分类计数 | 退出码 1；按需 `--include-failed` |
| 图片/语音等媒体链接失效 | 单资源失败登记 media 表与 `metadata.json` 例外表（保留远程引用），文章仍正常 downloaded | 退出码 0（有告警）；重跑可补齐 |
| 采集服务凭证过期（401/403） | 不落任何归档重试，凭证状态写库 `expired` 并立即终止 | 退出码 2；重新扫码后续跑 |

熔断与中断（含 kill -9）都不破坏幂等：每篇成功/失败即时落库，半成目录重跑时整体清空重建；普通重跑只采 pending，`--include-failed` 才重试失败篇，不产生重复文件。

`export-rag` 是纯派生离线命令（不触网、幂等，临时文件 + 原子覆盖），仅导出 `downloaded` 文章：从本地化 `article.html` 的 `#js_content` 提取段落结构完整的纯文本（块级换行、列表转 `- `、代码块保留缩进、语音/视频转「［音频：标题］」占位、图片节点移除），默认保守清洗微信排版噪声（文末关注/在看/扫码引导短行、纯装饰行、相邻重复行、文章后半部平台推荐块）。每行一个 JSON、UTF-8、`ensure_ascii=False`，字段：

| 字段 | 说明 |
|---|---|
| `id` | articles 表行 id |
| `account` | 账号别名（`account_alias`） |
| `title` / `author` / `publish_time` / `url` | 文章元数据（取自 DB） |
| `original` | 是否原创（布尔） |
| `album` / `digest` | 所属合集与摘要 |
| `text` | 清洗后纯文本；加 `--with-raw` 时另附 `text_raw`（清洗前原文，供逐行对照评阅） |

选项：`-a/--account`（默认全部账号）、`-o/--out`（默认 `exports/rag.jsonl`，可用 `MP_ARCHIVER_EXPORT_ROOT` 改根目录）、`--no-clean`（关清洗）、`--with-raw`（附原文对照）、`--limit`（调试限量）。DB 标记 downloaded 但 HTML 缺失/路径越界的单篇计入失败、不阻断其余导出，存在失败时退出码为 1。

`report` 是纯派生离线命令（不触网、幂等，HTML/CSV 均临时文件 + 原子覆盖），产出到 `exports/report/`：`report.html` 为单文件报表（内联 CSS，无 JS/外链/CDN，断网可开），含五项统计——①发文量时间序列（年/月）、②星期×时段（0–23 时）发布热力、③原创占比、④合集 Top N、⑤含音频/视频文章占比；`report.csv` 为逐篇明细（UTF-8 BOM，Excel 直接打开），含发布时间 UTC 原文与北京时间派生列（年/年月/星期/小时），可自行透视复核。统计口径在报表页首明确声明：前四项基于**有发布时间的全部文章**（未归档也参与），音视频占比基于**已归档（downloaded）文章**（富媒体仅在正文归档时识别）；所有时间按**北京时间（UTC+8）**聚合（SQL 侧 `strftime(..., '+8 hours')`）。报表页脚附每项数字对应的对账 SQL（`:biz` 为占位参数），可直接在 SQLite 上核对。选项：`-a/--account`（默认全部账号）、`-o/--out`（输出目录，默认 `exports/report/`）、`--top`（合集 Top N，默认 10）。空库/单篇/无合集等边界渲染空态而非报错；退出码 `0` 成功、`3` 账号未找到。

## 结构

```
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
