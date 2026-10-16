# doocs/md Python 3.14 全功能复刻（doocs-md-py）- 需求规格说明书

## Overview

- **Summary**：在 `apps/doocs-md-py` 中以纯 Python 3.14 包（包名 `doocs_md_py`，CLI 名 `mdpy`，scikit-build-core 构建）复刻 doocs/md v2.1  monorepo 的全部可服务端化能力：微信兼容 Markdown 渲染核心库、与 Cloudflare Workers API 1:1 契约的 FastAPI 服务端（账号/同步/上传/分享/市场/表情/通知/爱发电回调）、13 图床 Python 上传器、stdio MCP Server、`mdpy` CLI 与 Web 静态托管；原版 Vue3 前端零源码修改、构建产物由同源 FastAPI 托管，浏览器直接对接。
- **Purpose**：获得一个不依赖 Cloudflare 平台（D1/R2/Workers/ASSETS）、可本地自托管、可嵌入 Python 生态（库 + MCP + CLI）的 doocs/md 等价物，用于本地隐私优先的写作与内网部署。
- **Target Users**：①希望本地/内网自托管 md 编辑器全栈能力的个人用户；②需要在 Python/AI Agent 工作流中调用 md 渲染能力的开发者（MCP/库）；③需要命令行批量渲染 Markdown→微信 HTML 的运维/内容生产用户。

## Goals

- **G1 渲染等价**：Python 渲染核心覆盖原版 `packages/core` 的全部管线：front-matter 解析、marked 自定义渲染器全部元素规则、12 个扩展（component、markup、emoji、toc、slider、alert、katex、footnotes、mermaid、plantUML、infographic、ruby）、净化、阅读时间、主题 CSS 装配（变量/标题样式/`var()`/`calc()` 运行时解析）。
- **G2 API 契约 1:1**：FastAPI 实现 `apps/api` 全部公开与鉴权端点，HTTP 方法/路径/状态码/错误体字符串/限流数值/校验阈值/SQL 持久化语义与 Hono 版逐一对拍；SQLite 替代 D1（8 个迁移等价落地），本地文件系统与 S3 替代 R2。
- **G3 前端零修改接入**：用原版 Vue3 源码在 node:22 + pnpm 11 环境构建 `apps/web/dist`，通过构建期环境变量指向同源 Python API，不修改任何前端源码（如确需补丁须经用户批准并登记）；FastAPI 同源托管 dist，浏览器中全部功能（编辑/IndexedDB/同步/上传/分享/市场/表情/导出/AI 助手 BYOK）可用。
- **G4 通道等价**：stdio MCP Server 复刻原版 13 个工具（同名、同入参 schema、同 JSON 输出形状）；`mdpy` CLI 覆盖渲染、托管、上传、MCP、数据库迁移；13 图床上传器以纯 Python（标准库签名 + httpx）实现。
- **G5 工程合规**：满足仓库硬约束（scikit-build-core ≥0.9、Python ≥3.14、禁止 `from __future__ import annotations` 并配 AST 守护、kebab-case 纯英文文件名、中文 Conventional Commits、覆盖率门禁），并在 `apps/AGENTS.md` 完成应用登记。

## Non-Goals

- **NG1 JS 专属渠道复刻**：不实现 VS Code 扩展（`apps/vscode`）、uTools 插件（`apps/utools`）、Chrome/Firefox/Safari 扩展（WXT 产物）。其能力由 Web 托管 + MCP + CLI 等价覆盖；spec 中仅记录平台差异。
- **NG2 浏览器运行时能力搬迁**：PDF 打印、PNG/分段截图、剪贴板 juice 内联、浏览器图片压缩、浏览器内直传图床（七牛 qiniu-js、AWS SDK 浏览器预签名、formCustom 的用户 JS 沙箱执行）均由原版前端 JS 在浏览器内完成，Python 侧不重写。formCustom 以"Python 插件注册入口"作为可扩展替代，不承诺执行用户 JS。
- **NG3 云服务运营**：不提供官方托管、不内置任何付费凭证/AI Key；爱发电付费回调默认关闭；GitHub OAuth、图床凭证、S3/本地存储均由部署者自备配置；默认配置即可本地离线运行。
- **NG4 平台运维等价**：不追求 Cloudflare D1/R2/KV/ASSETS/Cache API/`CF-Connecting-IP` 等云厂商特性的运维等价；IP 取值班退化为 `X-Forwarded-For` 首项/对端地址。
- **NG5 服务端 AI 代理**：AI 助手为前端 BYOK 直连 OpenAI 兼容端点；Python 侧仅复刻服务选项清单（MCP `list_ai_services` 字面量），不实现默认 Key 的 AI 代理端点。
- **NG6 字节级渲染一致**：marked（JS）与 markdown-it-py 的 token 模型存在固有差异，不承诺输出 HTML 字节一致；验收以**归一化 DOM 结构/属性/文本等价**与关键行为（类名钩子、占位符、微信兼容约束）一致为准。

## Background & Context

### 逆向事实（R 阶段，证据锚点均在源树 `d:\AI\.chaos\libs\md`）

