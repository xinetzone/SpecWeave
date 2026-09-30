---
id: "inurl-byok-assumptions-and-differences"
title: "假设与差异说明（A1–A24）"
source: "../README.md"
---
# 假设与差异说明

> 内容迁移自根 README §8。每条含「默认值 / 溯源 / 风险提示 / 代码定位」。

| # | 假设 | 默认值 | 溯源 | 风险与说明 | 代码定位 |
|---|---|---|---|---|---|
| A1 | 运行环境 | conda `py314`（Python 3.14.3） | 仓库既有 Python 应用惯例 | 本机默认 python 为 3.13.12，须显式走 py314 | [pyproject.toml](../pyproject.toml)：requires-python |
| A2 | 持久化 | JSON 文件仓库 + 可插拔 `Repository` | 文档未指定存储 | 单机场景足够；多实例写入靠单实例锁互斥 | [storage/repository.py](../src/inurl_byok_token_hub/storage/repository.py) |
| A3 | 目录数据 | 内置种子 `data/catalog.json`（46/17/29/10/133） | F-077/F-082/F-090/F-091 | **非实时抓取，不可作为免费政策事实源**（F-079/F-080 已证原站目录陈旧）；具名 8 家标 `doc`，其余标 `seed` | [data/catalog.json](../data/catalog.json)、[services/catalog_service.py](../src/inurl_byok_token_hub/services/catalog_service.py) |
| A4 | AEAD 依赖 | 硬依赖 `cryptography` 46.0.7 | 标准库无 AEAD | 不提供自研 GCM 回退——手写密码学原语是安全反模式 | [crypto.py](../src/inurl_byok_token_hub/crypto.py) |
| A5 | 流式 | `stream=true` 返回 `text/event-stream`：role 首帧 → 内容分帧（24 字符/帧）→ finish 尾帧（附 `_route`）→ `data: [DONE]` | F-027「SSE 透传」（`references/verification.md` 标注「仅文案未登录实测」） | 上游在本实现只返回完整响应，故为**本地降级切分下发**，非真流式透传；未实现 `stream_options.include_usage` 用量帧，首字节后不跨厂商续写 | [api/proxy.py](../src/inurl_byok_token_hub/api/proxy.py)：_sse_stream |
| A6 | 控制台 | 精简 Jinja2 服务端渲染四页 | 文档只描述界面 | 不还原原产品全部交互 | [web/console.py](../src/inurl_byok_token_hub/web/console.py) |
| A7 | 启动器 | 只生成说明，**不下载、不内嵌密钥** | F-053 供应链风险 | 与原产品 `byok-launch` 每次 curl 拉取闭源脚本的行为**相反**，这是本复刻最重要的安全差异 | [cli.py](../src/inurl_byok_token_hub/cli.py)：launcher |
| A8 | 邀请奖励 | 每邀请 1 人 +1 密钥额度，上限 +5 | 文档未给数值 | 可在 `config.yaml` 调整 | [config.yaml](../config.yaml)：invite_bonus_* |
| A9 | 隐藏厂商 | 默认随公开接口下发（保持原产品行为）+ `hide_hidden_providers` 开关 | F-077 | 默认行为会暴露预留/测试厂商，生产建议开启开关 | [config.py](../src/inurl_byok_token_hub/config.py)、[api/public.py](../src/inurl_byok_token_hub/api/public.py) |
| A10 | 主密钥驻留 | 解锁后仅驻留进程内存，重启需重新解锁 | 原产品由启动器内嵌 | 落盘仅密文，进程内明文不写盘 | [services/hub.py](../src/inurl_byok_token_hub/services/hub.py) |
| A11 | 故障切换边界 | 仅 429 与 5xx 切换；400/401/403/404 不切换 | F-048 有证据 | 切换上限、熔断阈值（连续 3 次失败、冷却 30s）属本实现默认 | [config.yaml](../config.yaml)、[services/health_service.py](../src/inurl_byok_token_hub/services/health_service.py) |
| A12 | 19 策略算法 | 名称集合取自界面证据，排序算法为本实现默认 | F-095 | 原产品闭源，不得宣称策略行为等价 | [services/strategies.py](../src/inurl_byok_token_hub/services/strategies.py) |
| A13 | 压缩率 | 5 档规则式实现，返回估算值 | F-095（页面自标「估算值」） | 压缩率属厂商自述，**不作承诺指标**；代码块/链接/JSON 强制原样保留，自检失败则回退原文 | [services/compression_service.py](../src/inurl_byok_token_hub/services/compression_service.py) |
| A14 | 支付 | 仅状态机（创建→凭证→人工核销），无资金流转 | F-097/F-098 | 不接入支付宝，不实现返佣短链 | [services/billing_service.py](../src/inurl_byok_token_hub/services/billing_service.py) |
| A15 | 运营内容 | 示例广告/公告，无埋点、无返佣 | F-084/F-086 风险项 | 不实现 `track.js` 式第一方行为采集 | [services/ops_service.py](../src/inurl_byok_token_hub/services/ops_service.py) |
| A16 | 改密语义 | 重新包裹主密钥（不重加密全部密钥） | F-075「改密重加密」表述模糊 | 更安全且无需恢复密语在场；密钥 `generation` 递增可审计 | [services/vault_service.py](../src/inurl_byok_token_hub/services/vault_service.py) |
| A17 | 监听地址 | 仅回环（127.0.0.1 / ::1 / localhost），配置期即拒绝 | 原产品代理仅本机 | 不提供 `--host 0.0.0.0`，对外暴露需自建受 TLS 的反向代理 | [config.py](../src/inurl_byok_token_hub/config.py)：Settings.__post_init__ |
| A18 | video/audio | 明确返回「当前没有支持该类别的厂商」 | F-082 | 目录无对应能力厂商，不伪装支持 | [services/catalog_service.py](../src/inurl_byok_token_hub/services/catalog_service.py)：by_capability |
| A19 | 未知请求字段 | 非白名单键（`model`/`messages`/`stream`/`temperature`/`max_tokens` 之外）进 `ChatRequest.extra`：OpenAI 兼容原样透传，Anthropic/Gemini 显式 422 `unsupported_feature` | 「无法映射的字段不得静默丢弃」契约 | 严格策略会让携带 `tools`/`top_p` 的客户端在 Anthropic/Gemini 上直接 422，这是刻意取舍而非缺陷 | [api/proxy.py](../src/inurl_byok_token_hub/api/proxy.py)：_CHAT_KNOWN_KEYS |
| A20 | 厂商线协议来源 | 密钥记录协议 = 显式指定 > 目录厂商协议 > `openai_compat` 兜底 | F-047 三协议 | 若沿用默认兜底，目录内的 Anthropic/Gemini 厂商将永远走不到各自适配器 | [services/vault_service.py](../src/inurl_byok_token_hub/services/vault_service.py)：_resolve_protocol |
| A21 | 双 escrow 归属 | **服务端代生成**主密钥；`POST /api/escrow` 接管客户端生成的 escrow 时必须同传 `password`，服务端据此解出新主密钥并重写全部密钥密文 | F-052（原产品为浏览器端 E2EE，主密钥不出浏览器） | 与原产品相反：本地代理转发需要明文 Key，服务端必须能解出主密钥；缺少 `password` 时明确 400，不谎报 `stored` | [api/account.py](../src/inurl_byok_token_hub/api/account.py)：post_escrow、[services/vault_service.py](../src/inurl_byok_token_hub/services/vault_service.py)：adopt_client_escrow |
| A22 | 管理员令牌文件 | 运行期 `{data_dir}/admin.token` 为**明文**令牌（权限 0600 + 启动告警），库内仍只存摘要 | 便于 CLI/演示直接读取 | 拿到该文件即等同管理员权限；生产部署应删除该文件并改走 `/api/login` | [services/hub.py](../src/inurl_byok_token_hub/services/hub.py)：ensure_admin |
| A23 | 路由运行期状态 | Combo 每层产出独立候选序列（本层耗尽流转下一层）；轮询游标按用户驻留内存（重启归零）；无健康样本时按厂商 id 派生 20~70ms 稳定伪基线延迟 | F-095「Combo（`>` 分层流转）」 | 伪基线仅用于打破并列，不代表真实延迟；进程重启后轮询回到起点 | [services/router_service.py](../src/inurl_byok_token_hub/services/router_service.py)、[services/chat_service.py](../src/inurl_byok_token_hub/services/chat_service.py) |
| A24 | 后台模块口径 | 八模块按 spec FR-10 重新枚举（用户/目录/套餐订单/核销/用量/内容/配置/审计） | F-097 的枚举含 Turnstile 配置、邀请码、官网链接、catalog-overrides | 与 F-097 **不一致**：本复刻按可实施性取舍，四项未单列（Turnstile 走 `config`，邀请码走注册参数） | [services/ops_service.py](../src/inurl_byok_token_hub/services/ops_service.py)：ADMIN_MODULES |
