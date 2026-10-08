---
name: wechat-public-okf
description: 将微信公众号、技术博客或公开资讯文章转化为可溯源的 OKF Wiki 教程。用户提到公众号文章、微信文章、公开文章批量整理、文章转 OKF/Wiki、文章方法论萃取或提供 mp.weixin.qq.com URL 并要求提取归纳时使用。强制公开性预检、账号归属核验、R→I→E、F 编号、P0 核验和原创改写；不得绕过登录、验证码、邀请码或复制全文。
---

# WeChat Public Article to OKF

## Why

公开文章的“全部内容”通常既无法证明覆盖完整，也不等于可以复制全文。先登记可访问来源，再把页面事实、作者观点和执行者洞察分开，才能让 OKF 教程可复核、可更新且不把单篇修辞误写成普遍事实。

## Trigger and Inputs

Use this skill for:

- `mp.weixin.qq.com` 或其他公开博客/资讯 URL；
- “公众号文章转 OKF/Wiki”“整理某公众号公开内容”“批量萃取文章方法论”；
- 将一次文章整理流程沉淀成可重复 Skill。

Required input:

1. 账号名或可核验 URL；
2. 内容范围（默认公开可检索文章）；
3. 输出形态（默认原创教程 + 事实索引）。

If account or scope is unclear, pause for confirmation before collecting.

## Public-Only Gate

1. Confirm account name, page ownership signals, source URL, access time and discovery channel.
2. Accept only pages accessible without login, invitation code, CAPTCHA bypass or special permission.
3. On login wall, CAPTCHA, rate-limit loop or repeated failure, stop and record `not-collected` with the reason.
4. Do not infer missing articles from search snippets. “All” means all items discovered and verified through the declared public entry points at the execution time.
5. Do not save article全文, raw HTML dumps, private attachments or restricted content into a public bundle.

## Workflow: R → I → E

### R: Record facts

Create `source-manifest.md` first. Each source needs `source_id`, URL, title, account, date if available, accessibility, ownership evidence and status.

Create `facts.md` with continuous `F-001` identifiers. Use this table:

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|

Allowed `type` values:

- `page_fact`: title, author, date, page structure;
- `author_claim`: advice, causal language, value judgement or interpretation made by the source author.

Do not put the executor's interpretation in `facts.md`.

### P0 verification

Create `verification.md` and check:

- dates and timestamps;
- quantities, percentages, rankings or outcome claims;
- official statements and quoted research;
- claims presented as universal or scientific.

For each item, cite an independent authoritative URL when available. Otherwise use `single-source` or `single-source/flagged`. Never upgrade a source author's claim to a research fact.

### I: Build the knowledge map

Create `knowledge-map.md` with three explicit layers:

1. **Fact layer**: page facts and F mappings.
2. **Mechanism layer**: executor insight, always marked as hypothesis when based on a single source.
3. **Transfer layer**: neutral, reversible practices that respect consent and boundaries.

Every insight must contain the four-tuple: phenomenon, working cause, impact, recommendation.

Ask the reproducibility questions:

1. Is there a defined input, procedure and observable output?
2. Can an independent executor repeat and verify the result?

Create `examples/` only if both answers are yes. Relationship advice, opinion pieces and persuasive essays normally fail this gate.

### E: Extract and generate

Generate an original OKF bundle in this order:

1. bundle `index.md`;
2. `concepts/` tutorial documents;
3. `references/` facts and source index;
4. `examples/` only when approved by the two-question gate;
5. `log.md`;
6. parent index and toctree updates.

Every non-reserved Markdown file needs OKF frontmatter with at least `type`, `title`, `sources`, `status`, `stale_after` and `generated`. Link concrete claims to F identifiers and source IDs. Keep `status: draft` until independent review passes.

## Modes

### Dry-run

Do not write the formal bundle. Produce only:

- account verification result;
- candidate source manifest;
- expected F count and topic map;
- inaccessible/uncertain items;
- planned output paths.

### Normal run

Write the manifest, facts, verification, knowledge map and bundle only after the public-only gate passes.

### 幂等重跑

Read existing manifest, `log.md`, F registry and indexes first. Match by canonical URL and source ID. Update or append facts without renumbering existing F identifiers, do not duplicate index rows, and record the rerun in `log.md`.

## 失败清单

Record every skipped or failed source as `not-collected`, `unverified` or `single-source/flagged`, with the URL, failure signal, retry boundary and next permitted action. Do not replace a failure with guessed content.

## 双方案采集

- **脚本方案**: use a local Playwright/browser script for repeatable runs, dry-run, persisted login state and idempotent manifests.
- **Browser MCP path**: use an integrated browser MCP for interactive, read-only inspection in the IDE when no persisted automation is needed.
- **Parser fallback**: use a permitted URL parser/fetcher only for stable public pages; retain minimal metadata and locators.

Prefer the script path for repeatable or batch collection and the browser MCP path for one-off inspection. Both primary paths must produce the same manifest and fact schema. If paths disagree, mark the source for manual review instead of silently choosing one.

## Safety and Copyright

- Never bypass login, CAPTCHA, invitation codes, robots/access controls or rate limits.
- Never create a full-text mirror or reproduce long verbatim passages.
- Summarize and transform; retain short quotations only when necessary for attribution.
- Do not present relationship tactics as guarantees, psychological laws or consent substitutes.
- Treat personal data, private messages and private notes as out of scope for public bundles.

## Validation Checklist

- [ ] `source-manifest.md` records account, entry point, access time, ownership signal and stopping rules.
- [ ] F identifiers are continuous and the facts/verification sets match exactly.
- [ ] Page facts, author claims and executor insights are separated.
- [ ] P0 claims have independent sources or explicit `single-source/flagged`.
- [ ] No full-text mirror, restricted content or private cache entered the bundle.
- [ ] Every bundle document has valid frontmatter and source IDs.
- [ ] `index.md` toctree, parent index, UTF-8 and bundle counts pass project gates.
- [ ] Dry-run, restricted-content and idempotent-rerun evals pass.

## Output Contract

Return:

1. account/source manifest path;
2. article count and F range;
3. not-collected list with reasons;
4. bundle path and status;
5. validation commands and pass/fail results;
6. known single-source or stale-after limitations.