- **monorepo 构成**：`apps/web`（Vue3 + Vite8 + WXT + Pinia + CodeMirror6 + vue-i18n 四语 + IndexedDB）、`apps/api`（Hono + D1 + R2，8 个迁移 12 张/13 类端点）、`apps/vscode`、`apps/utools`、`packages/core`（marked + 12 扩展 + DOMPurify）、`packages/shared`（配置/主题 CSS/编辑器封装/工具）、`packages/config`、`packages/md-cli`（Express，127.0.0.1:8800，本地/dcloud 上传 + 反代）、`packages/mcp-server`（stdio，13 工具，版本 2.1.1）、`docker/`（node:22-alpine 构建 dist 到 `apps/web/dist`；Go embed 静态服务器；nginx 变体）。许可证 **WTFPL v2**（允许修改再分发，保留署名即可）。
- **渲染管线**：front-matter → marked（`breaks:true`，自定义 renderer 覆盖 heading/paragraph/blockquote/code/codespan/list/listitem/image/link/strong/em/del/table/tablecell/hr）→ 12 扩展 → `stripBreakBeforeInlineKatex` → DOMPurify（保护 mermaid/infographic 占位，`ADD_TAGS: ['mp-common-profile']`）→ 阅读时间前缀/footnotes/addition style/Mac 代码块显隐 style → `<section class="container">`。特色行为：图片尺寸语法 `alt|宽`/`alt|宽x高`；legend 六值（`title-alt/alt-title/title/alt/filename/none`）；链接 href===text 输出纯文本、微信链接保留、`citeStatus` 转 `[n]` 脚注；`diff-<lang>` 代码块 +/- 行着色；未注册语言 `data-language-pending` 走 CDN；Mac 三点 SVG；行号；hr 三变体（dash/star/underscore）；有序列表 `N. `、无序 `• ` 前缀。
- **主题与装配**：`shared/src/configs/theme-css/` 四文件（base/default/grace/simple）。CSS 变量 `--md-primary-color/--md-font-family/--md-font-size/--md-line-height/--md-block-spacing/--md-link-color/--md-blockquote-background`；标题样式 `color-only/border-bottom/border-left`（custom 由 CSS 编辑器承载，服务端不生成）；`processCSS` 在无 PostCSS 环境下迭代解析 `var()`（含 fallback 与嵌套，≤10 轮）和仅支持同单位加减/标量乘除的 `calc()`（round 到 4 位小数）；代码块主题为 10 个 hljs CDN URL 白名单（`cdn-doocs.oss-cn-shenzhen.aliyuncs.com/npm/highlightjs/11.11.1/styles/<name>.min.css`），10s 超时、缓存、`</style` 转义。
- **同步契约**：Bearer JWT（HS256，30 天，payload `{sub,login,exp}`）；`GET /sync/pull?since=`、`POST /sync/push`；文档 LWW 以 `update_datetime`、设置以 `updated_at` 为准（服务端已存在且时间戳 **≥** 客户端则跳过）；游标为 `server_updated_at`（epoch ms），push 后以服务端时钟为新游标并回拉 `now-1` 之后的全量记录；设置值存储为 JSON 字符串，读出时非字符串 JSON 值回退序列化字符串、解析失败回退 null。每次 push ≤100 文档/80 设置；id ≤128 字符；title ≤500B；content ≤512KiB；history ≤20 项且每项 ≤512KiB；setting key ≤256 字符、value ≤1MiB；请求体 ≤8MiB；单行估算 ≤1.8MB；配额 free 200 活文档/400 行、pro 2000/4000；频率 free 30/h、pro 300/h（UTC 小时键）；墓碑剥离 title/content/history。
- **前端同步白名单（25 键，必须逐字一致）**：`MD__theme`、`MD__themeSettings`、`MD__use_indent`、`MD__use_justify`、`isCiteStatus`、`isCountStatus`、`legend`、`previewWidth`、`locale`、`showAIToolbox`、`viewMode`、`previewDevice`、`MD__copyMode`、`MD__sort_mode`、`MD__enableImageReupload`、`MD__enableScrollSync`、`openai_type`、`openai_temperature`、`openai_max_token`、`MD__css_content_config`、`MD__templates`、`MD__custom_components`、`MD__marketplace_installed_themes`、`MD__marketplace_installed_components`、`quick_commands`。元数据键 `MD__sync_settings_meta`。
- **账号/OAuth**：`GET /auth/github`（state 为 uuidv4，双 cookie `md_oauth_state`/`md_oauth_redirect`，httpOnly/Lax/maxAge 600，scope `read:user`）→ 回调换 token（`POST github.com/login/oauth/access_token`，`GET api.github.com/user` 须带 `User-Agent: md-api`）→ 302 回前端 URL hash `#account_token=`/`#oauth_error=`。`APP_URL` 逗号分隔，`*` 仅匹配单 host 标签 `[^./]+`，chrome/moz/safari 扩展 origin 全放行。`GET /me` 返回 `{id,login,name,avatar,plan,planExpiresAt,isAdmin}`。
- **上传**：`POST /upload`（multipart 字段 `file`，门控 `UPLOAD_ENABLED`，仅 `image/*` MIME 前缀，0 < size ≤5MiB；匿名 60/h、free 120/h、pro 300/h（UTC 小时）；对象键 `<epochms>-<uuid>.<ext>` + `YYYY/MM/DD` 目录；扩展名映射/拒绝 `blob|bin|octet-stream`/后缀长度 ≤10/兜底 png；GitHub 后端 `PUT /repos/.../contents/...`（随机 token+repo、message 含 Referer），`raw.githubusercontent.com` → `fastly.jsdelivr.net/gh/...@branch/` CDN 改写；R2 后端 PUT 对象并返回 public URL；成功 `{url}`、失败 502 `{error:'upload_failed',message}`。
- **13 图床（前端 providers.ts 签名协议，Python 上传器按同一协议实现）**：default（走 API /upload）、github（contents API + 可选 jsDelivr CDN）、qiniu（HMAC-SHA1 putPolicy 上传凭证，deadline now+3600）、aliOSS/txCOS/minio/s3/r2（S3 SigV4 预签名 PUT，expiresIn=300，各自 endpoint/pathStyle/CDN 拼 URL 规则）、mp（stable_token 缓存；<1MiB 且 jpeg/png 走 uploadimg，否则 add_material type=image）、upyun（`UPYUN <operator>:<HMAC-SHA1(base64, MD5(password))>`，签名串 `PUT&/<bucket>/<key>&<UTC date>`，X-Date 头）、telegram（sendPhoto 取最大尺寸 file_id → getFile 拼 URL）、cloudinary（参数字典序 + SHA1(...+apiSecret) 签名或无签名 upload_preset）、formCustom（用户自定义代码，NG2）。
- **分享**：`POST /share`（free 2/天且强制过期 1d；pro 可选 1d/7d/30d/never；快照 bodyHtml+stylesHtml ≤2MiB；postId ≤64；shareId=sha256(`userId:postId`) 前 12 hex；密码模式 none/custom(4–64)/auto(8 字符去易混字母表)；PBKDF2-SHA256 100000 迭代串格式 `pbkdf2:100000:<b64salt>:<b64hash>`，常量时间比较；访问 JWT typ=`share_access`，cookie `md_share_<id>` 且 path 精确为 `/s/<id>`；解锁失败 20/h/IP；410 过期纯文本；密码门 HTML；浏览量自增；固定 CSP：`default-src 'self'; script-src 'none'; style-src 'unsafe-inline'; img-src 'self' https: data: blob:; font-src https: data:; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self'`；净化删 script/iframe/object/embed/form/meta/link/base、on* 属性、javascript:/vbscript: URL、`</style>`、危险 `@import`）。`GET /share`、`DELETE /share/:id` 仅 pro。
- **市场**：主题与组件两类；默认 pageSize 20/上限 50；sort=newest|popular；q 截断 64；slug 正则 `^[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?$`；name ≤64、description ≤2000、cover URL 须 http(s)、CSS ≤200KiB 且禁 `@import`/外部 url()、组件 JSON ≤50KiB（PascalCase 组件名、危险模板标签/属性拒绝、props 类型白名单）、sampleMarkdown ≤32KiB；发布 free 5/天、pro 30/天、admin 无限；新提交 status=pending、服务端写死 version 1.0.0；PATCH 仅作者、版本服务端按十进制 +0.0.1 并重置 pending；approve/reject 仅对 pending 生效并联动通知（`marketplace_pending/approved/rejected`）；install 仅 approved 且原子计数。
- **表情**：系统包 `system-default` 种子 + 用户包 `user-<id>` 自动创建；每包 ≤100 items（条件 INSERT 防并发突破，超限 409）；仅 png/jpeg/gif/webp、≤5MiB 且 **magic bytes 强校验**（PNG/JPEG/GIF/RIFF+WEBP）；对象键 `user/<userId>/<uuid>.<ext>`；资产头 nosniff + ETag，系统包 immutable、用户包 max-age=300；manifest 固定字段结构。
- **通知**：仅 3 类型；`GET /notifications`（30/50）、`/unread-count`、`POST /:id/read`（属主校验、幂等）、`/read-all`、`DELETE /`。
- **爱发电**：出站签名 `md5(token+"params"+params+"ts"+ts+"user_id"+userId)`，POST `/query-order`；合格订单 status=2 且 product_type∈{0,1} 且 plan_id 命中白名单（空=全接受）；webhook 只信 body 的 `out_trade_no` 并服务端重查；可选 path token；`afdian_orders` 幂等；续费 = max(now, 当前到期) + months×31 天。`POST /sync/activate` 手动激活（remark 登录名校验，大小写不敏感）。
- **MCP（13 工具）**：`render_markdown`（**20 个入参**〔2026-10-15 按 A1 以磁盘为准更正：上游 index.ts:26-137 的 zod 字段实测 20 个，原记「19」系与 `get_renderer_options` 的 19 行选项表混算〕：markdown/theme/primaryColor/fontFamily/fontSize/lineHeight/blockSpacing/linkColor/blockquoteBackground/legend/isMacCodeBlock/isShowLineNumber/citeStatus/countStatus/themeMode/isUseIndent/isUseJustify/headingStyles/codeBlockTheme/customCSS；输出 `{html, frontMatter, readingTime:{words,minutes}}`）、`list_themes/colors/fonts/font_sizes/legend_formats/heading_styles/spacing_options/color_options/code_block_themes/ai_services`、`explain_extensions`、`get_renderer_options`；默认 primaryColor `#0F4C81`、fontSize 16px、lineHeight 1.75、linkColor `#576b95`、legend `alt`。
- **md-cli**：仅绑 127.0.0.1，port 默认 8800 且占用自动换端口，`POST /upload`（multipart `file`，本地 public 目录保留原始文件名或 dcloud 四步签名上传：HMAC-MD5 `x-serverless-sign` → anonymousAuthorize → generateProximalSign → OSS multipart → report），其余路径反代线上站点。
- **环境事实**：主机 Windows 10；Python 3.14.7 + pip 25.3 在 `C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe`（PATH 被裁剪，脚本中用全路径）；主机无 Node.js；WSL（openKylin-3.0、podman machine 已修复 cgroup）可用，`/mnt/ai`（S 盘 SMB，351GB 可用）适合放大体积构建产物；同仓 `apps/travel-planner` 提供 scikit-build-core + FastAPI + src 布局先例。

