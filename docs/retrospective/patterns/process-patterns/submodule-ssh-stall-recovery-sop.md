---
id: "submodule-ssh-stall-recovery-sop"
title: "子模块 SSH 停滞换源恢复 SOP"
type: process
date: 2026-08-29
maturity: L2 已验证
maturity_note: "2 个独立故障子模块同法恢复成功（caffe 预置 HTTPS URL、veadk-python 环境变量 insteadOf），另含 1 个超级工程 pull 后 pin 漂移收敛案例；待跨项目/非 GitHub 主机场景验证后升级 L3"
source: "2026-08-29 SpecWeave 七概念问题解决会话（sc-20260829-submodule-caffe）：git submodule update --init --recursive 因 caffe/veadk-python 双故障子模块失败，F→V→C→R→I→E 全链路闭环"
related_patterns: ["force-push-submodule-commit-recovery.md", "git-bundle-offline-clone.md", "vhdx-two-phase-recovery-sop.md", "pre-kill-identity-verification.md"]
tags: ["git", "submodule", "ssh", "https", "insteadOf", "recovery", "windows", "network", "sop"]
validation_count: 2
reuse_count: 0
---

# 子模块 SSH 停滞换源恢复 SOP

## 模式概述

`git submodule update --init --recursive`（或任何声明式递归 Git 操作）在某子模块上**反复失败或长时间停滞**，根因常为两类叠加：

1. **传输通道停滞**：SSH 通道握手/认证成功，但大对象传输阶段速率趋零挂死（同一仓库 HTTPS 匿名通道稳定）；
2. **中断残骸非幂等**：被杀死的克隆留下"半出生" gitdir（空 `objects/pack`、无 remote、未出生 HEAD），而 `update --init` 见到 gitdir 即跳过克隆，导致重跑确定性失败（典型报错 `fatal: Unable to find current revision in submodule path '<name>'`）。

本模式的恢复协议：**换通道（不改仓库声明）→ 清残骸（恢复幂等）→ 受控重跑（可观测）→ 原命令端到端验收**。核心手段是用 `GIT_CONFIG_*` 环境变量注入 `url.<https>.insteadOf=<ssh>` 重写，经子进程继承覆盖**整棵递归树所有嵌套层级**，且不写任何持久配置。

## 触发场景

- 当 `git submodule update --init --recursive` 报 `Unable to find current revision in submodule path ...` / `Failed to recurse into submodule path ...`，或某子模块克隆阶段停滞 10 分钟以上无进度时
- 适用于：`.gitmodules` 记录 SSH URL（`git@host:org/repo.git`）、本机 SSH 大传输不稳定但 HTTPS 可达的环境；Windows 与类 Unix 均适用（命令以 PowerShell 为主，附 POSIX 等价）
- 不适用于：
  - 目标仓库仅在内网 SSH 可达、HTTPS 匿名/凭证均不可达——换源不成立，应修网络/SSH 配置，或改用 [Git Bundle 离线克隆五步法](../code-patterns/git-bundle-offline-clone.md)
  - 故障是 gitlink 指向已被 force-push 剪除、任何远端都不存在的提交——属 [Force-push 剪除子模块提交的 pull 恢复法](../code-patterns/force-push-submodule-commit-recovery.md) 域
  - 子模块工作区有未提交改动——先处理改动，禁止直接 checkout 收敛

## 一、前置条件

- 对超级工程仓库有本地读写权限（仅改 `.git/` 元数据与子模块工作区检出，**不改 `.gitmodules`、不提交任何变更**）
- 能枚举本机进程树（Windows: `Get-CimInstance Win32_Process`；POSIX: `ps -ef`/`pstree`）
- 已确认故障子模块的 HTTPS 匿名可达：

```powershell
git ls-remote https://github.com/<org>/<repo>.git HEAD
```

## 二、快速开始（核心六步）

```powershell
# ① 环境变量换源：git@github.com: → https://github.com/（整棵递归树继承，零持久改动）
$env:GIT_CONFIG_COUNT='1'
$env:GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf'
$env:GIT_CONFIG_VALUE_0='git@github.com:'

# ② 受控重跑（后台 + 进度日志，便于轮询）
git submodule update --init --recursive --progress 2>&1 |
  Out-File -Encoding utf8 .temp/submodule-update-$(Get-Date -Format yyyyMMdd).log

# ③ 完成后：纯净环境（新开终端或清除变量）重跑原命令验收
git submodule update --init --recursive   # 期望：无输出（全 no-op），退出码 0

# ④ 全树状态零脏标记
git submodule status --recursive          # 期望：每行前缀为空格，无 + - U
```

