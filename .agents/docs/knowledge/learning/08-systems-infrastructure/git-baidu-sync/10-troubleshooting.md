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

**解决方案**：
1. **配置Git支持中文路径**：
   ```bash
   # 所有平台都执行
   git config --global core.quotepath false
   git config --global i18n.commitencoding utf-8
   git config --global i18n.logoutputencoding utf-8
   ```

2. **设置终端为UTF-8（Windows PowerShell）**：
   ```powershell
   # 当前临时设置
   chcp 65001
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   
   # 永久设置：在PowerShell配置文件中添加
   notepad $PROFILE
   # 添加上述两行后保存
   ```

3. **使用Git Bash/WSL**：
   - Git Bash对中文支持通常比PowerShell/cmd更好
   - 或使用Windows Terminal，配置默认编码为UTF-8

**预防措施**：
- 安装Git后第一时间配置中文支持（setup-git-config脚本会自动配置）
- 使用Windows Terminal代替旧版cmd/powershell.exe
- 尽量使用英文文件名可彻底避免此类问题

---

### 仓库损坏类

#### 场景13：git fsck报"error: corrupt loose object"或"missing blob"

**现象描述**：
运行`git fsck --full`时报错：
```
error: corrupt loose object 'abc123...'
fatal: object abc123... is corrupted
error: missing blob def456...
broken link from    tree ...
```

**可能原因**：
1. 网盘同步冲突导致object文件损坏
2. 写入过程中磁盘满/断电
3. 裸仓库冲突文件（(1)文件）被错误保留/删除
4. 磁盘坏道

**诊断步骤**：
```bash
# 1. 运行完整fsck，记录所有错误
cd <工作仓库路径>
git fsck --full 2>&1 | tee fsck-errors.log

# 2. 检查裸仓库是否有冲突文件（这是最常见原因！）
.\check-conflicts.ps1 -RepoName <repo名> -SyncRoot <SyncRoot>
# 如果有CRITICAL级别的objects/pack/冲突，确认同步冲突导致
```

**解决方案**：
🛑 **严重错误！停止所有push/pull操作。**

1. **有备份时的标准恢复流程**：
   - 参考场景7"从备份恢复"的完整流程
   - 这是最安全可靠的方案

2. **尝试修复（仅当没有备份时，不保证成功）**：
   ```bash
   # 1. 首先在所有设备停止操作！
   
   # 2. 备份当前损坏的仓库（两个备份：工作区+裸仓库）
   cp -r <裸仓库路径> <裸仓库路径>.broken-backup-$(date +%Y%m%d)
   
   # 3. 尝试从其他完好的设备push重建
   # 找一台本地仓库完好、git fsck通过的设备
   # 在该设备上：
   git fsck --full  # 确认本地完好
   # 备份并重命名损坏的裸仓库
   # 从该设备重新init裸仓库并push
   
   # 4. 如果只有当前设备，尝试从pack恢复
   # （复杂操作，成功率不高，建议优先从备份恢复）
   ```

**预防措施**：
- 每次push自动创建.bundle备份，不要禁用备份功能
- 定期运行git-doctor全量检查
- 避免在网盘同步时强制关机

---

#### 场景14：git status报"fatal: bad object HEAD"

**现象描述**：
执行任何git命令都输出：
```
fatal: bad object HEAD
fatal: Not a valid object name HEAD
```
或进入仓库时提示处于detached HEAD状态但commit不存在。

**可能原因**：
1. HEAD文件指向的ref不存在或损坏
2. refs/heads/main分支文件损坏
3. 网盘冲突导致refs文件出现冲突副本
4. HEAD被直接修改损坏

**诊断步骤**：
```bash
# 1. 查看HEAD文件内容
cat .git/HEAD
# 正常应为: ref: refs/heads/main

# 2. 检查refs/heads目录
ls -la .git/refs/heads/
# 检查是否有 main (1) 或 冲突版本 文件
ls -la <裸仓库>/refs/heads/

# 3. 查看reflog（可能救命）
git reflog
# 如果reflog还在，可以找到最后一个有效的commit
```

