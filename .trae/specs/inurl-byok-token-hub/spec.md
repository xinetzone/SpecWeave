---
title: "inurl BYOK Token Hub 复刻（Python 3.14+）"
status: "draft"
methodology: "seven-concepts (F→V→I→C)"
spec_mode: "Specify"
---

# inurl BYOK Token Hub - Product Requirements Document

## Overview

- **Summary**: 依据 OKF 知识包 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/inurl-byok-token-hub/`（13 份文档、F-001~F-122 事实台账）的规格，在本仓库 `apps/inurl-byok-token-hub/` 用 **Python 3.14+** 完整复刻 `token.inurl.link` 的 BYOK（Bring Your Own Key）统一令牌枢纽：云控制台侧的**密钥托管/E2EE 托管库/套餐计费/用量台账/系统后台**，与本机侧的 **OpenAI 兼容本地代理（`http://localhost:3003/v1`）**、**逻辑模型别名路由**、**19 种路由策略与 Combo 回退链**、**5 档提示词压缩**、**三协议自定义厂商适配**。
- **Purpose**: 把一份"只存在于文档与界面自述"的产品规格，重建为**可运行、可测试、可审计**的本地优先（local-first）参考实现。重点不是复现闭源代理二进制，而是把文档已描述的全部**能力、规则与边界条件**（鉴权语义、令牌生命周期、故障切换、额度与套餐上限、错误码、公开/私有接口分界）落成有测试证据的代码。
- **Target Users**: 需要一个自托管 BYOK 网关的开发者；研究"统一令牌 + 本地代理 + E2EE 托管库"架构的研究者；本仓库后续需要复用路由/压缩/厂商适配能力的应用。

## Goals

- G1 完整实现文档已描述的**配置层、数据模型层、服务层、接口层、外部依赖调用层**，模块职责分明。
- G2 忠实复刻关键语义：令牌前缀 `byok_live_`、本地代理固定 `:3003/v1`、逻辑别名 `inurl*` 与其旧别名、429/5xx 故障切换、19 策略 + `>` Combo、5 档压缩、三协议自定义厂商、套餐密钥上限、401 `unauthorized` / 403 `forbidden`、`/api/ads` 与 `/api/news` 公开无鉴权。
- G3 以**模拟厂商（mock provider）**驱动端到端冒烟，不依赖任何真实密钥即可运行与验证。
- G4 对文档中缺失/歧义处给出**合理默认实现**，并在 README 集中列出「假设与差异说明」。
- G5 通过 pytest 覆盖（整体 ≥80%、关键模块 ≥90%）与基础冒烟（启动 → `/v1/models` → 别名路由 → 故障切换 → 401/403 → 压缩 → 用量扣减）。

## Non-Goals

- **不复刻闭源代理二进制与其供应链行为**：不实现运行时下载、启动器内嵌令牌/主密钥、自动更新。启动器仅提供**可读的生成脚本/说明**，默认关闭且需显式启用。
- **不接入真实支付**：支付宝/收款码仅实现「订单创建 → 用户提交凭证 → 管理员人工核销」的状态机，无资金流转。
- **不抓取/同步线上目录**：`/api/catalog` 使用仓库内置**种子目录数据**（源自文档登记的事实），不联网抓取。
- **不实现浏览器端 WebCrypto**：E2EE 由 Python 参考实现（同等算法与参数）承载，服务端只存密文；不实现浏览器 JS。
- **不实现第一方行为采集**：不实现 `track.js` 式埋点（属风险项而非功能）。
- **不实现 VPN 机场广告、返佣短链等运营内容**。
- **不修改** `projects/awesome-okf-xs` 子模块（只读引用）。

## Background & Context

