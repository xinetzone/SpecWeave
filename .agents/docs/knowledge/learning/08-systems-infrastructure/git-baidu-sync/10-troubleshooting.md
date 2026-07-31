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

# Bash - 指定仓库路径
./git-diag.sh --repo-path ~/projects/myrepo --sync-root ~/BaiduSync/git-sync

# Bash - 保存报告到文件
./git-diag.sh --full --output
```

### 输出解读
脚本输出分章节，使用以下标记：
- `[OK]` - 正常项，无需处理
- `[WARN]` - 警告项，建议关注和修复
- `[ERR]` - 错误项，必须修复后才能继续操作
- `[INFO]` - 提示信息，供参考

**诊断总结**会在最后输出：
- 发现问题总数、警告数、错误数
- 推荐的下一步操作（如"先pull再push"、"从备份恢复"等）

---

## 问题场景详解

---

### 同步卡住类

#### 场景1：push后脚本一直等待"等待网盘同步完成"不返回

**现象描述**：
执行 `git-sync-push` 后，脚本输出"等待网盘同步完成..."后长时间无响应，不返回命令行。

**可能原因**（按概率排序）：
1. 百度网盘客户端未运行或已崩溃
2. 网络中断导致网盘无法上传
3. 网盘同步队列中有大量大文件排队，同步极慢
4. 文件被其他程序锁定导致网盘无法读取
5. 网盘空间已满

**诊断步骤**：
```powershell
# 1. 检查百度网盘进程
Get-Process BaiduNetdisk -ErrorAction SilentlyContinue
# 预期输出：能看到BaiduNetdisk进程，如果没有说明客户端未运行

# 2. 检查网盘同步目录是否可访问
Test-Path <SyncRoot路径>
# 预期输出：True

# 3. 检查裸仓库目录是否有.tmp临时文件（表示上传中）
$bareRepo = Join-Path <SyncRoot> "repos\<repo>.git"
Get-ChildItem $bareRepo -Recurse -Filter "*.tmp" -File -ErrorAction SilentlyContinue | Select-Object -First 5 Name, Length, LastWriteTime

# 4. 检查磁盘/网盘空间
# （打开百度网盘客户端查看空间使用情况）
```

**解决方案**：
1. **检查网盘客户端**：
   - 打开百度网盘客户端，确认其正常运行并登录
   - 查看"传输"页面，是否有失败/暂停的任务
   - 如果客户端崩溃，结束进程后重新启动

2. **检查网络**：
   - 确认网络连接正常
   - 如果使用VPN/代理，尝试关闭后重试

3. **处理大文件同步**：
   - 如果仓库中有大文件（>100MB），等待时间会较长
   - 可以按 `Ctrl+C` 中断脚本，确认网盘客户端传输完成后重新push（锁会超时自动释放）

4. **检查文件锁定**：
   - 关闭可能正在使用仓库文件的程序（编辑器、IDE等）
   - 重启电脑后重试

**预防措施**：
- push前确认百度网盘客户端正在运行且同步正常
- 大文件（>50MB）考虑使用Git LFS或其他方式存储
- 定期检查网盘剩余空间，保持至少1GB可用空间

---

#### 场景2：百度网盘客户端显示"同步中"但长时间无进度

**现象描述**：
百度网盘客户端显示正在同步，但进度条长时间不动，传输列表中文件速度为0。

**可能原因**（按概率排序）：
1. 个别大文件传输卡住
2. 文件名包含特殊字符导致同步失败
3. 文件被占用无法读取
4. 网盘客户端bug
5. 网络连接不稳定

**诊断步骤**：
```powershell
# 1. 查看同步目录最近修改的文件
$bareRepo = Join-Path <SyncRoot> "repos\<repo>.git"
Get-ChildItem $bareRepo -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10 FullName, Length, LastWriteTime

# 2. 检查是否有0字节的异常文件
Get-ChildItem $bareRepo -Recurse -File | Where-Object { $_.Length -eq 0 } | Select-Object FullName