**解决方案**：
🛑 **严重级别问题。**

1. **reflog可恢复的情况**：
   ```bash
   # 如果git reflog还能看到历史
   git reflog
   # 找到最后一个正常的commit（通常是HEAD@{0}之前的）
   # 例如abc1234是最后一个好commit
   
   # 备份当前状态
   cp -r .git .git.bad-head-backup
   
   # 重置HEAD到好的commit
   git reset --hard abc1234
   
   # 然后检查裸仓库的状态，可能需要重建裸仓库
   ```

2. **裸仓库refs冲突导致**：
   - 检查裸仓库 `refs/heads/` 目录，是否有 `main (1)` 或 `main (冲突版本)` 文件
   - 如果有，**不要直接删除！** 先备份整个裸仓库
   - 对比两个文件内容：
     ```powershell
     Get-Content <裸仓库>\refs\heads\main
     Get-Content <裸仓库>\refs\heads\main` (1)
     ```
   - 如果两个内容都是有效的commit hash，选择时间更新的那个（或从备份恢复）

3. **从备份恢复**（最安全）：
   - 同场景7的备份恢复流程

**预防措施**：
- 不要手动编辑.git/目录下的文件
- 运行check-conflicts发现HEAD/packed-refs冲突时立即处理
- 正常push/pull流程不会导致HEAD损坏，通常与网盘冲突或手动修改有关

---

#### 场景15：网盘目录出现大量"(1)"、"(冲突版本)"文件

**现象描述**：
在文件资源管理器中查看网盘同步目录时，发现大量文件名带后缀：
- `HEAD (1)`
- `pack-abc123.pack (冲突版本)`
- `config (来自 DESKTOP-XXX)`
- `tmp_pack_xyz (2).tmp`

**可能原因**：
1. 两台设备同时修改同一文件，网盘创建冲突副本
2. 文件被锁定时网盘尝试写入失败，创建冲突版本
3. Git操作与网盘同步竞态
4. 锁机制失效导致并发push

**诊断步骤**：
```powershell
# 1. 立即运行冲突检测
.\check-conflicts.ps1 -RepoName <repo名> -SyncRoot <SyncRoot>
# 重点关注CRITICAL级别：
# - objects/pack/下的冲突 = 严重，仓库损坏
# - HEAD/packed-refs冲突 = 严重
# - refs/下冲突 = 警告，需要人工处理
```

**解决方案**：
根据冲突分类处理：

1. **CRITICAL（红色/严重）冲突 - objects/pack/HEAD/packed-refs**：
   - 🛑 停止所有操作
   - 按场景7流程从备份恢复
   - **不要手动删除这些冲突文件！**

2. **WARNING（黄色/警告）冲突 - refs/config/hooks**：
   - 确认所有设备都没有在执行push/pull
   - 检查锁状态：`Lock-Check`应显示无锁
   - 对比原文件和冲突文件：
     ```powershell
     # 例如refs/heads/main冲突
     $orig = Get-Content "$bareRepo\refs\heads\main"
     $conflict = Get-Content "$bareRepo\refs\heads\main (1)"
     Write-Host "原始: $orig"
     Write-Host "冲突: $conflict"
     ```
   - 通常保留时间更新的那个是正确的（或从所有设备pull后确认哪个hash最新）
   - 人工确认后重命名/删除冲突文件：
     ```powershell
     # 先备份
     Copy-Item "$bareRepo\refs\heads\main (1)" "$bareRepo\refs\heads\main (1).backup"
     # 确认正确后删除冲突副本
     Remove-Item "$bareRepo\refs\heads\main (1)"
     ```

3. **INFO（蓝色/提示）冲突 - .tmp临时文件**：
   - 确认无Git进程后可以安全清理
   - `.\check-conflicts.ps1 -RepoName <repo名> -SyncRoot <SyncRoot> -AutoClean`

**预防措施**：
- 锁机制就是为了防止并发push产生冲突，不要跳过锁检查
- push完成等待脚本返回再关机
- 发现冲突及时处理，不要积累

---

#### 场景16：refs/heads/main (冲突版本)导致分支丢失

**现象描述**：
push/pull时报分支不存在，或git branch不显示main分支，但在refs/heads目录看到`main (1)`或`main (冲突版本)`文件。

**可能原因**：
1. 并发push导致refs文件冲突
2. 网盘同步refs文件时被中断
3. Git写入refs时恰好坏同步

**诊断步骤**：
```bash
# 1. 列出所有refs文件
ls -la <裸仓库>/refs/heads/
ls -la <工作仓库>/.git/refs/heads/

