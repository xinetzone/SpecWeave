# WSL 3.0 podman machine cgroup pids 委托缺失修复手册

> 配合 [../SKILL.md](../SKILL.md) §7.3 使用。SKILL.md 只保留判据与决策摘要；
> 本文承载源码级根因、完整修复/冷启动/验证/回滚命令与操作手法。
> 实证基线：Windows 11 + WSL 3.0.3.0（2026-09-29 基线为 2.9.3，无此问题）+ podman 5.8.1/5.8.2 + Fedora CoreOS machine 镜像，日期 2026-10-14。

## 1. 现象与四条件判据

故障表现：任意普通 rootless 容器（含 `hello-world`）都无法启动，报：

```
crun: controller 'pids' is not available under
/sys/fs/cgroup/non-systemd/user.slice/user-1000.slice/user@1000.service/.../cgroup.controllers
```

关键特征是 cgroup 路径中的 **`non-systemd`** 子树。以下四条全部满足才是本故障，任一不满足回 SKILL.md §7.2（普通 WARN 分诊），禁止动 wsl.conf：

1. 宿主 `wsl --version` 为 **3.0.x**
2. 任意普通容器报上述 `non-systemd` 路径的 crun pids 错误（不是 WARN，是直接失败）
3. `podman run --rm --cgroups=disabled <镜像> echo ok` **能成功**——证明存储/镜像/overlay 完好，纯 cgroup 委托问题
4. machine 内 `cat /proc/1/cgroup` 形如 `0::/non-systemd/init.scope`，且 `cat /sys/fs/cgroup/non-systemd/cgroup.controllers` 为空

## 2. 源码级根因（取证记录，勿再走内部委托弯路）

- podman machine 设计上**不使用 WSL 原生 systemd**：`/etc/wsl.conf` 原本只有 `[user]`；start 时执行 `/root/bootstrap`，用 `unshare --fork --pid --mount --mount-proc ... /lib/systemd/systemd` 在嵌套命名空间手搓 systemd。WSL 3.0 把该命名空间挂到 `/non-systemd` 子树
- `/non-systemd` 层内有 **9 个跨 PID 命名空间的 WSL 基础设施进程**——在该发行版视角里 `cgroup.procs` 只显示为 `0`，不可见、不可杀、不可迁移。cgroup v2 规则：父 cgroup 的 `cgroup.procs` 非空时写 `cgroup.subtree_control` 必返回 **EBUSY**。逐级 `echo +pids` 的委托脚本是死路
- 根级旁路 cgroup（`mkdir /sys/fs/cgroup/podmanfix` + 委托 + chown 用户）同样不可行：rootless 进程跨 cgroup 子树迁移时，内核要求对"源/目标最近公共祖先"（此处即根 cgroup，root 所有）的 `cgroup.procs` 有写权限，必返回 **EPERM**。这是内核规则而非文件权限问题，chmod/chown 无解
- 禁止重启 machine 内 `user@1000.service` / `user.slice` "补委托"——实测会终止整个 WSL VM

## 3. 修复：两步缺一不可（machine 内以 root 执行）

步骤 1 让 PID1 变回 WSL 原生 systemd（cgroup 回到根 `/init.scope`，cpu/io/memory/pids 自动委托）；步骤 2 是 podman 5.8.x 客户端兼容补丁，缺了它 `podman machine start` 会在约 30~50s 后误报 `ssh error: machine not in running state`——实例实际 Running、gvproxy API 实际可用、手动密钥 SSH 也正常，纯粹是客户端就绪探针失配。

探针源码依据：podman `pkg/machine/wsl/declares.go`（v5.8.1）常量 `sysdpid` 为字面量命令 `ps -eo cmd,pid | grep -m 1 ^/lib/systemd/systemd | awk '{print $2}'`。WSL3 经 `/sbin/init`（指向 `../lib/systemd/systemd` 的符号链接）拉起 PID1 时 argv[0] 保持 `/sbin/init`，grep 失配。

```bash
# 步骤 1：启用 WSL 原生 systemd
sudo cp /etc/wsl.conf /etc/wsl.conf.bak-cgroup
printf '[boot]\nsystemd=true\n[user]\ndefault=user\n' | sudo tee /etc/wsl.conf

# 步骤 2：/sbin/init argv[0] 修正 shim
sudo cp -a /sbin/init /sbin/init.orig-symlink   # 备份原符号链接
sudo rm /sbin/init
printf '#!/bin/sh\n# WSL3/podman-5.8.x compat: force argv[0]=/lib/systemd/systemd for readiness probe\nexec -a /lib/systemd/systemd /usr/lib/systemd/systemd "$@"\n' | sudo tee /sbin/init
sudo chmod 755 /sbin/init
```

