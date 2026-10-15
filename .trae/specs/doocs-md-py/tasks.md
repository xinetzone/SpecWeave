# doocs/md Python 3.14 全功能复刻（doocs-md-py）- 实施计划

> 任务状态机：pending → in_progress → completed（/blocked/cancelled）。每任务完成必须填 Completion Evidence（rule 给命令/输出，rubric 给分数+理由+证据）。全部代码路径锚点以源树 `d:\AI\.chaos\libs\md` 为准。

## Task 1: 应用骨架与工程门禁

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Completion Evidence**（2026-10-14）:
  - TR-1.1 ✅ `.venv`（Python 3.14.7/pip 25.3）`pip install -e .[dev]` 成功；`mdpy --help` 与 `python -m doocs_md_py --help` 均退出 0 且列全 render/serve/upload/mcp/migrate；console_script `mdpy.exe` 可用。实测依赖：fastapi 0.143.0、markdown-it-py 4.2.0、nh3 0.3.7、pyjwt 2.15.1、httpx 0.28.1、**mcp 2.3.0（Python 3.14 有 wheel，A6/Q2 关闭：采用官方 SDK，无需手写 stdio JSON-RPC）**、pyyaml（传递）、uvicorn/python-multipart（随 serve 路径已装）。mcp 传递拉入 cryptography 50.0.2（业务代码不 import，签名仍全部标准库，差异登记 T21 contract-differences）。
  - TR-1.2 ✅ `python -m build --wheel` 产出 `doocs_md_py-0.1.0-py3-none-any.whl`（scikit-build-core 1.1.1 隔离构建，无 CMake）；wheel 含 cli.py/py.typed/assets 包数据/NOTICE（自动进 dist-info/licenses）/entry_points.txt。
  - TR-1.3 ✅ AST 守护红相：注入 `_redline_probe.py` 后测试失败并精确报路径，删除后绿相通过；`ruff check src tests` 零告警；pytest 12/12 通过。
  - 骨架文件：pyproject.toml、src/doocs_md_py/{__init__,__main__,cli}.py、tests/{test_cli,test_no_future_annotations}.py、.gitignore、.env.example、NOTICE、py.typed、assets/web-dist/{.gitkeep,NOTICE}。
- **Description**:
  - 创建 `apps/doocs-md-py/`：`pyproject.toml`（仿 travel-planner：scikit-build-core≥0.9、wheel.packages=["src/doocs_md_py"]、build-dir、minimum-version="0.9"、requires-python>=3.14、依赖按 NFR-2 锁定主版本、scripts `mdpy = "doocs_md_py.cli:main"`、pytest/ruff 配置）、`src/doocs_md_py/` 包骨架（cli.py 用 argparse 建 render/serve/upload/mcp/migrate 五子命令占位，全部返回明确未实现提示）、`tests/`、`scripts/`、`docs/`、`.gitignore`、`NOTICE`（WTFPL v2 上游署名与版本声明）、`.env.example` 占位。
  - 写 `tests/test_no_future_annotations.py`（AST 扫描 src/，出现 `from __future__ import annotations` 即红）。
  - 用全路径 Python（`C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe`）建 venv 于 `/mnt/ai`（WSL）或应用内 `.venv-windows` 视实施环境，安装可编辑包与 dev 依赖并锁定版本（写 requirements-lock 或 pyproject 下限+实测版本记录到 docs）。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: `python -m pip install -e .[dev]` 成功；`mdpy --help` 退出码 0 且含五个子命令名；证据：命令输出。
  - `rule` TR-1.2: `python -m build` 产出 wheel；wheel 内含 doocs_md_py 包；证据：dist/ 产物清单。
  - `rule` TR-1.3: 在临时样例中写入 `from __future__ import annotations` 时 AST 守护测试失败、移除后通过；ruff 对 src 零告警；证据：pytest 输出。
- **Notes**: 依赖 wheel 的 3.14 可用性在此任务实测；若某依赖无 3.14 wheel，按 A6 同策略记录并选替代。

## Task 2: 前端 dist 构建管线（高风险先验）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None（与 T1 并行；是后续 T20/E2E 的前置）
- **Completion Evidence**（2026-10-14）:
  - TR-2.1 ✅ `scripts/build-web-dist.sh`（WSL openKylin + podman）+ `build-web-dist.ps1`（Windows 入口）：node:22-alpine（经 docker.m.daocloud.io 拉取，Docker Hub 直连超时）、`--network slirp4netns`（rootless 无 pasta）、rsync 源树到 WSL 原生 ext4（规避 drvfs 小文件 I/O）、pnpm store 具名卷 md-pnpm-store、npmmirror。实测 node v22.23.3 / pnpm 12.6.0（corepack 按 packageManager 自动获取；注：计划中 pnpm@11 更正为上游实际 12.6.0）、frozen-lockfile 通过供应链策略（1382 条目）、vite 8.3.3 7381 模块 17.72s；产物 325 文件/12MB（index.html + static/js|css hashed + favicon + assets/mpmd/upload）。可重复性：第二次执行由 store 卷复用（日志存档）。
  - TR-2.2 ✅ 产物 grep `md-api.doocs.org` 命中 0；index.html 资源前缀 `/static/...`（SERVER_ENV=NETLIFY → base=/，非 /md/）；构建 env 清空 VITE_MD_API_URL/VITE_SYNC_API_URL（同源）+ 三个 UI 开关；源树 `git status --porcelain` 空（零补丁，commit 1bdad48d20048bddc8d32afb1b75a6475169f163）。**登记项**：NETLIFY 变体 index.html 含上游 Google Analytics gtag（G-7NZL3PZ0NK），T21 文档须说明并提供可选移除策略。
  - TR-2.3 ✅ `MANIFEST.sha256`（上游 commit/构建时间/镜像/pnpm/registry/env + 全文件 SHA256）+ 随附 LICENSE（WTFPL v2）与资产目录 NOTICE。
  - 已知无害告警：容器内无 git，simple-git-hooks postinstall 刷 git not found（退出码仍 0，wxt prepare 正常）；workerd 二进制校验告警（仅影响容器内 wrangler 本地开发，vite build 不依赖）。
- **Description**:
  - 先读 `apps/web/.env*`、`apps/web/vite.config.*`、`apps/web/wxt.config.*`、`apps/web/src/services/account/config.ts` 及 sync client 的 env 读取处，核实零源码补丁同源方案（Q1/A3）：需要注入的构建期变量至少 `SERVER_ENV=NETLIFY` 等价的普通 web 构建、`VITE_MD_API_URL=""`（同源）、`VITE_UPLOAD_VIA_API=true`、UI 开关（VITE_SYNC_UI_ENABLED/VITE_ACCOUNT_UI_ENABLED）的取值核实。
  - 写 `scripts/build-web-dist.sh`（在 WSL openKylin/podman 内执行；先验证 `/mnt/ai` 挂载条目数>0）：用 node:22-alpine 容器挂载源树（只读）与 `/mnt/ai/md-build`（pnpm store + 输出），corepack/pnpm@11，必要时 npm 国内镜像，`pnpm install --frozen-lockfile`（失败则记录并退普通 install）后执行 h5 构建；产物输出到 `apps/doocs-md-py/src/doocs_md_py/assets/web-dist/`。
  - 生成 `scripts/build-web-dist.ps1`（Windows 侧调用 wsl.exe 全路径）、产物 SHA256 清单文件与构建说明（含 Node/pnpm 版本、镜像源、env 值、上游 commit 哈希 `git -C 源树 rev-parse HEAD`）。
  - 回退预案（A2）写进 docs：拉取 `doocs/md:latest-assets` 提取 `/app/assets`。
  - 静态资源服务路径约定（供 T19）：资产目录常量 + 不存在时的启动报错文案。
- **Acceptance Criteria Addressed**: AC-15
- **Test Requirements**:
  - `rule` TR-2.1: 构建脚本在干净 /mnt/ai 工作目录可重复执行完成，产物含 index.html 与 hashed JS/CSS 资产；证据：两次执行日志、dist 文件清单。
  - `rule` TR-2.2: 产物中能 grep 到同源 API 调用基址（空 baseURL 行为）或构建 env 记录证明其同源；前端源树零修改（git status 干净，或补丁清单经用户批准）；证据：grep 结果、git status、env 记录。
  - `rule` TR-2.3: SHA256 清单生成且 NOTICE/LICENSE 随资产保留；证据：清单文件内容。
- **Notes**: 源树在 D 盘 drvfs，pnpm store 必须放 /mnt/ai 原生路径或容器内卷，避免海量小文件走 9p；若网络拉镜像失败，先尝试本机已缓存镜像（podman images 查证）。

## Task 3: SQLite 迁移与持久化基座

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T1
- **Completion Evidence**（2026-10-14）:
  - 产物：`server/migrations/0001-0008.sql`（原样移植，仅加 upstream 锚点注释）、`server/migrations/__init__.py`（注册表）、`server/db.py`（connect WAL/FK/Row、apply_migrations 幂等应用器 + `_migrations` 表、upsert_user/get_user_by_id/count_active/count_stored/D1_IN_ID_CHUNK=99 分块/list_existing/pull_changes/push_changes）、`server/types.py`（SyncDocument/SyncSetting/SyncHistoryEntry/UserRow，camelCase 契约映射）。
  - TR-3.1 ✅ tests/server/test_migrations.py 17 用例：13 表（含 _migrations）/10 显式索引/列默认值/0002 plan 列/0005 sample_markdown/CHECK（kind/owner 互斥/size>0）/FK 级联/system-default 种子（含 1785547610000 字面量）/coolapk 清除/8 迁移登记有序/文件库重开幂等。
  - TR-3.2 ✅ tests/server/test_db_lww.py 23 用例：LWW `>=`（含相等拒绝）、游标严格大于、回拉 now-1 仅含本批落库行（同步协议"先 pull 后 push"语义，db.ts:243 注释）、墓碑计数与复活、设置编解码五分支（字符串/null/非字符串 JSON 重序列化/坏 JSON→null/非 ASCII 不转义）、history 损坏回退 [] 与遗留字符串时间戳、多用户隔离、99 分块去重保序。
  - 集成：`mdpy migrate [--db]` 已接线（默认 data/doocs-md-py.db，自动建目录、二次执行幂等），CLI 测试覆盖。
  - 全量 50 测试通过、ruff 零告警。
- **Description**:
  - 逐文件移植 `apps/api/migrations/0001-0008` 为包内迁移 SQL（保持原始 DDL，仅调整 D1 无关差异；SQLite 原生支持 ON CONFLICT/CHECK/整数时间戳；保留全部索引名与列默认值；种子时间戳 1785547610000 原样）。
  - 实现 `server/db.py`：连接工厂（WAL、外键开、row_factory）、用户版本表 `_migrations` 幂等应用；`server/db/repositories` 或同文件实现 upsertUser/getUserById/countActive/countStored/listExisting（99 分块常量保留）/pullChanges/pushChanges（严格按 db.ts：LWW 条件为 existing.ts >= client 则跳过、设置 JSON.stringify(value ?? null) 语义、rowToSetting 的非字符串 JSON 回退序列化/解析失败 null、push 后 pull(now-1) 回拉、游标 now）。
  - 时间统一 epoch ms int；全部 SQL 参数化。
- **Acceptance Criteria Addressed**: AC-2, AC-3（持久化部分）
- **Test Requirements**:
  - `rule` TR-3.1: 空库迁移后对象清单（表/索引/CHECK）与 8 个上游 SQL 的映射清单逐项断言一致，种子 system-default 存在；重复迁移幂等；证据：test_migrations.py。
  - `rule` TR-3.2: LWW/游标/回拉/墓碑/设置编解码怪癖按 db.ts 场景逐条参数化测试通过；证据：test_db_lww.py 输出。
- **Notes**: 上游锚点注释必须逐函数标注（`# upstream: apps/api/src/db.ts:L173` 等）。

## Task 4: FastAPI 骨架、配置与 CORS

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T1
- **Completion Evidence**（2026-10-14）:
  - `server/config.py`：dataclass + os.environ（不引白名单外的 pydantic-settings），全量 Env 字段 + Python 新增 SQLITE_PATH/STORAGE_LOCAL_*；upload 默认值 1:1（bucketio/img0..19/main/CDN 默认开/5MiB/限流 60·120·300）；local 后端零配置 ready 判定。
  - `server/origin.py`：origin.ts 1:1（escapeRegex、`[^./]+` 单标签通配、扩展协议三族、defaultOrigin 首字面量、resolveRedirect 白名单回退）。
  - `server/app.py`：create_app 工厂 + 自写 CORS HTTP 中间件复刻 Hono cors（凭证 true、方法 GET/POST/PATCH/DELETE/OPTIONS、头 Authorization/Content-Type、maxAge 86400、预检 204、不命中不加头继续、Vary: Origin）；`GET /` → `{name:'md-api',ok:true}`；serve() 入口留待 T19 接线静态托管。
  - `server/httputil.py`：client_ip（XFF 链首→对端，注释 CF-Connecting-IP 口径）、error_response（`{"error": msg}` 统一错误体，extra 支持 OAuth2 error_description）。
  - TR-4.1 ✅ test_cors.py 9 用例 + test_origin.py 21 用例：精确/单标签不跨点/后缀攻击/localhost 端口/扩展 origin/Netlify 预览/多通配/CSV/预检全头/拒绝无 CORS 头/无 Origin 同源。
  - TR-4.2 ✅ test_app.py 8 用例：健康检查、缺省云端禁用与 local 上传可用、env 覆盖、管理员大小写不敏感、IP 解析。全量 81 测试通过、ruff 零告警。
  - 偏差登记：缺省 UPLOAD_ENABLED 上游为 false（仅 "true"/"1" 开启），Python 版默认 true（local 后端零配置可用），env 可关；待写入 contract-differences.md（T21）。
- **Description**:
  - `server/config.py`：pydantic Settings 映射全部环境变量（GITHUB_CLIENT_ID/SECRET、JWT_SECRET、APP_URL、AFDIAN_* 六个、UPLOAD_* 九个、ADMIN_GITHUB_LOGINS，新增 SQLITE_PATH/STORAGE_LOCAL_DIR/STORAGE_LOCAL_BASE_URL/S3_*）；与 upload-config.ts 默认值一致（默认 bucketio、img0..img19、main、CDN 默认开、5MiB）。
  - `server/app.py`：app factory、全局 CORS 中间件按 origin.ts 复刻（逗号分隔 APP_URL、单标签 `*`→正则 `[^./]+`、扩展协议放行、methods/headers/credentials/maxAge=86400、不命中回 null）、JSON 错误体工具、`GET /` 健康检查、favicon 占位（由静态资产提供）。
  - 请求 IP 解析工具（X-Forwarded-For 首项/对端 host 兜底，注释说明 CF-Connecting-IP 差异）。
- **Acceptance Criteria Addressed**: AC-6（CORS 部分）, AC-14（app 基座）
- **Test Requirements**:
  - `rule` TR-4.1: CORS 矩阵测试（精确/单标签通配不跨点/多标签拒绝/扩展 origin/凭证回显/方法头白名单）全绿；证据：test_cors.py。
  - `rule` TR-4.2: GET / 返回 `{name:'md-api', ok:true}`；缺省配置下 app 可启动且各功能禁用标志正确；证据：test_app.py。

## Task 5: 渲染核心 - front-matter 与 marked 等价渲染器（基础元素）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T1
- **Completion Evidence**（2026-10-14）:
  - `render/options.py`：IOpts/CountMessages/DiagramMessages/RenderMessages（common.ts 1:1，浅合并 merge）。
  - `render/frontmatter.py`：front-matter.ts 1:1（BOM/CRLF/`---`/`...`/`= yaml =` 围栏、`* ` 列表别名归一化、空/非对象/坏 YAML 四分支，pyyaml safe_load）。
  - `render/reading_time.py`：readingTime.ts 1:1（CJK 四范围、200 wpm、标点吞并、UTF-16 code unit 遍历忠实代理对语义）。
  - `render/html_utils.py`：escape/unescape/stripInlineHtml（html.unescape 等价 decodeHTML）。
  - `render/highlight.py`：languages.ts 结构 1:1（formatHighlightedCode 三正则/&nbsp;、splitHighlightedHtmlByLines span 栈、行号 flex 双栏、LRU 128、renderDiffCode 红绿行、Mac SVG）；语法着色 span 待 T6 决策（注册集仅 plaintext，data-language-pending 三属性完整，前端 CDN 延迟高亮链路不变）。
  - `render/renderer.py`：markdown-it-py(commonmark, breaks+html, enable table/strikethrough) 17 规则等价——heading 收集 data-heading、p 解包（figure/空/katex-only/tight/loose 首段）、codespan/list（• 与 N. 前缀、嵌套栈、start）、image（`|w`/`|wxh`、legend alt-title-filename）、link（mp.weixin 保留/href===text 纯文本/citeStatus 脚注去重）、table（section 滚动+preview-table+tr/th/td class+align 默认 left，预扫改类型跳过区间）、hr 三变体。
  - `render/markdown.py`：renderMarkdown/postProcessHtml/modifyHtmlContent（container、reading time blockquote、footnotes、addition style、mac-sign display 开关、h2 strong）；sanitize 直通占位待 T8 nh3。
  - `render/domcompare.py`：黄金样例框架（html.parser 归一化树：空白折叠、void 元素、属性排序、差异路径报告）。
  - 测试：tests/render/ 5 文件 61 用例（17 规则黄金 DOM + frontmatter 8 场景 + readingTime 8 场景 + 流水线 7 + 比较器 8），全量 142 测试通过、ruff 零告警。
  - 已知等价差异（T21 登记）：markdown-it-py 自闭合输出 `<br />`（marked `<br>`，DOM 等价）；无 info 代码块 class `language-` 与空 pending（忠实 marked 模板）。
