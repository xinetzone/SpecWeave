---
type: Pattern
id: "config-cache-separation-backup"
source: "retro-20260901-trae-env（Trae 主目录配置资产二分类）+ Windows 磁盘清理复盘（2026-07-22，cleanup-trae-cache.ps1 双清单策略）"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/config-cache-separation-backup.toml"
maturity: "L2"
validation_count: 2
reuse_count: 0
related_patterns:
  - "credential-copy-minimization"
  - "dual-env-drift-reconciliation"
  - "destruction-protection-isolation"
tags: ["backup", "config-assets", "runtime-cache", "migration", "environment-management"]
---
# 配置缓存分离：环境目录备份迁移的二分类法

## 模式类型

治理策略/环境资产治理模式（配置目录备份与归档场景的二分类口径，属治理流程类）

## 成熟度

L2-validated（2 次验证：①Trae 主目录配置资产二分类 2026-09-01；②Windows 磁盘清理复盘的 safeCleanupTargets/protectedPaths 双清单策略 2026-07-22）

## 触发场景

- 当需要备份/迁移/归档一个「配置目录」，但该目录同时混有可再生运行时产物（会话数据、下载缓存、索引库、内置二进制）时，使用这个模式
- 适用于：IDE/工具配置目录（.vscode、.idea、.npm、conda envs）、应用数据目录、容器工作目录
- 不适用于：①目录内容全部为用户数据无缓存混入；②可再生资产重建成本极高（如构建 20-40 分钟的镜像）——此时应反向操作：主动缓存可再生资产（互补模式，见迁移示例场景3）

## 核心做法

1. **二分类盘点**：将目录内容分为两类——**配置资产**（用户意图的沉淀：手动资产、权限、*-config、偏好/记忆数据）与**可再生缓存**（运行时产物：会话目录、索引库、下载缓存、内置二进制、缩略图）
2. **白名单化**：配置资产列为受保护白名单（备份必含、清理必排除）；可再生缓存标记「可丢弃，按需重建」
3. **备份只含配置**：备份/归档清单只包含配置资产，凭证类按凭证副本最小化模式另行排除
4. **恢复顺序**：迁移时先恢复配置资产，再启动客户端让其按需重建缓存；验证白名单内资产完整、缓存正常再生
5. **口径固化**：将二分类清单固化为文档或脚本（可重复执行的清理/备份脚本），避免每次重新判断

## 反模式（不要这么做）

- ❌ **整目录打包备份**：体积膨胀、恢复慢、过期缓存数据污染新环境（案例①：.trae-cn 混有 work/、design_libraries/、binaries/ 等可再生目录）
- ❌ **把运行时会话目录当配置保留**：会话工作区、缩略图、事件缓存无长期价值，混入备份徒增噪声
- ❌ **清理时无白名单直接删目录**：误删用户配置/聊天记录/状态数据（案例②的反模式表明确记载：必须 protectedPaths 白名单保护）
- ❌ **把"可再生"等同于"无价值"一刀切**：重建昂贵的资产（大镜像、长构建产物）应反向缓存，二分类的判断依据是「重建成本」而非「是否可再生」

## 检验标准

做完之后怎么知道做对了？

- 标准1：目录每个顶层条目都有明确分类（配置资产/可再生缓存），无未分类项
- 标准2：备份包只含配置资产（凭证已按专门模式排除），体积显著小于整目录
- 标准3：恢复后白名单内资产完整可用，缓存由客户端正常重建
- 标准4：二分类口径已固化为可复用文档或脚本，非一次性判断

## 迁移示例

这个模式还能用在什么其他场景？

- 场景1（已验证，磁盘清理方向）：cleanup-trae-cache.ps1——safeCleanupTargets（13 项可再生缓存，标注 "will rebuild"）+ protectedPaths（settings.json/keybindings/snippets/state.vscdb 白名单），安全释放 26GB
- 场景2（非当前领域）：.vscode/.idea 目录迁移、conda envs 与 pip 缓存分离、浏览器 Profile 备份（书签/扩展是配置，Cache/GPUCache 是缓存）
- 场景3（互补方向）：Docker 镜像缓存迁移——镜像可再生但重建昂贵（20-40 分钟），反向操作主动缓存（docker-cache 系列），与本模式构成「重建成本」判断轴的两端

## 案例记录

| 案例 | 日期 | 对象 | 关键发现 |
|---|---|---|---|
| Trae 主目录二分类 | 2026-09-01 | .trae / .trae-cn 主目录 | 配置资产 10 项（skills/permission/memory/mcps/各 config/sandbox.json）vs 可再生缓存 13 项（binaries/builtin/work/worktrees/attachments 等）；产出备份口径文档与恢复顺序 |
| Windows 磁盘清理复盘 | 2026-07-22 | Trae 缓存目录（.ckg 索引 24.81GB） | 双清单策略：safeCleanupTargets 可再生清单 + protectedPaths 配置白名单；安全释放约 26GB，零配置误删 |
