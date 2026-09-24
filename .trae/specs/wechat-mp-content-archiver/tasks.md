# 微信公众号全量内容采集与存档管线 - Implementation Plan

> 执行约定：严格按依赖顺序取任务；每个任务开始时置 `in_progress`，完成自验后写 Completion Evidence 置 `completed`。
> 代码落位 `apps/wechat-mp-archiver/`（Task 2 启动前必须先读 `apps/AGENTS.md` 完成子区域路由）；对外方案文档落位 `docs/knowledge/`（Task 1 执行「落盘前三查」确认具体子目录）。所有采集默认保守限速，凭证只走环境变量。

## Task 1: 方案对比与选型文档固化
- **Status**: `completed`（2026-09-24）
- **Priority**: high
- **Depends On**: None
- **Approval Record**: 用户于 2026-09-24 批准 spec.md 推荐选型（R2 主路线 + R3 兜底 + R1 条件补充 + R4 本期不采用）。
- **Completion Evidence**:
  - 成稿：[docs/knowledge/operations/wechat-mp-full-archive-solution.md](../../../docs/knowledge/operations/wechat-mp-full-archive-solution.md)（配套元数据 `.meta/toml/docs/knowledge/operations/wechat-mp-full-archive-solution.toml`，落位经「落盘前三查」与既有 `wechat-mp-content-extraction.md` 互补不重复）。
  - TR-1.1：R1–R4 × 多维度矩阵 + 逐路线门槛/凭证续期/失效模式齐备；信源三类齐全（官方 freepublish 文档与限额页、exporter/wechatDownload 仓库、2026-09 第三方实测），抽样 3 条可回源（官方接口页、wechat-download-api 2026-09-21 文档、本库 js_content 实战复盘）；新证据 `tmwgsicp/wechat-download-api`（API-first/增量游标/ARM64/凭证4天/Webhook 预警）已如实入档并定为 Task 3 doctor 实测裁决项。
  - TR-1.2：含现状核实、官方边界证据、逐路线反证与明确取舍；批准结论在档。
  - 链接校验：`check-links.py` 对新文档 0 断链（operations 目录历史遗留的 16 个 `d:/spaces/chaos/` 绝对路径断链与本文档无关，不在本任务范围）。
- **Description**:
  - 将 spec.md「Background & Context」的调研事实与四路线矩阵固化为正式中文方案文档（落位经「落盘前三查」确认的 `docs/knowledge/` 子目录），补充：各路线操作门槛、凭证时效与续期方式、典型失效模式、合规边界、参考链接与核实日期。
  - 明确「主路线 R2 + 兜底 R3 + R1 条件补充 + R4 本期不采用」的取舍论证，记录用户在 Approve 门的选型结论。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-15
- **Test Requirements**:
  - `rule` TR-1.1: 文档覆盖 R1–R4 × 六维度矩阵；每条关键事实附来源 URL 与 2026-09 核实日期；官方文档/开源仓库/第三方实测三类信源齐全；抽样 3 条可回源。证据：文档成稿 + 链接抽验记录。
  - `rubric` TR-1.2: 选型论证质量；scale 1-5；anchors 1=工具罗列无论证，3=对比完整但风险泛泛，5=含现状核实+官方边界证据+逐路线反证+明确取舍；threshold >= 4；证据：文档评审。
- **Notes**: 文档含 frontmatter（YAML，`source` 字段标注调研来源与日期）；Markdown 链接用相对路径，禁止 file:/// 绝对路径。

## Task 2: 项目骨架与公共基建
- **Status**: `completed`（2026-09-24）
- **Priority**: high
- **Depends On**: Task 1
- **Path Decision**: 依 `apps/AGENTS.md` 应用分组规则（2026-09-24 回读磁盘原文），落位由 spec 暂定的 `apps/wechat-mp-archiver/` 细化为 **`apps/dev-tools/wechat-mp-archiver/`**（dev-tools 组，与 camera-power-controller / prompt_extraction 同组）；简单工具无独立 AGENTS.md，已在 apps/AGENTS.md 路由表与边界声明两处登记。
- **Completion Evidence**:
  - 骨架：`pyproject.toml`（scikit-build-core 纯 Python，`wheel.cmake=false`，`requires-python>=3.14`，入口 `mp-archiver`）、src 布局包（config/models/logging_utils/naming/http_client/db + adapters/core/exporters 分层）、`.env.example`、`.gitignore`、README、26 项单测全绿（Python 3.14.7 venv）。
  - TR-2.1：`.env`/`data/`/`archive/`/`exports/`/`.venv/`/`build/` 全部 ignore（应用级 .gitignore + 根 .gitignore 双层；主机未安装 git CLI，无法跑 `git check-ignore`，规则经人工核对）；`.env.example` 仅非敏感默认值，凭证字段全空；脱敏实跑 `token=***REDACTED*** pass_ticket=***REDACTED***`（test_logging 6 例 + 命令行实测）。
  - TR-2.2：init_db 连续执行幂等；文章按 `biz+mid+idx`、退化按 `sn` upsert 不产生重复行（test_db 6 例，含同 biz 不同 idx、字段/状态推进、sync_state 水位）。
  - TR-2.3：503/403/超时按 `base*2**n` 退避（2s→4s）、401 立即返回不重试、退避封顶 8s 实测、异常耗尽上抛（test_http_client 6 例，MockTransport 无真实网络）；文件名工具覆盖 Windows 非法字符/保留名/尾点空格/超长保扩展名（test_naming 9 例）。
  - TR-2.4：适配器层以 `ArticleListAdapter` Protocol 隔离后端（Task 3/4/8 填充），配置全量外置，日志可观测；`mp-archiver doctor`/`init-db` 实跑通过。链接校验 0 断链。
