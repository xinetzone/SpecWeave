---
title: "netease-youdao 6 仓库 vendor 子模块迁移基线"
source: "netease-youdao 6 仓库 GitHub 远端（G0 信源稳定性门迁移前于旧临时克隆采集，克隆已按流程清理）"
---

# 迁移基线（SubTask 1.1 采集）

- **采集时间**: 2026-09-09 14:57 (+08:00)
- **采集方式**: `git remote get-url origin` / `git rev-parse HEAD` / `git describe --tags` / `git log -1 --format=%cI` / LICENSE 文件首部识别
- **勘察 spec 基线**: `.trae/specs/okf-wiki-ecosystem/netease-youdao-okf-wiki/spec.md` 信源稳定性门表格（约 2026-09-09 勘察）

## 基线总表

| 仓库 | 远程 URL | 当前分支 | HEAD 完整 hash（实际值=勘察值） | HEAD 最近 tag | tag 指向 commit | 最后提交日期 | LICENSE 文件 | 许可证类型 | 工作树 |
|---|---|---|---|---|---|---|---|---|---|
| BCEmbedding | git@github.com:netease-youdao/BCEmbedding.git | master | `1aa07ea64f94523965c8672e93da47c3faf4d2cd` | 无 | — | 2026-09-03 | LICENSE | Apache-2.0 | clean |
| Confucius4-TTS | git@github.com:netease-youdao/Confucius4-TTS.git | main | `4fb32c481302d8858c3aec6a1c2a8b4cea8894c0` | 无 | — | 2026-09-03 | LICENSE | Apache-2.0 | clean |
| EmotiVoice | git@github.com:netease-youdao/EmotiVoice.git | main | `59f0f36de4db12825f4705dd4e0780d79dd6bb01` | v0.3 | `0ade5e3df226b36da7ecb09485b303580395388c`（HEAD 超前 17 commits） | 2026-09-03 | LICENSE | Apache-2.0 | clean |
| LobsterAI | git@github.com:netease-youdao/LobsterAI.git | main | `7592cd034a7cb458a8650df0325b4980dd1bc162` | 2026.9.4 | `7592cd034a7cb458a8650df0325b4980dd1bc162`（与 HEAD 一致） | 2026-09-04 | LICENSE | MIT | clean |
| QAnything | git@github.com:netease-youdao/QAnything.git | qanything-v2 | `615417a92420d77a2606392a74f5771ca2f31a4b` | v2.0.0 | `f3e96fa41325ea978de6bb3eabbd8d0742f33d0c`（HEAD 超前 69 commits） | 2026-09-03 | LICENSE | AGPL-3.0 | clean |
| ScholarClaw | git@github.com:netease-youdao/ScholarClaw.git | main | `97bdb5e4a763d4f98d4603f5be876587c0871e0f` | 无 | — | 2026-04-03 | LICENSE.txt | MIT | clean |

## 勘察值 vs 实际值对照

| 仓库 | 勘察短 hash（spec） | 实际 HEAD 短 hash | 结论 |
|---|---|---|---|
| BCEmbedding | 1aa07ea | 1aa07ea | 一致 |
| Confucius4-TTS | 4fb32c4 | 4fb32c4 | 一致 |
| EmotiVoice | 59f0f36 | 59f0f36 | 一致 |
| LobsterAI | 7592cd0 | 7592cd0 | 一致 |
| QAnything | 615417a | 615417a | 一致 |
| ScholarClaw | 97bdb5e | 97bdb5e | 一致 |

## 固定方式决策记录

- **勘察 HEAD 与执行时 HEAD 完全一致**，6 仓库均按上表完整 hash 固定（detached HEAD），不浮动分支。
- **EmotiVoice / QAnything 的 HEAD 超前各自最近 tag**（v0.3 +17、v2.0.0 +69）。任务说明中"有 tag 的 checkout tag"与基线 hash 冲突，按 spec「当前基线」列与"以实际 HEAD 为准"原则，**pin 勘察 HEAD commit**，tag 仅作版本描述（`git describe` 形式 `v0.3-17-g59f0f36` / `v2.0.0-69-g615417a`）。R 阶段事实采集以 pin 住的 commit 为准，不触发 spec「tag 选型冲突」改选判据（文档引用集合尚不存在）。
- **LobsterAI**：tag 2026.9.4 恰指向 HEAD，按 tag 固定。
- **QAnything 当前分支为 `qanything-v2`**（非 main/master），.gitmodules 不设置 branch（先例：无 branch 字段 + gitlink pin commit）。
- **无 tag 仓库**（BCEmbedding / Confucius4-TTS / ScholarClaw）：VERSION.md 版本字段标注 `N/A@<hash>`。
