# inurl BYOK Token Hub - Implementation Plan

> 方法论编排：seven-concepts（scenario = innovation，链路 F→V→I→C，depth=deep，V 强制）
> 会话前缀：`sc-20260929-inurl-token-hub`
> Spec：同目录 `spec.md`（AC-1 ~ AC-11）
> 交付落点：`apps/inurl-byok-token-hub/`（先在 `.temp/inurl-byok-token-hub/` 开发，验证后迁移）
> 验证环境：conda 环境 `py314`（Python 3.14.3）
> **状态：等待用户批准（Approve 门）后方可实施**

## Task 1: 项目骨架与配置层（config）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `.temp/inurl-byok-token-hub/` 建立 src-layout：`src/inurl_byok_token_hub/{config,errors,models,crypto,services,providers,api,cli,web}`，`tests/`，`data/catalog.json`，`pyproject.toml`（scikit-build-core 后端、`requires-python>=3.14`、ruff/pytest/coverage 配置对齐 `apps/agent-monetize`）。
  - `config.py`：默认值 → YAML → 环境变量（`BYOK_*`、`AGENT_TOKEN`、`AGENT_MASTERKEY`、`AUTO_MODELS`、`AUTO_PROVIDER_ORDER`）三级合并，输出冻结的 `Settings` 数据类；含监听地址/端口（默认 `127.0.0.1:3003`）、API 前缀 `/v1`、数据目录、故障切换状态码集（429+5xx）、超时重试、套餐定义、管理员初始账户、Turnstile 默认 `false`、`hide_hidden_providers=false`。
  - `errors.py`：统一错误码枚举 + 中文异常体系 + 异常→HTTP 映射。
- **Acceptance Criteria Addressed**: AC-1（部分）、AC-9
- **Test Requirements**:
  - `rule` TR-1.1: 三级配置合并优先级正确，环境变量可覆盖 YAML 与默认值；`Settings` 冻结不可变。证据：`pytest -k config` 通过。
  - `rule` TR-1.2: `pyproject.toml` 构建后端为 `scikit-build-core`，`requires-python>=3.14`，`wheel.packages` 指向 `src/inurl_byok_token_hub`，且不存在 `cmake.*` dotted key 与 `[tool.scikit-build.cmake]` 并存（避免 `pip install -e .` 静默挂起）。证据：pyproject 内容 + `conda run -n py314 pip install -e .` 成功输出。
  - `rule` TR-1.4: 静态审计测试可红绿复现：断言构建后端为 `scikit_build_core.build`；依赖落在声明白名单；源码与测试中无真实 Key/口令/`byok_live_` 字面量/`file:///` 路径；运行期数据目录在 git 中零条目。故意写入 setuptools 后端或明文 Key 字面量时测试须失败。证据：`pytest -k audit` 绿 + 故意污染后红的两次输出。
  - `rubric` TR-1.3: 维度=配置与错误码设计完备性；1-5；1=散落魔法值/无错误码；3=有配置但边界项缺失；5=全部 FR-1 字段齐备、错误码语义单一且可映射到 HTTP。阈值 >= 4。证据：审查者对照 FR-1/FR-4 逐项核查。
