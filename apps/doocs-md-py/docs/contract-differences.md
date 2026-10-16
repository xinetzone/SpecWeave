---
title: doocs-md-py 契约差异台账（JS ↔ Python）
source: d:/AI/.chaos/libs/md（doocs/md v2.1.0，package.json version=2.1.0，commit 1bdad48d20048bddc8d32afb1b75a6475169f163，2026-10-12）
date: 2026-10-16
---

# 契约差异台账

本文件登记 **doocs/md（TypeScript 单体仓库）** 与 **doocs-md-py（Python 复刻）** 之间所有已知的行为差异及其裁决，是 AC-U3「差异可追溯、有裁决」的交付证据，也是审计时判断"某处不一致到底是缺陷还是记录在案的差异"的唯一依据。

- 上游事实源：`d:/AI/.chaos/libs/md`，版本 **v2.1.0**，commit **1bdad48d20048bddc8d32afb1b75a6475169f163**。
- 上游路径根：下文所有 `packages/...`、`apps/...` 锚点均相对该 monorepo 根。
- 差异编号：`CD-n` 为本文件新登记项；`D-1..D-4` 为 T20 已在 [contract-mapping.md](contract-mapping.md) 逐条建档的服务端契约差异，此处只做摘要索引，**不重复抄录**。

## 一、差异总表