# 3. 检查带特殊字符的文件名
Get-ChildItem $bareRepo -Recurse -File | Where-Object { $_.Name -match '[<>:"|?*]' } | Select-Object FullName
```

**解决方案**：
1. **暂停后恢复同步**：
   - 在百度网盘客户端中暂停同步，等待10秒后恢复
   - 或在客户端中对卡住的任务选择"重试"

2. **重启网盘客户端**：
   - 完全退出百度网盘（右键托盘图标→退出）
   - 结束残留进程：`Stop-Process -Name BaiduNetdisk* -Force -ErrorAction SilentlyContinue`
   - 重新启动客户端

3. **检查并清理问题文件**：
   - 如果发现0字节临时文件，等确认无Git操作后删除
   - 不要删除Git正常的object文件！

4. **重新触发同步**：
   - 对裸仓库中任意已有文件执行一次touch（修改时间戳）触发重新同步：
     ```powershell
     (Get-Item "$bareRepo\HEAD").LastWriteTime = Get-Date
     ```

**预防措施**：
- 定期检查百度网盘客户端传输列表，及时处理失败任务
- 文件名避免使用特殊字符
- 仓库大小建议控制在1GB以内（pack后）

---

#### 场景3：pull时提示"裸仓库可能未完全同步"

**现象描述**：
执行 `git-sync-pull` 时，脚本提示"裸仓库可能未完全同步，检测到临时文件"或类似警告，中止pull操作。

**可能原因**（按概率排序）：
1. 另一个设备的push还没完全同步到本地网盘
2. 上次push被中断，留下了.tmp/.pack-tmp临时文件
3. 网盘正在同步裸仓库文件，文件尚未完整下载
4. 存在残留的.lock文件

**诊断步骤**：
```powershell
# 1. 运行冲突检测
$syncRoot = <SyncRoot路径>
$repoName = <repo名>
$bareRepo = Join-Path $syncRoot "repos\$repoName.git"

# 检查临时文件
Get-ChildItem $bareRepo -Recurse -Include "*.tmp","*.pack-tmp","*.part","tmp_pack_*" -File -ErrorAction SilentlyContinue | Select-Object Name, Length, LastWriteTime

# 检查残留lock文件（非locks目录下的）
Get-ChildItem $bareRepo -Recurse -Filter "*.lock" -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "\\locks\\" }

# 2. 用check-conflicts扫描
.\check-conflicts.ps1 -RepoName $repoName -SyncRoot $syncRoot
```

**解决方案**：
1. **等待同步完成**：
   - 打开百度网盘客户端，确认所有传输任务完成
   - 等待1-2分钟确保文件系统缓存刷新
   - 重新执行pull

2. **清理临时文件（确认安全后）**：
   - **重要**：先确认所有设备都没有在执行push/pull！
   - 确认锁不存在：`Lock-Check $repoName` 应显示无锁
   - 清理临时文件：
     ```powershell
     # 仅清理明确的临时文件，不要碰其他文件！
     Get-ChildItem $bareRepo -Recurse -Include "*.tmp","*.pack-tmp","*.part","tmp_pack_*" -File | Remove-Item -Force
     # 清理残留lock（非locks目录）
     Get-ChildItem $bareRepo -Recurse -Filter "*.lock" -File | Where-Object { $_.FullName -notmatch "\\locks\\" } | Remove-Item -Force
     ```
   - 或使用自动清理：`.\check-conflicts.ps1 -RepoName $repoName -SyncRoot $syncRoot -AutoClean`

3. **重新运行诊断**：
   - `.\git-diag.ps1 -RepoPath <工作仓库路径>`
   - 确认临时文件问题已解决

**预防措施**：
- push后等待脚本完全返回（显示"推送成功"）再关闭电脑
- 不要在网盘同步过程中强行关机
- pull前先运行快速诊断确认状态

---

### Push被拒类

#### 场景4：push报错"non-fast-forward"（远程有新提交）

**现象描述**：
push时输出类似错误：
```
! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to '...'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart.
```

**可能原因**（按概率排序）：
1. 其他设备有新push，本地没有pull最新代码
2. 自己在另一台设备做了提交但忘记pull
3. 强制推送历史被重写后本地未更新

**诊断步骤**：
```bash
# 1. 查看本地和远程差异
git fetch baidu
git log --oneline --graph --left-right HEAD...baidu/main
# 输出中: < 表示本地独有的提交，> 表示远程独有的提交

