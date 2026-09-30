# 附录 B：V 阶段对抗审查记录

> 审查对象：`docs/knowledge/tech/public-server-hardening/` 初稿（index + concepts 索引 1 + 概念页 8 + references 1 初稿；本文件为审查产物）。
> 审查时点：2026-09-30，session `sc-20260930-public-server-hardening`。
> 方法：四视角独立提审 → 意见编号 O1–O7 → 逐条裁定（采纳/登记）→ 修正 → 回归确认。

## B.1 四视角与意见清单

### 视角一：魔鬼代言人（质疑事实与推断强度）

**O1｜WAF 术语在正文中未展开解释**
concepts/04 §4.2 首次出现 "CDN/WAF" 时直接使用缩写，新人读者无法区分 CDN 与 WAF 各自功能；05 篇同样直接使用。术语首次出现缺少定义。
**裁定：采纳。**

**O2｜自动更新验收命令名写错**
concepts/04 §4.5 初稿写 `unattended-upgrades --dry-run`。实际 Debian/Ubuntu 中包名为 `unattended-upgrades`（复数），可执行命令为 `unattended-upgrade`（单数），照初稿执行会得到 command not found。经手册（S11）核对为确定性错误。
**裁定：采纳。**

**O3｜缺少后量子密钥交换提示**
2026 年的加固资料普遍提到 `sntrup761x25519-sha512` 混合密钥交换，新版 OpenSSH 已默认启用；教程若未提示，读者手工硬编码 `KexAlgorithms` 白名单时可能将其移除而不自知。
**裁定：采纳。**

### 视角二：新人（能否照着完成操作）

**O4｜RHEL 防火墙示例缺少防锁提醒**
concepts/02 firewalld 段直接给出默认 zone 改 drop 再 reload 的流程，没有像 SSH 章节那样提示保留会话与确认带外通道；RHEL 系读者按顺序操作时风险与改 sshd 相同。
**裁定：采纳。**

**O5｜socket activation 改端口时三处配置不同步**
concepts/03 §3.3 给出 socket 覆盖方法，但初稿未说明 `ListenStream`、sshd 的 `Port`、fail2ban 的 `port` 与防火墙放行规则之间须保持一致；端口对不上时故障点不直观。
**裁定：采纳。**

### 视角三：老板/决策者（结论边界与成本）

**O6｜IPv6 隐私扩展的适用对象表述含混**
concepts/01 §1.4 初稿写"防护重心转向主机防火墙与隐私扩展地址"，可能被误解为 IPv6 服务器也应启用随机化扩展地址。隐私扩展（RFC 8981）适用于出站客户端；服务器需要固定地址供 DNS 与访问定位。
**裁定：采纳。**

### 视角四：未来维护者（时效与可验证性）

**O7｜全部步骤未在 RHEL 与具体云环境实测**
教程命令以 Debian/Ubuntu 口径为主，未逐环境实操；软件版本与云控制台随时间变化。该局限无法在本次审查中通过修文消除。
**裁定：登记为局限。** 已写入 index.md 局限声明 ①②③，信源台账 A.3 同步说明。

## B.2 裁定与回归确认表

| 编号 | 视角 | 问题 | 裁定 | 修正位置 | 回归确认 |
|---|---|---|---|---|---|
| O1 | 魔鬼 | WAF 未解释 | 采纳 | concepts/04 §4.2 首次出现处补"Web 应用防火墙，WAF，工作在应用层做攻击特征拦截" | ✅ 缩写与功能同屏可见 |
| O2 | 魔鬼 | `unattended-upgrades --dry-run` 命令名错误 | 采纳 | concepts/04 §4.5 改为 `sudo unattended-upgrade --dry-run -v`，并注明包名/命令名单复数差异与日志路径 | ✅ 与 S11 手册一致 |
| O3 | 魔鬼 | 缺后量子 KEX 提示 | 采纳 | concepts/03 §3.2 新增提示块（默认含 sntrup761x25519，硬编码白名单须保留） | ✅ 提示与默认行为一致 |
| O4 | 新人 | firewalld 无防锁提醒 | 采纳 | concepts/02 RHEL 段后新增引用 03 §3.0 的防锁规则，说明 reload 不中断已有连接 | ✅ 两类系统操作安全要求对齐 |
| O5 | 新人 | socket activation 配置同步点缺失 | 采纳 | concepts/03 §3.3 新增同步说明（ListenStream/Port/fail2ban port/防火墙） | ✅ 四处配置点位列明 |
| O6 | 老板 | IPv6 隐私扩展适用对象含混 | 采纳 | concepts/01 §1.4 改为"客户端用隐私扩展、服务器配静态地址" | ✅ 与 RFC 8981 适用场景一致 |
| O7 | 未来 | 跨环境未实测 | 登记局限 | index.md 局限声明 + source-inventory.md A.3 | ✅ 边界显式可见 |

合计：意见 **7** 条；采纳并修正 **6** 条（O1–O6）；登记局限 **1** 条（O7）。

## B.3 机械回归（链接与命名）

修正后对全部文件执行机械审计：

1. 逐页核对"上一篇/下一篇"与正文内相对链接：concepts/01→index、02→01、03→02、04→03、05→04、06→05、07→06、08→07 及 `../index.md`，目标文件全部存在；
2. index.md 快速导航中 10 个链接（8 概念页 + 2 参考页）与文件实际路径逐一对应；
3. 相对路径层级核对：`concepts/*.md` → 主教程用 `../index.md`、→ references 用 `../references/...`；`references/*.md` → 主教程用 `../index.md`、→ 概念页用 `../concepts/...`；
4. 文件名规范与断链最终以仓库脚本判定：`check-filename-convention.py` 与 `check-links.py --path docs/knowledge/tech/public-server-hardening`（结果回填 index.md G4）。

## B.4 V 门结论

| 标准 | 要求 | 实际 | 结果 |
|---|---|---|---|
| 视角覆盖 | 4 视角 | 4/4 | ✅ |
| 意见数量 | ≥5 且具体可定位 | 7 条，均给出文件、章节与错误文本 | ✅ |
| 采纳修正 | ≥2 并回归 | 6 条采纳、逐文件修正并回归确认 | ✅ |
| 数字自洽 | 与 index §4/§5 声明一致 | 7 意见 / 6 采纳 / 1 局限，两处一致 | ✅ |

**V 门：通过。** 审查未推翻 R 阶段任何事实编号与 I 阶段洞察；确定性错误一处（O2 命令名），已修正并经手册复核。
