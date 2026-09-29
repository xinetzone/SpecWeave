# Review — inurl BYOK Token Hub（Python 3.14+ 复刻）

> Spec：同目录 `spec.md`（AC-1 ~ AC-11） · Plan：同目录 `tasks.md`（Task 1~15）
> 交付落点：`apps/inurl-byok-token-hub/`（86 个文件）
> 审查日期：2026-09-29
> 审查上下文：**独立上下文**（由未参与实现的审查者执行；实施者自验不计入验收，见 TR-15 / TRAE-spec-mode Review 阶段要求）
> 验证环境：conda `py314`（Python 3.14.3）；`pytest` 170 passed；`ruff check .` All checks passed；`--cov` 87.64%；`smoke` 19/19 PASS

## 1. 结论

**通过**（进入 C 阶段原子提交）。

审查共提出 9 条意见：阻塞 2 条、重要 4 条、建议 3 条。实施侧**采纳 8 条、部分采纳 1 条、驳回 0 条**；
2 条阻塞项已在本次审查内修复并用红→绿用例锁死，3 条「重要」项达标（关键模块覆盖率由 81% → 92~100%）。

## 2. AC 逐条判定

| AC | 判定 | 关键证据 |
|---|---|---|
| AC-1 鉴权语义 | ✅ 通过 | `tests/test_auth.py`：无令牌/无效令牌/未匹配路由均 401 且 body 逐字 `{"error":"unauthorized"}`；非管理员访问 `/api/admin/modules` 为 403 `{"error":"forbidden"}`；5 个公开端点无令牌 200 |
| AC-2 E2EE | ✅ 通过（修复后） | PBKDF2-SHA256/100000 → AES-256-GCM；双 escrow；`raw_text()` 无明文 Key/恢复密语；**`POST /api/escrow` 由谎报 `stored:True` 改为真正落盘并接管主密钥**（R2） |
| AC-3 路由 | ✅ 通过（修复后） | 别名含旧 `auto`/`default`；19 策略注册表齐全；**Combo 分层流转由「扁平去重」改为逐层回退**（R1）；video/audio 明确 422 `unsupported_capability` |
| AC-4 压缩 | ✅ 通过 | 5 档；代码块/URL/JSON 原样保留；2 例「拒绝压缩原样回退」；**新增 API 侧接线用例**（此前无人守护，且修复了 LITE 档被误压缩的缺陷，R7） |
| AC-5 三协议 | ✅ 通过 | OpenAI 兼容 Bearer / Anthropic `x-api-key` / Gemini `?key=`；429/5xx 可切换、401/403/404 不可切换（参数化双维）；不可映射字段 → 422 `unsupported_feature`（HTTP 层新增端到端用例） |
| AC-6 计费 | ✅ 通过 | 免费 3 / 标准 10 / 专业无限；价格 0/990/2990 分（E1 勘误）；额度 = 手填 − 已用；订单状态机含非法流转拒绝 |
| AC-7 目录 | ✅ 通过 | 46 = 17 free + 29 paid（10 个 `public:false`）、133 模型；video/audio 无厂商；DeepSeek=paid（E2）、Agnes 免费 512K（E5） |
| AC-8 冒烟 | ✅ 通过 | `smoke` 19/19 PASS；**已纳入 `tests/test_cli.py`**（此前 CLI 覆盖率 0%） |
| AC-9 工程质量 | ✅ 通过 | ruff 零错误；覆盖 87.64%（≥80%）；关键模块 92~100%（≥90%）；scikit-build-core + `requires-python>=3.14` + 无 cmake 段；四处索引已登记 |
| AC-10 分层（rubric ≥4） | ✅ 4/5 | 层次严格、外部调用全经 `providers/transport.py`、静态门禁守护 services↛api/web/cli；扣分：`web/console.py` 反向引用 `api/deps`、`api/account.py` 直读 `hub._master_keys` |
| AC-11 README（rubric） | ✅ 5/5 | A1~A24 每条含「默认值 / 溯源 F 编号 / 风险提示 / 代码定位」；抽查 A3/A17/A20/A21 定位精确可达；审查指出的 3 处「实际行为未登记」已补为 A21~A24 |