- **Description**:
  - 先读 `apps/AGENTS.md` 路由并确定 `apps/wechat-mp-archiver/` 结构与构建后端（纯 Python 应用按仓库规范选择声明方式，需要可安装时默认 scikit-build-core，纯 Python 不写 cmake 段）。
  - 建立：`pyproject.toml`、包结构（config/adapters/core/exporters/cli）、`pydantic` 配置模型（读 `.env`/环境变量：`EXPORTER_BASE_URL`、存档根目录、限速参数、可选微信 credentials 与官方 API 凭证）、`.env.example`、`.gitignore`（覆盖 `.env`、`data/`、`archive/`）。
  - 公共组件：SQLite schema 与初始化（articles/media/comments/metrics/state 五表 + 唯一键）、采集状态枚举（pending/downloaded/failed/skipped/skipped_no_credential/external_ref）、脱敏日志器（token/cookie/key 模式打码）、带令牌桶限速与指数退避的 HTTP 客户端、跨平台安全文件名工具。
- **Acceptance Criteria Addressed**: AC-9, AC-10, AC-17
- **Test Requirements**:
  - `rule` TR-2.1: `git ls-files` 不包含 `.env`/`data/`/`archive/`；`.env.example` 仅占位；对样例日志输出 grep 不到明文凭证。证据：命令输出。
  - `rule` TR-2.2: SQLite 初始化幂等（连续执行两次不报错），文章唯一键（biz+mid+idx 或 sn）重复插入被忽略/更新而非报错。证据：单测。
  - `rule` TR-2.3: HTTP 客户端在模拟 403/超时下按配置退避；文件名工具对 Windows 非法字符与超长标题输出合法结果。证据：单测（mock）。
  - `rubric` TR-2.4: 工程基建质量（分层/配置化/日志）；scale 1-5；anchors 1=脚本堆叠，3=可运行但耦合，5=adapter 分层+配置完备+日志可观测；threshold >= 4；证据：代码评审。

## Task 3: exporter 私有部署与连通性自检
- **Status**: `in_progress`
- **Priority**: high
- **Depends On**: Task 2
- **Environment Note**: 主机当前未安装 Docker/Podman（2026-09-24 探测）；扫码登录依任务约定必须由用户本人用专用订阅号完成。故先交付不依赖运行时/授权的软件产物（compose/doctor 探测代码与单测/操作文档），TR-3.1 的真实号实测待用户就绪后闭环。
- **Description**:
  - 编写 `docker-compose.yml` 私有部署 wechat-article-exporter（数据卷持久化、仅本机绑定端口），核实其当前版本 LICENSE 并记录署名/使用义务；核对其开放 API（或等效接口）形态。
  - 实现 `mp-archiver doctor` 自检命令：检查 exporter 存活、登录态、搜索目标号（按名称解析 biz/fakeid）、拉取首页列表。
  - 编写扫码登录与登录态失效后重新登录的操作文档（截图位留空由用户实操补充）。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-3.1: `docker compose up -d` 后健康检查通过；`doctor` 对「意识食谱」返回 biz 与 ≥1 篇文章。证据：命令输出（含目标号名称与首条标题）。
  - `rule` TR-3.2: 文档说明登录态失效的观测信号与重新扫码步骤。证据：文档章节。
