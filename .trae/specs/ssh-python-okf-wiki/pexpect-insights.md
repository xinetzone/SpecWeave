# pexpect 架构洞察

> 基于 55 条源码事实提炼的 4 个核心架构洞察。

## 洞察 1：PTY 子进程控制模型与增量缓冲区匹配

pexpect 的核心设计围绕"伪终端（PTY）+ 增量缓冲区"展开。`spawn` 类通过 `ptyprocess.PtyProcess.spawn()` 创建一个连接到 PTY 的子进程，子进程的 stdout/stderr 写入 PTY 主端，pexpect 从主端读取。这与 `subprocess.Popen` 的管道模型有本质区别：

- **PTY 模式**：子进程认为自己连接到真实终端，会进行行缓冲、启用颜色输出、密码输入时关闭回显等终端行为；换行符为 `\r\n`（CR/LF 对）。
- **管道模式**（PopenSpawn）：子进程检测到非 tty 时通常切换为全缓冲，不输出颜色；换行符为 `os.linesep`，无 CR/LF 转换。

`read_nonblocking` 使用 `select.select()` 或 `select.poll()` 实现超时，每次最多读取 `maxread`（默认 2000）字节到内部缓冲区。`Expecter` 引擎维护 `_buffer`（当前搜索窗口）和 `_before`（完整历史），利用 `freshlen`（新增数据长度）避免重复搜索整个缓冲区，在保证正确性的同时控制性能开销。

## 洞察 2：expect 正则匹配引擎——模式列表索引与三元组状态

`expect` 方法的设计体现了"模式即分支"的编程范式：传入一个模式列表，返回匹配项的索引，调用方通过索引分派处理逻辑。这种模式比 try/except 捕获 EOF/TIMEOUT 更优雅：

```python
i = child.expect(['password:', 'Permission denied', pexpect.EOF, pexpect.TIMEOUT])
if i == 0: child.sendline(password)
elif i == 1: handle_denied()
elif i == 2: handle_eof()
elif i == 3: handle_timeout()
```

每次 expect 调用后，三个属性构成"匹配三元组"：
- `before`：匹配位置之前的所有数据（完整输出历史）
- `after`：匹配到的字符串（EOF/TIMEOUT 时为异常类型本身）
- `match`：re.MatchObject（可用于提取分组）或 None

匹配规则有两个容易踩坑的细节：
1. **多模式同位置匹配时选列表最左项**（非"最佳匹配"），如 `expect(['bar', 'foo', 'foobar'])` 对输入 'foobar' 返回 1（foo）。
2. **数据分块到达影响匹配结果**，如 `expect(['foobar', 'foo'])` 在 'foobar' 一次性到达时返回 0，但 'bar' 延迟到达时可能先返回 1。

## 洞察 3：pxssh 的唯一提示符状态机封装

pxssh 解决了 SSH 自动化中的核心难题——**如何可靠判断远程 shell 已就绪**。它采用"提示符重置"策略：

1. 登录后通过 `sync_original_prompt()` 发送多次回车，用 Levenshtein 距离比较两次响应来检测原始提示符（阈值 0.4）。
2. 调用 `set_unique_prompt()` 发送 `PS1='[PEXPECT]\$ '`（sh）或等效的 csh/zsh 命令，将提示符改为不可能在正常输出中出现的 `[PEXPECT]$ `。
3. 之后 `prompt()` 方法只需 `expect([self.PROMPT, TIMEOUT])` 即可精确同步。

源码中有一个微妙的 hack：设置提示符的命令（`PROMPT_SET_SH`）与匹配正则（`UNIQUE_PROMPT`）故意不同——设置命令中 `$` 前有反斜杠，确保命令回显时不会被正则误匹配。pxssh 还处理了首次连接的主机密钥确认（"are you sure you want to continue connecting"）、密码/密钥认证、终端类型查询、MOTD 干扰等多种边界情况。

## 洞察 4：跨平台 spawn 变体策略与继承层次

pexpect 通过 `SpawnBase` 抽象基类统一接口，针对不同 I/O 机制提供四个具体实现：

| 子类 | I/O 机制 | 平台 | 子进程控制 |
|------|---------|------|-----------|
| `spawn`（pty_spawn） | PTY（ptyprocess） | 仅 Unix | 完整（信号/终端控制/interact） |
| `PopenSpawn` | subprocess.Popen 管道 | 跨平台 | 有限（无终端控制/interact） |
| `fdspawn` | 任意文件描述符 | Unix | 无（terminate 抛异常） |
| `SocketSpawn` | socket | 跨平台 | 无（仅网络 I/O） |

这种策略模式让用户根据目标平台和需求选择实现。`SpawnBase` 提供 expect 匹配引擎、read/readline 文件接口、日志、编码处理等通用能力，子类只需实现 `read_nonblocking`、`send`、`close`、`isalive` 等 I/O 原语。值得注意的是，Windows 上 `pexpect.spawn` 和 `pexpect.run` 根本不在顶层命名空间中（`__init__.py` 用 `if sys.platform != 'win32'` 条件导入），Windows 用户必须显式使用 `pexpect.popen_spawn.PopenSpawn`。
