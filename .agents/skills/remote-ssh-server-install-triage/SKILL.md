---
name: remote-ssh-server-install-triage
version: 1.0.0
description: 'Remote-SSH 远端 IDE server 安装卡在下载环节的诊断与修复门面（Trae CN / VS Code / Cursor 通用）。当用户在 IDE 里连接远端主机时界面长时间停在 "Downloading and installing remote server"、"正在下载并安装远程服务器"、"正在配置 SSH 主机 <ip>"、"Setting up SSH Host"、SOLO 面板一直 Loading、远端文件打不开、所有依赖远端工作区的工具调用全部无响应时，必须使用此技能。适用症状：远端 ~/.trae-cn-server 或 ~/.vscode-server 下的 bin/stable-<commit>-* 目录为 total 0、安装进程 curl/fetch 存活但字节数十分钟不增长、socket 已 ESTABLISHED 却只收到几百字节、wchan=do_poll、.resolve-lock-* 锁目录长期不释放。核心判据是「字节停滞 + 进程存活 + 连接已建立」三条件同时成立；修复主线是精准 kill 卡死的下载子进程、由上安装脚本自动重试并重新解析 DNS 落到健康 CDN 节点，而不是重启客户端、删锁目录或重装 IDE。不用于：SSH 根本连不上（TCP 22 不通 / 认证失败，走 ssh 排障）、server 已启动但扩展报错（走扩展宿主日志）、纯 Skill 逻辑缺陷排查——Skill"卡住"通常只是远端通道未建立的表象，须先定位故障域。'
argument-hint: "<host> [--server-root ~/.trae-cn-server|~/.vscode-server] [--dry-run]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/remote-ssh-server-install-triage/**"
title: Remote-SSH 远端 Server 下载卡死：取证→精准 kill→重试闭环
x-toml-ref: "../../../.meta/toml/.agents/skills/remote-ssh-server-install-triage/SKILL.toml"
---
# remote-ssh-server-install-triage — Remote-SSH 远端 Server 下载卡死诊断与修复

## 1. Skill ID

`remote-ssh-server-install-triage`（诊断 SOP 门面，无外部脚本依赖；捆绑只读取证脚本 [scripts/triage.sh](scripts/triage.sh)）。

> **边界（必遵守）**：本技能只管「SSH 通道已通、远端 server 正在安装、卡在下载环节」这一段。不做 SSH 建连排障（`ssh -v` / 密钥 / 端口，归 ssh 排障）；不做扩展宿主报错分析（归扩展日志）；不做 IDE 客户端自身的更新问题；也不负责判断用户所报的 Skill 是否真有逻辑缺陷——**Skill 卡住是症状，远端通道未建立才是病灶**，本技能只负责把通道打通。

## 2. 功能描述

提供 **2 方案** 支持，按取证结果自动选择：

| 方案 | 推荐场景 | 优势 |
|---|---|---|
| **方案A·精准 kill 触发重试**（⭐默认） | 下载进程存活、socket ESTABLISHED、字节数停滞、`wchan=do_poll` | 零额外依赖；上层安装脚本自带重试，重试会重新解析 DNS，天然换到健康边缘节点；实测 327 MB 主包一次通过 |
| **方案B·异机下载 + 手工解压兜底** | 远端对 CDN 全域不可达、或反复重试都撞同一坏节点 | 绕开远端网络；只需一次性搬一个大文件 |

核心功能：
1. **故障域切换**：先把"Skill 卡了"改写为"远端 server 没装完"，避免在错误方向上花时间；
2. **三条件判定**：字节停滞 + 进程存活 + 连接已建立，三者同时成立才动手，杜绝"凭感觉 kill"；
3. **只读取证优先**：`--dry-run` 模式跑完全部取证、打印修复建议，零副作用；
4. **最小杀伤**：只 kill 下载子进程（curl / fetch），保留安装脚本与已运行的 server；
5. **数值化验收**：目录体积、进程、日志、锁释放四项对账，缺一不算完成。

> **为什么故障域切换要放在第一位？** 真实案例里用户报的是"`seven-concepts-cmd` 一直卡着"，但截图右下角写着「来源：Remote SSH Extension / Downloading and installing remote server」。Skill 的每次工具调用都要走远端工作区通道，通道没建好，任何 Skill 都表现为无响应。若顺着用户措辞去审 Skill 逻辑，方向从一开始就错了。