- **Notes**: 不写 cmake 段（纯 Python）；包名与目录为 `inurl_byok_token_hub` / `apps/inurl-byok-token-hub`（沿用用户指定名词），不使用 `tokenhub` 等简称。运行期命令一律走 `conda run -n py314 ...`（本机默认 python 为 3.13.12，不满足 >=3.14）。
  构建后端模板直接抄 `apps/dev-tools/zhihu-checkin-hub/pyproject.toml:1-3` 与 `:31-36`：`requires = ["scikit-build-core>=0.9"]`、`build-backend = "scikit_build_core.build"`、`[tool.scikit-build]` 含 `wheel.packages = ["src/inurl_byok_token_hub"]`、`wheel.cmake = false`、`build.verbose = false`、`build-dir = "build/{wheel_tag}"`、`minimum-version = "0.9"`；目录内不建 CMakeLists.txt。apps 区已有 zhihu-checkin-hub / wechat-mp-archiver / containers-shared / containers-client 四个同款实例；`apps/agent-monetize` 的 setuptools 是**历史违规**（根 `AGENTS.md:116` 明文禁止），不得作为先例。
  FastAPI 分层与测试写法参照 `apps/dev-tools/zhihu-checkin-hub`：`web/app.py:76-94` 的 `create_app(cfg, ...)` 工厂 + `app.state.svc`、`web/security.py` 的 CSRF/Origin 白名单/`SingleInstanceLock`、`config.py:21-107` 的 `@dataclass(frozen=True) Config` + 四级优先级、`errors.py:4-35` 中文异常体系；测试用 `fastapi.testclient.TestClient` + fixture 链 + `test_audit.py` 式静态审计。
  ruff 非仓库级硬门禁（根 AGENTS.md 无条款，仅 zhihu 自选并绑定 CI）；本应用按 zhihu 口径配 `target-version = "py314"`，并沿用其 TID251 禁用 `from __future__ import annotations`（注意：`apps/agent-monetize/src/agent_monetize/cli.py:3` 违反该口径，不得照抄）。

## Task 2: 数据模型层（models）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - pydantic v2 模型：`Provider`、`ModelEntry`、`User`、`UnifiedToken`、`RecoverySecret`、`VaultKeyRecord`、`EscrowRecord`、`RouteRequest`/`RouteDecision`、`StrategySpec`（19 种注册表）、`ComboSpec`（`>` 分隔）、`CompressionSpec`（5 档）、`UsageRecord`/`BillingEvent`、`AdminPaymentOrder`、`AdItem`/`NewsItem`。
  - `Repository` 协议 + JSON 文件实现（持久化目录可配置），令牌只存 SHA-256 摘要，密文 blob 含 `alg/iter/salt/iv/ct`。
- **Acceptance Criteria Addressed**: AC-2、AC-6、AC-7
- **Test Requirements**:
  - `rule` TR-2.1: 每个模型可序列化/反序列化往返一致；`UnifiedToken` 落盘字段不含明文令牌（仅摘要）。证据：`pytest -k models` 通过 + 落盘 JSON grep 无明文。
  - `rule` TR-2.2: 19 种策略与 5 档压缩常量注册表条目数分别为 19 与 5，别名表含 `inurl/inurl-text/auto/default/inurl-code/inurl-image/inurl-video/inurl-audio`。证据：断言输出。
- **Notes**: 模型不得反向依赖 services/api。

## Task 3: E2EE 托管库（crypto + vault_service）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `crypto.py`：`derive_master_key(password, salt, iterations=100000, SHA-256)` → 256-bit；`aes_gcm_encrypt/decrypt`；`make_escrow_pair`（`escrow_pw` + `escrow_rec` 双密文）；**只持久化密文**，明文不落盘、不入日志。
  - `services/vault_service.py`：密钥录入/列表/删除/状态流转（`active`/`error`/`quota_exhausted`）、双 escrow 存储、`/api/recover` 恢复、`/api/password` 改密重加密；列表接口永不下发明文。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-3.1: PBKDF2/SHA-256/100000 迭代/AES-GCM-256 参数逐字正确；加解密往返一致；不同 salt 产生不同密文。证据：`pytest -k crypto` 输出。
  - `rule` TR-3.2: 落盘文件 grep 不到明文 Key 子串；日志输出仅显示前缀与后 4 位。证据：grep + caplog 断言。
  - `rule` TR-3.3: 恢复流程可用恢复密语还原原文；改密后旧口令解密失败、新口令成功。证据：`pytest -k vault` 通过。
- **Notes**: 若 `cryptography` 不可用，提供纯标准库 GCM 回退并在 README 标注（假设 A4）。