- **Description**:
  - 通读 `packages/core/src/renderer/renderer-impl.ts`、`utils/front-matter.ts`、`utils/markdownHelpers.ts`、`utils/index.ts`、`shared/types/common.ts`，逐行对拍。
  - `render/options.py`（IOpts 等价：legend/citeStatus/countStatus/isMacCodeBlock/isShowLineNumber/themeMode/components/diagramMessages/countMessages/renderMessages/assetResolver + parseFrontMatterAndContent）。
  - `render/frontmatter.py`（与 front-matter npm 包语义一致：--- 分隔、yamlData）。
  - `render/renderer.py`：基于 markdown-it-py 定制 tokenizer/renderer 规则覆盖 heading/paragraph/blockquote/code/codespan/list/listitem/image/link/strong/em/del/table/tablecell/hr；`breaks:true`；图片 `alt|宽`/`alt|宽x高` 尺寸；legend 六值含 filename；链接 href===text 纯文本、mp.weixin.qq.com 保留、citeStatus `[n]` 收集；代码块 diff-<lang> +绿/-红、data-language-pending、Mac 三点 SVG、行号；hr 三变体；列表前缀 `N. `/`• `。
  - 建黄金样例框架：样例为 (markdown, expected_html_dom) 对，比较器做空白归一化 + DOM 结构比对（用 html.parser 标准库写小型比较器，不引重依赖）。
- **Acceptance Criteria Addressed**: AC-4（基础部分）
- **Test Requirements**:
  - `rule` TR-5.1: 基础元素黄金样例（≥25 条，含全部上述特色行为边界）全绿；证据：tests/test_renderer_basic.py 与 golden 清单。
  - `rubric` TR-5.2: 上游锚点完备与对拍忠实度；scale 1-5；anchors 1=多处臆造无锚点/3=主路径有锚点但边界缺失/5=每规则可定位 renderer-impl.ts 行号；threshold ≥4；证据：renderer.py docstring 评审抽查。
- **Notes**: 代码高亮不在服务端做（保留 language-* class + data-language-pending，由前端 hljs/CDN 接管），与 MCP 原行为一致；若 markdown-it-py 无法表达某 marked token 差异，在该规则注释中记录差异点及处置。

## Task 6: 渲染扩展批次一（markup/emoji/toc/slider/alert）

- **Status**: `completed`（T6a markup/toc/slider ✅；T6b emoji ✅；T6c alert ✅）
- **Priority**: high
- **Depends On**: T5
- **Completion Evidence**:
  - T6a（2026-10-14 完成）：`render/extensions/{markup,toc,slider}.py` 对拍 markup.ts/toc.ts/slider.ts；core ruler after text_join 收集标题；`tests/render/test_extensions_markup.py` 18 用例。
  - T6b（2026-10-14 完成）：`render/extensions/emoji.py` + `emoji_data.py`（515 条 shortcode，由 `scripts/gen-emoji-data.py` 从上游 emoji-data.ts 机械派生）；parseEmojiTag（属性序自由/自闭合或空标签/id 白名单/width clamp 1-100/align 白名单/名称边界）、行内 shortcode/legacy/asset 三语法、块级独占行 `<p>`+align、SAFE_SRC 收敛、opts.assetResolver 动态闭包；装配顺序 markup→emoji→toc→slider（emoji 行内规则 before strikethrough 先于内建 image/html_inline，块规则 before html_block）；`tests/render/test_extensions_emoji.py` 86 用例（emoji.test.ts 全部 + 50 shortcode 确定性抽样 + 未知字面 + 3:4:5/12:30:45/key:value 字面 + 行内 code 隔离）。
  - T6c（2026-10-14 完成）：`render/extensions/alert.py` + `alert_data.py`（34 变体：6 GFM+18 Obsidian+10 学术，含 octicon SVG，由 `scripts/gen-alert-data.py` 机械派生）；GFM blockquote 改造走 block/inline 之间 core ruler（首段物理行裁剪等价上游 br/text-\n splice；map 行对齐守卫拦截首行空行/非段首）、`:::` 容器块规则 before paragraph（body trim 后 block.parse、闭合残余按上游续解）；自定义名 → custom 变体无图标、标题 escapeHtml（`<b>`→`&lt;b&gt;`）、标题内联 markdown 保持字面、大小写不敏感；`tests/render/test_extensions_alert.py` 60 用例（34 变体全别名参数化 + 4 大小写 + 自定义 CJK 标题/名字 + 容器嵌套标题列表 + 未闭合/无名回退 + 围栏/段内守卫 + 硬换行裁剪）。
  - TR-6.1 证据文件按扩展拆分为 test_extensions_{markup,emoji,alert}.py（非单一 batch1 文件）；全量 306 测试绿、ruff check src/tests/scripts 0。
- **Description**:
  - 逐行对拍 `extensions/markup.ts`（==高亮==/++下划线++/~波浪~/^上标^）、`emoji.ts`+`emoji-data.ts`（GitHub shortcode 表原样移植为数据资产；未知名保留字面）、`toc.ts`（[toc] 标记与 titleList 数据）、`slider.ts`（`<<< ... >>>`）、`alert.ts`（24KB：GFM/Obsidian/学术类型全集、blockquote `[!TYPE]` 与 `::: type 标题` 容器、自定义名中性回退、图标/颜色/body 内联 markdown+KaTeX、diagramMessages 等）。
  - 各扩展产出黄金样例（从 extensions.test.ts/emoji.test.ts 转录期望值）。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-6.1: 五扩展黄金样例（alert 至少覆盖全部类型别名 + 自定义标题/非 ASCII 名/嵌套数学）全绿；emoji 抽样 ≥50 个 shortcode 与未知保留；证据：test_extensions_batch1.py。

## Task 7: 渲染扩展批次二（katex/footnotes/mermaid/plantuml/infographic/ruby/component + 后处理）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T5
- **Description**:
  - 对拍 `katex.ts`（定界符识别、MDKatex 占位/输出形态、mathDetection.ts、`stripBreakBeforeInlineKatex` 规则、mathjax.ts 占位语义）、`footnotes.ts`（收集+文末区）、`mermaid.ts`（占位保护、themeMode 注入）、`plantuml.ts`（编码/链接/占位容器，9.7KB 全读）、`infographic.ts`、`ruby.ts`（`{漢字|かんじ}`）、`component.ts`（24KB：自定义组件占位与 components 选项解析，web 端 custom_components 数据形态对齐）。
  - `render/postprocess.py`：阅读时间前缀（readingTime 算法对齐 utils/readingTime：中英文字符计数口径）、footnotes 注入、addition style（renderMessages）、Mac 代码块显隐 style、`<section class="container">` 包裹。
- **Acceptance Criteria Addressed**: AC-4, AC-U1
- **Test Requirements**:
  - `rule` TR-7.1: 七扩展+后处理黄金样例全绿；数学边界（行内/块/定界符误判样例来自 mathDetection.test.ts）逐条通过；证据：test_extensions_batch2.py、test_postprocess.py。
  - `rule` TR-7.2: 复杂组合文档（AC-U1 描述的 5000 字综合样例）结构对拍通过并留档；证据：tests/golden/complex_doc.* 与对拍报告。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 实现：src/doocs_md_py/render/extensions/{katex,footnotes,diagrams,ruby,component,component_data}.py；stripBreakBeforeInlineKatex 落于 extensions/katex.py 尾部并接入 render/markdown.py 两条流水线（render_markdown、modify_html_content，sanitize 前）。后处理（阅读时间前缀/footnotes 注入/addition style/Mac 显隐 style/container 包裹）在 renderer.render_markdown_to_html 内对齐，TR-7.2 全节点等价已覆盖，无独立 postprocess.py。
  - 持久测试（全绿）：tests/render/test_extensions_katex.py 24 例（含 strip 3 例）、test_extensions_footnotes.py 12 例、test_extensions_diagrams.py 19 例、test_extensions_ruby.py 16 例、test_extensions_component.py 31 例。
  - TR-7.1：数学边界（金额守卫、行首单 $、软/硬换行 #1743、行内/块/LaTeX 定界符）、脚注定义序编号与重复引用、三图 SSR 占位 hash（w0enk7/w1qwat/6tkwri/0）、ruby 两格式与全角分隔符、8 组件 + 未知名 + 模板引擎（if/unless/each/children）逐条通过。
  - TR-7.2：tests/golden/complex_doc.md（约 5000 字，覆盖 frontmatter 外全部扩展交互）+ complex_doc.expected.html（上游 Node 22 + marked 18.1.0 initRenderer 输出锁定，26176 字符）+ test_complex_doc.py；domcompare 归一化 DOM **逐节点等价**。重生成器 scripts/golden_regenerate.py（WSL podman localhost/node:22-alpine，shim svgCache 参数属性/languages/hljs/fetch/document）。
  - 对拍捕获并修复三处真实偏差：① katex 两条块规则注册补 `alt=[paragraph,reference,blockquote,list]`，`\[...\]` 块级 LaTeX 才能中断段落（marked start() vs markdown-it alt 语义差）；② 脚注引用锚文本应为字面 `[1]`（JS 模板 `\[1\]` 求值）非 `\[1\]`；③ GFM 自定义表格 thead 直接挂 th、无 tr（renderer-impl.ts:423-446）。
  - 全量回归：ruff check src tests scripts 通过；pytest 409 例全绿。

## Task 8: 净化层（DOMPurify 等价）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T7
- **Description**:
  - 用 nh3 配置等价 DOMPurify：从 web/core 源码核实完整 hook 点——mermaid/infographic 占位保护、ADD_TAGS `mp-common-profile`、允许标签/属性白名单（以 core 中 DOMPurify 配置源码为准，先 grep 定位再逐字移植）。
  - 另实现分享快照净化（share-sanitize.ts 更严格的规则集：script/iframe/object/embed/form/meta/link/base 移除、on* 移除、javascript:/vbscript: 移除、styles 额外去 `</style>` 与危险 @import、转义表 `& < > "`）——放 server 分享模块共用。
  - XSS 回归样例集（脚本/事件/伪协议/编码绕过/嵌套）。
