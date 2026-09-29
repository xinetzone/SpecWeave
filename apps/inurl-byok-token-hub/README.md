# inurl BYOK Token Hub（Python 3.14+ 复刻）

BYOK 统一令牌枢纽复刻：E2EE 密钥保险库 + 逻辑别名路由 + 本地三协议代理 + 用量计费。

依据 OKF 知识包 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/inurl-byok-token-hub/`（13 份文档、F-001~F-122 事实台账）的规格，用 Python 3.14 复刻 `token.inurl.link` 的 **BYOK（Bring Your Own Key）统一令牌枢纽**：

- 云控制台侧：E2EE 密钥托管库、双 escrow、套餐与人工核销、用量台账、八模块后台；
- 本机侧：OpenAI 兼容本地代理（`http://127.0.0.1:3003/v1`）、逻辑别名路由、19 种策略 + Combo 回退链、5 档提示词压缩、三协议厂商适配、429/5xx 故障切换。

> **这不是原产品的源码移植**。原产品的本地代理是闭源二进制，知识包全程「未注册、未下载、未运行」，本复刻依据文档已描述的能力与边界条件重建，缺失与歧义处按合理默认实现（见末尾「假设与差异说明」）。

---

## 1. 快速开始

```bash
# 本机默认 python 为 3.13.12，不满足 requires-python >= 3.14，须显式走 py314
conda activate py314
cd apps/inurl-byok-token-hub

# 安装（scikit-build-core 后端，纯 Python）
pip install -e ".[dev]"

# 端到端冒烟：全 mock、零真实密钥
PYTHONPATH=src python -m inurl_byok_token_hub smoke

# 启动本地代理 + 控制台
python -m inurl_byok_token_hub serve
# → http://127.0.0.1:3003/v1   控制台 http://127.0.0.1:3003/console/login
```

其他子命令：

```bash
python -m inurl_byok_token_hub catalog --capability text   # 目录统计与条目
python -m inurl_byok_token_hub strategies                  # 19 种策略
python -m inurl_byok_token_hub route inurl --combo "latency_first>round_robin"
python -m inurl_byok_token_hub compress ultra --text "..."
python -m inurl_byok_token_hub vault add --provider zhipu --api-key sk-xxx --password <口令> --user <user_id>
python -m inurl_byok_token_hub launcher                    # 启动器说明（含供应链差异）
```

## 2. 架构与分层

```
config/       配置（默认值 → config.yaml → 环境变量 BYOK_*）
models/       数据模型（pydantic v2，frozen）
crypto/       E2EE：PBKDF2-SHA256(100000) → AES-256-GCM
storage/      JSON 表仓库 + 原子写 + 跨平台单实例锁
services/     token / vault / catalog / router / strategies / compression
              health / usage / billing / chat / ops / hub
providers/    transport 抽象 + OpenAI兼容 / Anthropic / Gemini 三协议适配器
api/          FastAPI：/v1 代理、/api 账户与公开、/api/admin 后台
web/          Jinja2 精简控制台（服务端渲染，无前端构建链）
cli/          Typer 命令行
```

分层约束（由 `tests/test_audit.py::test_layer_boundaries` 守护）：`services` 不得反向依赖 `api`/`web`/`cli`；`models` 不得依赖 `services`/`api`。外部调用**必须**经 `providers.transport` 抽象，适配器中禁止直接使用 httpx。

## 3. 环境变量

| 变量 | 作用 |
|---|---|
| `BYOK_*` | 覆盖 `config.yaml` 同名项，如 `BYOK_PORT`、`BYOK_MAX_ATTEMPTS`、`BYOK_HIDE_HIDDEN_PROVIDERS` |
| `AGENT_TOKEN` | 统一令牌（对应原产品手动启动方式） |
| `AGENT_MASTERKEY` | 主密钥（同上） |
| `AUTO_MODELS` | 限定路由模型池（逗号分隔） |
| `AUTO_PROVIDER_ORDER` | 厂商优先级（逗号分隔） |

## 4. 接口清单

### 本地代理（`/v1`）

| 路由 | 鉴权 | 说明 |
|---|---|---|
| `GET /v1/models` | 用户 | 逻辑别名 + 已录入厂商的真实模型 |
| `POST /v1/chat/completions` | 用户 | OpenAI 兼容；响应含 `_route`（最终厂商/策略/切换次数/跳过原因） |
| `GET /v1/metrics` | 用户 | 控制台轮询的代理状态 |
| `GET/PUT /v1/settings` | 用户 | 路由策略、Combo、压缩档、限池 |
| `GET /v1/capabilities` | 用户 | 别名与能力标签映射 |

