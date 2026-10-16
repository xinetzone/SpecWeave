# 腾讯会议 CLI 知识束 v0.4.0 复核轮·全信源漂移矩阵

- 复核日期：2026-10-15
- 时区口径（R1 落盘评审勘误 P2-1）：采集时间列除 S9 外原始记录取自本机 Windows 北京时钟（UTC+8），初稿曾误加 Z 后缀；正确换算 UTC = 北京时 − 8h，即北京 09:47–09:57 ≈ UTC 01:47–01:57Z。S9（QQ）时间来自服务端 epoch 毫秒，本即为 UTC。npm registry/GitHub API 返回值中的发布时间戳（如 09:17:53.445Z、08:48:38Z）为服务端原生 UTC，不变。
- 复核方法：七概念 R 阶段机械比对（无因果推断；结论仅 `零漂移 / 漂移（引原文） / 不可达` 三类）
- 基线：束 v0.3.0（199 事实，信源抓取于 2026-10-03/04，上游 v1.0.18 @ e631b355）
- 工作副本：`%TEMP%\tmeet-reaudit-20261015\`（5 个 tag 文件哈希留存；不进入版本库）

## 裁决规则

1. **零漂移**：版本面锚点一致且信源正文/元数据锚点全部命中基线事实。
2. **漂移**：任一用户面/命令面/源码面锚点出现双方原文级差异（必须引用双方值）；仅"页面元数据时间变化但正文零变化"记零漂移并说明。
3. **不可达**：通道失败且两轮重试不成 → 维持原事实、登记覆盖缺口（不阻塞裁决，除非版本面不可达）。

## 版本面三证

| ID | 通道 | 采集时间（北京钟/换算UTC） | 基线锚点 | 本次实测 | 结论 |
|----|------|--------------|----------|----------|------|
| V1 npm registry | `npm view @tencentcloud/tmeet version time --json` | 北京 09:47:43（≈01:47:43Z） | latest=1.0.18，末发布 2026-09-11T09:17:53Z | `"version":"1.0.18"`；1.0.18=2026-09-11T09:17:53.445Z；modified=2026-09-11T09:18:10.494Z；1.0.0~1.0.18 共 19 条时间记录无新版 | 零漂移 |
| V2 GitHub 默认分支 | `GET /repos/TencentCloud/tencentmeeting-cli/commits?since=2026-09-11T10:00:00Z` | 北京 09:47（≈01:47Z） | v1.0.18 后无提交 | 响应体 `[]`（空数组） | 零漂移 |
| V3 tag 锚点 | `GET /commits/v1.0.18` | 北京 09:47（≈01:47Z） | commit `e631b355da2b001d24b82f453b65d96f39c59865`（2026-09-11，"chore: Bump v1.0.18 and add event subcommand and fixes"） | sha 逐字符一致；同 message、同日期 2026-09-11T08:48:38Z | 零漂移 |

## 信源逐源比对（10 源）

| ID | 信源/URL | 采集时间（北京钟/换算UTC，S9为原生UTC） | 方法 | 基线锚点 | 本次锚点 | 结论 | 受影响 F |
|----|----------|--------------|------|----------|----------|------|---------|
| S1 product-page | meeting.tencent.com/meeting-cli/index.html | 北京 09:49（≈01:49Z） | WebFetch 全文 | F-002~F-009（slogan、6 Agent、3 场景、8 业务域、5 条 FAQ、安装/授权口径） | slogan「一行指令，让 AI 为你管理腾讯会议」逐字一致；WorkBuddy/DeepSeek Harness/Claude Code/Codex/Cursor/GitHub Copilot 6 名一致；教育培训/销售面客/办公协作 3 场景一致；8 业务域标题逐字一致；5 条 FAQ（定义/Claude Code+Cursor/command not found/跨平台平台/auth login 5 分钟+AES-256-GCM+--no-browser）逐字一致 | 零漂移 | 无 |
| S2 install-guide | cli-install-guide?ch=web | 北京 09:50（≈01:50Z） | WebFetch 全文 | F-012（skill 必需）、F-013（Node>=14）、F-019（重启+auth status）、F-020（一句话 prompt） | 标题《腾讯会议 CLI 安装指南》；`Node.js >= 14` 逐字；两条命令 `npm i -g` + `npx skills add TencentCloud/tencentmeeting-cli -y -g`（标注必需）；第 2 步 tmeet auth login；第 3 步重启 AI 工具 + tmeet auth status；更多帮助两链接（云文档/GitHub）一致 | 零漂移 | 无 |
| S3 github-readme | README.md @v1.0.18（jsDelivr） | 北京 09:54:16（≈01:54:16Z） | curl 下载→SHA256/行数/Grep | F-001/F-003/F-011/F-017/F-018/F-021/F-022/F-024/F-028/F-031/F-033/F-097 | 10523 B / 265 行 / sha256 `ac526a68…344d2`；npm install 命中 1、AES-256-GCM 1、--no-browser 1、TMEET_CLI_CONFIG_DIR 1、make build 1、MIT 4；命令树（行 171-222）auth/meeting/contact/record/report/control/minutes/tshoot/app/event 十域齐（event 子节点 list/schema/consume 可见）；行 238 风险长文（幻觉/提示词注入/投毒/执行偏差）逐字一致 | 零漂移 | 无 |
| S4 command-reference | docs/command.md @v1.0.18 | 北京 09:54:16（≈01:54:16Z） | curl→哈希/行数/Grep | F-033：1594 行、44 子命令、10 域；F-080~F-086 event；F-173 meeting.end | 59259 B / **1594 行精确一致** / sha256 `a82289be…e09d36`；`### ` 域标题 10；event 五子命令 list/schema/consume/status/stop 全命中；app get/set 命中；page-token 29 处；meeting.end 3 处（含行 1472 区域 jq_root_path=.payload、长度恒 1 契约原文）；meeting.started 10 处 | 零漂移 | 无 |
| S5 skill-manifest(a) | skills/tmeet-skill/SKILL.md @v1.0.18 | 北京 09:54:16（≈01:54:16Z） | curl→哈希/行数/Grep | F-023/F-036/F-037/F-062~F-066/F-071~F-078/F-092/F-095：401 行、9 个 `##` | 34265 B / **401 行精确一致** / **9 个 H2 精确一致** / sha256 `63d331e9…27a9182`；meeting_code 5 处、二次确认 7 处、300（秒超时）1 处 | 零漂移 | 无 |
| S6 skill-manifest(b) | CHANGELOG.md @v1.0.18 | 北京 09:54:16（≈01:54:16Z） | curl→哈希/Grep | F-079/F-195：18 个版本条目（v1.0.1~v1.0.18，无 v1.0.0），最新 v1.0.18 2026-09-11 | 95634 B / 512 行 / sha256 `c7654ed1…4ce47ae`；`## ` 版本标题 **18 个精确一致**；前三 = `[v1.0.18] - 2026-09-11`、`[v1.0.17] - 2026-09-09`、`[v1.0.16] - 2026-09-02` | 零漂移 | 无 |
| S7 skill-manifest(c) | package.json @v1.0.18 | 北京 09:53:43 / 09:54:16（≈01:53:43Z / 01:54:16Z） | curl→JSON 解析 + contents API blob sha | F-008/F-014/F-121/F-122：version v1.0.18、bin.tmeet=./scripts/tmeet.js、engines.node>=14、postinstall=node scripts/cleanup.js、files=[scripts/,dist/]、MIT | 438 B / 23 行 / sha256(文件) `7d641d46…2c34ca`；GitHub blob sha `609470997aa1444424d082fda436fd3c42828e94`；6 个字段逐值一致 | 零漂移 | 无 |
| S8 cloud-doc | cloud.tencent.com/document/product/1095/133827 | 北京 09:49（≈01:49Z） | WebFetch 全文 336 行 | 页面时间 2026-07-08；F-004/F-015/F-021/F-025/F-029/F-030/F-034/F-040/F-067/F-093/F-094/F-096 | 页面时间 **2026-07-08 15:50:30 原样**；19 命令分组 3/7/6/2/1 逐表一致（auth 3、meeting 7 含 invitees-list、record 6、report 2、tshoot 1）；Node ≥16 口径；4 条常见报错表逐行；灰度智能表 URL 在位；单账号 logout/login；Keychain/AES-256-GCM；Workbuddy/Qclaw 点名；rule/202603130003 链接；4 高频场景一致 | 零漂移 | 无 |
| S9 user-manual-qqdoc | docs.qq.com/doc/DVUNDV0trdUdqeW5X（dop-api/opendoc） | ≈01:56–01:57Z（原生 UTC；响应 serverTimestamp=01:56:17Z） | v0.2.0 路径复现：浏览器 UA+Referer→JSON→base64→递归 protobuf walker | lastSaveTimestamp=2026-06-25 16:00（北京，分钟级登记）；F-099~F-112 | `lastModifyTime=1782374442912`=2026-06-25T08:00:42.912Z（=北京 16:00:42），与基线分钟级登记（北京 16:00）**分钟级一致**（基线只持久化到分钟，非逐秒比对；R1 P2-2 勘误）；metaCreateTime=1777453837667=2026-04-29T09:10:37.667Z；正文 3649 文本块/66923 字：标题《腾讯会议 CLI使用说明》、"给 AI Agent 的那双手"×1、Workbuddy/Qclaw 各 1、Cursor/Claude Code 各 2、Codex 1、"19 个命令"×1、AES-256-GCM×1、Keychain×2、灰度×1、202603130003×1、tshoot log/waiting-room-log/smart-minutes/transcript/invitees-list 全命中 | 零漂移 | 无 |
| S10 source-code | github.com/.../tree/v1.0.18（固定 tag 源码主体） | 北京 09:47（≈01:47Z） | V3 tag SHA 同一性证明（不可变对象） | F-113~F-199 锚定 commit e631b355…（252/64 Go 文件、38 ApiCmd、8 EventKey 等计数） | tag commit SHA 逐字符一致 → git 对象不可变，F-113~F-199 全部 `文件:行号` 锚点持续有效，无需重数；2026-10-04 本地学习副本已不在本机（不影响：SHA 同一性即充分证据） | 零漂移 | 无 |

