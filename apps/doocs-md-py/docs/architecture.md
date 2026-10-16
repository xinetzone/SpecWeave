---
title: doocs-md-py 架构与上游映射总表
source: d:/AI/.chaos/libs/md（doocs/md v2.1.0，commit 1bdad48d20048bddc8d32afb1b75a6475169f163）
date: 2026-10-16
---

# 架构与上游映射总表

> **本文用途**：作为 **AC-U2**（可审计的上游对应关系）与 **AC-U3**（差异有据可查）的审计依据。审计员据此可从任一 Python 模块定位到上游文件与行号，进而判断该处是"逐字复刻""等价实现"还是"规格新增/裁剪"。
>
> **基线**：上游 `doocs/md` **v2.1.0**，commit **1bdad48d20048bddc8d32afb1b75a6475169f163**（2026-10-12）。下表所有上游路径均相对上游 monorepo 根；Python 路径均相对 `apps/doocs-md-py/src/doocs_md_py/`。
>
> **行为差异**（不是每条映射都逐字等价）全部集中登记在 [contract-differences.md](contract-differences.md)，请与本文对照阅读。

## 一、分层与数据流

本应用对外提供三条入口，共用同一渲染核心：

```
                 ┌──────────────────────────────────────────┐
   CLI 入口  ────►│  cli.py（mdpy render / serve / upload /  │
                 │  mcp / migrate）                          │
   MCP 入口  ────►│  mcp_server/（stdio JSON-RPC，13 工具）  │──► render/（渲染核心）
   HTTP 入口 ────►│  server/（FastAPI：认证/同步/分享/市场/   │      │
                 │  表情/上传/webhook）+ web_dist（同源 SPA）│      ▼
                 └──────────┬───────────────────┬───────────┘  markdown-it-py
                            │                   │              token 遍历
                            ▼                   ▼              → 归一化 DOM
                     SQLite（db.py +         对象存储
                     migrations/0001-0008）   （storage.py：local / S3）
```

- **渲染核心（render/）**：Markdown 文本 → HTML 片段，是 CLI、MCP、API 三入口的公共依赖；无 I/O 副作用。
- **服务层（server/）**：FastAPI 应用工厂 + 8 个路由组 + SQLite 持久化 + 对象存储 + 上传后端（GitHub / R2 等价 S3）。
- **上传器（uploaders/）**：面向浏览器侧 `apps/web` 上传通道的独立复刻，与 server 侧的 `/upload` 是**两套不同的上传路径**（前者为 Web 客户端图床清单，后者为 md-api 服务端上传接口）。
- **前端资产（assets/web-dist/）**：上游 `apps/web` 的 Vite 构建产物镜像（**不入库**），构建与回退见 [build-web-dist.md](build-web-dist.md)。

## 二、渲染核心 render/（27 模块）

| Python 模块 | 上游锚点 | 复刻口径 |
|---|---|---|
| [render/\_\_init\_\_.py](../src/doocs_md_py/render/__init__.py) | `packages/core/src/renderer/index.ts` | 包入口 |
| [render/options.py](../src/doocs_md_py/render/options.py) | `packages/shared/src/types/common.ts`（`IOpts`） | 1:1 |
| [render/article.py](../src/doocs_md_py/render/article.py) | `packages/mcp-server/src/render-article.ts`（`buildRenderedOutput`） | 1:1 |
| [render/markdown.py](../src/doocs_md_py/render/markdown.py) | `packages/core/src/utils/markdownHelpers.ts` | 流水线等价 |
| [render/renderer.py](../src/doocs_md_py/render/renderer.py) | `packages/core/src/renderer/renderer-impl.ts`（`RendererObject` 17 规则） | 逐字复刻 |
| [render/sanitize.py](../src/doocs_md_py/render/sanitize.py) | `packages/core/src/utils/markdownHelpers.ts:17`（`sanitizeHtml`） | 等价（后端换 nh3，见 CD-5） |
| [render/highlight.py](../src/doocs_md_py/render/highlight.py) | `renderer-impl.ts` `code()` / `renderDiffCode` + `languages.ts` | 包裹结构等价（无 hljs，见 CD-3） |
| [render/css.py](../src/doocs_md_py/render/css.py) | `packages/core/src/theme/cssVariables.ts` + `cssProcessor.ts` | 逐字复刻（含上游 `calc()` 缺陷，见 CD-2） |
| [render/frontmatter.py](../src/doocs_md_py/render/frontmatter.py) | `packages/core/src/utils/front-matter.ts` | 1:1 |
| [render/reading_time.py](../src/doocs_md_py/render/reading_time.py) | `packages/shared/src/utils/readingTime.ts` | 1:1 |
| [render/html_utils.py](../src/doocs_md_py/render/html_utils.py) | `basicHelpers.ts` + `renderer-impl.stripInlineHtml` | 等价 |
| [render/code_themes.py](../src/doocs_md_py/render/code_themes.py) | `packages/mcp-server/src/config-options.ts:105-136` | 1:1 |
| [render/domcompare.py](../src/doocs_md_py/render/domcompare.py) | —（本仓新增） | 黄金样例归一化 DOM 比较器（NG6 裁决工具） |