## 3. 何时触发（触发词 + 强触发条件）

**主触发词**（满足任一项即用）：
- 界面文案：`Downloading and installing remote server`、`正在下载并安装远程服务器`、`正在配置 SSH 主机`、`Setting up SSH Host`、`Installing VS Code Server`、`正在安装 Trae Server`
- 目录特征：`~/.trae-cn-server`、`~/.vscode-server`、`bin/stable-<commit>-debian10`、`bin/stable-<commit>-linux-x64`、`.resolve-lock-`
- 症状描述：`远端连上了但一直 Loading`、`远端文件打不开`、`server 装了半小时`、`SSH 通了但工作区起不来`

**强触发条件**：即使没有上述词，只要用户同时表达"①SSH 能登进去；②IDE 连远端一直转圈"，**就必须先走本技能取证**，不要直接建议重启客户端或重装 IDE。

> **为什么触发条件要写得这么具体？** 这类故障的搜索结果里混着大量无关方案（改 DNS、关防火墙、重装 IDE），共同点是都没有取证。把"目录为空 + 进程存活 + 连接已建立"写成触发条件，等于在入口处就拦住"靠猜"的路径。

## 4. 判定决策树

```
IDE 连远端一直转圈 / 报 Downloading and installing remote server？
├─ TCP 22 通？认证过？ —— ssh <host> 'echo ok'
│   ├─ 否 → 退出本技能（走 ssh 排障）
│   └─ 是 ↓
├─ 远端 server 进程已在跑？ —— ps -eo pid,args | grep server-main
│   ├─ 是 → 不是下载问题，走扩展宿主日志（退出本技能）
│   └─ 否 ↓
├─ 有存活下载进程？ —— ps | grep -E 'curl|fetch'
│   ├─ 否 → 方案B（异机下载兜底）或检查安装脚本是否根本没启动
│   └─ 是 ↓
├─ socket ESTABLISHED 且字节数十秒不增长？ —— ss -tnp + /proc/<pid>/io 两次采样
│   ├─ 字节在涨 → 只是慢，等或看磁盘（df -h ~）；不要 kill
│   └─ 字节停滞 → 方案A：kill -TERM <下载子进程PID>，让安装脚本重试
└─ 重试 2 次仍撞同一坏节点 → 方案B + --resolve 指定健康 IP
```

**写操作前置规则**：方案A 的 `kill` 是唯一的写操作。执行前必须先跑完 §7 的全部只读取证，并把三项判据的实测值摆出来；证据不全不得执行。

> **为什么强调"字节在涨就不要 kill"？** 大文件确实可能慢（实测主包 327 MB，多分片并发）。把"慢"误判成"死"，kill 掉正在正常推进的下载，会让用户白等一轮；反之把"死"当成"慢"，就是本次故障里耗时 10 分钟以上的主要原因。判据必须落到数字上。

## 5. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| host | string | 是 | — | `~/.ssh/config` 里已配置的 Host 别名或 IP，如 `10.16.11.3` |
| server-root | string | 否 | 先探测 `~/.trae-cn-server`，其次 `~/.vscode-server` | Trae CN 用前者，VS Code / Cursor 用后者 |
| dry-run | switch | 否 | false | **只读**：跑完 §7 取证并打印建议，不做任何 kill |
| retry-limit | int | 否 | 2 | 允许重试次数；超过则转方案B |

## 6. 依赖与前置准备

- 本机：`ssh` 客户端，且 `~/.ssh/config` 中该 Host 可免密登录（`ssh <host> 'echo ok'` 直接返回）。
- 远端：`ps`、`ss`、`/proc`、`curl`、`getent` 可用（主流 Linux 发行版默认具备）。
- 权限：远端以登录用户身份操作 `~` 下目录即可，**不需要 sudo**。
- 磁盘：`df -h ~` 剩余空间应大于 2 GB；低于该值先清理旧版本目录再重试。

> **为什么磁盘要单独前置？** 静默下载失败与磁盘写满的现场高度相似（目录同样是 `total 0`）。先看一眼 `df` 只要一秒，却能排除一整类误判。实测案例中磁盘已到 93%，虽非本次根因，但同环境下极易叠加。

