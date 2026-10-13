# 命令签名与判据速查（wsl-drvfs-mount）

> 环境基线：Windows 受管主机 + PowerShell 7+ + WSL 2（openKylin-3.0，systemd=true），2026-10-13 实测。
> 路径事实：本机 PATH 被裁剪，`net.exe`、`git` 裸名可能不可用；以下均给全路径或前置 PATH 写法。

## 0. 公共前置（PowerShell）

```powershell
$env:WSL_UTF8 = 1
$wsl = "$env:WINDIR\System32\wsl.exe"
$net = "$env:WINDIR\System32\net.exe"
# git（提交类操作需要时）
$env:PATH = "D:\Program Files\Git\mingw64\bin;$env:PATH"
```

进入 WSL 的系统类命令统一前缀：`export LC_ALL=C LANGUAGE=C`。

## 1. 只读探测（§2）

| 目的 | 命令 | 通过判据 |
|---|---|---|
| WSL 形态 | `& $wsl -l -v` | 目标发行版存在、VERSION 2 |
| SMB 端口 | `Test-NetConnection <server> -Port 445`（或 TcpClient 3s 超时） | `TcpTestSucceeded : True` |
| ICMP | `Test-Connection -TargetName <server> -Count 2 -Quiet` | True（不通但 445 通亦可继续，按主机禁 ping 处理） |
| 共享与既有映射 | `& $net view \\<server>` | 列出共享；目标行 `Used as <盘符>:` 即存在持久映射 |
| 本机会话列表 | `& $net use` | 看到 `\\server\share` 与盘符/状态 |
| 挂载点查重 | `& $wsl -d <distro> -- bash -lc "mount \| grep /mnt/ai; grep /mnt/ai /etc/fstab"` | 二者均无命中才可新建/写入 |

`net view` 成功返回示例（关键字段）：

```text
Shared resources at \\10.16.11.3
Alg server (Samba, Ubuntu)
Share name  Type  Used as  Comment
ai          Disk  S:       Home
The command completed successfully.
```

## 2. 凭据分支（仅探测要求认证时）

```powershell
# Windows 侧建会话（* 交互输入密码，不进命令历史/脚本明文）
& $net use \\10.16.11.3\ai /user:<域或主机>\<用户名> *
# 持久化（可选）：加 /persistent:yes；清除会话：& $net use \\10.16.11.3\ai /delete
```

闭合后重试 `net view`，成功才回挂载流程。drvfs 本身不接受用户名/密码参数。

## 3. 挂载（§5.1）

```bash
sudo mkdir -p /mnt/ai
# 形态 A：持久映射盘符（最短，本机成功形态）
sudo mount -t drvfs S: /mnt/ai
# 形态 B：UNC 直挂（可移植；必须单引号）
sudo mount -t drvfs '\\10.16.11.3\ai' /mnt/ai
# 形态 C：无盘符 NTFS 文件夹卷（源必须是 NTFS 挂载点卷）
sudo mount -t drvfs 'C:\mountpoint' /mnt/myvolume
```

可选元数据/权限选项（按需，非必需）：`-o metadata,uid=$(id -u),gid=$(id -g),umask=22,fmask=11`。

## 4. 三段验证（§5.1，逐条留输出）

```bash
# 1) 挂载表层：关键字 type 9p + aname=drvfs;path=S:
mount | grep /mnt/ai
# 期望片段：S: on /mnt/ai type 9p (rw,...,aname=drvfs;path=S:;...)

# 2) 内容层（硬闸口）：必须 > 0
ls /mnt/ai | wc -l

# 3) 写入层：业务用户 + 非空写读回
id -un
echo "probe-$(date +%s)" > /mnt/ai/.probe && cat /mnt/ai/.probe && rm /mnt/ai/.probe
```

失败分诊：

| 现象 | 优先怀疑 | 下一步 |
|---|---|---|
| `mount: no such device`/drvfs 不识别 | WSL 1 或旧版本 | `wsl -l -v` 确认 VERSION 2；升级 WSL |
| 挂载成功但条目数 0 | 映射断开/空共享/路径错 | `net use` 查状态；改 UNC 形态重挂 |
| 写探针 Permission denied | Samba/Windows ACL；root 与业务用户语义差 | 以业务用户复测；在 Windows 侧核权限 |
| DNS/超时 | 网络/VPN | 回到 445 探测；检查 VPN 与路由 |

## 5. 持久化（§5.2）

```bash
# 备份 + 幂等追加 fstab（nofail 不可省）
sudo cp /etc/fstab /etc/fstab.bak.$(date +%Y%m%d)
grep -qE '^S:[[:space:]]+/mnt/ai[[:space:]]+drvfs' /etc/fstab \
  || echo 'S: /mnt/ai drvfs defaults,nofail 0 0' | sudo tee -a /etc/fstab

# 显式 automount（消除默认值依赖；段已存在则跳过）
grep -q '\[automount\]' /etc/wsl.conf \
  || printf '\n[automount]\nenabled=true\nmountFsTab=true\n' | sudo tee -a /etc/wsl.conf

# 静态校验：只认两行计数
findmnt --verify --verbose
# 期望：0 parse errors, 0 errors（drvfs 三类 warning 见 SKILL §5.3，忽略）
sudo systemctl daemon-reload 2>/dev/null || true
```

UNC 形态 fstab 行（注意 fstab 内单引号保留）：

```text
'\\10.16.11.3\ai' /mnt/ai drvfs defaults,nofail 0 0
```

## 6. 冷启动实证（§5.4）

```powershell
& $wsl --terminate openKylin-3.0
& $wsl -d openKylin-3.0 -- bash -lc "export LC_ALL=C LANGUAGE=C; mount | grep -E '/mnt/(ai|c|d)'; ls /mnt/ai | wc -l; id -un; echo x > /mnt/ai/.p && cat /mnt/ai/.p && rm /mnt/ai/.p"
```

期望同时具备：

- `/mnt/ai` 的 9p/drvfs 自动挂载条目；
- `/mnt/c`、`/mnt/d` 既有自动挂载仍在（无回归）；
- 条目数与挂载前一致（本机 13）；
- `id -un` 为业务用户（本机 openkylin），写读回成功。

补挂（nofail 触发空目录时）：恢复映射会话后 `sudo mount -a`。

## 7. 卸载与回滚

```bash
sudo umount /mnt/ai
```

回滚持久化：用备份覆盖（`sudo cp /etc/fstab.bak.20261013 /etc/fstab`，wsl.conf 同理）→ `wsl --terminate <distro>` → 冷启动确认。备份稳定一月后删除。

## 8. 本机实测事实卡（2026-10-13）

| 项 | 值 |
|---|---|
| 目标 | `\\10.16.11.3\ai`（Samba on Ubuntu，共享 ai/media/shared） |
| 复用会话 | 当前 Windows 身份已认证，持久映射 S:（Home） |
| 发行版 | openKylin-3.0，WSL 2，默认用户 openkylin |
| 挂载点 | `/mnt/ai`，条目数 13，业务用户读写通过 |
| 持久化 | fstab `S: /mnt/ai drvfs defaults,nofail 0 0` + wsl.conf automount 段 |
| 校验 | findmnt 0 parse errors / 0 errors / 4 warnings（已知噪音）；terminate 冷启动通过 |
