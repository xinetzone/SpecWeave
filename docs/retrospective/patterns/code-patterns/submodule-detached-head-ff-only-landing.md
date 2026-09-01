---
id: "submodule-detached-head-ff-only-landing"
title: "子模块汇合仓库 detached HEAD 显式落分支法"
type: code-pattern
date: 2026-08-31
maturity: L2 已验证
maturity_note: "三个独立会话案例（yangsheng/fusheng/sexology）均以「提交→检测 detached→ff-only 落分支」闭环（复盘报告 F-022）；其中 sexology 案例全程留痕可查，另两例为二手记录，升级 L3 前建议回查 reflog 直证"
source: ".agents/docs/retrospective/reports/concepts/milestone/retrospective-sexology-classics-wiki-20260830.md"
related_patterns: ["force-push-submodule-commit-recovery.md", "../process-patterns/submodule-ssh-stall-recovery-sop.md"]
tags: ["git", "submodule", "detached-head", "version-control", "ff-only", "workflow"]
validation_count: 3
reuse_count: 0
---

# 子模块汇合仓库 detached HEAD 显式落分支法

## 触发场景

在**汇合型仓库**（多来源内容汇聚的 git submodule，如 awesome-okf-xs 各 bundle 汇合库）中完成 `git commit` 后，提交可能落在 detached HEAD 上——适用于：

- 子模块工作区由检出操作（`git submodule update`、`checkout <hash>`）进入，而非切在分支上
- 在 detached 状态下直接 commit，git 静默成功、无任何警告
- 提交后还需要推送远端或继续迭代，提交必须"进分支"才安全

**不适用**：
- 提交前已确认在分支上（`git status` 无 "HEAD detached" 字样）——无需本模式
- 父提交不属于任何分支 tip 的悬空提交——ff-only 快进不适用，见「待验证问题」情形 B

## 核心做法

### 步骤1：提交后立即检测 HEAD 状态

```bash
git symbolic-ref HEAD
# 分支上: 返回 refs/heads/main，exit 0
# detached: fatal: ref 'HEAD' is not a symbolic ref，exit 非零
```

或看 `git status` 首行是否含 "HEAD detached at <hash>"。**此检查必须在提交后立刻做**——任何后续 checkout/submodule update 都可能移动 HEAD，使找回依赖 reflog。

### 步骤2：判定父提交与分支 tip 的关系

```bash
git rev-parse HEAD            # 当前提交
git rev-parse main            # 目标分支 tip
```

两者相等 → 提交的父提交恰为目标分支 tip，可安全 ff-only 快进（本源案例 sexology 提交 `16d6a514` 的父提交即 main 的 `20649368`）。

### 步骤3：显式落入分支（ff-only）

```bash
git checkout main
git merge --ff-only <commit-hash>
```

`--ff-only` 是关键安全阀：父提交=分支 tip 时快进成功且不产生新提交；若关系判断有误则**拒绝合并**，从机制上杜绝覆盖分支已有提交。

### 步骤4：复核落分支结果

```bash
git symbolic-ref HEAD                 # 期望: refs/heads/<branch>
git branch --contains <commit-hash>   # 期望: 输出包含 <branch>
```

### 步骤5：推送闭环

```bash
git push origin <branch>
git ls-remote origin <branch>         # 期望 == 本地提交
```

推送只认分支引用——detached 上的提交无法推送，这也是本模式的最终验收点。

## 反模式（不要这么做）

### ❌ 反模式1：提交"成功"即当作已进分支
- **错误**：git 在 detached HEAD 下 commit 静默成功、无警告，误以为安全
- **后果**：提交悬空；后续 submodule update/checkout 移动 HEAD 后，提交脱离任何引用，存在被 GC 回收或被分支管理覆盖的风险
- **正确做法**：步骤1提交后立即 `git symbolic-ref HEAD` 检测

### ❌ 反模式2：不合并直接 `git checkout <branch>` 切走
- **错误**：发现 detached 后直接切回分支，未处理刚做的提交
- **后果**：提交留在 detached 悬空态，等于白做
- **正确做法**：切分支后必须 `git merge --ff-only <hash>` 带上提交

### ❌ 反模式3：用 `git reset --hard <hash>` 强移分支
- **错误**：为省事在分支上直接 reset 到 detached 提交
- **后果**：若提交并非分支 tip 的直接后代，reset 会静默丢弃分支上的其他提交
- **正确做法**：统一用 `merge --ff-only`，关系不符即失败可见

### ❌ 反模式4：先做 submodule update / 清理再处置
- **错误**：提交后先继续其他操作（更新子模块、清理工作区），回头再落分支
- **后果**：HEAD 已被移动，找回依赖 reflog（`git reflog`），操作成本与风险陡增
- **正确做法**：落分支是提交后的**第一动作**，之后才继续其他操作

## 检验标准

- [ ] 标准1：`git symbolic-ref HEAD` exit 0，返回目标分支名
- [ ] 标准2：`git branch --contains <commit-hash>` 输出包含目标分支
- [ ] 标准3：`git merge --ff-only` exit 0（或提交时本就在分支上）
- [ ] 标准4：推送后 `git ls-remote origin <branch>` == 本地提交哈希

## 迁移示例

- **场景1（本源案例：汇合型文档仓库）**：多 bundle 汇聚的 OKF 子模块库高频迭代，各会话检出→提交→推送循环，每次提交后走"检测→ff-only→推送"闭环（sexology `16d6a514`、yangsheng、fusheng 三案例）
- **场景2（CI 回写提交）**：`actions/checkout` 默认 detached 检出，构建产物提交版本号后，同样需要落分支（或改用带 token 的分支检出）才能推送
- **场景3（实验性提交）**：checkout 中间提交做热修/试验后决定保留，ff-only 落入当前分支或新分支

## 待验证问题（升级 L3 需确认）

1. **情形 B**（父提交不属于任何分支 tip）的最优处置：新建分支 vs cherry-pick 到目标分支，边界与取舍准则未验证
2. yangsheng/fusheng 两案例的 ff-only 细节来自复盘报告 F-022 二手记录，升级前建议回查两仓库 reflog 直接验证
3. `git submodule update` 对悬空提交的实际威胁路径（引用覆盖 vs GC 回收，`gc.pruneExpire` 默认 2 周）未实测，当前措辞保守为"存在风险"