- **Acceptance Criteria Addressed**: AC-4（净化部分）, AC-7（快照净化部分）
- **Test Requirements**:
  - `rule` TR-8.1: XSS 样例集（≥20 条）全部拦截且正常内容不被破坏；mp-common-profile 与图表占位保留；证据：test_sanitize.py。
  - `rule` TR-8.2: 分享净化样例（含 `</style>`、javascript @import、data:text/html）行为逐字对拍 share-sanitize.ts；证据：test_share_sanitize.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 实现 src/doocs_md_py/render/sanitize.py：nh3.Cleaner 单例，tags=nh3 默认 ∪ {section,nav,svg,path,ellipse,mp-common-profile,form/button/input/select/option/optgroup/textarea/label/fieldset/legend,video/audio/source/track}；通用属性集（class/id/style/target/rel/colspan/SVG 全属性等）+ data-*/aria-* 前缀；url_schemes 收窄为 DOMPurify 默认 ALLOWED_URI_REGEXP 十协议（http/https/ftp/ftps/mailto/tel/callto/sms/cid/xmpp，拒绝 about:/data:/blob:，相对/锚点/协议相对 pass_through）；link_rel=None（DOMPurify 默认不插 rel）；style 属性原值不过滤（与 DOMPurify 一致）；script/style 连内容移除、注释剥除。mermaid/infographic 注释占位净化前转 `<span data-md-protected="N">`、净化后按序还原（markdownHelpers.ts:17-46 逐字移植）。
  - 接入：render/markdown.py 删除 T5 直通占位，两条流水线（render_markdown、modify_html_content）均经 sanitize_html。
  - src/doocs_md_py/server/share_sanitize.py：逐字移植 apps/api/src/share-sanitize.ts 全部六条正则 + escape_html（& < > "）+ SHARE_PAGE_CSP 十条指令与 share_page_csp_meta；sanitize_html_snapshot / sanitize_styles_snapshot 供 T12 分享模块共用。
  - 测试：tests/render/test_sanitize.py 38 例（28 条 XSS 参数化向量：script 嵌套/分裂、img/svg/details/marquee/input 事件、javascript 大小写/HTML 实体/冒号实体/前导 tab、vbscript、data:text/html、iframe/object/embed/form action/base/link/meta、注释突破、body onload；+ 正常内容/协议白名单/mp-common-profile/三类占位保护与顺序/SVG 图标/注释剥除 10 结构例）；tests/server/test_share_sanitize.py 12 例（上游三条 vitest 用例 + CSP/转义逐字对拍，及单/双引号/无引号事件、七类危险标签、data:text/html @import、安全 @import 保留、未闭合 script 不匹配等边界）。
  - 已知逐字行为（T21 contract-differences 候选）：① 上游 share 正则 `[^"'>\s]*` 不消费危险 URL 属性的闭合引号，残留 `<a">`，与 JS 逐字一致，由分享页 CSP script-src 'none' 兜底；② style 属性内 CSS 文本（url(javascript:) 等）DOMPurify/nh3 均不解析，原样保留（现代浏览器不执行）；③ emoji `<img src="about:blank"> 的 src 在主净化层被剥（data-emoji-id 保留，前端 hydrate 真实 CDN 地址），DOMPurify 默认同样拒绝 about:。
  - 回归：ruff check src tests scripts 通过；pytest 459 例全绿。

## Task 9: 主题资产与 CSS 装配层

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T5
- **Description**:
  - 原样复制 `shared/src/configs/theme-css/{base,default,grace,simple}.css` 到 `render/assets/`（WTFPL 署名）；同时移植 4 语言 default-custom-theme txt 资产（核实用途后随包）。
  - `render/css.py`：generateCSSVariables（含 default 不声明 blockquote 背景特例、缩进/两端对齐规则）、generateHeadingStyles（color-only/border-bottom/border-left 字面 CSS）、processCSS（正则抽变量、var() 迭代≤10 含 fallback/嵌套、calc 四类运算+round 4 位）、escapeStyleContent（`<\/style`）。
  - `render/code_themes.py`：10 个白名单 URL 常量集、assert 校验、httpx 抓取 10s 超时 + 内存缓存。
  - `render/article.py`：等价 buildRenderedOutput（装配顺序 variables→base→theme→heading→hljs→custom，`<style>...` 前缀 + html；返回 dataclass html/front_matter/reading_time）；默认值字面对齐 config-options.ts。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-9.1: options 矩阵 CSS 黄金字符串测试全绿（default 特例、heading 三态、var 嵌套/fallback/未解析保留、calc 乘除加减/异单位保留/rounding、转义）；非白名单 URL 抛错；证据：test_css_assembly.py。
  - `rule` TR-9.2: buildRenderedOutput 默认参数输出含 `<style>`、frontMatter、readingTime 三键结构；证据：test_article.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 资产：8 文件字节原样复制到 src/doocs_md_py/render/assets/（base/default/grace/simple.css 四主题 + default-custom-theme.{en-US,ja-JP,zh-CN,zh-TW}.txt 四语言自定义主题默认文本，LF 行尾经字节/字符核对无损）；scikit-build-core wheel.packages 整包默认包含非 .py 资产，已实测构建 py3-none-any wheel 内含 8 文件（误配的 wheel.package-data 键不被 0.9 支持，已移除）。
  - render/css.py：CSSVariableConfig slots dataclass + generate_css_variables（DEFAULT_LINE_HEIGHT 1.75/DEFAULT_BLOCK_SPACING 1/DEFAULT_LINK_COLOR #576b95；blockquoteBackground 空或 "default" 不声明 --md-blockquote-background 特例；indent/justify 两布尔行；输出 .strip()）、generate_heading_styles（h1-h6 六元组遍历，default/custom 跳过，color-only/border-bottom/border-left 三字面模板，规则间 \n\n）、process_css（_VAR_DECL_RE 后写覆盖；var() 迭代替换≤10 轮支持 fallback 与一层嵌套括号；calc() 再迭代≤10 轮；乘恰一带单位/除纯数/加减同单位；_js_round=Math.round 语义 floor(n*10000+0.5)/10000 非银行家舍入，整数不带 .0）、escape_style_content（IGNORECASE 匹配但替换串固定小写 `<\\/style`，与 JS 逐字）。
  - render/code_themes.py：CODE_BLOCK_URL_PREFIX（highlightjs/11.11.1/styles/）+ 10 主题名（github/github-dark/atom-one-light/atom-one-dark/monokai/vs/xcode/nord/tokyo-night-light/tokyo-night-dark）+ CODE_BLOCK_THEME_OPTIONS（label=name/value=URL/desc=""）+ ALLOWED frozenset；assert_allowed_code_block_theme_url 错误文案逐字；fetch_code_block_css(url, *, client=None) 模块级 dict 缓存 + 模块级懒 httpx.Client(timeout=10)，非 200 RuntimeError 带状态码，httpx.TimeoutException 转 TimeoutError 10000ms 文案；clear_hljs_css_cache。
  - render/article.py：DEFAULT_RENDER_OPTIONS 逐字（theme=default/#0F4C81/无衬线长串保留逗号空格原貌/16px/1.75/1/#576b95/default/legend=alt/github URL/四 false/light/两 false）；importlib.resources 模块加载期读四 CSS；RenderArticleInput（20 字段全 Optional）+ RenderedArticle（html/front_matter/reading_time{words,minutes}）；normalize_heading_styles 逐字（仅排除 falsy/default，保留 custom）；build_rendered_output 用 `?? 默认` 语义（None 才回退，空串覆盖）、renderer 初始化六开关、render_markdown+post_process_html+二次 parseFrontMatter、CSS 六段序 variables→base→theme（MCP 路径单取不叠加 default）→heading→hljs（code_block_theme 经默认值合并后 truthy 才抓）→custom（trim+escape），filter(Boolean) 双换行 join 后整体 process_css，`<style>\\n...\\n</style>\\n` 前缀；code_css_fetcher 关键字注入便于测试。
  - 黄金对拍三层：
    ① tests/golden/css_snapshot.json（上游 Node 22 直跑真实 cssVariables.ts/cssProcessor.ts 生成，variables 4 例/headings 5 例/process 14 例，含整个 default.css 11.8KB 处理结果；重新生成器 scripts/css_snapshot_regen.py 已验证重生成字节一致，普通 pytest 不依赖 Node）；
    ② tests/golden/article_cases.json + article_expected_{complex-default,styled}.html：scripts/article_golden_regen.py 在 podman 中逐行复刻 buildRenderedOutput，渲染用真实 initRenderer + 真实 isomorphic-dompurify@4.5.0 + 真实 highlight.js@11.11.1（COMMON_LANGUAGES 剪枝仅留 plaintext，对齐 Python T5 契约）+ 真实 cssVariables/cssProcessor/config-options + 四份真实主题 CSS；complex-default 用 TR-7.2 五千字综合文档（39663 字符），styled 覆盖 grace/全开关/heading 三态/customCSS 逃逸/空 codeBlockTheme/frontmatter/脚注/表格/行号布局（8680 字符）；tests/golden/test_article_doc.py 两例归一化 DOM 全等价；
    ③ 单元测试 tests/render/test_css.py（30 例）、test_code_themes.py（9 例，httpx MockTransport 成功转义缓存/404/超时翻译/白名单前置/clear 重取）、test_article.py（18 例，默认字面值/资产/装配顺序锚点/grace/未知主题回退/customCSS trim 转义/空主题不抓取/heading 解析后色值/frontmatter/reading_time/mac 开关）。
  - 对拍捕获并修复的真实偏差（勿回退）：① fence/缩进代码 token 尾换行——marked 恰好去一个尾换行（Node 实测 "x\\n"→"x"、"x\\n\\n"→"x\\n"），markdown-it token.content 保留，renderer.py code_render 统一在渲染前 endswith("\\n") 去一个（diff/highlight/pending 三路径共用该 text）；② processCSS calc 除法上游解构 `const [, a, unit,, b]` 多一个 elision 致 b 恒 undefined（Node 实测 calc(8px / 2)→NaNpx），css.py 逐字等价返回 `NaN<unit>`，标记上游疑似 bug。
  - 已知契约差异（T21 contract-differences 登记）：① calc 除法 NaN（上游 bug 逐字复刻）；② Python 端无 highlight.js 语法着色（NFR-2 白名单不含 pygments），REGISTERED_LANGUAGES={plaintext}，9+1 内置语言（bash/css/javascript/json/markdown/python/shell/typescript/xml + plaintext）在 Node MCP 真高亮、Python 一律 pending + plaintext 转义，由前端 CDN 语法包 hydrate；包裹结构/Mac 三点/三 pending 属性/行号布局/diff 红绿行 1:1（styled golden 已验证 plaintext 路径结构等价）。
  - 回归：ruff check src tests scripts 通过；pytest 507 例全绿（较 T8 的 459 新增 48 例）。

## Task 10: 鉴权（JWT + GitHub OAuth + plan）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T3, T4
- **Description**:
  - `server/security.py`：PyJWT HS256 签发/校验（30 天、{sub,login,exp}）、Bearer 中间件（401 unauthorized/invalid_token 分支）、share_access JWT 签发/校验（放 T12 共用，先建工具）。
  - `server/routers/auth.py`：GET /auth/github（uuid4 state、双 cookie 属性、authorize URL 参数 scope=read:user）、callback（立即清 cookie、error/code/state 各分支 hash 回跳、httpx 换 token 需 UA/json Accept、拉用户带 UA md-api、upsertUser）、GET /me（plan 有效期判定、isAdmin）。
  - `server/plan.py`：getEffectivePlan、续费月计算（31 天、max(now,exp)、月数 floor 兜底 1）、parseGithubLoginFromRemark（正则+分隔符回退+lowercase trim）、admin 集合解析。
  - OAuth httpx 调用全部走可注入 transport 便于测试。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-10.1: OAuth 全分支（含 redirect 白名单单标签 `*` 与扩展 origin）MockTransport 测试通过；cookie 属性逐条断言；证据：test_auth.py。
  - `rule` TR-10.2: 用独立脚本生成已知 HS256 token（含与 hono jwt 互认的已知向量：secret+claim→固定 token，先在 Node 侧或手算记录一组）验证互认；plan/remark 解析边界测试；证据：test_jwt_interop.py、test_plan.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建 server/security.py：issue_token/verify_token（PyJWT HS256，{sub,login,exp}，TOKEN_TTL_SECONDS=2592000）；issue_share_access_token/verify_share_access_token（T12 先建：typ=share_access、exp=min(分享到期秒, now+86400)、typ/sub 严格校验、异常一律 False）；FastAPI 依赖 require_user（无 Bearer→401 unauthorized；验签失败或 sub 非非空字符串→401 invalid_token）。时间戳全部 now_s 可注入。
  - 新建 server/plan.py（upstream plan.ts:7-50 纯函数段）：MS_PER_SPONSOR_MONTH=31 天毫秒、SYNC_RATE_LIMIT{free:30,pro:300}、SHARE_CREATE_LIMIT{free:2,pro:None}；normalize_github_login、parse_github_login_from_remark（整体裸名/github[:：]前缀正则 + 分隔片段回退，登录名 1-39 字符、中划线仅内部）、get_effective_plan（pro 且 expires 严格 > now）、extend_plan_expires（base=max(未过期到期,now)、Math.floor(months)||1 逐字含 NaN/0/负数兜底 1、max(1,...)）。同表小时/日限流函数留 T11 在同文件扩展。
  - 新建 server/github_oauth.py：build_authorize_url（scope=read:user 四参数）、exchange_code_for_token（Accept+Content-Type application/json，access_token 缺失返 None）、fetch_github_user（UA md-api、Accept application/vnd.github+json、Bearer；非 2xx ok=False）；client 全部显式入参。
  - 新建 server/routers/auth.py：router(prefix=/auth) 挂 GET /github（uuid4 state、secure 随请求 scheme、HttpOnly/SameSite=Lax/Path=//Max-Age=600 双 cookie、回跳地址先经 resolveRedirect 白名单校验）与 GET /github/callback（读 cookie 后无条件 delete-cookie 再分流；oauth_error 透传、缺 code/state 不符→invalid_oauth_state、换 token 失败→oauth_exchange_failed、拉用户失败→github_user_fetch_failed、成功按 github_id 查既有用户复用 uuid、upsert 资料、issue token、302 回白名单 origin 且 account_token 仅在 fragment）；me_router() 挂 GET /me（注意上游挂载点是 index.ts:55 根路径 api.get('/me') 而非 /auth/me；404 not_found、camelCase 响应、plan 有效期与 isAdmin 判定）。
  - 配套：httputil.py 新增 ApiError + app.py 注册 exception_handler 统一输出 {"error":...}（替代 Hono c.json）；deps.py 新建 get_db（app.state.db 注入优先，否则按 sqlite_path 懒连+迁移）与 get_http_client（app.state.http_client 注入优先，否则模块级 15s 超时单例——上游 Workers fetch 无超时，Python 侧必须设，T21 偏差）；create_app(config, *, conn, http_client) 支持测试注入。
  - 基础设施修正：db.connect 加 check_same_thread=False（FastAPI 同步路由在线程池执行，单服务连接需跨线程；自托管单 worker + WAL；多 worker 需各持文件连接，T21 登记部署约束）。
  - JWT 互认黄金向量：scripts/jwt_interop_regen.py 在 podman node:22 装精确 hono@4.13.13（pnpm-lock.yaml:4341 锁定版），① Node sign 的 node_token 交 PyJWT verify；② PyJWT 令牌交 hono verify claims 全等；③ 过期/错 secret/篡改负向量双侧拒绝。固化 tests/golden/jwt_interop.json，五项检查全 true；实测同 claims 同 secret 两库紧凑序列化**字节完全相同**（header/payload 规范化一致）。普通 pytest 不依赖 Node。
  - 测试新增 52 例全绿：tests/server/test_plan.py 20 例（remark 14 参数化含中文冒号/下划线非法/39 字符边界/find 首片段语义、plan 有效期等值边界、续费 floor/NaN/负数/base 语义、常量字面）、test_security.py 15 例（roundtrip/过期/错 secret/垃圾、share 三 exp 分支/错 id/错 secret/过期/类型不符、require_user 四分支）、test_auth.py 17 例（authorize 302 全 query 断言+cookie 五属性+https Secure+非法回跳回退；callback 七分支含换 token 请求体/头逐字段断言、user 请求 UA/Accept/Authorization、成功 upsert 字段与 fragment、二次登录同一内部 id 且资料更新行数仍为 1；/me 401 双码/404/free/pro+admin/过期回退 free，MockTransport 全注入无真实网络）、test_jwt_interop.py 6 例。
  - 测试基础设施要点：httpx cookiejar 对 testserver 这类无点域名的显式 domain cookie 不回发，client.cookies.set 必须省略 domain 参数（按请求 host 匹配）；hono/Starlette setCookie 均不对 cookie 值做百分号编码，回跳 URL 原样存储。
  - 回归：ruff check src tests scripts 通过；pytest 559 例全绿（较 T9 的 507 新增 52 例）。

## Task 11: 限流基础设施与同步端点

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T3, T10
- **Description**:
  - `server/ratelimit.py`：UTC 小时键 `YYYY-MM-DDTHH`、UTC 日键；三表计数（sync_rate_limits(user_id,hour)、share_rate_limits(scope_key,hour) 共用表、marketplace_rate_limits(scope,day)）；先查后插 count+1；retryAfterSec 到窗口末（最少 1s/日界到 UTC 0 点）。
  - `server/sync_limits.py`：逐行移植 sync-limits.ts 全部常量与校验（100/80、128/500B/512KiB/20×512KiB/256/1MiB/8MiB/1.8MiB；墓碑剥离；错误码 400 校验类/413 尺寸类/403 配额类，field/max 字段）。
  - `server/routers/sync.py`：pull（since 解析兜底 0）、push（Content-Length 预检 413→invalid_body→validate→配额双计数（新活跃/新行含墓碑复活）→pushChanges，响应 documents/settings/cursor）、activate 占位（T17 接线）。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-11.1: 同步场景矩阵（≥30 场景：LWW 双向/游标/墓碑/全部超限码/配额/限流/坏 token/无用户）全绿；证据：test_sync_contract.py。
  - `rule` TR-11.2: UTC 窗口边界用例（跨小时计数清零、retryAfterSec 取值范围）通过；证据：test_rate_limit.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建 server/ratelimit.py（upstream plan.ts:52-144 + marketplace-db.ts:349-394）：`_clock` 统一 UTC（注入 naive datetime 按 UTC 解释，aware 转 UTC）；utc_hour_key `YYYY-MM-DDTHH`、utc_day_key `YYYY-MM-DD`；sync_retry_after_sec 到小时末（1..3600）、day_retry_after_sec 到次日 UTC 0 点（1..86400）。check_sync_rate_limit（sync_rate_limits 表 PK(user_id,hour_key)，先查后 upsert count+1，超限返 allowed/limit/retry_after_sec）；peek_share_create_rate_limit（只读不扣减；pro limit=None 直接放行且 period=day；scope_key 逐字 `share:publish:{user_id}`、日键存 hour_key 列）；consume_share_create_rate_limit（pro no-op 不写行）；consume_marketplace_publish_rate_limit（scope_key `publish:{user_id}`、day_key 列，T15 使用）。
  - 新建 server/sync_limits.py（upstream sync-limits.ts 1:1，校验作用于 JSON 原生 dict/list）：SYNC_PUSH_LIMITS 十字面常量（100/80 批量、id 128 字符、title 500B、content 512KiB、history 20 项×512KiB、setting key 256/value 1MiB、整包 8MiB、单行 1_800_000B）+ SYNC_STORED_DOCUMENT_LIMIT{free:200,pro:2000}/SYNC_STORED_ROW_LIMIT{free:400,pro:4000}；utf8_bytes 按 UTF-8 字节；PayloadRejection TypedDict（error/status/field?/max?）；validateHistory（None 放行、非数组/非对象项/finite number|string datetime/content str→invalid_history 400、超 20 项 history_too_large 413、内容超限 history_content_too_large 413）；validateDocument（id/title/content/parentId/双时间戳/deleted 全分支 invalid_* 400、各尺寸 413、history 复用、estimateDocumentRowBytes 超 1.8MB document_too_large 413，JSON 序列化用 ensure_ascii=False 紧凑分隔符等价 JSON.stringify）；validateSetting（invalid_setting_key/invalid_setting/setting_value_too_large）；validate_push_payload（非数组 invalid_body、批量上限、逐项校验、整包字节累加 payload_too_large field=body）；normalize_push_documents（dataclasses.replace 剥墓碑 title/content/history）；count_new_document_ids（去重后未知 id 计数含墓碑）/count_new_active_documents（跳过 deleted 与同批重复，existing 缺省或 True=已删才计复活）/exceeds_stored_document_quota/exceeds_stored_row_quota（newCount<=0 恒 False）。关键 Python 边界：bool 是 int 子类，_is_finite_number 显式排除 bool（JS typeof boolean≠number），NaN/Infinity 经 math.isfinite 拒绝。
  - 新建 server/routers/sync.py 并挂 app.py（鉴权 api 组，三端点均 Depends(require_user)）：_enforce_sync_rate_limit（get_user_by_id 缺省→404 not_found；get_effective_plan；小时窗限流→429 {error:rate_limit_exceeded,plan,limit,retryAfterSec,upgradeRequired:plan==free}）；GET /sync/pull（_parse_int_loose 等价 Number.parseInt 前导数字宽容解析（"12abc"→12），非有限或 ≤0 兜底 0；db.pull_changes 严格 server_updated_at>cursor；响应 camelCase documents/settings/cursor）；POST /sync/push（限流→Content-Length 头预检（可解析且 >8MiB 直接 413 payload_too_large，无该头/畸形跳过）→request.json() 异常或非 object→400 invalid_body→documents/settings 缺省 []→validate_push_payload 400/413 透传 field/max→SyncDocument/SyncSetting.from_api_dict 类型化→normalize 剥墓碑→有文档时 list_existing_documents+双 count+countNew*，双配额任一超限→403 document_quota_exceeded{plan,limit（活跃 200/2000 或行 400/4000）,upgradeRequired}→db.push_changes 响应服务端合并版本；验证 LWW 被拒行不在 push 响应内，与上游 D1 ON CONFLICT…WHERE+RETURNING 语义一致）；POST /sync/activate 占位（config.is_afdian_configured() 未配置→503 afdian_not_configured，T17 接 queryOrder/activateProFromOrder 全链路）。路由为 async def 仅因读 JSON body，SQLite 本地调用直接执行（单 worker 自托管，配套 check_same_thread=False，T21 登记）。
  - 测试新增 75 例全绿：tests/server/test_rate_limit.py 15 例（UTC 键零填充/naive 按 UTC/小时末 1s 与整点 3600/日界 36870 与 86400/free 30 次第 31 拒且跨小时清零/用户隔离/pro 300/share peek 五次不扣减、consume 2 后拒且次日清零、pro 无限不写计数行/marketplace 5 后拒+次日清零/scope 与 share 表隔离/常量字面）、test_sync_limits.py 29 例（空批/utf8 中文 6 字节/批量 101 与 81/content/title 按字节/单行 1.8MB/全部 invalid_* 分支含空 parentId 与 NaN 时间戳/bool 非 number/float 时间戳/history None|字符串 datetime|非对象|超长|内容超限/setting 空 key/长 key/非 str value/大 value/null value/整包 17×500KB 触 8MiB 但单篇不触 content/estimate 非字符串字段计 0/配额边界/复活计数/同批去重/未知墓碑计行/newCount=0 恒放行/墓碑剥离/常量）、test_sync_contract.py 31 例（无/坏 token 401、幽灵用户 404；pull 空形态、since 四变体含 parseInt 宽容回显、增量严格 >cursor、用户隔离、camelCase+墓碑；push 空 no-op、缺省数组、非法 JSON、文档往返含中文与 history、设置往返 value 解码、LWW 旧戳拒绝与等戳保留（经 pull 验证）、墓碑落库剥正文、复活；非数组 400、畸形文档 400 field、空 id 400 max=128、坏 setting 400；too_many/documents content/Content-Length 谎报/row cap 四类 413；预置 200 活跃→新 id 403 limit200、预置 400 行→未知墓碑 403 limit400、满额更新既有放行、满额设置放行；429 响应体五字段、pull/push 共享窗口计数；activate 503；校验失败零落库）。预置存量走直接 INSERT 到 documents 表，无需慢速 HTTP 打满。
  - 对拍修正：① 注入 naive datetime 曾被 astimezone 当本地时区（UTC+8 主机偏 8 小时），改为 replace(tzinfo=utc)；② 整包超限测试初版用 1MiB 单篇先触 content 512KiB，改为 17×500KB 精确只触 body 8MiB；③ LWW 被拒行上游本就不返回（D1 RETURNING WHERE false 无行），契约改为断言 push 返回空 + pull 回拉服务端版本。
  - 回归：ruff check src tests scripts 通过；pytest 634 例全绿（较 T10 的 559 新增 75 例）。

## Task 12: 分享模块全套

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T3, T8, T10, T11
- **Description**:
  - `server/share/`：share-password（hashlib.pbkdf2_hmac 100000/16B salt/串格式/自动密码字母表/自定义 4–64/常量时间比较 hmac.compare_digest/访问 JWT typ=share_access 24h 与到期夹取/cookie 名与 path 精确）、share-db（创建复用 (user,post)、sha256(`user:postId`)[:12]、view_count 自增、列表/删除/解锁失败计数）、share-sanitize（T8 共用）、页面模板移植 share-page.ts/share-gate-page.ts/share-head.ts（占位符、CSP meta、noindex、750px、隐藏 diagram-download-bar、中文页脚与密码门主色 #07c160、favicon）。
  - 路由：POST /share（free 2/天成功后扣减、free 强制 1d、pro 四档、2MiB 净化后字节、postId ≤64、title 截 200、updated 语义、响应体 {id,url,expiresAt,updated,protected,password?}）、GET 列表与 DELETE（pro 门）、GET /s/:id（404 文本/410 文本/密码门/授权后计数注入页脚/CSP 头）、POST unlock（无密码 303、20/h/IP、JSON 与表单双形态、成功 cookie 303 或 {ok,url}）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-12.1: 分享场景矩阵（配额/过期/密码三模式/限流/双 accept 形态/410/404/cookie 属性/CSP 字面/页脚计数/幂等复用）全绿；证据：test_share_contract.py。
  - `rule` TR-12.2: PBKDF2 已知答案向量（密码+盐+迭代→已知 hash 串）通过；证据：test_share_password.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建 server/share_password.py（upstream share-password.ts 1:1；JWT 部分复用 T10 security.issue/verify_share_access_token，与该文件 issueShare/verifyShare 逐字同义）：PBKDF2_ITERATIONS=100000、生成密码 8 位、字母表逐字 55 字符（大写去 I/O 24 + 小写去 i/l/o 23 + 数字 2-9 共 8，已在测试纠正最初的 56 误数）、自定义密码 trim 后 4–64；hash 串 `pbkdf2:<iter>:<saltB64>:<hashB64>`（标准 Base64 含 padding，16B 盐/32B hash）；verify 四段解析、iterations 按 Number() 语义（float 可解析 "1e3"、拒 0/负/非整数/NaN/Infinity）、validate=True 解码、空 hash 拒、长度等后 hmac.compare_digest（等价上游手写 XOR diff 常量时间）；share_access_cookie_name/path 精确（md_share_<id>、/s/<id>）。
  - 新建 server/share_db.py（upstream share-db.ts）：slots dataclass ShareRow/ShareListRow；get_share_by_user_and_post_id/get_share_by_id/list_shares_by_user_id（created_at DESC，不含 html）/delete_share_by_user_and_id（rowcount）/insert_share（view_count=0）/update_share_content/increment_share_view_count（UPDATE 后 SELECT，缺失兜 1）；解锁失败小时窗 get/increment_share_rate_limit（scope=`unlock:<id>:<ip>` 存 share_rate_limits，UTC hour_key，复用 T11 ratelimit.utc_hour_key；重试秒数复用 sync_retry_after_sec 同公式）。
  - 新建 server/share_head.py（favicon 字面）、server/share_page.py（build_share_page_html 整页骨架：lang=zh-CN/noindex/CSP meta/favicon/默认标题"Markdown 分享"/styles 注入/750px/.diagram-download-bar{display:none}/SHARE_FOOTER_STYLES 逐字/存库含 {{SHARE_AUTHOR}}、{{SHARE_VIEW_COUNT}} 双占位符；ShareFooterAuthor；build_share_author_html "由 X 分享" 经 escapeHtml；inject_share_footer 占位符全量替换 + legacy 页脚兼容：share-footer-copy 或含 share-footer 但无 share-footer-author 时非贪婪正则替换第一处并在首个 </style> 前补样式，Python str.replace 必须 count=1 对齐 JS 无 g 标志单次替换）、server/share_gate_page.py（400px 卡片、主色 #07c160/hover #06ad56、error 双文案、form POST /s/<id>/unlock、password input 属性 current-password/required autofocus、作者缺省"由 doocs/md 分享"）。
  - 新建 server/routers/share.py 挂 app.py：GET /share 与 DELETE /share/{id}（require_user + pro 门：无用户 404 not_found、非 pro 403 pro_required；DELETE 非法 id 400 invalid_id、他人/不存在 404、成功 {ok:true}）；POST /share（注意上游错误码是 invalid_json 非 invalid_body；postId trim 非空 ≤64→post_id_required；htmlSnapshot 必须 object 且 bodyHtml/stylesHtml 为 str 且 bodyHtml.trim() 非空→html_snapshot_required；**净化后** body+styles UTF-8 字节 >2MiB→413 snapshot_too_large；密码 none/custom/auto 三模式，custom 4–64 否则 invalid_password，auto 生成明文仅响应返回一次；peek 日窗→429 {error:rate_limited,plan,period:"day",limit,retryAfterSec}；existing=(user,postId) 幂等复用 sha256(`user:postId`)[:12]；title trim+slice 200（JS UTF-16 码元 vs Python 码点，BMP 外差异 T21 登记）；free 强制 1d/pro 四档（1d/7d/30d/never，非法 mode 兜底 1d）；build 失败 render_failed 400；更新竞态 forbidden 403；**consume 在 upsert 后无条件执行（更新也扣配额）**；响应 {id,url,expiresAt,updated,protected,password?}）；GET /s/{id}（id 正则 ^[a-f0-9]{12}$ i，畸形/不存在→text/plain "Not Found" 404，过期→"This share link has expired." 410，有密码且 cookie JWT 无效→gate HTML（query error 仅透传 rate_limited|invalid，带作者），否则 increment view + resolveShareAuthor（无用户→"未知用户"，name.trim() 空则 login）+ inject 页脚，HTML 一律带 Content-Security-Policy 头）；POST unlock（畸形/不存在 404 文本、过期 410、无密码直接 303 不带 cookie；20/h/IP 超限 JSON 429 {error:rate_limited,retryAfterSec} 或表单 303 ?error=rate_limited；密码空/错→计数后 JSON 401 invalid_password 或表单 303 ?error=invalid；wantsJson 判 accept 或 content-type 含 application/json；成功 issue JWT（T10），JSON 形态 200 {ok:true,url} 且**不 set-cookie**（逐字：上游仅表单分支 setCookie），表单 303 + cookie（HttpOnly/SameSite=Lax/Path=/s/<id>/maxAge=max(60,min(86400,到期秒-now))/secure 随 https））。IP 解析 CF-Connecting-IP→XFF 首段 trim→unknown。
  - cookie 大小写修正：Starlette set_cookie 原样输出 samesite 大小写，Hono 固定 SameSite=Lax；share 与 T10 auth.py 统一传 "Lax"，test_auth.py 断言同步改为 SameSite=Lax。
  - PBKDF2 WebCrypto 互认 golden：scripts/share_pbkdf2_regen.py 在 podman node:22（WebCrypto 内置无需 npm）跑与上游同 API（importKey/deriveBits PBKDF2-SHA256 100000/256bit）：① 固定向量 salt=`fixed-salt-16by!` 双端 base64 全等（Python hash 锁 9nLzB9dUCgu32YSVMKLs9zgc+OhzDYeoLrBl1i2vMIQ=）；② Python 随机盐存储串 Node 拆串重算相等且拒错密码；③ Node 随机盐串 Python verify 接受/拒绝正确。固化 tests/golden/share_pbkdf2_interop.json，五项 checks 全 true；.temp-pbkdf2 已 WSL 清理，普通 pytest 不依赖 Node。
  - 测试新增 80 例全绿：test_share_password.py 21 例（常量/字母表 55/cookie 名 path/模式与自定义密码参数化/生成分布/hash 格式与随机盐/roundtrip/unicode/九类坏存储串/短 hash/固定向量/golden 五项）、test_share_page.py 14 例（favicon 字面/骨架锚点/标题 escape/页脚占位替换/负数 floor/无占位透传/legacy 两路径/门骨架双主色/error 变体/作者 escape/样式锚点）、test_share_contract.py 45 例（三端点 401 + 幽灵 404 + free pro 门；pro 列表空/字段与 expired/删除生命周期含非法 id 与他人 404/用户隔离；invalid_json/postId 四分支/快照四分支/2MiB 413/custom 密码/创建成功 id 派生与 1d/free 忽略 30d 与非法 mode；free 2/天 429 体五字段/pro 5+ 次不限与 never/7d/幂等复用且更新扣配额；auto 密码返回一次且可解锁/title trim 截 200 与非串空串；净化 script/onerror/iframe；畸形 id GET+POST 文本 404/wellformed 404/410 双端点；正文页脚计数三刷=3/未知作者/gate CSP；门遮正文/error query 三态/无密码 303 无 cookie/错误密码表单+JSON/空密码非串密码/表单成功 cookie 全属性与 Max-Age 区间并解锁正文/JSON 成功无 cookie 仍见门/20 次限流 JSON+表单+正确密码也拦/IP 隔离 XFF 与 CF 优先/篡改 cookie 仍门）。
  - 回归：ruff check src tests scripts 通过；pytest 714 例全绿（较 T11 的 634 新增 80 例）。

## Task 13: API 上传与存储后端

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T4, T11
- **Description**:
  - `server/storage.py`：抽象 StorageBackend；LocalBackend（落盘 STORAGE_LOCAL_DIR/YYYY/MM/DD/<key>，返回 LOCAL_BASE_URL/key，防路径穿越）；S3Backend（手写 SigV4：AWS4-HMAC-SHA256 规范 canonical request/string-to-sign，PUT 对象；用 AWS 官方公开测试向量做单测）。
  - upload-filename（MIME 映射表、blob/bin/octet-stream 拒绝、后缀 >10 拒绝、subtype `+` 前截断、png 兜底）、upload-rate（IP/用户两口径、成功后才计数）、upload-github（随机 token+repo、PUT contents、message 用 Referer/Origin/md-api、download_url、CDN raw→jsdelivr @ 改写）、upload-r2 等价走 S3Backend。
  - 路由 POST /upload：UPLOAD_ENABLED、门控 404、image/* 前缀（不做 magic）、5MiB、匿名降级鉴权、{url}/各错误码（upload_disabled/upload_not_configured/invalid_form_data/file_required/invalid_file_type/file_too_large{maxBytes}/rate_limited_exceeded/upload_failed 502）。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-13.1: /upload 分支矩阵（含三种后端成功/失败、CDN 改写、成功后计数）全绿；本地后端路径穿越用例被拦；证据：test_upload_api.py。
  - `rule` TR-13.2: SigV4 与 AWS 官方测试向量（get-object/put-object 各一组）逐字节匹配；证据：test_sigv4_vectors.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建 server/upload_filename.py（upstream upload-filename.ts 1:1）：MIME_TO_EXT 十条逐字（jpeg/jpg 同映 jpg、x-icon 与 vnd.microsoft.icon→ico、svg+xml 表查优先不做 + 截断）；INVALID_EXTENSIONS={blob,bin,octet-stream}、MAX_EXTENSION_LENGTH=10；extension_from_mime（strip 小写、无斜杠/subtype 空/octet-stream 拒、subtype 截 `+` 前）、extension_from_filename（splitext 语义：无点/点开头/点后空拒、小写、非法扩展名与 >10 拒）、resolve_image_extension（文件名扩展名优先→MIME→png 兜底）；build_dated_object_key(filename, mime, *, clock=None) → `<epoch_ms>-<uuid4hex 连字符>.<ext>`；dated_directory(now_epoch_sec=None) → time.strftime UTC `%Y/%m/%d`。
  - 新建 server/upload_rate.py（upstream upload-rate.ts）：复用 T11 share_rate_limits 表（scope_key/hour_key/count，仅 scope 命名空间不同）；UPLOAD_RATE_LIMIT{anonymous:60,free:120,pro:300} 权威常量在 config.py；get/increment_upload_rate_limit（UTC 小时窗复用 ratelimit.utc_hour_key，先查后 upsert+1）；upload_rate_limit_for_plan（None→60/free→120/pro→300）；retryAfterSec 复用 sync_retry_after_sec（1..3600 到小时末）。
  - 新建 server/upload_config.py：UPLOAD_MAX_BYTES=5MiB（200-100 警告码字面）；GithubUploadConfig slots dataclass；is_upload_enabled/get_upload_backend（枚举 local|s3|github，未知值兜底 local）/parse_github_upload_config（tokens 空返 None）/is_r2_upload_ready（bucket+public_url 非空）/is_upload_backend_ready（**未知枚举先 get_upload_backend 归一化再判就绪**，避免 ready 门判 github 缺凭证 503、路由却选 local 的矛盾；local 恒就绪、s3 判 bucket+AK/SK、github 判 tokens）。
  - 新建 server/storage.py（SigV4 全标准库，NFR-2 零新依赖）：sha256_hex/hmac_sha256/EMPTY_SHA256；amz_date_format（astimezone UTC `%Y%m%dT%H%M%SZ`）；encode_canonical_path（**接收未编码 raw_path，quote(path, safe="/") 单次编码**：$→%24、分段斜杠保留、~ 不编码、中文 UTF-8 百分号大写；传已编码 path 会双重编码成 %2524）；build_canonical_headers（键小写 strip、字典序、值 strip 折叠为单行）；build_canonical_request（method/编码 path/query（本场景空串）/headers/空行/joined names/payload hash）；derive_signing_key（kDate=`AWS4`+SK HMAC 日期→kRegion→kService=`s3`→kSigning=`aws4_request`）；sign_sigv4(method, raw_path, query_string, headers, payload, *, access_key_id, secret_access_key, region, service, amz_date, payload_hash=None) 返回 canonical_request/string_to_sign/signature/authorization 全中间产物；LocalBackend（base_dir resolve、**目录包含校验防穿越**：resolve 后 key 路径必须仍在 base_dir 之内，拦截 `../`、`..\`（Windows 双分隔符）、绝对路径；父目录 mkdir(parents,exist_ok)、`.tmp` 同目录临时文件 os.replace 原子落盘；base_url 去尾斜杠拼 key）；S3Backend（endpoint 必填且带 scheme 否则 ValueError；_target_host_and_paths 返 host/raw_path/encoded_path 三元组：force_path_style 时 host=endpoint 域、path=/<bucket>/<key>，否则 virtual-host host=`<bucket>.<endpoint 域>`、path=/<key>；PUT 带 x-amz-date/x-amz-content-sha256=payload 实 hash/host/content-type，Authorization=sign_sigv4(raw_path=未编码 key)；非 2xx RuntimeError `S3 upload failed: <status>`；public_url 配置时返回其拼接（去尾斜杠），否则回退实际请求 URL）。
  - 新建 server/upload_github.py（upstream upload-github.ts）：UploadPayload slots(name, content_type, content: bytes)；pick_random（rng.randrange，可注入 random.Random 确定性测试）；upload_to_github(config, file, referer, http_client, *, rng/now_sec/clock_ms 可注入)——随机选 repo+token，path=`<dated_dir>/<dated_key>`，PUT `https://api.github.com/repos/<u>/<r>/contents/<path>`（Authorization `token <t>`、Accept application/vnd.github+json、User-Agent md-api-upload、body content 标准 base64/branch/message `Upload by {referer}`）；非 2xx 读 json.message，缺 message 用 reason_phrase，抛 `GitHub upload failed: <detail>`；成功体 content.download_url 空/缺失抛 `... missing download_url`；useCdn 时 `raw.githubusercontent.com/<u>/<r>/<branch>/` → `fastly.jsdelivr.net/gh/<u>/<r>@<branch>/`，str.replace count=1 对齐 JS 单次替换。
  - 新建 server/upload_r2.py（upstream upload-r2.ts；**契约差异：上游 Workers 用 R2 runtime binding，Python 改走 S3 SigV4 PUT**）：DEFAULT_CONTENT_TYPE application/octet-stream；build_r2_backend（S3Backend region=auto）；upload_to_r2（bucket 或 public_url 缺失抛 `R2 upload is not configured`，key=`<dated_dir>/<dated_key>`）。
  - 新建 server/routers/upload.py 并挂 app.py（upstream upload.ts:35-37 注释锚点）：POST /upload 分支顺序逐字——404 upload_disabled → 503 upload_not_configured → request.form() try/except 400 invalid_form_data → form.get("file") 非 UploadFile 400 file_required → content_type 缺省 "" 非 image/ 前缀 400 invalid_file_type（不做 magic 嗅探）→ 读完 body 后 len<=0 或 >5MiB 400 file_too_large{maxBytes:5242880} → _resolve_upload_scope（Bearer verify_token；无 token/jwt.PyJWTError/sub 非 str/幽灵用户四分支降级 IP；命中真实用户取 get_effective_plan；scope `upload:ip:<ip>`/`upload:user:<id>`）→ 超限 429 {error:rate_limit_exceeded,limit,retryAfterSec,upgradeRequired: plan=="free"}（匿名 None→False）→ referer=Referer||Origin||"md-api" → 三后端分发（s3→upload_to_r2；github→parse+upload_to_github；local→key=`<dated_dir>/<dated_key>`+LocalBackend）→ **仅成功后 increment**，200 {url}；任何后端异常 502 {error:upload_failed,message:str(exc) 或 upload_failed}。IP 解析 CF-Connecting-IP→XFF 首段 trim→unknown。config.py 上传字段 T4 已预置（upload_enabled 默认 True、**Python 默认后端 local 零配置，上游默认 github**、github user/repo20/branch/tokens/use_cdn、s3 endpoint/region auto/bucket/AK/SK/pathStyle/publicUrl、storage_local_dir=data/uploads、base_url=/uploads、from_env 全量）。
  - TR-13.2 SigV4 golden 双锚点（scripts/sigv4_vectors_regen.py + tests/golden/sigv4_vectors.json）：向量取自 AWS 官方《Signature Calculations for the Authorization Header: Transferring Payload in a Single Chunk》GET /test.txt 与 PUT /test$file.text（20130524T000000Z、us-east-1/s3、examplebucket.s3.amazonaws.com、AKIAIOSFODNN7EXAMPLE 文档密钥）。**GET 组三重一致**：Python sign_sigv4 实算 == AWS SDK v3（@aws-sdk/signature-v4@3.374.0 + @aws-crypto/sha256-js，podman node:22-alpine harness）== 文档公布签名 f0e8bdb87c96…bdb41，canonical request 与文档代码块逐字相同（host;range;x-amz-content-sha256;x-amz-date、空 body hash e3b0c44…）。**PUT 组以文档公布值为唯一锚点**：签名 98ad7217…108bd、StringToSign 末行 hash 9e0e90d9…019d、SignedHeaders=date;host;x-amz-content-sha256;x-amz-date;x-amz-storage-class（date: Fri, 24 May 2013 00:00:00 GMT 与 x-amz-storage-class: REDUCED_REDUNDANCY 均参与）、body=`Welcome to Amazon S3.`（19 字符）真实 SHA256=44ce7dd6…34a8b803f8b072（以 hashlib 实算为准；文档排版曾诱抄 …cab9646c 不存在值）。**关键坑：AWS SDK v3 sign() 规范化时主动剥离 Date 头只签 x-amz-date，故 SDK 对该 2013 老示例算出不同签名（SignedHeaders 无 date）——PUT 组不与 SDK 对拍，regen 中仅断言 Python==文档常量，golden 标 cross_checked_with="official documentation only (SDK v3 strips Date header)"**；GET 组标 @aws-sdk/signature-v4 双锚点。regen 经 podman npm（--network slirp4netns）重跑 SDK harness 后写 golden，.temp-sigv4 已 WSL rm -rf 清理，普通 pytest 零 Node 依赖。
  - 测试新增 96 例全绿：tests/server/test_sigv4_vectors.py 10 例（get/put golden 逐层逐字节 canonical→sts hash→Authorization→signature、PUT/GET 文档签名与 sts hash 硬锚点、双 body hash 文档值、Authorization 结构与两组 SignedHeaders、encode_canonical_path $/斜杠/~ /中文 UTF-8 三例、canonical headers 排序与 trim、amz_date_format、signing key scope 身份）；tests/server/test_upload_units.py 55 例（MIME 表 12 参数化/拒绝集与 `/png`→png 对齐 JS split/非 image subtype/`+xml` 截断/文件名扩展名 4 正 9 反/resolve 三优先级/dated key 正则/dated_directory UTC；限流 plan 映射/同小时累加/跨 UTC 小时归零/scope 隔离/retryAfterSec 1..3600；LocalBackend 往返/重名原子覆盖/无 .tmp 残留/四类穿越 key 拒；GitHub MockTransport 录制 PUT URL 形态/token 四头/message 三 referer 形态/base64 体/CDN 改写与 use_cdn=False/403+500+缺 download_url+空串+非 JSON reason 五失败路径；S3 virtual-host 录制签名头与 scope/日期/payload hash/CT、path-style 特殊字符 key（$→%24、中文 percent-encode）与无 public_url 回退、403 抛错、endpoint 两非法形态、build_r2_backend 配置映射）；tests/server/test_upload_api.py 31 例（404 disabled/503 github 与 s3 未配/未知后端兜底 local 成功；畸形 multipart 帧 400/错字段与 urlencoded file_required/text 等四 ct invalid/image/x-made-up 通过/0 字节与 5MiB+1 含 maxBytes/恰 5MiB 边界；local 成功 URL 形态+尾斜杠无双斜杠+落盘字节一致；匿名预置 59→第 60 成功→429 体五字段 retryAfterSec 区间/free 120 upgradeRequired=True/pro 300 False/坏 Bearer 与幽灵用户降级 IP/CF scope 与不同 IP 隔离/XFF 首段与 CF 优先；**github 500 后 share_rate_limits 无行（成功才计数）**；github 成功 CDN+三 referer 录制+no-cdn+403 502；S3 200 签名 PUT+公开 URL 前缀+403 502）。预置计数走 increment_upload_rate_limit 直填，不打满真实 HTTP。
  - 对拍修正：① is_upload_backend_ready 初版直接转发 config.upload_backend_ready，未知后端枚举在缺 github 凭证时 503 而 get_upload_backend 兜底 local，门与分发矛盾，改为先归一化；② Starlette request.form() 对 application/json 返回空 FormData 不抛（异于 Hono formData()），invalid_form_data 用例改为声明 multipart 但帧体损坏触发 python-multipart 解析异常；③ SigV4 曾传已编码 path 造成 %2524 双重编码，定型 raw_path 入参+函数内单次编码。
  - 回归：ruff check src tests scripts 通过；pytest 810 例全绿（较 T12 的 714 新增 96 例）。

