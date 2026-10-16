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

## 七、差异维护约定

1. 新增差异必须先在本文件登记并给出裁决与锚点，再进入实现；未登记的差异一律按缺陷处理。
2. 上游升级（版本/commit 变更）时，本文件与 [contract-mapping.md](contract-mapping.md) 必须同步复核。
3. 已登记为"保留上游缺陷"的条目（当前仅 CD-2）不得在本仓单方面修正。
