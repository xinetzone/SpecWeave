# Facts: MobileWorld
> 信源根：external/libs/tools/Tongyi-MAI/MobileWorld（下述路径均相对此根）
> 采集日期：2026-08-29 ｜ 采集方式：源码直读（零推测）

## F-001 包名与构建后端
- 位置: pyproject.toml
- 内容: `name = "mobile-world"`，`version = "0.1.0"`，`description = "Mobile GUI automation and testing framework"`，`requires-python = ">=3.12,<3.13"`，`build-backend = "hatchling.build"`。

## F-002 CLI 入口点
- 位置: pyproject.toml
- 内容: `[project.scripts]` 定义两个等价入口：`mobile-world = "mobile_world.core.cli:main"` 与 `mw = "mobile_world.core.cli:main"`。

## F-003 运行时依赖清单
- 位置: pyproject.toml
- 内容: dependencies 含 `absl-py==2.1.0`、`android_env==1.2.3`、`fastapi>=0.104.0`、`uvicorn[standard]>=0.24.0`、`gradio>=5.49.0`、`mcp>=1.9.4`、`fastmcp>=2.9.2`、`openai>=1.106.1`、`qwen-agent>=0.0.31`、`python-fasthtml>=0.12.33`、`psycopg2-binary>=2.9.10`、`loguru>=0.7.3`、`python-dotenv>=0.9.9`、`joblib`、`imagehash>=4.3.2`、`markdownify>=1.2.2` 等共 40 项。optional-dependencies：`agents = ["openai>=1.106.1"]`、`dev`（pytest/pytest-asyncio/ruff/pylint/black/mypy/ipdb）、`all = ["mobile-world[agents,dev]"]`。

## F-004 ruff/mypy/pytest 配置
- 位置: pyproject.toml
- 内容: `target-version = "py312"`，`line-length = 100`，lint select 含 `E,W,F,I,UP,FA`；per-file-ignores 对 `src/mobile_world/core/log_viewer/routes.py` 豁免 `F405/F403`（FastHTML 星号导入标准模式）；pytest `testpaths = ["tests"]`。

## F-005 .env 变量清单
- 位置: .env.example
- 内容: 共 6 个变量：`API_KEY`（agent 模型密钥）、`DASHSCOPE_API_KEY`（MCP 用）、`MODELSCOPE_API_KEY`（MCP 用）、`USER_AGENT_API_KEY`、`USER_AGENT_BASE_URL`、`USER_AGENT_MODEL`（示例值 `gpt-4.1`）。

## F-006 git submodule 资源
- 位置: .gitmodules
- 内容: 3 个 submodule：`resources/mall` → `https://github.com/qykong/mall_fork.git`；`resources/mail` → `https://github.com/nrgao/mail_fork.git`；`resources/mastodon-android` → `https://github.com/patdooog/mastodon-android.git`。

## F-007 BaseAgent 抽象基类
- 位置: src/mobile_world/agents/base.py
- 内容: `class BaseAgent(ABC)`，`__init__(self, *args: Any, **kwargs: Any)` 初始化 `_total_completion_tokens/_total_prompt_tokens/_total_cached_tokens = 0`。核心方法：`initialize(self, instruction: str) -> bool`、`initialize_hook(self, instruction: str) -> None`、抽象方法 `predict(self, observation: dict[str, Any]) -> tuple[str, JSONAction]`、`done() -> None`、`reset() -> None`、`build_openai_client(self, base_url: str, api_key: str) -> None`（OpenAI 客户端 `timeout=120.0`，api_key 为空时用 `"empty"`）。

## F-008 BaseAgent.openai_chat_completions_create 签名
- 位置: src/mobile_world/agents/base.py
- 内容: `def openai_chat_completions_create(self, model: str, messages: list[dict], retry_times: int = 3, stream: bool = False, **kwargs: Any) -> str | None`。模型名含 `"claude"` 时强制 `kwargs["max_tokens"] = 64000` 并删除 `temperature`；`"gpt"/"o1"` 将 `max_tokens` 换成 `max_completion_tokens`；`"kimi-k"` 加 `extra_body={"enable_thinking": True}` 且把 `reasoning_content` 包成 `<think>...</think>` 前缀；重试失败 `time.sleep(1)`。

## F-009 token 用量统计接口
- 位置: src/mobile_world/agents/base.py
- 内容: `get_total_token_usage(self) -> dict[str, int]` 返回键 `completion_tokens/prompt_tokens/cached_tokens/total_tokens`（total 为 completion+prompt）；`reset_token_usage(self) -> None` 归零三个计数器；`_wrap_stream_with_usage_logging` 在流结束时取最后一个带 usage 的 chunk 记账。

## F-010 MCPAgent 子类
- 位置: src/mobile_world/agents/base.py
- 内容: `class MCPAgent(BaseAgent)`，`__init__(self, tools: list[dict], *args, **kwargs)` 保存 `self.tools`；提供 `reset_tools(self, tools: list[dict]) -> None`；`predict` 仍为抽象方法。

## F-011 AGENT_CONFIGS 注册表
- 位置: src/mobile_world/agents/registry.py
- 内容: 模块级字典 `AGENT_CONFIGS` 固定 9 项映射（注册名 → 类）：`"qwen3vl": Qwen3VLAgentMCP`、`"planner_executor": PlannerExecutorAgentMCP`、`"mai_ui_agent": MAIUINaivigationAgent`、`"general_e2e": GeneralE2EAgentMCP`、`"seed_agent": SeedAgent`、`"gelab_agent": GelabAgent`、`"ui_venus_agent": VenusNaviAgent`、`"gui_owl_1_5": GUIOWL15AgentMCP`、`"memgui": MemGUIAgent`。

## F-012 create_agent 工厂签名与双路径
- 位置: src/mobile_world/agents/registry.py
- 内容: `def create_agent(agent_type: str, model_name: str, llm_base_url: str, api_key: str = "empty", **kwargs)`。若 `agent_type.endswith(".py") or os.path.exists(agent_type)` 走文件加载路径 `load_agent_from_file`，以 `model_name/llm_base_url/api_key` 实例化；否则查 `AGENT_CONFIGS`，以 `model_name/llm_base_url/tools=kwargs["env"].tools/api_key` 实例化；未知类型抛 `ValueError(f"Unsupported agent type: {agent_type}")`。

## F-013 load_agent_from_file 动态加载
- 位置: src/mobile_world/agents/registry.py
- 内容: `def load_agent_from_file(file_path: str) -> type[BaseAgent]`，用 `importlib.util.spec_from_file_location` 加载模块，`inspect.getmembers(module, inspect.isclass)` 收集 `issubclass(obj, BaseAgent) and obj is not BaseAgent` 的类；0 个抛 ValueError，多个取第一个并 warning。

## F-014 UIINSGroundingAgent（grounding 子代理）
- 位置: src/mobile_world/agents/grounding/uiins.py
- 内容: `class UIINSGroundingAgent(BaseAgent)`，`__init__(self, llm_base_url: str, model_name: str, runtime_conf: dict = {"temperature": 0.0, "max_tokens": 512, "min_pixels": 3136, "max_pixels": 4096*2160}, ...)`；`predict` 内 `smart_resize` 后 base64 编码截图，system prompt 要求输出 `<tool_call>{"name": "grounding", ...}`，`parse_coordinates_from_response` 用正则 `\[(\d+),(\d+)\]` 提取坐标；请求参数含 `frequency_penalty=0.0, presence_penalty=0.0, extra_body={"repetition_penalty": 1.0}, seed=42`，`max_retries = 3`。辅助函数 `parsing_response_to_andoid_world_env_action(response, instruction)` 按指令含 "click"/"press" 映射 CLICK/LONG_PRESS。

