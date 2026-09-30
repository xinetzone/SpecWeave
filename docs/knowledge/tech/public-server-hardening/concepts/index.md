# 概念页索引（按运维问题域重组）

> 本目录按"先理解风险，再收敛边界、强化认证、维持修补，最后监测兜底"的运维决策路径组织。建议初学者按 01→08 顺序阅读；有明确问题时可直接查阅对应篇章。

| 篇 | 主题 | 核心内容 |
|---|---|---|
| [01 IP 暴露与风险本质](01-ip-exposure-and-risk.md) | IP 的协议定位、入侵链三要素、场景风险分级、IPv6 与隐私维度 |
| [02 暴露面盘点与防火墙](02-exposure-survey-and-firewall.md) | 端口盘点、服务绑定、ufw/安全组双层控制、内核网络参数 |
| [03 SSH 加固与暴力破解防御](03-ssh-and-brute-force-defense.md) | ed25519 密钥、sshd 加固项、socket activation 陷阱、fail2ban |
| [04 补丁管理与源站隐藏](04-patching-and-source-hiding.md) | 自动安全更新、CDN/WAF 回源锁定、IP 泄露处置、抗 DDoS |
| [05 Web 服务加固](05-web-service-hardening.md) | HTTPS、TLS 配置、安全响应头、WAF 与应用层加固 |
| [06 最小权限与隔离](06-least-privilege-and-isolation.md) | 账户权限、文件权限、容器安全、内网/VPC 隔离 |
| [07 监控、备份与韧性](07-monitoring-backup-and-resilience.md) | 集中日志、入侵检测、3-2-1 备份、恢复演练、运维节奏 |
| [08 非技术人员执行摘要](08-executive-briefing.md) | 通俗比喻、六件事、操作红线、验收证明、长期意识 |