### 2.1 扩展 render/extensions/（14 模块）

| Python 模块 | 上游锚点 |
|---|---|
| [extensions/\_\_init\_\_.py](../src/doocs_md_py/render/extensions/__init__.py) | `packages/core/src/extensions/`（装配顺序对齐） |
| [extensions/alert.py](../src/doocs_md_py/render/extensions/alert.py) / [alert_data.py](../src/doocs_md_py/render/extensions/alert_data.py) | `extensions/alert.ts`（`markedAlert` / `defaultAlertVariant`） |
| [extensions/component.py](../src/doocs_md_py/render/extensions/component.py) / [component_data.py](../src/doocs_md_py/render/extensions/component_data.py) | `extensions/component.ts`（`BUILT_IN_COMPONENTS`） |
| [extensions/diagrams.py](../src/doocs_md_py/render/extensions/diagrams.py) | `extensions/{mermaid,plantuml,infographic}.ts` |
| [extensions/emoji.py](../src/doocs_md_py/render/extensions/emoji.py) / [emoji_data.py](../src/doocs_md_py/render/extensions/emoji_data.py) | `extensions/emoji.ts` / `emoji-data.ts`（`EMOJI_SHORTCODES`） |
| [extensions/footnotes.py](../src/doocs_md_py/render/extensions/footnotes.py) | `extensions/footnotes.ts`（`markedFootnotes`） |
| [extensions/katex.py](../src/doocs_md_py/render/extensions/katex.py) | `extensions/katex.ts` + `utils/mathDetection.ts` |
| [extensions/markup.py](../src/doocs_md_py/render/extensions/markup.py) | `extensions/markup.ts`（`markedMarkup`） |
| [extensions/ruby.py](../src/doocs_md_py/render/extensions/ruby.py) | `extensions/ruby.ts`（`markedRuby`） |
| [extensions/slider.py](../src/doocs_md_py/render/extensions/slider.py) | `extensions/slider.ts`（`markedSlider`） |
| [extensions/toc.py](../src/doocs_md_py/render/extensions/toc.py) | `extensions/toc.ts`（`markedToc`） |

## 三、MCP 服务 mcp_server/（6 模块）

| Python 模块 | 上游锚点 |
|---|---|
| [mcp_server/\_\_init\_\_.py](../src/doocs_md_py/mcp_server/__init__.py) | `packages/mcp-server/src` |
| [mcp_server/options.py](../src/doocs_md_py/mcp_server/options.py) | `packages/mcp-server/src/config-options.ts`（11 组选项 + 代码块主题） |
| [mcp_server/schema.py](../src/doocs_md_py/mcp_server/schema.py) | `packages/mcp-server/src/index.ts:24-137`（`render_markdown` 入参 schema） |
| [mcp_server/stdio.py](../src/doocs_md_py/mcp_server/stdio.py) | `packages/mcp-server/src/index.ts:139-441`（McpServer + StdioServerTransport） |
| [mcp_server/tools.py](../src/doocs_md_py/mcp_server/tools.py) | `packages/mcp-server/src/index.ts:150-431`（13 个工具注册表） |
| [mcp_server/\_\_main\_\_.py](../src/doocs_md_py/mcp_server/__main__.py) | —（本仓新增，stdio 入口） |

## 四、服务端 server/（44 模块）

