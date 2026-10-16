---
title: doocs-md-py —— doocs/md 的 Python 复刻
source: d:/AI/.chaos/libs/md（doocs/md v2.1.0，commit 1bdad48d20048bddc8d32afb1b75a6475169f163）
date: 2026-10-16
---

# doocs-md-py

**doocs/md 的 Python 3.14 复刻**：微信兼容 Markdown 渲染库 + 自托管 API + 14 图床上传器 + MCP/CLI。

上游项目 [doocs/md](https://github.com/doocs/md) 是一套 TypeScript 单体仓库（渲染核心 + Web 编辑器 + md-api 服务 + md-cli + MCP Server，cloudflare Worker 托管）。本应用把其中**可服务化的部分**（渲染/上传/API/MCP/CLI）以 Python 重写为本地自托管形态，保持与上游的**可追溯对应关系**与**归一化 DOM 等价**的渲染口径。

| 项 | 值 |
|---|---|
| 上游版本 | **v2.1.0**（`package.json` version 2.1.0） |
| 上游 commit | `1bdad48d20048bddc8d32afb1b75a6475169f163`（2026-10-12） |
| Python 要求 | `>= 3.14` |
| 许可证 | **WTFPL**（上游为 WTFPL-2.0，版权归 doocs/md 上游贡献者；见 [NOTICE](NOTICE) 与 `assets/web-dist/LICENSE`） |

## 一、功能矩阵

| 能力 | 状态 | 说明 | 上游对应 |
|---|---|---|---|
| Markdown → 微信兼容 HTML 渲染 | ✅ | 27 个渲染模块，含 12 类扩展（alert/组件/图表/emoji/脚注/KaTeX/markup/ruby/slider/TOC） | `packages/core` |
| 主题与样式选项 | ✅ | 主题、主题色、字体族/字号、行高、段间距、链接色、引用块底色、图注、明暗模式、标题样式、自定义 CSS | `packages/core` + `packages/shared` |
| 自托管 API 服务 | ✅ | 认证（GitHub OAuth）/ 云同步 / 公开分享（含密码门与快照净化）/ 主题组件市场 / 站内通知 / 表情包 / 上传 / 爱发电 webhook | `apps/api` |
| Web UI（同源托管） | ✅（需构建产物） | 托管上游 `apps/web` 的 Vite 构建产物镜像，SPA 回退 + 哈希资产长缓存 | `apps/web`（构建）/ `packages/md-cli`（托管） |
| CLI（`mdpy`） | ✅ | `render` / `serve` / `upload` / `mcp` / `migrate` 五个子命令 | `packages/md-cli` |
| MCP stdio Server | ✅ | 13 个工具，含 `render_markdown` 与 11 个枚举查询 + `get_renderer_options` | `packages/mcp-server` |
| 图床上传器 | ✅ | **14 家**：default / github / aliOSS / txCOS / qiniu / minio / s3 / r2 / mp / upyun / telegram / cloudinary / formCustom / dcloud | `apps/web` `providers.ts` + `packages/md-cli` |
| 多平台客户端 | ❌ | VS Code 扩展、uTools 插件、浏览器扩展等分发渠道不复刻 | 非目标 |
| 执行用户自定义 JS | ❌ | 仓库内**不存在任何执行用户提供 JS 的代码路径**（`formCustom` 仅保留配置形态 + Python 插件入口） | 非目标 |
| 云平台原生依赖 | ❌ | Cloudflare Workers / D1 / R2 绑定不上游直连，改由 FastAPI + SQLite + S3 兼容后端等价替代 | 平台替代 |
| 语法着色 / diff 高亮 | ⚠️ | 运行期依赖白名单不含着色库，代码块保留同构包裹但无 span 级着色（前端可 CDN 侧 hydrate） | 能力裁剪 |
| HTML 字节级一致 | ❌ | 验收口径为**归一化 DOM 结构等价**，不承诺字节相等 | 渲染口径 |

> **非目标（NG）的完整逐条定义**见规格文档 [spec.md](../../.trae/specs/doocs-md-py/spec.md)；本文只列出对使用者有实际影响的部分。

## 二、快速开始

前置：**Python 3.14+**。

```bash
# 1) 进入应用目录并建虚拟环境
cd apps/doocs-md-py
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux / macOS

# 2) 安装（可编辑安装，附带开发依赖）
pip install -e ".[dev]"

# 3) 初始化数据库（幂等，可重复执行）
mdpy migrate

# 4) 渲染一份 Markdown（读文件 -> 写文件；缺省走标准输入/输出）
mdpy render -i README.md -o out.html
```

以上四步完成后，**库 / CLI / MCP 三条路径已完全可用**（渲染、图床上传、MCP 工具调用，均不依赖前端产物）。

> **MCP 零外部依赖**：stdio MCP Server 为**本仓手写实现**——按 MCP 规范实现 JSON-RPC 2.0 传输层（[mcp_server/stdio.py](src/doocs_md_py/mcp_server/stdio.py)）与 13 工具注册表（[mcp_server/tools.py](src/doocs_md_py/mcp_server/tools.py)），**不经由任何第三方 `mcp` 包**。故 [pyproject.toml](pyproject.toml) 的运行期依赖白名单为 fastapi / uvicorn / python-multipart / markdown-it-py / nh3 / PyJWT / httpx / pyyaml 共 **8 项，不含 `mcp`**，与上游 `packages/mcp-server` 的契约仍保持 1:1（同名、同入参 schema、同输出形状）。

### 2.1 启用 Web UI（`mdpy serve`）

Web UI 由上游前端构建产物驱动，而**产物不入库**（见 [.gitignore](.gitignore)）：fresh clone 后 `src/doocs_md_py/assets/web-dist/` 内**没有 `index.html`**，此时直接 `mdpy serve` 会以启动错误提示 dist 缺失。启用步骤如下：

```bash
# 5) 构建前端产物（WSL+podman 主路线，或 Windows 原生回退路线）
pwsh ./scripts/build-web-dist.sh      # Windows 侧入口为 scripts/build-web-dist.ps1
#    详细前置条件、环境变量与回退预案见 docs/build-web-dist.md

# 6) 启动同源服务（默认仅本机 127.0.0.1:8800；端口占用时自动递增）
mdpy serve
#    浏览器打开 http://localhost:8800
```

- 默认**只绑定本机**；需要外部访问时必须显式 `--host 0.0.0.0`，并同步配置 `APP_URL` 与来源白名单。
- 首次启动会打印**配置体检报告**（哪些能力已启用、哪些密钥已配置），报告**不含任何密钥值**（FR-15）。
- 数据落在 `data/`（SQLite 与 `data/uploads`），已被 `.gitignore` 排除。
- **部署约束**：以**单 worker** 运行。SQLite 连接以 `check_same_thread=False` 跨线程复用（FastAPI 同步路由在线程池执行），多 worker 部署须**各持独立文件连接**，不可共享同一连接（见 [docs/contract-differences.md](docs/contract-differences.md) 的 CD-13）。
- **前端遥测提示**：构建产物 `index.html` 由上游零补丁产出，沿带上游 Google Analytics `gtag`（`G-7NZL3PZ0NK`），已登记为差异 CD-10；如需剥离见 [docs/build-web-dist.md](docs/build-web-dist.md) 第七节（部署侧后处理，非默认行为）。

## 三、CLI 命令

| 命令 | 作用 | 常用参数 |
|---|---|---|
| `mdpy render` | Markdown → 微信兼容 HTML | `-i/--input`、`-o/--output`、`--theme`、`--primary-color`、`--font-family`、`--font-size`、`--line-height`、`--block-spacing`、`--link-color`、`--blockquote-background`、`--legend`、`--code-block-theme`、`--theme-mode`、`--heading-styles`（JSON）、`--custom-css`、`--mac-code-block`、`--show-line-number`、`--cite-status`、`--count-status`、`--use-indent`、`--use-justify`、`--full-document` |
| `mdpy serve` | 同源托管前端产物 + API | `--host`（默认 `127.0.0.1`）、`--port`（默认 `8800`，占用自动递增） |
| `mdpy upload` | 经指定图床上传图片并打印 URL | `--provider`、`--file`、`--config`；可用 `MD_UPLOAD_PROVIDER` / `MD_UPLOAD_FILE` / `MD_CONFIG_FILE` 替代 |
| `mdpy mcp` | 启动 stdio MCP Server | 无 |
| `mdpy migrate` | 初始化 / 升级 SQLite 数据库 | `--db`（默认 `data/doocs-md-py.db`） |
| `mdpy --version` | 打印版本 | — |

- `render` 缺省输出**库返回的片段**；需要完整 HTML 文档时加 `--full-document`（标题取 front-matter 的 `title`）。
- 退出码约定：使用性错误（文件缺失、图床未配置、参数非法）为 `2`。

## 四、配置项全表

配置来源优先级：**默认值 < `.env`（或进程环境变量）**；CLI 另有用户级配置文件（见第五节）。下表逐条对齐 [.env.example](.env.example)。

### 4.1 服务（上游同名）

| 变量 | 示例值 / 默认 | 用途 |
|---|---|---|
| `APP_URL` | `http://localhost:8800` | 允许的前端来源；`*` 仅匹配单个主机标签 |
| `JWT_SECRET` | 空 | JWT HS256 密钥；留空使用仅开发用固定值并告警，**生产必须改为随机长串** |
| `ADMIN_GITHUB_LOGINS` | 空 | 管理员 GitHub 登录名（逗号分隔，大小写不敏感） |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | 空 | GitHub OAuth；留空则登录端点禁用（本地编辑器仍可用） |
| `AFDIAN_USER_ID` / `AFDIAN_API_TOKEN` / `AFDIAN_WEBHOOK_TOKEN` | 空 | 爱发电开放平台；全空时 webhook 静默、activate 返回 503 |
| `AFDIAN_API_BASE` | `https://afdian.com/api/open` | 爱发电 API 基址 |
| `AFDIAN_PRO_PLAN_IDS` | 空 | 授予 Pro 的方案 id 白名单（逗号分隔） |

### 4.2 图片上传（上游同名，`/upload`）

| 变量 | 示例值 / 默认 | 用途 |
|---|---|---|
| `UPLOAD_ENABLED` | `true` | 上传总开关 |
| `UPLOAD_BACKEND` | `local` | 后端：`github` \| `local` \| `s3`（`local` 为本仓新增分支） |
| `UPLOAD_MAX_BYTES` | `5242880` | 上传体积上限常量（见 [contract-differences.md](docs/contract-differences.md) 的 D-3：上游该配置为死配置） |
| `UPLOAD_GITHUB_USERNAME` | `bucketio` | GitHub 后端用户/组织名 |
| `UPLOAD_GITHUB_REPO_LIST` | 空 | 逗号分隔仓库列表；留空默认 `img0..img19` |
| `UPLOAD_GITHUB_BRANCH` | `main` | 目标分支 |
| `UPLOAD_GITHUB_USE_CDN` | `true` | 是否用 CDN 域名回链 |
| `UPLOAD_GITHUB_TOKENS_BUCKETIO` | 空 | 逗号分隔 PAT；`UPLOAD_BACKEND=github` 时必填 |
| `UPLOAD_S3_ENDPOINT` / `UPLOAD_S3_REGION` / `UPLOAD_S3_BUCKET` | 空 / `auto` / 空 | S3 兼容端点（对应上游 R2 绑定语义） |
| `UPLOAD_S3_ACCESS_KEY_ID` / `UPLOAD_S3_SECRET_ACCESS_KEY` | 空 | S3 凭证 |
| `UPLOAD_S3_FORCE_PATH_STYLE` | `false` | 路径风格寻址（MinIO 等自建端点常需 `true`） |
| `UPLOAD_S3_PUBLIC_URL` | 空 | 对外可访问的基础 URL |

### 4.3 Python 侧新增

| 变量 | 示例值 / 默认 | 用途 |
|---|---|---|
| `DOOCS_MD_PY_SQLITE_PATH` | `data/doocs-md-py.db` | SQLite 数据库路径 |
| `DOOCS_MD_PY_STORAGE_LOCAL_DIR` | `data/uploads` | 本地对象存储落盘目录 |
| `DOOCS_MD_PY_STORAGE_LOCAL_BASE_URL` | `/uploads` | 本地对象存储对外基础 URL |
| `DOOCS_MD_PY_EMOJI_PREFIX` | `emoji` | 表情资产前缀（本地后端子目录或 S3 前缀） |

> 代码另支持 `DOOCS_MD_PY_EMOJI_BACKEND`（`local` \| `s3`）、`DOOCS_MD_PY_EMOJI_LOCAL_DIR`、`DOOCS_MD_PY_EMOJI_S3_BUCKET`、`DOOCS_MD_PY_EMOJI_S3_PUBLIC_URL`（`.env.example` 未列举，默认 `local`）。

### 4.4 CLI 层（仅影响 `mdpy upload`）

| 变量 | 用途 |
|---|---|
| `MD_CONFIG_FILE` | 用户配置文件路径（覆盖默认 `~/.config/doocs-md-py/config`） |
| `MD_UPLOAD_PROVIDER` / `MD_UPLOAD_FILE` | `--provider` / `--file` 的环境变量回退 |
| `XDG_CONFIG_HOME` | 决定默认配置目录（默认 `~/.config`） |

## 五、图床上传（14 家）

### 5.1 用户配置文件

CLI 从**用户级配置文件**读取各图床凭据（凭证只存在于本机，**不入版本库**），默认路径 `~/.config/doocs-md-py/config`：

```toml
# ~/.config/doocs-md-py/config  （TOML；.yaml/.yml/.json 亦按扩展名解析）
# default 与 dcloud 共用本段（两家字段不同名，可共存）
[config]
api_base = "https://your-md-api.example.com"   # default：等价 MD_API_URL（无尾斜杠）
token = ""                                     # default：可选鉴权令牌
space_id = ""                                  # dcloud：unicloud 空间 ID
client_secret = ""                             # dcloud：unicloud 客户端密钥

[githubConfig]
username = "your-name"
repo = "img0"
access_token = "ghp_xxx"
branch = "master"
use_cdn = false

[qiniuConfig]
access_key = ""
secret_key = ""
bucket = ""
path = ""
domain = ""
region = ""        # 空 -> 使用默认上传域名
```

读取优先级：默认路径 < `--config` / `MD_CONFIG_FILE` 指定文件 < `MD_*` 环境变量。

### 5.2 图床与配置段对照

| provider id | 配置段名 | 必填/常用字段 |
|---|---|---|
| `default` | `[config]` | `api_base`（必填）、`token` |
| `github` | `[githubConfig]` | `username`、`repo`、`access_token`、`branch`、`use_cdn` |
| `aliOSS` | `[aliOSSConfig]` | `region`、`bucket`、`access_key_id`、`access_key_secret`、`use_ssl`、`cdn_host`、`path` |
| `txCOS` | `[txCOSConfig]` | `secret_id`、`secret_key`、`bucket`、`region`、`path`、`cdn_host` |
| `qiniu` | `[qiniuConfig]` | `access_key`、`secret_key`、`bucket`、`path`、`domain`、`region` |
| `minio` | `[minioConfig]` | `endpoint`、`port`、`use_ssl`、`bucket`、`access_key`、`secret_key` |
| `s3` | `[s3Config]` | `endpoint`、`region`、`bucket`、`access_key_id`、`access_key_secret`、`path`、`cdn_host`、`path_style` |
| `r2` | `[r2Config]` | `account_id`、`access_key`、`secret_key`、`bucket`、`path`、`domain` |
| `mp` | `[mpConfig]` | `app_id`、`app_secret`、`proxy_origin` |
| `upyun` | `[upyunConfig]` | `bucket`、`operator`、`password`、`path`、`domain` |
| `telegram` | `[telegramConfig]` | `token`、`chat_id` |
| `cloudinary` | `[cloudinaryConfig]` | `cloud_name`、`api_key`、`api_secret`、`upload_preset`、`folder`、`domain` |
| `formCustom` | `[formCustomConfig]` | `name`、`raw`（**仅配置形态**，不执行用户 JS，见差异台账 CD-9） |
| `dcloud` | `[config]` | `space_id`、`client_secret`（上游 `md-cli` 独有通道，本仓一并登记） |

### 5.3 上传用法

```bash
mdpy upload --provider github --file ./cover.png
# 或经环境变量
set MD_UPLOAD_PROVIDER=github && set MD_UPLOAD_FILE=./cover.png && mdpy upload
# 指定其它配置文件
mdpy upload --provider qiniu --file ./cover.png --config ./my-config.toml
```

成功时 stdout 打印上传后的 URL。若所选图床需要配置段而配置文件中缺失，命令会以退出码 `2` 报错并提示所需段名。

> `uploaders/` 是**Web 客户端侧的图床清单**，与 API 侧 `UPLOAD_BACKEND` 的 `github`/`s3` 上传路径是两套独立实现；二者均登记于 [architecture.md](docs/architecture.md)。

## 六、MCP 客户端配置

本应用提供 **stdio MCP Server**，可直接接入支持 MCP 的客户端：

```json
{
  "mcpServers": {
    "doocs-md-py": {
      "command": "mdpy",
      "args": ["mcp"]
    }
  }
}
```

未把 `mdpy` 装进 PATH 时，可改用模块入口：

```json
{
  "mcpServers": {
    "doocs-md-py": {
      "command": "python",
      "args": ["-m", "doocs_md_py.mcp_server"]
    }
  }
}
```

### 13 个工具

| 工具 | 用途 |
|---|---|
| `render_markdown` | 渲染 Markdown 为微信兼容 HTML（入参 schema 与上游 1:1，含全部渲染选项） |
| `get_renderer_options` | 返回渲染器全部可选值与默认值 |
| `list_themes` / `list_colors` / `list_fonts` / `list_font_sizes` | 主题 / 主题色 / 字体族 / 字号枚举 |
| `list_legend_formats` / `list_heading_styles` / `list_spacing_options` | 图注格式 / 标题样式 / 间距选项枚举 |
| `list_color_options` / `list_code_block_themes` | 配色项 / 代码块高亮主题枚举 |
| `list_ai_services` | 上游内置 AI 服务清单 |
| `explain_extensions` | 解释 Markdown 扩展语法（alert、组件、图表、脚注、KaTeX、ruby、slider、TOC 等） |

## 七、文档地图

| 文档 | 内容 |
|---|---|
| [docs/architecture.md](docs/architecture.md) | **模块 ↔ 上游文件映射总表**（AC-U2/AC-U3 审计依据）、分层与数据流、测试布局 |
| [docs/contract-differences.md](docs/contract-differences.md) | **行为差异台账**：markdown-it ↔ marked 差异清单、14 家图床/托管/配置层差异与裁决 |
| [docs/contract-mapping.md](docs/contract-mapping.md) | 上游 13 个 API 测试文件 / 60 条用例的逐条契约映射，含 D-1..D-4 完整档案 |
| [docs/build-web-dist.md](docs/build-web-dist.md) | 前端产物构建（WSL+podman 主路线 / Windows 原生回退）与回退预案 |
| [docs/coverage-report-t20.md](docs/coverage-report-t20.md) | 覆盖率与性能基准验收报告（1309 passed / 总覆盖 95.91%） |

## 八、开发与验证

```bash
pip install -e ".[dev]"

pytest                      # 全量测试（testpaths 已锁定 tests/）
pytest --cov                # 覆盖率（总门槛 80%，关键模块 per-module >= 90%）
python scripts/check_coverage.py   # 关键模块覆盖率机械判定（消费 --cov-report=json）
ruff check .                # 静态检查（py314；禁止 __future__ 导入）
python scripts/bench_render.py     # 渲染性能基准（NFR-6）
```

技术红线：Python 代码**禁止 `from __future__ import annotations`**；运行期依赖白名单为 fastapi / uvicorn / python-multipart / markdown-it-py / nh3 / PyJWT / httpx / pyyaml；与上游对应的契约函数保留 `# upstream: 文件:行号` 锚点。

## 九、许可证与来源

- 本应用遵循上游 **WTFPL** 许可；上游为 WTFPL-2.0，**版权归 doocs/md 上游贡献者**。见 [NOTICE](NOTICE)。
- 前端产物镜像内含上游 `LICENSE`，并附可复现清单 `assets/web-dist/MANIFEST.sha256`（含 `upstream_commit`、`built_at_utc`、构建环境与逐文件 SHA256）。
- 上游基线：**v2.1.0**，commit `1bdad48d20048bddc8d32afb1b75a6475169f163`。