## F-015 动作映射字典
- 位置: src/mobile_world/agents/utils/agent_mapping.py
- 内容: `QWENVL2AW_ACTION_MAP` 14 键（click/type/long_press/scroll/back/home/enter/answer/open_app/wait/terminate/swipe/ask_user/drag）；`GUIOWL2AW_ACTION_MAP` 13 键（open→OPEN_APP、interact→ASK_USER）；`UIINS_ACTION_MAP = {"click": CLICK, "long_press": LONG_PRESS}`。值为 `runtime.utils.models` 中的动作类型常量。

## F-016 图像处理常量与工具函数
- 位置: src/mobile_world/agents/utils/helpers.py
- 内容: `IMAGE_FACTOR = 28`、`MIN_PIXELS = 100*28*28`、`MAX_PIXELS = 16384*28*28`、`MAX_RATIO = 200`；函数 `add_period_robustly(text: str) -> str`（按中英文 dominant 判定补 `。` 或 `.`）、`pil_to_base64(image) -> str`、`pil_adaptive_resize(image: Image.Image, max_dimension: int = 2576) -> tuple[Image.Image, float, float]`。

## F-017 统一 agent 测试脚本
- 位置: src/mobile_world/agents/utils/test_agent.py
- 内容: `python -m mobile_world.agents.utils.test_agent` 入口；`get_agent_class(agent_type)` 支持 `general_e2e/planner_executor/qwen3vl/mai_ui_agent` 四种；`test_agent(agent_type, model_name, llm_base_url, api_key, screenshot_path, instruction, output_image_path=None, runtime_conf=None, **kwargs)`；默认 `runtime_conf = {"history_n_images": 3, "temperature": 0.0, "max_tokens": 2048}`；argparse 含 `--scale_factor`（默认 1000）与 planner_executor 专用 `--executor_agent_class/--executor_model_name/--executor_llm_base_url`。

## F-018 CLI 顶层子命令清单
- 位置: src/mobile_world/core/cli.py + subcommands/__init__.py
- 内容: `create_parser()` 依次注册 8 个子命令配置函数：server、eval（别名 `run`）、test、device（别名 `viewer`）、logs、env、info、eval-server；`async_main()` 按 `args.command` 分发到 `subcommands.execute_*`；`main()` 用 `asyncio.run(async_main())`。

## F-019 eval 子命令公共参数组
- 位置: src/mobile_world/core/subcommands/eval.py
- 内容: `_add_common_arguments(parser)` 注册（每个均提供下划线别名）：`--agent-type`（required）、`--model-name`、`--llm-base-url`、`--api-key`、`--log-file-root`、`--max-round`（别名 `--max-step`）、`--aw-host`、`--timeout`、`--output`、`--executor-llm-base-url`、`--executor-model-name`、`--executor-agent-class`、`--device`、`--step-wait-time`（default 1.0）、`--suite-family`（choices=["mobile_world"], default="mobile_world"）、`--env-name-prefix`（default "mobile_world_env"）、`--env-image`（default "mobile_world"）、`--enable-mcp`、`--enable-user-interaction`、`--scale-factor`（default 1000）。

## F-020 eval 子命令专有参数与默认日志目录
- 位置: src/mobile_world/core/subcommands/eval.py
- 内容: eval 专有：`--task`（逗号分隔或 `"ALL"`）、`--auto-retry`（default 10）、`--dry-run`、`--max-concurrency`、`--shuffle-tasks`、`--pass-k`（default 1）。`execute` 中 `log_file_root = args.log_file_root or args.output or "./traj_logs"`；`device=args.device or "emulator-5554"`；`api_key=args.api_key or os.getenv("API_KEY")`。

## F-021 pass@k 报告生成
- 位置: src/mobile_world/core/subcommands/eval.py
- 内容: `generate_pass_k_report(log_file_root: str, k: int, total_duration: float, agent_type: str, model_name: str | None) -> dict`：逐次读取 `log_file_root/run_{i}/`（i∈1..k）调用 `scan_finished_tasks`，任务判过条件为 `score > 0.99` 且至少一次；返回 dict 含 `summary/metadata/tasks` 三键；报告写 `pass_k_report_{YYYYmmdd_HHMMSS}.json`。

## F-022 ALL 任务统计报告
- 位置: src/mobile_world/core/subcommands/eval.py
- 内容: `--task ALL` 时统计 `successful_tasks = sum(1 for result in task_results if result["score"] > 0.99)`，报告写入 `eval_report_{timestamp}.json`，含 `summary.total_tasks_assigned/total_tasks_with_results/successful_tasks/total_tasks_with_no_results/overall_success_rate/total_duration_seconds`。

## F-023 server 子命令默认端口
- 位置: src/mobile_world/core/subcommands/server.py
- 内容: `mobile-world server` 参数：`--host`（default "0.0.0.0"）、`--port`（default 6800）、`--debug`、`--suite-family`（default "mobile_world"）、`--enable-mcp`；执行 `await start_server(...)`。

## F-024 env 子命令动作集
- 位置: src/mobile_world/core/subcommands/env.py
- 内容: `env` 下 8 个子动作映射：`run/rm/list(ls)/info/restart/exec/check`。`run` 端口参数默认：`--backend-start-port 6800`、`--viewer-start-port 7860`、`--vnc-start-port 5800`、`--adb-start-port 5556`、`--count 1`、`--launch-interval 10`；`--dev` 只允许单容器（count>1 时 sys.exit(1)）；挂载 `.env` → `/app/service/.env`，dev 模式挂 `src` → `/app/service/src`；`--http-proxy` 说明 "10.0.2.2/127.0.0.1/localhost are always excluded"。

## F-025 env check 的 .env 校验占位符
- 位置: src/mobile_world/core/subcommands/env.py
- 内容: `_check_env_file()` 中 placeholders 字面量：`API_KEY="your_api_key_for_agent_model"`、`DASHSCOPE_API_KEY="dashscope_api_key_for_mcp"`、`MODELSCOPE_API_KEY="modelscope_api_key_for_mcp"`、`USER_AGENT_API_KEY="your_user_agent_llm_api_key"`、`USER_AGENT_BASE_URL="your_user_agent_base_url"`；API_KEY 缺失/占位为 issue，MCP 与 USER_AGENT_* 键缺失为 warning。

## F-026 restart 命令的容器内重启命令
- 位置: src/mobile_world/core/subcommands/env.py
- 内容: `_restart_single_container` 中 interactive 模式执行 `docker_exec_replace(container_name, "cd /app/service && uv run mobile-world server --port 6800 --enable-mcp", interactive=True)`；非交互调用 `restart_server_in_container(container_name, detach=True, enable_mcp=True)`。

