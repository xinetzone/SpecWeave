---
title: doocs-md-py 上游测试边界映射表
source:
  - d:\AI\.chaos\libs\md\apps\api\src\*.test.ts
  - d:\AI\.chaos\libs\md\apps\api\src\*.ts
---

# 上游测试边界映射表（TR-20.2 / T20）

上游 `apps/api/src` 下共 **13 个 `*.test.ts`（60 条 `it`）**。本文逐条给出「上游断言 → Python 测试」映射；
凡无法 1:1 落地的，登记为差异（D-1..D-4）并说明裁决。Python 侧落点均在 `apps/doocs-md-py/tests/`。

## 1. 映射总表

| 上游测试文件 | 断言组 | it 数 | Python 落点 | 差异 |
|---|---|---|---|---|
| `sync-limits.test.ts` | validatePushPayload / stored document quota / normalizePushDocuments | 18 | `server/test_sync_limits.py`（27） | — |
| `share.test.ts` | share manage authentication / share public routes | 3 | `server/test_share_contract.py`（36） | — |
| `share-sanitize.test.ts` | sanitizeHtmlSnapshot / sanitizeStylesSnapshot / sharePageCspMeta | 4 | `server/test_share_sanitize.py`（12） | — |
| `marketplace.test.ts` | marketplace authentication / public browse | 3 | `server/test_marketplace_contract.py`（20） | — |
| `marketplace-validate.test.ts` | marketplace-admin / validateThemeCss / validatePublishTheme / validatePublishComponent / validateUpdate / bumpMarketplaceVersion | 10 | `server/test_marketplace_validate.py`（19） | — |
| `emojis.test.ts` | emoji manifests / emoji route authentication | 2 | `server/test_emoji_routes.py`（23） | — |
| `emoji-validate.test.ts` | validateEmojiFile / emoji name sanitization | 4 | `server/test_emoji_validate.py`（9） | — |
| `emoji-db.test.ts` | insertUserEmojiItemConditional | 2 | `server/test_emoji_db.py`（9） | — |
| `notifications-db.test.ts` | rowToNotification / notifyUsers + isolation / resolveAdminUserIds | 6 | `server/test_notifications.py`（12）+ `server/test_marketplace_notify.py`（6） | — |
| `origin.test.ts` | isBrowserExtensionOrigin / matchPattern / origin helpers | 9 | `server/test_cors.py`（9）+ `server/test_auth.py`（15） | — |
| `plan.test.ts` | getEffectivePlan / extendPlanExpires / parseGithubLoginFromRemark | 5 | `server/test_plan.py`（6） | — |
| `db.test.ts` | chunkDocumentIds | 2 | `server/test_db_lww.py`（23） | — |
| `uuid.test.ts` | uuidv4 | 2 | — | **D-1** |

## 2. 逐条映射

### 2.1 `sync-limits.test.ts` → `server/test_sync_limits.py`

| 上游 it | Python 测试 |
|---|---|
| accepts a well-formed empty push | `test_empty_push_accepted` |
| accepts valid documents and settings | `test_valid_payload_accepted` |
| rejects oversized document batches | `test_too_many_documents` |
| rejects oversized setting batches | `test_too_many_settings` |
| rejects oversize content | `test_oversize_content` |
| rejects documents whose stored row would exceed the D1 cap | `test_document_row_cap` |
| rejects oversize titles by utf-8 bytes | `test_oversize_title_by_utf8_bytes` |
| rejects malformed documents | `test_malformed_documents` |
| rejects overlong history and history content | `test_history_too_long`、`test_history_content_too_large` |
| rejects invalid settings | `test_invalid_settings` |
| allows updates when already at the cap | `test_quota_allows_updates_at_cap` |
| blocks new active documents past the plan cap | `test_quota_blocks_past_cap` |
| counts resurrected tombstones as new active documents | `test_resurrected_tombstone_counts_as_new_active` |
| counts unknown tombstones toward the row cap | `test_unknown_tombstone_counts_toward_row_cap` |
| strips title, content and history from tombstones | `test_normalize_strips_tombstones` |

Python 额外补充（上游测试未覆盖但代码存在分支）：`test_boolean_is_not_finite_number`、
`test_float_timestamps_accepted`、`test_null_history_accepted`、`test_history_item_must_be_object`、
`test_history_string_datetime_accepted`、`test_null_setting_value_accepted`、`test_payload_too_large_aggregate`、
`test_estimate_row_bytes_non_string_fields_count_zero`、`test_new_counts_zero_never_blocks`、`test_plan_limit_constants`。

### 2.2 `share.test.ts` / `share-sanitize.test.ts` → `server/test_share_contract.py`、`server/test_share_sanitize.py`

