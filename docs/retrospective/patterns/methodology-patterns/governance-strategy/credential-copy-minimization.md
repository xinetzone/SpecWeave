---
type: Pattern
id: "credential-copy-minimization"
source: "retro-20260901-trae-env（Trae 目录镜像中 JWT token 第二副本）+ 敏感信息治理复盘（2026-07-08）+ tao-ai-knowledge 密钥泄露复盘（2026-08-07）"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/credential-copy-minimization.toml"
maturity: "L2"
validation_count: 3
reuse_count: 0
related_patterns:
  - "ledger-stock-consistency-audit"
  - "destruction-protection-isolation"
  - "gitignore-validation"
tags: ["credential", "backup-safety", "mirror", "gitignore", "security-governance"]
---
# 凭证副本最小化：目录镜像/备份/同步中的凭证防护法

## 模式类型

治理策略/安全治理模式（配置目录镜像与备份场景的凭证扩散防护，属安全流程类）

## 成熟度

L2-validated（3 次验证：①Trae 目录镜像 JWT token 副本治理 2026-09-01；②敏感信息治理复盘中文件名级凭证忽略规则落地 2026-07-08；③tao-ai-knowledge Supabase 密钥泄露反面案例 2026-08-07）

## 触发场景

- 当对用户主目录/配置目录做镜像、备份、同步（归档快照、dotfiles 仓库、云同步盘、分析用副本），且源目录含明文凭证文件时，使用这个模式
- 适用于：凭证以明文文件形式存在（*-token、*.key、*.pem、credentials*、.env）、副本将进入版本控制或他人可访问位置的场景
- 不适用于：①凭证已由密钥管理服务托管且本地无明文文件；②副本全程留在加密卷内且不离开本机（此时加密即可，无需排除）

## 核心做法

1. **凭证清单化**：先枚举源目录中的凭证类文件（`*-token`、`*.key`、`*.pem`、`credentials*`、`.env`），建立凭证清单
2. **镜像前过滤**：同步/镜像时排除凭证文件，或用占位符替代；分析类副本只保留结构不保留凭证
3. **双层忽略规则**：版本控制忽略文件中，目录级规则 + 文件名级通配兜底（如 `**/trae-jwt-token`、`credentials.json`）并存，不依赖单一目录级规则
4. **用后即清**：分析类镜像使用完毕后删除凭证副本；确需保留的显式登记理由
5. **分享前扫描**：任何归档/分享/提交操作前执行凭证扫描（文件名模式 + 内容关键字 + `git ls-files` 跟踪检查）

## 反模式（不要这么做）

- ❌ **整目录无差别镜像**：凭证随副本扩散到第二处位置，泄露面随副本数量线性增长（案例①：token 出现在仓库路径下）
- ❌ **只靠目录级忽略规则兜底**：目录结构调整或副本移到别处后规则失效，文件名级通配才是最后防线（案例②的教训：凭证规则必须落到文件名模式）
- ❌ **在报告/日志/示例文件中记录凭证值"以便核对"**：真实凭据一旦进入文档即构成泄露（案例③：真实 Supabase key 写进 `.env.example`，本应是占位符）
- ❌ **泄露后只删文件不轮换密钥**：凭证已进入历史/副本，删除不等于消除，必须轮换

## 检验标准

做完之后怎么知道做对了？

- 标准1：`git check-ignore` 对每个凭证文件路径返回规则命中（双层规则均验证）
- 标准2：`git ls-files` 无任何凭证条目（历史未跟踪）
- 标准3：全仓/全副本扫描无主位置之外的失控凭证副本（或已登记保留理由）
- 标准4：报告、日志、示例文件中 grep 不到任何真实凭据值

## 迁移示例

这个模式还能用在什么其他场景？

- 场景1（已验证，仓库治理）：`.gitignore` 凭证规则体系——目录级 `external/` + 文件名级 `**/trae-jwt-token`/`credentials.json` 双层防护
- 场景2（非当前领域）：`.ssh`、`.aws`、`.docker/config.json` 目录的备份——同样先凭证清单化再排除
- 场景3（跨领域）：云同步盘（网盘同步工作目录）、虚拟机快照导出、容器镜像打包——凡"整目录复制"动作都先过凭证过滤

## 案例记录

| 案例 | 日期 | 场景 | 关键发现 |
|---|---|---|---|
| Trae 目录镜像凭证治理 | 2026-09-01 | 配置目录镜像含 JWT token | token 随镜像出现第二副本；补 `**/trae-jwt-token` 文件名级兜底，验证 `git check-ignore` 命中、历史未跟踪 |
| 敏感信息治理复盘 | 2026-07-08 | 仓库凭证忽略规则建设 | 落地文件名级规则（credentials.json、service-account*.json、*.pem 等）+ pre-commit 检测钩子 |
| tao-ai-knowledge 密钥泄露 | 2026-08-07 | 真实凭据写入示例文件 | Supabase service role key 硬编码进 `.env.example`；整改：轮换密钥+改占位符+凭证扫描门禁 |
