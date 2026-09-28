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
- **AC 验收取证（Task 14 / TR-14.2）**: AC-9 凭证零泄露的独立取证记录（`git ls-files` / `git grep` 原始输出与逐行归类）见 [evidence/acceptance-evidence.md](evidence/acceptance-evidence.md) §6 与 [evidence/credential-scan.txt](evidence/credential-scan.txt)。
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
- **AC 验收取证（Task 14 / TR-14.2）**: AC-4 全量列表落库的端到端取证（11 条落库 + 对账标记 + 唯一键去重 + 已删状态记录，期望值↔实测值对照表）见 [evidence/acceptance-evidence.md](evidence/acceptance-evidence.md) §1。
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
- **AC 验收取证（Task 14 / TR-14.2）**: AC-5 正文与图片离线保真的端到端取证（10 篇四件套齐全、图片 100% 本地化、无远程残留、长文/图集形态无损）见 [evidence/acceptance-evidence.md](evidence/acceptance-evidence.md) §2。
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
- **AC 验收取证（Task 14 / TR-14.2）**: AC-6 富媒体分类处置的端到端取证（四类媒体逐类计数、`media/` 仅 1 个真实落盘文件即「无伪造」强证据）见 [evidence/acceptance-evidence.md](evidence/acceptance-evidence.md) §3。
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
- **AC 验收取证（Task 14 / TR-14.2）**: AC-7 互动条件性采集三态（开关关闭零写入 / 无凭证 `skipped_no_credential` / 有凭证评论与指标入库）与真实 CLI `run --full --fetch-metrics` 退出码 0 的独立取证见 [evidence/acceptance-evidence.md](evidence/acceptance-evidence.md) §4。
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
- **AC 验收取证（Task 14 / TR-14.2）**: AC-8 重跑幂等（DB 四表计数 + 归档文件清单集合级双不变）与失败注入续跑的独立取证见 [evidence/acceptance-evidence.md](evidence/acceptance-evidence.md) §5。
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
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Completion Evidence**:
  - 纯文本提取器（新增 [src/mp_archiver/core/text_extract.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/core/text_extract.py)，无 IO 纯函数层）：`html_to_plain_text()` 从本地化 `article.html` 的 `#js_content`（缺失时回退 article→body→根）提取——块级元素闭合转换行保留段落、`li` 转 `- `、`<pre>` 经哨兵标记保留代码缩进、script/style/img 等无文本节点移除（含懒加载图 alt 广告文案）、mpvoice/mpvideo/qqmusic 等富媒体自定义标签转「［音频：标题］」占位行（标题取 data-name/name/title/alt）；`\xa0`/全角空格/tab 规范化、连续空行折叠。`clean_plain_text()` 保守清洗并返回 CleanStats（removed_noise_lines/collapsed_duplicates/trimmed_tail_lines）：①短行整行强匹配（去空白 ≤40 字 + 关注/扫码/在看/转发/赞赏等动作词正则 + 纯装饰符号行），代码缩进行豁免；②相邻完全重复非空行折叠；③平台推荐块仅在文章后半部命中锚点（「喜欢此内容的人还喜欢」等 4 个）时整段裁剪，前半部命中保留，防正文误伤。
  - 导出编排（新增 [src/mp_archiver/exporters/rag.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/exporters/rag.py)）：`export_rag_jsonl()` 枚举 DB 中 status=downloaded 文章（新增 `db.iter_downloaded_articles`，发布时间升序、支持账号 biz 过滤与 limit，已登记 db/__init__.py re-export），逐篇读归档 HTML→提取→可选清洗→写 JSONL；UTF-8、LF、`ensure_ascii=False`、同目录 `.tmp`+`os.replace` 原子覆盖（幂等），单篇异常（路径为空/绝对路径或 `..` 越界/文件缺失/解析错误）隔离计 failed 不阻断批次，空正文（纯图片帖）仍保留元数据条目；报告 RagExportReport 含 total/exported/empty_text/failed 与清洗计数。字段为需求七字段的超集：`id/account/title/author/publish_time/url/original(bool)/album/digest/text`，`--with-raw` 追加 `text_raw`（清洗前原文）实现逐行对照。
  - CLI（[src/mp_archiver/cli.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/cli.py)）：新增离线命令 `export-rag [-a 账号] [-o 文件] [--no-clean] [--with-raw] [--limit N]`；默认输出 `exports/rag.jsonl`（新增配置 `MP_ARCHIVER_EXPORT_ROOT`，默认 exports/，已在 .gitignore；.env.example 已补）；打印导出计数与三类清洗动作统计与失败清单；退出码 0 成功/1 存在失败条目/3 账号未找到。README.md 命令区新增命令、字段表与清洗纪律说明，结构树 exporters 注释同步。
  - TR-10.1（软件侧闭环）：新增 25 个单测，全量 188/188 通过（基线 163 + 新增 25，无回归）。① [tests/test_text_extract.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_text_extract.py) 14 例：块级段落与导航排除、懒加载 img 移除、富媒体占位、pre 缩进保留（提取后与清洗后双锁）、容器缺失回退、空白规范化、空/纯 script 页容错；清洗 7 例（引导/装饰行删除、**正文讨论"二维码技术原理"不误伤**、尾部推荐块裁剪/前半部锚点保留、重复行折叠、空文本稳定）。② [tests/test_rag_export.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_rag_export.py) 11 例：逐行 json.loads 合法、字段集齐全、original 为 bool、UTF-8 中文、发布时间升序、仅 downloaded 导出、账号过滤、clean/--no-clean/--with-raw 三模式对照、HTML 缺失隔离、**路径越界拒绝**、空正文保留、空库 0 行且自动建目录、幂等重跑字节稳定且无 .tmp 残留、CLI 退出码 0/1/3。另在隔离临时库完成真实进程 CLI 端到端冒烟（造文→导出→with-raw 对照人工核对），结果符合预期；仓库 check-links 校验通过。
  - TR-10.2（rubric，挂起）：真实号抽样 5 篇人工评阅挂起——主机暂无真实归档语料，与 TR-3.1/TR-9.1 等真机验收项一并在部署环境执行。软件侧评阅条件已就绪：默认清洗产出 + `--no-clean` 独立产出 + `--with-raw` 同条记录双文本对照 + CLI 打印清洗动作计数，可直接按 anchors（1=标签/噪声满屏，3=可读有残留，5=干净+段落完整+可按元数据过滤）打分；防误伤机制（长度门+动作词+尾部锚定+代码缩进豁免）已由单测显式锁定。