- **事实底座**：`references/article-source.md` 的 F-001~F-122 与 `references/verification.md` 的核验报告（E1~E9 勘误）、`references/omniroute-benchmark.md`（开源对标 OmniRoute：MIT、`localhost:20128`、19 策略、Combo、RTK+Caveman 压缩）。
- **核心勘误（必须体现在实现中）**：E1——产品免费档只允许 **3 个厂商密钥**（标准 ¥9.9/月 10 个、专业 ¥29.9/月 无限），"17 家 Key + 0 元"不成立；E2——DeepSeek 官方**收费**，catalog 中 `tier=paid`；E5——Agnes 免费档为 **512K** 而非 1M；E4——百度千帆为**每模型 100 万 / 3 个月**且另有永久免费层。
- **目录事实**：46 providers = 17 free + 29 paid（其中 10 家 `public:false` 隐藏）、133 模型；capabilities 仅 text(12)/code(5)/image(7)，**video/audio 无可路由厂商**（必须返回"当前没有支持该类别的厂商"）。
- **安全边界**：E2EE 覆盖"云端脱库"，**不覆盖**闭源本地代理供应链；运营主体匿名；Turnstile 实测 `enabled:false`。
- **仓库约束**：`apps/*` 新增 Python 子项目默认使用 **scikit-build-core** 作为 PEP 517 后端（纯 Python 不写 cmake 段）；Conventional Commits 中文主体；新应用先经 `.temp/` 暂存开发再迁移 `apps/`。
- **方法论编排**：seven-concepts 识别为**场景 5 创新突破**，链路 **F（第一性原理）→ V（对抗审查，强制）→ I（洞察落地）→ C（原子提交）**，depth=deep。

## Functional Requirements

### FR-1 配置层（config）
系统 SHALL 提供分层配置：内置默认值 → YAML 配置文件 → 环境变量（`BYOK_*`、`AGENT_TOKEN`、`AGENT_MASTERKEY`、`AUTO_MODELS`、`AUTO_PROVIDER_ORDER`）。至少覆盖：代理监听地址与端口（默认 `127.0.0.1:3003`）、API 前缀 `/v1`、数据目录、目录快照路径、默认路由策略与 Combo、默认压缩档、故障切换触发状态码集合（默认 429 + 5xx）、重试与超时、套餐定义、管理员初始账户、Turnstile 开关（默认 `false`）。

### FR-2 数据模型层（models）
系统 SHALL 以 pydantic v2 模型表达：`Provider`（id/name/base_url/protocol/tier/free/public/capabilities/models）、`ModelEntry`（id/alias/context_window/capabilities/free/rate_limit）、`User`（id/email_hash/plan/role/created_at）、`UnifiedToken`（前缀 `byok_live_`、hash 存储、状态、轮换历史）与 `RecoverySecret`、`VaultKeyRecord`（provider_id/密文 blob/key_status/last_error/quota）、`EscrowRecord`（`escrow_pw` / `escrow_rec` 双密文）、`RouteRequest`/`RouteDecision`、`StrategySpec`（19 种）与 `ComboSpec`（`>` 分隔链）、`CompressionSpec`（5 档）、`UsageRecord`/`BillingEvent`、`AdminPaymentOrder`（人工核销状态机）、`AdItem`/`NewsItem`。

### FR-3 E2EE 托管库（crypto + vault_service）
系统 SHALL 实现与文档逐字对应的浏览器侧加密参考实现：`PBKDF2(password, salt, iterations=100000, SHA-256)` 派生 256-bit 主密钥 → `AES-256-GCM` 加密厂商 Key；生成**双份 escrow**（`escrow_pw` 口令恢复密文 + `escrow_rec` 恢复密语密文）并 `POST /api/escrow` 存储。服务端 SHALL **只持久化密文**（含 salt/iv/iter/alg），明文 Key 仅在内存中出现、不得落盘、不得进入日志。恢复（`/api/recover`）与改密重加密（`/api/password`）SHALL 走完整流程。

### FR-4 统一令牌与鉴权（token_service + auth）
- 令牌 SHALL 以 `byok_live_` 为前缀，随机熵 ≥128 bit；库内只存 SHA-256 摘要。
- SHALL 支持签发、校验、轮换（旧令牌进入宽限期）、吊销。
- **鉴权语义（硬性）**：用户类接口未带/无效令牌 → **HTTP 401** 且 body 为裸 JSON `{"error":"unauthorized"}`；管理员类接口非管理员 → **HTTP 403** `{"error":"forbidden"}`；**未匹配路由的随机路径 → HTTP 401**（F-085 订正口径）。
- `/api/ads`、`/api/news`、`/api/catalog`、`/api/billing/plans`、`/api/turnstile` SHALL **无鉴权公开**。
- Turnstile SHALL 默认 `enabled:false`，可通过配置开启（开启后校验 token，未通过返回 401）。