| Python 模块 | 上游锚点 | 复刻口径 |
|---|---|---|
| [server/app.py](../src/doocs_md_py/server/app.py) | `apps/api/src/index.ts`（装配顺序） | 1:1 |
| [server/config.py](../src/doocs_md_py/server/config.py) | `apps/api/src/types.ts`（`Env`）+ `upload-config.ts` | 等价（新增 `DOOCS_MD_PY_*`） |
| [server/db.py](../src/doocs_md_py/server/db.py) | `apps/api/src/db.ts` | 1:1 移植 |
| [server/types.py](../src/doocs_md_py/server/types.py) | `apps/api/src/types.ts` | 1:1 |
| [server/security.py](../src/doocs_md_py/server/security.py) | `apps/api/src/auth.ts:14,29-51` + `share-password.ts:9,133-161` | 等价（JWT HS256） |
| [server/github_oauth.py](../src/doocs_md_py/server/github_oauth.py) | `apps/api/src/auth.ts:73-124` | 1:1 |
| [server/origin.py](../src/doocs_md_py/server/origin.py) | `apps/api/src/origin.ts` | 1:1 |
| [server/plan.py](../src/doocs_md_py/server/plan.py) | `apps/api/src/plan.ts:5-50`（纯函数部分） | 1:1 |
| [server/ratelimit.py](../src/doocs_md_py/server/ratelimit.py) | `apps/api/src/plan.ts:52-144` + `marketplace-db.ts:349-394` | 等价（UTC 窗口） |
| [server/afdian.py](../src/doocs_md_py/server/afdian.py) | `apps/api/src/afdian.ts` | 1:1 |
| [server/share_db.py](../src/doocs_md_py/server/share_db.py) | `apps/api/src/share-db.ts` | 1:1 |
| [server/share_password.py](../src/doocs_md_py/server/share_password.py) | `apps/api/src/share-password.ts` | 1:1 |
| [server/share_page.py](../src/doocs_md_py/server/share_page.py) | `apps/api/src/share-page.ts` | 1:1 |
| [server/share_gate_page.py](../src/doocs_md_py/server/share_gate_page.py) | `apps/api/src/share-gate-page.ts` | 1:1 |
| [server/share_head.py](../src/doocs_md_py/server/share_head.py) | `apps/api/src/share-head.ts` | 1:1 |
| [server/share_sanitize.py](../src/doocs_md_py/server/share_sanitize.py) | `apps/api/src/share-sanitize.ts` | 1:1 |
| [server/sync_limits.py](../src/doocs_md_py/server/sync_limits.py) | `apps/api/src/sync-limits.ts` | 1:1 |
| [server/marketplace_db.py](../src/doocs_md_py/server/marketplace_db.py) | `apps/api/src/marketplace-db.ts` | 1:1 |
| [server/marketplace_admin.py](../src/doocs_md_py/server/marketplace_admin.py) | `apps/api/src/marketplace-admin.ts` | 1:1 |
| [server/marketplace_validate.py](../src/doocs_md_py/server/marketplace_validate.py) | `apps/api/src/marketplace-validate.ts` | 1:1 |
| [server/notifications_db.py](../src/doocs_md_py/server/notifications_db.py) | `apps/api/src/notifications-db.ts` | 1:1 |
| [server/emoji_db.py](../src/doocs_md_py/server/emoji_db.py) | `apps/api/src/emoji-db.ts` | 1:1 |
| [server/emoji_validate.py](../src/doocs_md_py/server/emoji_validate.py) | `apps/api/src/emoji-validate.ts` | 1:1 |
| [server/emoji_storage.py](../src/doocs_md_py/server/emoji_storage.py) | `Env.EMOJI_ASSETS` 独立 R2 桶 | 等价层（本地/S3 后端） |
| [server/upload_config.py](../src/doocs_md_py/server/upload_config.py) | `apps/api/src/upload-config.ts` | 1:1 语义层 |
| [server/upload_filename.py](../src/doocs_md_py/server/upload_filename.py) | `apps/api/src/upload-filename.ts` | 1:1 |
| [server/upload_github.py](../src/doocs_md_py/server/upload_github.py) | `apps/api/src/upload-github.ts` | 1:1 |
| [server/upload_r2.py](../src/doocs_md_py/server/upload_r2.py) | `apps/api/src/upload-r2.ts` | 等价层（S3 SigV4） |
| [server/upload_rate.py](../src/doocs_md_py/server/upload_rate.py) | `apps/api/src/upload-rate.ts` | 1:1 |
| [server/web_dist.py](../src/doocs_md_py/server/web_dist.py) | `packages/md-cli/server.js:48`（仅 `express.static`） | **规格新增**（同源 SPA 托管，见 CD-6） |
| [server/migrations/0001_init.sql](../src/doocs_md_py/server/migrations/0001_init.sql)（0001..0008 共 8 个） | `apps/api/migrations/0001..0008*.sql` | 原样移植 |
| [server/config_report.py](../src/doocs_md_py/server/config_report.py) | —（本仓新增） | FR-15 启动配置体检，密钥不入日志 |
| [server/deps.py](../src/doocs_md_py/server/deps.py) | —（本仓新增） | FastAPI 共享依赖（DB 连接 / httpx） |
| [server/httputil.py](../src/doocs_md_py/server/httputil.py) | —（本仓新增） | 客户端 IP 与 JSON 错误体 |
| [server/storage.py](../src/doocs_md_py/server/storage.py) | —（本仓新增） | 对象存储抽象层（local / S3，替代 R2 绑定） |