## F-027 info 子命令结构
- 位置: src/mobile_world/core/subcommands/info.py
- 内容: `info` 下 4 个子命令：`task`（`--name/--filter/--suite-family/--export-excel/--no-pager`）、`agent`（`--filter`）、`app`（`--name/--filter/--suite-family`）、`mcp`（`--name/--filter`）；`export_tasks_to_excel` 用 pandas+openpyxl 写 Tasks/Statistics/Tag Statistics 三张 sheet。

## F-028 logs 子命令
- 位置: src/mobile_world/core/subcommands/logs.py
- 内容: `logs` 子动作含 `view`（`--log-dir` required、`--port` default 8760、`--base` default "/"）与 `results`（打印结果表）。

## F-029 eval-server 子命令参数
- 位置: src/mobile_world/core/subcommands/eval_server.py
- 内容: `eval-server` 参数：`--port`（default 8800）、`--max-containers`（default 40）、`--data-dir`（default "."）、`--base-path`（default "/"）、`--shell-prefix`（default ""）；调用 `eval_server.app.main(...)`。

## F-030 test 子命令设备自动发现
- 位置: src/mobile_world/core/subcommands/test.py
- 内容: `test` 接收位置参数 `goal`；`args.device is None` 时运行 `adb devices` 解析，0 台抛 `ValueError("No Android devices found")`，多台抛 `ValueError("Multiple Android devices found, please specify the device ID")`；调用 `run_user_task(goal=..., ...)`，`aw_url = args.aw_host.split(",")[0]`。

## F-031 FastAPI 服务与常量
- 位置: src/mobile_world/core/server.py
- 内容: `app = FastAPI(title="Mobile GUI Agent Benchmark Server", version="0.1.0")`；模块常量 `SUITE_FAMILY: str = "mobile_world"`、`AVD_MAPPING = {"mobile_world": "Pixel_8_API_34_x86_64"}`、`CONTROLLERS: dict[str, AndroidController] = {}`、`RESTART_COOLDOWN_SECONDS = 300`；CORS `allow_origins=["*"]`；`initialize_suite_family(suite_family)` 创建 `TaskRegistry()` 并打印 `Loaded {n} mobile_world tasks`。

## F-032 /health 端点自愈行为
- 位置: src/mobile_world/core/server.py
- 内容: `GET /health` 遍历 CONTROLLERS 调 `controller.check_health(try_times=2)`；不健康时在 `_restart_lock` + 300 秒冷却窗口内调用 `restart_emulator_with_avd(AVD_MAPPING[SUITE_FAMILY])`；健康返回 200 `{"ok": true, "devices": [...], "device_status": {...}}`，否则 503。

## F-033 server HTTP 端点全表
- 位置: src/mobile_world/core/server.py
- 内容: 路由清单：`GET /health`、`GET|POST /init`、`GET /state`、`GET /screenshot`（参数 device/prefix/return_b64）、`GET /download`、`GET /task-asset/{asset_path:path}`（校验 rel 以 ".." 开头或缺 "assets" 段则 400）、`GET /xml`（mode: Literal["uia","ac"]）、`POST /sms`、`POST /step`、`GET /task/list`、`GET /task/goal`、`GET /task/metadata`、`POST /task/init`、`GET /task/eval`、`POST /task/tear_down`、`GET /task/complexity`、`POST /task/callback`、`GET /config/callback`、`POST /suite_family/switch`。

## F-034 /step 动作分发表
- 位置: src/mobile_world/core/server.py
- 内容: `POST /step` 按 `action.action_type` 分发到 AndroidController：CLICK→`ctr.tap(int(x), int(y))`；SWIPE→`ctr.swipe(x, y, direction or "up")`；INPUT_TEXT→`ctr.text(text)`（空串跳过）；NAVIGATE_BACK/HOME→`ctr.back()/ctr.home()`；KEYBOARD_ENTER→`ctr.enter()`；LONG_PRESS→`ctr.long_press(x, y, 1000)`；DOUBLE_TAP→`ctr.double_tap(x, y)`；DRAG→`ctr.drag(start_x, start_y, end_x, end_y)`；SCROLL→映射为 `ctr.swipe(None, None, direction)`（scroll 的 up/down 与 swipe 相反）；OPEN_APP→`ctr.launch_app(app_name)`；WAIT→`time.sleep(1.0)`；ANSWER→`ctr.answer(text)`；STATUS→返回 goal_status；ASK_USER→`ctr.ask_user(agent_question)`；UNKNOWN→返回 `"UNKNOWN_ACTION"`。

## F-035 start_server 编程接口
- 位置: src/mobile_world/core/api/server.py
- 内容: `async def start_server(host="0.0.0.0", port=6800, debug=False, suite_family="mobile_world", enable_mcp=False, suppress_health_logs=True)`；`HealthCheckFilter` 过滤日志含 `/health` 的 access 记录；enable_mcp 时打印 `MCP server available at http://{host}:{port}/mcp-server/mcp`；另有 `create_server_config(...) -> uvicorn.Config` 与 `get_server_app()`。

## F-036 api/env.py 容器管理函数
- 位置: src/mobile_world/core/api/env.py
- 内容: 函数清单：`is_port_available(port, host="0.0.0.0")`、`find_available_ports(...)`、`find_next_container_index(prefix=DEFAULT_NAME_PREFIX, dev_mode=False)`、`wait_for_container_ready(...)`、`build_container_config(...)`、`launch_container(...)`、`launch_containers(...)`、`list_containers(...)`、`get_container_info(container_name) -> ContainerInfo | None`、`remove_container/remove_containers(...)`、`kill_server_in_container(container_name) -> bool`、`restart_server_in_container(...)`、`resolve_container_name(name, prefix=DEFAULT_NAME_PREFIX)`、`check_docker_installed/check_docker_permission/check_docker_running/check_kvm_available/check_iptables_nat -> PrerequisiteCheckResult`、`check_prerequisites() -> PrerequisiteCheckResults`、`check_image_status(image=DEFAULT_IMAGE) -> ImageStatus`、`pull_image(image=DEFAULT_IMAGE) -> tuple[bool, str]`。

## F-037 run_agent_with_evaluation 签名
- 位置: src/mobile_world/core/runner.py
- 内容: `def run_agent_with_evaluation(agent_type: str, model_name: str, llm_base_url: str, log_file_root: str, tasks: list[str], max_step: int = -1, aw_urls: list[str] | None = None, api_key: str | None = None, device: str = "emulator-5554", step_wait_time: float = 1.0, suite_family: str = "mobile_world", env_name_prefix: str = "mobile_world_env", env_image: str = "mobile_world", dry_run: bool = False, enable_mcp: bool = False, enable_user_interaction: bool = False, max_concurrency: int | None = None, shuffle_tasks: bool = False, auto_retry: int = 10, **kwargs) -> list[dict]`。aw_urls 为空时 `discover_backends(image_filter=env_image, prefix=env_name_prefix)` 自动发现容器。