### FR-5 目录与能力（catalog_service）
系统 SHALL 加载仓库内置种子目录（`data/catalog.json`）：46 providers / 133 models 的规模与结构；支持 `?all=1` 与默认返回**同一份数据**（对齐 F-077：`public:false` 条目虽不在 `/models` 渲染但仍随公开接口下发的既有行为，同时在 README 标注该行为为风险项）；按 `capability` 过滤；`video`/`audio` 查询 SHALL 返回"当前没有支持该类别的厂商"；付费卡 SHALL 带"落后当期旗舰 ≥1 大版本"的时效标记字段。

### FR-6 路由与故障切换（router_service）
- 逻辑别名：`inurl` / `inurl-text`（默认，旧别名 `auto`、`default`）、`inurl-code`、`inurl-image`、`inurl-video`、`inurl-audio`，且 SHALL 兼容直接传入真实模型 id。
- SHALL 实现 **19 种路由策略**（轮询、延迟优先、优先级、成本优先、健康优先、成功率优先、随机、最少使用、余量优先、加权、粘性、多样性、可靠性、成本+延迟兼顾、新鲜度、自动、极速优先、极廉价优先、均衡 Top3 轮询）。
- SHALL 支持 **Combo**：以 `>` 分隔的策略链，上一层全部失败自动流转下一层。
- SHALL 在 **429 / 5xx** 时切下一家（可配置状态码集合与最大尝试次数），并支持 `AUTO_MODELS` / `AUTO_PROVIDER_ORDER` 限定候选池。
- 每次路由 SHALL 产出可审计的 `RouteDecision`（候选顺序、跳过原因、最终厂商、尝试记录）。

### FR-7 提示词压缩（compression_service）
SHALL 实现 5 档：Lite（≈15%）、Standard（≈30%）、Aggressive（≈50%）、Ultra（≈75%）、RTK（工具链去重 60–90%）。规则式实现；**代码块、链接、JSON 必须原样保留**；输出 SHALL 附带"估算压缩率"与"是否发生不可逆损坏"的自检标记（损坏即拒绝压缩、回退原文）。

### FR-8 外部依赖调用（providers/*）
SHALL 实现三种厂商协议适配器：
1. **OpenAI 兼容**：`POST {base_url}/chat/completions`，`Authorization: Bearer <key>`；
2. **Anthropic**：`POST {base_url}/v1/messages`，头 `x-api-key` + `anthropic-version`；
3. **Gemini**：`POST {base_url}/v1beta/models/{model}:generateContent?key=<key>`。
适配器 SHALL 统一为 `ChatRequest`/`ChatResponse` 内部表示，规范错误为统一错误码；SHALL 提供 **mock 传输层**（`transport` 抽象），使全部测试与冒烟无需真实密钥与网络。

### FR-9 健康度与用量（health + usage）
SHALL 记录每厂商成功率/延迟/连续失败/熔断状态；SHALL 维护"手填额度 − 已用 = 剩余"的每厂商用量统计与全局用量台账；额度耗尽厂商 SHALL 自动退出候选池并在 UI/接口可见。

### FR-10 接口层（api，FastAPI）
- 本地代理：`GET /v1/models`、`POST /v1/chat/completions`（支持 `stream` 的 SSE 最小实现）。
- 账户：`/api/register`、`/api/login`、`/api/escrow`、`/api/recover`、`/api/password`。
- 密钥库：密钥 CRUD、`/api/keys` 列表（永不下发明文）、状态与用量。
- 公开：`/api/catalog`、`/api/billing/plans`、`/api/turnstile`、`/api/ads`、`/api/news`。
- 用户类：设置（路由策略/Combo/压缩档/自定义厂商）。
- 管理员：八模块后台（用户管理、厂商目录、套餐与订单、人工核销、用量总览、公告/广告位、系统配置、审计日志）。
- 未匹配路径 → 401 裸 JSON（见 FR-4）。

### FR-11 计费套餐（billing_service）
免费 ¥0 / **3 个厂商密钥**；标准 ¥9.9 月 / 10 个；专业 ¥29.9 月 / 无限。SHALL 在写入密钥时强制校验上限（超限返回明确错误码与升级提示），SHALL 记录邀请奖励带来的额度增量。

### FR-12 系统后台与人工核销（ops_service）
SHALL 实现八模块后台的数据与接口；支付订单状态机 `created → proof_submitted → confirmed(人工核销) / rejected`；默认支付方式为**个人收款码 + 人工核销**，管理员审核动作写入审计日志。

