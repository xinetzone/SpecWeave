---
name: wsl-drvfs-mount
description: 在 WSL 2 中挂载 Windows 盘符、UNC 网络共享（SMB/Samba）或无盘符 NTFS 卷并做 fstab 持久化的标准作业。当用户提到挂载网络盘/共享目录到 WSL、drvfs mount、/etc/fstab 开机挂载、wsl.conf automount、挂载后为空目录时使用；不用于 wsl --mount 物理磁盘直通、内核态 cifs/nfs 客户端或容器卷管理。
---

# wsl-drvfs-mount

把「Windows 侧已可访问」的盘或共享挂进 WSL 2，并在需要时持久化。沉淀自 2026-10-13 实战（`\\10.16.11.3\ai` 经 S: 映射挂入 openKylin-3.0，fstab 冷启动实证）与同日 OKF 教程束。

环境基线（2026-10-13 本机实测）：Windows 受管环境，PowerShell 7+，默认发行版 openKylin-3.0（WSL 2，systemd=true）。

## 0. 边界（先判断该不该用本技能）

- **适用**：WSL 2 访问 Windows 本地盘符、`\\server\share` 网络共享、无盘符 NTFS 文件夹卷；手动挂载或 fstab 持久化。
- **不适用，改走对应路径**：
  - 物理磁盘/U 盘/裸盘直通 → `wsl --mount <DiskPath>`（WSL 2.0.14+），不是 drvfs；
  - WSL 内主动访问 Windows 侧**无凭据**的共享 → 先在 Windows 侧建会话（见 §3 凭据分支），或改用内核态 `cifs`（自行承担工具安装与凭据管理）；
  - NFS / 对象存储 / FTP → 对应客户端，drvfs 只桥接 Windows 文件系统语义；
  - 容器内卷 → Docker/podman 卷编排，本技能只到发行版挂载点；
  - WSL 1、纯 Linux 虚拟机 → 无 interop/drvfs 桥，不适用。
- 与既有技能分工：`wsl-vhdx-compact-cmd`（磁盘压缩）、`wsl-ops-cmd`（Docker 自启/GPU/缓存等主机层运维）、`compose-overlay-ops`（podman-compose 工作负载）互不重叠。

## 1. 环境冻结（受管 Windows 铁律）

禁止假设 PATH。本机实测裸名 `net.exe`/`git` 可能不可识别，全程使用：

- `$wsl = "$env:WINDIR\System32\wsl.exe"`；`$net = "$env:WINDIR\System32\net.exe"`；
- git 固定 `D:\Program Files\Git\mingw64\bin\git.exe`（或会话前 `$env:PATH` 前置其 bin）；
- 调用 wsl 前 `$env:WSL_UTF8=1` 消除中文/UTF-16 乱码；
- WSL 内系统类命令前 `export LC_ALL=C LANGUAGE=C`（openKylin 默认 zh_CN.UTF-8，输出会被翻译）；
- 具体命令签名与预期输出见 [references/command-map.md](references/command-map.md)。

## 2. R · 只读探测（挂载前四连，零写入）

按序执行，任一不满足先停下处理，禁止直接 mount 试错：

1. **WSL 形态**：`wsl -l -v` —— 确认目标发行版存在、VERSION 2、状态。
2. **网络可达**（仅网络共享）：TCP 连 `<server>:445`（3 秒超时）+ ICMP。445 不通是网络/防火墙问题，不是挂载问题。
3. **既有会话探测（最关键）**：`net.exe view \\<server>` 与 `net.exe use`：
   - 看到共享行 **`Used as <盘符>:`** → Windows 侧认证早已闭合，走盘符路径（最省）；
   - 列出了共享但无盘符 → UNC 直挂（凭据可能仍由登录会话提供）；
   - 返回凭据/拒绝错误 → 进入 §3 凭据分支。
4. **挂载点查重**：WSL 内 `mount | grep <point>` 与 `grep <point> /etc/fstab`，防止重复挂载/重复写配置。

> 探测阶段不安装软件、不改 WSL 内任何文件。

## 3. I · 源形态与凭据决策

