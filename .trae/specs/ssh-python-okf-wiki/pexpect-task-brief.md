# pexpect 知识束生成任务指导书

## 路径
- 源码: `d:\spaces\SpecWeave\external\libs\pexpect\pexpect\`
- 输出: `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\networking\pexpect\`
- 事实: `.trae\specs\ssh-python-okf-wiki\pexpect-facts.md`
- 洞察: `.trae\specs\ssh-python-okf-wiki\pexpect-insights.md`
- 格式参考: `bundles\networking\paramiko\index.md`

## 版本: pexpect 4.9.0, commit fc8f062518b4
纯 Python Expect 风格交互控制库。核心模块：
- `__init__.py` — 导出 spawn, run, EOF, TIMEOUT, ExceptionPexpect 等
- `pty_spawn.py` — spawn 类（Unix PTY 实现，spawn 是 pty_spawn.spawn 的别名）
- `pxssh.py` — pxssh 类（SSH 登录专用，继承 spawn）
- `popen_spawn.py` — PopenSpawn（跨平台，基于 subprocess.Popen，无 PTY）
- `fdpexpect.py` — fdspawn（基于文件描述符）
- `socket_pexpect.py` — SocketSpawn（基于 socket）
- `replwrap.py` — REPLWrapper（REPL 交互封装）
- `run.py` — run() 函数
- `exceptions.py` — ExceptionPexpect, EOF, TIMEOUT
- `utils.py` — 工具函数
- `FSM.py` — 有限状态机

## R 阶段（50+ 事实）
阅读以上模块提取 F-001~F-050+。重点：
- spawn.__init__ 参数（command, args, timeout, maxread, searchwindowsize, logfile, cwd, env, echo, encoding, codec_errors, dimensions, use_poll）
- spawn.expect(pattern, timeout, searchwindowsize, async_=False) 方法和返回值（匹配索引）
- spawn.expect_list, expect_exact, expect_exact_list
- spawn.send, spawn.sendline, spawn.write, spawn.writelines
- spawn.before, spawn.after, spawn.match, spawn.match_index
- spawn.interact(escape_character) — 交回终端控制权
- spawn.close, spawn.kill, spawn.terminate, spawn.isalive
- spawn.read, spawn.readline, spawn.read_nonblocking
- spawn.compile_pattern_list
- pxssh.login(server, username, password, ...), pxssh.logout(), pxssh.prompt()
- pxssh.UNIQUE_PROMPT, PROMPT_SET_SH, force_password
- PopenSpawn 差异（无 PTY、跨平台、基于 subprocess.Popen）
- run() 函数签名和返回值
- EOF/TIMEOUT 特殊模式
- 平台差异（pty_spawn 仅 Unix，popen_spawn 跨平台）

## I 阶段（3-5 洞察）
1. spawn 的 PTY 子进程控制模型与增量缓冲区匹配
2. expect 正则匹配引擎——模式列表返回索引、before/after/match 三元组
3. pxssh 对 SSH 登录的状态机封装（unique prompt 技巧）
4. 跨平台 spawn 变体策略（pty_spawn/popen_spawn/fdspawn/SocketSpawn 继承层次）

## E 阶段

### references/pexpect-source.md（先生成）
版本 4.9.0、核心模块清单、公开 API、平台限制说明

### concepts/（≥8篇）
1. `00-introduction.md` — 简介、Expect 概念、安装、平台支持
2. `01-getting-started.md` — 第一个 spawn+expect 示例
3. `02-spawn-class.md` — spawn 构造参数、子进程生命周期、PTY
4. `03-expect-patterns.md` — expect/expect_exact/expect_list、模式列表返回索引、EOF/TIMEOUT、before/after/match、searchwindowsize、maxread
5. `04-send-interact.md` — send/sendline/write、interact() 交回控制、logfile 日志
6. `05-pxssh.md` — pxssh SSH 登录、login/logout/prompt、unique prompt 机制、force_password
7. `06-cross-platform-spawn.md` — PopenSpawn（跨平台无 PTY）、fdspawn、SocketSpawn、Unix vs Windows 差异
8. `07-replwrap.md` — REPLWrapper 封装 REPL 交互
9. `08-advanced-patterns.md` — FSM 有限状态机、run() 函数、超时处理、非阻塞读取、调试技巧

### examples/（≥4篇）
1. `ssh-login-automation.md` — pxssh 自动登录
2. `ftp-interaction.md` — FTP 交互自动化
3. `password-prompts.md` — 密码提示自动响应
4. `repl-control.md` — REPL 交互控制

### index.md 文件（最后生成）

## Frontmatter
tags 包含 pexpect，stale_after: 2027-12-31（pexpect API 非常稳定）

## V 阶段 Grep 验证
验证: spawn, pxssh, run, EOF, TIMEOUT, ExceptionPexpect, ExceptionPxssh, PopenSpawn, fdspawn, fdpexpect, SocketSpawn, REPLWrapper
方法: expect, expect_list, expect_exact, send, sendline, sendcontrol, sendeof, interact, before, after, match, close, kill, terminate, isalive, login, logout, prompt, read, readline, read_nonblocking, compile_pattern_list
注意: spawn 实际是 pty_spawn.spawn 在 __init__.py 中导入的别名；Windows 上 spawn 不可用（需用 PopenSpawn）。

## 返回
事实数、文件列表、虚构 API 修复、Grep 验证摘要。