# 2. 查看packed-refs文件
cat <裸仓库>/packed-refs
cat <工作仓库>/.git/packed-refs

# 3. 从reflog查找最后有效的commit
git reflog
```

**解决方案**：
1. **找到正确的commit hash**：
   ```powershell
   # 读取所有冲突的refs文件内容
   $refDir = Join-Path <裸仓库> "refs\heads"
   Get-ChildItem $refDir -Filter "main*" | ForEach-Object {
       $hash = (Get-Content $_.FullName -Raw).Trim()
       Write-Host "$($_.Name): $hash"
       # 验证这个hash是否存在
       git -C <裸仓库> cat-file -t $hash 2>&1
   }
   ```

2. **恢复refs文件**：
   ```powershell
   # 假设正确的hash是abc123def456...
   # 先备份
   Copy-Item $refDir\main* $refDir\..\..\backups\refs-backup\ -Recurse -Force
   
   # 删除冲突版本
   Remove-Item "$refDir\main (*" -Force
   Remove-Item "$refDir\main *冲突*" -Force
   
   # 写入正确的hash
   "abc123def456..." | Set-Content "$refDir\main" -Encoding UTF8 -NoNewline
   
   # 验证
   git -C <裸仓库> rev-parse main
   git -C <裸仓库> fsck --full
   ```

3. **如果所有refs文件都无效**：
   - 从reflog找到最后一个有效commit
   - 或按场景7从备份恢复

**预防措施**：
- 锁机制正常工作时不应出现此问题
- 不要在push过程中关闭电脑
- 定期检查refs目录是否有冲突文件

---

### 跨平台类

#### 场景17：Windows上正常，Linux/macOS上git status显示所有shell脚本权限变更

**现象描述**：
在Windows上clone/push一切正常，在Linux/macOS上pull后，所有`.sh`文件显示已修改，`git diff`显示：
```
diff --git a/script.sh b/script.sh
old mode 100644
new mode 100755
```

**可能原因**：
1. core.filemode=true（默认）记录了文件可执行位
2. Windows不支持Unix权限，push时权限位丢失
3. 不同设备umask设置不同

**诊断步骤**：
```bash
# 检查filemode配置
git config --get core.filemode
# 预期在Linux/macOS也应该是false（对于网盘同步方案）
```

**解决方案**：
1. **全局配置（推荐）**：
   ```bash
   # 在Linux/macOS上执行（Windows不需要，默认不支持权限）
   git config --global core.filemode false
   ```

2. **单个仓库配置**：
   ```bash
   git config core.filemode false
   ```

3. **修复已有的权限变更记录**：
   ```bash
   git config core.filemode false
   git reset --hard HEAD  # 丢弃权限变更的"修改"
   ```

**预防措施**：
- 在所有非Windows设备上设置 `core.filemode false`
- setup-git-config脚本会自动配置
- 可执行权限问题：需要执行权限的脚本在clone后手动chmod +x，或在仓库中说明

---

#### 场景18：大小写文件名冲突（File.txt和file.txt在Linux上是两个文件，Windows上合并）

**现象描述**：
- Windows上工作正常，但Linux/macOS pull时报文件冲突
- 或反过来：Linux上创建了File.txt和file.txt，Windows上只看到一个，另一个"消失"
- push时报告"will be replaced by merge"或类似大小写冲突

**可能原因**：
1. Windows/macOS默认文件系统不区分大小写（NTFS/HFS+默认）
2. Linux ext4/xfs区分大小写
3. 重命名文件时只改了大小写，Git未正确识别

**诊断步骤**：
```bash
# 列出当前目录所有文件，检查大小写重复
ls | sort -f | uniq -di
# Git Bash/WSL:
find . -maxdepth 1 -type f | tr '[:upper:]' '[:lower:]' | sort | uniq -d
```

**解决方案**：
1. **重命名解决冲突**：
   ```bash
   # 方案：用临时名中转，确保所有平台都能识别
   git mv File.txt File.txt.tmp
   git commit -m "rename: temp name to avoid case conflict"
   git mv File.txt.tmp file_renamed.txt
   git commit -m "rename: final name"
   git push baidu
   ```

2. **Windows上强制大小写敏感（高级）**：
   ```powershell
   # Windows 10 1803+支持目录级别大小写敏感
   # 以管理员运行PowerShell：
   fsutil.exe file setCaseSensitiveInfo <仓库路径> enable
   # 注意：这只影响新创建的文件，且需要所有协作者都做同样设置
   ```

3. **预防规则**：
   - 项目中文件名统一使用小写，用短横线/下划线分隔
   - 重命名时一定用`git mv`而不是直接在资源管理器重命名
   - 代码Review时检查文件名大小写

**预防措施**：
- 团队约定文件名命名规范（建议全小写+短横线）
- 配置Git配置项：
  ```bash
  git config --global core.ignorecase false  # 在区分大小写的系统上
  ```
- 避免仅大小写不同的文件名

---

#### 场景19：符号链接变成普通文本文件

**现象描述**：
- 在Linux/macOS创建的符号链接（symlink），在Windows上pull后变成普通文本文件
- 文件内容就是链接目标路径，而不是指向目标文件

**可能原因**：
1. Windows文件系统/或Git配置不支持符号链接
2. 创建链接时没有管理员权限
3. core.symlinks配置为false

**诊断步骤**：
```bash
# 检查symlinks配置
git config --get core.symlinks

