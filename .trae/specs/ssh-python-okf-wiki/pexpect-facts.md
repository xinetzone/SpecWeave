# pexpect 源码事实清单

> 版本：4.9.0（commit fc8f062518b4）
> 源码路径：`external/libs/pexpect/pexpect/`
> 事实数：55 条

## 包结构与导出

- F-001: `__init__.py` 定义 `__version__ = '4.9.0'`，从 `.exceptions` 导入 `ExceptionPexpect`、`EOF`、`TIMEOUT`，从 `.utils` 导入 `split_command_line`、`which`、`is_executable_file`，从 `.expect` 导入 `Expecter`、`searcher_re`、`searcher_string`。
- F-002: 在非 win32 平台，`__init__.py` 从 `.pty_spawn` 导入 `spawn`、`spawnu`，从 `.run` 导入 `run`、`runu`。Windows 上这些名称不在包顶层命名空间中。
- F-003: `__all__` 列表为 `['ExceptionPexpect', 'EOF', 'TIMEOUT', 'spawn', 'spawnu', 'run', 'runu', 'which', 'split_command_line', '__version__', '__revision__']`。
- F-004: `spawnu()` 函数（pty_spawn.py:857）已弃用，内部通过 `kwargs.setdefault('encoding', 'utf-8')` 后调用 `spawn()`。
- F-005: `runu()` 函数（run.py:150）已弃用，同样通过设置 encoding='utf-8' 后调用 `run()`。

## 异常体系

- F-006: `ExceptionPexpect`（exceptions.py:6）继承 `Exception`，是所有 pexpect 异常的基类，具有 `value` 属性和 `get_trace()` 方法。
- F-007: `EOF`（exceptions.py:29）继承 `ExceptionPexpect`，在从子进程读到 EOF 时抛出，通常表示子进程已退出。
- F-008: `TIMEOUT`（exceptions.py:34）继承 `ExceptionPexpect`，在读取超时超出设定值时抛出。
- F-009: `ExceptionPxssh`（pxssh.py:32）继承 `ExceptionPexpect`，是 pxssh 模块专用异常。
- F-010: `ExceptionFSM`（FSM.py:87）继承 `Exception`，是 FSM 有限状态机模块的专用异常。

## SpawnBase 基类

- F-011: `SpawnBase`（spawnbase.py:23）是抽象基类，提供 expect 系列方法、read/readline、compile_pattern_list 等通用能力；不应直接实例化。
- F-012: `SpawnBase.__init__` 接受 `timeout=30, maxread=2000, searchwindowsize=None, logfile=None, encoding=None, codec_errors='strict'` 参数。
- F-013: SpawnBase 初始化 `before=None`、`after=None`、`match=None`、`match_index=None`、`exitstatus=None`、`signalstatus=None`、`child_fd=-1`、`closed=True`、`terminated=True` 等状态属性。
- F-014: SpawnBase 定义 `delaybeforesend=0.05`（发送前延迟50ms，解决密码回显问题）、`delayafterclose=0.1`、`delayafterterminate=0.1`、`delayafterread=0.0001` 四个时序参数。
- F-015: `buffer` 是 property（spawnbase.py:168），底层使用 `BytesIO` 或 `StringIO`（取决于 encoding 是否为 None），支持向后兼容的读写访问。
- F-016: 当 `encoding=None` 时为 bytes 模式，`string_type=bytes`、`linesep=os.linesep.encode('ascii')`、`crlf=b'\r\n'`；当 encoding 指定时为 unicode 模式，`string_type=str`、`linesep=os.linesep`、`crlf=u'\r\n'`。

## spawn 类（pty_spawn.py）