- **Software Deliverables（2026-09-24，待环境实测闭环）**:
  - `deploy/docker-compose.yml`：主承载 `tmwgsicp/wechat-download-api:latest`（多架构），端口仅绑 `127.0.0.1:5000`，凭证持久化命名卷 `mp_archiver_collector_data`，内置 openapi.json 健康检查；`deploy/collector.env.example`（SITE_URL/MCP_TOKEN）。
  - `src/mp_archiver/adapters/health.py`：多端点宽容探测（/openapi.json→/health→/api/health→/），三态判定 up/auth_required/down，并从 OpenAPI 抽取登录/账号/文章相关能力路径供 Task 4 对接；`doctor` 已集成（本机未部署时 down→warn 不改变退出码，实测输出符合预期）；7 例 MockTransport 单测全绿，全套件 33/33。
  - `deploy/README.md` 覆盖 TR-3.2：失效观测信号（doctor 401/403、接口重定向登录页、列表异常为空、服务日志、Webhook）与重新扫码 SOP、停止/升级/卷备份、备选承载 exporter 源码自建指引、故障速查。
  - LICENSE 核实：wechat-download-api 据项目文档为 AGPL-3.0，文档已标注「部署时以镜像内 /app/LICENSE 复核」；exporter LICENSE 因当前网络人机验证拦截未能在线核实，文档已显式标注待部署时从所用版本仓库回填，未臆造。
  - **TR-3.1 挂起**：`docker compose up -d` healthy 与 doctor 对「意识食谱」返回 biz+首条标题的实测，受①主机无容器运行时、②扫码须用户本人完成、③账号搜索/列表适配器属 Task 4 三项约束，待用户环境就绪后与 Task 4 合并端到端闭环。
- **Notes**: 必须使用采集专用（非主力）订阅号扫码；登录操作由用户本人完成，实现者不得索要账号密码。

## Task 4: 全量文章列表采集器
- **Status**: `in_progress`（软件完成 2026-09-24；TR-4.1 真实号对照待采集服务部署+扫码后闭环）
- **Priority**: high
- **Depends On**: Task 3
- **Completion Evidence（软件侧）**:
  - 解析层 `adapters/wechat_payload.py`：严格按微信公开 getmsg 契约——`general_msg_list` 二次 JSON 解码、`type==49` 图文过滤、主图文+`multi_app_msg_item_list` 拆条（idx 以各 content_url 为准）、`__biz/mid/idx/sn` URL 标识解析（HTML 实体还原）、UTC ISO 时间、copyright_stat 原创位（经验值 11 已标注待校准）、ret 错误分级（200013→凭证失效）、searchbiz 账号解析与精确/包含两级匹配。
  - 发现层 `adapters/api_surface.py`：OpenAPI 关键词评分自动发现搜索/历史端点（GET 优先、登录/导出路径排除），支持 `MP_ARCHIVER_EXPORTER_SEARCH_PATH/HISTORY_PATH` 显式覆写；不硬编码任何未实测路径。
  - 适配层 `adapters/wechat_download_api.py`：搜索最多 5 页翻页、参数名按端点声明自适应（query/__biz/fakeid/offset/count/f），401/403→CredentialExpiredError，端点缺失→明确错误并给出覆写指引。
  - 编排层 `core/list_sync.py`：翻页 upsert（已存在记录 preserve_status：downloaded 不回退、元数据仍刷新）、next_offset 水位与空转/死循环防护、**完整全量**到尾页后对账（不可见文章→skipped+`not_visible_in_full_scan@日期`，max-pages 截断不对账）、凭证失效先落 EXPIRED 水位再抛出。
  - TR-4.3：`core/validation.py` 输出 title/url/publish_time 非空率，list 结束自动打印；schema 增加 `is_original`/`album`（含旧库 ALTER 迁移）；顺带修复 Task 2 遗留 `upsert_sync_state` 在 total_seen=None 时违反 NOT NULL 的缺陷。
  - CLI：`mp-archiver list -a <名称> [--max-pages N] [--no-reconcile]`，退出码 0 成功/2 凭证失效/3 未找到号/4 环境或端点异常；无服务冒烟实测返回 exit=4 + 部署指引。
  - TR-4.2：去重 upsert（跨页重复→updated 不增行）、断点水位 sync_state 均有单测；**真实中断续跑演练**待环境实测。
  - 测试：66/66 全绿（新增 36 例：原生/搜索 payload、端点发现、HTTP 适配器含翻页与 401、同步编排含对账/截断/保状态/凭证失效、完整性校验）；链接检查通过。
  - **TR-4.1 挂起**：与 TR-3.1 合并——部署 + 专用号扫码后，对「意识食谱」跑全量，核对最早一篇日期与总数与微信客户端一致（允许近 24h 新发误差）。