### 已定范围决策（用户拍板）

1. 保留原版前端构建产物，Python 后端按原 API 契约 1:1 实现，前端零修改接入；Python 另做渲染核心库/MCP/CLI。
2. VS Code/uTools/浏览器扩展列为非目标（NG1）。
3. 云端功能全量逻辑复刻（8 表、端点、校验、LWW、限流、图床、爱发电验签）；凭证自备、付费回调默认关闭、提供本地模式。
4. 落点 `apps/doocs-md-py`，包名 `doocs_md_py`，CLI `mdpy`。

## Functional Requirements

- **FR-1 包与 CLI**：可 wheel 构建、可编辑安装；`mdpy` 提供 `render`（Markdown 文件/标准输入 → 独立 HTML 或片段）、`serve`（同源托管 dist + API，默认 127.0.0.1，端口可配且占用自动递增）、`upload`（指定图床与凭证配置上传本地图片，打印 URL）、`mcp`（stdio MCP 服务）、`migrate`（初始化/升级 SQLite）子命令。
- **FR-2 渲染库 API**：提供 `render_markdown(markdown, **options) -> {html, front_matter, reading_time}` 与可配置的装配函数（主题/色/字体/字号/行距/块距/链接色/引用背景/legend/标题样式/代码块主题/customCSS/themeMode/缩进/两端对齐/Mac/行号/引用/阅读时间）；选项默认值与字面值和 MCP 原版一致。
- **FR-3 持久化层**：SQLite 自动应用 8 个迁移（幂等），表/列/索引/CHECK/种子与 D1 迁移语义一致；时间戳一律 epoch ms 整数；提供 LWW upsert、游标 pull、配额计数、限流计数事务。
- **FR-4 鉴权与账号**：JWT HS256 签发/校验（30 天、`{sub,login,exp}`）；GitHub OAuth 两阶段（state 双 cookie、redirect origin 白名单含单标签 `*` 与扩展协议、hash 回传）；`/me`；plan 判定（pro 且未过期）；未配置 OAuth 时登录端点返回可配置的禁用响应而非崩溃；本地模式默认无需登录即可使用编辑器（数据在浏览器 IndexedDB）。
- **FR-5 同步**：pull/push 契约按背景事实逐条实现（含全部限额、错误码与字段名、墓碑剥离、设置 JSON 编解码怪癖、push 后回拉与游标语义）。
- **FR-6 上传后端**：`/upload` 开关/类型/大小/限流/文件名/GitHub 后端（多 token 多 repo 随机、CDN 改写）/本地后端（落盘到可配置目录并返回静态 URL）/S3 后端（手写 SigV4 PUT）。
- **FR-7 图床上传器**：库形式提供 12 种非 formCustom 上传器（default 即 API 后端客户端），签名与 URL 规则按背景事实逐家实现，凭证从显式参数/环境变量/配置文件读取，不内置任何凭证。
- **FR-8 分享**：创建/列举/删除/公开访问/解锁全套；密码 PBKDF2 与 cookie/JWT 细节、过期与配额、CSP 与净化、密码门与页脚中文文案、410/404/计数语义按事实复刻。
- **FR-9 市场**：公开列表/详情/install，作者发布/PATCH/DELETE/me，管理员 pending/approve/reject；全部校验常量、版本十进制自增、slug 唯一 409、分页排序、限流、通知联动按事实复刻。
- **FR-10 表情与通知**：emoji 全套端点（magic bytes、100 上限条件插入、资产缓存头与 manifest 结构、级联删除）；notifications 五端点。
- **FR-11 爱发电**：webhook（可选 path token、只信订单号重查、静默 200、幂等发 Pro）与手动 activate；未配置时 503/静默 200 的行为按事实复刻；功能开关默认关闭。
- **FR-12 MCP**：stdio JSON-RPC 2.0，13 工具同名同 schema；选项清单返回字面值（主题/11 色/3 字体/5 字号/6 legend/5 标题样式/5 行距/5 块距/3 链接色/3 引用背景/10 代码块主题/AI 服务清单/扩展说明/渲染器选项）与原版逐字一致。
- **FR-13 前端资产管线**：提供在 WSL（podman node:22-alpine）中从本地源树构建 dist 的脚本（pnpm 11、依赖与 pnpm store 放 `/mnt/ai`、必要时 npm 镜像源），构建期环境变量使 API 指向同源（`VITE_MD_API_URL` 为空同源、`VITE_UPLOAD_VIA_API=true` 等，实施前须先核实 web 的 env/vite 默认值），产物哈希清单随仓库记录；FastAPI 托管 dist 并提供 SPA fallback；WTFPL 署名与版本声明随产物保留。
- **FR-14 可配置性**：全部环境变量名与原版对齐（GITHUB_CLIENT_ID/SECRET、JWT_SECRET、APP_URL、AFDIAN_*、UPLOAD_*、ADMIN_GITHUB_LOGINS 等），另加 Python 侧新增项（SQLite 路径、本地存储目录/基础 URL、S3 区域/端点/桶/凭证）；提供 `.env.example`；缺失关键凭证时相关功能优雅禁用，不影响其余功能。
- **FR-15 可观测与安全**：请求日志、启动时配置体检（哪些功能启用）；安全头（分享页 CSP、nosniff 等）；密码/密钥不入库不入日志。

