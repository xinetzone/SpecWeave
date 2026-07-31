---
title: Git 百度网盘同步 - 故障排查手册
version: 1.0.0
created: 2026-07-31
updated: 2026-07-31
source: original
---

# Git 百度网盘同步 - 故障排查手册

## 快速诊断流程图

```mermaid
flowchart TD
    Start([遇到问题]) --> First[第一步: 运行 git-diag 一键诊断]
    First --> DiagOK{诊断结果?}
    
    DiagOK -->|无错误| Normal[操作正常，可能是使用问题]
    DiagOK -->|有警告/错误| FollowDiag[按诊断建议修复]
    
    Start --> Symptom{问题类型?}
    
    %% 同步卡住类
    Symptom -->|同步卡住/等待| Stuck[同步卡住类]
    Stuck --> Stuck1{是否显示等待网盘同步?}
    Stuck1 -->|是| CheckNet[检查网盘客户端是否运行/网络]
    Stuck1 -->|否| CheckLock[检查锁状态: lock-check]
    
    %% Push被拒类
    Symptom -->|Push被拒| PushRej[Push被拒类]
    PushRej --> PushErr{错误类型?}
    PushErr -->|non-fast-forward| NeedPull[先pull再push]
    PushErr -->|lock is held| WaitLock[等待锁释放/超时后force-unlock]
    PushErr -->|Could not read remote| CheckPath[检查remote路径是否正确]
    PushErr -->|pre-receive hook| BareCorrupt[裸仓库损坏，从备份恢复]
    
    %% Pull失败类
    Symptom -->|Pull失败| PullFail[Pull失败类]
    PullFail --> PullErr{错误类型?}
    PullErr -->|unrelated histories| AllowUnrelated[添加 --allow-unrelated-histories]
    PullErr -->|local changes overwritten| Stash[git stash暂存后pull]
    PullErr -->|文件显示修改但实际没有| CheckCRLF[检查core.autocrlf配置]
    PullErr -->|中文乱码| CheckEncoding[检查git编码配置]
    
    %% 仓库损坏类
    Symptom -->|仓库损坏/冲突文件| Corrupt[仓库损坏类]
    Corrupt --> FsckErr{git fsck报错?}
    FsckErr -->|是| Severe[严重！从备份恢复]
    FsckErr -->|否| HasConflict{有 (1) 或冲突版本文件?}
    HasConflict -->|是| ConflictLoc{冲突位置?}
    ConflictLoc -->|objects/pack/或HEAD| Severe
    ConflictLoc -->|refs/或其他| ManualResolve[人工检查处理]
    
    %% 跨平台类
    Symptom -->|跨平台问题| CrossPlat[跨平台类]
    CrossPlat --> Perm{权限/换行符/大小写?}
    Perm -->|shell脚本权限| FileMode[设置core.filemode=false]
    Perm -->|大小写冲突| Rename[重命名文件]
    Perm -->|符号链接变文件| Symlink[检查core.symlinks配置]
    
    %% 日常使用类
    Symptom -->|日常使用问题| Daily[日常使用类]
    Daily --> DailyQ{具体问题?}
    DailyQ -->|设备未push导致分叉| Rebase[rebase或merge解决分叉]
    DailyQ -->|误force-push| Restore[从备份/reflog恢复]
    DailyQ -->|新设备开始| CloneNew[用clone-repo脚本克隆]
    DailyQ -->|归档仓库| Archive[打包备份后删除remote]
    
    Severe --> STOP[⚠️ 立即停止所有操作！]
    STOP --> RecoverBackup[从最近的.bundle备份恢复]
    
    CheckNet --> WaitSync[等待网盘同步完成]
    CheckLock --> LockHolder{锁持有者?}
    LockHolder -->|本设备残留锁| AutoClean[自动清理]
    LockHolder -->|其他设备且超时| ForceUnlock[确认后force-unlock]
    LockHolder -->|其他设备且未超时| WaitDevice[联系持有者等待]
    
    classDef severe fill:#ff4444,stroke:#cc0000,color:white
    classDef warn fill:#ffaa00,stroke:#cc8800
    classDef ok fill:#44aa44,stroke:#228822,color:white
    class Severe,STOP severe
    class NeedPull,WaitLock,CheckPath,AllowUnrelated,Stash,CheckCRLF,CheckEncoding,ManualResolve,FileMode,Rename,Symlink,Rebase,Restore,CloneNew,Archive,WaitSync,AutoClean,WaitDevice warn
    class FollowDiag,Normal ok
```