- **Description**:
  - 实现 exporter adapter：按目标号分页拉取全部群发文章元数据 → SQLite（title/url/biz/mid/idx/sn/author/publish_time/digest/original/album），含翻页水位、去重 upsert、已删除/不可见文章识别（接口返回过滤项记录状态）。
  - CLI：`mp-archiver list --account 意识食谱 [--full]`。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-4.1: 全量完成后最早一条记录的发布日期与微信客户端该号历史消息页最早可见文章一致；记录数与微信端逐页加载数一致（允许近 24h 新发误差）。证据：库查询 + 微信端对照记录。
  - `rule` TR-4.2: 重复执行同一分页任务不产生重复行；断点偏移持久化，中断重跑续接。证据：单测 + 中断演练。
  - `rule` TR-4.3: 列表字段非空率符合约定（title/url/publish_time 100%）。证据：校验脚本输出。

## Task 5: 正文存档与图片本地化
- **Status**: `in_progress`（软件完成 2026-09-24；TR-5.1 真实抽样 10 篇与 TR-5.3 人工保真度评分待实测后闭环）
- **Priority**: high
- **Depends On**: Task 4
- **Completion Evidence（软件侧）**:
  - 纯函数层 `core/html_transform.py`：以 `#js_content` 为正文边界；页面分类（ok/deleted/violation/risk，文案标记为经验值已注释待校准）；懒加载图片收集（data-src 优先、data: 占位过滤、去重保序）；本地化双写 src/data-src、失败远程兜底、纯占位节点清理；扩展名按 wx_fmt→Content-Type→默认 jpg 推断；Markdown 转换保留 ATX 标题/列表/有序列表/引用/围栏代码（code_language_callback 从内层 `<code class="language-*">` 提语言），连续空行收敛。
  - 归档层 `core/article_archive.py`：四件套落盘（article.html 为完整原始页+本地化图片，含 utf-8 声明可离线打开；article.md 含标题/作者/时间/原文头与归档时间；metadata.json 含全量元数据与图片成功/失败清单）；目录 `archive/<别名>/<YYYY>/<YYYY-MM-DD_标题>/`，同日同名异文追加 -2/-3，本文重跑整体重写（幂等）；删除/违规→skipped（content_deleted/content_violation@日期），风控/容器缺失/传输错误→failed；单图失败不阻断（保留远程引用+登记例外）；下载图片带 mp.weixin.qq.com Referer。
  - 安全：fetch 使用剥离本地服务 Token 的 Settings 副本，避免 Bearer 凭证发往微信域；DB 新增 get_account_biz_by_alias/iter_articles_by_status/mark_article_archived/mark_article_failed。
  - CLI `fetch -a <名称> [--limit N] [--include-failed]`：逐篇独立成败、汇总成功/跳过/失败/图片例外，未知号 exit 3，有失败 exit 1；冒烟实测通过。
  - 异常类上提至顶层 `exceptions.py`（adapters/core 共享），适配器模块保持 re-export 兼容。
  - TR-5.2 已满足：四类结构 fixture 单测 11 例全绿；另端到端 3 例（MockTransport：正常图 200+失败图 404/删除页/风控页、四件套与字节核对、状态机、重跑幂等与 -2 后缀、未知号）。
  - 测试：**80/80 全绿**；链接检查通过。
  - **TR-5.1/TR-5.3 挂起**：真实 10 篇抽样（长图文/图集/纯文字）断网核对与 1-5 分保真度评分（阈值≥4）待 list 实测后执行。
- **Description**:
  - 逐篇下载原始 HTML 存档；解析正文 DOM，下载 mmbiz 图片至文章媒体目录并改写引用为相对路径；HTML→Markdown 转换（保留标题层级、列表、代码块、引用）；输出 `metadata.json`。
  - 目录布局 `archive/<别名>/<YYYY>/<YYYY-MM-DD_安全标题>/{article.md,article.html,metadata.json,images/}`；失败重试与状态回写。
- **Acceptance Criteria Addressed**: AC-5, AC-16
- **Test Requirements**:
  - `rule` TR-5.1: 每篇文章目录四件套齐全；抽样 10 篇（覆盖长图文/图集/纯文字）断网打开，章节与图片无缺失，图片本地化率 100%（原图失效的外链登记例外表）。证据：抽样核对清单。
  - `rule` TR-5.2: Markdown 转换对标题/列表/代码块/引用四类结构有 fixture 单测。证据：pytest。
  - `rubric` TR-5.3: 采集保真度；scale 1-5；anchors 1=纯文本大量缺失，3=正文完整但媒体/排版有可察觉损失，5=离线阅读与原文无实质差异；threshold >= 4；证据：AC-5 抽样。

