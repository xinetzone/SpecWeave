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
pytest                 # 运行测试
```

`sync` 与 `run` 是统一编排命令，一次完成「列表 → 正文/富媒体 →（可选）互动」：增量模式从最新页向后翻，遇到整页全已知即停，只下载 pending 新文章；全量模式翻到历史尾页并执行下架对账（未显式加 `--full` 不会执行，防止误触发长任务）。两者均幂等可中断：进程随时终止后重跑，已归档文章按状态自动跳过、失败文章随后续任务补齐，不产生重复文件。退出码：`0` 成功；`1` 存在失败文章或参数错误；`2` 登录态失效需重新扫码；`3` 账号未找到；`4` 采集服务不可达/环境异常。每日增量与每周全量的计划任务配置（Windows 任务计划程序 pwsh7 脚本、NAS cron）见 [deploy/README.md 第 12 节](deploy/README.md)。

`list` 会自动发现采集服务的搜索/历史端点（可由环境变量覆写），翻页采集元数据并幂等入库；完整翻到尾页后执行下架/不可见文章对账，凭证失效时返回退出码 2 并提示重新扫码。

`fetch` 直连 `mp.weixin.qq.com` 逐篇下载：正文图片（含微信懒加载 `data-src`）全部本地化并改写为相对路径，单图失败保留远程引用并登记进 `metadata.json`；平台明确删除/违规的文章标记 skipped，风控页与传输错误标记 failed 且不影响后续文章。归档产物位于 `archive/<账号>/<YYYY>/<YYYY-MM-DD_标题>/`。

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
└── exporters/         # 派生产物导出（RAG JSONL：rag.py 编排 + core/text_extract.py 提取与清洗）
```