## F-038 任务执行主循环
- 位置: src/mobile_world/core/runner.py
- 内容: `_execute_single_task(env, agent, task_name, max_step, traj_logger, enable_mcp=False) -> tuple[int, float]`：`env.get_task_goal(task_type=task_name)` → `agent.initialize(task_goal)` → 循环 `agent.predict({"screenshot", "tool_call", "ask_user_response"})` → `traj_logger.log_traj(...)` → `env.execute_action(action)`；`action.action_type in [ENV_FAIL, FINISHED, UNKNOWN]` 终止；ANSWER 执行后终止；`step >= max_step` 终止；最后 `env.get_task_score()` → `traj_logger.log_score` → `env.tear_down_task()` → `agent.done()`。并发用 `joblib.Parallel(backend="threading")` + `Queue` 分配 env；异常消息含 `"Device is not healthy"` 时 sleep(20) 重试（`retry_on_device_unhealthy: int = 2`）；`max_attempts = min(1 + auto_retry, 10)`。

## F-039 环境初始化分派
- 位置: src/mobile_world/core/runner.py
- 内容: `_init_env(env_url, device, step_wait_time, suite_family, enable_mcp)`：enable_mcp 为 True 时创建 `AndroidMCPEnvClient(env_url, device, step_wait_time=step_wait_time)`，否则 `AndroidEnvClient(...)`；随后 `env.switch_suite_family(suite_family)`。模块顶部执行 `load_dotenv()`。

## F-040 user_task_runner 交互式运行器
- 位置: src/mobile_world/core/user_task_runner/runner.py
- 内容: 提供 `run_user_task(...)`（`test` 子命令调用）与内部 `_execute_user_task/_ask_user_interactive/_print_step_header/_print_observation/_print_agent_response/_print_task_start/_print_task_end` 函数；`_ask_user_interactive(question: str) -> str` 供无 USER_AGENT 配置时人工应答。

## F-041 eval_server SQLite 表结构
- 位置: src/mobile_world/core/eval_server/db.py
- 内容: SQLite（WAL 模式）库文件 `{data_dir}/eval_jobs.db`，表 `jobs` 字段：`id TEXT PRIMARY KEY, label TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'queued', agent_type/model_name/llm_base_url TEXT NOT NULL, api_key TEXT DEFAULT '', env_count INTEGER NOT NULL, max_round INTEGER DEFAULT 50, step_wait_time REAL DEFAULT 1.0, auto_retry INTEGER DEFAULT 0, enable_user_interaction INTEGER DEFAULT 0, env_image TEXT DEFAULT '', container_prefix TEXT NOT NULL, log_dir/tmux_session/log_file TEXT DEFAULT '', total_tasks/successful_tasks INTEGER, success_rate REAL, scores_json TEXT DEFAULT '', created_at REAL DEFAULT (strftime('%s','now')), started_at/finished_at TEXT`。含 auto_retry/env_image 两段 ALTER TABLE 迁移。`create_job(...)` 用 `uuid.uuid4().hex[:12]` 生成 id，`container_prefix = f"eval_{job_id}"`；`count_running_envs()` 汇总 status='running' 的 env_count。

## F-042 eval_server FastHTML 应用与路由
- 位置: src/mobile_world/core/eval_server/app.py + routes.py
- 内容: `app, rt = fast_app()`；`async def main(port=8800, max_containers=40, data_dir=".", base_path="/", shell_prefix="")`：`db.init_db` → `register_routes(rt, base_path)` → 挂载 log_viewer 路由至 `{base_path}/log-viewer/` → `start_worker(max_containers, shell_prefix)` → uvicorn（`ws="none"`）。routes 内 `@rt` 路由：`/`、`/dashboard-content`、`/agent-types`、`/image-versions`、`/submit-form`、`/jobs/{job_id}/copy-form`、`POST /submit`、`/jobs/{job_id}`、`/jobs/{job_id}/log-tail`、`POST /jobs/{job_id}/cancel`、`POST /jobs/{job_id}/rerun`。

## F-043 eval_server 后台 worker
- 位置: src/mobile_world/core/eval_server/worker.py
- 内容: 常量 `MAX_CONTAINERS = 40`、`POLL_INTERVAL = 5`（秒）、`LOG_BASE_DIR = "eval_server_logs"`、`SHELL_PREFIX = ""`；`get_docker_containers()` 用 `docker ps --format '{{.Names}}\t{{.Status}}\t{{.Image}}'`；`get_available_images(repo="ghcr.io/tongyi-mai/mobile_world")`；`_start_job(job)` 在 tmux 会话 `eval_{job_id}` 中启动容器与 eval 命令，日志写 `output.log`。

## F-044 log_viewer 模块
- 位置: src/mobile_world/core/log_viewer/
- 内容: 文件组成 app.py/routes.py/styles.py/static_export.py/utils.py/__main__.py；`routes.register_routes(rt, base_path="/", route_prefix="")` 注册路由（FastHTML 星号导入，pyproject 对该文件豁免 F403/F405）；`logs view` 子命令默认端口 8760。

## F-045 ScrcpyScreenViewer 设备查看器
- 位置: src/mobile_world/core/device_viewer.py
- 内容: `class ScrcpyScreenViewer`，方法 `get_connected_devices()`（解析 `adb devices`）、`take_screenshot(device_id=None)`（`adb exec-out screencap -p`）、`start_streaming(device_id, fps=2)`（后台线程循环截图）。entrypoint.sh 中以 `uv run mobile-world viewer --port 7860` 启动。

## F-046 AndroidEnvClient 签名与默认值
- 位置: src/mobile_world/runtime/client.py
- 内容: `class AndroidEnvClient`，`__init__(self, url: str = "http://localhost:8000", device: str = "emulator-5554", step_wait_time: float = 1.0)`；模块常量 `TASK_META_DATA_PATH = "./new_task_metadata.json"`、`DEFAULT_MAX_STEP = 15`。`get_screenshot` 带 `@backoff.on_exception(backoff.expo, Exception, max_tries=3)` 装饰；`get_observation(type="screenshot")` 对 accessibility_tree 类型抛 `ValueError("Accessibility tree is not supported yet")`。

## F-047 AndroidEnvClient 任务生命周期方法
- 位置: src/mobile_world/runtime/client.py
- 内容: `initialize_task(self, task_name: str) -> Observation`（POST `/task/init`，timeout=300）→ 截图返回 Observation；`execute_action(self, action: JSONAction) -> Observation`（POST `/step`）；`get_task_score(self, task_type: str) -> tuple[float, str]`（GET `/task/eval`）；`get_task_goal(self, task_type: str) -> str`；`tear_down_task`（POST `/task/tear_down`）；`switch_suite_family(self, target_family: str) -> dict`（POST `/suite_family/switch`，timeout=300）；`get_suite_task_list(self, enable_mcp=False, enable_user_interaction=False)` 按 tags 过滤 `"agent-mcp"` 与 `"agent-user-interaction"`；`health() -> bool` 查 `/health` 的 `ok` 字段。

## F-048 AndroidMCPEnvClient 工具过滤
- 位置: src/mobile_world/runtime/client.py
- 内容: `class AndroidMCPEnvClient(AndroidEnvClient)`，`__init__` 调 `init_mcp_clients()` 后 `self.tools = mcp_client.list_tools_sync()`，`self.tool_map = {tool["name"]: mcp_client for tool in self.tools}`；`reset_tools(self, filters: list[str] = None, task_type=None)`：查任务 metadata，无 `"agent-mcp"` tag 时置空 tools；有则按 `metadata["apps"]` 中含 `"MCP"` 的项取 `app.split("-")[-1]` 作为过滤词；`execute_action` 中 `action.action_type == MCP` 时 `client.call_tool_sync(action_name, action_args)`，结果若以 `<!DOCTYPE html>` 开头经 `markdownify` 转换（`_truncate_tool_call`）。