## 4. Windows 侧冷启动（PowerShell）

PATH 必须前置 System32 与 OpenSSH（本机用户 PATH 被裁剪，不加前置会找不到 wsl/ssh）：

```powershell
$env:PATH = "$env:WINDIR\System32\OpenSSH;$env:WINDIR\System32;$env:WINDIR;$env:PATH"
$env:WSL_UTF8 = '1'
& "$env:WINDIR\System32\wsl.exe" --shutdown
Start-Sleep 8
& 'C:\Program Files\RedHat\podman\podman.exe' machine start podman-machine-default   # 实测 11~15s 成功
```

## 5. 验证清单（逐项过）

```bash
cat /proc/1/cmdline | tr '\0' ' '                  # 期望: /lib/systemd/systemd
cat /proc/1/cgroup                                  # 期望: 0::/init.scope（不再有 non-systemd）
cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/cgroup.controllers
# 期望: cpu io memory pids
podman run --rm --pids-limit=42 docker.io/library/ubuntu:26.04 echo ok
# 宿主侧实证限制真的下发（容器内 /sys/fs/cgroup/pids.max 是命名空间视图，可能显示 max，不足为据）:
cid=$(podman run -d --pids-limit=42 docker.io/library/ubuntu:26.04 sleep 300)
cat /sys/fs/cgroup$(podman inspect -f '{{.State.CgroupPath}}' $cid)/pids.max           # 期望: 42
podman rm -f $cid >/dev/null
systemctl --user --failed --no-legend               # 期望: 无输出（podman-mnt-bindings 竞态失败应消失）
```

Windows 侧全链路：`podman machine ssh ... echo ok` 与 `podman -c podman-machine-default run ...` 均成功；带端口的容器（如 nginx）经 `http://127.0.0.1:<port>/` 在 Windows 浏览器拿到 HTTP 200（实测 896 字节响应）。

排障观察纪律：`wsl --terminate <distro>` 在 WSL3 原生 systemd 下可能不重启 systemd（`journalctl --list-boots` 的 boot id 不变），以 `/proc/1/cmdline` 与 boot 列表为准，勿信单次 `wsl -l -v` 的瞬时状态；machine 空闲约 60s 被 vmIdleTimeout 回收是正常现象，重新 start 即可。

## 6. 回滚（恢复 #28341 常规形态）

```bash
sudo rm /sbin/init && sudo ln -s ../lib/systemd/systemd /sbin/init
sudo mv /etc/wsl.conf.bak-cgroup /etc/wsl.conf
# 然后宿主 wsl --shutdown
```

## 7. 持久性注意与降级退路

- `podman machine rm` / `podman machine init` 重建实例会同时抹掉两步——重建后必须重做
- podman 升级到已修正就绪探针的版本后，可评估只保留步骤 1、把 `/sbin/init` 还原为符号链接（步骤 2 仅为兼容 argv[0] 硬匹配）
- 退路 A（功能降级，非修复）：`~/.config/containers/containers.conf` 写 `[containers]` + `cgroups = "disabled"` 可立刻恢复容器运行，但 `--pids-limit`/内存限制与统计被静默忽略
- 退路 B：`podman machine set --rootful` 会切换语义且 root 镜像存储为空（需 `podman save | sudo podman load` 迁镜像），与 rootless 叠加栈 SOP 冲突。两者均非首选

## 8. PowerShell→guest 操作手法

PowerShell 经 wsl/ssh 传多行脚本必然踩引号与 `$` 转义（`ForEach-Object` 不能作管道起始；here-string 拼接 `` `n `` 易解析错）。复杂 guest 探针统一 base64 传参：

```powershell
$env:PATH = "$env:WINDIR\System32\OpenSSH;$env:WINDIR\System32;$env:WINDIR;$env:PATH"
$env:WSL_UTF8 = '1'
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($probe))
& "$env:WINDIR\System32\wsl.exe" -d podman-machine-default -u root bash -lc "echo $b64 | base64 -d | bash"
```

远程会话读环境变量用 `printenv`，不要在双引号里写 `$VAR`——SSH 外层 shell 会提前展开为空，制造"变量没注入"的测量假象。