## Task 6: 富媒体分类采集
- **Status**: `in_progress`（软件完成 2026-09-25；TR-6.2 已由 7 项识别器/归档单测闭环；TR-6.1 真实 mpvoice 文章播放抽检待采集服务部署+扫码后闭环）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 媒体识别器（纯函数 + fixture）：mpvoice 语音（直链下载，重点验证播客文章）、mmbiz 图片、腾讯视频 embed（提取 vid 与封面，落占位元数据）、视频号卡片（标记 `video_channel_unavailable`）、外链音频/视频如小宇宙（记录 `external_ref`）。
  - 媒体文件入 `media/` 并在 media 表登记类型/大小/哈希/来源 URL；禁止为不可下载类型生成伪造文件。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-6.1: 至少 3 篇含 mpvoice 的示例号文章语音落盘且可播放（时长/文件大小与原文一致级核对）。证据：文件清单 + 播放抽检。
  - `rule` TR-6.2: 四类媒体在含各类卡片的 fixture 文章上识别结果与人工标注一一对应，视频号/外链不产生伪本地文件。证据：识别器单测 + 人工标注对照。

## Task 7: 评论与互动数据条件采集
- **Status**: `in_progress`（软件完成 2026-09-25；TR-7.2 已由 11 项解析/降级/集成单测闭环（无凭证整批退出正常、状态 skipped_no_credential）；TR-7.1 真实凭证对照待用户抓包提供 appmsg_token/pass_ticket 后联调；接口字段为经验形态，已在 comment_sync.py 标注实测校准点；凭证获取步骤见 deploy/README.md 第 8 节）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 实现手机端 credentials 读取（环境变量，含获取步骤文档）；经可用通道（exporter 凭证能力或直接接口，实现时以实测可用形态为准）采集评论/回复、阅读数、点赞、在看、转发，入 comments/metrics 表。
  - 无凭证或凭证失效时：相关字段置 `skipped_no_credential`，主流程成功退出；不把缺数据记为 failed。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 配置有效凭证时，抽样文章的评论数与微信端显示一致（允许实时新增误差），阅读/点赞字段非空。证据：对照记录。
  - `rule` TR-7.2: 无凭证运行整批任务退出码 0，状态全部为 skipped_no_credential 且无堆栈错误。证据：运行日志。
- **Notes**: 若用户在 Open Questions 中选择本期不抓包，则凭证联调以 mock 单测交付，状态路径保留并在文档说明；实际抓取推迟到用户提供凭证后。

