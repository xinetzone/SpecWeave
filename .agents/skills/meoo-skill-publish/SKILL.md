---
name: meoo-skill-publish
version: 1.0.0
description: 把本地 Skill 打包为自包含 ZIP 并发布或版本更新到 Meoo 技能市场（meoo.com/skills），含字节级回验。当用户提到"上传技能""发布技能到 Meoo/技能市场""更新技能版本""技能市场上架"或给出 meoo.com/skills 链接要求发布时必须使用。不用于秒悟应用（meoo deploy）部署——那归 meoo-cli。
argument-hint: "<package|publish|update|verify> [技能名或ID]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/meoo-skill-publish/**"
title: "Meoo 技能市场发布 (Meoo Skill Publish)"
x-toml-ref: "../../.meta/toml/.agents/skills/meoo-skill-publish/SKILL.toml"
---
# Meoo 技能市场发布 (Meoo Skill Publish)

## 1. Skill ID
`meoo-skill-publish`

## 2. 功能描述

把工作区里的 Skill 变成**可安装到任意 AI 助手的自包含 ZIP**，发布到 Meoo 技能市场（https://meoo.com/skills），并在发布后做字节级回验。三阶段流水线：

| 阶段 | 动作 | 工具 |
|------|------|------|
| P1 打包 | 自包含合规检查 → 根级 ZIP → base64 载荷 + 逐文件清单 | `scripts/meoo_skill_publish.py package` |
| P2 发布 | 读详情元数据 → 调官方 publish 接口（新建/版本更新统一入口） | 登录态页内 fetch（browser_evaluate） |
| P3 回验 | 下载线上版本 → 逐文件 SHA256 比对 → 零包外引用复扫 | `relay` + `verify` 子命令 |

> **为什么必须三阶段且 P3 不可省？** 平台不回显包内容，"发布成功"只代表服务器收下了文件；选错文件、前端二次打包、传了旧缓存都会静默上线（本流程首战就真实发生过：手动选错 ZIP，线上跑了三天项目耦合版）。逐文件 hash 一致是"线上即所发"的唯一证据。

## 3. 何时使用与边界路由

- 触发："上传/上架/发布/更新技能"、"技能市场"、`meoo.com/skills/<id>` 链接、版本更新/change_note。
- **不归本技能**：`meoo deploy`、Mise、CDN、容器、Sandbox——那是 [meoo-cli](../meoo-cli/SKILL.md) 的应用部署领域。
- **主权区纪律**：发布前若要新建/修改 `.agents/skills/` 下的技能资产本身，先走 [sovereign-rollout-cmd](../sovereign-rollout-cmd/SKILL.md) 提案门；本技能只负责打包与发布，不负责技能资产的治理落盘。
- 成熟度：L1（单技能实战：seven-concepts-cmd 104319，v1 耦合版→v2 独立版，2026-10-18）。第二次独立技能发布后回填 reuse_count 升 L2。

## 4. 前置条件

1. 浏览器已登录 meoo.com（发布依赖会话 Cookie，无 token 替代路线；401/403 时让用户先登录）。
2. 可用浏览器自动化（browser_navigate + browser_evaluate）。
3. Python 3（脚本零第三方依赖，标准库即可）。
4. 暂存目录选在源技能目录之外（推荐仓库 `build/`，已 gitignore；禁止原地打包污染源目录）。

## 5. P1 自包含打包纪律

发布到市场的技能脱离本工作区独立运行，以下每条都是实战拦截过的真实失败：

1. **ZIP 根级必须直接是 `SKILL.md`**（可带 `references/`、`scripts/`、`assets/` 平级条目），禁止外层再套一层同名目录。
2. **`SKILL.md` 必须有 YAML frontmatter**，至少含 `name`、`description`；`name` 与目录名一致。缺头平台报"SKILL.md 格式不正确 需要YAML头信息"。
3. **零包外引用**：全包扫描不得出现 `../`、`file:///` 以及对宿主工作区路径（`.agents/`、`.agents/commands/`、`docs/...`）的运行时依赖；需要的方法论内容必须编入包内 `references/`。frontmatter 的 `paths`、`x-toml-ref` 等工作区专属字段在独立发行版中必须删除。
4. **源目录零改动**：需要改造（如重写独立版 SKILL.md）时，复制到暂存目录再改，源技能目录保持不动。

```bash
python .agents/skills/meoo-skill-publish/scripts/meoo_skill_publish.py package `
  --src <暂存技能目录（内含SKILL.md）> `
  --out build/meoo-skills/<name>.zip          # 加 --strict 则发现包外引用疑似项即失败
# 产物：<name>.zip、<name>.zip.b64（MIME base64）、<name>.zip.manifest.json（逐文件 sha256）
```