## Task 14: 13 图床 Python 上传器库

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: T13
- **Description**:
  - `uploaders/`：base（协议类型、配置 dataclass、日期目录/时间戳-uuid 命名）、github、qiniu（putPolicy JSON、deadline +3600、AK:safe64(HMAC-SHA1(b64(policy)),SK):b64(policy)）、alioss（SigV4 endpoint `<region>.aliyuncs.com` virtual-host、expires 300）、txcos（cos.<region>.myqcloud.com）、minio（pathStyle、region auto、无 path 前缀）、s3（endpoint 补协议、pathStyle/virtual-host 三返回优先级 cdn→endpoint→AWS 域）、r2（<account>.r2.cloudflarestorage.com auto）、mp（stable_token 缓存、<1MiB jpeg/png 分流 uploadimg/add_material、字段 media、wsrv 代理条件）、upyun（MD5(password)→HMAC-SHA1(`PUT&uri&date`) base64、UPYUN 头、X-Date）、telegram（sendPhoto→取 photo[-1].file_id→getFile 拼 URL）、cloudinary（签名参数字典序+folder/preset/timestamp、SHA1+secret、无签名 preset、secure_url 优先、自定义 domain 替换）、default（API /upload 客户端）。
  - 统一从参数/环境变量读凭证；不内置凭证；formCustom 不实现 JS 执行，提供 Python 插件注册入口（entry point 文档说明）。
  - dcloud（md-cli util.js 四步：HMAC-MD5 x-serverless-sign 签名串构造、anonymousAuthorize/generateProximalSign/report、OSS form 字段全集含原拼写 `encrpytion` 头）作为上传器之一实现（Q4）。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-14.1: 每家上传器至少一条请求录制断言（方法/URL/头/体关键字段）+ 签名已知答案（七牛/upyun/cloudinary/dcloud）；mp 分流两分支与 token 缓存键断言；证据：test_uploaders.py。
  - `rule` TR-14.2: S3 五家 endpoint/pathStyle/返回 URL 拼接矩阵（≥12 组合）通过；证据：同文件。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建 src/doocs_md_py/uploaders/ 11 个模块，14 个 provider（13 Web + md-cli dcloud）全部实现并经统一注册表调度：__init__.py（UPLOAD_PROVIDERS 顺序与 config_key 逐字 provider-registry.ts:8-22；resolve_upload_provider 未知值回退 default；file_upload(id, file, config, client, *, env) 按家白名单过滤注入参数 now/now_sec/now_ms/clock_ms/location_href/page_href/store，None 值不传回落默认）、base.py（UploadFile slots；get_dir UTC `%Y/%m/%d`；get_date_filename=`<epoch_ms>-<uuid4 连字符>.<split(".")[-1]>`，**无点文件名尾段即原名本身（"noext"→".noext"）、仅以点结尾才空尾，扩展名不做大小写转换**，逐字 JS split/pop；trim_trailing_slash）、qiniu.py、upyun.py、cloudinary.py、dcloud.py、s3_presign.py、s3.py（五家）、mp.py、telegram.py、github.py、default.py、form_custom.py。
  - qiniu（providers.ts:107-152）：qiniu_upload_token=`<AK>:<safe64(b64(HMAC-SHA1(encoded, SK UTF-8)))>:<encoded>`，policy json.dumps(separators 紧凑, ensure_ascii=False) 等价 JSON.stringify+TextEncoder；**safe64 仅 `+`→`-`、`/`→`_`，保留 padding `=`（golden 实证 sign 与 encoded 均以 = 结尾）**；deadline=trunc(now_sec)+3600；key=`<path?/>`+dateFilename（无独立日期目录段）；multipart data token/key + files file；resolve_qiniu_upload_url（空→https://upload.qiniup.com；http(s) 前缀原样；其余回落默认域；**qiniu-js region 对象在 Python 侧收敛为上传 URL 字符串等价直传，见契约差异**）；失败 `Qiniu upload failed: <text>`；返回 `<domain>/<key>`。
  - upyun（providers.ts:530-563）：filename=`${path}/${dateFn}` 逐字（path 空时以 `/` 开头，测试断言 `/bucket//`）；uri=`/<bucket>/<filename>`；X-Date=email.utils.formatdate(usegmt=True) 等价 toUTCString；**passwordMd5=MD5(password) 的 32 位小写 hex 字符串按 UTF-8 取字节作 HMAC-SHA1 key（非 16 字节摘要，golden 锁定）**；sig base64；Authorization=`UPYUN <operator>:<sig>`；PUT v0.api.upyun.com 三头发送；失败消息含 response.text；返回 `<domain>/<filename>`。
  - cloudinary（providers.ts:609-685）：cloudinary_signature(params, secret)——参与参数（folder/upload_preset 按存在性、timestamp 恒定）Object.keys.sort() 字典序 `k=v` join('&') 后直接拼接 apiSecret（无分隔符）SHA1 hex；有 secret 走签名（timestamp+signature+folder），无 secret 有 upload_preset 走 unsigned（append upload_preset 不签），二者皆无 cloudinaryMissingPreset；缺 cloudName/apiKey cloudinaryMissingConfig；multipart POST `/v1_1/<cloud>/image/upload`；secure_url||url 取值，缺失 cloudinaryMissingUrl；自定义 domain=`${domain}${pathname}${?search}`（保留查询串，golden 行为测试锁定 t=2&q=80）。
  - dcloud（md-cli util.js:53-153 逐字）：dcloud_sign=sorted keys reduce `&k=v` slice(1) → node:crypto HMAC-MD5 hex（golden 与 node:crypto 对拍，含中文 spaceId/secret 的 UTF-8 路径；定点 36d5dfe8…）；四步流程：① anonymousAuthorize POST https://api.bspapp.com/client，头 x-serverless-sign，**body 手拼字符串非 JSON.stringify**（紧凑字面、timestamp 数字不加引号）→② generateProximalSign（params 内嵌 `{"env":"public","filename":"<name>"}`，头加 x-basement-token，body 为 JSON.stringify，内嵌引号转义经测试断言）→③ OSS form POST 九字段全集（Cache-Control/Content-Disposition/OSSAccessKeyId/Signature/host/id/key/policy/success_action_status=200）到 `https://<host>`，**头 `X-OSS-server-side-encrpytion: AES256` 保留上游 encrpytion 原拼写**，**OSS 响应逐字不检查状态码直接进入 report**→④ report（params `{"id":"<id>"}` 同样转义）；返回 `https://<cdnDomain>/<ossPath>`；缺 spaceId/secret 抛 `请填写 spaceInfo`；name 默认 unnamed.file。
  - S3 query 签名 presign（s3_presign.py，与 T13 header 签名不同）：build_presigned_put_url 只签 host 头、载荷占位 UNSIGNED-PAYLOAD、expiresIn 300、时间全注入。**经锁版 @aws-sdk/client-s3@3.1147.0 + @aws-sdk/s3-request-presigner@3.1147.0 podman node:22 六场景录制逐字节对拍**（scripts/s3_presign_regen.py + tests/golden/s3_presign_vectors.json）：aws-vhost / 自定义 vhost https / path-style https / MinIO http:9000 path-style / alioss vhost（key 含 `$` 与空格，%24/%20 编码）/ cos vhost。**对拍发现并固化两个 SDK 3.1147 行为：① presign PutObject 默认注入 flexible-checksum 查询参数 x-amz-checksum-crc32=AAAAAA%3D%3D（command 无 Body 时空体 CRC32 base64 恒 AAAAAA==）与 x-amz-sdk-checksum-algorithm=CRC32，连同 X-Amz-Content-Sha256=UNSIGNED-PAYLOAD 全部参与 canonical query 签名；② x-id=PutObject 追踪参数实测在签名中间件之前注入、参与签名（枚举 8 种参数组合 + path 编码/x-id 变体后定位），同时固定出现在最终 URL 末尾**；最终 URL 查询段顺序非 canonical 字母序（Signature 位于 Expires 与 SignedHeaders 之间），canonical 排序与 URL 拼装分别构造。
  - s3.py 五家：AliOSSConfig（endpoint `<bucket>.<region>.aliyuncs.com` vhost、scheme 随 useSSL、cdnHost 去尾斜杠→`<host>/<key>`，默认 `<proto>://<bucket>.<region>.aliyuncs.com/<key>`，失败 `Upload failed: <reason>`）；TxCOSConfig（host `<bucket>.cos.<region>.myqcloud.com`；**cdnHost 分支不拼 key：path 空→`<cdn>/<dateFilename>`，非空→`<cdn>/<path>/<dateFilename>`；默认 https 域**）；MinioConfig（`<endpoint>[:<port>]`、region=auto、**forcePathStyle path=/<bucket>/<dateFilename> 无 path 前缀**、scheme 随 useSSL、失败 `MinIO upload failed: <status> <reason>`）；GenericS3Config（endpoint 空→AWS 域 `<bucket>.s3.<region>.amazonaws.com`；非空且无 http(s) 前缀补 https；pathStyle 与 vhost 双 host/path 形态；返回优先级 cdnHost→endpoint 形态（http 时 http）→AWS 默认域）；R2Config（region auto、host `<bucket>.<accountId>.r2.cloudflarestorage.com`、filename=`<path?/>`+dateFn、**domain 逐字不去尾斜杠**（测试锁定双斜杠）、失败 `R2 upload failed: <status> <reason>`）。五家 PUT 均带 Content-Type 头、body 为文件原始字节（无 multipart）。
  - mp（providers.ts:404-499）：MpTokenStore 协议 + InMemoryMpTokenStore（等价 localStorage 键 `mpToken:<appID>`，缓存值为含 expire=now_ms+expires_in*1000 的 JSON，expire>当前 ms 才复用，坏 JSON 静默重取）；stable_token POST JSON {grant_type:client_credential,appid,secret}；access_token 缺失带 errcode 抛 `upload.provider.accessTokenFailed: [code] errmsg`，无 token 抛无后缀版；**分流 size/1024/1024 < 1 且 jpeg/png（小写比较）→ media/uploadimg，否则 material/add_material?type=image（1MiB 整与小 GIF 走永久素材，测试锁定）**；multipart 字段 media；proxyOrigin 替换 `https://api.weixin.qq.com` 前缀（stable_token 与素材 URL 均替换）；**微信 text/plain 响应也按 JSON 解析（issue #1877）**，httpx 按内容解析天然覆盖；无 url 抛 `upload.provider.uploadNoUrl: [code] msg`；proxy 且 page_href（注入的 window.location.href 等价物）startswith("http") 时包 `https://wsrv.nl?url=`，编码 safe 集合 `-_.~!*'()` 逐字 encodeURIComponent（冒号/斜杠/空格全编码，测试锁定）。
  - telegram（providers.ts:565-607）：sendPhoto multipart chat_id+photo，ok=false 或 photo 空抛 telegramSendPhotoFailed；取 result.photo[-1].file_id → getFile?file_id= → ok=false 抛 telegramGetFileFailed；返回 `https://api.telegram.org/file/bot<token>/<file_path>`。github.py（**Web 客户端版**，区别 server/upload_github.py）：parse_github_repo_url 三连前缀剥离后 `/` 切分；branch 默认 master；PUT contents 仅 Authorization `token <t>` 头；message `Upload by <location_href>`；body content 标准 base64；非 2xx `GitHub upload failed: <reason>`；useCDN raw.githubusercontent.com/<u>/<r>/<branch>/ → fastly.jsdelivr.net/gh/<u>/<r>@<branch>/（count=1）。default.py：POST `<api_base>/upload` multipart，可选 Bearer；UploadApiError(status, message, body) 消息回退 body.message→body.error→reason_phrase；200 无 url 抛 upload_failed。form_custom.py：**Python 不内嵌 JS 引擎执行用户脚本**，改为 @register_form_custom(name) 装饰器注册 Python entry point，build_util_bundle 暴露 getDir/getDateFilename/qiniu_token/upyun_signature/cloudinary_signature/dcloud_sign/s3_presigned_put 纯函数；未知名 KeyError；FormCustomConfig(name, raw) raw 仅留档。
  - TR-14.1 签名 golden（scripts/uploader_sig_regen.py + tests/golden/uploader_signature_vectors.json）：qiniu/upyun/cloudinary 三家经锁版 **crypto-es@3.1.3**（podman node:22）录制、dcloud 经 node:crypto 录制，输入刻意含中文 AK/密钥/policy/uri 与 `+//=` Base64 敏感字符；Python 标准库 hmac/hashlib 四家逐字节相等。**harness 坑：crypto-es@3.x 为 CJS 平铺导出，enc.Base64 即顶层 Base64（上游 crypto-js-compat.ts:96 的 buildCompat 手动挂 enc 命名空间），Node ESM 需 createRequire 加载且无 CryptoES.enc**。
  - 测试新增 60 例全绿（tests/uploaders/test_uploaders.py）：base 4（UTC 目录/扩展名逐字含无点与尾点/trim）；golden 回放 2（四家签名 + presign 六场景 URL 与 canonical_request 逐字节、结构断言 CRC32/x-id/SignedHeaders）；qiniu 3（region 解析四分支/录制字段 key 前缀/401）；upyun 2（path 空前导斜杠三头部 X-Date 定点/403 含文本）；cloudinary 5（签名录制独立函数交叉验证/unsigned 无 signature/双缺失错误/自定义 domain 保留 pathname+search）；dcloud 3（缺配置/四步全录制：手拼首步体、签名步 token 与转义 params、OSS 九字段+encrpytion 头、report 转义 id、三签名头 32 hex、请求次序 4、定点 HMAC-MD5）；S3 矩阵 12（alioss https 默认+http/cdn、txcos cdn path 空/非空+默认公开域、minio host/port/pathStyle/无 path 前缀+403 消息、s3 AWS 域 vhost/裸 endpoint 补 https/pathStyle+cdn/http 回退、r2 vhost+domain/尾斜杠逐字）；mp 9（缓存命中 1 次 stable_token+expire 计算/过期重取/大 PNG 与 1MiB 整/小 GIF 分流/text-plain JSON/errcode 两形态/proxy 替换+wsrv 编码/page_href 空不包 wsrv）；telegram 3（两步成功取最后一档+query 录制/sendPhoto 失败/getFile 失败）；github 4（三 URL 前缀解析/录制 path+message+branch+authorization/base64/CDN @ 改写/401）；default 5（Bearer/无头/message-error-reason 三回退参数化/无 url upload_failed）；formCustom 2（注册 entry point 执行+util 可用/未知名 KeyError）；注册表与调度 4（14 id 与 config_key 顺序/未知四值回退 default/default-qiniu-telegram 三端到端 dispatch）。
  - 对拍修正：① presign 初版漏 SDK 3.1147 默认 CRC32/x-id 查询参数且误判 x-id 不签，经 8 组合枚举定位后内置；② dcloud 初版对 OSS 响应加了非 2xx 抛错，复读 util.js:134-140 确认上游不检查状态码，删除以逐字；③ dcloud name 默认值对齐 unnamed.file；④ get_date_filename docstring 修正"无扩展名空尾"的误读（JS split/pop 无点时返回原名）；⑤ dispatch env 按家白名单过滤，避免 now_ms 等异名注入误入 S3 五家签名。
  - 回归：ruff check src tests scripts 通过；pytest 870 例全绿（较 T13 的 810 新增 60 例）；两组 golden regen 脚本的 .temp-s3presign/.temp-uploader-sig 均已 WSL rm -rf 清理，普通 pytest 零 Node 依赖。
  - 契约差异（T21 contract-differences 汇总）：get_dir 用 UTC（上游浏览器本地时区）；qiniu-js 浏览器 SDK 的 region 对象模型收敛为 HTTP multipart 直传（region 仅在为显式 URL 时生效，否则默认上传域）；formCustom 不执行用户 JS，改为显式注册的 Python 插件 entry point；S3 五家以手写 query SigV4 + httpx PUT 替代 @aws-sdk 运行时依赖（NFR-2 零新增依赖），签名经锁版 SDK golden 逐字节对拍；dcloud 保留 X-OSS-server-side-encrpytion 原拼写且 OSS 响应不校验状态码。

