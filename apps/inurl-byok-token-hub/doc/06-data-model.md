---
id: "inurl-byok-data-model"
title: "数据模型要点"
source: "../README.md"
---
# 数据模型要点

> 内容迁移自根 README §6。模型定义见 `src/inurl_byok_token_hub/models/`。

- `Provider`：`tier(free/paid)` / `public` / `capabilities(text|code|image|video|audio)` / `protocol(openai_compat|anthropic|gemini)`
- `ModelEntry`：`context_window` / `free` / `behind_flagship`（付费卡落后当期旗舰 ≥1 大版本）
- `EscrowRecord`：`escrow_pw` + `escrow_rec` 双份密文 + `generation`
- `VaultKeyRecord`：只含 `CipherBlob`（alg/kdf/iterations/salt/iv/ct），**不含明文**
- `RouteDecision`：候选顺序、跳过原因、最终厂商、每次尝试记录（可审计）