Linux/macOS 用行尾续行符 `\`。脚本对 ZIP 条目使用固定时间戳，重复打包字节可复现。

## 6. P2 发布（官方接口，浏览器登录态）

### 6.1 先判定新建还是更新，并取回现网元数据

- 已知技能 ID（更新）：`GET /api/v1/skills/{id}/detail` 返回 JSON。
  注意：直接 `GET /api/v1/skills/{id}` 返回的是技能首页 HTML，不是 JSON，勿用于取元数据。
- 名称占用检查：`GET /api/v1/skills/check-name?skill_name=<name>&exclude_skill_id=<id>`。
- 从 detail 原样取：`skill_name`、`skill_name_for_user`、`description`、`description_for_user`、**tags（标签是 `v2_content_creation` 这类 key，不是页面上的中文标签名；至少 1 个最多 3 个）**、`visibility_scope`、`icon_url`、`market_intro`、`one_sentence_example`。更新时这些字段必须原样回传，缺字段会被清空或报 fieldErrors。

### 6.2 统一发布端点

`POST /api/v1/skills/publish`——新建与更新共用；**请求体带 `skill_id` 即为版本更新**。这是逆向前端 `SkillUploadModal.js` 逐字确认的机制，比网页弹窗可靠：市场上传弹窗是 create 模式，对同名技能硬拦截"标识名已被占用"，无法用于更新。

**发布前预览确认门（dry-run 等价，不可跳过）**：publish 接口没有服务端 dry-run，每次调用都会真实生成新版本，因此 POST 前必须完成本地预检/预览：① package 产物已生成且 WARN 逐项裁决；② 打开 `.zip.manifest.json` 与 P1 暂存目录，向用户展示预览——文件清单、逐文件 hash、ZIP 字节数、skill_id/技能名/visibility_scope/change_note；③ 用户明确确认后才发 POST。禁止在未预览载荷的情况下直接发布。

**幂等性事实**：publish **不是幂等接口**——同一载荷重复 POST 会生成第二个新版本。保护手段是上面的预览门 + POST 前先读 detail 记录当前 latest_version + 成功后立即 P3 回验；已拿到 201 就绝不重试（疑似超时先查 detail/版本列表确认，勿盲目再发）。

启动本地中继把 b64 送进页面、把回流文件接出（仅监听 127.0.0.1）：

```bash
python .agents/skills/meoo-skill-publish/scripts/meoo_skill_publish.py relay `
  --b64 build/meoo-skills/<name>.zip.b64 --received-dir build/meoo-skills/dump --port 8765
```

在任意已登录的 https://meoo.com 页面用 browser_evaluate 执行（第一步启动异步并写 window 变量；**evaluate 不会等待 Promise 返回值**，必须隔 8–15 秒第二步读取）：

```javascript
(async () => {
  try {
    const b64 = (await (await fetch('http://127.0.0.1:8765/payload.b64')).text()).replace(/\s+/g, '');
    const payload = {
      skill_id: "104319",                 // 更新必带；新建省略
      skill_name: "<kebab-name>",
      package_base64: b64,                // 整个 zip 的 base64
      skill_name_for_user: "<市场展示名>",
      description: "<标识名描述，更新时取 detail 原值>",
      description_for_user: "<市场一句话介绍>",
      tags: ["v2_content_creation", "v2_productivity", "v2_development"],
      publish_to_market: true,            // false 等价仅私域保存
      visibility_scope: "public",         // public / private / tenant
      change_note: "<本版本说明>"          // 可选但强烈建议
      // 图标字段：更新且不换图标时整体省略，服务端保留原图标（实证 201）
    };
    const r = await fetch('/api/v1/skills/publish', {
      method: 'POST', credentials: 'include',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    window.__pub = {status: r.status, body: (await r.text()).slice(0, 3000)};
  } catch (e) { window.__pub = {error: String(e && e.stack || e)}; }
})();
```

第二次 evaluate 读 `JSON.stringify(window.__pub)`。成功标志：HTTP **201** 且 body 含 `version`（新版本号）、`version_id`、`market_status`（4=公开上架）。审核通过后 detail 中 `security_review.status = "passed"`。

> **为什么不需要复刻前端的 smartRezip？** 前端发布前会动态 import 重打包模块，但服务端只校验 ZIP 结构与 frontmatter；根级、结构标准的 ZIP 直传实测 201 通过（2026-10-18）。若返回 400 且提示包结构问题，再考虑走官方上传弹窗让前端重打包。

## 7. P3 字节级回验（发布成功不算完）

页内两步法下载新版本并 POST 回中继：

```javascript
(async () => {
  const r = await fetch('/api/v1/skills/104319/download?version=2'); // 用 P2 返回的新版本号
  const u8 = new Uint8Array(await r.arrayBuffer());
  await fetch('http://127.0.0.1:8765/dump?name=online.zip', {method: 'POST', body: u8});
  window.__dl = {status: r.status, bytes: u8.length};
})();
```