## Task 15: 市场（marketplace）全套

- **Status**: `completed`
- **Priority**: high
- **Depends On**: T3, T10, T11
- **Description**:
  - 逐行移植 marketplace-validate.ts（全部常量：200KiB/50KiB/32KiB/64/48/2000/512/500；slug/name/cover/primaryColor 正则；CSS @import/外链检测；组件 PascalCase/危险标签/onxxx/javascript:/props 白名单；服务端写死 1.0.0；PATCH 十进制 +0.0.1 进位算法 1.0.9→1.1.0/1.9.9→2.0.0/非法段兜底；empty_update）。
  - marketplace-db（列表 q 截断 64/LIKE、popular/newest 排序、分页 20/50、详情可见性、install 原子计数、作者校验、slug 唯一 409、approve/reject pending 守卫+published_at 流转、发布限流 5/30 管理员豁免）。
  - 路由全集（public/me/admin 三组）+ 通知联动（新提交发全部存在管理员含本人、结果发作者，失败不阻断）。
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `rule` TR-15.1: 拒绝条件全集逐条测试（≥25 条），版本进位三场景，状态机流转，409/404/403/429 全部分支；证据：test_marketplace.py。
  - `rule` TR-15.2: 通知联动收件人断言（管理员集、作者、管理员作者提交自发）；证据：test_marketplace_notify.py（与 T16 通知夹具复用）。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建源码 6 处：src/doocs_md_py/server/marketplace_validate.py（纯校验）、marketplace_admin.py（get_admin_logins/is_admin，消费 config.admin_github_logins，独立模块对齐上游边界而未复用 Config.is_admin_login）、notifications_db.py（parse_payload 损坏兜底/row_to_notification/resolve_admin_user_ids 仅返回 users 表已存在 id/notify_users 事务批量插 uuid4 去重/list/count_unread/mark_read/get_by_id/mark_all/clear_all，T16 挂路由）、marketplace_db.py（AUTHOR_JOIN、row_to_summary/detail camelCase 含 author{id,login,name,avatar}、列表/详情/插入/作者 patch/delete/approve/reject/原子计数）、routers/marketplace.py（APIRouter prefix=/marketplace 全路由）；修改 db.py 新增 get_user_by_github_login（函数内 import normalize_github_login、lower(login) 等值）、app.py 在 upload_router 后挂载。
  - 校验层契约点：ValidateResult 为 slots dataclass 判别联合（success/failure 类方法）；**三态哨兵 _UNSET 表达 JS undefined、None 表达显式 null**；JS `Number(seg)` 以自写 _js_number 复刻（空串→0、0x 十六进制→十进制、非法→NaN），math.isfinite+floor 且显式排除 bool（int 子类陷阱），major 默认 1/minor/patch 默认 0；bump 1.0.9→1.1.0、1.9.9→2.0.0、空白/非法→1.0.0；CSS 字节数→@import→外链顺序校验；组件 name PascalCase→template 非空→危险标签（script/iframe/object/embed/link/style）与 onxxx 属性与 javascript: 协议→props 白名单 string|number|boolean|array→紧凑 JSON 固定字段序 name/description/template/props/example（example 缺省省略）；cover 用 urllib.parse.urlparse 仅收 http/https 且需 netloc；description 截断 2000、rejectReason 截断 500；validate_update 客户端 version 恒忽略、服务端 bump、除 version 外无字段→empty_update，theme 处理 primaryColor/sampleMarkdown/css、component 处理 component。
  - 路由契约点：MARKETPLACE_PUBLISH_LIMIT={free:5,pro:30}、分页默认 20/上限 50（page<1→1、pageSize 越界/非数→归一化）；**注册顺序静态优先**：GET /themes、/components → GET /me、POST /themes、/components → GET /admin/pending、POST /admin/{id}/approve|reject → GET /{id}、POST /{id}/install、PATCH/DELETE /{id}；可选 Bearer（坏 token 匿名化）与强制鉴权分层；管理员发布豁免限流且作者为管理员时自发自收；非管理员 get_effective_plan→consume_marketplace_publish_rate_limit，超限 JSONResponse 429 rate_limited 带 limit/retryAfterSec（retryAfterSec 钳 1..86400）；坏 JSON→body=None→invalid_body 400；insert 捕 sqlite3.IntegrityError 且消息含 UNIQUE→409 slug_taken，**唯一键为 (author_id,type,slug)，同 slug 异 type 允许**；DELETE 他人条目上游按 author 条件 changes=0→404（非 403），PATCH 他人先查 existing→403；approve/reject 仅 status='pending' 生效（cursor.rowcount 守卫，重复→404），approve 写 published_at==updated_at、reject 存 trim 原因；公开详情非 approved 且非作者且非管理员→404；install pending 404、download_count 原子 +1 回读；通知两处（_notify_admins_pending 含管理员本人、_notify_author_review_result）均 logging.exception 吞异常不阻断主流程。
  - 测试新增 64 例全绿：test_marketplace_validate.py 19 函数/31 收集（参数化版本进位 13 例，覆盖 40+ 拒绝分支：空/超长/非法 slug 与 name、CSS 超限与 @import/外链、sample 三态、组件 PascalCase/危险标签/onxxx/javascript:/props 类型与嵌套/紧凑序列化、cover 协议、update empty_update 与字段忽略与版本服务端化、reject 截断）；test_marketplace_contract.py 27 例（8 端点 401/坏 token、空目录、分页归一化、排序 popular/newest 与 q 三列 LIKE、类型隔离、五级可见性、发布 shape 与组件、坏 JSON、ghost 合法 JWT 用户不存在 /me 200 空列表而发布 404、slug 唯一 409 与跨类型允许、free 5 次后 429 字段断言、pro/admin 6 次放行、pending 队列 403/404/ASC/type 过滤、approve 重复 404 与 publishedAt 时点、reject 原因 trim 与作者可见公开 404、PATCH 403/404/empty_update/1.0.1/流转清原因、DELETE 他人 404 与本人 ok、install 404 与 3→4→5 计数、/me 全状态 DESC+rejectReason）；test_marketplace_notify.py 6 例（TR-15.2：新提交通知全部已注册管理员、未登录白名单管理员不收、管理员作者自发自收、approve 仅作者 marketplace_approved payload 五字段、reject marketplace_rejected 带原因、驳回后更新重提再次通知、monkeypatch notify_users 抛异常发布仍 201）。
  - 修正：① 组件更新用例 name="x" 先撞 name 校验（name 在 template 前），改 PascalCase 后命中 unsafe_component_template；② payload 超限原以 description 撑大会先被截断 2000，改用不截断的 template；③ seed_item 默认 slug 与 item_id 联动消除同作者同类型唯一键冲突；④ ghost /me 期望由 401 修正为 200 空列表（上游 listMy 不加载用户，404 仅在发布/管理端加载用户时发生）；⑤ _parse_cover_url 的 urlparse 上移为模块级 import。
  - 回归：ruff check src tests scripts 通过；pytest 全量 934 例全绿（较 T14 的 870 新增 64 例）；文件名规范扫描对应用目录的 15 条违规全部为 T3 既有迁移编号（0001-0008）、前端 dist 哈希无扩展名产物与 .whl/.typed/.sha256 构建文件，T15 新增文件零违规；AST 守护（禁 from __future__ import annotations）随全量测试通过；零新增运行时依赖。
  - 契约差异（T21 contract-differences 汇总）：通知发送失败仅 logging.exception 不影响发布（上游同为 try/catch 吞掉，行为一致）；发布限流计数以 sqlite marketplace_rate_limits(scope_key,day_key,count) 持久化替代 Workers D1；dayKey/retryAfterSec 经核对上游 marketplace-db.ts:349-358 用 getUTCDate/Date.UTC 即 UTC 日界（非 Asia/Shanghai），Python 侧 day_retry_after_sec 同为 UTC 0 点剩余秒、floor、min 1，逐字一致无差异。

