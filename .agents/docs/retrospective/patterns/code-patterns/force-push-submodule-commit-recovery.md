---
id: "force-push-submodule-commit-recovery"
title: "Force-push 剪除子模块提交的 pull 恢复法"
type: code-pattern
date: 2026-08-24
maturity: L1 实验性
maturity_note: "单案例验证（SpecWeave 仓库 git pull 修复），待第二个 force-push+子模块断链场景验证后升级 L2"
source: "2026-08-24 SpecWeave git pull 断链修复会话：origin/main 引用 vendor/flexloop 被 force-push 剪除的 d3cb358，合流后收敛至 7754e53 并推送闭环" 
related_patterns: ["git-bundle-offline-clone.md", "try-prepare-merge.md"]
tags: ["git", "submodule", "force-push", "version-control", "recovery", "gitlink"]
validation_count: 1
reuse_count: 0
---

# Force-push 剪除子模块提交的 pull 恢复法

## 触发场景

- 当你执行 `git pull` 时报 `fatal: git upload-pack: not our ref <hash>` 或 `fatal: remote error: upload-pack: not our ref <hash>`，且提示 `Errors during submodule fetch: <submodule-path>` 时
- 适用于：父仓库（superproject）的 `origin` 分支引用了某个子模块提交，而该提交已在子模块远端被 force-push 剪除；子模块`branch`配置在 `.gitmodules` 的场景
- 不适用于：
  - 子模块 check-out 状态不一致（`+`前缀）但子模块远端提交仍存在——直接用 `git submodule update <path>` 即可，无需本模式
  - 普通（非子模块）仓库的 force-push 覆盖——属于另一类 rebase/reflog 恢复问题

## 核心做法

### 步骤1：定位根因（确认断链）

报错中 `not our ref <hash>` 的 `<hash>` 即父仓库 `origin` 引用的子模块提交。核实它已不存在于子模块远端：

```powershell
# 父仓库 origin 引用的子模块提交
git ls-tree origin/main <submodule-path>          # 例: 160000 commit d3cb358... vendor/flexloop
# 子模块远端真实存在的 main
git -C <submodule-path> ls-remote origin main     # 例: 7754e53... = 该提交仍被剪除的那一个
```
若 `ls-remote` 返回的哈希 ≠ `ls-tree origin/main` 的哈希，则确认是"origin 引用了被剪除的子模块提交"。

### 步骤2：建立安全回滚点

任何写入前先保全现场，杜绝不可逆操作：

```powershell
git branch backup/main-<date>          # 备份当前 HEAD
git stash push -u -m "wip-before-merge"          # 暂存未提交修改（-u 含未跟踪文件）
```

### 步骤3：合流双端历史（merge/rebase）

本地与远端若已分叉，需先合流。**注意**：若双端独立重组了同一批文件，rebase 会在首个提交就遭遇大量结构性冲突——此时立即 `git rebase --abort` 回滚，改走单次三方 `git merge origin/main`（冲突面更集中、可整体权衡）。

### 步骤4：显式收敛 gitlink（关键步骤，最易遗漏）

合并会把 gitlink 解析给"改动方"——即可能把远端侧有缺陷的引用（指向被剪除提交）带回来。**必须显式覆盖为子模块远端真实存在的提交**：

```powershell
git -C <submodule-path> checkout <valid-hash>     # 检出步骤1确认的有效哈希（如 7754e53）
git add <submodule-path>                          # 更新 index 中的 gitlink
git commit -m "chore(submodule): 收敛<submodule>至远端main(<valid-hash>)修复断链"
git ls-tree HEAD <submodule-path>                 # 复核 == <valid-hash>
```

### 步骤5：推送父仓库（真正的闭环）

只本地恢复不够——`origin` 仍挂着对已删除提交的引用，其他协作者与下次 `pull` 仍会失败。**必须把修正后的 gitlink 推回 `origin`**，从源头消除断链（父仓库可 normal push 实现快速前进）：

```powershell
git push origin main
```

### 步骤6：验证闭环