- **Description**:
  - `mp-archiver export-rag`：逐篇输出 JSONL（title/author/publish_time/url/original/album/text）；纯文本提取器去 HTML 标签，可选清洗模板噪声（文末推广、二维码图注、重复声明），段落结构保留；清洗前后可对照。
- **Acceptance Criteria Addressed**: AC-11, AC-18
- **Test Requirements**:
  - `rule` TR-10.1: 全量 JSONL 逐行通过 `json.loads`；字段齐全、UTF-8；条数与 articles 表 downloaded 数一致。证据：校验脚本。
  - `rubric` TR-10.2: 语料洁净度；scale 1-5；anchors 1=标签/噪声满屏，3=可读但有残留，5=噪声干净+段落完整+可按元数据过滤；threshold >= 3；证据：抽样 5 篇人工评阅。

## Task 11: 分析报表
- **Status**: `completed`（软件完成 2026-09-24；TR-11.1 对账已由 17 项单测在样例库闭环，真实号报表评阅待部署环境执行）
- **Priority**: medium
- **Depends On**: Task 6
- **Completion Evidence（软件侧）**:
  - 报表模块（新增 [src/mp_archiver/exporters/report.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/exporters/report.py)，纯派生离线任务不触网）：
    - 聚合层 `load_report_data()`：五项统计全部由带 `GROUP BY` 的单条 SQL 产出——年/月序列 `strftime('%Y'|'%Y-%m', publish_time, '+8 hours')`、星期×小时热力 `strftime('%w'|'%H', ..., '+8 hours')`、原创计数、合集 Top N（`n DESC, album ASC` 稳定排序）、音视频文章数（`media JOIN articles`，`media_type IN ('audio','video')` 的 `DISTINCT article_id`）。
    - **双口径显式声明**：统计①–④分母为有 `publish_time` 的全部文章（未归档也参与，M 集）；统计⑤分母为 `status=downloaded`（D 集，媒体行仅正文归档时写入，避免假性偏低）；`ReportData.scoped` 显式布尔标志区分单账号/全量，不依赖账号别名推断。
    - **北京时间口径**：SQL 聚合 `+8 hours` 与明细层 pandas `to_datetime(utc=True).tz_convert('Asia/Shanghai')` 双路一致；UTC 跨日/跨月/跨年（如 2023-12-31T17:00→北京 2024-01-01 周一 01 时）有单测锁定；兼容上游 `isoformat()` 实际产出的 `+00:00` 后缀与 `Z` 后缀（已实测 SQLite 四种时间形态）。
    - 明细层 `build_articles_frame()`：pandas SQL 读取（含 `EXISTS` 子查询的 has_audio/has_video），派生列发布时间_北京/年/年月/星期（中文）/小时；CSV 固定列序 + 中文表头 + **utf-8-sig BOM**（Excel 打开不乱码）+ 换行 LF。
    - HTML 渲染：Jinja2 内联模板（autoescape 开启，专辑名 `<img onerror>` 注入有转义测试）、内联 CSS、**零 JS/零外链/零 CDN**（测试断言无 `src="http`/`href="http`/`<script`）；7×24 热力用静态 rgba 背景色；KPI/比例条/月年条形全为静态 HTML；空库/无时间/单篇/无合集/无媒体均渲染空态文案；页脚展开区附七组对账 SQL（scoped 时自动带 `:biz` 过滤，全部账号时不带）。
    - 原子写入：HTML 与 CSV 均同目录 `.tmp + os.replace` 整体覆盖，重跑字节稳定、无 .tmp 残留。CSV 防公式注入：`=+-@`/制表/回车开头文本单元格前置单引号（OWASP 建议，标题/链接/合集名为公众号侧可控文本）。
    - CLI `report [-a 账号] [-o 目录] [--top N]`（[cli.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/cli.py)）：默认输出 `exports/report/report.{html,csv}`（复用 Task 10 的 `MP_ARCHIVER_EXPORT_ROOT`）；终端打印各口径计数；退出码 0 成功/3 账号未找到。pyproject 依赖新增 `pandas>=2.2`、`jinja2>=3.1`（venv 实装 pandas 3.0.6 / jinja2 3.1.6）。
  - TR-11.1（软件侧闭环）：新增 [tests/test_report.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_report.py) 17 例——五项统计数字与**独立重算 SQL** 逐项断言一致（年/月/热力/原创/合集/音视频，含跨账号、跨年、pending 不进音视频分母、一篇同时含音视频去重）、CSV 明细行数与北京派生列、HTML 五区块+对账 SQL+离线单文件+转义、账号过滤、Top N 排序与限量、幂等无残留、真实 `+00:00` 时间格式、CSV 注入防护、scoped 页脚（含账号别名恰为「全部账号」的反例）、CLI 0/3 退出码；全量 **205/205 通过**（基线 188 + 新增 17，无回归）。
  - TR-11.2（闭环）：空库（两文件正常生成、CSV 仅表头、KPI 显「—」非 None）、单篇、无发布时间（2 篇）等边界均有单测且不报错。
  - **真实号报表评阅挂起**：主机暂无真实归档语料，HTML 视觉评阅（热力配色/中文排版）与 TR-11.1 真实库对账待部署环境执行；对账 SQL 已内置报表页脚，届时可直接复制核对。