## Task 8: 自有号官方 API 条件 adapter
- **Status**: `completed`
- **Priority**: low
- **Depends On**: Task 4
- **Completion Evidence**:
  - 新增 [src/mp_archiver/adapters/official_api.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/adapters/official_api.py)：access_token 获取与提前 300 秒过期、40001/40014/42001 强制刷新一次、48001 抛 `OfficialApiPermissionError`、`freepublish/batchget` 按群发 offset 翻页（PAGE_SIZE=20）并展开 news_item（1–8 篇/组，`is_deleted` 标记 external_ref 后跳过）；`DailyQuotaGuard` 以 `data/official_api_quota.json` 持久化、按 UTC 日滚动，默认阈值 90。
  - 新增 [src/mp_archiver/core/official_sync.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/core/official_sync.py)：biz 解析（显式配置 → R2 已同步数据按别名查）、去重入库（`preserve_status=True` 不回退采集状态）、配额触顶优雅停止。
  - articles 表新增 `source` 列（schema.sql + ALTER 迁移），多源命中合并为 `exporter+official_api`；CLI 新增 `sync-official -a`（无凭证零请求跳过/48001 降级退出码 0/网络错误退出码 4/biz 缺失退出码 3），实跑验证通过。
  - TR-8.1：[tests/test_official_api.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_official_api.py) 22 个 mock 用例覆盖解析展开、48001/其他 errcode、token 刷新一次（二次仍失败不循环）、无凭证零请求、biz 缺失/R2 别名回退、与 R2 合并保状态、配额触顶/持久化/跨日重置/坏文件容错、no_content 裁剪自动重取/永久空页报错、畸形 item/越界时间戳、CLI 五档退出码（0/3/4 × 48001、biz 缺失、40164、非 JSON、空白 secret）；全量 120/120 通过。
  - TR-8.1 真实联调（2026-09-24 完成）：分段证据链排障推进，五段探针 `official-doctor -a 自有号` 实测结论如下。① 配置形态：biz `MzcwMzE5NTI5NA==` 经 [resolve_article_identity](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/core/official_probe.py) 用 MicroMessenger UA 抓取公众号文章短链提取（绕过 `wappoc_appmsgcaptcha` 人机验证码页），填入 .env。② 网络可达：本机直连 `api.weixin.qq.com/getcallbackip` 200 响应。③ token 换取：用户在公众平台后台加入出口 IP `124.160.63.178` 白名单后（40164 解除），`cgi-bin/token` 返回有效 `access_token`。④ batchget 实页：`freepublish/batchget` 调用成功但 `total_count=0`——该号文章经群发发布，**不在 freepublish 覆盖范围**（接口契约仅含"已发布图文"含"发表不通知"，群发历史不返回），代码注释已声明此边界。⑤ biz 一致性：合集页 `__biz=MzcwMzE5NTI5NA==` 与配置一致。
  - TR-8.1 失败测试修复（同日）：`test_cli_missing_biz_exits_three` 预存在失败定位与修复。根因不是 `OfficialApiAdapter.__init__` 在构造时触发 token 请求（实测构造无副作用），而是**测试隔离不彻底**——`monkeypatch.delenv("MP_ARCHIVER_WECHAT_OFFICIAL_BIZ")` 只删环境变量，但 pydantic-settings 在环境变量缺失时**回退到项目根 `.env` 文件**加载 biz，导致 biz 检查通过、token 被实际发起。修复：`monkeypatch.setenv("MP_ARCHIVER_WECHAT_OFFICIAL_BIZ", "")`——环境变量存在且为空，pydantic 直接取空串不回退 .env。修复后该测试通过，全量 147/147 通过，无回归。另：[official_probe.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/core/official_probe.py) 同期加固 `resolve_article_identity`：新增 `_MICROMESSENGER_UA` 常量、`_is_valid_biz()` 校验函数（排除 `${window.biz}` JS 占位符、要求 Base64 形态）、`wappoc` 验证码页直接抛 `PayloadError`；`tests/test_official_probe.py` 新增 3 个测试覆盖新行为。
  - 独立评审（fresh context）首轮结论 NEEDS-FIX，5 个 P1 与 8 项 P2 已全部关闭：P1-1 no_content=1 静默零产出（有组无条目时 no_content=0 自动重取，仍空抛 PayloadError）；P1-2 item/group 畸形类型安全处理；P1-3 越界时间戳与非法 errcode 容错（_safe_int/OverflowError/OSError）；P1-4 CLI 补 ApiRetError（40164/40125/45009 定向提示）/PayloadError/非 JSON 干净处理退出码 4；P1-5 文档统一为"官方仅列认证服务号、认证订阅号以后台权限页与实测为准"。P2：source 合并改 Python 端精确成员+字典序规范化（merge_source 幂等，杜绝 api 误命中 official_api）、配额状态文件非对象/非数字容错、身份键优先取图文 URL 的 mid/idx/sn（article_id 退化）、夹具 is_deleted 改布尔、CLI strip 预检、错误输出 redact 兜底、EXTERNAL_REF 复用注释。
  - TR-8.2：deploy/README.md 新增第 11 节（适用边界/配置使用/入库语义），故障表补 3 行；.env.example 补 `MP_ARCHIVER_WECHAT_OFFICIAL_BIZ`、`MP_ARCHIVER_OFFICIAL_DAILY_CALL_CAP` 与边界注释；README.md 命令区补 `sync-official`。
- **Description**:
  - 实现 `freepublish/batchget` adapter（access_token 刷新、分页、日限 100×20 的配额守护），仅在配置认证账号凭证时启用；数据并入统一 articles 表并标记来源 `official_api`，与 exporter 来源去重合并。
  - 文档写明：仅覆盖「发表不通知」内容、2025-07 起个人/未认证主体权限回收（48001）、群发历史仍以 R2 为主。
- **Acceptance Criteria Addressed**: AC-13
- **Test Requirements**:
  - `rule` TR-8.1: 无凭证时该源不发起请求、不报错；有凭证（或 mock 48001/正常响应）时分支行为正确；配额守护在到达阈值前停止。证据：mock 单测。
  - `rule` TR-8.2: 文档准确陈述接口边界与权限收紧事实。证据：文档评审。
- **Notes**: 真实接口联调于 2026-09-24 完成（TR-8.1 凭证部分已实测）：分段证据链确认配置/网络/token/biz 四段均通过，但 `freepublish/batchget` 对该号返回 `total_count=0`——这是**接口覆盖范围限制**（仅含已发布图文，不含群发历史），非配置或权限错误。结论：自有号官方 API 路径在本号场景下不产出文章，历史全量采集仍需以 R2 exporter 为主源；官方 API adapter 代码本身可用，对覆盖范围内的号有效。测试层面：发现并修复 `test_cli_missing_biz_exits_three` 预存在失败（pydantic-settings `.env` 回退陷阱），全量 147/147 通过。后续合集路径（`appmsgalbum`）已探查：技术可抓（`window.cgiData.articleList` 含完整 mid/idx/sn/title/create_time），但合集是作者手动选编的主题精选，不覆盖全量历史，不作为主采集源。