# 检查文件类型（Git Bash/Linux）
ls -la <symlink文件>
# 符号链接开头显示 l，普通文件显示 -
file <symlink文件>
```

**解决方案**：
1. **Windows启用符号链接支持**：
   - 启用Windows开发者模式（设置→更新和安全→开发者选项→开发人员模式）
   - 或以管理员身份运行Git/终端
   - 配置Git支持符号链接：
     ```powershell
     git config --global core.symlinks true
     ```
   - 重新pull/clone仓库

2. **不使用符号链接（兼容性最好）**：
   - 如果跨平台需求强烈，避免在仓库中使用符号链接
   - 用脚本、构建工具或复制文件代替
   - 文档中说明如何手动创建链接

3. **修复已变文件的符号链接**：
   ```bash
   # Linux/macOS
   git reset --hard HEAD
   # 如果core.symlinks配置正确应该能恢复
   ```

**预防措施**：
- 评估项目是否真的需要符号链接，能避免就避免
- Windows用户启用开发者模式
- 团队统一core.symlinks配置

---

### 日常使用类

#### 场景20：忘记在A设备push就关电脑，B设备上做了新提交（分叉）

**现象描述**：
在设备A做了提交但没push就关机了，在设备B继续工作做了新提交并push。后来打开设备A，push时被non-fast-forward拒绝，git log显示历史分叉。

**可能原因**：
典型的多设备未同步场景，两台设备各自有独立提交。

**诊断步骤**：
```bash
# 1. 在设备A，fetch远程查看分叉情况
git fetch baidu
git log --oneline --graph --left-right HEAD...baidu/main
# < 开头是设备A的本地提交
# > 开头是设备B已push的提交