## Non-Functional Requirements

- **NFR-1 运行时**：CPython 3.14（`requires-python = ">=3.14"`），纯 Python 包（scikit-build-core 声明 wheel.packages/build-dir/minimum-version，不写 cmake 段）；Windows 10 与 Linux（WSL）双平台可运行，测试不硬编码路径分隔符。
- **NFR-2 依赖克制**：运行期依赖限定为 fastapi、uvicorn、python-multipart、markdown-it-py、nh3、PyJWT、httpx、pyyaml、mcp（官方 Python SDK）；S3/七牛/又拍/Cloudinary 签名全部标准库手写，不引入 boto3/cryptography；开发依赖 pytest/pytest-cov/ruff/build。新增依赖须在 tasks.md 对应任务中说明理由。
- **NFR-3 测试覆盖**：单元测试覆盖率整体 ≥80%，渲染核心、同步 LWW、限流、签名、分享密码/净化等关键模块 ≥90%；全部用例通过无回归；黄金样例以源仓库 TS 测试与手工特征文档为基准。
- **NFR-4 契约可审计**：每个模块在 docstring 或模块注释中标注对拍的上游文件路径（如 `# upstream: apps/api/src/db.ts`）；关键魔数集中为常量并注释来源行号；关键算法附已知答案测试向量。
- **NFR-5 可移植资产**：主题 CSS 等静态资产原样复制（不重写），随包安装；前端 dist 不强制入库（由脚本构建到应用内资产目录，`.gitignore` 规则在实施时确定），README 写清一键构建步骤。
- **NFR-6 性能不劣化基线**：单篇 100KB Markdown 渲染（含全部扩展短样例）P95 < 500ms（本机 Windows，纯库调用）；同步 push 100 文档批处理 < 1s（SQLite 本地）；该指标为非强制 CI 门槛，以基准脚本记录为准。