## Task 4: 统一令牌、鉴权与错误中间件（token_service + auth + api 错误）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `byok_live_` 前缀签发（熵 ≥128 bit）、校验、轮换（宽限期）、吊销；库内只存 SHA-256。
  - 依赖注入式 `require_user` / `require_admin`；用户类未授权 → **401** 裸 JSON `{"error":"unauthorized"}`；管理员类非管理员 → **403** `{"error":"forbidden"}`；**未匹配路由 → 401**；`/api/ads`、`/api/news`、`/api/catalog`、`/api/billing/plans`、`/api/turnstile` 无鉴权公开。
  - Turnstile 默认 `enabled:false`，开启后校验失败返回 401。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-4.1: 7 组鉴权断言（无令牌/无效令牌/越权/随机路径/5 个公开端点）状态码与 body 逐字匹配。证据：`pytest -k auth` 输出。
  - `rule` TR-4.2: 令牌前缀为 `byok_live_`，存储仅摘要；轮换后旧令牌在宽限期内可用、期外 401。证据：测试断言。
- **Notes**: 裸 JSON 指不包 HTML 错误页、不加外层包装字段。

## Task 5: 目录与能力（catalog_service + data/catalog.json）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 种子目录：46 providers（17 free + 29 paid，含 10 个 `public:false`）、133 models；条目含 `source=seed` 标记；DeepSeek 标 `tier=paid`；Agnes 免费档 `context=512K`；付费卡带 `behind_flagship:true` 时效标记。
  - 服务：`?all=1` 与默认同数据（对齐 F-077）、按 capability/tier 过滤、video/audio 返回"当前没有支持该类别的厂商"、目录快照与 `reload`（对应"catalog 更新需重启代理"）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-5.1: provider 总数 46、model 总数 133、free 17、paid 29、hidden 10；`?all=1` 与默认响应逐字节一致。证据：`catalog` CLI + 测试快照。
  - `rule` TR-5.2: `capability=video|audio` 返回空与指定提示文案；`tier` 过滤计数正确；付费条目带 `behind_flagship`。证据：断言输出。
- **Notes**: README 明示种子数据非实时抓取、不可作免费政策事实源（F-079/F-080）。

## Task 6: 路由与故障切换（router_service + 19 策略 + Combo）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 别名解析（含旧别名 `auto`/`default` 与真实模型 id 直通）；19 种策略实现与注册表；`>` 分隔 Combo 链逐层回退；429/5xx 切下一家（可配状态码集与最大尝试）；`AUTO_MODELS`/`AUTO_PROVIDER_ORDER` 限池；额度耗尽/熔断厂商退出候选。
  - 产出可审计 `RouteDecision`（候选顺序、跳过原因、最终厂商、尝试记录）。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-6.1: 19 种策略均可被单独选中并产生确定性或明确随机的选择；注册表条目数 19。证据：`pytest -k router` 参数化输出。
  - `rule` TR-6.2: A=429、B=503、C=200 场景下最终落 C 且 `RouteDecision` 记录两次跳过原因；Combo `延迟优先>轮询` 按层级流转。证据：测试断言。
  - `rule` TR-6.3: `inurl-video` 返回"当前没有支持该类别的厂商"；`AUTO_PROVIDER_ORDER` 限池生效。证据：断言输出。
- **Notes**: 随机类策略需可注入种子以保证测试确定性。

## Task 7: 提示词压缩（compression_service）
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 5 档规则式压缩（Lite≈15%/Standard≈30%/Aggressive≈50%/Ultra≈75%/RTK 60–90% 工具链去重）；**代码块、链接、JSON 原样保留**；返回估算压缩率；自检判定会损坏内容时拒绝压缩并回退原文。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-7.1: 5 档 × 3 类保护对象（代码块/URL/JSON）逐字保留；每档返回非空结果与估算压缩率。证据：`pytest -k compress` 输出。
  - `rule` TR-7.2: 至少 1 例触发"拒绝压缩并回退原文"（返回结果与原文相等且标记 refused）。证据：断言输出。
