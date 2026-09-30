# 04 补丁管理与源站隐藏：持续修补 + 让真实地址不可直达

> 本文处理两类问题：脆弱性的持续修补（补丁）与真实 IP 已暴露这一既定事实的处置（CDN 隔离、泄露处置、抗拒绝服务）。

## 4.1 及时修补与自动安全更新

```bash
# 手动更新（Debian/Ubuntu）
sudo apt update && sudo apt upgrade -y

# RHEL 系
sudo dnf upgrade --security
```

配置自动安装安全更新：

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

可检查 `/etc/apt/apt.conf.d/20auto-upgrades` 确认包含：

```ini
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```

运维要点：

- 订阅发行版与关键软件（Nginx、OpenSSL、OpenSSH、Docker）的安全公告；
- 内核更新后安排重启；可安装 `needrestart` 检查需要重启的服务；
- 大版本升级前先在测试环境验证，并确认有可回滚的备份。

## 4.2 CDN/WAF 前置与回源锁定

仅接入 CDN 但不限制回源，攻击者可绕过 CDN 直达源站（"CDN 裸奔"反模式）。完整配置分三步：

1. **接入 CDN/WAF**（Web 应用防火墙，WAF，工作在应用层做攻击特征拦截）：域名解析指向 CDN 提供的 CNAME 或节点地址，对外只暴露 CDN 节点 IP；
2. **锁定回源来源**：在云安全组与主机防火墙中，仅允许 CDN/WAF 公布的回源 IP 地址段访问 80/443 端口，拒绝其他一切来源；
3. **回源链路加密**：源站同样配置有效证书，CDN 到源站使用 HTTPS 回源。

Nginx 层可进一步只接受带 CDN 标识的请求；具体规则以所用 CDN 厂商的回源 IP 列表与文档为准。

## 4.3 真实 IP 泄露渠道与处置

真实源站 IP 的常见公开获取渠道包括：历史 DNS 解析记录、邮件头信息（如站点同时用本域发信）、证书透明日志、子域名直接解析、早期未接 CDN 时的扫描存档。

处置建议：

- 核查 `mail`、`直接IP访问`、子域名解析等旁路；发信服务使用独立邮件服务商；
- 若历史泄露面较大，最彻底的办法是**更换服务器公网 IP**（云平台可申请弹性 IP 重新绑定），随后再上线 CDN；
- 对直接使用 IP 访问的请求在 Web 服务层直接拒绝（默认虚拟主机返回 444/403）。

## 4.4 拒绝服务防护

- 基础层：云厂商默认提供的 DDoS 基础防护、[02 篇](02-exposure-survey-and-firewall.md)中的 SYN Cookies 与内核参数；
- 进阶层：业务面向公众的服务器接入带清洗能力的 CDN/高防 IP，攻击流量在清洗节点被拦截而不直达源站；
- 可用性预案：准备弹性 IP 切换、限流降级的操作手册，并确认服务带宽与连接数上限。

## 4.5 验收标准

- `sudo unattended-upgrade --dry-run -v`（注意：包名为复数 unattended-upgrades，可执行命令为单数 unattended-upgrade）或检查 `/var/log/unattended-upgrades/` 日志，确认安全更新机制运行；
- 直接访问源站真实 IP 的 80/443 被拒绝，仅 CDN 回源地址段可访问；
- 域名对外解析结果为 CDN 地址；
- 历史泄露渠道完成排查并有记录。

> 上一篇：[03 SSH 加固与暴力破解防御](03-ssh-and-brute-force-defense.md) ｜ 下一篇：[05 Web 服务加固](05-web-service-hardening.md)