- **Description**:
  - `mp-archiver report`：CSV 明细 + 单文件 HTML（pandas + jinja2，无外部依赖可离线打开），五项统计：发文量时间序列（月/年）、星期×时段热力、原创占比、合集 Top 分布、含音频/视频文章占比。
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements**:
  - `rule` TR-11.1: 报表包含五项统计且渲染正常；每个数字可由一条 SQL 对账一致。证据：报表文件 + 对账 SQL 输出。
  - `rule` TR-11.2: 空库/单篇等边界数据不报错。证据：单测。

## Task 12: 故障注入与韧性验收
- **Status**: `completed`（软件完成 2026-09-25；六剧本以 MockTransport 故障注入在 CI 内闭环并留可复现演练命令，真实微信环境/Docker 扫码实操演练仍挂起）
- **AC 验收取证（Task 14 / TR-14.2）**: AC-8 断点续跑与 AC-10 熔断语义的独立取证见 [evidence/acceptance-evidence.md](evidence/acceptance-evidence.md) §0 结论摘要与 §5.2（中断后续跑）。
- **Priority**: high
- **Depends On**: Task 9
- **Completion Evidence（软件侧）**:
  - 故障按作用域分流（I/F 阶段事实采集→七概念 I→F→A→V→C，AC-10/AC-8）：
    - **账号/IP 级风控立即熔断**：文章页 403/429 在 [http_client.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/http_client.py) 请求级指数退避（`min(cap, base·2^attempt)+抖动`，封顶 60s）用尽后，由 [article_archive.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/core/article_archive.py) `archive_article()` 抛 `RiskControlError(kind="risk_control")`；验证码/环境异常页经**结构感知**页面判定（`#js_content` 缺失或为空才在容器外查风控标记，正文非空时即便包含「去验证/环境异常」等词也判正常，杜绝误杀）同样熔断。当前篇置 failed（原因 `risk_abort:` 前缀可查），本批后续文章保持 pending **零请求**，CLI 打印 `[abort]` 横幅并返回退出码 4。
    - **连续传输/服务故障阈值熔断**：超时/连接错误重试用尽、以及文章页 500/502/503/504 重试用尽（`RiskControlError(kind="transport")`）先隔离为单篇 failed；连续达新配置 `transport_abort_threshold`（[config.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/config.py) 默认 2，`MP_ARCHIVER_TRANSPORT_ABORT_THRESHOLD` 可调）才熔断；成功篇/删除违规跳过篇/单篇业务失败（404 等）均重置连续计数，偶发抖动不误熔断。
    - **单篇/单资源失败隔离**：单篇 404 不重试、置 failed 批次继续，批次末尾输出成功/跳过/失败分类计数与失败清单；图片 404/语音 5xx 等媒体失效逐项登记 media 表与 `metadata.json` 例外表（保留远程引用），文章仍 downloaded；采集服务 401/403 维持凭证过期语义（退出码 2，不在凭证错误上空耗重试预算）。
    - **退避可观测且脱敏**：`_backoff()` 每次退避输出 WARNING 日志（`HTTP 重试退避：GET <host> 第 n/m 次…x.xx 秒后重试`），只记 netloc 不记 query/userinfo（sn 不入日志），畸形 URL 回退 `<unknown-host>`。
    - **现场保留与幂等续跑（AC-8）**：`FetchReport` 新增 `aborted/abort_reason/pending_in_account` 与 `pending_left`；每篇成败即时落库，普通重跑只采 pending（自动越过 failed 熔断篇），`--include-failed` 才重试失败篇；三批续跑演练验证最终 5 篇 downloaded、恰 5 目录 5 份 article.html 无重复；`--limit` 熔断时横幅额外提示库内真实 pending 总量。
  - TR-12.1（软件侧闭环）：新增 [tests/test_fault_injection.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_fault_injection.py) **15 例**故障注入演练（全程 MockTransport 不触网），剧本与用例一一对应——①403 退避 3 请求/`[2.0,4.0]` 秒/日志可见/仅处理 1 篇即熔断；②验证码页（含空 `js_content` 变体，断言零归档产物）；③a 超时连续 2 篇熔断（退避秒数精确断言）、③b 超时被 404/成功篇隔开不熔断；④单篇 404 隔离不重试；成功/失败/跳过三分类计数；⑤图片 404+语音 500 例外表与 media 行状态；⑥adapter 403→`CredentialExpiredError` 仅 1 请求 + 列表中途凭证失效落库 `expired`；⑦熔断→pending 续跑→`--include-failed` 补齐的幂等三批；⑧fetch CLI 与 ⑨sync pipeline 两路径熔断横幅 + 退出码 4（后者在 [test_cli_pipeline.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_cli_pipeline.py)）；另含 `--limit` 本批/库内剩余计数断言。**演练日志归档方式**：测试模块 docstring 固化可复现命令 `pytest tests/test_fault_injection.py -s -o log_cli=true --log-cli-level=WARNING`（退避/熔断日志随演练实时输出，即 TR-12.1 要求的可重复演练日志）。
  - TR-12.2（闭环）：fresh-context 独立对抗评审（六类反例实证）发现 **2 个 P1 + 8 项 P2 全部处置**——P1-1 风控 marker 全文子串匹配会误杀正文含风控词的正常文章（修复为结构感知判定 + 回归）；P1-2 文章页 5xx 重试用尽后被当业务失败、网关整体故障时逐篇重试放大请求（修复为 `kind="transport"` 连续计数熔断 + 回归，同时激活原死契约）；P2 含未知拦截页变体熔断、`--limit` 横幅真实剩余、退避日志畸形 URL 防泄露、阈值默认值双写注释、退出码 4 语义在 README 固化、pipeline 熔断路径补测等；图床 CDN 整体故障维持「媒体隔离不阻断文章」既有边界（与剧本⑤一致，记录为刻意决策）。
  - 全量 **221/221 通过**（Task 11 基线 205 + 新增 16：演练文件 15、CLI pipeline 1），旧风控断言（`PageUnavailableError` → `risk_abort/risk_control`）同步更新，无回归。文档：[README.md](../../../apps/dev-tools/wechat-mp-archiver/README.md) 新增「故障处置与断点续跑（韧性设计）」小节（六类故障行为/处置表 + 退出码语义）。
  - **真实演练挂起**：403/验证码/超时在真实微信域名上的触发频率、风控页真实文案样本校准（`_PAGE_MARKERS` 经验值，源码已留校准入口）需 Docker 采集服务扫码环境实操；软件侧熔断/退避/隔离/续跑机制与可观测性已全部可测。