# 2. 查看分叉点
git merge-base HEAD baidu/main
```

**解决方案**：
有两种处理方式，根据提交性质选择：

1. **方式一：rebase（保持线性历史，推荐）**：
   ```bash
   # 在设备A
   git stash  # 如果有未提交修改
   git fetch baidu
   git rebase baidu/main
   # 如果有冲突，解决冲突：
   # 编辑冲突文件，然后
   git add <解决的文件>
   git rebase --continue
   # 重复直到rebase完成
   git stash pop  # 恢复stash
   git-sync-push
   ```
   **注意**：rebase会重写本地未push提交的hash，如果这些提交已经在其他地方被基于开发，不要rebase。但此处A设备的提交从未push过，所以是安全的。

2. **方式二：merge（保留合并点，简单）**：
   ```bash
   git stash
   git fetch baidu
   git merge baidu/main
   # 解决冲突
   git add <解决的文件>
   git commit  # 或使用默认合并信息
   git stash pop
   git-sync-push
   ```
   这会产生一个merge commit，历史有分叉合并点。

**预防措施**：
- 离开设备前一定push（`git-sync-push`）
- 养成"关机前push，开机后pull"的习惯
- 或设置定时自动push（个人项目可以，团队项目慎重）

---

#### 场景21：误执行了git push -f强制推送覆盖了远程

**现象描述**：
错误执行了`git push -f`（force push），覆盖了远程的提交，其他设备pull时发现自己的提交不见了，或提示unrelated histories。

**可能原因**：
手误执行了强制推送，或误以为需要force。

**诊断步骤**：
```bash
# 1. 不要做任何多余操作，先看reflog
# 在执行force-push的设备上：
git reflog
# 找到force-push之前HEAD的位置，通常是HEAD@{1}
# 例如输出：
# abc1234 (HEAD -> main) HEAD@{0}: push: forcing main to ... (forced update)
# def5678 HEAD@{1}: commit: 我之前正确的提交
```

**解决方案**：
⚠️ **时间就是生命，越快恢复越好，不要继续操作！**

1. **在force-push的设备上立即恢复（最简单）**：
   ```bash
   # 找到force前的位置
   git reflog
   # 假设HEAD@{1}是force-push前的状态
   git reset --hard HEAD@{1}
   # （注意：这会丢弃工作区修改，如果有需要先stash）
   
   # 强制推回去恢复远程！
   git push baidu main --force
   
   # 验证远程恢复后，通知所有其他设备执行：
   # git fetch baidu
   # git reset --hard baidu/main  # 注意：丢弃本地未push提交！
   ```

2. **force-push的设备已关闭/找不到了**：
   从备份恢复：
   ```powershell
   # 查找force-push之前的备份文件
   # 备份按时间命名，选force-push时间之前的那个
   Get-ChildItem <SyncRoot>\backups\<repo名>\*.bundle | Sort-Object LastWriteTime -Descending
   ```
   按场景7的备份恢复流程操作。

3. **其他设备上恢复（本地还有旧提交）**：
   ```bash
   # 在还没pull的其他设备上（幸运的话）
   git reflog
   git branch recovery <旧提交hash>
   # 然后从recovery分支push或bundle
   ```

**预防措施**：
- **永远不要使用`git push -f`/`--force`！** 日常同步完全不需要
- 如果确实需要（比如已经push了敏感信息），使用`--force-with-lease`更安全
- 配置Git禁止裸force-push：
  ```bash
  git config --global push.default current
  # 或设置服务器端（本方案是网盘，没有服务器端保护，靠自觉）
  ```
- 保护分支：在重要分支上避免强制操作

---

#### 场景22：想要重命名仓库/迁移到新目录

**现象描述**：
想要把仓库从`old-name`改名为`new-name`，或把SyncRoot移动到新位置。

**可能原因**：
项目重命名、磁盘空间不够迁移、目录结构调整。

**诊断步骤**：
无需诊断，这是正常操作需求。

**解决方案**：
**方案一：重命名仓库（不移动SyncRoot位置）**
```powershell
# 1. 确保所有设备都已push，工作区干净
git status
# 在所有设备上确认工作区clean并已push