| 编号 | 层 | 差异要点 | 裁决 | 证据/锚点 |
|---|---|---|---|---|
| D-1..D-4 | 服务层 | uuid 回退分支、未命中路由响应体、`upload_max_bytes` 死配置、marked→markdown-it-py 归一化 DOM 对拍 | 见 [contract-mapping.md](contract-mapping.md) | T20 契约映射逐条档案 |
| CD-1 | 渲染层 | 围栏代码块 token 尾换行处理 | **对齐**（Python 侧显式去一个尾换行，逐字等价复现） | `packages/core/src/renderer/renderer-impl.ts` code() 分支 |
| CD-2 | 渲染层 | `calc()` 除法产出 `NaN<unit>` | **保留上游缺陷**（逐字复现，不修正） | `packages/shared/src/utils/cssProcessor.ts`（T8 黄金快照对拍） |
| CD-3 | 渲染层 | 无 highlight.js 语法着色 | **接受差异**（NFR-2 依赖白名单禁 pygments；包裹结构 1:1，前端 CDN 延迟 hydrate） | [highlight.py](../src/doocs_md_py/render/highlight.py) |
| CD-4 | 上传器 | 对象键日期取本地时区 | **接受差异**（Python 侧显式 UTC） | `packages/web/src/services/upload/providers.ts` getDir |
| CD-5 | 净化层 | DOMPurify → nh3 | **接受差异**（等价净化语义，白名单已对齐） | [sanitize.py](../src/doocs_md_py/render/sanitize.py) |
| CD-6 | 托管层 | express 静态 + 线上反代 → 同源托管 dist | **规格新增**（SPA 回退 + 哈希资产长缓存） | [web_dist.py](../src/doocs_md_py/server/web_dist.py) |
| CD-7 | CLI 层 | `get-port` 随机空闲端口 → 严格递增端口 | **改进**（确定性更强、可断言） | [app.py](../src/doocs_md_py/server/app.py) |
| CD-8 | 配置层 | 用户级配置文件为 Python 新增 | **规格新增**（凭证仍只入本地文件/环境变量，不入库） | [user_config.py](../src/doocs_md_py/user_config.py) |
| CD-9 | 扩展层 | 自定义图床（formCustom）执行用户 JS | **不复刻**（NG2：仓库内无任何执行用户 JS 的代码路径） | `packages/web/src/services/upload/providers.ts` formCustom |
| CD-10 | 前端产物 | NETLIFY 变体 `index.html` 内置上游 Google Analytics `gtag`（`G-7NZL3PZ0NK`） | **接受**（零源码补丁同源构建的必然产物；提供可选移除策略） | 见 §7.1 与 [build-web-dist.md](build-web-dist.md) |
| CD-11 | 配置层 | 缺省 `UPLOAD_ENABLED`：上游 `false`（仅 `"true"`/`"1"` 开启）vs 本仓 `true` | **接受差异**（自托管 local 后端零配置可用；`UPLOAD_ENABLED=false` 可关） | [config.py](../src/doocs_md_py/server/config.py) |
| CD-12 | 网络层 | 上游 Workers `fetch` 无超时概念；本仓注入 `httpx.Client` **15s 默认超时** | **规格新增**（自托管必须有超时，否则挂死） | [deps.py](../src/doocs_md_py/server/deps.py) |
| CD-13 | 部署约束 | SQLite 单连接 `check_same_thread=False`；自托管**单 worker**；多 worker 须各持文件连接 | **部署约束登记**（见 §7.4 与 [README](../README.md)） | [db.py](../src/doocs_md_py/server/db.py)、`routers/sync.py` |
| CD-14 | CLI 层 | 未知 `--provider` **显式报错**（退出码 2）；上游 `resolve_upload_provider` 静默回退 `default` | **改进**（拼写错误不再被静默吞掉） | [cli.py](../src/doocs_md_py/cli.py) |
| CD-15 | 分享层 | `title` 按 `trim` + `slice(200)` 截断：JS 以 **UTF-16 码元** 计长，Python 以**码点**计长 | **接受差异**（BMP 外字符截断位置可能不同） | [share.py](../src/doocs_md_py/server/routers/share.py) |
| CD-16 | 分享层 | 上游埋点正则 `[^"'>\s]*` 不消费危险 URL 属性的闭合引号，残留 `<a">` | **对齐**（逐字复现；分享页 CSP `script-src 'none'` 兜底） | [share.py](../src/doocs_md_py/server/routers/share.py) |
| CD-17 | 上传器 | qiniu-js 浏览器 SDK 的 region 对象模型 → **HTTP multipart 直传**（仅在显式 URL 时用 region，否则默认上传域） | **接受差异**（去掉浏览器 SDK 依赖） | [qiniu.py](../src/doocs_md_py/uploaders/qiniu.py) |
| CD-18 | 上传器 | dcloud 保留上游 `X-OSS-server-side-encrpytion` **原拼写**；OSS 响应不校验状态码 | **对齐**（逐字复现上游笔误与宽容行为） | [dcloud.py](../src/doocs_md_py/uploaders/dcloud.py) |
| CD-19 | 表情层 | 本地后端 ETag 用**对象 MD5 hex（带引号）**；`Content-Type` 不持久化，以 DB 记录的 mime 为准；`Content-Length` 取 DB 记录的 size | **等价**（对 R2 `httpEtag` 的等价替代） | [emojis.py](../src/doocs_md_py/server/routers/emojis.py) |
| CD-20 | 爱发电 | `AFDIAN_*` 环境变量**无前缀逐字保留**；webhook 应答体用平台约定 `{ec,em}` 而非统一 `{error}` | **对齐**（平台协议不可改） | [webhooks.py](../src/doocs_md_py/server/routers/webhooks.py) |
| CD-21 | MCP 层 | 官方 TS SDK（`McpServer`+`StdioServerTransport`）→ **手写 stdio JSON-RPC 2.0**；`initialize` 形状本仓定义；schema 去偏（`\d`→`[0-9]`、hex 大小写展开）；协议版本取本仓规范版；删除 `mcp` 依赖 | **规格新增**（`mcp` 2.3.0 对 Python 3.14 不兼容实证） | [stdio.py](../src/doocs_md_py/mcp_server/stdio.py) |

## 二、渲染层差异（NG6 裁决口径）

NG6 裁决口径为「**归一化 DOM 结构等价**」，而非 HTML 字节相等：忽略标签间换行/缩进与属性书写顺序，比较标签树、属性键值与文本节点（文本空白折叠为单空格）。因此下列差异在验收时**不构成失败**，但必须逐条登记。

### 2.1 markdown-it-py ↔ marked 差异清单

上游用 `marked`（含大量自定义 tokenizer/token 后处理），本仓用 `markdown-it-py` + 自定义 token 遍历。两者 token 模型不同，已知差异分三类：