```powershell
git pull                                    # 期望: Already up to date / 成功，exit 0
git submodule status <submodule-path>       # 期望: 无 `+` 前缀（gitlink 与检出一致）
git ls-tree origin/main <submodule-path>    # 期望 == 子模块远端 main 实际哈希
```

---

## 反模式（不要这么做）

### ❌ 反模式1：只本地收敛、不推送 origin
- **错误**：修好本地 gitlink 就结束，不把修正推回远端
- **后果**：`origin` 仍引用已被 force-push 剪除的子模块提交，本地下次 pull、以及其他所有协作者的 pull 依旧报 `not our ref`。修复未形成闭环
- **正确做法**：步骤5必须推送，从远端源头消除对已删除提交的引用

### ❌ 反模式2：合并后不检查 gitlink，直接提交
- **错误**：`git merge` 完成后不核对 `git ls-tree HEAD <submodule>`，直接用合并结果
- **后果**：合并会把 gitlink 交给"改动方"（单侧改动时取改动侧），很可能把远端侧那个指向已删除提交的坏值带回来——断链被原样保留
- **正确做法**：步骤4显式收敛 gitlink 并提交，作为独立修正提交

### ❌ 反模式3：盲启 rebase 遇结构性冲突仍硬解
- **错误**：双端各自重组了同一批文件，rebase 首提交即大量冲突，仍逐个人工强解
- **后果**：22 提交级联冲突，解析极易损坏文档树/误删内容，效率与风险不可控
- **正确做法**：首提交冲突即 `git rebase --abort` 回滚，改走单次三方 `git merge` 整体权衡

### ❌ 反模式4：丢弃含独有内容的本地分支以求对齐
- **错误**：为快速对齐 origin，重置/删除本地领先分支，未先确认本地是否含远端正缺失的独有产出
- **后果**：数据不可逆丢失（本案例本地含 200-perspectives 视角库、codewhale 迁移、1515 篇 learning，远端均无）
- **正确做法**：先备份分支，合流时"保留本地独有 + 吸收远端独有"，二者兼得

---

## 检验标准

做完之后怎么知道做对了？

- [ ] 标准1：`git pull` 成功执行，返回 "Already up to date" 或完成集成，exit code 0
- [ ] 标准2：`git submodule status <submodule-path>` 无 `+` 前缀（gitlink 与检出一致）
- [ ] 标准3：`git ls-tree origin/main <submodule-path>` == 子模块远端 `main` 实际携带的提交
- [ ] 标准4：全树不再存在对被剪除提交的引用（`git grep -l "<deleted-hash>"` 无命中）
- [ ] 标准5：本地领先/落后于 origin 均为 0（`git rev-list --count HEAD..origin/main` 与反向均为 0）
- [ ] 标准6：本地独有产出（如视角文档库、专项迁移）与远端新增内容均在合并后保留

---

## 迁移示例

这个模式还能用在什么场景？

- **场景1（nginx/Docker Registry 镜像引用）**：部署清单引用了一个已被从镜像仓库删除（`docker image rm` / registry GC）的镜像 digest，拉取报错；收敛到现存 digest 并推送新清单
- **场景2（maven/npm lockfile）**：lockfile 锁定了被 `yarn remove`/npm unpublish 的包版本，`CI install` 失败；升级 lockfile 到可解析版本并回传，从源头修复全团队拉取
- **场景3（微服务契约版本）**：服务间通过 API 版本哈希协商，某接口提交被强制回退下线，调用方仍引用旧契约导致 404；统一收敛到存活版本并下发，修复所有下游

---

## 待验证问题（升级 L2 需确认）

1. 子模块远端仅 force-push 了远端提交、但本地仍有该提交对象的特殊场景（对象仍可 fetch）是否应先行尝试 fetch 而非直接收敛？（本案例 `d3cb358` 本地亦无，直接收敛）
2. 本模式适用于 `git pull --recurse-submodules` 与默认 on-demand 两种递归策略的行为差异？
3. 当本地也有独有提交与远端冲突时，"merge 后显式收敛 gitlink" 相比 "rebase 保持 gitlink" 的边界与取舍准则？