## F-049 AndroidController 初始化
- 位置: src/mobile_world/runtime/controller.py
- 内容: `class AndroidController`，`__init__(self, device="emulator-5554")`：`self.screenshot_dir = "/sdcard"`、`self.xml_dir = "/sdcard"`、`self.ac_xml_dir = "/sdcard/Android/data/com.example.android.xml_parser/files"`；`self.width, self.height = self.get_device_size()`（`adb shell wm size` 解析）；实例属性 `interaction_cache = ""`、`user_agent_chat_history = []`、`user_sys_prompt = None`、`model_config = None`。模块级 `APP_LOWER_DICT` 由 COMMON_APP_MAPPER 与 APP_DICT 小写化合并。

## F-050 AndroidController 方法清单
- 位置: src/mobile_world/runtime/controller.py
- 内容: 方法签名（共 32 个，不含 `__init__`）：`get_device_size`、`get_screenshot(self, prefix, save_dir, try_times: int = 0) -> AdbResponse`（先试 `exec-out screencap -p` 重定向，失败回退 `shell screencap` + `pull` + `rm`）、`get_xml(self, prefix, save_dir)`、`get_ac_xml(self, prefix, save_dir)`、`get_current_activity`、`get_current_app`、`back/enter/home/app_switch() -> AdbResponse`、`tap(self, x: int, y: int)`、`double_tap(self, x: int, y: int)`、`text(self, input_str: str)`、`simulate_sms(self, sender: str | None, message: str | None)`、`long_press(self, x: int, y: int, duration: int = 1000)`、`kill_package(self, package_name: str)`、`swipe(...)`、`drag(...)`、`launch_app(self, app_name: str)`、`answer(self, answer_str: str) -> None`、`ask_user(self, agent_question: str) -> str`、`check_ac_survive`、`list_snapshots`、`delete_snapshot(self, tag)`、`create_snapshot(self, tag=None)`、`load_snapshot(self, tag)`、`activate_adb_keyboard`、`check_health(self, try_times: int = 0) -> bool`、`push_file/pull_file/remove_file`、`refresh_media_scan(self, file_path)`。

## F-051 ask_user 的 LLM 用户模拟实现
- 位置: src/mobile_world/runtime/controller.py
- 内容: `ask_user` 校验 `user_sys_prompt`/`model_config` 非空（否则 RuntimeError），调 `user_agent_answer_question(self.user_sys_prompt, agent_question, self.model_config, self.user_agent_chat_history)`，将问答以 `{"role": "user"/"assistant", ...}` 追加进 `user_agent_chat_history`；`answer(answer_str)` 仅设置 `self.interaction_cache = answer_str`。

## F-052 MCP_CONFIG 五个远端 MCP 服务
- 位置: src/mobile_world/runtime/mcp_server.py
- 内容: 模块级 `MCP_CONFIG = {"mcpServers": {...}}` 固定 5 项：`amap`（SSE，`https://dashscope.aliyuncs.com/api/v1/mcps/amap-maps/sse`）、`stockstar`（SSE，dashscope）、`gitHub`（HTTP，modelscope `.../c3c76357651542/mcp`）、`jina`（HTTP，modelscope `.../25a924b9ce914b/mcp`）、`arXiv`（HTTP，modelscope `.../d9b238e019f04e/mcp`）；鉴权头 `Authorization: Bearer {DASHSCOPE_API_KEY}` 或 `Bearer {MODELSCOPE_API_KEY}`（模块加载时 `os.getenv`）。

## F-053 SyncMCPClient 类
- 位置: src/mobile_world/runtime/mcp_server.py
- 内容: `class SyncMCPClient`，`__init__(self, url=None, config=None, max_retries=5, retry_delay=10, retry_backoff=2)`，`self.timeout = 120`；`list_tools()`/`call_tool(name, arguments=None)` 为 async，重试延迟指数递增（`delay *= retry_backoff`）；`list_tools_sync()`/`call_tool_sync()` 用模块级 `client_lock`（`threading.Lock`）串行化，并在已有事件循环时经 ThreadPoolExecutor 提交 `asyncio.run`。`init_mcp_clients() -> SyncMCPClient` 单例化全局 `CLIENT`。

## F-054 JSONAction 模型与动作常量
- 位置: src/mobile_world/runtime/utils/models.py
- 内容: 动作类型常量字面量：`ANSWER="answer"`, `CLICK="click"`, `DOUBLE_TAP="double_tap"`, `FINISHED="finished"`, `INPUT_TEXT="input_text"`, `KEYBOARD_ENTER="keyboard_enter"`, `LONG_PRESS="long_press"`, `NAVIGATE_BACK="navigate_back"`, `NAVIGATE_HOME="navigate_home"`, `OPEN_APP="open_app"`, `SCROLL="scroll"`, `STATUS="status"`, `SWIPE="swipe"`, `UNKNOWN="unknown"`, `WAIT="wait"`, `DRAG="drag"`, `ASK_USER="ask_user"`, `MCP="mcp"`, `ENV_FAIL="error_env"`；`DEFAULT_IMAGE = "ghcr.io/tongyi-mai/mobile_world:latest"`、`DEFAULT_NAME_PREFIX = "mobile_world_env"`。`class JSONAction(BaseModel)` 字段：`action_type/index/x/y/text/direction/goal_status/app_name/keycode/clear_text/start_x/start_y/end_x/end_y/action_name/action_json`；field_validator：action_type 须在 `_ACTION_TYPES` 元组内、direction 须在 `("left","right","down","up")`、keycode 须以 `"KEYCODE_"` 开头、x/y 四舍五入取整、index 转 int；`model_post_init` 校验 index 与 x/y 互斥；`__eq__` 对 app_name/text 忽略大小写比较。请求模型：`InitRequest(device="emulator-5554", type: Literal["cmd","docker"]="cmd", instance: InstanceInfo | None)`、`StepRequest(device, action: JSONAction)`、`TaskOperationRequest(task_name, req_device)`、`SmsRequest(device, sender, message)`、`TaskCallbackRequest(device, callback_data: dict[str, Any])`、`Observation(screenshot, accessibility_tree=None, ask_user_response=None, tool_call=None)`、容器模型 `ContainerInfo/ContainerConfig/LaunchResult/ImageStatus`。

## F-055 APP_DICT 与 COMMON_APP_MAPPER
- 位置: src/mobile_world/runtime/utils/models.py
- 内容: `APP_DICT` 18 项（如 `"淘店": "com.testmall.app"`、`"Mattermost": "com.mattermost.rnbeta"`、`"Mastodon": "org.joinmastodon.android.mastodon"`、`"Mail": "com.gmailclone"`、`"Calendar": "org.fossify.calendar"`、`"Camera": "com.android.camera2"`）；`COMMON_APP_MAPPER` 约 190 项包名→中文名映射（如 `"com.tencent.mm": "微信"`、`"com.alibaba.wireless": "阿里巴巴"`）。

