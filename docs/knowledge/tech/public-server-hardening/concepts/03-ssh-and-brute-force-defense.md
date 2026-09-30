# 03 SSH 加固与暴力破解防御：收益最高的一项

> SSH 是公网服务器的管理入口，也是自动化扫描与暴力破解的首要目标。本文覆盖密钥认证、服务端加固、两个现代系统陷阱（配置目录与 socket activation）以及 fail2ban 自动封禁。

## 3.0 安全前置（防止把自己锁在门外）

1. **保留当前已登录的 SSH 会话不要关闭**，另开新终端验证新配置可登录，确认后再退出旧会话；
2. 确认可使用云厂商提供的网页控制台/VNC（带外管理通道），它是 SSH 配置出错时的兜底入口；
3. 每一步修改后先做语法检查再应用：`sudo sshd -t`。

## 3.1 改用密钥认证

在本地管理机生成密钥对（ed25519 为当前推荐类型）：

```bash
ssh-keygen -t ed25519 -C "server-admin"
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@服务器IP
```

若服务器使用非默认端口：`ssh-copy-id -p <端口> ...`。上传后先验证密钥可正常登录，再进行下一步。

## 3.2 服务端加固项

现代 Debian/Ubuntu 支持 drop-in 配置目录，推荐新建 `/etc/ssh/sshd_config.d/99-hardening.conf`（避免直接改主配置文件；旧系统直接编辑 `/etc/ssh/sshd_config`）：

```ini
PermitRootLogin no                  # 禁止 root 直接登录
PasswordAuthentication no           # 禁用密码认证（确认密钥可用后再设置）
PubkeyAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30
AllowUsers yourname                 # 仅允许指定用户
X11Forwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
```

应用配置：

```bash
sudo sshd -t && sudo systemctl reload ssh     # RHEL 系服务名为 sshd
# 新开终端验证密钥登录成功后，再关闭旧会话
```

日常管理使用普通用户配合 `sudo` 提权；`AllowUsers` 按实际登录用户填写。

> **后量子密钥交换提示**：新版 OpenSSH 的默认密钥交换算法已包含 `sntrup761x25519-sha512`（抗"先截获、后解密"威胁的混合算法）。若手工设置 `KexAlgorithms` 白名单，应保留该算法，避免因硬编码列表使其被意外移除。

> **过渡建议**：单人维护且私钥托管稳妥时可直接禁用密码；若团队尚无密钥管理流程，可先保留密码认证一到两周并同步部署 fail2ban，完成全员密钥切换后再禁用。

## 3.3 两个现代系统陷阱

1. **配置优先级**：`sshd_config.d/` 中的文件按字典序加载，文件名以 `99-` 开头可确保覆盖默认值；修改后用 `sudo sshd -T | grep -i passwordauthentication` 确认实际生效值。
2. **systemd socket activation**：Ubuntu 22.04 及更新版本中 SSH 端口可能由 `ssh.socket` 单元接管监听。若修改了 `Port` 却发现端口未变化，需检查并覆盖 socket 配置：

```bash
systemctl status ssh.socket
mkdir -p /etc/systemd/system/ssh.socket.d
printf '[Socket]\nListenStream=\nListenStream=新端口\n' \
  | sudo tee /etc/systemd/system/ssh.socket.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh.socket ssh
```

采用 socket activation 并改过端口时，三处配置须同步：socket 的 `ListenStream`、`sshd_config` 的 `Port`（二者不一致时以 socket 监听为准）、fail2ban `[sshd] jail` 中的 `port`，以及防火墙/安全组的放行规则。

## 3.4 关于修改 SSH 端口

修改默认 22 端口**不提升真实安全性**——端口扫描同样可以发现它，实际作用只是降低日志中的暴力破解噪音。若决定修改，顺序不可颠倒：

1. 先在云安全组与主机防火墙放行新端口；
2. 再修改 `Port`（或 3.3 的 socket 覆盖）；
3. 新终端验证新端口可登录后，再关闭旧端口放行规则。

## 3.5 fail2ban：自动封禁暴力破解

```bash
sudo apt install fail2ban                 # RHEL 系位于 EPEL 仓库
sudo systemctl enable --now fail2ban
```

创建 `/etc/fail2ban/jail.local`：

```ini
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 4
ignoreip = 127.0.0.1/8 ::1 <你的固定管理IP>

[sshd]
enabled = true
port    = 22                # 若改过端口，此处填写实际端口
```

验证：

```bash
sudo fail2ban-client status sshd
```

`ignoreip` 必须加入自己的管理 IP 以避免误封；封禁时间与重试阈值可按管理需要调整。

## 3.6 验收标准

- 不携带密钥尝试 SSH 登录被直接拒绝；
- `sudo sshd -T` 输出中 `permitrootlogin no`、`passwordauthentication no`；
- `fail2ban-client status sshd` 显示 jail 正常运行；
- 错误口令连续尝试超过阈值后来源 IP 被封禁。

> 上一篇：[02 暴露面盘点与防火墙](02-exposure-survey-and-firewall.md) ｜ 下一篇：[04 补丁管理与源站隐藏](04-patching-and-source-hiding.md)