- **Notes**: 压缩率为估算值，不得作为承诺指标写进 README 结论。

## Task 8: 外部依赖调用（providers：openai_compat / anthropic / gemini + transport）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `transport` 抽象（httpx 实现 + mock 实现）；三协议适配器按 FR-8 的路径/头/查询参数约定；统一 `ChatRequest`/`ChatResponse` 归一化；统一错误码（429/5xx/超时/鉴权失败）。
  - 自定义厂商 CRUD 与三协议配置校验。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-8.1: 三种协议的请求方法、路径、头、查询参数逐项匹配 FR-8；响应归一化为同一 `ChatResponse` 结构。证据：mock transport 录制快照断言。
  - `rule` TR-8.2: 429/5xx/超时/401 分别映射为统一错误码，并可供 router 判定是否切换。证据：`pytest -k providers` 输出。
- **Notes**: 不实现联网集成测试；仅 mock（OQ-1 默认否）。

## Task 9: 健康度、用量与计费（health + usage + billing_service）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2, Task 8
- **Description**:
  - 每厂商成功率/延迟/连续失败/熔断；"手填额度 − 已用 = 剩余"用量统计与全局台账；额度耗尽退出候选池。
  - 套餐：免费 ¥0/3 密钥、标准 ¥9.9/10、专业 ¥29.9/无限；写入密钥强制上限校验（明确错误码 + 升级提示）；邀请奖励默认 +1（上限 +5，可配）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-9.1: 免费档第 4 个、标准档第 11 个密钥被拒且错误码/升级提示正确；专业档放行。证据：`pytest -k billing` 输出。
  - `rule` TR-9.2: 模拟调用后用量 +1，剩余额度 = 手填额度 − 已用；额度耗尽厂商退出候选池（router 的 `RouteDecision` 记录跳过原因）。证据：断言输出。
- **Notes**: 套餐上限与 E1 勘误口径一致，不得放宽。

## Task 10: 接口层（api：代理 / 账户 / 密钥库 / 公开 / 用户设置 / 管理员后台）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6, Task 8, Task 9
- **Description**:
  - 本地代理：`GET /v1/models`、`POST /v1/chat/completions`（含 `stream` 的 SSE 最小实现）。
  - 账户：`/api/register`、`/api/login`、`/api/escrow`、`/api/recover`、`/api/password`。
  - 密钥库：CRUD + 状态 + 用量（永不下发明文）。
  - 公开：`/api/catalog`、`/api/billing/plans`、`/api/turnstile`、`/api/ads`、`/api/news`。
  - 用户设置：路由策略/Combo/压缩档/自定义厂商。
  - 管理员：八模块后台 + 人工核销订单状态机（`created → proof_submitted → confirmed/rejected`）+ 审计日志。
  - 未匹配路径 → 401 裸 JSON。
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-6、AC-8
- **Test Requirements**:
  - `rule` TR-10.1: `/v1/models` 同时返回逻辑别名与真实模型；`/v1/chat/completions` 返回归一化响应（含一次故障切换）。证据：TestClient 断言输出。
  - `rule` TR-10.2: 后台八模块端点在非管理员下 403、管理员下 200；人工核销状态机流转正确且写入审计日志。证据：`pytest -k admin` 输出。
- **Notes**: 错误响应统一走 Task 4 的中间件。

## Task 11: 系统后台运营数据（ops_service：广告位 / 公告 / 配置）
- **Status**: `completed`
- **Priority**: low
- **Depends On**: Task 2
- **Description**:
  - `AdItem`/`NewsItem` 数据与 `/api/ads`、`/api/news` 公开接口（无鉴权）；后台侧 CRUD；系统配置读写（Turnstile 开关、隐藏厂商开关、路由默认值）。