### 账户与密钥库（`/api`）

`POST /api/register`、`POST /api/login`、`POST /api/unlock`、`POST /api/unlock/recover`、
`GET/POST /api/escrow`、`POST /api/recover`、`POST /api/password`、
`GET/POST/DELETE /api/keys`、`GET/POST /api/orders`、`POST /api/orders/{id}/proof`

### 公开（无鉴权）

`GET /api/catalog`（`?all=1` 与默认同一份数据）、`GET /api/billing/plans`、
`GET /api/turnstile`（默认 `enabled:false`）、`GET /api/ads`、`GET /api/news`

### 管理员后台（`/api/admin`，非管理员 403）

八模块（`services/ops_service.ADMIN_MODULES`，`GET /api/admin/modules` 返回同一清单）：
`users` 用户管理 / `catalog` 厂商目录（含 `POST /api/admin/catalog/reload`）/ `plans` 套餐与订单（含 `confirm`、`reject` 人工核销）/ `redemption` 待核销订单 / `usage` 用量总览 / `content` 公告与广告位 / `config` 系统配置 / `audit` 审计日志。
端点：`GET /api/admin/{modules,users,catalog,keys,usage,orders,audit,config}`、`POST /api/admin/config`、`POST /api/admin/catalog/reload`、`POST /api/admin/orders/{id}/{confirm,reject}`。

> 口径差异见 A24：F-097 记录的后台八模块是「Turnstile 配置/邀请码/用户管理/广告/资讯/官网链接/catalog-overrides/待核销订单」，与本复刻的枚举不同。

### 控制台（`/console`）

`/console/login`、`/console/keys`、`/console/usage`、`/console/routes`、`/console/plans`、`/console/logout`

## 5. 鉴权与错误语义（逐字对齐源文档 F-085 / F-099）

| 场景 | 状态码 | 响应体 |
|---|---|---|
| 用户类接口未带/无效/过期/已撤销令牌 | **401** | `{"error": "unauthorized"}` |
| 管理员类接口越权 | **403** | `{"error": "forbidden"}` |
| 未匹配路由（含随机路径） | **401** | `{"error": "unauthorized"}` |
| 业务错误 | 4xx/5xx | OpenAI 风格 `{"error": {"message","type","code","param"}}` |

统一令牌前缀 `byok_live_`，库内**只存 SHA-256 摘要**，明文仅签发时返回一次。

## 6. 数据模型要点

- `Provider`：`tier(free/paid)` / `public` / `capabilities(text|code|image|video|audio)` / `protocol(openai_compat|anthropic|gemini)`
- `ModelEntry`：`context_window` / `free` / `behind_flagship`（付费卡落后当期旗舰 ≥1 大版本）
- `EscrowRecord`：`escrow_pw` + `escrow_rec` 双份密文 + `generation`
- `VaultKeyRecord`：只含 `CipherBlob`（alg/kdf/iterations/salt/iv/ct），**不含明文**
- `RouteDecision`：候选顺序、跳过原因、最终厂商、每次尝试记录（可审计）

## 7. 测试与构建

```bash
conda run -n py314 python -m pytest -q --cov=inurl_byok_token_hub
conda run -n py314 python -m ruff check .
```

- 覆盖：整体 **87.6%**（170 项测试全通过；阈值：整体 ≥80%、关键模块 ≥90%）
- 关键模块：crypto **100%** / compression **96%** / vault **95%** / token_service **94%** / router **92%** / billing **92%** / providers **91~95%** / api/deps **100%**
- CLI 冒烟已纳入 pytest（`tests/test_cli.py`），不再是「只有人工跑过」的证据
- 构建后端：**scikit-build-core**（`apps/*` Python 子项目的仓库默认；`apps/agent-monetize` 的 setuptools 属历史违规，不可作为先例）
- 新增测试须保持：无 `from __future__` 导入、无令牌/密钥字面量、无 file 协议本地绝对路径（`tests/test_audit.py` 静态门禁会自动拦截）
- 覆盖率口径：本机 `conda run -n py314 python -m pytest -q --cov=inurl_byok_token_hub`

## 8. 假设与差异说明