# 2. 查看分叉点
git merge-base HEAD baidu/main
```

**解决方案**：
1. **标准流程：先pull再push**：
   ```bash
   # 先stash工作区更改（如果有的话）
   git stash
   # 拉取并合并
   git-sync-pull
   # 恢复stash
   git stash pop
   # 解决冲突（如果有），然后重新push
   git-sync-push
   ```

2. **如果希望保持线性历史（rebase方式）**：
   ```bash
   git stash
   git fetch baidu
   git rebase baidu/main
   # 解决冲突后
   git add <解决的文件>
   git rebase --continue
   git stash pop
   git-sync-push
   ```

**预防措施**：
- 养成每次开始工作前先pull的习惯
- 多设备工作时，切换设备前一定push完成
- 避免使用`git push -f`除非明确知道在做什么

---

#### 场景5：push报错"failed to push some refs"（非快进）

**现象描述**：
与场景4类似，但可能伴随其他信息，本质都是远程有更新本地没有。

**可能原因**：
同场景4。

**诊断步骤与解决方案**：
同场景4。这是Git的标准保护机制，防止覆盖他人提交。按先pull再push的流程处理即可。

**重要提示**：看到此错误时**不要**使用 `--force` 强制推送！这会覆盖远程提交，导致其他设备的工作丢失。

---

#### 场景6：push报错"lock is held by another device"（锁被占用）

**现象描述**：
push时脚本输出：
```
[lock-utils ERROR] 仓库 myrepo 已被其他设备持有锁
  device_id: xxx-win-01
  hostname:   other-pc
  pid:        1234
  operation:  push
  acquired_at: 2026-07-31T10:00:00+08:00
请等待持有者完成或确认超时后使用 force-unlock 工具
```

**可能原因**（按概率排序）：
1. 另一台设备正在push/pull，正常持有锁
2. 另一台设备push时崩溃/关机，锁未正常释放
3. 锁已超时但还没被自动清理
4. 网络分区导致两台设备同时尝试获取锁（罕见）

**诊断步骤**：
```powershell
# 1. 检查锁状态
. .\lock-utils.ps1
Lock-Init <SyncRoot>
Lock-Check <repo名>
# 关注输出中的：
# - 已持有时间（分钟）
# - 持有者hostname
# - 状态显示

# 2. 查看锁详情
Lock-GetHolderInfo <repo名>
```

**解决方案**：
1. **如果是正常持有（未超时，持有者在线）**：
   - 等待持有者设备完成操作（通常1-5分钟）
   - 联系持有者确认是否正在操作
   - 不要强制解锁！

2. **如果持有者已崩溃/关机/离线**：
   - 确认持有者设备确实已关机，且没有Git进程在运行
   - 等待超过超时时间（默认30分钟），脚本会自动清理超时锁
   - 如需立即处理，使用强制解锁：
     ```powershell
     .\force-unlock.ps1 -RepoName <repo名> -SyncRoot <SyncRoot>
     # 会提示确认，输入YES继续
     ```
   - 强制解锁后，**等待网盘同步1-2分钟**再操作

3. **本设备残留锁（显示持有者是自己但pid已不存在）**：
   - 脚本会自动检测并清理本设备残留锁，无需手动操作

**预防措施**：
- push过程中不要强行关闭终端或关机
- 如果必须中断push，按Ctrl+C等待脚本清理锁
- 设备关机前确认所有同步操作已完成

---

#### 场景7：push报错"pre-receive hook declined"或裸仓库错误（裸仓库损坏）

**现象描述**：
push时输出类似错误：
```
remote: error: object directory ... does not exist
remote: fatal: failed to read object ...: Permission denied
error: remote unpack failed: unable to create temporary object directory
To ...
 ! [remote rejected] main -> main (pre-receive hook declined)