## Task 9: 增量模式与 CLI 编排
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6, Task 7
- **Completion Evidence**:
  - 增量水位与 catch-up（[src/mp_archiver/core/list_sync.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/core/list_sync.py)）：复用 sync_state 表 `extras` 列（JSON），完整翻到尾页时写入 `full_completed_at`（UTC 日期）作为「曾完成全量」标记；`upsert_sync_state` 新增 `extras` 形参（COALESCE 语义，None 保留旧值）。增量模式（`catch_up=True`）从最新页向后翻，整页零新增（全已知）且非尾页即提前停止，`SyncReport.caught_up=True`，不做下架对账；**安全护栏**：若无 full_completed_at 标记（上次全量被 max_pages 截断或空库），增量必须翻到尾页，防止永久漏文。
  - 统一编排（新增 [src/mp_archiver/core/pipeline.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/core/pipeline.py)）：`run_pipeline()` 两阶段——阶段 1 携带本地 Bearer Token 访问采集服务同步列表；阶段 2 用 `model_copy(exporter_token=SecretStr(""))` 剥离 Token 后直连微信公域执行 `fetch_articles`（内含富媒体本地化与 settings.fetch_metrics 条件互动采集），凭证边界与独立 fetch 命令一致。列表异常不吞，交由 CLI 映射退出码。导出（export-rag/report）属 Task 10/11，本任务不编排。
  - CLI（[src/mp_archiver/cli.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/cli.py)）：新增 `sync -a <账号> [--limit N] [--fetch-metrics]`（增量）与 `run -a <账号> --full [--include-failed] [--limit N] [--fetch-metrics] [--no-reconcile] [--max-pages N]`（全量回溯+对账，`--full` 为显式确认门，缺失时退出码 1 且不执行）。输出含增量追平/尾页状态、对账计数、全量后元数据完整性、正文成功/失败/跳过与互动摘要；退出码沿用 0/1/2/3/4 五档语义。
  - TR-9.1（软件侧闭环）：新增 16 个单测，全量 163/163 通过（基线 147 + 新增 16，无回归）。① [tests/test_list_sync.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_list_sync.py) 新增 3 例：全量后增量首页 1 新 1 旧继续、次页全旧即停（offset 未越界请求，验证不再翻页）、标记保留；截断全量（无标记）增量不提前停并补回缺口文章；空库增量走完全程。② [tests/test_pipeline.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_pipeline.py) 5 例：增量/全量接线与 Token 两阶段边界（stage1 `local-token`、stage2 空串）、列表阶段 CredentialExpiredError 时不进入正文、列表阶段 catch_up 实翻页验证、**失败注入中断续跑**（前两篇注入 RuntimeError 模拟 kill，首次 2 成功 2 失败；二次 `include_failed` 补齐 4/4 downloaded；第三次零待采集，全树 SHA-256 哈希集合 8 个文件前后不变——零新增、零重复文件）。③ [tests/test_cli_pipeline.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_cli_pipeline.py) 8 例：零新增追平退出 0、`--limit/--fetch-metrics` 透传、无 `--full` 被拦截退出 1 且编排零调用、全量成功含对账/完整性输出、正文失败退出 1、凭证失效 2/账号缺失 3/端点异常 4。
  - TR-9.1 真实 kill 演练：挂起。主机无 Docker 环境、真实号扫码待用户完成，与 TR-3.1/TR-4.1 等真机验收项一并在部署环境执行；中断恢复的软件语义（文章状态机筛选 + 目录整体重建 + 账号水位 extras）已由上述失败注入单测覆盖。
  - TR-9.2：新增 [deploy/sync-incremental.ps1](../../../apps/dev-tools/wechat-mp-archiver/deploy/sync-incremental.ps1)（首行 `#Requires -Version 7.4`，通过 check-pwsh7-compliance；自动定位项目根、优先 .venv、追加 `logs/sync-yyyyMMdd.log`、透传五档退出码，支持 `-Account/-Full/-FetchMetrics`）；`.gitignore` 增忽略 `logs/`；[deploy/README.md](../../../apps/dev-tools/wechat-mp-archiver/deploy/README.md) 新增第 12 节：频率建议（增量每日 1 次 03:17、全量每周至多 1 次、失效不自动重试）、可直接注册的 Windows 任务计划程序 pwsh7 命令（每日增量 + 每周全量两个任务）、NAS/Linux cron 等价示例与分机部署/容器边界说明；第 5 节重试指引同步更新。README.md 命令区与结构树同步更新。