POSIX（bash/zsh）等价：

```bash
GIT_CONFIG_COUNT=1 \
GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf' \
GIT_CONFIG_VALUE_0='git@github.com:' \
git submodule update --init --recursive --progress
```

> 需要凭证的私有仓库：把 HTTPS URL 换成带 token 的形式（如 `https://<token>@github.com/`）或先配置 credential helper；主机非 GitHub 时改写规则相应替换（如 `git@gitlab.com:` → `https://gitlab.com/`）。

## 三、详细步骤

### 步骤 1：确诊"停滞"而非"失败"，并对比双通道

```powershell
# 1a. 找到停滞的更新进程树（记录 PID，勿杀终端 shell 本体）
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'submodule|git-remote|ssh|index-pack' } |
  Select-Object ProcessId, ParentProcessId, Name,
    @{n='CMD';e={$_.CommandLine.Substring(0,[Math]::Min(120,$_.CommandLine.Length))}}

# 1b. 看传输是否真的在推进：读 --progress 日志的 MiB 数（不要看 tmp_pack 文件尺寸，见反模式 4）
Get-Content .temp/submodule-update-*.log -Tail 5

# 1c. 双通道对比：SSH 挂死 vs HTTPS 可达即确诊
git ls-remote git@github.com:<org>/<repo>.git HEAD   # 慢/超时
git ls-remote https://github.com/<org>/<repo>.git HEAD  # 秒回 commit SHA
```

### 步骤 2：终止停滞/竞争传输（只杀子树，保终端）

- IDE、codex、其他终端会**反复自动发起**同一子模块的 fetch，与受控更新争抢带宽；处置 SOP 同 [pre-kill-identity-verification](../code-patterns/pre-kill-identity-verification.md)：枚举父 PID 链确认归属后，只杀 `ssh`/`git-remote-*`/`index-pack`/`fetch` 子树，**保留用户终端 shell 主进程**。
- 杀死后重新枚举确认竞争树已消失。

### 步骤 3：残骸双清（恢复克隆幂等）

中断的克隆会在两处留下残骸，**两处都要清**：

```powershell
# 3a. 子模块 gitdir（关键！update --init 见它存在就跳过克隆）
Remove-Item -Recurse -Force .git/modules/<submodule-path> -ErrorAction SilentlyContinue
# 嵌套子模块路径形如：.git/modules/projects/xuanspace/modules/vendor/caffe

# 3b. 工作区残留目录（内容为空或只有 .git 指针文件）
Remove-Item -Recurse -Force <submodule-path> -ErrorAction SilentlyContinue
```

- Windows 上若工作区空目录报 `being used by another process`：多为某 shell 的 CWD 句柄锁定——**空目录可直接作为 clone 目标，无需删除**，只清 gitdir 即可。
- 清理后顺手删除同目录下遗留的 `objects/pack/tmp_pack_*` 大文件（被杀传输的孤儿包，可达上百 MB）。

### 步骤 4：环境变量换源 + 受控重跑

- 用"快速开始"中的 `GIT_CONFIG_COUNT/KEY_0/VALUE_0` 三元组注入 insteadOf。
- **为什么必须用环境变量而不是 `git -c`**：`-c` 只作用于顶层 git 进程；递归子模块由子进程执行克隆，不继承命令行 `-c`；而环境变量经进程环境被整棵树继承。命令行日志中仍显示原始 SSH URL 是正常现象——以传输子进程名为准（应出现 `git-remote-https` 而非 `ssh`）。
- 后台运行并重定向 `--progress` 输出到 `.temp/` 日志，每 2-5 分钟轮询日志尾部的 `Receiving objects: xx% (n/N), xx MiB`。

### 步骤 5：端到端验收（不可跳过）

1. **纯净重跑原命令**：新开终端（或 `Remove-Item Env:GIT_CONFIG_*`）后执行 `git submodule update --init --recursive`，要求**退出码 0**（已全部就位时无输出=全 no-op）。
2. **全树状态零脏标记**：

```powershell
git submodule status --recursive | Where-Object { $_ -match '^[+\-U]' }
# 期望：无输出。+ = 检出与超级工程 gitlink 不一致；- = 未初始化；U = 冲突
```

3. **关键 SHA 比对**：故障子模块 `git -C <path> rev-parse HEAD` 必须等于超级工程记录的 gitlink（`git ls-tree HEAD <path>`）。

