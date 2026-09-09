# netease-youdao 子模块分组

本目录为网易有道（netease-youdao）开源生态的 vendor 子模块分组目录，仅承载 git 子模块与元数据，不存放自行修改的源码。

## 元数据

- **名称**：netease-youdao 开源生态（BCEmbedding、Confucius4-TTS、EmotiVoice、LobsterAI、QAnything、ScholarClaw）
- **版本**：固定 commit 检出（BCEmbedding@1aa07ea、Confucius4-TTS@4fb32c4、EmotiVoice@59f0f36、LobsterAI@7592cd0、QAnything@615417a、ScholarClaw@97bdb5e，均为短 hash，完整 hash 见 ../VERSION.md）
- **来源**：git@github.com:netease-youdao/<repo>.git（6 个仓库，均为 third_party）
- **引入日期**：2026-09-09
- **用途**：OKF Wiki 教程（netease-youdao-okf-wiki）的信源稳定性门（G0）——为 R→I→E→V→C 五阶段知识生成提供稳定、可溯源的只读源码信源
- **许可证**：Apache-2.0（BCEmbedding、Confucius4-TTS、EmotiVoice）、MIT（LobsterAI、ScholarClaw）、AGPL-3.0（QAnything），以各仓库 LICENSE 文件为准

## 管理说明

- 6 个仓库均为 **Git 子模块（third_party）**：第三方只读依赖，gitlink 固定 commit，禁止本地修改
- 分组内各子模块的固定 hash、远程 URL 与许可证详情以 [../VERSION.md](../VERSION.md) 为准
- 迁移基线（勘察值 vs 实际值对照）见 `.trae/specs/okf-wiki-ecosystem/netease-youdao-okf-wiki/migration-baseline.md`