# 2. 重命名裸仓库目录
$syncRoot = <SyncRoot路径>
$oldBare = Join-Path $syncRoot "repos\old-name.git"
$newBare = Join-Path $syncRoot "repos\new-name.git"
Rename-Item $oldBare "new-name.git"

# 3. 在所有工作仓库更新remote URL
git remote set-url baidu $newBare

# 4. 重命名备份目录（可选）
$oldBackup = Join-Path $syncRoot "backups\old-name"
$newBackup = Join-Path $syncRoot "backups\new-name"
if (Test-Path $oldBackup) { Rename-Item $oldBackup "new-name" }

# 5. 重命名锁文件（可选）
$oldLock = Join-Path $syncRoot "locks\old-name.lock.json"
if (Test-Path $oldLock) { Remove-Item $oldLock -Force }  # 锁是临时的，直接删除即可

# 6. 验证
git remote -v
git-sync-push
git-sync-pull
```

**方案二：迁移整个SyncRoot到新位置**
```powershell
# 1. 所有设备push并停止操作
# 2. 等待网盘完全同步
# 3. 在所有设备上：
#    - 退出百度网盘客户端
#    - 移动/复制SyncRoot目录到新位置
#    - 重新配置百度网盘同步新目录
# 4. 在所有工作仓库更新remote路径
# （可以写个脚本批量更新，或者重新clone更简单）