### 步骤 6：pin 漂移收敛（超级工程被 pull/切换后）

若验收时出现 `+` 且根仓库 reflog 显示近期有 `pull: Fast-forward`/checkout（自动化代理常做此事）：超级工程更新 gitlink 后**不会自动同步子模块工作区**。此时直接再跑一次原命令即可收敛到当前 pin（目标对象通常已在本地，无需网络）：

```powershell
git reflog -5                       # 确认是否有外部 pull
git submodule update --init --recursive   # 输出 Submodule path '...': checked out '<pin>'
```

## 反模式（不要这么做）

- ❌ **反复重跑原命令碰运气**：半出生 gitdir 存在时 `update --init` 跳过克隆，失败是确定性的；不做残骸双清，重跑一百次也一样。
- ❌ **只清一处残骸**：只删工作区目录不删 `.git/modules/<name>`（或反之），克隆仍不会重新发生；两处必须双清。
- ❌ **用 `git -c url...insteadOf=...` 顶层注入**：`-c` 不随递归子进程继承，嵌套层子模块仍走 SSH 停滞通道；必须用 `GIT_CONFIG_*` 环境变量（或修改 `.git/modules/<name>/config` 里的 url，但那是持久改动）。
- ❌ **以 tmp_pack 文件尺寸判断停滞**：Windows 活动 index-pack 期间目录项尺寸严重滞后少报（实测日志已接收 144 MiB 时 tmp_pack 一度报 0 字节）；判据只能是 `--progress` 日志的 MiB 增长与最终 pack 安装。据此误杀健康克隆会制造新残骸。
- ❌ **手动 `git checkout <SHA>` 拼凑后宣布完成**：跳过端到端回归会漏掉其他未初始化的同病子模块——本模式第二个故障子模块（veadk-python）正是被"原命令必须退出码 0"的回归验收逼出来的。
- ❌ **杀传输进程时连带终端 shell / IDE 主进程**：会丢失用户会话，且 shell 的 CWD 句柄会锁住子模块目录导致残骸清不掉。
- ❌ **把 insteadOf 写进仓库级配置或提交 `.gitmodules` 改动**：污染团队共享声明；环境变量方案零持久改动，任务结束即失效。

## 检验标准

- 原命令 `git submodule update --init --recursive` 在**无环境变量**的纯净终端中退出码 0
- `git submodule status --recursive` 输出无任何 `+`/`-`/`U` 前缀
- 每个曾故障的子模块：`rev-parse HEAD` == 超级工程 gitlink SHA，且工作区文件数正常
- 重跑期间的传输子进程为 `git-remote-https`（进程树可证）
- `.git/modules/**/objects/pack/` 下无遗留 `tmp_pack_*` 孤儿文件
- 未修改 `.gitmodules`、未产生任何待提交变更（`git status --short` 无子模块相关条目）

## 迁移示例

- **场景 1（跨工具链，npm/pnpm/yarn）**：`package.json` 中 `git+ssh://git@github.com/...` 依赖在安装时停滞，同样用 `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:` 包裹包管理器命令（Git 子进程继承环境变量），无需改依赖声明。
- **场景 2（CI/CD）**：runner 上不便配置 SSH key 时，用环境变量注入 `https://<deploy-token>@host/` 的 insteadOf 完成子模块初始化，凭证不落盘、不进 `.gitmodules`。
- **场景 3（非 Git 领域，同构恢复）**：大文件下载工具断流后"删临时分片 → 换镜像源 → 断点/全量重跑 → 哈希校验"的恢复流程，与本模式"清残骸 → 换通道 → 受控重跑 → 端到端校验"同构；判据同样是"看进度日志而非临时文件大小"。

## 关联文档

- [Force-push 剪除子模块提交的 pull 恢复法](../code-patterns/force-push-submodule-commit-recovery.md)：gitlink 引用对象在远端已不存在时的恢复（本模式的边界外场景）
- [Git Bundle 离线克隆五步法](../code-patterns/git-bundle-offline-clone.md)：HTTPS/SSH 均不可达时的离线交付通道
- [VHDX 二相回收 SOP](vhdx-two-phase-recovery-sop.md)：同类型"诊断→清残骸→验收"Windows 运维 SOP，孤儿临时文件清理思路互通
- [pre-kill-identity-verification](../code-patterns/pre-kill-identity-verification.md)：杀进程前的身份核验纪律