## 通道备注（可复现性）

- raw.githubusercontent.com 在本机网络被重置（curl 56 / IWR connection reset），改用 `https://cdn.jsdelivr.net/gh/TencentCloud/tencentmeeting-cli@v1.0.18/<path>` 钉 tag 下载；package.json 另经 GitHub contents API（blob sha `6094709…`）交叉验证，两通道内容一致。
- GitHub 未认证 API 本次共 3 次请求（commits?since、commits/v1.0.18、contents/package.json），远低于 60/h 限额。
- QQ 文档正文不在服务端 HTML，v0.2.0 的 dop-api 路径本轮仍有效；`clientVars.serverTimestamp=1792029377`（2026-10-15T01:56Z）证明响应为实时数据而非缓存。

## 裁决

```
VERDICT=zero-drift
```

- 版本面三证一致（npm/GitHub 分支/tag SHA）；
- 10 个信源全部零漂移（含两个用户面文档页面时间锚点原样、tag 内 5 文件行数/章节/关键锚点逐项命中，其中 command.md 1594 行与 SKILL.md 401 行/9 H2 精确一致）；
- 无不可达源（raw 通道失败已由 jsDelivr + contents API 双替代并交叉验证）。

→ 执行 tasks.md **Task 4a（零漂移最小留痕）**；Task 4b（v0.4.0 增补）不触发，按 spec 已批准的条件条款取消（用户在 Approve 阶段批准互斥路径设计）。