## Constraints

- **Technical**：
  - 仓库硬约束：禁止 `from __future__ import annotations`（须配 AST 守护测试）；文件名 kebab-case 纯英文；Markdown/YAML frontmatter 规范；不得创建无主根目录文件；Python 代码须兼容 3.14 语法（类型注解直接用内置泛型，不用 PEP 585 顾虑）。
  - PATH 被裁剪：自动化脚本中 Python 用全路径，WSL 调用用 `wsl.exe` 全路径；不得假设 node/python 在 PATH。
  - 主机 C/D 盘空间紧张：Node 构建的依赖、store、中间产物放 `/mnt/ai`（须先验证挂载有效：mount 表存在且条目数 >0），代码工作在 `d:\AI`。
  - D1 SQL 方言=SQLite：`ON CONFLICT`、整数 epoch、`RETURNING`（SQLite ≥3.35）可直接用；无 D1 的 `?` 绑定 100 参数限制（Python sqlite3 上限 32766/999 版本相关，仍保留分块常量以记录契约）。
- **Business**：上游 WTFPL v2 要求保留许可声明；复刻品不得使用 doocs 官方名义分发；不得内置官方运营凭证。
- **Dependencies**：前端构建依赖外网（node:22-alpine 镜像、npm 源），在 WSL/podman 中完成；GitHub OAuth 回调需要公网可达地址（本地可用 127.0.0.1 手工测，完整链路需部署者自备）；Python 依赖须有 Python 3.14 兼容 wheel（实施时锁定版本）。

## Assumptions

- A1：源树 `d:\AI\.chaos\libs\md` 为 v2.1.x 主线代码（MCP 2.1.1/md-cli 2.1.3 为包内独立版本号），实施时所有契约以磁盘源码逐行对拍为准，本 spec 中的数字若与磁盘冲突以磁盘为准。
- A2：WSL podman 可拉取 node:22-alpine（或已有镜像）；若拉取失败，回退方案为拉取 `doocs/md:latest-assets` 镜像从 `/app/assets` 提取官方 dist（版本可能与本地源略有差异，须在交付说明中记录）；两方案都失败时暂停并请用户裁决（安装 Node for Windows 或手工放置 dist）。
- A3：前端构建期环境变量足以实现同源指向而无需改源码；若核实后发现必须改源码，以最小补丁（patches/ 目录 + 脚本应用）实现并在 tasks.md 与评审中披露。
- A4：mermaid/plantuml/infographic/KaTeX 的最终渲染仍在浏览器/MCP 消费端完成，Python 侧只负责产出与原版一致的占位/容器 HTML（含 `data-language-pending`、图表代码内容与主题模式标记）。
- A5：`mp`（公众号）上传器的调用者自带有效 appID/appsecret 且出口可访问微信 API；本地无凭证时不进行在线验证，仅以 httpx mock 做契约测试。
- A6：MCP Python SDK（`mcp` 包）在 Python 3.14 上有兼容发行版；若无，则按 MCP 规范用标准库手写最小 stdio JSON-RPC 传输层（须在任务中回退说明）。

## Acceptance Criteria

### AC-1：包骨架与仓库工程门禁

- **Type**: `rule`
- **Given**：在 `apps/doocs-md-py` 完成骨架后
- **When**：执行 wheel 构建、可编辑安装、`mdpy --help`、ruff、AST 守护与文件名校验
- **Then**：`python -m build` 成功产出 wheel；`mdpy --help` 列出 5 个子命令；AST 守护测试能对含 `from __future__ import annotations` 的样例变红；全部文件名通过 kebab-case 纯英文校验；pyproject 含 scikit-build-core ≥0.9 三段必需声明
- **Pass Condition**：上述命令全部退出码 0；产物中不含 `__future__` 导入；应用目录无中文文件名
- **Evidence**：命令输出日志、`tests/test_no_future_annotations.py`、pyproject.toml 内容、文件名检查脚本输出

### AC-2：SQLite 迁移与 D1 八迁移语义等价