| 类别 | 内容 | 处理方式 |
|---|---|---|
| 已定位并处理的**实质偏差** | ① 围栏代码块 token 尾换行（CD-1）；② `calc()` 除法 `NaN`（CD-2） | 逐字对齐上游产物，证据为黄金样例（`tests/golden/`） |
| **字节级不承诺** | 属性书写顺序、自闭合标签写法、实体转义形式、空白折叠前的原始字节 | 不做字节比对；以归一化 DOM 对拍验收 |
| **无覆盖的次要行为** | marked 内联规则优先级在极端嵌套输入下的边界case | 已用 `test_article_doc.py`（两例）/`test_complex_doc.py` 归一化 DOM 全等价覆盖；未被样例覆盖的极端输入不承诺等价 |

其余渲染细节为**逐字复刻**：17 条元素渲染规则、链接 href===text 时的输出、微信外链转脚注、图片 `alt|宽x高` 尺寸语法、代码块 `data-*` 包裹属性等，均按上游实现。（映射见 [architecture.md](architecture.md)。）

### 2.2 CD-1 围栏代码块尾换行

上游 `code()` 分支对 `token.text` 做「去掉恰好一个尾随换行」处理后再行转义与高亮；markdown-it-py 的 `fence` token 默认保留该换行。Python 侧在渲染前显式施加上游同款归一化，保证产物与黄金快照一致。

### 2.3 CD-2 `calc()` 除法保留上游缺陷

上游 `cssProcessor` 在 `calc()` 表达式中对 `--变量` 做解构时，除法分支会产出形如 `NaN<unit>` 的结果。经评估：

- 该行为属上游缺陷，但**会影响渲染产物的可观测输出**，且本仓验收口径是"与上游逐字等价"；
- 修正它反而会让产物与上游不一致，使黄金样例对拍失效。

**裁决：保留，逐字复现**，并在本节明确登记为「已知上游缺陷（非本仓缺陷）」。

### 2.4 CD-3 语法着色的能力落差

上游依赖 highlight.js 的注册语言集做语法着色，并在 `renderDiffCode` 中做 diff 高亮。本仓 NFR-2 运行期依赖白名单（fastapi / uvicorn / python-multipart / markdown-it-py / nh3 / PyJWT / httpx / pyyaml）**不含任何着色库**，故：

- 注册语言集为 `{plaintext}`，`code()` 仍产出与上游同构的包裹元素与 `class="language-xxx"`；
- 非 plaintext 语言额外产出三个 `data-language-pending` 属性，由前端 CDN 侧延迟 hydrate 完成着色；
- `renderDiffCode` 的上游行为不做等价承诺。

**影响**：不改变 DOM 结构，只影响代码块内部 span 级着色；纯渲染 API 的消费方若依赖 hljs span，需自行在后端补齐着色后端（本仓不提供）。

## 三、服务层差异（D-1..D-4 索引）

T20 已在上游 `apps/api/src/*.test.ts`（13 个测试文件、60 条 `it`）与本仓实现之间做逐条映射，并对无法等价的条目建档 `D-1..D-4`：uuid 回退分支、未命中路由响应体、`upload_max_bytes` 死配置、marked→markdown-it-py 归一化 DOM 对拍。**完整档案（含双端行号锚点、最小触发条件、关闭条件）见 [contract-mapping.md](contract-mapping.md)**，本文件仅作索引，避免第二事实源。

## 四、上传器差异

### 4.1 CD-4 对象键日期时区

上游 `getDir` 用浏览器/Node 本地时区拼 `YYYY/MM/DD`；服务端语义下本地时区会导致同一时刻不同部署产出不同键。本仓改为**显式 UTC**，保证同一时刻全球一致。差异已登记；如需与上游逐字一致，属部署方偏好，不在本仓承诺范围。

### 4.2 CD-9 formCustom 不执行用户 JS（NG2）

上游 `formCustom` 允许用户以配置形式注入并执行 JS 完成自定义上传。本仓 NG2 明确**仓库内不存在任何执行用户提供 JS/代码的路径**，因此：

- `formCustom` 仅保留配置形态与调用契约（`name` / `raw`），执行侧以 **Python 插件注册入口**替代；
- 任何"让用户脚本自己跑"的能力均不复刻，属**能力裁剪**而非实现差异。

### 4.3 图床数量 14 家（上游 13 家 + dcloud）