## V 阶段补强与勘误（2026-10-15，fresh-context 审查员独立复跑后）

- **V-2 补强**：新增第 4 项版本面证据 `commits?per_page=1` → 默认分支 HEAD sha 恰为 e631b355，main==tag 由直证成立（原 since 参数较 tag commit 晚 71 分钟的盲区关闭）；tags 列表恰 18 个（v1.0.1~v1.0.18）无新 tag。
- **V-5 勘误**：矩阵 S3 "MIT => 4" 为行级、大小写不敏感、无词边界匹配的粗数，其中 2 处为 `--limit`/`permission-apply-commit` 子串误含；真实 MIT 行为 2 行。meeting_code 为 5 行 6 次、--no-browser 为 1 行 2 次。均为证据表述口径，不影响零漂移结论（文件 SHA256 同一性为强证明）。
- **V-6 口径**：行数为 PowerShell Get-Content 元素数；SKILL.md/CHANGELOG.md 无尾换行，Linux `wc -l` 为 400/511。
- **V-7 行号**：meeting.end 三处为 L1321/L1472/L1478；jq_root_path=.payload 原文在 L1478（非 1472）。
- **V-4 渲染限制**：安装指南为 SPA（原始 HTML 1733B 外壳），F-020 prompt 在该页渲染未直接取到，由产品页同源命中兜底。
- **V-8 命名**：QQ `clientVars.lastModifyTime` 即基线所称 lastSaveTimestamp（同字段异名）；精确换算 1782374442912=2026-06-25T08:00:42.912Z（北京 16:00:42），基线登记为分钟级 16:00，结论表述由"逐秒一致"修正为"分钟级一致"（R1 P2-2）；采集时点由 serverTimestamp=1792029377=2026-10-15T01:56:17Z 锚定（北京 09:56）。
- 审查结论：**V pass（P0=0）**，两项 P1（持久物证内联 log、C 阶段 2 文件白名单机械验收）已全部吸收。