- **Description**:
  - 演练剧本：403/验证码页/超时/单篇 404/媒体链接失效/凭证过期；验证指数退避、现场保留、失败隔离与 failed 清单输出、续跑恢复。
  - 据演练结果修补 Task 2 客户端与各 adapter 的韧性缺口。
- **Acceptance Criteria Addressed**: AC-10, AC-8
- **Test Requirements**:
  - `rule` TR-12.1: 五类故障注入下行为符合 AC-10；无猛打请求（退避日志可见），批次最终给出成功/失败/跳过分类计数。证据：tests/test_fault_injection.py 15 例 + docstring 可复现演练日志命令（CI 内 MockTransport 闭环；真实环境实操挂起）。
  - `rule` TR-12.2: 演练中发现的问题全部关闭并有回归测试。证据：独立对抗评审 P1×2/P2 清单全部处置，6 个 V 阶段回归用例（marker 误杀、未知拦截页、5xx 连续熔断/单次不熔断、limit 计数、pipeline CLI 退出码）。

## Task 13: 文档、合规声明与默认限速
- **Status**: `completed`（软件完成 2026-09-28；文档可用性走查已在干净临时目录实跑闭环，真机扫码部署演练与截图仍挂起）
- **Priority**: high
- **Depends On**: Task 10, Task 11
- **Completion Evidence（软件侧）**:
  - 主文档 [README.md](../../../apps/dev-tools/wechat-mp-archiver/README.md) 按任务清单补齐八块：
    - **架构图（Mermaid）**：三泳道（微信平台 / 采集服务 Docker 仅绑回环 / 本机管线），显式区分「回环取列表」与「正文媒体直连 mp.weixin.qq.com（剥离 Token）」两条数据流及离线派生产物；通过仓库维护版检查器 `python .agents/scripts/check-mermaid.py --path apps/dev-tools/wechat-mp-archiver`（0 错误；该检查器规则为单行标签、禁 `<br/>`/圈码/【】/Markdown 列表触发符——注：仓库根 `check_mermaid.py` 是硬编码到历史路径的一次性脚本，不扫描本项目，TR-13.1 取证以 `.agents/scripts/check-mermaid.py` 为准）；`check-links.py --path` 同目录 0 断链。
    - **部署与从零演练**：安装段标注 Python ≥3.14 与 Docker（含 Linux/macOS venv 激活路径）；「快速开始」7 步——专用订阅号准备 → `deploy/` 起容器扫码 → 复制 `.env` → `init-db`/`doctor` → `list --max-pages 2` → `fetch --limit 1` 单篇四件套核对 → 转入 `sync`/`run --full` 日常。
    - **账号准备与凭证获取/续期**：凭证矩阵覆盖扫码登录态（经验 4 天，退出码 2/doctor 授权提示 → deploy 第 4–5 节重扫）、`MP_ARCHIVER_EXPORTER_TOKEN`（与 `collector.env` 的 `MCP_TOKEN` 同值，已核对 [collector.env.example](../../../apps/dev-tools/wechat-mp-archiver/deploy/collector.env.example)）、互动票据（deploy 第 8 节抓包，失效记 `skipped_no_credential`）、官方 AppID/AppSecret（deploy 第 11 节，48001 自动降级、日配额 90）。
    - **CLI 用法**：命令块补齐此前遗漏的 `official-doctor`、`resolve-biz`，与 [cli.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/cli.py) argparse 实际 11 个子命令及全部选项逐一核对；退出码语义补全（3 在 `sync-official` 路径含 biz 未配置；4 含 R2 列表 biz 不可得——V 阶段 P1 修复，deploy 第 12.2 节同步更正）。
    - **存储布局**：目录树逐项对代码取证——`.env`、`data/archive.db`（articles/media/comments/metrics/sync_state 五表）、`data/official_api_quota.json`、文章目录四件套 `article.html`/`article.md`/`metadata.json`/`images/`/`media/`、`exports/rag.jsonl` 与 `exports/report/report.{html,csv}`、`logs/`，采集服务凭证卷 `mp_archiver_collector_data`（deploy 侧）。
    - **故障排查索引**：熔断（链 Task 12 韧性表）、登录态过期、采集服务未响应（改用真实输出串，doctor 退出码仍 0）、无服务时 list 约 1 分钟退避后退出码 4、媒体防盗链/视频号迁移平台侧不可得、互动票据短期失效、官方 48001/配额/biz 六行，与 deploy 第 10 节交叉引用。
    - **合规声明六条**：①个人学习/本地存档（含离线 RAG）限定，禁止商用与公开再分发、禁止重建替代服务；②不绕付费阅读/会员/赞赏等访问控制与平台权限；③尊重版权、合理引用标注出处；④频率自律（默认限速、每日增量至多一次/全量每周至多一次、见风控信号即停）；⑤凭证与数据安全（本人扫码、`.env` 不入库且日志脱敏、服务不暴露公网）；⑥**24 小时删除义务**（权利人主张/投诉/合规要求时 24h 内删除正文、媒体与派生产物且不留副本）。AC-14 五要点 + 任务要求的 24h 声明全覆盖，且每条承诺与代码实际行为一致（互动默认关闭、派生产物纯离线等）。
  - **默认限速保守值与依据**：[config.py](../../../apps/dev-tools/wechat-mp-archiver/src/mp_archiver/config.py) 限速字段上方注释核定结论，[.env.example](../../../apps/dev-tools/wechat-mp-archiver/.env.example) 同步；README「默认限速」表列 6 项参数实测默认值（请求间隔 2.0/5.0 秒、重试 5、退避 2.0 封顶 60、超时 30、传输熔断阈值 2、官方日配额 90）。依据分层表述：**保守方向**来自方案文档 3.2 节实证失效模式（高频请求触发验证码/临时封禁）与第六节访问克制；**2–5 秒具体区间为本项目工程判断**（贴近人工浏览节奏，非平台公布阈值，V 阶段 P2 修正了引用强度）；调度频率依据 deploy 第 12 节（登录态约 4 天，每日增量可追平）。
  - TR-13.1（闭环）：合规六要点齐全；默认限速参数存在且为保守值并在两处配置文件标注依据；Mermaid 与链接检查器输出 0 错误（命令见上）。
  - TR-13.2（软件侧闭环）：fresh-context 独立评审员在系统临时干净目录实跑「建库→五表→doctor→无服务 list→未知账号 fetch」走查：`init-db` 退出 0 且建成恰好五表；设置默认值逐项读取为 2.0/5.0/5/2.0/60.0/30.0/2/90 与文档表一致；doctor 无服务时仅告警不崩溃（退出 0，输出串与文档一致）；无服务 list 经退避后退出 4；未知账号 fetch 退出 3。另核全部命令/参数/路径/卷名/交叉引用节号属实，临时产物已清理。评审输出 **P0=0、P1=1、P2=7 全部处置**：P1（deploy 退出码 3/4 的 biz 映射与代码矛盾）已更正 README 与 deploy 两处；P2 含 Mermaid 补正文直连边、RAG 音频/视频/音乐占位符精确化、doctor 真实输出串、依据引用强度、Linux/macOS 激活路径、list 退避等待窗口提示，末项为根历史检查器不适用本项目的取证说明（本证据已记录）。全量 **221/221 通过**（config.py 仅注释变更，无回归）。
  - **真机演练挂起**：Docker 起容器、专用订阅号扫码截图、真实账号单篇下载的环境实操待部署环境执行（deploy/README.md 第 3 节已留截图位）；文档命令本身已逐条与代码/实跑对齐。
