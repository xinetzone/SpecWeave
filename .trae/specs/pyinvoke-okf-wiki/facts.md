---
name: pyinvoke-facts
version: 1.0.0
created: 2026-08-21
source: external/libs/pyinvoke/invoke/invoke/
---

# PyInvoke 源码事实清单

> 本文件记录从 pyinvoke 源码中提取的纯客观事实，不含因果推断。共70条。

## 一、包入口与导出（__init__.py）

**F-001**: `__init__.py` 导出核心类：`Collection`, `Config`, `Context`, `MockContext`, `Executor`, `FilesystemLoader`, `Program`, `Parser`, `Argument`, `ParserContext`, `ParseResult`, `Task`, `Call`, `task`, `call`, `Runner`, `Local`, `Result`, `Failure`, `Promise`, `StreamWatcher`, `Responder`, `FailingResponder`, `pty_size`，以及异常类集合。来源：`__init__.py` L4-L31

**F-002**: 版本号通过 `importlib.metadata.version("invoke")` 动态获取。来源：`__init__.py` L33

**F-003**: 模块级便捷函数 `run(command, **kwargs)` 创建匿名 `Context()` 并调用其 `run()` 方法。来源：`__init__.py` L36-L52

**F-004**: 模块级便捷函数 `sudo(command, **kwargs)` 创建匿名 `Context()` 并调用其 `sudo()` 方法（v1.4新增）。来源：`__init__.py` L55-L72

## 二、Task 类与 @task 装饰器（tasks.py）

**F-005**: `Task(Generic[T])` 构造参数：`body`, `name=None`, `aliases=()`, `positional=None`, `optional=()`, `default=False`, `auto_shortflags=True`, `help=None`, `pre=None`, `post=None`, `autoprint=False`, `iterable=None`, `incrementable=None`。来源：`tasks.py`

**F-006**: Task 使用 `update_wrapper(self, self.body)` 复制函数元数据；显式复制 `__doc__`、`__name__`、`__module__`。来源：`tasks.py`

**F-007**: `positional=None` 时通过 `fill_implicit_positionals` 自动推断无默认值参数为 positional。来源：`tasks.py`

**F-008**: `Task.__call__(*args, **kwargs)` 第一个参数必须是 Context 实例，否则 TypeError；调用 body，递增 `times_called`。来源：`tasks.py`

**F-009**: `Task.get_arguments()` 通过 `inspect.Signature` 获取函数签名（移除第一个Context参数），对每个参数调用 `arg_opts()` 构造 Argument 对象；positional 参数按顺序移到列表前端。来源：`tasks.py`

**F-010**: `Task.arg_opts(name, default, taken_names)` 为参数生成 Argument 选项：下划线自动转连字符，`auto_shortflags=True` 时自动分配短flag，根据 default 值推断 kind。来源：`tasks.py`

**F-011**: `@task` 装饰器支持两种形式：无括号 `@task` 直接包装函数；有括号 `@task(pre=[...], aliases=[...])` 返回 inner 装饰器；`klass` kwarg 默认 Task（v1.1新增）。来源：`tasks.py`

**F-012**: `Call` 类封装带参数的任务调用：`__init__(self, task, called_as=None, args=None, kwargs=None)`；`__getattr__` 委托到 self.task；`make_context(config, core_parse_result)` 创建 Context。来源：`tasks.py`

**F-013**: `call(task, *args, **kwargs)` 便捷函数等价于 `Call(task, args=args, kwargs=kwargs)`，用于 pre/post 预设参数。来源：`tasks.py`

## 三、Context 对象（context.py）

**F-014**: `Context(DataProxy)` 构造参数：`config=None`（默认 `Config()`），`remainder=""`；初始化 `command_prefixes=[]`、`command_cwds=[]`。来源：`context.py`

**F-015**: Context 继承 DataProxy，支持 `c['foo']` 和 `c.foo` 两种方式访问配置。来源：`context.py`, `config.py` L111-L130

**F-016**: `Context.run(command, **kwargs)` 通过 `self.config.runners.local(self)` 实例化 Runner，调用 `_run(runner, command, **kwargs)`。来源：`context.py`

**F-017**: `Context.sudo(command, **kwargs)` 构造 `sudo -S -p '{prompt}' {env_flags}{user_flags}{command}`，自动注入 FailingResponder 响应密码提示，捕获 ResponseNotAccepted 转为 AuthFailure。来源：`context.py`

**F-018**: `Context.cd(path)` 是 @contextmanager，append str(path) 到 command_cwds，退出时 pop；支持嵌套和 PathLike（v1.5+）。来源：`context.py`

