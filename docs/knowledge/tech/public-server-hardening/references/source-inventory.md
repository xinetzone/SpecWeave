# 附录 A：信源台账（S01–S12）

> 本教程的事实来源分两级：一级为本 SpecWeave 方法论会话的分析产出（内部派生），二级为公开权威安全基线与官方文档（交叉核验）。核验日期：**2026-09-30**。

## A.1 内部派生信源

| 键 | 信源 | 位置 | 支撑内容 |
|---|---|---|---|
| S01 | 风险证伪分析（场景2，F→V→I） | 方法论会话 `sc-20260929-ip-exposure-risk`（d:\AI 工作区） | IP 第一性原理拆解、入侵链三要素、场景分级、隐私维度 |
| S02 | 公网服务器加固清单与非技术摘要 | 同会话后续两轮产出 | P0–P2 分层加固操作、管理者执行摘要与注意事项 |

## A.2 公开权威基线（交叉核验）

| 键 | 信源 | URL | 核验方式 | 支撑内容 |
|---|---|---|---|---|
| S03 | Red Hat RHEL 10 Securing networks（OpenSSH 章） | https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/securing_networks/ | WebSearch + 官方文档 | 密钥为唯一认证方式、`PasswordAuthentication no`、限制用户/IP、jumphost |
| S04 | CIS Benchmarks | https://www.cisecurity.org/cis-benchmarks/ | 公开基线对照 | 服务最小化、审计、补丁、加固项组织方式 |
| S05 | NIST SP 800-123 Guide to General Server Security | https://csrc.nist.gov/publications/detail/sp/800-123/final | 公开基线对照 | 服务器安全管理总体原则 |
| S06 | OWASP Cheat Sheet Series | https://cheatsheetseries.owasp.org/ | 公开基线对照 | 传输层、安全响应头、应用层防护 |
| S07 | Mozilla SSL Configuration Generator | https://ssl-config.mozilla.org/ | 官方工具 | TLS 协议版本与套件配置生成 |
| S08 | fail2ban 官方文档与 wiki | https://github.com/fail2ban/fail2ban/wiki | 官方文档 | jail 配置、封禁参数 |
| S09 | Let's Encrypt 与 Certbot 文档 | https://letsencrypt.org/docs/ ；https://certbot.eff.org/docs/ | 官方文档 | 免费证书签发、自动续期 |
| S10 | Ubuntu UFW 文档 / Debian Securing 文档 | https://help.ubuntu.com/community/UFW | 官方社区文档 | ufw 规则语法与默认策略 |
| S11 | unattended-upgrades 手册 | `man unattended-upgrade`；Debian 包文档 | 手册核对 | 命令名单数/包名复数、dry-run 参数 |
| S12 | Docker security 文档 | https://docs.docker.com/engine/security/ | 官方文档 | privileged、docker.sock、非 root 运行、端口发布与 iptables |

## A.3 信源使用说明

- 本教程的命令示例为通用稳定语法，具体软件版本（OpenSSH、Nginx、Docker 等）迭代后参数可能调整，执行前应以所用系统的 `man` 手册与上述官方文档的当前版本为准；
- 云平台的安全组、弹性 IP、对象存储等控制台操作以各云服务商当时文档为准，本教程不绑定特定厂商界面；
- 未在公网可验证的本机实测内容，本教程不做"已实测"标注；全部加固步骤的实操验证状态见[对抗审查记录](adversarial-review.md)的局限登记。