| 上游 it | Python 测试 |
|---|---|
| share manage authentication | `test_manage_endpoints_require_auth`、`test_unknown_user_404`、`test_free_user_blocked_from_manage` |
| share public routes | `test_public_wellformed_missing_404`、`test_public_malformed_id_404_text`、`test_public_expired_410_text` |
| returns 404 when a well-formed share id does not exist | `test_public_wellformed_missing_404` |
| strips script tags and event handlers | `test_ts_strips_script_tags_and_event_handlers`、`test_event_handler_quote_variants` |
| strips dangerous tags and javascript urls | `test_ts_strips_dangerous_tags_and_javascript_urls`、`test_vbscript_and_xlink_href_stripped`、`test_dangerous_tag_variants_removed` |
| blocks style breakout and dangerous imports | `test_ts_blocks_style_breakout_and_dangerous_imports`、`test_data_text_html_import_stripped`、`test_safe_css_import_preserved` |
| emits a CSP meta tag without scripts | `test_ts_csp_meta_without_scripts`、`test_csp_constant_complete` |

Python 额外补充：密码模式/cookie/解锁鉴权（`test_unlock_*`、`test_gate_*`、`test_create_*`）、
净化边界（`test_unclosed_script_not_matched_matches_upstream`，与上游正则语义逐字对齐）。

### 2.3 `marketplace.test.ts` / `marketplace-validate.test.ts` → `server/test_marketplace_contract.py`、`server/test_marketplace_validate.py`

| 上游 it | Python 测试 |
|---|---|
| marketplace authentication | `test_manage_endpoints_require_auth`、`test_invalid_token_401` |
| marketplace public browse | `test_empty_catalog_shape`、`test_pagination_param_normalization`、`test_public_list_filters_and_orders`、`test_public_detail_visibility` |
| returns 404 for a missing item | `test_public_detail_visibility`；HTTP 层另见 `test_error_contract.py::test_marketplace_unknown_item_not_found` |
| parses comma-separated admin logins case-insensitively | `server/test_app.py::test_admin_login_case_insensitive` |
| accepts plain css / rejects @import and external url() | `test_theme_css_rules` |
| requires slug, name and css | `test_theme_slug_rules`、`test_theme_name_rules`、`test_theme_success_shape` |
| stores custom sample markdown and treats empty as null | `test_theme_sample_markdown_rules`、`test_parse_sample_markdown_tri_state` |
| requires PascalCase name and safe template | `test_component_name_and_template_rules` |
| rejects empty patch | `test_update_rejects_empty` |
| accepts css update for themes | `test_update_theme_fields` |
| auto-bumps version and ignores client version | `test_bump_version_carry` |
| increments by 0.0.1 with base-10 carry | `test_bump_version_carry` |

Python 额外补充：发布/审批/驳回/安装/下架全链路（`test_publish_*`、`test_approve_flow`、`test_reject_flow`、
`test_install_atomic_count`、`test_delete_by_author`）与通知联动（`test_marketplace_notify.py` 6 例）。

### 2.4 `emojis.test.ts` / `emoji-validate.test.ts` / `emoji-db.test.ts` → `server/test_emoji_*.py`

| 上游 it | Python 测试 |
|---|---|
| builds stable absolute asset URLs and attribution metadata | `test_default_manifest_shape`、`test_get_me_creates_pack_and_manifest` |
| emoji route authentication | `test_auth_required` |
| rejects unsupported types and mismatched magic bytes | `test_rejects_unsupported_mime`、`test_rejects_magic_mismatch` |
| rejects empty and oversized files | `test_rejects_empty_and_oversized` |
| removes paths, extensions, control characters, and excess whitespace | `test_sanitize_name_removes_path_extension_control_and_whitespace` |
| rejects empty pack names | `test_sanitize_pack_name` |
| enforces the item cap in the INSERT statement | `test_item_cap_rejects_101st_and_rolls_back_nothing`；HTTP 层 `test_item_limit_101st_conflict_and_object_rollback` |
| reports a rejected insert at the concurrent quota boundary | 同上（条件 INSERT 的 101 条边界） |

Python 额外补充：四类 magic bytes 接受面、资产缓存头（`immutable` / `max-age=300`）、
删除级联与 502 回滚路径（`test_asset_put_failure_returns_502` 等）。

### 2.5 `notifications-db.test.ts` → `server/test_notifications.py`、`server/test_marketplace_notify.py`

| 上游 it | Python 测试 |
|---|---|
| parses payload and maps snake_case fields | `test_list_desc_order_shape_and_owner_isolation`、`test_payload_fallbacks` |
| tolerates malformed payload JSON | `test_payload_fallbacks` |
| inserts one row per recipient and ignores empty list | `test_marketplace_notify.py::test_publish_notifies_all_registered_admins` |
| markRead and clearAll are scoped to the owner | `test_mark_read_404_for_missing_and_others`、`test_read_all_only_affects_own_unread`、`test_clear_all_only_own` |
| returns only admins that exist in users table | `test_marketplace_notify.py`、`server/test_app.py::test_admin_login_case_insensitive` |
| can exclude a user id | `test_marketplace_notify.py::test_admin_author_gets_self_notification` |

### 2.6 `origin.test.ts` → `server/test_cors.py`、`server/test_auth.py`