| 情况 | 源写法 | 说明 |
|---|---|---|
| 有**持久**盘符映射、单机自用 | `S:` | 最短；桌面会话登录后映射就绪 |
| 无映射盘 / 写给他人复现 / 要可移植 | `'\\server\share'` | **必须单引号**防反斜杠转义 |
| 无盘符 NTFS 文件夹卷 | `'C:\mountpoint'` | 必须是 NTFS 挂载点卷；普通目录用 bind mount |

凭据分支（仅探测要求认证时）：凭据边界在 **Windows 侧**，drvfs 不接受任意凭据。先在 Windows 侧闭合：

```powershell
net.exe use \\server\share /user:<域或主机>\<用户名> *   # * 表示交互输入，不留明文
```

也可经文件资源管理器以「记住凭据」登录一次，或用 Credential Manager。WSL 内可经 interop 直接调用 `net.exe`。闭合后回到正常挂载。

## 4. F · 第一性原理（三条，决策依据）

1. **drvfs 是 WSL init 的用户态 9p 桥，不是内核文件系统**：它复用 Windows 的盘符、共享会话与凭据；因此源是「Windows 路径名」，凭据要在 Windows 侧解决，`findmnt` 等内核块层工具天然看不懂它。
2. **网络文件系统的错误延迟到首次 I/O**：mount 退出 0 只证明「请求被接受」，不证明内容可访问；完成判据必须来自三层独立证据。
3. **持久化的风险面在下次启动**：fstab 是启动期配置，任何不可用源都可能拖垮启动；写配置的纪律（nofail/守卫/备份）与终审方式（冷启动实证）都由这一点推出。

## 5. A · 标准作业

### 5.1 手动挂载 + 三段验证（不可裁剪）

```bash
sudo mkdir -p /mnt/ai
sudo mount -t drvfs S: /mnt/ai        # 或 UNC 形态：'\\10.16.11.3\ai'（单引号）
```

1. **挂载表层**：`mount | grep /mnt/ai` 出现 `type 9p (aname=drvfs;...)`；
2. **内容层（硬闸口）**：`ls /mnt/ai | wc -l` 结果 **> 0**。为 0 即失败：查映射是否断开（`net use` 状态）、改 UNC 直挂重试，不得带着空目录继续；
3. **写入层**：切换到**实际业务用户**（不要用 root 代替），写非空内容并读回：
   ```bash
   id -un                                          # 确认是业务用户
   echo probe-$(date +%s) > /mnt/ai/.probe && cat /mnt/ai/.probe && rm /mnt/ai/.probe
   ```
   只读共享：改为读一个已知文件，并在交付说明中记录只读预期。

卸载：`sudo umount /mnt/ai`。

### 5.2 幂等持久化（备份 → 守卫 → nofail → 显式开关）

WSL 内单次 root 调用完成（拆成「构造内容 + 特权追加」，不依赖 `sudo tee` 管道是否可用）：

```bash
sudo cp /etc/fstab /etc/fstab.bak.$(date +%Y%m%d)
sudo cp /etc/wsl.conf /etc/wsl.conf.bak.$(date +%Y%m%d)
grep -qE '^S:[[:space:]]+/mnt/ai[[:space:]]+drvfs' /etc/fstab \
  || echo 'S: /mnt/ai drvfs defaults,nofail 0 0' | sudo tee -a /etc/fstab
grep -q '\[automount\]' /etc/wsl.conf \
  || printf '\n[automount]\nenabled=true\nmountFsTab=true\n' | sudo tee -a /etc/wsl.conf
```

- **`nofail` 不可省略**：映射未就绪时发行版照常启动（挂载点为空目录），事后 `sudo mount -a` 补挂；
- `[automount] mountFsTab=true` 现代 WSL 本就是默认值，显式写入只为消除默认值依赖；
- UNC 形态 fstab 行：`'\\server\share' /mnt/ai drvfs defaults,nofail 0 0`（fstab 中单引号同样需要）；
- 备份文件稳定运行约一个月后删除，勿长期残留 /etc。

### 5.3 静态校验：只认两行计数

```bash
findmnt --verify --verbose
```