### 4.1 路由 server/routers/（9 模块）

| Python 模块 | 上游锚点 | 说明 |
|---|---|---|
| [routers/auth.py](../src/doocs_md_py/server/routers/auth.py) | `apps/api/src/auth.ts` | GitHub OAuth 与 `/me` |
| [routers/sync.py](../src/doocs_md_py/server/routers/sync.py) | `apps/api/src/sync.ts` | `/sync/pull`、`/sync/push`、`/sync/activate` |
| [routers/share.py](../src/doocs_md_py/server/routers/share.py) | `apps/api/src/share.ts` | `/share` 管理端点 + `/s/:id` 公开页 |
| [routers/marketplace.py](../src/doocs_md_py/server/routers/marketplace.py) | `apps/api/src/marketplace.ts` | `/marketplace` 路由全集 |
| [routers/emojis.py](../src/doocs_md_py/server/routers/emojis.py) | `apps/api/src/emojis.ts` | `/emojis` 路由 |
| [routers/notifications.py](../src/doocs_md_py/server/routers/notifications.py) | `apps/api/src/notifications.ts` | `/notifications` 路由 |
| [routers/upload.py](../src/doocs_md_py/server/routers/upload.py) | `apps/api/src/upload.ts` | `POST /upload`（新增 local 后端分支） |
| [routers/webhooks.py](../src/doocs_md_py/server/routers/webhooks.py) | `apps/api/src/webhook.ts` | 爱发电订单 webhook |
| [routers/\_\_init\_\_.py](../src/doocs_md_py/server/routers/__init__.py) | —（本仓新增） | 路由装配 |

## 五、图床 uploaders/（13 模块，14 家图床）

| Python 模块 | 上游锚点 | 备注 |
|---|---|---|
| [uploaders/base.py](../src/doocs_md_py/uploaders/base.py) | `apps/web/src/services/upload/providers.ts` | 公共基础设施 + provider 注册表 |
| [uploaders/github.py](../src/doocs_md_py/uploaders/github.py) | `providers.ts:66-105` | **Web 客户端版**（与 server 侧 `upload_github.py` 不同） |
| [uploaders/qiniu.py](../src/doocs_md_py/uploaders/qiniu.py) | `providers.ts:107-152` | qiniu-js 3.4.4 网络层等价复刻 |
| [uploaders/s3.py](../src/doocs_md_py/uploaders/s3.py) | `providers.ts`（aliOSS/txCOS/minio/s3/r2 五函数） | 覆盖 5 家 |
| [uploaders/s3_presign.py](../src/doocs_md_py/uploaders/s3_presign.py) | `@aws-sdk/s3-request-presigner`（`getSignedUrl`） | SigV4 预签名 |
| [uploaders/mp.py](../src/doocs_md_py/uploaders/mp.py) | `providers.ts:404-499` | 微信公众号素材 |
| [uploaders/upyun.py](../src/doocs_md_py/uploaders/upyun.py) | `providers.ts:530-563` | 又拍云 |
| [uploaders/telegram.py](../src/doocs_md_py/uploaders/telegram.py) | `providers.ts:565-607` | Telegram |
| [uploaders/cloudinary.py](../src/doocs_md_py/uploaders/cloudinary.py) | `providers.ts:609-685` | Cloudinary |
| [uploaders/form_custom.py](../src/doocs_md_py/uploaders/form_custom.py) | `providers.ts:687-733`（`formCustomUpload`） | 不执行用户 JS（NG2，见 CD-9） |
| [uploaders/dcloud.py](../src/doocs_md_py/uploaders/dcloud.py) | `packages/md-cli/util.js` `dcloud()` | **上游 md-cli 独有通道**，本仓一并登记（第 14 家） |
| [uploaders/default.py](../src/doocs_md_py/uploaders/default.py) | `services/upload/client.ts` | 走 md-api `POST /upload` |
| [uploaders/\_\_init\_\_.py](../src/doocs_md_py/uploaders/__init__.py) | `services/upload/provider-registry.ts` | 注册表 |