### FR-13 CLI 与冒烟（cli）
SHALL 提供 CLI：`serve`（启代理）、`catalog`（列目录）、`route`（干跑路由决策）、`compress`（试压缩）、`vault`（密钥 CRUD）、`smoke`（端到端冒烟，全 mock）。`python -m inurl_byok_token_hub smoke` SHALL 在零真实密钥下跑通全流程。

### FR-14 精简控制台（web）
SHALL 提供最小 Jinja2 控制台：密钥库、用量、路由/压缩设置、套餐与订单。纯服务端渲染，不引入前端构建链。

### FR-15 文档（README）
README SHALL 记录：产品定位与架构、目录结构、启动方式、环境变量、接口清单、数据模型、与源文档的**假设与差异说明**（逐条编号）、已知边界与安全提示（供应链/E2EE 不覆盖范围）。

## Non-Functional Requirements

- **NFR-1 可运行性**：Python 3.14（本机验证环境 `py314`，Python 3.14.3）；`python -m inurl_byok_token_hub smoke` 零真实密钥通过。
- **NFR-2 测试**：pytest 整体覆盖率 ≥80%、关键模块（crypto/router/token_provider 鉴权/billing 上限）≥90%；`ruff check` 零错误。
- **NFR-3 安全**：明文 Key 不落盘、不进日志；令牌只存摘要；日志脱敏（Key/令牌仅显示前缀与后 4 位）。
- **NFR-4 构建**：`apps/inurl-byok-token-hub/pyproject.toml` 使用 **scikit-build-core** 后端（纯 Python，`wheel.packages` 指向 `src/inurl_byok_token_hub`），遵循仓库开发规范。
- **NFR-5 模块性**：分层清晰（config / models / crypto / services / providers / api / cli / web），禁止跨层反向依赖；外部依赖调用全部经 `providers.transport` 抽象，便于 mock。
- **NFR-6 提交**：Conventional Commits，中文主体；每个原子切片单独提交。
- **NFR-7 合规**：不实现行为采集/广告返佣；不触碰 `projects/` 子模块；不写入 `.agents/docs/`。

## Constraints

- **Technical**: Python 3.14+；FastAPI + Uvicorn + Jinja2 + Typer + httpx + PyYAML + pydantic v2（本机 `py314` 环境已具备，见证据 E-ENV）。目录数据内置为种子 JSON，不联网。
- **Business**: 源知识包 `status: flagged`（E1~E9 勘误必须体现）；免费档 3 密钥为硬约束。
- **Dependencies**: `projects/awesome-okf-xs`（只读源）；`apps/` 主权区（可写）；新应用先 `.temp/` 暂存后迁移。
- **Process**: TRAE-spec-mode 五阶段——本文件为 Specify 产物，**获得显式批准前不得实施**；Review 必须由独立上下文执行。

## Assumptions

- **A1 运行时**：以本机 conda 环境 `py314`（Python 3.14.3）为验证环境；代码不使用 3.14 独有语法，`requires-python = ">=3.14"`。
- **A2 持久化**：文件仓库（JSON，位于可配置数据目录）+ 可插拔 `Repository` 协议；不引入数据库依赖（文档未指定）。
- **A3 目录数据**：46 providers / 133 models 用"文档已登记具名厂商 + 规模补齐的占位条目"构造，逐条标注 `source=seed`，并在 README 明示**非实时抓取、不可作为免费政策事实源**（对齐 F-079/F-080）。
- **A4 E2EE**：以 Python `hashlib.pbkdf2_hmac` + `cryptography` 的 AES-GCM 复刻浏览器侧算法；若 `cryptography` 不可用则提供纯标准库 GCM 回退实现（需显式标注）。
- **A5 流式**：`/v1/chat/completions` 的 `stream=true` 提供 SSE 最小实现（mock 场景可验证；真实厂商按协议透传）。
- **A6 控制台**：只做服务端渲染的精简控制台（FR-14），不还原原站全部交互。
- **A7 启动器**：提供 `byok-launch.sh/.bat` 的**生成与说明**，默认不下载、不内嵌密钥；README 明示与原产品供应链差异。
- **A8 邀请奖励**：文档未给具体数值，默认"每成功邀请 1 人 +1 密钥额度（上限 +5）"，可在配置修改。
- **A9 隐藏厂商**：保留 `public:false` 条目随公开接口下发的**原行为**以忠实复刻，同时在 README 标注为风险并提供 `hide_hidden_providers` 配置开关（默认 `false`，即保持原行为）。