## 紧急联系/求助时机

### 🛑 必须立即停手的情况（严重级别）
出现以下任何一种情况，**请停止所有Git操作**，不要尝试自行修复：
1. `git fsck --full` 报告 `error: corrupt loose object`、`missing blob`、`broken link` 等错误
2. `git status` 报告 `fatal: bad object HEAD` 或 `fatal: Not a valid object name HEAD`
3. 网盘裸仓库目录（`repos/<repo>.git/objects/pack/`）出现带 `(1)`、`(冲突版本)` 的文件
4. 网盘裸仓库出现 `HEAD (1)`、`packed-refs (冲突版本)` 文件
5. **所有设备**都报告相同的仓库错误（不是单机问题）
6. 裸仓库中 `refs/heads/main (冲突版本)` 导致分支丢失

**正确做法**：
1. 不要执行任何 `git push`/`git gc`/`git prune` 操作
2. 不要手动删除任何带 `(1)` 的冲突文件
3. 立即从 `backups/<repo>/` 目录找到最近的 `.bundle` 备份文件恢复
4. 如果没有备份，在**所有设备都停止操作**后，从最后一次成功pull的工作仓库重建裸仓库

### ⚠️ 可以自行处理的情况
以下问题通常可以按本文档步骤自行解决：
- Push被拒（non-fast-forward、lock held）
- Pull冲突（unrelated histories、工作区不干净）
- 换行符/权限导致的虚假修改
- 中文文件名乱码
- 临时文件/锁残留清理
- 分叉提交的合并/rebase
- 换行符、大小写、符号链接等跨平台配置问题

---

## 日志收集命令

当遇到问题需要诊断时，请按顺序收集以下信息。一键诊断脚本 `git-diag` 会自动收集这些信息。

### 1. 基本环境信息
```powershell
# PowerShell
git --version
$PSVersionTable.PSVersion
[System.Environment]::OSVersion.VersionString

# Bash
git --version
uname -a
```

### 2. 仓库状态
```bash
# 在工作仓库内执行
git status
git branch -vv
git log --oneline -5
git remote -v
```

### 3. 锁状态检查
```powershell
# PowerShell（脚本库中）
. .\lock-utils.ps1
Lock-Init <SyncRoot路径>
Lock-Check <仓库名>
Lock-GetHolderInfo <仓库名>

# Bash
source ./lock-utils.sh
_lock_init <SyncRoot路径>
_lock_check <仓库名>
cat "$SYNC_ROOT/locks/<repo>.lock.json"
```

### 4. 冲突文件扫描
```powershell
# PowerShell
. .\check-conflicts.ps1
.\check-conflicts.ps1 -RepoName <repo> -SyncRoot <SyncRoot>

# Bash
./check-conflicts.sh -RepoName <repo> -SyncRoot <SyncRoot>
```

### 5. 裸仓库状态检查
```bash
# 假设裸仓库路径为 $BARE_REPO
git -C "$BARE_REPO" rev-parse HEAD
git -C "$BARE_REPO" fsck --full 2>&1 | head -50
ls -la "$BARE_REPO/HEAD"* 2>/dev/null
ls -la "$BARE_REPO/objects/pack/" 2>/dev/null
find "$BARE_REPO" -name "*(1)*" -o -name "*冲突*" 2>/dev/null
```

### 6. 网盘客户端状态（Windows）
```powershell
# 检查百度网盘进程是否运行
Get-Process BaiduNetdisk -ErrorAction SilentlyContinue
Get-Process BaiduNetdiskHost -ErrorAction SilentlyContinue

# 检查同步目录是否可访问
Test-Path <SyncRoot路径>
```

---

## 一键诊断脚本（git-diag）使用说明

### 快速使用
```powershell
# PowerShell - 快速诊断当前仓库
.\git-diag.ps1

# PowerShell - 完整诊断
.\git-diag.ps1 -Full

# PowerShell - 指定仓库路径和SyncRoot
.\git-diag.ps1 -RepoPath D:\projects\myrepo -SyncRoot D:\BaiduSync\git-sync

# PowerShell - 保存报告到文件
.\git-diag.ps1 -Full -Output
```

```bash
# Bash - 快速诊断当前仓库
./git-diag.sh

# Bash - 完整诊断
./git-diag.sh --full

# Bash - 指定仓库