## F-056 artifacts 目录常量
- 位置: src/mobile_world/runtime/utils/constants.py
- 内容: `ARTIFACTS_ROOT = Path(os.getenv("ARTIFACTS_ROOT", "./artifacts")).resolve()`（导入时即 mkdir）；`device_dir(artifacts_root: Path, device: str) -> Path` 返回 `artifacts_root / device` 并 mkdir。

## F-057 TrajLogger 与结果文件名
- 位置: src/mobile_world/runtime/utils/trajectory_logger.py
- 内容: `SCORE_FILE_NAME = "result.txt"`；`parse_result_file`（client.py）解析格式：第 1 行 `score:<float>`，第 2 行 reason。工具函数 `save_screenshot(screenshot, path)`、`extract_click_coordinates(action)`、`extract_drag_coordinates(action)`、`draw_clicks_on_image(image_path, output_path, click_coords)`、`draw_drag_on_image(...)`；`class TrajLogger` 提供 `log_traj/log_tools/log_score/reset_traj`（runner.py 调用）。

## F-058 docker 工具函数
- 位置: src/mobile_world/runtime/utils/docker.py
- 内容: 函数：`run_command(...)`、`docker_ps(include_all=False)`、`list_containers_by_image_substring(...)`、`docker_inspect(container_name)`、`docker_rm(container_name, *, force=True, volumes=False)`、`build_run_command(...)`、`docker_exec_bash(...)`、`docker_exec_replace(container_name, command, *, interactive=True)`、`discover_backends(...)`、`restart_emulator_with_avd(avd_name: str) -> str`（返回新 device_id）。

## F-059 app_helpers 模块职责
- 位置: src/mobile_world/runtime/app_helpers/
- 内容: 7 个模块：`mail.py`（`initialize_inbox(state: str)`、`initialize_attachments()`、`get_sent_email_info()`）；`fossify_calendar.py`（`insert_calendar_event(...)`、`get_calendar_events(...)`，直写日历数据库）；`mall.py`（`class MallConfig(BaseModel)`、`get_config() -> MallConfig`、`set_config(config)`、`clear_config()`、`write_callback_file(callback_data: dict, task_name: str, device_name: str) -> str`、`clear_callback_files(device_name)`、`get_recent_callback_content(num: int = 1)`）；`mastodon.py`（约 50 个函数：`start/stop/restart_mastodon_backend`、`connect_to_postgres()`、`get_latest_toots_by_username(username, limit=1)`、`compute_phash(file_path) -> int` 等，含 `parse_dt(dt, tz="Europe/London")`）；`mattermost.py`（`class MattermostCLI`、`mattermost_operation(...)`、`start/stop/restart_mattermost_backend`、`_extend_session_expiry()`、`connect_to_postgres()`、`get_latest_messages()` 等）；`mcp.py`（async 工具封装：`get_stocks_esg_ratings`、`get_high_dividend_stocks`、`query_weather`、`calculate_distance`、`plan_route`、`search_arxiv_papers(query, max_results=5)` 等）；`system.py`（`time_sync_to_now()`，base.py 的 initialize_task_hook 调用）。

## F-060 BaseTask 抽象接口
- 位置: src/mobile_world/tasks/base.py
- 内容: `class BaseTask(abc.ABC)`，类属性 `start_on_home_screen = True`；`__init__(self, params: dict[str, Any] = None)` 设 `initialized=False`、`self.apps_require_time_sync = ["Chrome", "Maps", "MCP-arXiv"]`；抽象 property：`app_names -> set[str]`、`goal -> str`；非抽象 property：`task_tags -> set[str]`（默认空集）、`name -> str`（返回 `self.__class__.__name__`）、`snapshot_tag -> str | None`（默认 `"init_state"`）；`_compute_current_date()`：app_names 含 time_sync 应用时返回当天日期，否则字面量 `"2025-10-16"`。

## F-061 initialize_task 流程
- 位置: src/mobile_world/tasks/base.py
- 内容: `initialize_task(self, controller: AndroidController) -> bool | None` 顺序执行：`reset_task_state()` → 刷新 `current_date` → `controller.load_snapshot(self.snapshot_tag)`（成功后 `app_switch()`+`home()`+sleep(2)）→ 时间同步（app_names 命中 apps_require_time_sync 时 `time_sync_to_now()`）→ `mattermost.stop_mattermost_backend()` + `mastodon.stop_mastodon_backend()` + `clear_config()` + `clear_callback_files(controller.device)` → `initialize_task_hook(controller)`（默认实现 `time_sync_to_now()`）→ `initialize_user_agent_hook(controller)` → `controller.home()` → `controller.interaction_cache = ""`、`user_agent_chat_history = []`、`initialized = True`。

## F-062 用户代理初始化与默认配置
- 位置: src/mobile_world/tasks/base.py
- 内容: `initialize_user_agent_hook` 默认 `self.relevant_information = "No more task-related information can be provided."`；构造 user_sys_prompt（含 goal、relevant_information、拒绝无关提问规则、`Today is {self.current_date}`）；无 `self.model_config` 时用 `ModelConfig(model_name=os.getenv("USER_AGENT_MODEL", "gpt-4o-mini"), api_key=os.getenv("USER_AGENT_API_KEY", ""), url=os.getenv("USER_AGENT_BASE_URL", "https://api.openai.com/v1"))`。`is_successful(self, controller) -> float | tuple[float, str]` 约定 `(0.0, reason)` 失败 / `(1.0, reason)` 成功，未被子类覆盖时转调 `is_successful_async`；`tear_down` 清空 interaction_cache/user_sys_prompt/model_config/chat_history。

## F-063 TaskRegistry 自动扫描注册
- 位置: src/mobile_world/tasks/registry.py
- 内容: `class TaskRegistry`，`__init__(self, task_set_path: str | None = None)`：默认路径为 `Path(mobile_world.__file__).parent / "tasks" / "definitions"`；`_scan_and_register_tasks()` 用 `Path(self.task_set_path).rglob("*.py")` 递归扫描（跳过 `__init__.py`），逐文件 `spec_from_file_location` 动态加载；`_register_tasks_from_module` 注册满足 `issubclass(obj, BaseTask) and obj is not BaseTask and obj.__module__ == module.__name__` 的类，键为类名，重复时覆盖并 warning；实例存 `self.tasks: dict[str, object]`；类属性 `_scan_logged: set[str]` 防重复日志；查询接口 `get_task(task_name)`（KeyError）、`list_tasks()`、`has_task(task_name)`。

## F-064 ModelConfig 与用户模拟应答函数
- 位置: src/mobile_world/tasks/utils.py
- 内容: `@dataclass class ModelConfig: model_name: str; api_key: str; url: str`；`user_agent_answer_question(sys_prompt: str, agent_question: str, model_config: ModelConfig, chat_history: list[dict[str, str]] = None) -> str`：OpenAI 客户端请求参数 `temperature=0.0, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0, seed=42`；`wait_for_execution(controller=None, answer_text=None)` 用 `input()` 等待人工执行（仅测试用）；模块顶部 `load_dotenv()`。

## F-065 任务测试脚本
- 位置: src/mobile_world/tasks/test_task.py
- 内容: argparse 参数 `--task/-t`、`--device/-d`（default "emulator-5554"）、`--question/-q`、`--list/-l`；`--list` 打印 `registry.list_tasks()` 排序清单；否则 `task.run_task(controller=controller, agent_question=args.question)`（注：BaseTask.run_task 实际签名为 `run_task(self, agent_question=None)`，自行创建 `AndroidController(device="emulator-5554")`）。