- F-017: `spawn`（pty_spawn.py:29）继承 `SpawnBase`，是 pexpect 的主类，仅在 Unix 平台可用（依赖 pty 和 ptyprocess）。
- F-018: `spawn.__init__` 完整签名为 `(self, command, args=[], timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None, env=None, ignore_sighup=False, echo=True, preexec_fn=None, encoding=None, codec_errors='strict', dimensions=None, use_poll=False)`。
- F-019: `spawn._spawn` 方法（pty_spawn.py:240）负责实际启动子进程，通过 `ptyprocess.PtyProcess.spawn()` 创建 PTY 子进程，设置 `self.pid` 和 `self.child_fd`。
- F-020: spawn 不解释 shell 元字符（`>`、`|`、`*`）；如需管道/重定向，必须显式启动 shell（如 `/bin/bash -c "..."`）。
- F-021: `spawn.close(force=True)`（pty_spawn.py:317）关闭与子进程的连接，force=True 时若子进程忽略 SIGHUP/SIGINT 则发送 SIGKILL。
- F-022: `spawn.isalive()`（pty_spawn.py:696）非阻塞检测子进程是否存活，子进程终止时更新 `exitstatus`/`signalstatus`/`status`。
- F-023: `spawn.terminate(force=False)`（pty_spawn.py:632）依次尝试 SIGHUP→SIGCONT→SIGINT，force=True 时追加 SIGKILL。
- F-024: `spawn.kill(sig)`（pty_spawn.py:715）通过 `os.kill(self.pid, sig)` 向子进程发送指定信号。
- F-025: `spawn.wait()`（pty_spawn.py:672）阻塞等待子进程退出，返回 exitstatus；若子进程有未读输出则可能永久阻塞。
- F-026: `spawn.send(s)`（pty_spawn.py:527）向子进程发送字符串，返回写入字节数；发送前若 `delaybeforesend` 非 None 则先 sleep。
- F-027: `spawn.sendline(s='')`（pty_spawn.py:571）在 send 基础上追加 `os.linesep`（bytes 模式）或 `self.linesep`。
- F-028: `spawn.sendcontrol(char)`（pty_spawn.py:586）发送控制字符（如 Ctrl-C 传 'c'、Ctrl-D 传 'd'），委托给 `self.ptyproc.sendcontrol(char)`。
- F-029: `spawn.sendeof()`（pty_spawn.py:599）发送 EOF 字符（Ctrl-D），委托给 `self.ptyproc.sendeof()`。
- F-030: `spawn.sendintr()`（pty_spawn.py:612）发送 SIGINT 信号（Ctrl-C），委托给 `self.ptyproc.sendintr()`。
- F-031: `spawn.write(s)`（pty_spawn.py:512）调用 `self.send(s)`，无返回值；`spawn.writelines(sequence)`（pty_spawn.py:518）对序列中每个元素调用 write。
- F-032: `spawn.interact(escape_character=chr(29), input_filter=None, output_filter=None)`（pty_spawn.py:739）将终端控制权交还给用户，默认转义字符为 Ctrl-]（ASCII 29）。
- F-033: `spawn.read_nonblocking(size=1, timeout=-1)`（pty_spawn.py:416）使用 `select.select()` 或 `select.poll()`（由 use_poll 控制）实现带超时的非阻塞读取。
- F-034: `spawn.waitnoecho(timeout=-1)`（pty_spawn.py:344）轮询等待终端 ECHO 标志关闭，可用于检测密码输入等待；`spawn.getecho()` 和 `spawn.setecho(state)` 控制终端回显模式。
- F-035: `spawn.getwinsize()` 返回 `(rows, cols)` 元组；`spawn.setwinsize(rows, cols)` 设置终端窗口大小并触发 SIGWINCH。
- F-036: `spawn.flag_eof` 是 property（pty_spawn.py:619），委托给 `self.ptyproc.flag_eof`；`spawn.eof()` 方法返回 `self.flag_eof`。

## expect 匹配引擎

- F-037: `SpawnBase.expect(pattern, timeout=-1, searchwindowsize=-1, async_=False, **kw)`（spawnbase.py:254）是核心匹配方法，先调用 `compile_pattern_list` 编译模式，再委托给 `expect_list`。
- F-038: `SpawnBase.expect_list(pattern_list, timeout=-1, searchwindowsize=-1, async_=False, **kw)`（spawnbase.py:357）接受已编译的正则表达式列表，避免重复编译；async_=True 时返回 asyncio coroutine。
- F-039: `SpawnBase.expect_exact(pattern_list, timeout=-1, searchwindowsize=-1, async_=False, **kw)`（spawnbase.py:385）使用纯字符串匹配（非正则），性能更好，使用 `searcher_string` 而非 `searcher_re`。
- F-040: `SpawnBase.compile_pattern_list(patterns)`（spawnbase.py:205）将字符串/正则/EOF/TIMEOUT 混合列表编译为统一格式；字符串用 `re.DOTALL` 编译（dot 匹配换行），`ignorecase=True` 时追加 `re.IGNORECASE`。
- F-041: expect 返回匹配模式在列表中的索引；非列表参数成功匹配时返回 0。多模式同时匹配时，选择流中最先出现的；同一位置多模式匹配时选择列表中最左的。
- F-042: 匹配成功后，`before` 属性为匹配位置之前的所有数据，`after` 为匹配到的字符串，`match` 为 re.MatchObject（正则匹配）或字符串本身（expect_exact），`match_index` 为匹配索引。
- F-043: EOF/TIMEOUT 可作为模式列表中的条目；匹配时返回其索引而非抛出异常，`after` 设为对应异常类型，`match` 设为 None。
- F-044: `Expecter` 类（expect.py:5）是 expect 循环的内部引擎，管理缓冲区窗口、freshlen 增量搜索和 before/after/match 状态设置。
- F-045: `searcher_string`（expect.py:187）和 `searcher_re`（expect.py:285）是两种搜索策略，分别用于纯字符串和正则匹配；都有 `eof_index`、`timeout_index` 属性和 `search(buffer, freshlen, searchwindowsize)` 方法。