## 7. 只读取证（dry-run 预检，零副作用）

以下命令全部只读，建议用捆绑脚本一次性采集：`bash scripts/triage.sh <host>`。手工执行时按序逐项。

### 7.1 故障域与安装根目录

```bash
ssh <host> 'echo ok'                                  # 通道基线
ssh <host> 'ls -d ~/.trae-cn-server ~/.vscode-server 2>/dev/null'
ssh <host> 'df -h ~ | tail -1'                        # 剩余空间
ssh <host> 'du -sh ~/.trae-cn-server 2>/dev/null'     # 安装根体积
```

### 7.2 进程链与锁

```bash
ssh <host> "ps -eo pid,ppid,etime,stat,wchan:24,args | grep -E 'fetch|curl|server-main' | grep -v grep"
ssh <host> 'ls -la ~/.trae-cn-server/ | grep resolve-lock'
ssh <host> 'cat ~/.trae-cn-server/.resolve-lock-*/pid 2>/dev/null'
ssh <host> 'stat -c "%y %n" ~/.trae-cn-server/.resolve-lock-*/heartbeat 2>/dev/null'
```

锁目录内含 `pid` / `resolveId` / `heartbeat` 三件。`heartbeat` 的 mtime 停滞 + `pid` 已不存在 = 陈旧锁；`pid` 存活则说明安装仍在进行。

### 7.3 卡死三判据（核心）

```bash
PID=<下载子进程 PID>
ssh <host> "ss -tnp 2>/dev/null | grep 'pid=$PID'"
ssh <host> "cat /proc/$PID/wchan; echo"
ssh <host> "cat /proc/$PID/io"     # 间隔 10 秒采第二次，比较 rchar 增量
ssh <host> "ls -l /proc/$PID/fd | grep -E 'tar|tmp'"
```

判死条件（三条同时成立）：`ss` 显示 `ESTAB`、两次 `rchar` 增量约等于 0、`wchan` 为 `do_poll` 或同类等待态。实测现场为：ESTABLISHED 到 `221.195.209.14:443`、累计仅 346 字节、`wchan=do_poll`、`etime` 已 10 分 18 秒。

### 7.4 落盘目标是否为空

```bash
ssh <host> 'ls -la ~/.trae-cn-server/bin/'
ssh <host> 'ls -la ~/.trae-cn-server/bin/stable-*-debian10/ | head'
```

`total 0` 说明解压阶段尚未开始。注意：**目录已存在且为空不等于"没在装"**，必须以 §7.2 的进程为准。

### 7.5 CDN 多节点探测（判断是节点问题还是全域不可达）

```bash
ssh <host> 'getent ahostsv4 lf-cdn.trae.com.cn | awk "{print \$1}" | sort -u'
ssh <host> 'curl -sS -I -m 8 -o /dev/null -w "%{http_code} ip=%{remote_ip} t=%{time_total}\n" https://lf-cdn.trae.com.cn/'
```

`lf-cdn.trae.com.cn` 通常解析出十余个 IPv4。实测中一个节点停滞，另一节点 `122.193.246.46` 的 HEAD 返回 200、耗时 0.13 秒——**说明是单边缘节点问题，不是 DNS 或外网整体故障**。

> **为什么不能拿 `baidu.com` 当连通性代表？** 实测远端 `curl https://www.baidu.com` 返回 `000`（内部 DNS 只回不可路由的 AAAA），而 Trae 的真实下载域 `lf-cdn.trae.com.cn` 有正常 A 记录、HEAD 200。用无关域名做连通性判据，会得出"远端没有外网"的错误结论并直接放弃修复。

## 8. 方案A：精准 kill 触发重试（⭐默认）

### 8.1 执行

```bash
# 只 kill 下载子进程，不要 kill 上层 bash 安装脚本，也不要 kill node server-main
ssh <host> 'kill -TERM <下载子进程PID>'
```

上层安装脚本检测到子进程非零退出后会自行重试，重试链路会重新解析 `lf-cdn.trae.com.cn`，从而改落到健康节点。随后自动完成：引导包 `fetch-linux-x64.tar.gz` 下载 → `fetch download` 分片拉取主包 → `tar -xf --strip-components 1` 解压 → `node ./out/server-main` 拉起。