## F-066 任务定义目录结构
- 位置: src/mobile_world/tasks/definitions/
- 内容: 10 个场景子目录（任务文件数不含 `__init__.py`）：`work/`（35 个，mattermost_*.py 16 个、search_*/extract_*/email 类等）、`settings/`（7 个：open_flight_mode、close_flight_mode、change_wallpaper、adjust_font_icon_min/max、adjust_brigtness_min/max）、`native/`（33 个：set_alarm、take_selfie、read_paper_1..5、check_invoice_1..4、sms_management 等）、`messages/`（23 个：send_weather_sms、plan_*_route_sms、check_candidate_ask_user 等）、`mastodon/`（41 个：mastodon_follow、mastodon_post_poll、mastodon_mall_purchase_commodity 等）、`map/`（10 个：check_distance、check_phone_numbers、text_arrival_time 等）、`mall/`（13 个：cart_management、item_checkout、buy_cola_ask_user 等）、`gmail/`（21 个）、`chrome/`（4 个）、`calendar/`（14 个）；`work/assets/visual_instruction/generate_images.py` 为资产生成脚本。

## F-067 Dockerfile 基础镜像与构建内容
- 位置: docker/Dockerfile
- 内容: `FROM cruizba/ubuntu-dind:latest`；安装 `openjdk-17-jdk、scrcpy、ffmpeg、xvfb、x11vnc、openbox、novnc、websockify、socat` 等；Android SDK：`commandlinetools-linux-13114758_latest.zip` + `emulator-linux_x64-14214601.zip` + `sdkmanager "platform-tools" "build-tools;34.0.0" "platforms;android-34" "system-images;android-34;google_apis;x86_64"`；`ENV AVD_NAME=Pixel_8_API_34_x86_64`，COPY `docker/${AVD_NAME}.avd`、`.ini`、`adbkey/adbkey.pub` 至 `/root/.android/`；`COPY docker/mattermost-docker /app/mattermost-docker-bk`、`docker/mastodon-docker /app/mastodon-docker-bk`（chown 991:991）、`docker/images /app/images`；`uv sync`；`HEALTHCHECK ... CMD curl -f http://localhost:6800/health || exit 1`；`CMD tail -f /var/log/emulator.log /var/log/server.log /var/log/dockerd.err.log`。

## F-068 entrypoint.sh 启动序列
- 位置: docker/entrypoint.sh
- 内容: 顺序：① 代理规范化并强制 `no_proxy="10.0.2.2,127.0.0.1,localhost,::1[,用户值]"`；② `sysctl net.ipv6.conf.all.disable_ipv6=1`（注释引用 Google issue 215231636，禁 IPv6 以保 SIM 卡可用）；③ iptables 后端自动探测（先 `iptables-nft -L -n` 成功则设 nft，否则 legacy）；④ `start-docker.sh` 后 30 秒内轮询 `docker info`，超时打印 `dockerd.err.log` 末 20 行并 exit 1；⑤ `cd /app/images && for f in *.tar; do docker load -i "$f"; done`；⑥ `ENABLE_VNC=true/1` 时启动 `start_novnc.sh` + `uv sync --extra dev --no-cache`，否则 `uv run mobile-world viewer --port 7860 &`；⑦ `/app/docker/start_emulator.sh`；⑧ `socat TCP-LISTEN:5556,fork,reuseaddr,bind=0.0.0.0 TCP:127.0.0.1:5555 &`（ADB 中继）；⑨ `uv run mobile-world server --port 6800 >> /var/log/server.log 2>&1 &`；⑩ `exec "$@"`。

## F-069 start_emulator.sh 行为
- 位置: docker/start_emulator.sh
- 内容: 先 kill 现有 emulator（`adb devices | grep emulator | cut -f1 | xargs -I {} adb -s "{}" emu kill`）；`options="-no-audio -no-snapshot -gpu swiftshader_indirect"`；`ENABLE_VNC` 开启时有窗口（`DISPLAY=:0`），否则 `-no-window`；启动日志写 `/var/log/emulator.log`；`check_emulator_status` 轮询 `adb shell getprop sys.boot_completed`，超时 `${EMULATOR_TIMEOUT:-600}` 秒，成功后 `adb shell input keyevent 82`；`disable_animation` 置三个 animation scale 为 0.0；配置 HTTP 代理时启动 `proxy_chain.py`（`LOCAL_PROXY_PORT` 默认 38888）并 `adb shell settings put global http_proxy "10.0.2.2:${LOCAL_PROXY_PORT}"`；最后 `adb root`。

## F-070 proxy_chain.py 旁路代理
- 位置: docker/proxy_chain.py
- 内容: 文档字符串声明拓扑 `emulator app → proxy_chain.py(listens 0.0.0.0:LOCAL_PORT) → {10.0.2.x/127.*/localhost 直连 | 其余转发 UPSTREAM_PROXY}`；`is_bypass(host)` 精确匹配 `localhost/127.0.0.1/::1` 与前缀 `10.0.2.`、`127.`；`rewrite_bypass_host(host)` 将 `10.0.2.*` 重写为 `127.0.0.1`（10.0.2.2 仅为 guest 侧 slirp 网关别名）；环境变量 `UPSTREAM_PROXY`（必需）与 `LOCAL_PORT`（默认 38888）；日志写 `/var/log/proxy_chain.log`。

## F-071 Docker 镜像版本历史
- 位置: docs/docker_changelog.md
- 内容: v1.0（2025-12-24，初版，基础镜像 cruizba/ubuntu-dind，Android SDK 34 + Pixel_8_API_34_x86_64 AVD + emulator build 14214601 + DinD + noVNC）；v1.1（加 socat 做 ADB 中继 0.0.0.0:5556→127.0.0.1:5555，CMD 增加 tail dockerd.err.log）；v1.2（2026-04-12，修 kernel 6.x+ 缺 iptable_nat 导致的 dockerd 静默失败——默认 iptables-nft 并自动回退 legacy；entrypoint 用 `docker info` 30 秒验证 dockerd 可用；`mw env check` 新增 iptables NAT 检查）。

## F-072 四个评测 shell 脚本的公共模式
- 位置: scripts/run_agentic.sh、run_claude_e2e.sh、run_gemini_e2e.sh、run_qwen3vl.sh
- 内容: 每个脚本第一行均为 `sudo mw env run --count 5 --launch-interval 20`；随后 `sudo mw eval --agent_type <X> --task ALL --max_round 50 --step_wait_time 3 --enable_mcp --enable_user_interaction`。差异：run_agentic 用 `planner_executor` + `--executor_agent_class uiins`（executor 模型与 planner 模型分别传占位符）；run_claude_e2e 用 `general_e2e` + `HISTORY_N_IMAGES=3` + `--model_name claude-sonnet-4-5-20250929`（注释说明 general_e2e 按名称含 "claude" 部分匹配触发图像缩放）；run_gemini_e2e 用 `general_e2e` + `HISTORY_N_IMAGES=3` + `--model_name gemini-3-pro-preview`；run_qwen3vl 用 `qwen3vl` + `--model_name Qwen3-VL-235B-A22B` + `--log_file_root traj_logs/qwen3_vl_logs`。