本地比对（ZIP 条目集合与逐文件 SHA256 全等，不一致 exit 1）：

```bash
python .agents/skills/meoo-skill-publish/scripts/meoo_skill_publish.py verify `
  --online build/meoo-skills/dump/online.zip --expect build/meoo-skills/<name>.zip
```

再确认三点：① 解压线上包复扫无 `../`、`file:///`、`.agents/` 包外引用；② detail 接口 `latest_version` 已递增、新版本 `is_current_market_version=true`、`security_review` 通过；③ 旧版本仍在版本历史中（平台保留历史，无回滚接口——要回退只能再发布一个新版本）。

收尾：停止 relay 进程；`build/` 下 ZIP/b64/dump 均为 gitignored 中间产物，按需清理；全程不留凭据文件（发布只用浏览器会话 Cookie）。

## 8. API 速查

| 用途 | 方法与路径 |
|------|-----------|
| 详情 JSON（tags 的 key、visibility、icon、版本列表） | GET `/api/v1/skills/{id}/detail` |
| 名称占用 | GET `/api/v1/skills/check-name?skill_name=&exclude_skill_id=` |
| 发布（新建/更新统一入口） | POST `/api/v1/skills/publish`（带 `skill_id` 即版本更新） |
| 下载某版本 | GET `/api/v1/skills/{id}/download?version={n}` |
| 我的技能 | GET `/api/v1/skills/my?page=&size=&keyword=` |

## 9. 安全检查清单

- [ ] 暂存目录在源技能目录之外；发布前后源目录内容 hash 不变
- [ ] 打包输出零包外引用（package 的 WARN 已逐项人工裁决；`--strict` 全绿）
- [ ] tags/名称/描述/visibility 取自 detail 真实回传，未凭记忆编造
- [ ] **发布前预览确认门已执行**（dry-run 等价）：向用户展示 manifest 文件清单/hash/字节数与 skill_id、visibility_scope、change_note，并获明确确认；publish 非幂等，已 201 绝不重试
- [ ] 201 与 body 内新版本号双确认，不把 HTTP 200 单独当成功
- [ ] verify 逐文件 SHA256 全等 + 线上包零包外引用复扫 + detail 版本递增
- [ ] relay 仅绑 127.0.0.1，结束即停；临时 b64/dump 已清理，无凭据落盘

## 10. 错误处理

| 现象 | 处置 |
|------|------|
| 401/403 | 登录态失效，让用户在浏览器登录 meoo.com 后重试 |
| 400 fieldErrors | 原文回报 JSON，按缺失字段补（常见 tags/description）；勿盲目重试 |
| 弹窗提示"标识名已被占用" | 预期行为：那是 create 模式；改走带 skill_id 的 publish 接口 |
| "SKILL.md 格式不正确" | frontmatter 缺失或非法，回 P1 重新打包 |
| REVIEW_QUEUE_FULL | 平台审核队列满，技能被存为非公开；如实报告，不要重复发布 |
| evaluate 返回 undefined | 异步未等待，用 window 变量两步法重读 |
| 页内 fetch 127.0.0.1 被拦（混合内容） | 实测 2026-10-18 可通；若被拦，把 b64 分块直接注入页面再拼合 |

## 11. Gotchas

- **DataTransfer 文件注入在隔离世界常静默失败**（dt.items.add 后 files 仍为空）；必须走弹窗时用 `<script>` 标签注入主世界。但更新场景优先直接调 API，根本不要碰上传弹窗。
- **browser_use 子代理每轮预算有限**（约 10–25 步）：一次只派单一目标（取 detail / 发布 / 回流下载分三次 resume），任务必须收窄。
- **标签是 key 不是中文**：detail 里的 `v2_content_creation` 等才是提交值；页面上的"内容创作"只是 label。
- **PowerShell `Compress-Archive` 压目录会多套一层文件夹名**：一律用 package 子命令（条目相对目录根、正斜杠、固定时间戳可复现）。
- **对话式"改造技能"工作台发送大附件会超时重置回首页**，该路线已证伪，勿再尝试。
- **浏览器截图工具偶发 unavailable** 不影响接口取证；以 JSON 响应与下载文件 hash 为准。

## 12. Changelog

- **v1.0.0** (2026-10-18): 初始版本。萃取自 seven-concepts-cmd 技能 104319 发布实战（v1 项目耦合版 → v1.2.0 独立发行版；逆向前端确认 `POST /api/v1/skills/publish` 带 `skill_id` 即版本更新；HTTP 201，线上包 14970 字节与本地逐文件 SHA256 比对一致；安全审核三项 passed）。