> 每条含「默认值 / 溯源 / 风险提示 / 代码定位」。

| # | 假设 | 默认值 | 溯源 | 风险与说明 | 代码定位 |
|---|---|---|---|---|---|
| A1 | 运行环境 | conda `py314`（Python 3.14.3） | 仓库既有 Python 应用惯例 | 本机默认 python 为 3.13.12，须显式走 py314 | `pyproject.toml:requires-python` |
| A2 | 持久化 | JSON 文件仓库 + 可插拔 `Repository` | 文档未指定存储 | 单机场景足够；多实例写入靠单实例锁互斥 | `storage/repository.py` |
| A3 | 目录数据 | 内置种子 `data/catalog.json`（46/17/29/10/133） | F-077/F-082/F-090/F-091 | **非实时抓取，不可作为免费政策事实源**（F-079/F-080 已证原站目录陈旧）；具名 8 家标 `doc`，其余标 `seed` | `data/catalog.json`、`services/catalog_service.py` |
| A4 | AEAD 依赖 | 硬依赖 `cryptography` 46.0.7 | 标准库无 AEAD | 不提供自研 GCM 回退——手写密码学原语是安全反模式 | `crypto.py` |
| A5 | 流式 | `stream=true` 返回 `text/event-stream`：role 首帧 → 内容分帧（24 字符/帧）→ finish 尾帧（附 `_route`）→ `data: [DONE]` | F-027「SSE 透传」（`references/verification.md` 标注「仅文案未登录实测」） | 上游在本实现只返回完整响应，故为**本地降级切分下发**，非真流式透传；未实现 `stream_options.include_usage` 用量帧，首字节后不跨厂商续写 | `api/proxy.py:_sse_stream` |
| A6 | 控制台 | 精简 Jinja2 服务端渲染四页 | 文档只描述界面 | 不还原原产品全部交互 | `web/console.py` |
| A7 | 启动器 | 只生成说明，**不下载、不内嵌密钥** | F-053 供应链风险 | 与原产品 `byok-launch` 每次 curl 拉取闭源脚本的行为**相反**，这是本复刻最重要的安全差异 | `cli.py:launcher` |
| A8 | 邀请奖励 | 每邀请 1 人 +1 密钥额度，上限 +5 | 文档未给数值 | 可在 `config.yaml` 调整 | `config.yaml:invite_bonus_*` |
| A9 | 隐藏厂商 | 默认随公开接口下发（保持原产品行为）+ `hide_hidden_providers` 开关 | F-077 | 默认行为会暴露预留/测试厂商，生产建议开启开关 | `config.py`、`api/public.py` |
| A10 | 主密钥驻留 | 解锁后仅驻留进程内存，重启需重新解锁 | 原产品由启动器内嵌 | 落盘仅密文，进程内明文不写盘 | `services/hub.py` |
| A11 | 故障切换边界 | 仅 429 与 5xx 切换；400/401/403/404 不切换 | F-048 有证据 | 切换上限、熔断阈值（连续 3 次失败、冷却 30s）属本实现默认 | `config.yaml`、`services/health_service.py` |
| A12 | 19 策略算法 | 名称集合取自界面证据，排序算法为本实现默认 | F-095 | 原产品闭源，不得宣称策略行为等价 | `services/strategies.py` |
| A13 | 压缩率 | 5 档规则式实现，返回估算值 | F-095（页面自标「估算值」） | 压缩率属厂商自述，**不作承诺指标**；代码块/链接/JSON 强制原样保留，自检失败则回退原文 | `services/compression_service.py` |
| A14 | 支付 | 仅状态机（创建→凭证→人工核销），无资金流转 | F-097/F-098 | 不接入支付宝，不实现返佣短链 | `services/billing_service.py` |
| A15 | 运营内容 | 示例广告/公告，无埋点、无返佣 | F-084/F-086 风险项 | 不实现 `track.js` 式第一方行为采集 | `services/ops_service.py` |
| A16 | 改密语义 | 重新包裹主密钥（不重加密全部密钥） | F-075「改密重加密」表述模糊 | 更安全且无需恢复密语在场；密钥 `generation` 递增可审计 | `services/vault_service.py` |
| A17 | 监听地址 | 仅回环（127.0.0.1 / ::1 / localhost），配置期即拒绝 | 原产品代理仅本机 | 不提供 `--host 0.0.0.0`，对外暴露需自建受 TLS 的反向代理 | `config.py:Settings.__post_init__` |
| A18 | video/audio | 明确返回「当前没有支持该类别的厂商」 | F-082 | 目录无对应能力厂商，不伪装支持 | `services/catalog_service.by_capability` |
| A19 | 未知请求字段 | 非白名单键（`model`/`messages`/`stream`/`temperature`/`max_tokens` 之外）进 `ChatRequest.extra`：OpenAI 兼容原样透传，Anthropic/Gemini 显式 422 `unsupported_feature` | 「无法映射的字段不得静默丢弃」契约 | 严格策略会让携带 `tools`/`top_p` 的客户端在 Anthropic/Gemini 上直接 422，这是刻意取舍而非缺陷 | `api/proxy.py:_CHAT_KNOWN_KEYS` |
| A20 | 厂商线协议来源 | 密钥记录协议 = 显式指定 > 目录厂商协议 > `openai_compat` 兜底 | F-047 三协议 | 若沿用默认兜底，目录内的 Anthropic/Gemini 厂商将永远走不到各自适配器 | `services/vault_service.py:_resolve_protocol` |
| A21 | 双 escrow 归属 | **服务端代生成**主密钥；`POST /api/escrow` 接管客户端生成的 escrow 时必须同传 `password`，服务端据此解出新主密钥并重写全部密钥密文 | F-052（原产品为浏览器端 E2EE，主密钥不出浏览器） | 与原产品相反：本地代理转发需要明文 Key，服务端必须能解出主密钥；缺少 `password` 时明确 400，不谎报 `stored` | `api/account.py:post_escrow`、`services/vault_service.py:adopt_client_escrow` |
| A22 | 管理员令牌文件 | 运行期 `{data_dir}/admin.token` 为**明文**令牌（权限 0600 + 启动告警），库内仍只存摘要 | 便于 CLI/演示直接读取 | 拿到该文件即等同管理员权限；生产部署应删除该文件并改走 `/api/login` | `services/hub.py:ensure_admin` |
| A23 | 路由运行期状态 | Combo 每层产出独立候选序列（本层耗尽流转下一层）；轮询游标按用户驻留内存（重启归零）；无健康样本时按厂商 id 派生 20~70ms 稳定伪基线延迟 | F-095「Combo（`>` 分层流转）」 | 伪基线仅用于打破并列，不代表真实延迟；进程重启后轮询回到起点 | `services/router_service.py`、`services/chat_service.py` |
| A24 | 后台模块口径 | 八模块按 spec FR-10 重新枚举（用户/目录/套餐订单/核销/用量/内容/配置/审计） | F-097 的枚举含 Turnstile 配置、邀请码、官网链接、catalog-overrides | 与 F-097 **不一致**：本复刻按可实施性取舍，四项未单列（Turnstile 走 `config`，邀请码走注册参数） | `services/ops_service.py:ADMIN_MODULES` |