- **Type**: `rule`
- **Given**：空 SQLite 数据库
- **When**：执行 `mdpy migrate`（或应用初始化自动迁移）
- **Then**：建成 users/documents/settings/afdian_orders/sync_rate_limits/shares/share_rate_limits/marketplace_items/marketplace_rate_limits/notifications/emoji_packs/emoji_items 全部表与索引/CHECK，种子存在 `system-default` 包；重复执行幂等不报错
- **Pass Condition**：以 `sqlite_master` 与 PRAGMA 核对，表/列/类型/默认值/唯一索引/CHECK 约束与 `apps/api/migrations/0001-0008` 逐张等价（一份映射清单测试逐项断言）；种子行存在
- **Evidence**：`tests/test_migrations.py`、迁移 SQL 移植清单（含上游文件锚点注释）

### AC-3：同步端点 LWW/游标/限额契约

- **Type**: `rule`
- **Given**：TestClient + 预置 free/pro 用户与 JWT
- **When**：按场景矩阵执行 pull/push（新旧时间戳双向覆盖、墓碑、设置编解码怪癖、100/80/8MiB/各字段尺寸超限、200/400/2000/4000 配额、30/300 频率、缺 Bearer/坏 token、无用户）
- **Then**：状态码与错误体字符串（`error/field/max/plan/limit/retryAfterSec/upgradeRequired`）逐场景等于 Hono 版；LWW 决胜、游标前进/回拉语义一致
- **Pass Condition**：覆盖背景事实中同步契约全部条款的参数化测试 100% 通过
- **Evidence**：`tests/test_sync_contract.py`（场景表）、失败响应快照

### AC-4：渲染核心全部元素与 12 扩展的 DOM 等价

- **Type**: `rule`
- **Given**：从上游 TS 测试用例与特征文档整理的黄金样例集（front-matter、17 类 marked 元素规则、12 扩展、图片尺寸/legend/cite/diff 代码/Mac/行号/hr 三变体/列表前缀）
- **When**：调用 Python `render_markdown` 并将输出与预期 HTML 做空白归一化后的 DOM 结构对比（标签树/属性/类名/文本节点）
- **Then**：每个样例结构等价；mermaid/plantuml/infographic 输出与原版同形占位容器；KaTeX 定界与 `stripBreakBeforeInlineKatex` 行为一致；DOMPurify 等价净化（白名单、`mp-common-profile` 放行、图表占位保护、危险标签/属性清除）逐 case 通过
- **Pass Condition**：黄金样例集全部通过；净化 XSS 样例集（脚本/事件/伪协议/`</style>`/危险 @import）全部被拦
- **Evidence**：`tests/golden/` 样例与 `tests/test_render_*.py`、`tests/test_sanitize.py`

### AC-5：主题 CSS 装配与运行时 CSS 处理等价

- **Type**: `rule`
- **Given**：四主题 CSS 已原样入资产，渲染选项覆盖默认/自定义组合
- **When**：生成装配后 `<style>` 内容
- **Then**：变量块字面量（含 blockquoteBackground=default 不声明的特例）、heading 三样式 CSS、缩进/两端对齐规则、var() 迭代替换（fallback/嵌套/未解析保留）、calc() 四类运算与 round(4 位) 行为、`</style` 转义与原版逐字对拍；非白名单 hljs URL 抛错
- **Pass Condition**：CSS 黄金字符串测试（含 options 矩阵）全部通过；白名单外 URL 断言异常
- **Evidence**：`tests/test_css_assembly.py`

### AC-6：GitHub OAuth 与 JWT 账号契约

- **Type**: `rule`
- **Given**：httpx MockTransport 模拟 GitHub 两接口；配置/未配置 OAuth 两种环境
- **When**：走 /auth/github → callback → /me 全链路，并构造非法 state/错误码/换 token 失败/拉用户失败/未配置场景；另用独立生成的已知 HS256 token 验证互认
- **Then**：cookie 属性（httpOnly/Lax/600s/path）、state 比对与清理、redirect 白名单（单标签 `*` 不跨点、扩展 origin 放行）、hash 回传参数名、`User-Agent: md-api`、错误分支全部与 auth.ts 一致；未配置时端点行为可预期（可配置 503/重定向信息），本地模式不受影响
- **Pass Condition**：全部分支测试通过
- **Evidence**：`tests/test_auth.py`

### AC-7：分享全生命周期契约

- **Type**: `rule`
- **Given**：free/pro 用户、受密码保护与公开两种分享
- **When**：创建（配额 2/天/强制 1d/pro 四档过期/2MiB/postId 64/三种密码模式/密码长度 4–64/自动 8 字符表）、列举与删除（pro 门禁）、公开访问（404/410/计数/页脚/CSP 头与 meta/密码门）、解锁（正确/错误/20 次限流/JSON 与表单双形态/cookie path 精确/访问 JWT 24h 与到期夹取）
- **Then**：响应码、响应体关键字、cookie 属性、CSP 字面量、PBKDF2 串格式与常量时间比较、shareId 推导（sha256 前 12 hex）全部与 share*.ts 一致
- **Pass Condition**：场景矩阵全绿；PBKDF2 串可被 Node 版校验逻辑互验（用已知盐/密码/迭代的已知答案向量）
- **Evidence**：`tests/test_share_contract.py`

### AC-8：API 上传链路契约

- **Type**: `rule`
- **Given**：开关切换、GitHub/本地/S3 三种后端、匿名/free/pro 三身份
- **When**：POST /upload（无 file/非 image/0 字节/超 5MiB/限流 60/120/300/扩展名规则各分支/GitHub API 成功与失败/CDN 改写/本地落盘/S3 PUT）
- **Then**：状态码与 `{error[,maxBytes,message,url]}`、对象键与目录日期格式、成功后才计数、匿名降级口径与 upload*.ts 一致
- **Pass Condition**：参数化测试全绿；SigV4 PUT 使用 AWS 官方测试向量验证签名
- **Evidence**：`tests/test_upload_api.py`