```
或其他来自裸仓库的奇怪错误。

**可能原因**（按概率排序）：
1. 裸仓库因网盘同步冲突损坏
2. 裸仓库文件权限问题（罕见）
3. 裸仓库被其他程序锁定
4. 磁盘错误导致文件损坏

**诊断步骤**：
```bash
# 1. 检查裸仓库是否有冲突文件（关键！）
# PowerShell:
.\check-conflicts.ps1 -RepoName <repo名> -SyncRoot <SyncRoot>
# 如果输出中有CRITICAL级别的冲突，特别是objects/pack/下的，确认是损坏

# 2. 在裸仓库运行fsck
$bareRepo = Join-Path <SyncRoot> "repos\<repo>.git"
git -C $bareRepo fsck --full 2>&1
# 如果输出 error: corrupt loose object / missing blob / broken link，确认损坏

# 3. 检查HEAD文件
Get-Content "$bareRepo\HEAD"
# 预期输出: ref: refs/heads/main
# 如果是乱码或有冲突版本，确认损坏
```

**解决方案**：
⚠️ **这是严重错误，不要尝试git gc或其他修复操作！**

1. **立即停止所有操作**：
   - 所有设备都停止push/pull
   - 不要尝试手动删除冲突文件

2. **从备份恢复**：
   ```powershell
   # 查看可用备份
   $backupDir = Join-Path <SyncRoot> "backups\<repo名>"
   Get-ChildItem $backupDir -Filter "*.bundle" | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime, Length
   
   # 选择最近的备份文件（例如 myrepo-20260730-120000.bundle）
   $latestBundle = (Get-ChildItem $backupDir -Filter "*.bundle" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
   
   # 在一个新目录中验证备份
   mkdir $env:TEMP\repo-restore-test
   cd $env:TEMP\repo-restore-test
   git clone $latestBundle test-restore
   cd test-restore
   git log --oneline -5  # 确认提交完整
   
   # 如果备份正常，重建裸仓库（必须在所有设备都停止后！）
   # 1. 备份损坏的裸仓库目录（重命名）
   Rename-Item $bareRepo "$bareRepo.broken-$(Get-Date -Format yyyyMMdd-HHmmss)"
   
   # 2. 从bundle重建裸仓库
   git clone --bare $latestBundle $bareRepo
   
   # 3. 验证
   git -C $bareRepo fsck --full
   
   # 4. 在工作仓库重新设置remote（如果路径没变则不需要）
   # 5. 在所有设备上重新pull
   ```

3. **如果没有备份**：
   - 找到最后一次成功pull的工作仓库（本地仓库完好的设备）
   - 在该设备上：`git bundle create <backup-file>.bundle --all` 创建备份
   - 按上述步骤从这个bundle重建裸仓库

**预防措施**：
- 定期push后会自动创建备份，确保备份功能正常
- 不要在网盘同步过程中断电或强制关机
- 定期运行 `git-doctor -Mode full` 检查仓库健康

---

#### 场景8：push报错"Could not read from remote repository"（路径问题）

**现象描述**：
push时输出：
```
fatal: 'D:\BaiduSync\git-sync\repos\myrepo.git' does not appear to be a git repository
fatal: Could not read from remote repository.
```
或者：
```
fatal: Could not read from remote repository.
Please make sure you have the correct access rights and the repository exists.
```

**可能原因**（按概率排序）：
1. remote路径配置错误
2. 网盘同步目录被移动或重命名
3. 路径中包含空格但未正确引用
4. 网盘目录未挂载/不可访问（网络驱动器断开）
5. bare仓库目录被误删除

**诊断步骤**：
```bash
# 1. 查看当前remote配置
git remote -v
# 预期输出类似：
# baidu  D:\BaiduSync\git-sync\repos\myrepo.git (fetch)
# baidu  D:\BaiduSync\git-sync\repos\myrepo.git (push)

# 2. 检查路径是否存在
# PowerShell:
Test-Path "D:\BaiduSync\git-sync\repos\myrepo.git"
# 预期输出：True

# 3. 检查路径是否是有效的git裸仓库
Test-Path "D:\BaiduSync\git-sync\repos\myrepo.git\HEAD"
Test-Path "D:\BaiduSync\git-sync\repos\myrepo.git\objects"
# 预期都为True
```

**解决方案**：
1. **路径被移动/重命名**：
   ```bash
   # 更新remote URL
   git remote set-url baidu "新的正确路径"
   # 例如：
   git remote set-url baidu "D:\NewPath\git-sync\repos\myrepo.git"
   ```

2. **路径包含空格问题**：
   ```bash
   # 重新设置时用引号包裹（命令行中）
   git remote set-url baidu "D:\Path With Spaces\git-sync\repos\myrepo.git"
   ```

3. **网络驱动器断开（Z:等映射盘）**：
   - 在文件资源管理器中访问该驱动器，确认连接正常
   - 重新连接网络驱动器
   - 建议使用本地同步目录，不要用网络映射盘作为SyncRoot

4. **裸仓库误删除**：
   - 如果有备份，从备份重建
   - 从最新的工作仓库重新初始化裸仓库：
     ```bash
     # 在工作仓库中，确认本地是最新的
     git status
     # 创建新的裸仓库
     $newBare = "<正确路径>\repos\myrepo.git"
     git init --bare $newBare
     git push baidu --all
     git push baidu --tags
     ```

**预防措施**：
- 初始化同步目录后不要随意移动SyncRoot位置
- 如果必须移动，使用register-repo脚本重新注册所有仓库
- 避免使用需要认证的网络共享作为SyncRoot

---

### Pull失败类

#### 场景9：pull报错"refusing to merge unrelated histories"

**现象描述**：
第一次pull时输出：
```
fatal: refusing to merge unrelated histories
```

**可能原因**（按概率排序）：
1. 本地仓库和远程仓库是两个独立初始化的仓库，没有共同祖先
2. 新建仓库后没有先pull就直接做了提交
3. 裸仓库被重建后与本地历史断开
4. clone时使用了错误的路径

**诊断步骤**：
```bash
# 查看本地历史
git log --oneline -5

# 查看远程历史
git fetch baidu
git log --oneline baidu/main -5

# 检查是否有共同祖先
git merge-base HEAD baidu/main
# 如果没有输出或报错，确认是unrelated histories
```

**解决方案**：
1. **第一次拉取（新设备克隆后首次pull）**：
   ```bash
   # 允许合并不相关的历史（仅首次需要）
   git pull baidu main --allow-unrelated-histories
   # 如果有冲突，解决冲突后commit
   ```

2. **确认是正确的仓库**：
   - 检查remote URL是否正确指向了**同一个**仓库
   - 不要把两个不同项目的仓库混在一起

3. **使用clone-repo脚本（推荐用于新设备）**：
   ```powershell
   # 不要手动git init + git remote add，使用封装好的脚本
   .\clone-repo.ps1 -RepoName <repo名> -SyncRoot <SyncRoot> -TargetPath <本地目录>
   ```

**预防措施**：
- 在新设备上获取仓库时，始终使用 `clone-repo` 脚本而不是手动初始化
- 新建仓库后，先pull确认空仓库状态再做首次提交

---

#### 场景10：pull报错"Your local changes would be overwritten"（工作区不干净）

**现象描述**：
pull时输出：
```
error: Your local changes to the following files would be overwritten by merge:
        <file list>
Please commit your changes or stash them before you merge.
Aborting
```

**可能原因**（按概率排序）：
1. 本地有未提交的修改
2. 跨平台换行符自动转换导致文件显示已修改（实际没改）
3. 文件权限变更被Git检测到（Linux/macOS）

**诊断步骤**：
```bash
# 1. 查看工作区状态
git status
# 查看具体哪些文件被修改

# 2. 查看实际差异（确认是真的修改还是换行符/权限）
git diff
# 如果是换行符问题，会看到整文件^M或整文件改动但内容看起来一样
```

**解决方案**：
1. **有真实的未提交修改**：
   ```bash
   # 方案A：暂存修改，pull后恢复
   git stash
   git-sync-pull
   git stash pop
   # 解决冲突（如果有）

   # 方案B：先提交本地修改
   git add -A
   git commit -m "WIP: 临时提交"
   git-sync-pull
   # 之后可以再amend或rebase整理提交
   ```

2. **换行符导致的虚假修改**：
   参见场景11的解决方案，先配置正确的core.autocrlf，然后：
   ```bash
   # 丢弃换行符导致的"修改"
   git reset --hard HEAD  # 注意：会丢弃所有未提交修改！确认没有真实改动再执行
   ```

3. **权限导致的虚假修改（Linux/macOS）**：
   参见场景17，配置core.filemode=false。

**预防措施**：
- pull前检查git status，了解本地状态
- 正确配置core.autocrlf（Windows: true, Linux/macOS: input）
- 工作区有未完成修改时使用stash暂存

---

#### 场景11：pull后大量文件显示已修改但未实际修改（换行符/权限问题）

**现象描述**：
pull后执行git status显示大量文件已修改，但git diff看不到实质性内容变化，或者看起来每一行都改了（换行符问题）。

**可能原因**（按概率排序）：
1. core.autocrlf配置不正确导致换行符不一致
2. core.filemode=true导致权限位变化被记录
3. 仓库中混入了CRLF和LF混合的换行符
4. 编辑器配置问题（自动转换换行符）

**诊断步骤**：
```bash
# 1. 检查当前autocrlf配置
git config --get core.autocrlf
git config --global --get core.autocrlf

# 2. 检查filemode配置
git config --get core.filemode

# 3. 检查文件实际换行符（file命令在Git Bash/WSL中可用）
file <一个被修改的文件>
# 输出中如果有 "with CRLF line terminators" 表示是Windows换行

# 4. 查看差异的空白字符
git diff -R | cat -A | head -20
# 行尾如果有^M表示是CRLF
```

**解决方案**：
1. **正确配置core.autocrlf**：
   ```powershell
   # Windows（以管理员运行或加--global）
   git config --global core.autocrlf true
   
   # Linux/macOS
   git config --global core.autocrlf input
   ```

2. **配置core.filemode（非Windows平台）**：
   ```bash
   git config --global core.filemode false
   ```

3. **规范化已有文件的换行符**：
   ```bash
   # 在仓库根目录，确保配置正确后
   git add . -u
   git commit -m "chore: 规范化换行符"
   # 或使用git的规范化功能：
   git rm --cached -r .
   git reset --hard
   ```

4. **添加.gitattributes（推荐多人项目）**：
   在仓库根目录创建 `.gitattributes` 文件：
   ```
   * text=auto
   *.sh text eol=lf
   *.bat text eol=crlf
   *.ps1 text eol=crlf
   ```
   提交后所有人共享统一配置。

**预防措施**：
- 安装Git时选择正确的换行符选项（Windows选"Checkout Windows-style, commit Unix-style"）
- 跨平台项目必须添加.gitattributes
- 所有设备统一配置core.autocrlf和core.filemode

---

#### 场景12：pull后中文文件名乱码

**现象描述**：
pull后，中文文件名变成类似 `\346\226\207\344\273\266.md` 或问号、方框等乱码字符。

**可能原因**（按概率排序）：
1. Git未配置UTF-8文件名支持
2. 终端/控制台编码不支持中文
3. 系统区域设置问题
4. 旧版本Git不支持unicode文件名

**诊断步骤**：
```bash
# 1. 检查Git编码配置
git config --get core.quotepath
git config --get i18n.commitencoding
git config --get i18n.logoutputencoding

# 2. 查看当前终端编码（PowerShell）
chcp
# Windows中文系统默认是936 (GBK)，UTF-8是65001

# 3. 查看文件名的八进制转义形式
ls | cat -v  # Git Bash
```