## 9. 安全边界（必读）

1. **E2EE 覆盖「落库泄露」**：明文厂商 Key 不落盘、不进日志（日志统一脱敏，仅显示前缀与后 4 位）。
2. **E2EE 不覆盖**：Python 运行时无法保证内存字符串彻底清零；同用户进程、调试器、恶意依赖不在防护承诺内。
3. **供应链**：本项目不在运行时下载或执行任何远端代码，也不在启动器中内嵌令牌或主密钥。若你自行修改启动脚本绕过此约束，风险自负。
4. **停止服务**：按 PID 精确终止或用 Ctrl-C，**不要**使用 `taskkill /f /im node.exe` 这类会误杀其他进程的命令。
5. **额度与费用**：故障切换可能产生重复计费；只有明确未提交或上游明确返回 429/5xx 时才自动换路。
6. **目录数据**：`data/catalog.json` 为种子数据，免费政策请以厂商官方文档为准。

## 10. 源文档边界

源知识包 `status: flagged`，核心勘误 E1（免费档仅 3 个厂商密钥，「17 家 Key + 0 元」不成立）、E2（DeepSeek 官方收费）、E5（Agnes 免费档 512K）、E4（百度千帆每模型 100 万 / 3 个月）均已体现在实现中：

- `deepseek` 的 `tier = paid`；
- `agnes` 免费模型 `context_window = 524288`；
- 免费档密钥上限硬校验 3（超限返回 `key_limit_exceeded` 与升级提示）。