- **Acceptance Criteria Addressed**: AC-1（公开端点部分）
- **Test Requirements**:
  - `rule` TR-11.1: 无令牌访问 `/api/ads`、`/api/news` 返回 200；后台 CRUD 需管理员且写入审计日志。证据：断言输出。
- **Notes**: 不实现行为采集与返佣（NFR-7）。

## Task 12: CLI、精简控制台与端到端冒烟（cli + web）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - CLI：`serve`、`catalog`、`route`（干跑）、`compress`、`vault`、`smoke`、`launcher`（生成启动脚本说明，默认不下载/不内嵌密钥）。
  - `web/`：Jinja2 服务端渲染精简控制台（密钥库、用量、路由/压缩设置、套餐与订单）。
  - `python -m inurl_byok_token_hub smoke`：全 mock、零真实密钥跑通 注册 → 令牌 → 录入 3 Key → 启代理 → `/v1/models` → 聊天（含故障切换）→ 用量 → 后台/403。
- **Acceptance Criteria Addressed**: AC-8、AC-9
- **Test Requirements**:
  - `rule` TR-12.1: `python -m inurl_byok_token_hub smoke` 退出码 0 且逐步骤打印结果。证据：完整 stdout。
  - `rule` TR-12.3: 监听地址守卫：在**配置加载期**拒绝非 loopback host（传入 `0.0.0.0` 直接退出码非 0，不进入 uvicorn）；403 响应不回显 Origin。证据：命令退出码 + 测试断言。
  - `rule` TR-12.4: 单实例锁（复用仓库既有的跨平台非阻塞文件锁范式，不自造 PID 文件）：第二个实例立即失败并给出中文指引；进程被强杀后锁自动释放、可再次启动。证据：两次启动输出。
  - `rule` TR-12.5: 配置/密文库并发写入使用 `pid+random` 临时名 + `os.replace` 原子替换，并发不互踩且崩溃后无半写残留。证据：并发写测试输出。
  - `rubric` TR-12.2: 维度=控制台与 CLI 可用性；1-5；1=无法启动或页面报错；3=可启动但关键操作缺失；5=四个控制台页面与全部子命令可用、错误提示清晰。阈值 >= 4。证据：审查者实际操作记录。
- **Notes**: 冒烟使用临时数据目录，不污染仓库。

## Task 13: README 与假设/差异说明
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - README：产品定位与架构图（Mermaid）、目录结构、启动方式、环境变量表、接口清单、数据模型表、模块职责、测试与构建。
  - **「假设与差异说明」章节**：逐条编号（A1~A9 及实现期新增假设），每条含默认值、溯源（F 编号 / E 勘误 / 文档章节）、风险提示、代码定位。
  - 安全提示：E2EE 覆盖范围与不覆盖的供应链层、匿名主体风险、video/audio 不可用、种子目录非事实源。
- **Acceptance Criteria Addressed**: AC-11、AC-10（部分）
- **Test Requirements**:
  - `rubric` TR-13.1: 维度=假设与差异说明完备性与可追溯性；1-5；1=缺失或一句带过；3=列出主要假设但缺溯源/风险；4=逐条编号含默认值、溯源与风险；5=4 且每条可在代码定位 + 给出安全使用建议。阈值 >= 4。证据：审查者抽查 3 条假设的代码可定位性。
- **Notes**: 禁止把压缩率、provider 数量等自述数字写成事实承诺。