# 或者更简单的方式：
# 在新SyncRoot位置初始化后，对每台设备每个仓库：
# 旧的remote改成新路径，或者用clone-repo重新克隆
```

**更安全的迁移方式**：
1. 在新位置初始化新的同步目录结构
2. 在当前完好的工作仓库上，把remote设为**两个**：
   ```bash
   git remote add baidu-new <新路径>
   git push baidu-new --all
   git push baidu-new --tags
   ```
3. 验证新仓库正常后，所有设备切换到新remote：
   ```bash
   git remote remove baidu
   git remote rename baidu-new baidu
   ```
4. 确认所有设备都切换后，删除旧目录

**预防措施**：
- 命名前想好，尽量避免重命名
- 重命名/迁移前所有设备都push
- 迁移后逐一验证仓库可正常push/pull

---

#### 场景23：如何在新设备上快速开始工作

**现象描述**：
买了新电脑/重装系统，需要把同步的仓库拉下来开始工作。

**可能原因**：
新设备环境搭建。

**解决方案**：
1. **准备工作（在新设备上）**：
   - 安装Git
   - 安装百度网盘客户端，登录并等待同步完全完成（等所有文件下载到本地）
   - 运行setup-git-config配置Git环境
   ```powershell
   .\setup-git-config.ps1
   ```

2. **克隆仓库（推荐方式，用封装脚本）**：
   ```powershell
   # 进入脚本目录
   cd d:\AI\.agents\scripts\git-baidu-sync
   
   # 克隆单个仓库
   .\clone-repo.ps1 -RepoName <repo名> -SyncRoot <SyncRoot路径> -TargetPath <本地工作目录>
   
   # 示例：
   .\clone-repo.ps1 -RepoName myproject -SyncRoot D:\BaiduSync\git-sync -TargetPath D:\projects\myproject
   ```

3. **手动方式（了解原理）**：
   ```bash
   # 1. 创建工作目录
   mkdir -p ~/projects/myproject
   cd ~/projects/myproject
   
   # 2. 克隆
   git clone <SyncRoot>/repos/myproject.git .
   
   # 3. 验证
   git status
   git log --oneline -3
   ```

4. **验证安装**：
   ```powershell
   # 运行快速诊断
   .\git-diag.ps1 -RepoPath <工作目录>
   # 应显示无错误
   
   # 测试pull（应该已经是最新）
   .\git-sync-pull.ps1
   ```

**注意事项**：
- 不要手动`git init`然后`git remote add`，用clone
- 第一次push如果报unrelated histories，参考场景9用--allow-unrelated-histories（但用正确的clone流程不会出现）
- 所有设备上的Git配置（autocrlf等）要一致，用setup-git-config脚本统一配置

---

#### 场景24：如何废弃一个仓库（归档）

**现象描述**：
项目结束不再需要同步，想要归档仓库，释放网盘空间但保留历史。

**解决方案**：
1. **最后一次备份**：
   ```powershell
   # 在任意设备的工作仓库
   .\git-backup.ps1 -RepoPath <工作仓库路径> -SyncRoot <SyncRoot>
   # 这会创建一个.bundle文件作为最终备份
   ```

2. **导出归档（可选但推荐）**：
   ```bash
   # 创建一个完整的bundle归档，包含所有分支标签
   git bundle create <repo名>-archive-$(date +%Y%m%d).bundle --all
   
   # 也可以导出为tar.gz压缩包
   cd ..
   tar -czf <repo名>-archive-$(date +%Y%m%d).tar.gz <repo名>/
   ```

3. **从网盘同步中移除**：
   ```powershell
   # 1. 所有设备删除工作目录（可选，或保留本地副本）
   
   # 2. （可选）在网盘客户端中把该仓库目录从同步列表移除
   
   # 3. 删除网盘上的裸仓库（等确认归档备份已妥善保存后！）
   # Remove-Item <SyncRoot>\repos\<repo名>.git -Recurse -Force
   # Remove-Item <SyncRoot>\backups\<repo名> -Recurse -Force
   # Remove-Item <SyncRoot>\locks\<repo名>.lock.json -Force -ErrorAction SilentlyContinue
   ```
   **注意**：删除是永久的！一定要确认归档备份已复制到安全位置（不要只放在同一个网盘里！）

4. **本地工作仓库处理**：
   - 可以保留本地目录继续作为普通Git仓库使用
   - 或删除baiduremote：`git remote remove baidu`
   - 或整个删除本地目录

**归档最佳实践**：
- 归档文件至少保存到两个不同的位置（本地移动硬盘+云存储）
- 在归档文件名中包含日期
- 可以导出一份静态HTML文档（用gitinstaweb或其他工具）方便不装Git也能查看代码
- 保留.bundle文件就可以随时恢复完整仓库历史

---

## 附录：常用命令速查表

| 操作 | PowerShell命令 | Bash命令 |
|------|---------------|---------|
| 快速诊断 | `.\git-diag.ps1` | `./git-diag.sh` |
| 完整诊断 | `.\git-diag.ps1 -Full` | `./git-diag.sh --full` |
| 健康检查 | `.\git-doctor.ps1 -Mode full` | `./git-doctor.sh --mode full` |
| 冲突扫描 | `.\check-conflicts.ps1 -RepoName <r> -SyncRoot <s>` | `./check-conflicts.sh -RepoName <r> -SyncRoot <s>` |
| 检查锁 | `.\lock-utils.ps1 → Lock-Check <r>` | `source lock-utils.sh; _lock_check <r>` |
| 强制解锁 | `.\force-unlock.ps1 -RepoName <r> -SyncRoot <s>` | `./force-unlock.sh -RepoName <r> -SyncRoot <s>` |
| Push | `.\git-sync-push.ps1` | `./git-sync-push.sh` |
| Pull | `.\git-sync-pull.ps1` | `./git-sync-pull.sh` |
| 创建备份 | `.\git-backup.ps1` | `./git-backup.sh` |
| 新设备克隆 | `.\clone-repo.ps1 ...` | `./clone-repo.sh ...` |
| 配置Git | `.\setup-git-config.ps1` | `./setup-git-config.sh` |