**F-019**: `Context.prefix(command)` 是 @contextmanager，append 到 command_prefixes，退出时 pop；`_prefix_commands` 用 ` && ` 连接所有前缀和命令。来源：`context.py`

**F-020**: `Context.cwd` 属性从 command_cwds 计算当前工作目录，从最后一个绝对路径开始拼接相对路径，自动转义空格。来源：`context.py`

**F-021**: `MockContext(Context)` 测试用类，run/sudo 参数接受 Result/bool/str/可迭代/dict，repeat=True 时用 itertools.cycle 无限循环。来源：`context.py`

## 四、Collection 与命名空间（collection.py）

**F-022**: `Collection` 构造参数：第一个位置参数若为 str 则作为 name；其余位置参数和 kwargs 通过 `_add_object` 自动分发：Task→add_task，Collection/ModuleType→add_collection。来源：`collection.py`

**F-023**: `Collection.from_module(module, name=None, config=None, ...)` 类方法：优先查找模块中 `ns` 或 `namespace` Collection 属性；无则自动收集所有 Task 实例。来源：`collection.py`

**F-024**: `Collection.add_task(task, name=None, aliases=None, default=None)`：name 优先级 传入name→task.name→body.__name__；名称经 transform 处理；检测与 sub-collection 的名称冲突。来源：`collection.py`

**F-025**: `Collection.add_collection(coll, name=None, default=None)`：ModuleType 自动转 `Collection.from_module()`；name 必须存在；检测与现有 task 名称冲突。来源：`collection.py`

**F-026**: `Collection.__getitem__(name)` 支持点分路径（如 `foo.bar`）递归查找；name 为空时返回默认任务；`task_with_config(name)` 返回 (Task, merged_config)。来源：`collection.py`

**F-027**: `Collection.transform(name)`：auto_dash_names=True（默认）时非首尾、非点号旁的下划线转连字符；False 时连字符转下划线。来源：`collection.py`

**F-028**: `Collection.configure(options)` 通过 `merge_dicts(self._configuration, options)` 递归合并配置；`configuration(taskpath=None)` 返回深拷贝配置。来源：`collection.py`

**F-029**: `Collection.to_contexts()` 将每个 task 转换为 ParserContext（name=primary name, aliases=alias list, args=task.get_arguments()）。来源：`collection.py`

**F-030**: `Collection.task_names` 属性返回扁平化 `{primary_name: [aliases]}` 字典，子集合任务加 `coll_name.` 前缀。来源：`collection.py`

## 五、配置系统（config.py）

**F-031**: `DataProxy` 类实现嵌套 dict+attr 访问：`__getattr__` 委托到 `_get(key)`，dict 值递归包装为 DataProxy；`_set()` 方法用 `object.__setattr__` 绕过代理设置真实属性。来源：`config.py` L36-L311

**F-032**: `Config(DataProxy)` 类属性：`prefix="invoke"`，`file_prefix=None`（默认用prefix），`env_prefix=None`（默认用prefix大写）。来源：`config.py` L313-L427

**F-033**: 配置层级（merge顺序，从低到高）：defaults → collection → system → user → project → env → runtime → overrides → modifications → deletions。来源：`config.py` L941-L964

**F-034**: `Config.global_defaults()` 返回核心默认值：`run` 子树（echo=False, pty=False, warn=False, shell=bash/cmd.exe, hide=None, watchers=[], 等）、`runners.local=Local`、`sudo` 子树、`tasks` 子树（auto_dash_names=True, collection_name="tasks", dedupe=True）、`timeouts.command=None`。来源：`config.py` L430-L510

**F-035**: Config 构造参数：`overrides=None`, `defaults=None`, `system_prefix=None`（默认 `/etc/`，Windows无）, `user_prefix=None`（默认 `~/.`）, `project_location=None`, `runtime_path=None`, `lazy=False`。来源：`config.py` L512-L575

**F-036**: 配置文件后缀搜索顺序：yaml → yml → json → py；支持 `_load_yaml/_load_json/_load_py` 三种加载器。来源：`config.py` L581, L913-L939

**F-037**: 系统级配置路径：`{system_prefix}{file_prefix}.{suffix}` → 如 `/etc/invoke.yaml`；用户级：`{user_prefix}{file_prefix}.{suffix}` → 如 `~/.invoke.yaml`；项目级：`{project_location}{file_prefix}.{suffix}`。来源：`config.py` L698-L752