| 上游 it | Python 测试 |
|---|---|
| accepts chrome and firefox extension origins | `test_browser_extension_origin_allowed` |
| rejects http origins and empty values | `test_suffix_attack_origin_rejected`、`test_request_without_origin_has_no_cors_headers` |
| matches exact origins | `test_exact_origin_get_echoes_credentials` |
| matches single-label wildcards | `test_wildcard_origin_allowed`、`test_wildcard_does_not_cross_dots` |
| parses allowed patterns | `test_wildcard_origin_allowed` |
| checks whitelist membership | `test_suffix_attack_origin_rejected` |
| picks a non-wildcard default origin | `server/test_auth.py::test_authorize_redirect_and_cookies` |
| resolves redirect URLs against the whitelist | `server/test_auth.py::test_authorize_invalid_redirect_falls_back` |
| returns local md-cli / Vite origins to the same address | `test_localhost_port_wildcard` |

### 2.7 `plan.test.ts` → `server/test_plan.py`

| 上游 it | Python 测试 |
|---|---|
| returns pro only while the expiry is in the future | `test_effective_plan` |
| extends from now when expired or missing | `test_extend_from_now_floor_and_clamp` |
| stacks months onto a still-valid expiry | `test_extend_from_now_floor_and_clamp` |
| parses plain and prefixed usernames | `test_parse_github_login` |
| returns null for empty or invalid remarks | `test_parse_github_login`、`test_login_length_bounds` |

### 2.8 `db.test.ts` → `server/test_db_lww.py`

| 上游 it | Python 测试 |
|---|---|
| keeps each IN chunk within D1's bound-parameter budget | `test_chunk_ids_99_boundary` |
| dedupes ids before chunking | `test_chunk_ids_dedup_preserve_order` |

## 3. 差异登记（TR-20.2「差异说明」）

| 编号 | 上游 | Python | 裁决 |
|---|---|---|---|
| **D-1** | `uuid.test.ts`：自实现 `uuidv4()`，含 `crypto.randomUUID` 不可用时的回退分支 | 直接使用标准库 `uuid.uuid4()`（RFC 4122 v4） | 无需独立 Python 测试：回退分支是 JS 运行时（无 `crypto.randomUUID`）专属问题，Python 标准库不存在该失败面；Python 侧 id 生成的契约由 `test_share_contract.py::test_create_free_success_shape_and_id_derivation`（shareId 派生前 12 hex）间接覆盖 |
| **D-2** | 未命中路由：Hono 未注册 `notFound`/`onError`，返回纯文本 `404 Not Found` | FastAPI 返回 `{"detail": "Not Found"}` | 两侧均非 `{"error": ...}`，不构成契约偏离；已登记白名单（`ERROR_BODY_ALLOWED_KEYS`）并由 `test_error_contract.py::test_framework_unknown_route_body_is_documented_difference` 固化 |
| **D-3** | 上传上限 `UPLOAD_MAX_BYTES` 为 `upload-config.ts:13` 常量（5MiB），非 env 驱动 | `/upload` handler 同用模块常量（`server/upload_config.py: UPLOAD_MAX_BYTES`），行为逐字一致；另存有 Python 独有的 `Config.upload_max_bytes` env 项（**当前 handler 不消费，等价于死配置**） | 契约一致；env 项登记为工程质量待办（T21 文档说明或后续清理），不影响 AC-16 |
| **D-4** | marked（JS）token 模型 | markdown-it-py token 模型（NG6 已声明不承诺字节一致） | 以归一化 DOM 结构/属性/文本等价验收：`tests/golden/test_complex_doc.py`（AC-U1 同维度）；另见 T21 的 `docs/contract-differences.md` |

## 4. 错误体字段一致性全表

cross-cutting 错误体全表落在 `tests/server/test_error_contract.py`（26 例）：逐条断言状态码、
`Content-Type: application/json`、**body 键集合逐字相等**（多键/少键均判违约），
覆盖鉴权 401（`unauthorized`/`invalid_token`）、同步 404/400/413/429、上传 404/503/400/429/502、
分享 403/400/413、市场 404/429、表情 400/404、通知 404，以及框架级 404（D-2）。

## 5. 上游无对应 `*.test.ts` 的 Python 测试（按 TS 源码核对，非测试文件）

`test_upload_api.py`、`test_upload_units.py`、`test_afdian.py`、`test_sigv4_vectors.py`、
`test_share_password.py`、`test_share_page.py`、`test_security.py`、`test_rate_limit.py`、
`test_migrations.py`、`test_app.py`、`test_auth.py`、`test_cors.py`（部分）、
`test_sync_contract.py`、`test_jwt_interop.py`、`test_emoji_s3_storage.py`、
`test_marketplace_notify.py`、`test_domcompare.py` 与 `tests/uploaders/test_uploaders.py`：
这些上游模块没有 `*.test.ts`，Python 测试按 TS 源码逐行核对构造（各文件 docstring 内标注
`upstream: 文件:行号`），构成 AC-U2 抽查的可追溯依据。