## Acceptance Criteria

### AC-1: 统一令牌与鉴权语义逐字成立
- **Type**: `rule`
- **Given**: 应用已启动，存在普通用户与管理员两类令牌；存在未注册路由 `/api/random-nonexistent`
- **When**: 分别以「无令牌」「无效令牌」「普通用户令牌访问管理员接口」「任意请求访问随机路径」调用
- **Then**: 前两者与随机路径返回 **HTTP 401** 且 body 为裸 JSON `{"error":"unauthorized"}`；第三者为 **HTTP 403** `{"error":"forbidden"}`；`/api/ads`、`/api/news`、`/api/catalog`、`/api/billing/plans`、`/api/turnstile` 在无令牌下返回 200
- **Pass Condition**: 上述 7 组断言全部通过，且签发的令牌前缀为 `byok_live_`、库中只存摘要
- **Evidence**: `pytest -k auth` 输出 + 冒烟脚本中打印的状态码/body 片段

### AC-2: E2EE 托管库只存密文且双 escrow 可恢复
- **Type**: `rule`
- **Given**: 用户口令与恢复密语；一份厂商明文 Key
- **When**: 走「派生主密钥 → AES-GCM 加密 → 生成 `escrow_pw`+`escrow_rec` → POST `/api/escrow`」完整流程，再用恢复密语走 `/api/recover`，再走 `/api/password` 改密重加密
- **Then**: 持久化文件中**不存在**明文 Key 子串；恢复流程可还原出与原文一致的 Key；改密后旧口令解不开、新口令可解开
- **Pass Condition**: 3 项断言全通过；参数逐字为 PBKDF2/SHA-256/100000 迭代/AES-GCM-256
- **Evidence**: 测试用例 + 落盘 JSON 的 grep 结果（无明文）

### AC-3: 路由别名、19 策略、Combo 与 429/5xx 故障切换
- **Type**: `rule`
- **Given**: mock 厂商池中 A 返回 429、B 返回 503、C 正常；别名与策略配置齐全
- **When**: 以 `inurl` / `inurl-text` / `auto` / `default` / `inurl-code` / `inurl-image` 与真实模型 id 分别请求；设置 Combo `延迟优先>轮询`；请求 `inurl-video`
- **Then**: 文本/代码/图像类分别落到具备对应 capability 的厂商；429 与 503 的厂商被跳过并最终落到 C；Combo 按层级流转；`inurl-video` 返回"当前没有支持该类别的厂商"；19 种策略均被注册表收录且可单独选中
- **Pass Condition**: 全部断言通过，`RouteDecision` 含候选顺序/跳过原因/最终厂商
- **Evidence**: `pytest -k router` + `route` 干跑输出

### AC-4: 5 档压缩与不可损坏保证
- **Type**: `rule`
- **Given**: 含代码块、URL、JSON 片段的提示词样本
- **When**: 分别以 Lite/Standard/Aggressive/Ultra/RTK 压缩
- **Then**: 各档均产出非空结果；代码块、链接、JSON 段**逐字保留**；返回估算压缩率；若自检判定会损坏内容则拒绝压缩并回退原文
- **Pass Condition**: 5 档 × 3 类保护对象全部保留，且存在至少 1 例"拒绝压缩回退"的用例
- **Evidence**: `pytest -k compress` 断言与样例输出

### AC-5: 三协议自定义厂商适配
- **Type**: `rule`
- **Given**: 三个 mock 传输层分别按 OpenAI 兼容 / Anthropic / Gemini 约定响应
- **When**: 通过统一 `ChatRequest` 调用三种协议适配器
- **Then**: OpenAI 走 `POST {base}/chat/completions` + `Authorization: Bearer`；Anthropic 走 `POST {base}/v1/messages` + `x-api-key` + `anthropic-version`；Gemini 走 `POST {base}/v1beta/models/{m}:generateContent?key=`；三者均归一化为同一 `ChatResponse`
- **Pass Condition**: 请求方法/路径/头/查询参数逐项匹配，响应字段归一化一致
- **Evidence**: 传输层录制的请求快照断言

