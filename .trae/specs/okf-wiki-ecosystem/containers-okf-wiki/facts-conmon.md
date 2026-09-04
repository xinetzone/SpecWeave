# conmon 项目事实提取

> 项目路径：d:\spaces\SpecWeave\external\dao\action\Containers\conmon
> 提取时间：2026-08-26

## 项目概述（来自 README.md）
- conmon 是一个 OCI 容器运行时监控器
- 使用 C 语言编写，设计为低内存占用
- 在容器管理器（如 Podman、CRI-O）和 OCI 运行时（如 runc、crun）之间充当监控程序和通信工具
- 启动时通常双 fork 以守护进程化
- 提供容器附加 socket、记录容器流到日志文件、记录容器退出时间和代码

## 源码文件清单（src/ 目录）
- .c 文件（16个）：cgroup.c、cli.c、close_fds.c、cmsg.c、conmon.c、conn_sock.c、ctr_exit.c、ctr_logging.c、ctr_stdio.c、ctrl.c、globals.c、oom.c、parent_pipe_fd.c、runtime_args.c、self_pipe.c、utils.c
- .h 文件（16个）：cgroup.h、cli.h、close_fds.h、cmsg.h、config.h、conn_sock.h、ctr_exit.h、ctr_logging.h、ctr_stdio.h、ctrl.h、globals.h、oom.h、parent_pipe_fd.h、runtime_args.h、self_pipe.h、utils.h

---

## 可验证事实列表

