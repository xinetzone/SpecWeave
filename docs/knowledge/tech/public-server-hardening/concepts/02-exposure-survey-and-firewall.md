# 02 暴露面盘点与防火墙：先关门，再谈其他

> 加固的第一步不是安装任何工具，而是搞清"服务器当前对外开了什么"。本文覆盖端口盘点、服务收敛、双层防火墙配置、内核网络参数与外部视角验证。

## 2.1 盘点监听端口

```bash
# 列出所有 TCP 监听端口与对应进程（需要 root 才能看到进程名）
sudo ss -tlnp
```

输出示例（简化）：

```
State   Local Address:Port   Process
LISTEN  0.0.0.0:22           sshd
LISTEN  0.0.0.0:80           nginx
LISTEN  127.0.0.1:3306       mysqld
```

核对方法：

1. 逐行确认每个端口是否必须对公网提供服务；
2. `0.0.0.0:<端口>` 或 `[::]:<端口>` 表示对所有网卡监听，外部可达；`127.0.0.1:<端口>` 仅本机可达；
3. 停用非必要服务：`sudo systemctl disable --now <服务名>`；
4. 数据库（MySQL 3306、PostgreSQL 5432）、缓存（Redis 6379）、消息队列、管理面板等一律绑定 `127.0.0.1`，需要跨机访问时走内网而非公网。

## 2.2 双层防火墙：云安全组 + 主机防火墙

云服务器存在两层访问控制，两者都要按"默认拒绝、最小放行"配置：

- **第一层：云控制台安全组**（在云厂商网页控制台配置，作用于虚拟机外部）；
- **第二层：主机内防火墙**（ufw / firewalld，作用于操作系统）。

### Debian/Ubuntu：ufw

```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp                 # 务必先放行 SSH！
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

### RHEL 系：firewalld

```bash
sudo systemctl enable --now firewalld
sudo firewall-cmd --set-default-zone=drop
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

> 执行防火墙变更同样适用 [03 篇 §3.0](03-ssh-and-brute-force-defense.md) 的防锁规则：保留当前会话、确认云控制台带外通道可用；reload 不会中断已建立的连接，但新入站规则立即生效。

### 管理端口的访问控制

管理类端口（8080 面板、数据库端口、Docker API 等）不直接对公网开放，按以下顺序选择方案：

1. **IP 白名单**：`sudo ufw allow from <你的固定IP> to any port 22`；
2. **VPN 接入**：管理端口仅对 VPN 内网开放；
3. **SSH 隧道**：`ssh -L 8080:127.0.0.1:8080 user@服务器` 后在本机访问。

## 2.3 内核网络参数加固

将以下内容写入 `/etc/sysctl.d/99-hardening.conf`，然后执行 `sudo sysctl --system` 生效：

```ini
# 反向路径过滤，校验源地址
net.ipv4.conf.all.rp_filter = 1
# 拒绝源路由与 ICMP 重定向
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
# 忽略广播 ICMP，开启 SYN Cookies 缓解 SYN 洪水
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.tcp_syncookies = 1
# 内存地址随机化
kernel.randomize_va_space = 2
```

> **环境前提**：在依赖 IPv6 无状态自动配置（SLAAC）获取地址的网络中，不要设置 `accept_ra = 0`，否则可能失去 IPv6 连通性；本文参数清单未包含该项。

## 2.4 外部视角验证

防火墙配置完成后，从另一台机器（或云主机外部网络）验证实际暴露面：

```bash
# 仅可扫描你自己拥有或已获授权的服务器
nmap -sS -Pn -p 1-10000 你的服务器IP
```

预期结果：只显示 22、80、443（以及你有意放行的端口），其余端口状态为 filtered。主机内视角（ss）与外部视角（nmap）结果一致，暴露面盘点才算完成。

> 上一篇：[01 IP 暴露与风险本质](01-ip-exposure-and-risk.md) ｜ 下一篇：[03 SSH 加固与暴力破解防御](03-ssh-and-brute-force-defense.md)