### AC-9：13 图床 Python 上传器协议等价

- **Type**: `rule`
- **Given**：各上传器与 httpx mock（或录制的请求断言）
- **When**：对 github/qiniu/aliOSS/txCOS/minio/s3/mp/r2/upyun/telegram/cloudinary/default 逐家构造上传
- **Then**：HTTP 方法/URL/头/体字段/签名串与 providers.ts 逐家一致：七牛凭证（HMAC-SHA1+safe64+deadline）、S3 五家预签名（endpoint/forcePathStyle/expiresIn=300/返回 URL 优先级）、mp（token 缓存键、<1MiB 分流、字段名 media）、upyun（签名串拼接与 X-Date）、telegram（两步与最大尺寸选择）、cloudinary（字典序签名/无签名 preset/自定义 domain）；返回 URL 拼接规则逐家断言
- **Pass Condition**：每家至少 1 条签名已知答案或请求录制断言通过；default 上传器对接 API /upload 链路
- **Evidence**：`tests/test_uploaders.py`

### AC-10：市场端点校验/状态机/限流/通知联动契约

- **Type**: `rule`
- **Given**：普通作者/另一作者/admin/访客四类身份
- **When**：执行 themes/components 的 list（分页 20/50、sort、q 截断）、detail 可见性、install 计数、发布（slug/name/cover/颜色/CSS 200KiB 与 @import/外链/组件 50KiB/PascalCase/props/示例 32KiB 全拒绝分支、5/30/无限限流）、PATCH（作者校验、版本十进制 +0.0.1 三进位场景、重置 pending）、DELETE、admin pending/approve/reject（pending 守卫、404、slug 唯一 409）
- **Then**：状态码、错误字符串、版本结果、published_at/status/reject_reason 变化、通知收件人（管理员/作者）与 marketplace*.ts 一致
- **Pass Condition**：拒绝条件全集逐条有测试
- **Evidence**：`tests/test_marketplace.py`

### AC-11：表情资产与通知端点契约

- **Type**: `rule`
- **Given**：用户包与系统包
- **When**：执行 emoji GET/me(自动建包)/PATCH/items 上传（4 类型/4 种 magic bytes 伪造/5MiB/第 101 个并发条件插入/级联删除/缓存头）与 notifications 五端点（分页 30/50、属主 404、幂等已读、read-all、删除）
- **Then**：错误码（mime_mismatch/item_limit_reached 409 等）、对象键、ETag/nosniff/max-age、manifest 字段顺序与 URL 编码、通知 payload 兜底解析与 emojis.ts/notifications-db.ts 一致
- **Pass Condition**：测试全绿
- **Evidence**：`tests/test_emoji.py`、`tests/test_notifications.py`

### AC-12：爱发电 webhook 与手动激活契约

- **Type**: `rule`
- **Given**：配置/未配置爱发电、合格/不合格/已处理订单、remark 匹配/不匹配
- **When**：POST /webhooks/afdian[/:token] 与 POST /sync/activate
- **Then**：path token 403；非订单/缺 out_trade_no/status≠2/解析不出登录名一律静默 200；签名 md5 拼接与 query-order 请求体正确；31 天/月续费与 max(now,到期) 语义、幂等返回、remark 大小写不敏感比对、未配置 503 等全部行为与 afdian.ts/webhook.ts/activate.ts/plan.ts 一致
- **Pass Condition**：MockTransport 下全分支通过
- **Evidence**：`tests/test_afdian.py`

### AC-13：MCP Server 13 工具契约

- **Type**: `rule`
- **Given**：stdio 启动 MCP 服务
- **When**：发 initialize/tools/list/tools/call
- **Then**：13 个工具同名；`render_markdown` 入参 19 个且默认值/正则约束与原版一致，返回 `{html, frontMatter, readingTime:{words,minutes}}`；12 个清单工具返回的字面值（主题作者署名、11 色、字体栈、字号、legend、标题样式、行距/块距、链接色/引用背景、10 hljs URL、AI 服务 endpoint+models、扩展说明、选项表）与 config-options.ts/ai-service-options.ts/index.ts 逐项一致
- **Pass Condition**：tools/list 快照测试 + render 调用测试 + 清单抽样比对全部通过
- **Evidence**：`tests/test_mcp_server.py`

### AC-14：mdpy CLI 与 Web 同源托管

- **Type**: `rule`
- **Given**：已构建 dist 资产
- **When**：执行 `mdpy render`（文件与 stdin 两形态）、`mdpy serve`（默认 127.0.0.1、端口占用自动换端口、SPA fallback、同源 API）、`mdpy upload`、`mdpy mcp`、`mdpy migrate`
- **Then**：浏览器访问首页返回原版 index.html 且其中 API 调用同源成功（TestClient 走完 push→pull→分享页生成链路）；非资产路径回退 index.html；静态资源 200 且带合理缓存头；CLI 退出码语义正确（失败非 0）
- **Pass Condition**：端到端测试通过；serve 不绑 0.0.0.0（除非显式配置）
- **Evidence**：`tests/test_cli.py`、`tests/test_serve_e2e.py`

### AC-15：前端 dist 可重复构建且零源码修改