## read/readline 文件接口

- F-046: `SpawnBase.read(size=-1)`（spawnbase.py:444）size<0 时读取直到 EOF/delimiter 并返回 before；size>0 时通过正则 `.{size}` 匹配精确字节数。
- F-047: `SpawnBase.readline(size=-1)`（spawnbase.py:473）查找 `self.crlf`（PTY 模式为 `\r\n`）或 delimiter，返回 `before + crlf`；size 参数除 0 外被忽略。
- F-048: SpawnBase 支持 `__iter__`（迭代 readline）、`readlines(sizehint=-1)`、`fileno()`、`flush()`、`isatty()`、`__enter__`/`__exit__`（上下文管理器）。

## pxssh 类

- F-049: `pxssh`（pxssh.py:52）继承 `spawn`，专门用于 SSH 连接自动化，添加 `login()`、`logout()`、`prompt()`、`set_unique_prompt()` 方法。
- F-050: `pxssh.__init__` 签名为 `(timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None, env=None, ignore_sighup=True, echo=True, options={}, encoding=None, codec_errors='strict', debug_command_string=False, use_poll=False)`，注意 ignore_sighup 默认为 True（spawn 默认为 False）。
- F-051: pxssh 定义 `UNIQUE_PROMPT = r"\[PEXPECT\][\$\#] "`，登录后将远程 shell 的 PS1 重置为此唯一提示，避免 MOTD 等输出干扰 prompt 匹配。
- F-052: pxssh 定义三种 shell 的 prompt 设置命令：`PROMPT_SET_SH = r"PS1='[PEXPECT]\$ '"`、`PROMPT_SET_CSH = r"set prompt='[PEXPECT]\$ '"`、`PROMPT_SET_ZSH = "prompt restore;\nPS1='[PEXPECT]%(!.#.$) '"`。
- F-053: `pxssh.login(server, username=None, password='', terminal_type='ansi', original_prompt=r"[#$]", login_timeout=10, port=None, auto_prompt_reset=True, ssh_key=None, quiet=True, sync_multiplier=1, check_local_ip=True, password_regex=..., ssh_tunnels={}, spawn_local_ssh=True, sync_original_prompt=True, ssh_config=None, cmd='ssh')` 处理完整 SSH 登录流程，包括主机密钥确认、密码/密钥认证、终端类型、prompt 同步。
- F-054: `pxssh.force_password` 属性（默认 False）设为 True 时在 SSH 命令行追加 `-o 'PubkeyAuthentication=no'`，强制密码认证。
- F-055: `pxssh.logout()`（pxssh.py:475）发送 `exit` 命令，若检测到 stopped jobs 则发送两次 exit；`pxssh.prompt(timeout=-1)` 是 `expect([PROMPT, TIMEOUT])` 的快捷方式，返回 True/False。

## PopenSpawn 跨平台实现

- F-056: `PopenSpawn`（popen_spawn.py:20）继承 `SpawnBase`，基于 `subprocess.Popen`，无 PTY，在 Windows 和 Unix 上均可使用。
- F-057: `PopenSpawn.__init__` 签名为 `(cmd, timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None, env=None, encoding=None, codec_errors='strict', preexec_fn=None)`，不支持 echo/dimensions/ignore_sighup/use_poll 等 PTY 专属参数。
- F-058: PopenSpawn 将 stderr 合并到 stdout（`stderr=subprocess.STDOUT`），使用独立守护线程 `_read_incoming` 将管道输出搬运到 `Queue`，`read_nonblocking` 从 Queue 取数据。
- F-059: PopenSpawn 在 Windows 上设置 `STARTF_USESHOWWINDOW` 和 `CREATE_NEW_PROCESS_GROUP`；`kill(sig)` 对 Windows 信号做映射（SIGINT→CTRL_C_EVENT、SIGBREAK→CTRL_BREAK_EVENT、其他→SIGTERM）。
- F-060: PopenSpawn 的 `crlf` 设为 `os.linesep`（非 PTY 的 `\r\n`），因为 subprocess 管道不做 CR/LF 转换；`sendeof()` 通过关闭 stdin 管道实现。