**F-038**: 环境变量前缀：默认 `INVOKE_`（prefix大写+下划线）；通过 `Environment` 类递归遍历配置键结构加载，只加载已知配置键对应的环境变量。来源：`config.py` L622-L628, L786-L809; `env.py`

**F-039**: `merge_dicts(base, updates)` 递归合并：dict值递归，非dict叶值用 `copy.copy`；类型冲突（dict vs non-dict）抛 AmbiguousMergeError；fileno对象按引用传递。来源：`config.py` L1168-L1224

**F-040**: Config 支持 `clone(into=None)` 创建副本，dict 值递归重建，非dict值用 `copy.copy`，支持升级到子类。来源：`config.py` L985-L1071

## 六、执行模型（executor.py）

**F-041**: `Executor` 构造参数：`collection`（必需）, `config=None`（默认 Config()）, `core=None`（默认空 ParseResult()）。来源：`executor.py` L23-L50

**F-042**: `Executor.execute(*tasks)` 流程：normalize→expand_calls(pre/post)→dedupe→逐个执行（load_collection→load_shell_env→make_context→调用task→autoprint）；返回 `{Task: Result}` 字典。来源：`executor.py` L52-L149

**F-043**: `Executor.normalize(tasks)` 支持三种输入：字符串（任务名）、(name, kwargs)二元组、ParserContext实例；无参数时使用 collection.default。来源：`executor.py` L151-L179

**F-044**: `Executor.expand_calls(calls)` 递归展开 pre/post 任务列表；`dedupe(calls)` 基于 Call.__eq__ 去重（默认 `config.tasks.dedupe=True`）。来源：`executor.py` L181-L232

## 七、Runner 系统（runners.py）

**F-045**: `Runner` 是半抽象基类，子类须实现 `start`, `wait`, `returncode`, `read_proc_stdout`, `read_proc_stderr`, `_write_proc_stdin`, `close_proc_stdin`, `kill` 等方法。来源：`runners.py` L62-L1231

**F-046**: `Runner.run(command, **kwargs)` 核心参数：asynchronous, disown, dry, echo, echo_stdin, encoding, env, err_stream, fallback, hide, in_stream, out_stream, pty, replace_env, shell, timeout, warn, watchers。来源：`runners.py` L126-L401

**F-047**: `Runner.run()` 执行流程：_setup→dry-run检查→start→start_timer→create_io_threads→线程start→（异步返回Promise/同步_finish）。来源：`runners.py` L439-L469

**F-048**: IO线程模型：handle_stdout/handle_stderr/handle_stdin 各为独立 ExceptionHandlingThread；stdout/stderr线程读取子进程输出并写入buffer和输出流，同时调用respond()处理watcher。来源：`runners.py` L643-L683, L750-L810

**F-049**: `Local(Runner)` 本地执行器：使用 subprocess.Popen；pty模式通过 pty.fork() 创建伪终端；stdin无fileno且fallback=True时自动降级为非pty并打印警告。来源：`runners.py` L1234+

**F-050**: `Result` 类封装执行结果：command, shell, env, pty, hide, encoding, stdout, stderr, exited, pid, disowned 属性；`ok` 属性（exited==0），`failed` 属性（not ok），`tail(stream, count=10)` 方法返回最后count行。来源：`runners.py`（Result类定义）

**F-051**: `Promise` 类用于异步执行：`join()` 阻塞等待完成，返回Result或抛异常；支持上下文管理器自动join。来源：`runners.py`（Promise类定义）

**F-052**: `Runner.respond(buffer_)` 将buffer内容拼接为string，遍历watchers调用submit()，将响应写入子进程stdin。来源：`runners.py` L932-L957

## 八、CLI 与 Program（program.py）

**F-053**: `Program` 管理顶层CLI调用，用于分发invoke自身和自定义独立CLI程序。来源：`program.py` L32-L44

**F-054**: Program.core_args() 返回18个核心Argument：command-timeout(-T), complete, config(-f), debug(-d), dry(-R), echo(-e), help(-h), hide, list(-l), list-depth(-D), list-format(-F), print-completion-script, prompt-for-sudo-password, pty(-p), version(-V), warn-only(-w), write-pyc。来源：`program.py` L48-L150

**F-055**: Program.task_args() 返回3个任务相关Argument（仅task runner模式）：collection(-c), no-dedupe, search-root(-r)。来源：`program.py` L152-L179

**F-056**: Program 构造参数：version=None, namespace=None, name=None, binary=None, loader_class=None, executor_class=None, config_class=None, binary_names=None。来源：`program.py` L190-L200

## 九、Loader（loader.py）