## 3. V 阶段意见与处置（修正对照）

| # | 级别 | 意见 | 处置 | 修正对照（改了什么 / 现在的行为） |
|---|---|---|---|---|
| 1 | 阻塞 | Combo 回退链形同虚设：各层作用于同一份全量候选后全局去重，第 2 层起零贡献；`round_robin` 的 `counter` 恒为 0（`bump_counter` 无调用点） | ✅ 采纳 | `services/router_service.py`：`RoutePlan` 新增 `layers`（每层一份有序候选），`plan()` 逐层产出并维护 per-user 轮询游标；`services/chat_service.py`：改为「层内依次尝试 → 本层耗尽进下一层」，不可重试错误置 `stop` 不再流转。`tests/test_router.py::test_combo_produces_one_layer_per_strategy`、`test_round_robin_rotates_across_calls`、`tests/test_api.py::test_chat_failover_crosses_combo_layers`（第一层两家全 429 后由第二层兜底成功，failover=2） |
| 2 | 阻塞 | `POST /api/escrow` 返回 `stored:True` 却从不落盘，客户端提交的密文被静默丢弃 | ✅ 采纳 | `services/vault_service.py::adopt_client_escrow` + `api/account.py::post_escrow`：要求同传 `password` → 校验口令并取旧主密钥 → 解开上传的 `escrow_pw` 得到客户端新主密钥 → `reencrypt_all` 重写全部密钥密文 → 落盘并递增 `generation`；缺 `password` 明确 400。`tests/test_api.py::test_client_escrow_is_actually_stored`、`test_escrow_upload_without_password_is_rejected` |
| 3 | 重要 | 管理员令牌明文写入 `{data_dir}/admin.token`，与 NFR-3「令牌只存摘要」及 A10「落盘仅密文」自述矛盾 | ✅ 采纳 | `services/hub.py`：`_restrict_permissions()` 收紧为 0600（Windows best-effort）+ 启动 `logger.warning` 明示「拿到该文件即等同管理员权限」；README 新增 **A22** 登记该差异与生产建议（删文件、改走 `/api/login`） |
| 4 | 重要 | NFR-2「关键模块 ≥90%」未达成：`token_service` 81%、`api/deps` 83%、`vault_service` 82%；CLI 0% | ✅ 采纳 | 新增 `tests/test_cli.py`（CliRunner 跑 `smoke`/`catalog`/`strategies`）、`test_auth.py` 5 项（login、require_user/require_admin、`X-API-Key` 分支、改密与恢复往返）、`test_vault.py` 2 项（`mark_error`/`remove_key`、非法 blob 拒绝）。现状：crypto 100%、compression 96%、vault 95%、token_service 94%、router 92%、billing 92%、providers 91~95%、api/deps 100%、整体 87.64% |
| 5 | 重要 | 冷启动时 19 策略退化为同一顺序（健康/用量全等 → `sorted` 恒等）；`random` 策略因固定种子 42 而不变 | ✅ 采纳 | `router_service.py`：`baseline_latency(provider_id)` 按 id 派生 20~70ms 确定性伪基线（仅用于打破并列）；`plan()` 未传 `seed` 时改用系统熵随机源（测试显式传 `seed` 保持可复现）。`tests/test_router.py::test_strategies_are_distinguishable_at_cold_start` |
| 6 | 重要 | Turnstile 是死代码：`require_turnstile` 无任何路由 `Depends`；另有 `is_retryable_status` / `constant_time_lookup` / `bump_counter` / `Strategy` 别名未使用 | ✅ 采纳 | `/api/register`、`/api/login`、`/api/recover` 挂 `Depends(require_turnstile)`，并补「开启后未带 token → 401」与「默认关闭放行」两组用例；删除 4 处死代码 |
| 7 | 建议 | 存在接近「假测试」的宽口径断言（video `{422,503}`、vault locked `{409,503}`），且 API 侧压缩接线、code/image 别名、真实模型 id 无用例 | ✅ 采纳 | 3 处宽断言收敛为精确状态码 + `error.code`；新增 API 侧压缩用例（并借此发现并修复 **`PUT /v1/settings` 把裸字符串写进枚举字段、导致 LITE 档被误压缩** 的真实缺陷：`api/proxy.py` 现显式归一化 `CompressionLevel` 并校验策略名）、`inurl-code`/`inurl-image`/真实模型 id 路由用例 |
| 8 | 建议 | 后台八模块与 F-097 不一致；README 自数列了 9 项；`/api/catalog` 回显 `param_all` 致 `?all=1` 非字节级相同（F-077） | ✅ 采纳 | `api/public.py` 去掉 `param_all` 回显；README §4 改为与 `ADMIN_MODULES` 一致的八模块清单并标注端点；新增 **A24** 登记与 F-097 的口径差异及取舍理由 |
| 9 | 建议 | 变更未落库（无提交证据）；`verify()` 每次鉴权都整表重写 `tokens.json`（写放大） | 🟡 部分采纳 | 提交部分：见 §5 原子切片提交（本次完成）。写放大：`token_service.verify()` 的 `last_used_at` 改为 **60s 节流**再写；未做脏标记异步 flush——单机场景下节流已足够，进一步改造属未来优化，不列入本次范围 |