- **Type**: `rule`
- **Given**：WSL/podman 环境，源树 `d:\AI\.chaos\libs\md`
- **When**：执行构建脚本（node:22-alpine + pnpm 11，store/临时目录在 /mnt/ai）
- **Then**：产出 dist 目录（index.html + hashed assets），构建环境变量使 API 同源；构建日志与产物文件清单（含 sha256）固化；应用内保留 WTFPL LICENSE 与上游版本声明；除脚本注入的构建期 env 外前端源码零 diff（`git status` 干净或补丁清单为空/经批准）
- **Pass Condition**：脚本可重复执行成功；产物由 FastAPI 托管且首页加载 200；同源 API 路径在构建产物配置中得到核实
- **Evidence**：`scripts/build-web-dist.*`、构建日志、哈希清单、`.env.example` 与资产目录 LICENSE

### AC-16：测试覆盖率与回归门禁

- **Type**: `rule`
- **Given**：全部实现完成
- **When**：运行完整 pytest（含覆盖率）与 ruff
- **Then**：总覆盖率 ≥80%，render/server(同步/分享/市场/上传/爱发电)/uploaders/mcp 关键模块 ≥90%；无失败用例；ruff 无告警
- **Pass Condition**：覆盖率报告数字达标并归档
- **Evidence**：pytest --cov 报告、CI/本地命令输出

### AC-U1：渲染保真度综合评价

- **Type**: `rubric`
- **Dimension**：在复杂组合文档（多级标题/表格/代码 diff/数学/图表/脚注/alert 嵌套/自定义组件/emoji/长文 5000 字）上，Python 输出与原版浏览器渲染 DOM 的语义等价程度与微信兼容约束（行内样式、类名钩子、无脚本）保持程度
- **Scale**: 1-5
- **Anchors**: 1 = 多个扩展不可用或结构明显不同；3 = 主要扩展可用但存在可察觉的结构/类名差异且影响微信呈现；5 = 全部组合用例归一化 DOM 等价、微信端关键样式钩子无缺失
- **Pass Threshold**: >= 4
- **Evidence**：复杂文档对拍报告（review 阶段用源站/构建产物人工或 DOM 比对取证）

### AC-U2：API 契约抽查一致性

- **Type**: `rubric`
- **Dimension**：独立评审者随机抽取至少 15 个端点场景，直接对照 `apps/api/src` TS 源码核对 Python 实现的行为一致性（含错误码、边界数值、副作用顺序）
- **Scale**: 1-5
- **Anchors**: 1 = 抽查中发现 ≥3 处契约偏离；3 = 发现 1–2 处非关键偏离；5 = 15 个场景零偏离且魔数来源均可追溯
- **Pass Threshold**: >= 4
- **Evidence**：review.md 抽查记录表

### AC-U3：代码质量与可维护性

- **Type**: `rubric`
- **Dimension**：模块边界清晰度、上游锚点注释完备度、常量集中与命名一致性、重复代码控制、配置与密钥安全
- **Scale**: 1-5
- **Anchors**: 1 = 魔数散落、无来源注释、难审计；3 = 结构合理但部分模块缺锚点或存在重复；5 = 模块划分清晰、每个契约模块可定位上游文件、无硬编码凭证
- **Pass Threshold**: >= 4
- **Evidence**：代码审查、模块 README/docstring

### AC-U4：文档与可运维性

- **Type**: `rubric`
- **Dimension**：应用 README（快速开始/构建 dist/配置项/本地模式）、工程架构文档（模块-上游映射）、`.env.example`、`apps/AGENTS.md` 路由登记的完整与准确程度
- **Scale**: 1-5
- **Anchors**: 1 = 新人无法按文档跑起来；3 = 能跑但构建/配置有缺口；5 = 按文档从零到可用（含 dist 构建）全程无卡点
- **Pass Threshold**: >= 4
- **Evidence**：README、docs/、AGENTS.md 变更、评审者按文档实操记录

## Open Questions

- [x] Q1：前端构建期 env 是否能做到零源码补丁同源指向（A3）——**已定论：可零补丁实现**。T2 核实 vite `loadEnv` 以进程环境变量优先于 `.env` 文件，故以 `SERVER_ENV=NETLIFY` + 清空 `VITE_MD_API_URL`/`VITE_SYNC_API_URL` 构建即得同源指向，未改任何前端源码（TR-2.2 证据；构建脚本与依据见 [build-web-dist.md](../../../apps/doocs-md-py/docs/build-web-dist.md)）。
- [x] Q2：Python `mcp` 官方 SDK 对 3.14 的兼容性（A6）——**已定论：不兼容，改手写最小传输层**。T18 实测 `mcp` 2.3.0 不可用于 Python 3.14，遂以手写 stdio JSON-RPC 2.0 替代，并从依赖中删除 `mcp`（登记为差异 CD-21）。
- [x] Q3：dist 分发方式（入库 or 脚本构建产物 gitignore）——**已定论：不入库**。产物落 `src/doocs_md_py/assets/web-dist/` 且被 `.gitignore` 排除，仅 `.gitkeep`/`MANIFEST.sha256`/`NOTICE` 入库；fresh clone 后按脚本一键构建（见 [build-web-dist.md](../../../apps/doocs-md-py/docs/build-web-dist.md)）。
- [x] Q4：md-cli 的 dcloud（uniCloud）上传是否在 Python CLI 中复刻——**已定论：已复刻并登记**。签名算法完成逆向，`dcloud` 上传器入库，图床总数记为 14 家（上游 13 家 + dcloud，见 [contract-differences.md](../../../apps/doocs-md-py/docs/contract-differences.md) §4.3），未发现该服务不可用。