## Task 16: 表情资产与通知

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: T3, T10, T13
- **Description**:
  - emoji-validate（4 MIME 映射、5MiB、magic bytes：PNG 8 字节/JPEG 3/GIF 头 6/RIFF+WEBP；名称净化 basename/控制字符/截断 100/兜底 emoji；包名截断 60）；emoji-db（用户包 ON CONFLICT DO NOTHING、≤100 条件 INSERT HAVING COUNT、失败回滚对象、sort_order、级联删、manifest 结构与 url encodeURIComponent）；资产走 LocalBackend 或 S3（替代 EMOJI_ASSETS 独立桶：配置独立前缀/桶）；响应头 ETag/nosniff/immutable vs max-age=300。
  - notifications：3 类型、payload 兜底解析、分页 30/50、属主 404、幂等已读、read-all、DELETE。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-16.1: magic bytes 伪造 4 类被拦；第 101 个返回 409 且对象回滚；缓存头/manifest/级联删除断言；证据：test_emoji.py。
  - `rule` TR-16.2: 通知五端点分支全绿；证据：test_notifications.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建源码 5 处：server/emoji_validate.py（upstream emoji-validate.ts 1:1：EMOJI_MAX_ITEMS=100、MIME_EXTENSIONS 四类、validate_emoji_file 判别联合 empty_file/file_too_large（UPLOAD_MAX_BYTES 5MiB 共享常量、错误带 maxBytes）/invalid_file_type（MIME trim+lower 白名单）/mime_mismatch（PNG 8 字节 89504E470D0A1A0A、JPEG FFD8FF、GIF GIF87a/GIF89a、WEBP RIFF@0+WEBP@8）；sanitize_emoji_name 按 `[\\/]` split 取末段→去末段扩展名→剔 U+0000-1F/U+007F 控制字符→`\s+`折单空格→trim→截 100→空兜底 "emoji"；sanitize_pack_name 非 str→None、截 60、空→None）、server/emoji_db.py（USER_PACK_NAME="My Emojis"、slug 前缀 user-；get_pack_by_slug/get_system_pack（kind=system ORDER BY created_at ASC LIMIT 1）/get_or_create_user_pack（uuid4 + ON CONFLICT(owner_user_id) DO NOTHING 后回读，失败抛 RuntimeError emoji_pack_create_failed）/list_pack_items（sort_order ASC,id ASC）/update_user_pack_name/insert_user_emoji_item_conditional（**单条 INSERT...SELECT...LEFT JOIN...GROUP BY p.id HAVING COUNT(i.id) < 100**，sort_order=COALESCE(MAX,-1)+1，rowcount==1 返 bool）/get_emoji_asset（JOIN 带 p.kind）/get_owned_emoji_item/delete_owned_emoji_item/delete_user_pack（`with conn:` 事务先 items 后 pack），每函数末尾 commit）、server/emoji_storage.py（PrefixedStorage 统一加键前缀 + build_emoji_backend：默认 local 专用 config.emoji_local_dir；s3 且 emoji_s3_bucket 非空=独立桶无前缀（键名逐字 `user/<uid>/<id>.<ext>`），留空=复用 upload_s3_bucket 加 emoji_prefix（默认 "emoji"）隔离；凭证不全或未知 backend 兜底 LocalBackend）、server/routers/emojis.py（APIRouter prefix=/emojis）、server/routers/notifications.py（APIRouter prefix=/notifications）。
  - 修改 3 处：storage.py 新增 @dataclass(slots=True) StoredObject(data, content_type, etag) 与 ABC 抽象 get/delete；LocalBackend get（etag 为对象 MD5 hex 带引号、content_type=None）+ delete（单键/列表、FileNotFoundError 静默、沿用 _safe_target 穿越防护）；S3Backend get（SigV4 GET EMPTY_SHA256、404→None、其他非 2xx "S3 get failed"、etag 缺省回退 md5，path-style/vhost 双形态）+ delete（单对象 SigV4 DELETE 404 静默；多对象 POST `?delete` XML `<Delete><Object><Key>xml_escape</Key>...<Quiet>true</Quiet>` + Content-MD5=base64(md5(body))，**canonical query 为 "delete="**，非 2xx "S3 batch delete failed"，空列表 no-op）。config.py 新增 emoji_backend/emoji_local_dir（data/emoji-assets）/emoji_s3_bucket/emoji_s3_public_url 四字段及 DOOCS_MD_PY_EMOJI_* 环境映射；app.py 构建 emoji_storage（共享注入 http_client）并在 marketplace 后挂 emojis_router（index.ts:50）、notifications_router（index.ts:63）。
  - 表情路由契约点：item_json camelCase（sortOrder/createdAt/updatedAt）、url=`<origin>/emojis/assets/<quote(id,safe='')>`；manifest_json metadata 六键。GET /default 公开（无系统包 404）；GET /assets/{id} 公开（DB 取 kind/object_key/mime/size，存储缺失 404；**Cache-Control 系统包 `public, max-age=31536000, immutable`，用户包 `public, max-age=300`**；Content-Type/Content-Length 取 DB 记录（逐字上游 c.req 行为，非对象实际长度）、ETag(obj.etag)、X-Content-Type-Options: nosniff）；GET/PATCH /me（坏 JSON→None→invalid_name 400；空名 400；get_or_create→改名→回读 manifest）；POST /me/items（multipart；非 UploadFile→file_required；size<=0 empty_file；>5MiB file_too_large；validate 映射；object_key=`user/<uid>/<uuid4>.<ext>`；**先 put 对象再条件 insert：put 异常→502 asset_upload_failed；insert 异常→删对象+500 database_write_failed；第 101 项 inserted False→删对象回滚+409 item_limit_reached{limit:100}；成功 201 完整 manifest**）；DELETE /me/items/{id}（非属主/缺失 404→删对象失败 502 asset_delete_failed→删行 False 404→回 manifest）；DELETE /me（列 items 批量删对象失败 502→delete_user_pack→{ok:true}）。
  - 通知路由契约点：DEFAULT_PAGE_SIZE=30/MAX_PAGE_SIZE=50（page<1/非数→1；pageSize 归一 min(n,50)）；GET "" 与 "/" 双装饰返回 {items,total,page,pageSize}，query 参数逐字 camelCase `pageSize`；GET /unread-count→{count}；**POST /read-all 必须先于 POST /{notification_id}/read 注册**（已用专门用例锁定静态路径不被动态路由吞掉）；属主条件 get_notification_by_id 缺失/他人一律 404；read_at is None 才标记，幂等不覆盖；DELETE 双装饰 clear_all；五端点均 Depends(get_db)+Depends(require_user)。
  - 测试新增 4 文件 92 例全绿：test_emoji_validate.py 19 例（四类 magic 接受含 GIF87a/89a、五种伪造、MIME 大小写空白归一、空/超限、EMOJI_MAX_ITEMS 字面、名称净化含上游同向量 `"folder\\ happy\x00   face.png"→"happy face"`、路径/扩展名/控制字符/兜底/截断 100、包名截 60 与非 str）；test_emoji_db.py 14 例（系统包种子、用户包幂等 created_at 不覆盖、sort_order 0,1、无包插入 False、**第 101 个 False 且无残留行**、属主查询/删除、改名、整包删除后重建 slug 复用、PRAGMA foreign_keys=ON 级联）；test_emoji_routes.py 32 例（五端点 401 矩阵、default/me shape、改名 400/200/坏 JSON、上传成功名称净化与对象落盘、四类 magic 伪造 400 且无文件、四类全接受、invalid_file_type/file_required/empty_file/超限 maxBytes/非法 multipart→invalid_form_data/filename 兜底、**第 101 项 409+物理对象恰好 100 个回滚**、用户资产 max-age=300+ETag 引号+nosniff、系统资产 immutable（直插 sys1+写文件）、资产双 404、单项删除、整包级联对象+items+pack 全清后重建空包、put/delete 故障 502）；test_notifications.py 16 例（401/invalid_token、空列表默认分页、DESC/shape 五键/属主隔离、分页归一化全分支、未读计数、404 缺失+他人、幂等已读不覆盖 read_at、read-all 不影响他人与已读、/read-all 不被吞、clear-all 隔离且幂等、payload 损坏兜底与 rejectReason=42 数字透传）；test_emoji_s3_storage.py 18 例（GET vhost/path-style `$`编码录制、404→None、403 raise；单删 DELETE 录制/404 静默/403 raise；**批删 POST /?delete 录制：XML 三 Key 含 `c&amp;d` 转义、Quiet true、Content-MD5 自洽，并用 sign_sigv4 重算逐字节断言 Authorization（canonical query "delete=" 参签）**；批删 path-style、500 raise、空列表不发请求；PrefixedStorage 前缀记录；build_emoji_backend 五分支）。
  - 上游事实核对：0007 种子仅建 system-default 空 pack、0008 仅清理 system-coolapk 并 upsert pack 元数据，**两迁移均无系统 emoji_items 种子**，系统资产由运维直灌 EMOJI_ASSETS R2 桶+DB（wrangler.toml:23 binding），Python 侧行为等价（系统 immutable 路径由测试直插行覆盖）。
  - 踩坑固化：**FastAPI 0.115 下 `fastapi.datastructures.UploadFile` 与 Starlette multipart 实际产生的 `starlette.datastructures.UploadFile` 不是同一个类，isinstance 必 False 导致 file_required 假失败；本项目统一从 starlette.datastructures / starlette.responses 导入 UploadFile/JSONResponse**（upload.py 既有约定，本任务续用）。
  - 回归：ruff check src tests scripts 通过；pytest 全量 1026 例全绿（较 T15 的 934 新增 92 例）；AST 守护随全量测试通过；零新增运行时依赖。
  - 契约差异（T21 contract-differences 汇总）：① EMOJI_ASSETS 独立 R2 binding → 默认 LocalBackend 专用 data/emoji-assets 目录，或 S3Backend（独立桶无前缀/复用上传桶加 emoji/ 前缀），资产字节始终经本服务读出发（上游同）；② 表情 get/单删/DeleteObjects 批删为手写 SigV4（GET/DELETE 空体 EMPTY_SHA256；批删 POST ?delete XML+Content-MD5，canonical query "delete="）；③ 本地后端 ETag 用对象 MD5 hex 带引号（R2 httpEtag 等价物），Content-Type 不持久化、以 DB mime 为准；④ Content-Length 头发 DB 记录的 size（逐字上游）；⑤ 静态文件/DB 均不内置系统表情 items（上游同样靠外部灌桶，0007/0008 无 items 种子）。