- **Description**:
  - README：架构图（Mermaid）、部署、账号准备（专用订阅号注册/扫码）、凭证获取与续期、CLI 用法、存储布局、故障排查（风控/验证/票据过期/媒体不可得）、合规声明（个人学习存档、禁止商用再分发与绕付费、尊重版权、24h 删除声明、频率自律）。
  - 核定默认限速为保守值并在配置中标注依据。
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `rule` TR-13.1: README 合规五要点齐全（实际交付六条，含 24h 删除）；默认限速参数存在且为保守值并标注依据；Mermaid 通过仓库维护版检查器 `.agents/scripts/check-mermaid.py --path apps/dev-tools/wechat-mp-archiver`（0 错误），链接检查同过。证据：README/config.py/.env.example + 检查输出（本证据记录）。
  - `rule` TR-13.2: 干净临时目录从零走查（init-db/五表/doctor/list/fetch 退出码与默认值）已由独立评审实跑通过；真机扫码部署演练挂起。证据：本 Completion Evidence 走查段。

## Task 14: 测试体系与端到端验收
- **Status**: `completed`（2026-09-28；软件侧闭环：302 全绿 + 覆盖率 96% + 证据包落盘 + V 阶段独立评审 P0=0；真机扫码部署类验收项已显式挂起）
- **Priority**: high
- **Depends On**: Task 12, Task 13
- **Completion Evidence（软件侧）**:
  - **TR-14.1（闭环）**：全仓库 `pytest` **302 passed**（Task 13 基线 221 + 净增 81），0 failed / 0 error / 0 skipped；覆盖率 **TOTAL 96%**（2665 语句 / 101 未覆盖）；关键模块全部 ≥90%——`wechat_payload` / `wechat_download_api` / `cli` / `pipeline` / `validation` / `credentials` / `exceptions` 均 100%，最低 `comment_sync` 90%；仅 `models.py` 89%、`official_probe.py` 88% 两个非核心模块低于 90%。凭证扫描：`git ls-files` 该应用 65 个受控文件中仅两份 `*.example` 命中，无 `.env` / `data/` / `*.db` / `archive/` / `exports/` 被跟踪；`git grep` 69 行命中逐行确认全为 `*.example` 空占位 / 文档与代码符号引用 / 测试夹具显式假值。证据：[evidence/pytest-coverage.txt](evidence/pytest-coverage.txt)、[evidence/credential-scan.txt](evidence/credential-scan.txt)。
  - **测试补强构成**：新增 [tests/test_cli_commands.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_cli_commands.py) 52 例（11 个子命令的正常/异常/退出码/输出文案 + `python -m` 入口）、新增 [tests/test_acceptance_e2e.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_acceptance_e2e.py) 6 例（AC-4/5/6/7/8 端到端）、[tests/test_wechat_payload.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_wechat_payload.py) 14→29（+15，覆盖率 86%→100%）、[tests/test_wechat_download_adapter.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_wechat_download_adapter.py) 7→15（+8，84%→100%）；另 [tests/test_report.py](../../../apps/dev-tools/wechat-mp-archiver/tests/test_report.py) 冻结时钟加固消除 `generated_at` 跨秒偶发失败，[pyproject.toml](../../../apps/dev-tools/wechat-mp-archiver/pyproject.toml) dev 附加依赖补 `pytest-cov>=5.0` 使覆盖率取证可复现。**未改动 `src/` 下任何生产代码**（`git status --short` 中 `src/` 零变更）。
  - **TR-14.2（闭环）**：验收证据包 [evidence/](evidence/README.md)（5 文件）——正文 [acceptance-evidence.md](evidence/acceptance-evidence.md) 给出逐条 AC 的 Given/When/Then 对照、断言期望值↔实测值对照表、结论与挂起项；配套三份原始输出 [e2e-acceptance.txt](evidence/e2e-acceptance.txt)（6 例逐例 PASSED + 用例↔AC 对照）、[pytest-coverage.txt](evidence/pytest-coverage.txt)、[credential-scan.txt](evidence/credential-scan.txt)，以及索引与复现命令 [README.md](evidence/README.md)。证据包路径已写入 **Task 2 / 4 / 5 / 6 / 7 / 9 / 12** 的 Completion Evidence（见各任务 Status 行下方的「AC 验收取证（Task 14 / TR-14.2）」条目）。
  - **TR-14.3（rubric 自评 5，下限 4）**：五项锚点要素（幂等可续跑 / adapter 隔离 / 日志完善 / 解析层 fixture 单测 / 文档齐全）均有可复现证据（详见 [acceptance-evidence.md](evidence/acceptance-evidence.md) §8）；扣分项披露：90 条既有 `ResourceWarning: unclosed database`（测试侧 sqlite 连接未显式 close，非本轮引入）与 `models.py` 89%、`official_probe.py` 88%，若评审计入则为 4 —— 两种口径均 ≥ 阈值 4。
  - **V 阶段 fresh-context 独立对抗评审（P0=0）**：评审提出 **2 个 P1 + 4 项 P2，全部处置**。P1-1 证据包 §6 文字结论「44 行命中」与粘贴原始输出（69 行）自相矛盾 → 更正为 69 行并复核；P1-2 §4.4「任务整体退出码 0」原引用桩掉编排层的 CLI 打印用例（`run_pipeline` 被替换为返回伪造 `PipelineReport` 的假函数，属推论冒充实测）→ 补真实 CLI 端到端用例 `test_acceptance_ac7_cli_run_without_credentials_exits_zero`（从 `cli.main(["run","-a",…,"--full","--fetch-metrics"])` 走完真实两阶段编排，仅把 HTTP 传输替换为 `httpx.MockTransport`）并改写该取证段。P2-3 `python -m` 入口用例原用 `--help`（argparse 在 `main()` 内部即抛 `SystemExit`，包装行 `raise SystemExit(main())` 的「int 返回值→退出码」路径永不执行）→ 改用 `init-db` 真实锁定；P2-4 证据包行号链接越界 ±1 修正；P2-5 `parse_article_url` 的自比对恒真断言改为具体字段断言；P2-6 `sync-official` 异常断言由笼统 `[fail]` 收窄为四类异常各自专属文案。修复后重跑全量 302 passed、覆盖率与关键模块数值不变。
  - **挂起（须真机扫码部署环境，不臆造）**：AC-4 最早文章与微信客户端对照（TR-4.1）、AC-5 真实 10 篇断网阅读与人工保真度评分（TR-5.1/5.3）、AC-6 真实 mpvoice 播放抽检（TR-6.1）、AC-7 真实凭证联调（TR-7.1）、AC-8 真实进程 kill 中断演练（TR-9.1）——均依赖 Docker 采集服务 + 专用订阅号扫码环境；汇总表见 [acceptance-evidence.md](evidence/acceptance-evidence.md) §9。软件侧等价证据（结构/引用层核对、失败注入续跑、字节级比对、MockTransport 全链路）已在本证据包逐条给出。
- **Description**:
  - 以本地 HTML/JSON fixture 覆盖解析/清洗/媒体识别/去重/状态机等纯逻辑，覆盖率 ≥80%（关键模块 ≥90%）；执行全仓库 pytest 无回归；完成 AC-4/5/6/7/8 的端到端验收取证；凭证泄露扫描；整理验收证据包。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-17
- **Test Requirements**:
  - `rule` TR-14.1: 覆盖率达标，pytest 全绿；`git grep` 凭证扫描与 `git ls-files` 检查通过。证据：覆盖率报告/命令输出。
  - `rule` TR-14.2: 每条引用的 AC 均有独立取证记录（命令输出、文件清单、对照表），证据包路径写入各任务 Completion Evidence。证据：验收证据包。
  - `rubric` TR-14.3: 整体工程质量；scale 1-5；anchors 1=不可维护一次性脚本，3=可用但脆弱，5=幂等可续跑+测试齐+文档全+接口变更隔离；threshold >= 4；证据：代码与证据包评审。