> 图床计数口径：`uploaders/s3.py` 一家模块承载 5 家 S3 兼容图床，故 **13 个模块 = 14 家图床**。上游 Web 侧为 13 家，本仓因并入 md-cli 的 `dcloud` 而多 1 家。

## 六、顶层与入口（4 模块）

| Python 模块 | 上游锚点 | 说明 |
|---|---|---|
| [\_\_init\_\_.py](../src/doocs_md_py/__init__.py) | —（本仓新增） | 包元数据与版本 |
| [\_\_main\_\_.py](../src/doocs_md_py/__main__.py) | —（本仓新增） | `python -m doocs_md_py` 入口 |
| [cli.py](../src/doocs_md_py/cli.py) | `packages/md-cli`（Express `127.0.0.1:8800`）+ `packages/mcp-server/src/render-article.ts` | `mdpy render/serve/upload/mcp/migrate` |
| [user_config.py](../src/doocs_md_py/user_config.py) | —（本仓新增） | 用户级配置文件与 `MD_*` 覆盖（见 CD-8） |

## 七、前端资产与构建

| 资产 | 上游来源 | 说明 |
|---|---|---|
| `src/doocs_md_py/assets/web-dist/` | `apps/web` 的 Vite 构建产物（含 `dist/`） | **产物不入库**，仅保留 `.gitkeep` / `MANIFEST.sha256` / `NOTICE`；构建与回退见 [build-web-dist.md](build-web-dist.md) |
| `scripts/*_regen.py`（13 个） | 上游对应生成逻辑 | 黄金数据/快照再生工具（emoji/alert/component 数据、CSS/PBKDF2/SigV4/JWT/S3 预签名向量等） |
| `scripts/build-web-dist.sh` / `.ps1` | `packages/md-cli` 构建流程 | 前端产物构建双平台脚本 |
| `scripts/check_coverage.py` / `bench_render.py` | —（本仓新增） | 覆盖率门禁与渲染性能基准（TR-20.1 / NFR-6） |

## 八、测试布局（6 个顶层文件 + 5 个目录）

| 路径 | 用例数 | 覆盖对象 |
|---|---|---|
| `tests/render/` | 20 | 渲染核心（含归一化 DOM、选项、扩展） |
| `tests/server/` | 31 | 服务端（认证/同步/分享/市场/表情/上传/迁移/配置体检） |
| `tests/golden/` | 2 | 黄金样例端到端（文章文档、复杂文档归一化 DOM 全等价） |
| `tests/mcp/` | 2 | MCP schema 与工具映射 |
| `tests/uploaders/` | 1 | 图床签名与请求构造 |
| `tests/*.py`（顶层） | — | 跨层用例（如故障注入、CLI 流水线、文件名规范等） |

验收基线（T20 实测）：`pytest --cov` **1309 passed**、总覆盖率 **95.91%**、关键模块 **83/83 ≥ 90%**，详见 [coverage-report-t20.md](coverage-report-t20.md)。

## 九、映射维护约定

1. **契约函数必带锚点**：新增或修改与上游对应的函数，须在 docstring 或行内注释保留 `# upstream: <上游文件>:<行号>` 形式锚点；本文表格随锚点变化同步更新。
2. **本仓新增模块须显式标注**：表中以「—（本仓新增）」标注的模块无上游对应，不得被误读为"复刻遗漏"。
3. **上游升级即复核**：上游版本/commit 变更时，本表与 [contract-differences.md](contract-differences.md)、[contract-mapping.md](contract-mapping.md) 三者必须同步复核。