## F-073 docs: configure_avd.md 的 AVD 定制流程
- 位置: docs/configure_avd.md
- 内容: 8 步流程：`sudo mobile-world env run --image mobile_world:v1.1 --dev` 启动 dev 容器 → `mobile-world env exec mobile_world_env_0_dev` 进入 → `adb emu avd snapshot load init_state` → VNC 页面手动配置 → 定日期 `adb shell su root date 101612002025.00`（2025-10-16 12:00:00）→ `adb emu avd snapshot save init_state` + `adb emu kill` → `docker cp mobile_world_env_0_dev:/root/.android/avd/Pixel_8_API_34_x86_64.avd docker/` → `docker buildx build -t mobile_world:v1.2 -f docker/Dockerfile .`。

## F-074 docs: real-devices.md 真机评测
- 位置: docs/real-devices.md
- 内容: 前置：USB 物理手机 + ADB；ADBKeyboard.apk 可选（未装时 MobileWorld 自动安装）；服务启动 `uv run mobile-world server`；任务运行示例 `uv run mw test "set an alarm at 8:00 am" --agent-type general_e2e --model_name anthropic/claude-sonnet-4-5 --llm_base_url https://openrouter.ai/api/v1 --aw-host http://127.0.0.1:6800 --api_key ...`；模型表：Claude Opus 4.7 绝对像素坐标、Gemini 3 Pro 与 Qwen-3.5 与 Seed-2.0-Pro 相对坐标 0–1000、Kimi K2.6/K2.5 相对 0–1、Claude Sonnet 4.5 需图像缩放至 1280×720；Seed-2.0-Pro 用 `seed_agent`。

## F-075 docs: submit.md 提交流程
- 位置: docs/submit.md
- 内容: 三步：① `uv run python site/bundle_trajs.py traj_logs/your_run -o site/trajs/your-model.json.gz [--with-screenshots --video-base-url ...]`；② 按 `site/leaderboard.json` 既有条目格式新增对象（字段 model/organization/date/link/category/model_type/max_steps/runs/gui_only/user_int/mcp/agent_type/num_images_in_history/notes/traj_file；`category` 必须为 `Agentic/General/Specialized` 之一）；③ 经 GitHub issue 或 Contact 提交 `.json.gz` 与 entry。

## F-076 docs: mcp_setup.md 服务商清单
- 位置: docs/mcp_setup.md
- 内容: 两个 MCP 提供商：DashScope（amap=AMap Maps SSE、stockstar=证券金融数据 SSE）与 ModelScope（gitHub/jina/arXiv，均 HTTP）；需配置 `DASHSCOPE_API_KEY` 与 `MODELSCOPE_API_KEY`；市场入口 `https://bailian.console.aliyun.com/#/mcp-market` 与 `https://modelscope.cn/mcp`。

## F-077 docs: development.md dev 模式
- 位置: docs/development.md
- 内容: `mobile-world env run --dev` 挂载本地 `src/` 至 `/app/service/src` 并自动启用 VNC，仅支持单容器；`mobile-world env restart <container_name>` 重启容器内服务（服务由 `uv run mobile-world server` 启动）；容器内日志 `tail -f /app/service/logs/server.log`，测试 `cd /app/service && uv run pytest`。

## F-078 CHANGELOG 时间线与关键数字
- 位置: CHANGELOG.md
- 内容: 条目：2025-12-23 初版发布（arXiv 2512.19432，镜像 `ghcr.io/Tongyi-MAI/mobile_world:latest`）；2025-12-29 MAI-UI 41.7%；2026-01-16 Seed-1.8 52.1% GUI-Only、MAI-UI-235B-A22B 45.4%；2026-03-20 Seed-2.0-Pro 63.2%/61.4% + 真机支持（gui_owl_1_5、ui_venus_agent 两个新 agent）；2026-04-15 Mattermost 会话过期修复（任务初始化时自动运行，无需重建镜像）；2026-04-22 加入 Claude-Opus-4.7 与 Kimi-K2.6；2026-04-29 Arena 对比页 + `site/bundle_trajs.py` 社区提交。

## F-079 .github 工作流
- 位置: .github/workflows/deploy-pages.yml
- 内容: 唯一工作流文件 `deploy-pages.yml`（GitHub Pages 部署，与 site/ 目录配套；site/ 下含 leaderboard.json、bundle_trajs.py、trajs/*.json.gz 轨迹包）。

## F-080 windows 安装文档
- 位置: docs/setup_for_windows.md
- 内容: 要求 WSL 安装（`wsl --install`）、KVM 组授权（`sudo usermod -a -G kvm ${USER}`）、`/etc/wsl.conf` 添加 `[boot] command = /bin/bash -c 'chown -v root:kvm /dev/kvm && chmod 660 /dev/kvm'` 与 `[wsl2] nestedVirtualization = true`。

## 模块覆盖核对表

| 模块 | 已读文件 |
|---|---|
| 根配置 | pyproject.toml、CHANGELOG.md、.env.example、.gitmodules、.gitignore（略读） |
| agents/ | base.py、registry.py、__init__.py（空文件）、grounding/uiins.py、grounding/__init__.py、utils/agent_mapping.py、utils/helpers.py、utils/test_agent.py、utils/prompts/（存在 10 个 prompt 文件，未逐字读取，仅确认文件清单）、implementations/（9 个实现类经 registry.py 导入关系确认，未逐字读取） |
| core/ | cli.py、runner.py、server.py、device_viewer.py、api/server.py、api/env.py、api/info.py（经 info.py 调用确认）、eval_server/app.py、eval_server/db.py、eval_server/routes.py（路由清单）、eval_server/worker.py、log_viewer/routes.py（签名）、log_viewer/（文件清单）、subcommands/__init__.py、subcommands/eval.py、subcommands/server.py、subcommands/env.py、subcommands/info.py、subcommands/logs.py、subcommands/device.py（签名）、subcommands/test.py、subcommands/eval_server.py、user_task_runner/runner.py（签名） |
| runtime/ | client.py、controller.py（方法清单 + ask_user/answer 实现）、mcp_server.py、app_helpers/（7 模块签名清单：mail、fossify_calendar、mall、mastodon、mattermost、mcp、system）、utils/models.py、utils/constants.py、utils/docker.py（签名清单）、utils/trajectory_logger.py（常量与函数清单） |
| tasks/ | base.py、registry.py、utils.py、test_task.py、definitions/（8 场景子目录文件清单统计） |
| docs/ | configure_avd.md、development.md、mcp_setup.md、real-devices.md、setup_for_windows.md、submit.md、docker_changelog.md（全部 7 个） |
| scripts/ | run_agentic.sh、run_claude_e2e.sh、run_gemini_e2e.sh、run_qwen3vl.sh（全部 4 个） |
| docker/ | Dockerfile、entrypoint.sh、start_emulator.sh、proxy_chain.py（Dockerfile.update、start_novnc.sh 未逐字读取，行为经 docker_changelog.md 与 entrypoint.sh 交叉确认） |
| 其他 | .github/workflows/deploy-pages.yml（存在性） |
| 排除项 | .git/、site/trajs/*.gz、assets/、docker/mastodon-docker/data/（按任务要求跳过） |