- F-001: 宏 DEFAULT_UMASK 定义值为 0022（源码位置：src/conmon.c#L37）
- F-002: 主函数为 main(int argc, char *argv[])（源码位置：src/conmon.c#L39）
- F-003: main 函数开头调用 setlocale(LC_ALL, "") 和 umask(DEFAULT_UMASK)（源码位置：src/conmon.c#L41-L42）
- F-004: main 函数调用 initialize_cli(argc, argv) 初始化 CLI，返回值≥0时直接 exit（源码位置：src/conmon.c#L50-L53）
- F-005: main 函数调用 attempt_oom_adjust(-1000) 调整 OOM 分数（源码位置：src/conmon.c#L57）
- F-006: main 函数中 signal(SIGPIPE, SIG_IGN) 忽略 SIGPIPE 信号，signal(SIGTERM, handle_signal) 捕获 SIGTERM（源码位置：src/conmon.c#L60-L62）
- F-007: 从环境变量 _OCI_STARTPIPE 获取启动管道 fd：get_pipe_fd_from_env("_OCI_STARTPIPE")（源码位置：src/conmon.c#L64）
- F-008: 非 opt_sync 模式下执行双 fork：pid_t main_pid = fork()，父进程写 pidfile 后 _exit(0)（源码位置：src/conmon.c#L90-L105）
- F-009: 注册 atexit(reap_children) 在退出时收割子进程（源码位置：src/conmon.c#L108）
- F-010: 调用 setsid() 创建新的会话组（源码位置：src/conmon.c#L132）
- F-011: 调用 set_subreaper(true) 将自身设置为子进程收割者（源码位置：src/conmon.c#L138）
- F-012: opt_terminal 为真时调用 setup_console_socket()，否则创建 stdin/stdout 管道（源码位置：src/conmon.c#L148-L178）
- F-013: 始终创建 stderr 管道：pipe2(fds, O_CLOEXEC)，mainfd_stderr = fds[0]，workerfd_stderr = fds[1]（源码位置：src/conmon.c#L182-L186）
- F-014: 调用 configure_runtime_args(csname) 配置运行时参数（源码位置：src/conmon.c#L188）
- F-015: fork 创建容器进程：create_pid = fork()（源码位置：src/conmon.c#L217）
- F-016: 子进程中调用 set_pdeathsig(SIGKILL) 设置父进程死亡信号（源码位置：src/conmon.c#L221）
- F-017: 子进程中调用 reset_oom_adjust() 重置 OOM 分数调整，然后 execv 运行时（源码位置：src/conmon.c#L284-L285）
- F-018: 使用 GHashTable *pid_to_handler 映射 pid 到处理回调函数（源码位置：src/conmon.c#L301）
- F-019: g_hash_table_insert 将 create_pid 映射到 runtime_exit_cb，container_pid 映射到 container_exit_cb（源码位置：src/conmon.c#L302、#L419）
- F-020: 使用 signalfd 处理 SIGCHLD：get_signal_descriptor() + g_unix_fd_add(signal_fd, G_IO_IN, on_signalfd_cb, &data)（源码位置：src/conmon.c#L309-L312）
- F-021: 调用 self_pipe_init(self_pipe_cb, &data) 初始化自管道用于安全唤醒主循环（源码位置：src/conmon.c#L317）
- F-022: opt_timeout > 0 时调用 g_timeout_add_seconds(opt_timeout, timeout_cb, NULL) 设置超时（源码位置：src/conmon.c#L440-L442）
- F-023: __linux__ 下调用 setup_oom_handling(container_pid) 设置 OOM 处理（源码位置：src/conmon.c#L429-L431）
- F-024: 主循环运行条件：opt_api_version < 1 || !opt_exec || !opt_terminal || container_status < 0（源码位置：src/conmon.c#L476）
- F-025: __linux__ 下主循环退出后调用 check_cgroup2_oom() 检查 cgroup v2 OOM（源码位置：src/conmon.c#L481-L483）
- F-026: timed_out 为真且 container_pid > 0 时，调用 kill(-process_group, SIGKILL) 或 kill(container_pid, SIGKILL) 杀死进程组（源码位置：src/conmon.c#L499-L507）
- F-027: 退出时向 opt_persist_path/exit 和 opt_exit_dir/opt_cid 写入退出状态码（源码位置：src/conmon.c#L530-L544）
- F-028: 宏 CGROUP2_SUPER_MAGIC 定义值为 0x63677270（源码位置：src/cgroup.c#L22）
- F-029: 宏 CGROUP_ROOT 定义值为 "/sys/fs/cgroup"（源码位置：src/cgroup.c#L25）
- F-030: 全局变量 oom_event_fd 和 oom_cgroup_fd 初始化为 -1（源码位置：src/cgroup.c#L27-L28）
- F-031: setup_oom_handling(int pid) 通过 statfs("/sys/fs/cgroup") 判断 cgroup v1/v2：f_type == CGROUP2_SUPER_MAGIC 为 v2（源码位置：src/cgroup.c#L40-L50）
- F-032: setup_oom_handling_cgroup_v2 使用 inotify_init() + inotify_add_watch 监控 memory.events 文件的 IN_MODIFY 事件（源码位置：src/cgroup.c#L128-L147）
- F-033: setup_oom_handling_cgroup_v1 打开 memory.cgroup.event_control 和 memory.oom_control，使用 eventfd(0, EFD_CLOEXEC) 创建事件 fd（源码位置：src/cgroup.c#L160-L188）
- F-034: check_cgroup2_oom() 解析 memory.events 文件中的 "oom " 和 "oom_kill " 计数器，与 last_oom_counter、last_oom_kill_counter 静态变量比较（源码位置：src/cgroup.c#L289-L358）
- F-035: create_oom_files() 分别在 opt_persist_path 和 opt_bundle_path 下创建名为 "oom" 的文件（源码位置：src/cgroup.c#L364-L371）
- F-036: 全局 volatile sig_atomic_t 变量 container_pid 和 create_pid 初始化为 -1（源码位置：src/ctr_exit.c#L20-L21）
- F-037: struct pid_check_data 包含两个 GHashTable 指针：pid_to_handler 和 exit_status_cache（源码位置：src/ctr_exit.h#L12-L15）
- F-038: check_child_processes() 使用 waitpid(-1, &status, WNOHANG) 非阻塞检查所有子进程（源码位置：src/ctr_exit.c#L48）
- F-039: get_exit_status(int status) 逻辑：WIFEXITED 返回 WEXITSTATUS；WIFSIGNALED 返回 128 + WTERMSIG；否则返回 -1（源码位置：src/ctr_exit.c#L142-L149）
- F-040: timeout_cb() 设置 timed_out = TRUE，调用 ninfo 记录日志，然后 g_main_loop_quit(main_loop)（源码位置：src/ctr_exit.c#L134-L140）
- F-041: reap_children() 循环调用 waitpid(-1, NULL, WNOHANG) 直到无更多僵尸进程（源码位置：src/ctr_exit.c#L253-L259）
- F-042: terminal_accept_cb() 调用 accept4(fd, NULL, NULL, SOCK_CLOEXEC) 接受 console socket 连接（源码位置：src/ctrl.c#L31）
- F-043: terminal_accept_cb() 调用 recvfd(connfd) 接收控制台文件描述符（源码位置：src/ctrl.c#L46）
- F-044: 终端属性设置 tset.c_oflag |= ONLCR（源码位置：src/ctrl.c#L62）
- F-045: mainfd_stdin = console.fd，mainfd_stdout = dup(console.fd)（源码位置：src/ctrl.c#L70-L71）
- F-046: process_terminal_ctrl_line() 解析 "%d %d %d\n" 格式的控制消息，支持 WIN_RESIZE_EVENT 和 REOPEN_LOGS_EVENT 两种类型（源码位置：src/ctrl.c#L142-L177）
- F-047: 宏 CTLBUFSZ 定义值为 200（源码位置：src/ctrl.c#L188）
- F-048: resize_winsz() 使用 ioctl(mainfd_stdout, TIOCSWINSZ, &ws) 设置终端窗口大小，struct winsize 的 ws_row 和 ws_col 分别为 height 和 width（源码位置：src/ctrl.c#L241-L250）
- F-049: setup_console_fifo() 创建名为 "winsz" 的 FIFO，setup_terminal_control_fifo() 创建名为 "ctl" 的 FIFO（源码位置：src/ctrl.c#L253-L271）
- F-050: setup_fifo() 使用 mkfifo(path, 0660) 创建命名管道，已存在时先 unlink 再重建（源码位置：src/ctrl.c#L273-L292）
- F-051: 全局变量 int old_oom_score 初始化为 0（源码位置：src/oom.c#L10）
- F-052: write_oom_adjust() 打开 /proc/self/oom_score_adj 进行读写操作（源码位置：src/oom.c#L16）
- F-053: attempt_oom_adjust(oom_score) 调用 write_oom_adjust 并保存旧值到 old_oom_score；reset_oom_adjust() 恢复 old_oom_score（源码位置：src/oom.c#L41-L48）
- F-054: 使用 GOptionEntry opt_entries[] 数组定义所有 CLI 选项（源码位置：src/cli.c#L62-L122）
- F-055: CLI 选项包含：--api-version、--bundle/-b、--cid/-c、--conmon-pidfile/-P、--container-pidfile/-p、--cuuid/-u、--exec/-e、--exec-attach、--terminal/-t、--timeout/-T、--version 等（源码位置：src/cli.c#L63-L121）
- F-056: opt_socket_path 默认值为 DEFAULT_SOCKET_PATH（"/var/run/crio"），opt_timeout 默认值为 0，opt_log_size_max 默认值为 -1，opt_log_max_files 默认值为 1（源码位置：src/cli.c#L42-L45、#L60）
- F-057: initialize_cli() 中如果 opt_cid == NULL，打印错误并退出："Container ID not provided. Use --cid"（源码位置：src/cli.c#L159-L162）
- F-058: process_cli() 中调用 g_main_loop_new(NULL, FALSE) 创建 GMainLoop（源码位置：src/cli.c#L172）
- F-059: 宏 BUF_SIZE 定义为 8192，STDIO_BUF_SIZE 定义为 8192，CONN_SOCK_BUF_SIZE 定义为 32768（源码位置：src/config.h#L5-L7）
- F-060: 宏 WIN_RESIZE_EVENT 定义为 1，REOPEN_LOGS_EVENT 定义为 2，TIMED_OUT_MESSAGE 定义为 "command timed out"（源码位置：src/config.h#L9-L11）
- F-061: 全局变量声明：runtime_status、container_status、mainfd_stdin、mainfd_stdout、mainfd_stderr、attach_socket_fd、console_socket_fd、terminal_ctrl_fd、inotify_fd、winsz_fd_w、winsz_fd_r、attach_pipe_fd、dev_null_r、dev_null_w、timed_out、main_loop、self_pipe_w（源码位置：src/globals.h#L7-L30）
- F-062: do_exit_command() 中先 fork()，子进程在 opt_exit_delay 秒 sleep 后 execv(opt_exit_command, args)（源码位置：src/ctr_exit.c#L199-L250）