**F-057**: `Loader` 抽象基类：`find(name)` 返回 ModuleSpec；`load(name=None)` 通过importlib加载模块，将模块所在目录加入sys.path，返回 (module, directory)。来源：`loader.py` L14-L96

**F-058**: `FilesystemLoader(Loader)` 从文件系统加载：从 start 目录向上递归查找 `{name}.py` 或 `{name}/__init__.py`；start 默认 CWD。来源：`loader.py` L99-L154

## 十、异常体系（exceptions.py）

**F-059**: 异常类层次：`Failure`（基类，含result和reason属性）→ `UnexpectedExit`（非零退出码）、`CommandTimedOut`（超时）、`AuthFailure`（认证失败）；其他：`Exit`（替代sys.exit）、`ParseError`、`ThreadException`、`WatcherError`→`ResponseNotAccepted`、`PlatformError`、`CollectionNotFound`、`AmbiguousEnvVar`、`UncastableEnvVar`、`UnknownFileType`、`UnpicklableConfigMember`、`SubprocessPipeError`。来源：`exceptions.py`

**F-060**: `Exit(message=None, code=None)`：有message时默认code=1，无message时默认code=0；替代scattered sys.exit调用以提高可测试性。来源：`exceptions.py` L207-L238

**F-061**: `ThreadException` 收集后台线程异常，`exceptions` 属性为 ExceptionWrapper 元组；`__str__` 格式化显示所有线程异常详情。来源：`exceptions.py` L326-L380

## 十一、Watcher（watchers.py）

**F-062**: `StreamWatcher(threading.local)` 基类：`submit(stream)` 接受完整流内容字符串，返回可迭代的响应字符串；继承 threading.local 以支持多线程分别监视stdout/stderr。来源：`watchers.py` L8-L50

**F-063**: `Responder(StreamWatcher)`：构造参数 `pattern`（正则表达式）、`response`（响应字符串）；使用 index 增量匹配避免重复响应。来源：`watchers.py` L53-L110

**F-064**: `FailingResponder(Responder)`：额外 `sentinel` 参数；submit 时检测sentinel模式，若已提交过响应且检测到sentinel则抛 ResponseNotAccepted。来源：`watchers.py` L113-L145

## 十二、Parser 系统（parser/）

**F-065**: `Argument` 构造参数：`name=None, names=(), kind=str, default=None, help=None, positional=False, optional=False, incrementable=False, attr_name=None`；takes_value 属性：kind is bool 或 incrementable→False，其余→True。来源：`parser/argument.py`

**F-066**: `ParserContext` 管理单个任务/核心的参数集合：args(Lexicon), positional_args(list), flags(Lexicon), inverse_flags(Dict)；`add_arg()` 注册参数并生成 --flag 和 --no-flag（bool default=True时）。来源：`parser/context.py`

**F-067**: `Parser` 使用 ParseMachine 状态机解析argv：三种状态（context/unknown/end），handle(token) 按优先级分发（flag→inverse_flag→flag_value→positional→context→core_flag→unknown/error）。来源：`parser/parser.py`

**F-068**: `ParseResult(list)` 继承list，额外属性 `remainder: str`（--后的内容）和 `unparsed: List[str]`（未能解析的token）。来源：`parser/parser.py`

## 十三、终端与工具（terminals.py, util.py, env.py）

**F-069**: `pty_size()` 返回 (cols, rows)，失败默认 (80, 24)；`character_buffered(stream)` 上下文管理器在Unix TTY上设置cbreak模式；`WINDOWS = sys.platform == "win32"`。来源：`terminals.py`

**F-070**: `Environment(config, prefix)` 递归遍历配置键结构，将匹配的环境变量通过类型转换（_cast）写入嵌套字典；bool转换：`new not in ("0", "")`；list/tuple抛UncastableEnvVar。来源：`env.py`

**F-071**: `ExceptionHandlingThread(threading.Thread)` 默认 daemon=True，run() 捕获 BaseException 存入 exc_info；`is_dead` = not is_alive() and exc_info is not None。来源：`util.py`

**F-072**: Lexicon和yaml双轨导入：优先 .vendor 子包，ImportError时回退到系统包。来源：`util.py`

## 数据流总览

**F-073**: 核心数据流：@task装饰函数→Task实例→Collection.add_task()注册→Collection.from_module()自动扫描→CLI时Collection.to_contexts()→Parser解析argv→ParseResult→Executor.normalize()转Call列表→expand_calls展开pre/post→dedupe去重→每个Call.make_context()创建Context→Context.run()通过Runner执行命令→返回Result。来源：综合多个文件