**采纳统计**：采纳 8 条、部分采纳 1 条、驳回 0 条（满足 TR-15.1「≥5 条意见、采纳 ≥2 条」）。

## 4. Rubric 评分

- **TR-15.2（架构分层与职责单一性）：4/5**
  加分：`config/models/crypto/storage/services/providers/api/web/cli` 层次严格；外部 HTTP 调用全部收敛到 `providers/transport.py`（适配器中无 httpx）；`tests/test_audit.py` 静态门禁守护 services↛api/web/cli、models↛services/api；无循环依赖。
  扣分：`web/console.py:20` 反向引用 `api/deps.extract_token`；`api/account.py` 直接读写 `hub._master_keys` 私有属性（绕过 `Hub` 封装）。二者均为已知权衡，未影响行为正确性，故不判阻塞。

- **AC-11（README 完整性）：5/5** —— A1~A24 结构统一，审查抽查的 4 条代码定位均精确可达；审查中发现的「实际行为与文档不符」已全部转为新增假设条目。

## 5. 提交切片（C 阶段）

按 Conventional Commits（中文主体）原子切片，仅包含本应用与相关索引文件：

1. `feat(byok): 新增 BYOK 统一令牌枢纽骨架与配置层`
2. `feat(byok): 实现数据模型与 JSON 文件仓库`
3. `feat(byok): 实现 E2EE 双 escrow 密钥托管`
4. `feat(byok): 实现统一令牌与鉴权错误语义`
5. `feat(byok): 内置厂商目录与目录服务`
6. `feat(byok): 实现别名路由、19 策略与 Combo 分层流转`
7. `feat(byok): 实现 5 档提示词压缩`
8. `feat(byok): 实现三协议厂商适配与故障切换`
9. `feat(byok): 实现健康熔断、用量与套餐计费`
10. `feat(byok): 实现接口层、控制台与 CLI 冒烟`
11. `docs(byok): 补齐 README 假设与差异说明并登记仓库索引`

## 6. 未验证项（明确标注）

- 真实 `serve` 进程下的**跨进程**单实例锁互斥与 Windows 文件锁释放（仅同进程 acquire/release 有测试，跨进程未实测）。
- `/console` 的前端交互（只核对路由与渲染逻辑，未做浏览器操作）。
- `providers/transport.py::HttpxTransport` 的真实网络路径（覆盖率 71%，属不可在 CI 内联网验证的基础设施胶水层；全部业务路径由 `MockTransport` 覆盖）。
- 三协议与真实厂商的联调（原产品未注册、未下载、未运行，知识包亦无实测数据——见 README A3/A21）。