通过判据：**`0 parse errors, 0 errors`**。drvfs 源必然产生这些 warning，属已知抽象层噪音，不处理：

- `unreachable source: S:` / 源路径 `No such file or directory`；
- `drvfs seems unsupported by the current kernel`；
- `cannot detect on-disk filesystem type`。

出现这三类之外的 warning/任何 error 必须排查；systemd 「uses the old version」提示可 `systemctl daemon-reload` 消除。

### 5.4 冷启动实证（持久化唯一终审）

PowerShell 侧：

```powershell
wsl --terminate <distro>      # 彻底销毁 VM；不要用 reboot 或重启 Windows 代替
wsl -d <distro> -- bash -lc "mount | grep -E '/mnt/(ai|c|d)'; ls /mnt/ai | wc -l; id -un; echo x > /mnt/ai/.p && cat /mnt/ai/.p && rm /mnt/ai/.p"
```

验收：自动挂载条目在、条目数 >0、业务用户写读回成功、`/mnt/c` `/mnt/d` 等既有挂载无回归。

## 6. V · 交付前验证清单

- [ ] 有只读探测留痕（445、net view/net use、查重）
- [ ] 源形态选择有依据（盘符持久映射 vs UNC 可移植）
- [ ] 三层证据齐全，内容层条目数 >0，写探针为业务用户非空写读回
- [ ] fstab 行含 nofail；写入有 grep 守卫与备份；无重复行
- [ ] findmnt 两行计数为 0/0，警告逐条归类完毕
- [ ] terminate 冷启动后自动挂载 + 既有挂载回归均通过
- [ ] 全程无凭据明文落盘；系统文件改动已告知用户（位于 ext4.vhdx 内，不进主仓库 git）

## 7. 反模式

1. 上来就在 WSL 侧找凭据方案（装 cifs-utils、研究密码选项）——先探测 Windows 既有会话。
2. mount 退出 0 即宣布完成——网络 drvfs 延迟报错、断开映射呈现空目录。
3. fstab 不加 nofail、重复执行不加守卫——启动被拖垮、配置出现重复行。
4. 试图消除 findmnt 对 drvfs 的全部警告——迎合块设备校验器只会改坏可用配置。
5. 用 reboot 或重启 Windows 代替 `wsl --terminate <distro>` 验证——副作用面不同，且不是最小验证。
6. 把网络 drvfs 当 POSIX 文件系统（常显 0777、大小写不敏感、符号链接受限）——SSH 私钥、git 仓库、依赖权限位的运行时留在发行版原生文件系统。

## 8. Gotchas

- 受管 PowerShell 中 `net` 可能解析成 `net` 命令的同名冲突或裸名缺失，一律用 `$env:WINDIR\System32\net.exe` 全路径。
- UNC 路径在 bash 中必须单引号；不写引号需把每个反斜杠双写。
- `git-commit-utf8.py` 传**目录**参数会因暂存区展开比对不一致而 FAIL：先显式 `git add <files>`，再让工具走「已暂存直接提交」分支（提交含中文信息时）。
- WSL 内挂载点目录权限（如 777）不代表共享实际权限；权限以 Windows/ Samba 侧 ACL 为准。
- 网络 drvfs 挂载选项无 uid/gid 映射，root 写成功不能推出业务用户可写——这是 §5.1 第三层必须换用户的原因。
- 环境漂移信号（出现即重验本 SOP）：WSL 大版本变更、systemd 关闭、发行版迁移、映射盘改 GPO 下发、`wsl --mount` 能力覆盖目标场景。

## 9. 参考

- [references/command-map.md](references/command-map.md) —— Windows 侧/WSL 侧命令签名、预期输出与判据速查
- OKF 教程：`docs/knowledge/tech/wsl-drvfs-mount-wiki/`（2017 原始改进 + 现代 WSL 演进对照）
- 模式卡：`docs/retrospective/patterns/methodology-patterns/tools-automation/wsl-network-share-drvfs-mount.md`（WSL-DRVFS-MOUNT-001，L1-draft）
- 复盘：`docs/retrospective/reports/concepts/milestone/wsl-drvfs-mount-wiki-milestone-20261013.md`