上游 `md-cli` 另外提供了 `dcloud`（DCloud/uni-app）上传通道，本仓将其登记进 provider 注册表，故图床总数为 **14 家**。该项为**新增**而非差异；用法与配置字段见应用 [README](../README.md)。

## 五、托管与 CLI 差异

| 编号 | 上游（md-cli） | 本仓 | 裁决 |
|---|---|---|---|
| CD-6 | `express.static` 托管本地 dist，其余路径反代线上站点 | 同源托管 T2 构建的 SPA：命中哈希资产给长缓存、其余路径回退 `index.html` | 规格新增契约；离线可用性优于上游 |
| CD-7 | `get-port` 取随机空闲端口 | 端口占用时**严格递增**探测 | 改进（确定性更强，便于断言与自动化） |
| CD-8 | 仅从 argv / 环境变量取配置 | 新增用户级配置文件 `~/.config/doocs-md-py/config`（`MD_*` 环境变量可覆盖） | 规格新增；凭证仍不入库 |

## 六、平台替代（非行为差异，登记备查）

以下为 spec 已声明的**平台级替代**（G2 约束、NG4 范围裁剪），不属于"行为差异"，但审计时需要一并知悉：

| 上游平台 | 本仓替代 | 说明 |
|---|---|---|
| Cloudflare Workers + D1 | FastAPI + SQLite（[db.py](../src/doocs_md_py/server/db.py)，迁移脚本由上游 SQL 原样移植） | 本地单机自托管形态 |
| Cloudflare R2 绑定 | S3 兼容后端（手写 SigV4；`UPLOAD_S3_*` 展开自上游 R2 绑定语义） | 见 [storage.py](../src/doocs_md_py/server/storage.py) |
| 云服务侧反代取客户端 IP | 本地自托管下取 `X-Forwarded-For` 首项，退化时取对端地址 | NG4 |
| Cloudflare Emoji / 市场等线上资源 | 本地 emoji 资产后端 + 可选 S3 后端 | `DOOCS_MD_PY_EMOJI_*` |
| Cloudflare D1（市场发布限流计数） | SQLite 表 `marketplace_rate_limits(scope_key, day_key, count)` | 持久化替代；UTC 日界经核对逐字一致（无行为差异） |
| D1 `batch` 双语句 | SQLite `with conn:` 单事务（失败整体回滚） | 等价事务语义（[爱发电激活](../src/doocs_md_py/server/routers/webhooks.py)） |

## 七、补登差异明细（CD-10..CD-21）

本节为 T22 补登：以下条目在实现期各任务的证据行中已声明，但未及时落盘到本台账（违反 §八第 1 条「未登记的差异一律按缺陷处理」）。逐条补录裁决与锚点。

### 7.1 CD-10 前端产物内置上游遥测脚本

T2 构建的 NETLIFY 变体 `index.html` 由上游源码零补丁产出，**必然包含**上游的 Google Analytics `gtag` 片段（测量 ID `G-7NZL3PZ0NK`）。裁决：**接受**——移除需修改产物或加构建期后处理，与「零源码补丁」的 TR-2.2 证据冲突，故不做默认移除。**可选移除策略**（部署方按需）：见 [build-web-dist.md](build-web-dist.md) 的分析脚本一节（产物构建后可对 `index.html` 做一次性 `gtag` 剥离，属部署侧后处理，不影响源码零补丁属性）。

### 7.2 CD-11 缺省 `UPLOAD_ENABLED`

上游缺省 `false`（仅显式 `"true"`/`"1"` 开启）；本仓缺省 `true`，与 `UPLOAD_BACKEND=local` 组合可零配置可用。裁决：**接受差异**，`UPLOAD_ENABLED=false` 可显式关闭。

### 7.3 CD-12 HTTP 客户端超时

上游 Workers `fetch` 无超时概念；本仓 `get_http_client` 用模块级 `httpx.Client` 并显式设 **15s** 默认超时（httpx 自身默认仅 5s，对图床/接口偏紧）。裁决：**规格新增**，自托管进程必须有超时以免请求挂死。该超时对爱发电 API、GitHub、各图床与表情后端一致生效。

### 7.4 CD-13 部署约束（单 worker / SQLite 连接）