## fdspawn 和 SocketSpawn

- F-061: `fdspawn`（fdpexpect.py:35）继承 `SpawnBase`，接受已打开的文件描述符（int 或具有 fileno() 方法的对象），适用于串口、命名管道等；调用者负责打开和关闭 fd。
- F-062: fdspawn 的 `terminate(force=False)` 直接抛出 `ExceptionPexpect('This method is not valid for file descriptors.')`。
- F-063: `SocketSpawn`（socket_pexpect.py:32）继承 `SpawnBase`，接受已连接的 `socket.socket` 对象，跨平台（Unix 和 Windows 均可），使用 socket.settimeout 实现超时。
- F-064: SocketSpawn 的 `read_nonblocking` 使用 `socket.recv(size)` 配合 `_timeout` contextmanager 设置 socket 超时；收到空字节抛出 EOF，socket.timeout 转为 TIMEOUT。

## REPLWrapper

- F-065: `REPLWrapper`（replwrap.py:17）封装 REPL（Read-Eval-Print Loop）交互，构造参数为 `(cmd_or_spawn, orig_prompt, prompt_change, new_prompt=PEXPECT_PROMPT, continuation_prompt=PEXPECT_CONTINUATION_PROMPT, extra_init_cmd=None)`。
- F-066: REPLWrapper 定义常量 `PEXPECT_PROMPT = u'[PEXPECT_PROMPT>'` 和 `PEXPECT_CONTINUATION_PROMPT = u'[PEXPECT_PROMPT+'`。
- F-067: `REPLWrapper.run_command(command, timeout=-1, async_=False)` 发送命令并等待 prompt 返回，将多行命令逐行发送，遇到 continuation prompt 时发送 SIGINT 并抛出 ValueError。
- F-068: replwrap 模块提供工厂函数 `python(command=sys.executable)`、`bash(command="bash")`、`zsh(command="zsh", args=("--no-rcs", "-V", "+Z"))`，分别返回预配置的 REPLWrapper 实例。

## run() 函数

- F-069: `run(command, timeout=30, withexitstatus=False, events=None, extra_args=None, logfile=None, cwd=None, env=None, **kwargs)`（run.py:7）是高层便捷函数，内部创建 spawn 实例，执行命令并返回输出。
- F-070: `events` 参数可以是 dict 或 tuple list，将模式映射到响应（字符串或回调函数）；回调接收 locals() 字典，返回 True 终止 run，返回字符串则发送给子进程。
- F-071: `withexitstatus=True` 时返回 `(output, exitstatus)` 元组，否则仅返回 output 字符串。

## FSM 有限状态机

- F-072: `FSM`（FSM.py:97）实现有限状态机，维护 `state_transitions`（精确匹配）、`state_transitions_any`（任意输入符号匹配）、`default_transition`（默认兜底）三张转换表。
- F-073: FSM 的 `process(input_symbol)` 方法按优先级查找转换：精确 `(input_symbol, state)` → `state` 任意 → default → 抛出 ExceptionFSM；action 函数接收 FSM 实例作为参数。
- F-074: FSM 提供 `add_transition`、`add_transition_list`、`add_transition_any`、`set_default_transition`、`reset`、`process_list` 方法，`memory` 属性可作为下推自动机的栈使用。

## 工具函数

- F-075: `which(filename, env=None)`（utils.py:48）在 PATH 中查找可执行文件，返回完整路径或 None；`is_executable_file(path)` 检查路径是否为可执行常规文件。
- F-076: `split_command_line(command_line)`（utils.py:69）使用小型状态机解析命令行，正确处理单引号、双引号和反斜杠转义。
- F-077: `select_ignore_interrupts(iwtd, owtd, ewtd, timeout=None)` 和 `poll_ignore_interrupts(fds, timeout=None)` 包装 select/poll，在 EINTR（如 SIGWINCH）时自动重试。