### 8.2 重试后观察（不做任何干预）

```bash
ssh <host> "ps -eo pid,etime,args | grep -E 'fetch|curl|server-main' | grep -v grep"
ssh <host> 'du -sh ~/.trae-cn-server/bin/stable-*-debian10/'
```

正常推进的特征：出现新的 `fetch download` 进程，目标目录体积开始增长（实测主包 327,345,664 字节）。

> **为什么优先 kill 子进程而不是重启 IDE？** 重启客户端只会让安装脚本从头再来，DNS 解析结果未必变化，反而多一轮完整耗时；而且在远端留有半截进程与陈旧锁时，客户端重启还可能叠加互斥冲突。最小杀伤的收益是可观测的。

## 9. 方案B：异机下载 + 手工解压兜底

仅在远端对 CDN 全域不可达、或方案A 重试超过 `retry-limit` 仍撞同一坏节点时使用。

```bash
# 1) 从日志里抓真实下载 URL（含版本号，随客户端更新变化）
ssh <host> 'grep -o "https://lf-cdn\.trae\.com\.cn[^ ]*\.tar\.xz" ~/.trae-cn-server/.stable-*.log | tail -1'

# 2) 在能正常下载的机器上取回，再传到远端
curl -fL -o server.tar.xz '<上一步的 URL>'
scp server.tar.xz <host>:~/

# 3) 在远端解压到与客户端约定一致的版本目录（目录名必须与日志中的 commit 一致）
ssh <host> 'mkdir -p ~/.trae-cn-server/bin/stable-<commit>-debian10 && \
  tar -xf ~/server.tar.xz -C ~/.trae-cn-server/bin/stable-<commit>-debian10 --strip-components 1'

# 4) 回 IDE 重新连接
```

若仍频繁撞坏节点，可在远端临时指定健康 IP（验证用，不写入全局配置）：

```bash
curl -sS -I -m 8 --resolve lf-cdn.trae.com.cn:443:<健康IP> https://lf-cdn.trae.com.cn/
```

> **为什么方案B 只做兜底不做首选？** 手工解压绕过了客户端的 `.token` / `.pid` 写入流程，版本目录名必须与日志中的 commit 精确对齐，错一位客户端就会重新下载一遍。只有当远端网络确实不可用时，这点手工成本才值得付。

## 10. 验收闭环（四项对账，缺一不算完成）

| 项 | 命令 | 通过标准 |
|---|---|---|
| 目录体量 | `du -sh ~/.trae-cn-server/bin/stable-<commit>-debian10/` | 约 1.3 GB，非 `total 0` |
| 关键文件 | `ls ~/.trae-cn-server/bin/stable-<commit>-debian10/` | 含 `ffmpeg`、`ffprobe`、`helpers`、`remote-cli`、`trae-cn-server`（VS Code 为 `bin/code-server`） |
| 进程 | `ps -eo pid,args \| grep server-main` | `node ./out/server-main` 存活 |
| 锁与日志 | `ls -d ~/.trae-cn-server/.resolve-lock-*`；`ls -lt ~/.trae-cn-server/.stable-*.log \| head` | 锁目录已释放，且生成新的 `.stable-<commit>-ba586a00.log` |

四项全过才算修复完成；IDE 界面恢复只是第五项佐证，不能替代前四项。

> **为什么要四项对账而不是看界面？** 界面恢复可能来自客户端超时后的降级表现。只有远端文件、进程、锁、日志四项同时对齐，才能证明 server 真的装完并在运行，避免"看起来好了、下次连接又重装一遍"。

### 10.1 顺带回收（可选，非本技能主线）

旧版本目录各约 1.3 GB，可回收但**必须先确认无进程占用**：

```bash
ssh <host> 'du -sh ~/.trae-cn-server/bin/*'                      # 预检：先看清单
ssh <host> 'ls -l /proc/*/exe 2>/dev/null | grep trae-cn-server' # 确认哪些版本仍被占用
```

只删除既非当前版本、又无进程占用的目录。被占用的目录删除后空间会延迟释放（inode 仍被持有），需等进程退出才真正回收。

## 11. 安全检查清单