## Task 17: 爱发电 webhook 与手动激活

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: T10, T11
- **Description**:
  - afdian client（api_base 去尾斜杠、md5 签名拼接、query-order POST {user_id,params,ts,sign}、ec!=200 空、list[0]、isProEligibleOrder status=2/product_type 0,1/plan 白名单空=全接受）。
  - webhook 路由（path token 403、未配置静默 200、坏 JSON 400、非 order/缺单号/查无/未支付/remark 无登录名静默 200、命中激活）；activate 路由（503/400/404/403 remark_mismatch/成功 {plan,planExpiresAt}）；activateProFromOrder（不合格/用户不存在/幂等返回/batch：UPDATE users + INSERT afdian_orders）。
  - 功能总开关默认关闭（不配置 AFDIAN_USER_ID/API_TOKEN）。
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements**:
  - `rule` TR-17.1: 签名已知答案向量（token/params/ts/user_id→md5）；全分支 MockTransport 测试；续费 max 语义与幂等（同单号两次返回相同到期）；证据：test_afdian.py。
- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - 新建 server/afdian.py（upstream: apps/api/src/afdian.ts 1:1）：AfdianOrder dataclass（title 可选）+ from_dict（字符串字段缺失归空串、number 字段保留原值交资格判定）；sign 用标准库 hashlib.md5 拼接 `token+"params"+params+"ts"+ts+"user_id"+user_id`（# noqa: S324，零新增依赖）；`_api_base` 用 `re.sub(r"/$","",…)` 仅去末尾一个斜杠（逐字上游非贪婪 replace）；afdian_request 未配置 user_id/token 抛 RuntimeError afdian_not_configured，params=JSON.stringify 等价（ensure_ascii=False、紧凑分隔符），POST {user_id,params,ts,sign} 到 `<base>/query-order`，Content-Type application/json，直接 response.json() 不校验 HTTP 状态码；query_order 对 ec!=200、data/list 缺失或空、非 dict 响应均回 None，取 list[0]；is_pro_eligible_order 三条件 status==2、product_type∈{0,1}、plan 白名单空=全接受否则 plan_id 命中（白名单复用 config._csv 解析）。
  - 修改 server/plan.py：新增 activate_pro_from_order（upstream: plan.ts:166-195）——不合格→`{ok:False,reason:"ineligible_plan"}`；get_user_by_github_login 缺失→user_not_found；is_order_processed 幂等短路回库中 plan_expires_at（NULL 时回当前时刻，逐字 `?? Date.now()`）；否则 extend_plan_expires 续期，`with conn:` 单事务 batch（UPDATE users SET plan='pro' + INSERT afdian_orders 五列 out_trade_no/user_id/github_login/months/processed_at）。新增 db.is_order_processed（plan.ts:158-164）；plan.py 顶层新增 `from . import db` / `from .afdian import …`（db 顶层不反向依赖 plan，无循环导入风险，经 create_app 实测）。
  - 新建 server/routers/webhooks.py（upstream: webhook.ts 1:1，index.ts:40-41 公开端点）：双装饰器 POST /webhooks/afdian 与 /webhooks/afdian/{token}；顺序严格按上游——① 配置 AFDIAN_WEBHOOK_TOKEN 且 path token 不匹配→403 `{"ec":403,"em":"forbidden"}`（无 token 路径同样 403，令牌校验先于一切、零回查）；② 未配置 API 凭证→静默 200 `{"ec":200,"em":""}`（在 JSON 解析之前，坏 body 也 200）；③ 坏 JSON→400 `{"ec":400,"em":"invalid_body"}`；④ 非 dict/ data.type!="order"/order 非 dict/out_trade_no 非字符串或 trim 后空→静默 200 且零回查；⑤ query_order 回查 None 或 status!=2→200；⑥ parse_github_login_from_remark 无登录名→200；⑦ 命中则 activate_pro_from_order（结果刻意忽略，用户不存在等仍 200）。**安全契约：回调体仅 out_trade_no 被采信，订单事实以开放平台回查为准，伪造 status/remark 字段无效**（测试固化）。
  - 修改 server/routers/sync.py：/sync/activate 从 503 占位接为完整实现（upstream: activate.ts:9-53）——503 afdian_not_configured→坏 JSON 400 invalid_body→orderNo trim 空 400 order_no_required→get_user_by_id 缺失 404 not_found→query_order None 404 order_not_found→status!=2 400 order_not_paid→remark 登录名存在且 != user.login.lower() 403 remark_mismatch（备注无登录名不拦截，按当前用户激活）→activate_pro_from_order 失败 user_not_found=404/其余=400→成功 200 {plan:get_effective_plan("pro"), planExpiresAt}；新增 get_http_client 依赖注入。app.py 挂载 webhooks_router（位于 auth 之后，对齐 index.ts:40-41）。
  - 配置沿用 T10 既有字段（afdian_user_id/afdian_api_token/afdian_api_base/afdian_pro_plan_ids/afdian_webhook_token，env 无前缀对齐上游 AFDIAN_* 命名）；功能默认关闭：默认 Config 下 /sync/activate 503、webhook 200（既有 test_sync_contract 未回归）。
  - 测试新增 tests/server/test_afdian.py 56 例全绿：① 签名已知答案向量 `378c76ef644fb7a11ed0ec0584b0aaeb`（独立进程预计算，锁定拼接顺序）；② 资格判定 status/product_type/白名单 7 例；③ query_order 请求录制（去尾斜杠 URL、POST、Content-Type、body 四键、params 为 JSON 串、ts 固定/默认、sign 用实际 params 重算一致）+ 9 种畸形/空响应 None + 未配置 RuntimeError 且零请求；④ activate_pro_from_order 10 例（三种不合格且无写库、用户不存在、成功 batch 五列断言、目标登录名大小写不敏感落库取行内 login、未来到期 max 续费、过期回落 now、month=0 兜 1、**同单号重复携带不同 month/不同 now 仍返回相同到期且订单行数 1**、processed 但 plan_expires_at NULL 回 now 分支）；⑤ webhook 11 例（错/缺令牌 403 零回查、未配置坏 JSON 200、配置后坏 JSON 400、9 种 body 静默零回查、查无/未支付、中文备注无登录名、**命中激活+伪造 status/remark 字段无效+伪造 W2 回查 status=3 不激活**、未知登录名仍 200、双回调幂等）；⑥ /sync/activate 12 分支（401、未配置 503 零请求、坏 JSON 400、5 种缺单号 400、幽灵用户 404 零回查、order_not_found、order_not_paid、remark_mismatch 403 无写库、product_type=2 与白名单不匹配 400、成功+github:大小写备注第二单在首单到期上叠加 31 天+/me 反映 pro、**同单号两次 planExpiresAt 相同但每次均回查开放平台（幂等只在 DB 激活层）**）。
  - 回归：ruff check src tests scripts 通过；pytest 全量 1082 例全绿（较 T16 的 1026 新增 56 例）；AST 守护随全量测试通过；零新增运行时依赖（md5=hashlib、HTTP=既有 httpx）。
  - 契约差异（T21 contract-differences 汇总）：① 爱发电 API 在 Workers 经 fetch 调用、本服务经注入 httpx.Client（15s 客户端默认超时，上游无超时概念）；② D1 batch 两语句→SQLite `with conn:` 单事务，失败整体回滚；③ AFDIAN_* 环境变量名逐字保留上游无前缀命名（区别于本项目 DOOCS_MD_PY_ 前缀的新增变量）；④ webhook 错误/成功应答体为爱发电平台约定的 {ec,em}（非本服务统一 {error} 形态），直接返回 starlette JSONResponse。