`db.connect` 以 `check_same_thread=False` 建连：FastAPI 同步路由在线程池执行，单服务连接需跨线程复用；配套 **WAL** 与**单 worker** 自托管形态。**多 worker 部署须各持独立文件连接**（不可共享同一 `sqlite3.Connection`）。裁决：**部署约束登记**，同步路由因此以 `async def` 仅用于读取 JSON body，SQLite 调用在线程池直接执行。

### 7.5 CD-14 未知图床显式报错

上游 `resolve_upload_provider` 对未知值**静默回退** `default`；本仓 `mdpy upload` 对未知 `--provider` **显式报错**并置退出码 2。裁决：**改进**（避免拼写错误静默走错通道）。注意：库内 `resolve_upload_provider` 仍保留上游的回退语义（供服务端路由复用），差异仅在 CLI 边界。

### 7.6 CD-15 / CD-16 分享层补充

- **CD-15**：`title` 经 `trim` 后 `slice(200)` 截断——JS 按 **UTF-16 码元** 计长，Python 按 **码点** 计长，故含 BMP 外字符（如 emoji）时截断位置可能不同。裁决：**接受差异**（不影响功能，仅标题长度边界）。
- **CD-16**：上游分享页埋点正则 `[^"'>\s]*` 不消费危险 URL 属性的闭合引号，产物残留 `<a">` 形态。裁决：**对齐**（逐字复现，不自作修正）；安全性由分享页 `Content-Security-Policy: script-src 'none'` 兜底。

### 7.7 CD-17 / CD-18 上传器补充

- **CD-17**：上游用 qiniu-js 浏览器 SDK 的 region 对象模型；本仓收敛为 **HTTP multipart 直传**（`region` 仅在配置为显式上传 URL 时生效，否则用默认上传域）。裁决：**接受差异**（去浏览器 SDK 依赖）。
- **CD-18**：dcloud 通道逐字保留上游 `X-OSS-server-side-encrpytion` 的**原拼写**（上游笔误），且 OSS 响应**不校验状态码**（宽容行为）。裁决：**对齐**。

### 7.8 CD-19 表情资产 ETag 与响应头

本地/ S3 后端：ETag 用**对象 MD5 的 hex（带引号）**（对 R2 `httpEtag` 的等价物）；`Content-Type` 不持久化、以 DB 记录的 mime 为准；`Content-Length` 取 DB 记录的 size（逐字上游）。裁决：**等价**。另：静态文件与 DB 均不内置系统表情 items（上游同样靠外部灌桶，`0007`/`0008` 无 items 种子）。

### 7.9 CD-20 爱发电平台约定

- `AFDIAN_*` 环境变量名**逐字保留上游无前缀命名**（区别于本项目 `DOOCS_MD_PY_` 前缀的新增变量）。
- webhook 的成功/错误应答体为平台约定的 `{ec, em}`，**非**本服务统一的 `{error}` 形态（直接返回 `JSONResponse`）。
裁决：**对齐**（平台协议不可改）。

### 7.10 CD-21 MCP 传输与形状

① 传输层由官方 TS SDK（`McpServer` + `StdioServerTransport`）改为**手写 stdio JSON-RPC 2.0**（`mcp` 2.3.0 对 Python 3.14 不兼容的实证见 T18）；② `initialize` result 形状与 capabilities 取值由本仓实现定义（SDK 版本间会追加字段），**非可对拍项**；③ 入参校验失败文案直接以 `content[0].text` 承载，对齐的是 zod 原始 message（SDK 会再加 `MCP error -32602:` 前缀）；④ JSON Schema 两条去偏（`\d`→`[0-9]`、hex 大小写展开）不改变接受集，但使 pattern 字面与上游 zod 正则不同；⑤ 协议协商候选集与缺省版本（`2025-06-18`）取自本仓当时的规范版本；⑥ `pyproject.toml` 删除 `mcp` 依赖声明。裁决：**规格新增**。

## 八、差异维护约定

1. 新增差异必须先在本文件登记并给出裁决与锚点，再进入实现；未登记的差异一律按缺陷处理。
2. 上游升级（版本/commit 变更）时，本文件与 [contract-mapping.md](contract-mapping.md) 必须同步复核。
3. 已登记为"保留上游缺陷"的条目（当前仅 CD-2）不得在本仓单方面修正。