## Task 14: 迁移至 apps/ 与仓库索引登记
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 从 `.temp/inurl-byok-token-hub/` 迁移到 `apps/inurl-byok-token-hub/`，清理临时产物。
  - 更新仓库索引（四处，缺一即不完整）：① `apps/AGENTS.md:41-68` 应用路由表新增条目；② `apps/AGENTS.md:231-286` 边界声明表新增一行（归属「应用自治（遵循根规范）」，末列「✅ 是」）；③ 先写应用 `README.md` 再跑 `python .agents/scripts/docgen.py apps` 刷新 `apps/README.md` 的 `<!-- APPS_TABLE_START/END -->` 自动清单（`generate-apps-index.py` 是其向后兼容包装，二选一即可）；④ `apps/README.md:116` 的维护约定目前只点名 `agent-monetize/`，新增第二个根级应用时同步补上本应用。
  - 运行 `ruff check`、`pytest --cov`（整体 ≥80%、关键模块 ≥90%）；可选新增 `.github/workflows/inurl-byok-token-hub-ci.yml`，照抄 `zhihu-checkin-hub-ci.yml`（paths 过滤 + python-version 3.14 + `pip install -e ".[dev]"` + `ruff check .` + `pytest -q`）。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-14.1: 应用位于 `apps/inurl-byok-token-hub/`；`ruff check` 零错误；覆盖率达标（整体 ≥80%、关键模块 ≥90%，依据根 `AGENTS.md:122` 与 `docs/tech/references/development-standards.md:228`）。证据：命令输出。
  - `rule` TR-14.2: 四处索引均已登记——`apps/AGENTS.md` 路由表与边界声明表各含本应用、 `apps/README.md` 自动清单含本应用；且根级 `pytest` 不误收该应用测试（靠应用内 `testpaths = ["tests"]`）。证据：grep 输出 + 根目录 pytest 输出。
- **Notes**: 迁移后重跑一次冒烟确认路径无关。

## Task 15: 对抗审查（V，强制）与原子提交（C）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 14
- **Description**:
  - V 阶段：四视角（魔鬼代言人/新人/老板/未来）攻击实现与文档，输出 ≥5 条具体意见并至少采纳 2 条修正，记录修正对照。
  - C 阶段：按原子切片逐个 Conventional Commits 中文主体提交（骨架/模型/加密/鉴权/目录/路由/压缩/厂商/计费/接口/CLI/文档/迁移）。
  - 队列清空后由**独立上下文**创建 `review.md` 执行 Review（实施者自验不算验收）。
- **Acceptance Criteria Addressed**: AC-10、AC-11
- **Test Requirements**:
  - `rule` TR-15.1: V 阶段输出 ≥5 条具体意见、采纳 ≥2 条并留有修正对照记录。证据：审查记录文件/日志。
  - `rubric` TR-15.2: 维度=架构分层与职责单一性；1-5；1=层次混杂/跨层反向依赖/外部调用散落；3=分层基本成立但有跨层捷径；5=分层严格、无反向依赖、外部调用全经 transport、每模块单一职责。阈值 >= 4。证据：独立审查者附文件/行的评分依据。
  - `rule` TR-15.3: 提交历史为原子切片、信息符合 Conventional Commits 中文主体。证据：`git log --oneline` 输出。
- **Notes**: Review 必须新开独立上下文执行；`fail` 则固化 issue 回 Implement 修复后复审。

# Task Dependencies

- Task 1 为全部任务的基础（配置与错误码）。
- Task 2 依赖 Task 1；Task 3/4/5 依赖 Task 2。
- Task 6 依赖 Task 5；Task 7 独立（仅依赖 Task 2）；Task 8 依赖 Task 2。
- Task 9 依赖 Task 2 与 Task 8。
- Task 10 依赖 Task 3、4、5、6、8、9（接口聚合层）。
- Task 11 依赖 Task 2。
- Task 12 依赖 Task 10。
- Task 13 依赖 Task 12；Task 14 依赖 Task 13；Task 15 依赖 Task 14。
- 可并行：Task 5 与 Task 7 与 Task 8（互不修改同一文件）；Task 11 与 Task 6/9 可并行。

# 状态约定

- 所有任务初始 `pending`；**Approve 门前不得改为 `in_progress`**。
- `completed` 必须附 `Completion Evidence`（命令输出 / 测试结果 / 文件路径）。