## Task 18: MCP Server（stdio，13 工具）

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: T9
- **Description**:
  - 实测官方 `mcp` SDK 的 3.14 兼容性（Q2/A6）；可用则用，不可用则按 MCP 规范手写 stdio JSON-RPC 2.0（initialize/notifications/tools/list/tools/ccall）最小传输。
  - 13 工具同名注册：render_markdown（**20 入参** zod 等价校验：hex 正则、px 正则、无单位数字正则、枚举、headingStyles 对象、默认值）、list_themes/colors/fonts/font_sizes/legend_formats/heading_styles/spacing_options/color_options/code_block_themes/ai_services（字面值从 config-options.ts 与 shared/configs/ai-service-options.ts 原样转录为 Python 数据资产）、explain_extensions（说明文案逐字）、get_renderer_options（选项表逐字）。
  - 输出 JSON 形状 `{content:[{type:'text',text: JSON.stringify(payload)}]}`；stderr 启动行/fatal 行等价。
- **Acceptance Criteria Addressed**: AC-13
- **Test Requirements**:
  - `rule` TR-18.1: initialize→tools/list 断言 13 工具名与 render_markdown 入参 **20** 个、默认值、非法 hex/px 拒绝；证据：test_mcp_server.py。
  - `rule` TR-18.2: 12 清单工具快照与上游字面值 diff 为空（转录资产与 TS 源提取结果做比对脚本，或评审快照）；证据：test_mcp_option_snapshots.py + 数据资产文件。

- **Evidence（2026-10-15 完成，session sc-20261014-md-py-replica）**:
  - **实现路径决策（I 阶段，依据 spec A6 回退条款）**：venv 实测 `mcp` 为 2.3.0，v2 已删除上游 1:1 复刻所需入口——`mcp.server.fastmcp` 导入即抛 ModuleNotFoundError 并提示改名 `mcp.server.mcpserver.MCPServer`，v1 内存直连测试助手 `create_connected_server_and_client_session` 亦已不存在；pyproject 的 `mcp>=1.2` 上下界无法表达「必须是 v1 形态」。故按 MCP 规范手写最小 stdio JSON-RPC 2.0 传输层，收益：零新增运行时依赖（NFR-2）、payload 字面值与键序可逐字控制、可在进程内以真实 JSON-RPC 帧断言 initialize/tools/list/tools/call。
  - 新增 `src/doocs_md_py/mcp_server/` 六个模块：`options.py`（15 组字面值常量：COLOR_OPTIONS 11 / THEME_OPTIONS 3 / FONT_FAMILY_OPTIONS 3 / FONT_SIZE_OPTIONS 5 / LINE_HEIGHT_OPTIONS 5 / BLOCK_SPACING_OPTIONS 5 / LINK_COLOR_OPTIONS 3 / BLOCKQUOTE_BACKGROUND_OPTIONS 3 / LEGEND_OPTIONS 6 / HEADING_STYLE_OPTIONS 5 / HEADING_LEVELS 6 / AI_SERVICE_OPTIONS 21 / EXTENSION_DOCS 11 / RENDERER_OPTION_DOCS 19 / DEFAULT_SERVICE_ENDPOINT，逐条 `# upstream:` 标注行号）、`schema.py`（RENDER_MARKDOWN_INPUT_SCHEMA 20 properties + `required:["markdown"]` + 10 个 default + 4 条 pattern + 4 组 enum；`parse_render_input` 实现 zod `.parse` 等价）、`tools.py`（13 个 ToolSpec 注册表 + `RENDER_INPUT_FIELDS` + `call_tool`/`list_tools_payload`）、`stdio.py`（JSONRPC_VERSION/四个错误码/SUPPORTED_PROTOCOL_VERSIONS/`json_dumps`/`_content_result`/`McpStdioServer` 的 `_result`/`_error`/`_negotiate`/`handle_message`/`_handle_call_tool`/`handle_line`/`serve`/`main`）、`__init__.py`（导出面）、`__main__.py`（`python -m doocs_md_py.mcp_server`）。
  - zod 语义等价四条：① strip 未知键；② `.optional().default(x)` → 缺省填默认值且不入 required；③ 显式 `null` 视为类型错误（`.optional()` 只放宽 `undefined`）；④ 报错文案逐字复刻上游第二实参（`Must be a valid 6-digit hex color` / `Must be a pixel size like 16px` / `Must be a unitless number like 1.75` / `Must be a unitless number like 1`）与 zod v3 枚举句式 `Invalid enum value. Expected 'a' | 'b', received 'x'`。TS→Python 去偏两条（不改变接受集）：JS `\d` 仅 ASCII、Python `re` 默认 Unicode → 一律写 `[0-9]`；JSON Schema 无 `/i` 标志 → hex 正则展开为 `[0-9A-Fa-f]`。
  - 协议边界（本仓契约，测试固化）：`initialize` 回显命中值否则回退 `2025-06-18`（SUPPORTED 含 2025-06-18/2025-03-26/2024-11-05）、capabilities 固定 `{"tools":{"listChanged":false}}`、支持 `ping`、通知（无 id）静默、坏 JSON -32700、非法请求形状 -32600、未知方法 -32601、未知工具/arguments 非对象/缺 name -32602、工具执行异常以 `isError:true` 结果返回（不抛回传输层）。
  - **本任务实测发现并修复的实现缺陷**：`_render_markdown` 原把 `parse_render_input` 输出的 camelCase 键直传 `RenderArticleInput(**parsed)`（snake_case 字段），实际抛 `TypeError: unexpected keyword argument 'primaryColor'` 并被 isError 兜底掩盖；已在 `tools.py` 新增 `RENDER_INPUT_FIELDS`（20 项 JSON 键 → dataclass 字段显式映射，因 `customCSS`→`custom_css` 无法由驼峰转换机械推导）并逐项映射后构造入参；配套 `test_render_input_field_mapping_is_total` 双向锁定（键集 == schema.properties、值集 == dataclasses.fields），防同类漂移再犯。
  - 新增 `scripts/mcp_options_snapshot_regen.py`（约 550 行，不 import 本包）：内建模板字面量/注释/正则感知的词法跳过器（`_skip_span`/`find_closer`/`iter_objects`/`parse_object`/`split_commas`/`eval_expr`），从上游 `packages/mcp-server/src/index.ts`、`config-options.ts`、`packages/shared/src/configs/ai-service-options.ts`、`packages/shared/src/constants/ai-config.ts` **机械提取**字面值，生成 `tests/golden/mcp_options_snapshot.json`（57.9KB，含四源 sha256、tool_order 13、tool_descriptions、schema{fields/required/defaults/enums/patterns}、raw 17 组、12 工具 payload）；脚本内置 `_EXPECTED_COUNTS` 断言（20 zod 字段/13 注册工具/各表条数）防止提取漂移。上游目录默认 `<repo>/.chaos/libs/md`，可经 `MD_UPSTREAM_DIR` 覆盖；输出 `regenerated: tests/golden/mcp_options_snapshot.json (tools=12, schema_fields=20, extensions=11, renderer_options=19)`。
  - TR-18.2 双向对拍结论：黄金快照与 Python 转录 **22 类比对 0 处不一致**（10 组选项表 + 代码块前缀/10 主题 URL + default_service_endpoint + service_options 21 + heading_levels + extensions 11 + renderer_options 19 + tool_order + 13 条描述 + schema 五段 + 12 工具 payload 按 `json_dumps` 逐字节）。
  - 新增测试 `tests/mcp/__init__.py`、`tests/mcp/test_mcp_server.py`（TR-18.1）、`tests/mcp/test_mcp_option_snapshots.py`（TR-18.2），共 **72 例**：13 工具注册序与 tools/list 载荷、仅 render_markdown 声明非空 schema、20 字段名序/required/10 默认值/类型、`parse_render_input` 三语义、15 例非法入参逐字文案（含 hex/px/无单位/4 组枚举/布尔与字符串类型错/显式 null/数组传入对象字段）、多错并列按行拼接、10 个候选 URL 枚举文案、`tools/call` 往返形状、注入 `code_css_fetcher` 实证（断言收到主题 URL 且 CSS 进入 html，避免真实联网）、省略 arguments、handler 异常转 isError、initialize 版本协商三分支、ping、通知静默、-32600/-32700/-32601/-32602 四类错误、serve 循环（stderr 启动行、空行与空白行跳过、应答计数与 id 序）、空 stdin 退出 0、fatal 分支、`mdpy mcp` CLI 接线（monkeypatch stdin/stdout 驱动真实帧）。
  - 修改 `src/doocs_md_py/cli.py`：`_handle_mcp` 接线（`mdpy mcp` → `mcp_server.main()`）并从 `main()` 分发；`tests/test_cli.py` 断言同步（mcp 从「占位退出码 2」参数集中移除）。
  - 修改 `pyproject.toml`：移除 `mcp>=1.2` 运行时依赖声明（全仓 grep 确认零 `import mcp`，手写传输层不消费该包；保留未使用的运行时依赖违反 NFR-2 最小化）。
  - 回归：`ruff check src tests scripts` 全通过；pytest 全量 **1153 例全绿**（基线 1082 + 新增 72 − 移除 1 例 mcp 占位断言）；AST 守护（`tests/test_no_future_annotations.py`）随全量通过；零新增运行时依赖（stdlib json/sys/dataclasses）。
  - spec 更正（A1：与磁盘冲突以磁盘为准）：spec.md 与 tasks.md 原文记 `render_markdown` 为「19 个入参」，实测上游 `index.ts:26-137` 的 zod 顶层字段为 **20 个**（含 `markdown`）；「19」源自 `get_renderer_options` 的 19 行选项表，二者被混算。已在 spec.md 背景事实（MCP 段）与 tasks.md 本任务 Description/TR-18.1 就地更正并注明更正理由。
  - 契约差异（T21 contract-differences 汇总）：① 传输层由官方 TS SDK（`McpServer` + `StdioServerTransport`）改为手写 stdio JSON-RPC 2.0（mcp 2.3.0 不兼容实证见上）；② `initialize` result 形状与 capabilities 取值由本仓实现定义（SDK 版本间会追加字段），非上游可对拍项；③ 入参校验失败文案直接以 `content[0].text` 承载（SDK 会再包一层 `MCP error -32602: Input validation error: ...` 前缀），故文案逐字对齐的是 zod 原始 message；④ JSON Schema 两条去偏（`\d`→`[0-9]`、hex 大小写敏感展开 `[0-9A-Fa-f]`）不改变接受集但使 pattern 字面与上游 zod 正则不同；⑤ 协议协商候选集与缺省版本（`2025-06-18`）取自本仓当时规范版本，SDK 内部协商策略不逐字复刻；⑥ `pyproject.toml` 删除 `mcp` 依赖声明。

## Task 19: mdpy CLI 与同源静态托管

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: T2, T9, T11, T12, T13, T14
- **Description**:
  - cli.py：`render`（-i/-o、stdin、主题与全部渲染选项 flags、输出完整文档或片段）、`serve`（默认 127.0.0.1、默认端口 8800 对齐 md-cli、占用自动换端口、--host 显式才允许外部、挂 API 全部路由 + 静态 dist：`/`index.html、hashed 资产长缓存、未命中路由 SPA 回退 index.html、favicon）、`upload`（--provider/--file/--config 或环境变量，打印 URL）、`mcp`（拉起 stdio）、`migrate`（显式初始化）。
  - 配置文件支持（~/.config/doocs-md-py/config 或 env 覆盖，凭证不入库）。
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `rule` TR-19.1: CLI 五子命令退出码/输出契约测试；render 与库调用结果一致；端口占用自动递增；证据：test_cli.py。
  - `rule` TR-19.2: TestClient E2E：首页 200、资产 200 缓存头、未知路径回退 index、同源 API 完成 token→push→pull→share 创建→GET /s/<id> 全链路；证据：test_serve_e2e.py。

## Task 20: 综合契约测试、覆盖率门禁与性能基准

- **Status**: `pending`
- **Priority**: high
- **Depends On**: T19, T15, T16, T17, T18
- **Description**:
  - 补齐 cross-cutting 测试：上游 `*.test.ts` 中被断言的边界逐条映射核对（sync-limits/share/marketplace/emoji/notifications/origin/plan/db）；错误体字段一致性全表；配置体检端点/启动日志；密钥不入日志断言。
  - 覆盖率配置（cov 源 src/doocs_md_py，门槛 80/90 per- module）；性能基准脚本（NFR-6）留档但不进 CI 红门。
  - 全量 ruff + pytest 绿；Windows/WSL 双平台跑一次（路径原语）。
- **Acceptance Criteria Addressed**: AC-16, AC-U1, AC-U2, AC-U3
- **Test Requirements**:
  - `rule` TR-20.1: `pytest --cov` 总覆盖 ≥80%、关键模块 ≥90% 的报告归档；ruff 零告警；证据：coverage 报告。
  - `rule` TR-20.2: 上游测试边界映射表每条有对应 Python 测试或差异说明；证据：docs/contract-mapping.md。
  - `rubric` TR-20.3: 复杂文档渲染保真度（AC-U1 同维度）；scale 1-5；threshold ≥4；证据：对拍报告（人工浏览渲染结果截图/DOM diff）。
  - `rubric` TR-20.4: 代码质量（模块边界清晰/魔数集中为常量/上游锚点注释完备/无硬编码凭证）；scale 1-5；anchors 1=魔数散落且无锚点/3=主模块有锚点但存在重复或缺注释/5=全部契约模块可定位上游文件且凭证仅来自配置；threshold ≥4；证据：全仓抽查记录（grep 密钥/魔数）+ 模块清单。

## Task 21: 应用文档、登记与交付说明

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: T20
- **Description**:
  - 应用 `README.md`：功能矩阵（含非目标渠道说明）、快速开始（venv→pip install→构建 dist→mdpy serve/migrate）、配置项全表（对齐 .env.example 并标注上游同名变量）、13 上传器用法、MCP 客户端配置示例、WTFPL 许可与上游版本/commit。
  - `docs/architecture.md`：模块 ↔ 上游文件映射总表（AC-U2/AC-U3 审计依据）；`docs/build-web-dist.md` 构建与回退预案；`docs/contract-differences.md`（所有发现的 JS/Python 行为差异及裁决，含 markdown-it vs marked 差异清单）。
  - 更新 `apps/AGENTS.md` 应用路由表与应用清单（先读其现有格式再按同格式登记）。
  - 若根 docs 需要发布向使用手册，按仓库双轨制在 docs/tech/guides/ 增补（视 apps 先例决定，不主动扩写）。
- **Acceptance Criteria Addressed**: AC-U4, AC-1（登记部分）
- **Test Requirements**:
  - `rule` TR-21.1: 链接检查（check-links.py 对变更目录）通过；apps/AGENTS.md 含新应用条目且路由字段完整；证据：脚本输出与 diff。
  - `rubric` TR-21.2: 新人按 README 从零到可访问（含 dist 构建）实操 ≤ 30 分钟无卡点；scale 1-5；anchors 1=无法完成/3=需口头补充/5=一次通过；threshold ≥4；证据：评审者实操记录入 review.md。