### AC-6: 套餐密钥上限与用量台账
- **Type**: `rule`
- **Given**: 免费档用户（上限 3）、标准档（10）、专业档（无限）
- **When**: 尝试写入第 4 / 第 11 个厂商密钥；随后模拟调用并统计用量
- **Then**: 免费档第 4 个被拒（明确错误码 + 升级提示），标准档第 11 个被拒，专业档放行；用量台账按"手填额度 − 已用 = 剩余"计算且额度耗尽厂商退出候选池
- **Pass Condition**: 4 项断言通过，且与 E1 勘误口径一致
- **Evidence**: `pytest -k billing` 输出

### AC-7: 目录事实与能力边界
- **Type**: `rule`
- **Given**: 内置种子目录
- **When**: 查询 `/api/catalog` 与 `/api/catalog?all=1`、`capability=video|audio`、`tier=free|paid`
- **Then**: 两者返回同一份数据（含 `public:false` 条目，与 F-077 一致）；video/audio 无结果并给出"当前没有支持该类别的厂商"；免费/付费计数与种子数据一致；付费卡带"落后旗舰 ≥1 大版本"标记
- **Pass Condition**: 全部断言通过
- **Evidence**: `catalog` CLI 输出 + 测试快照

### AC-8: 端到端冒烟（零真实密钥）
- **Type**: `rule`
- **Given**: 全新数据目录、全 mock 传输层
- **When**: 依次执行 注册 → 签发令牌 → 录入 3 个 mock 厂商 Key（E2EE）→ 启动代理 → `GET /v1/models` → `POST /v1/chat/completions`（含一次故障切换）→ 查询用量 → 管理员登录后台
- **Then**: 全流程零异常退出；`/v1/models` 返回别名与真实模型；聊天返回归一化响应；用量 +1；后台 200、非管理员 403
- **Pass Condition**: `python -m inurl_byok_token_hub smoke` 退出码 0 且打印每步结果
- **Evidence**: 冒烟命令完整 stdout

### AC-9: 工程质量与仓库规范
- **Type**: `rule`
- **Given**: `apps/inurl-byok-token-hub/` 完整代码
- **When**: 运行 `pytest --cov`（阈值）、`ruff check`、检查 `pyproject.toml` 构建后端与目录落点
- **Then**: 整体覆盖率 ≥80%、关键模块 ≥90%；`ruff check` 零错误；构建后端为 scikit-build-core；应用位于 `apps/inurl-byok-token-hub/`
- **Pass Condition**: 三项全通过
- **Evidence**: pytest/ruff 输出 + pyproject 内容

### AC-10: 架构分层与模块职责清晰度
- **Type**: `rubric`
- **Dimension**: 分层清晰度与职责单一性（config/models/crypto/services/providers/api/cli/web）
- **Scale**: 1-5
- **Anchors**: 1 = 层次混杂、跨层反向依赖、外部调用散落各处；3 = 分层基本成立但存在跨层捷径与外部调用未收敛；5 = 分层严格、无反向依赖、外部调用全部经 transport 抽象、每模块单一职责且有清晰接口
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查者阅读源码后的评分与依据（附具体文件/行）

### AC-11: 假设与差异说明的可审计性
- **Type**: `rubric`
- **Dimension**: README「假设与差异说明」的完备性与可追溯性
- **Scale**: 1-5
- **Anchors**: 1 = 无说明或仅一句带过；3 = 列出主要假设但缺溯源与风险标注；4 = 逐条编号、含默认值、溯源 F 编号/E 勘误与风险提示；5 = 在 4 基础上每条假设均可在代码中定位到实现位置，并对安全边界给出明确使用建议
- **Pass Threshold**: >= 4
- **Evidence**: README 章节 + 独立审查者抽查 3 条假设的代码可定位性

## Open Questions

- [ ] **OQ-1**：是否需要真实厂商适配器的**联网**集成测试（默认：否，仅 mock + 可选 `--live` 开关，需用户提供密钥）？
- [ ] **OQ-2**：控制台（FR-14）范围是否可裁剪为"仅 API + CLI"？（默认：保留精简控制台）
- [ ] **OQ-3**：`public:false` 隐藏厂商是否随公开接口下发？（默认 A9：保持原行为 + 提供开关）