- [ ] 已确认 TCP 22 可通且认证成功（`ssh <host> 'echo ok'`）
- [ ] 已确认 `server-main` 进程不存在（否则不是下载问题，应退出本技能）
- [ ] 已记录下载子进程 PID、`ppid`，确认其父进程是安装脚本而非 IDE 客户端直连
- [ ] 三判据实测值已记录：`ss` 状态、两次 `rchar` 增量、`wchan`
- [ ] 已确认字节数确实停滞（而非"慢"），必要时延长采样窗口至 30 秒
- [ ] `df -h ~` 剩余空间大于 2 GB
- [ ] kill 目标仅为下载子进程，未误伤 `bash` 安装脚本与 `node server-main`
- [ ] 未手动 `rm -rf` 任何 `.resolve-lock-*` 目录
- [ ] 重试次数未超过 `retry-limit`，超限已转方案B
- [ ] 验收四项（体量 / 关键文件 / 进程 / 锁与日志）全部实测通过

> **为什么锁目录一律不手工删？** 锁目录里有 `pid` 与 `heartbeat`，它的存在既可能是"安装卡住"，也可能是"安装正在进行"。手工删除会与存活进程竞争，导致同一版本被并行安装、目录半写。正确做法是让安装脚本自己在结束时释放——实测 kill 下载子进程后，锁会随重试流程自然 `lock released`。

## 12. Gotchas（陷阱与反直觉行为）

- **不要把"Skill 卡住"当 Skill 缺陷排查**：Skill 的每次工具调用都依赖远端工作区通道，通道未建立时任何 Skill 都无响应。先看 IDE 通知的来源（`Remote SSH Extension`）与目标主机，再决定排查方向。
- **`curl` 只设了 `--connect-timeout`，没有 `--max-time`**：连接超时只管建连，建连成功后若对端停止发数据，进程可以无限期阻塞。这是"能一直等下去"的结构性原因，也是必须由人介入 kill 的原因。
- **`update.trae.ai` / `update.trae.cn` 解析失败是噪音**：这两个域名实测 NXDOMAIN，真实下载域是 `lf-cdn.trae.com.cn`。不要拿前者的失败推定"没有外网"。
- **UI 上的"取消"按钮不一定终止远端进程**：本地取消后远端 `curl` 可能仍存活并继续占着锁，务必远端核验。
- **重试会重新解析 DNS**：这正是方案A 有效的机制；但若本地 DNS 缓存或内部 DNS 稳定返回同一坏节点，重试无效，需转方案B 或 `--resolve` 指定。
- **空目录 ≠ 没在装**：解压发生在下载完成之后，下载中途目标目录本就是 `total 0`，必须以进程与 `rchar` 为准。
- **磁盘高位会放大症状**：剩余空间紧张时目录同样表现为空，先 `df` 再判断。
- **可迁移性**：同一套三判据适用于 `~/.vscode-server`、`pip` / `npm` 下载卡住、`docker pull` 无进度、`git clone` 挂起——凡"进程存活 + 连接已建立 + 字节停滞"皆可套用。

## 13. 关键参考

| 参考 | 路径 | 何时查阅 |
|---|---|---|
| 只读取证脚本 | [scripts/triage.sh](scripts/triage.sh) | 需要一次性采集全部判据时 |
| 远端并发与改机集成 | [../vendor-snapshot-parity/SKILL.md](../vendor-snapshot-parity/SKILL.md) | 需要把远端结构对拍入库时（相邻场景） |
| 会话方法论编排 | [../seven-concepts-cmd/SKILL.md](../seven-concepts-cmd/SKILL.md) | 需要按 R→I→E 沉淀同类故障经验时 |

## 14. Changelog

- **v1.0.0** (2026-10-29): 初始版本。来源：远端 `10.16.11.3` 上 Trae CN Remote-SSH server 安装卡在下载环节的实测排障——`curl` 对单 CDN 边缘节点（`221.195.209.14:443`）ESTABLISHED 但仅收 346 字节、`wchan=do_poll`、停滞 10 分钟以上；`kill -TERM` 后安装脚本自动重试，主包 327,345,664 字节下载并解压成功，锁释放、`node ./out/server-main` 拉起。沉淀为「字节停滞 + 进程存活 + 连接已建立」三判据与最小杀伤修复流程。