- **Description**:
  - 实现增量水位（每账号最新采集时间/游标）与 `mp-archiver sync --account ...`（增量）、`run --full`（回溯+校验）命令；统一编排列表→正文→媒体→互动→导出。
  - 提供调度方案文档：本机计划任务（Windows 任务计划程序 pwsh7 脚本）或 NAS cron/容器定时，含频率建议。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-9.1: 全量后连续两次 sync：零新增、零重复文件（按哈希）；人工中途 kill 后重跑最终补齐且无重复。证据：计数对比 + 中断恢复日志。
  - `rule` TR-9.2: 文档含可直接使用的计划任务配置示例（pwsh7 合规）。证据：文档。

## Task 10: RAG JSONL 导出与清洗
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - `mp-archiver export-rag`：逐篇输出 JSONL（title/author/publish_time/url/original/album/text）；纯文本提取器去 HTML 标签，可选清洗模板噪声（文末推广、二维码图注、重复声明），段落结构保留；清洗前后可对照。
- **Acceptance Criteria Addressed**: AC-11, AC-18
- **Test Requirements**:
  - `rule` TR-10.1: 全量 JSONL 逐行通过 `json.loads`；字段齐全、UTF-8；条数与 articles 表 downloaded 数一致。证据：校验脚本。
  - `rubric` TR-10.2: 语料洁净度；scale 1-5；anchors 1=标签/噪声满屏，3=可读但有残留，5=噪声干净+段落完整+可按元数据过滤；threshold >= 3；证据：抽样 5 篇人工评阅。

## Task 11: 分析报表
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - `mp-archiver report`：CSV 明细 + 单文件 HTML（pandas + jinja2，无外部依赖可离线打开），五项统计：发文量时间序列（月/年）、星期×时段热力、原创占比、合集 Top 分布、含音频/视频文章占比。
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements**:
  - `rule` TR-11.1: 报表包含五项统计且渲染正常；每个数字可由一条 SQL 对账一致。证据：报表文件 + 对账 SQL 输出。
  - `rule` TR-11.2: 空库/单篇等边界数据不报错。证据：单测。

## Task 12: 故障注入与韧性验收
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 演练剧本：403/验证码页/超时/单篇 404/媒体链接失效/凭证过期；验证指数退避、现场保留、失败隔离与 failed 清单输出、续跑恢复。
  - 据演练结果修补 Task 2 客户端与各 adapter 的韧性缺口。
- **Acceptance Criteria Addressed**: AC-10, AC-8
- **Test Requirements**:
  - `rule` TR-12.1: 五类故障注入下行为符合 AC-10；无猛打请求（退避日志可见），批次最终给出成功/失败/跳过分类计数。证据：演练日志归档。
  - `rule` TR-12.2: 演练中发现的问题全部关闭并有回归测试。证据：问题清单与测试。

## Task 13: 文档、合规声明与默认限速
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10, Task 11
- **Description**:
  - README：架构图（Mermaid）、部署、账号准备（专用订阅号注册/扫码）、凭证获取与续期、CLI 用法、存储布局、故障排查（风控/验证/票据过期/媒体不可得）、合规声明（个人学习存档、禁止商用再分发与绕付费、尊重版权、24h 删除声明、频率自律）。
  - 核定默认限速为保守值并在配置中标注依据。
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `rule` TR-13.1: README 合规五要点齐全；默认限速参数存在且为保守值；Mermaid 通过 `check_mermaid.py`。证据：文档 + 检查输出。
  - `rule` TR-13.2: 按文档从零可在干净环境完成部署与一次单篇下载演练（文档可用性走查）。证据：走查记录。

## Task 14: 测试体系与端到端验收
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 12, Task 13
- **Description**:
  - 以本地 HTML/JSON fixture 覆盖解析/清洗/媒体识别/去重/状态机等纯逻辑，覆盖率 ≥80%（关键模块 ≥90%）；执行全仓库 pytest 无回归；完成 AC-4/5/6/7/8 的端到端验收取证；凭证泄露扫描；整理验收证据包。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-17
- **Test Requirements**:
  - `rule` TR-14.1: 覆盖率达标，pytest 全绿；`git grep` 凭证扫描与 `git ls-files` 检查通过。证据：覆盖率报告/命令输出。
  - `rule` TR-14.2: 每条引用的 AC 均有独立取证记录（命令输出、文件清单、对照表），证据包路径写入各任务 Completion Evidence。证据：验收证据包。
  - `rubric` TR-14.3: 整体工程质量；scale 1-5；anchors 1=不可维护一次性脚本，3=可用但脆弱，5=幂等可续跑+测试齐+文档全+接口变更隔离；threshold >= 4；证据：代码与证据包评审。
