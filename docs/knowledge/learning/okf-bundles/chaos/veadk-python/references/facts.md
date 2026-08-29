# veadk-python 源码事实采集（R 阶段）

> 采集对象：`d:\AI\vendor\veadk-python\`
> 采集原则：零推测，每条事实标注源码文件:行号
> 采集日期：2026-08-23

---

## 一、项目元信息

### F-001 项目名称与描述
- 包名：`veadk-python`
- 描述：`Volcengine agent development kit, integrations with Volcengine cloud services.`
- 来源：`pyproject.toml:6-8`

### F-002 版本管理
- 版本为动态字段（`dynamic = ["version"]`），由 `setuptools-scm` 从最新 git tag 派生
- 回退版本：`0.0.0`
- 来源：`pyproject.toml:7,129-130`
- 运行时通过 `importlib.metadata.version("veadk-python")` 获取；未安装时回退为 `"0.0.0+unknown"`
- 来源：`veadk/version.py:18-25`

### F-003 Python 版本要求
- `requires-python = ">=3.10"`
- 来源：`pyproject.toml:10`

### F-004 许可证
- Apache License 2.0，许可证文件为 `LICENSE`
- 来源：`pyproject.toml:11`

### F-005 作者列表
- Yaozheng Fang <fangyozheng@gmail.com>
- Guodong Li <cu.eric.lee@gmail.com>
- Zhi Han <sliverydayday@gmail.com>
- Meng Wang <mengwangwm@gmail.com>
- 来源：`pyproject.toml:12-17`

### F-006 核心依赖
- `pydantic-settings==2.10.1`（配置管理）
- `a2a-sdk==0.3.7`（Google Agent2Agent 协议）
- `google-adk>=1.34.0`（基础 Agent 架构）
- `litellm>=1.83.7`（LiteLlm 模型）
- `sqlalchemy>=2,<3`（会话存储）
- `python-dotenv>=1.1.0`
- `volcengine-python-sdk>=5.0.36`（火山引擎 API 与 Ark Responses）
- `volcengine>=1.0.193`（火山引擎签名与 AgentKit Runtime API）
- `omegaconf==2.3.0`（Agent Builder）
- `fastmcp>=2.12.3`、`mcp==1.26.0`（MCP 支持）
- `cookiecutter==2.6.0`（云部署模板）
- `jinja2==3.1.6`（模板引擎）
- `vikingdb-python-sdk>=0.1.3`（Viking DB）
- `tos>=2.8.4`（TOS 对象存储）
- 来源：`pyproject.toml:18-55`

### F-007 可选依赖组
- `codex`：`openai-codex==0.1.0b3`、`openai-codex-cli-bin==0.137.0a4`
- `extensions`：redis、cozeloop、llama-index 系列、opensearch-py、pymilvus、lark-channel-sdk、lark-oapi
- `database`：redis、pymysql、volcengine、mem0ai>=1.0.0,<2
- `a2ui`：`a2ui-agent-sdk>=0.2.1`
- `eval`：prometheus-client、deepeval>=3.2.6、google-adk[eval]
- `harness`：headroom
- `dev`：pre-commit、pytest、pytest-asyncio、pytest-xdist
- 来源：`pyproject.toml:60-104`

### F-008 CLI 入口点
- 控制台脚本：`veadk = "veadk.cli.cli:veadk"`
- 来源：`pyproject.toml:57-58`

### F-009 构建系统
- 构建后端：`setuptools.build_meta`
- 构建依赖：`setuptools>=64`、`setuptools-scm>=8`
- 来源：`pyproject.toml:1-3`

### F-010 包发现规则
- 包含：`veadk*`、`frontend`、`frontend.server*`
- 排除：`assets*`、`ide*`、`tests*`
- 包数据：`"veadk" = ["**/*"]`（包含所有包内文件）
- 来源：`pyproject.toml:115-123`

---

## 二、包导出与版本

### F-011 顶层包 `__init__.py`
- 使用 `TYPE_CHECKING` 进行类型标注的懒加载
- 通过 `__getattr__` 实现 `Agent` 和 `Runner` 的懒导入
- `__all__ = ["Agent", "Runner", "VERSION"]`
- 来源：`veadk/__init__.py:15-37`

### F-012 懒加载机制
- 访问 `veadk.Agent` 时从 `veadk.agent` 导入 `Agent`
- 访问 `veadk.Runner` 时从 `veadk.runner` 导入 `Runner`
- 未定义属性抛出 `AttributeError`
- 来源：`veadk/__init__.py:25-34`

---

## 三、Agent 核心类

### F-013 Agent 类定义与继承
- `class Agent(LlmAgent)`：继承自 Google ADK 的 `LlmAgent`
- 模块导入时执行三个补丁函数：`patch_tracer()`、`patch_asyncio()`、`patch_mcp_session_retry()`
- 来源：`veadk/agent.py:32,66-68,72`

### F-014 Agent Pydantic 配置
- `model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")`
- 来源：`veadk/agent.py:105`

### F-015 Agent 核心字段（身份与指令）
- `id: str`：默认 `uuid4().split("-")[0]`（8 字符短 ID）
- `name: str = DEFAULT_AGENT_NAME`（值为 `"veAgent"`）
- `description: str = DEFAULT_DESCRIPTION`
- `instruction: Union[str, InstructionProvider] = DEFAULT_INSTRUCTION`
- 来源：`veadk/agent.py:107-110`；`veadk/consts.py:20`；`veadk/prompts/agent_default_prompt.py:15-30`

### F-016 Agent 模型配置字段
- `model_name: Union[str, list[str]]`：默认 `settings.model.name`，支持列表（首个为主模型，其余为 fallback）
- `model_provider: str`：默认 `settings.model.provider`
- `model_api_base: str`：默认 `settings.model.api_base`
- `model_api_key: str = ""`
- `model_api_key_name: str`：默认 `settings.model.api_key_name`
- `model_extra_config: dict = Field(default_factory=dict)`
- 来源：`veadk/agent.py:112-124`

### F-017 Agent 工具与子代理字段
- `tools: list[ToolUnion] = []`
- `sub_agents: list[BaseAgent] = Field(default_factory=list, exclude=True)`
- 来源：`veadk/agent.py:126-128`

### F-018 Agent 扩展组件字段
- `prompt_manager: Optional[BasePromptManager] = None`
- `knowledgebase: Optional[KnowledgeBase] = None`
- `short_term_memory: Optional[ShortTermMemory] = None`
- `long_term_memory: Optional[LongTermMemory] = None`
- `tracers: list[BaseTracer] = []`
- `run_processor: Optional[BaseRunProcessor] = Field(default=None, exclude=True)`
- `example_store: Optional[BaseExampleProvider] = None`
- 来源：`veadk/agent.py:130-172`

### F-019 Agent 功能开关字段
- `enable_responses: bool = False`（Ark Responses API）
- `enable_responses_cache: bool = True`（多轮 `previous_response_id` 复用）
- `enable_authz: bool = False`（授权检查）
- `auto_save_session: bool = False`（自动保存到长期记忆）
- `enable_supervisor: bool = False`（监督者流程）
- `enable_ghostchar: bool = False`（幽灵字符）
- `enable_dataset_gen: bool = False`（数据集生成）
- `enable_dynamic_load_skills: bool = False`（动态技能加载）
- `enable_skills_checklist: bool = False`
- `enable_a2ui: bool = False`（Agent 驱动 UI）
- `enable_tunnel: bool = False`（隧道工具）
- 来源：`veadk/agent.py:139-212`

### F-020 Agent 技能字段
- `skills: list[str] = Field(default_factory=list)`
- `skills_mode: Optional[Literal["skills_sandbox", "aio_sandbox", "local"]] = None`
- `_skills_with_checklist: Dict[str, Any] = {}`（私有属性）
- 来源：`veadk/agent.py:168-182`

### F-021 Agent 运行时字段
- `runtime: Literal["adk", "codex", "piagent"] = "adk"`
- `codex_runtime_config: Optional[Any] = None`
- 非 `"adk"` 运行时在 `veadk.runtime` 模块下实现
- 来源：`veadk/agent.py:184-193`

### F-022 Agent A2UI 字段
- `a2ui_catalog: Optional[Any] = None`：接受 catalog JSON 路径、`BaseA2UICatalog`、`A2uiCatalog` 或预构建元组
- 来源：`veadk/agent.py:200-206`

### F-023 Agent `model_post_init` 方法签名
- `def model_post_init(self, __context: Any) -> None`
- 来源：`veadk/agent.py:214`

### F-024 API Key 解析优先级
1. 显式 `model_api_key`
2. 环境变量 `MODEL_AGENT_API_KEY`
3. `model_api_key_name` / `MODEL_AGENT_API_KEY_NAME`（通过 `get_ark_token` 按名称解析）
4. `settings.model.api_key`（账户首个 ARK key）
- 来源：`veadk/agent.py:223-232`

### F-025 模型实例化逻辑
- `enable_responses=True` 时创建 `ArkLlm` 实例
- 否则创建 `LiteLlm` 实例
- 模型名格式为 `f"{self.model_provider}/{model_name}"`
- 当 `model_name` 为列表时，首个为主模型，其余为 `fallbacks`
- 来源：`veadk/agent.py:256-293`

### F-026 默认请求头与 Body
- `extra_headers` 包含：`x-is-encrypted`、`veadk-source`、`veadk-version`、`User-Agent`、`X-Client-Request-Id`
- `extra_body` 包含：`caching.type`（默认 `enabled`）、`expire_at`（当前时间 + 3600 秒）
- 用户配置通过 `|=` 合并到默认值
- 来源：`veadk/agent.py:239-252`；`veadk/consts.py:25-42`

### F-027 知识库工具自动挂载
- 若 `knowledgebase` 存在，自动追加 `LoadKnowledgebaseTool`
- 若 `knowledgebase.enable_profile=True`，额外追加 `load_kb_queries`
- 来源：`veadk/agent.py:306-324`

### F-028 长期记忆工具自动挂载
- 若 `long_term_memory` 存在，追加 Google ADK 的 `load_memory` 工具
- 设置 `load_memory.custom_metadata["backend"]` 为长期记忆后端名
- 来源：`veadk/agent.py:326-333`

### F-029 授权回调注册
- `enable_authz=True` 时，将 `check_agent_authorization` 注册到 `before_agent_callback`
- 支持回调为单个函数或列表
- 来源：`veadk/agent.py:335-349`

### F-030 Prompt Manager 集成
- 若 `prompt_manager` 存在，将 `self.instruction` 设置为 `self.prompt_manager.get_prompt`（可调用对象）
- 来源：`veadk/agent.py:351-352`

### F-031 自动保存会话
- `auto_save_session=True` 且 `long_term_memory` 存在时，将 `save_session_to_long_term_memory` 注册到 `after_agent_callback`
- 若长期记忆未初始化则记录警告
- 来源：`veadk/agent.py:354-375`

### F-032 技能加载流程
- `skills` 非空时调用 `self.load_skills()`
- `enable_skills_checklist=True` 时注册 `create_init_skill_check_list_callback` 到 `before_tool_callback`
- 来源：`veadk/agent.py:377-397`

### F-033 其他功能自动挂载
- `example_store` → 追加 `ExampleTool`
- `enable_ghostchar` → 追加 `GhostcharTool`，在指令后追加 `<` 字符要求
- `enable_a2ui` → 追加 `build_a2ui_toolset(catalog=self.a2ui_catalog)`
- `enable_tunnel` → 追加 `TunnelToolset(agent_name=self.name)`
- `enable_dataset_gen` → 注册 `dataset_auto_gen_callback` 到 `after_agent_callback`
- 来源：`veadk/agent.py:399-438`

### F-034 `update_model` 方法
- `def update_model(self, model_name: str)`
- 通过 `self.model.model_copy(update={"model": f"{self.model_provider}/{model_name}"})` 更新模型
- 来源：`veadk/agent.py:447-451`

### F-035 `load_skills` 方法
- `def load_skills(self)`
- 技能模式自动判定：无 `AGENTKIT_TOOL_ID` 环境变量时为 `"local"`；否则通过 AgentKit API 获取工具类型判定为 `"skills_sandbox"` 或 `"aio_sandbox"`
- 本地模式已标记为 `DeprecationWarning`
- 技能来源：本地目录（`load_skills_from_directory`）或云端（`load_skills_from_cloud`）
- 将技能名称和描述追加到 `instruction`
- 最后追加 `SkillsToolset(self.skills_dict, self.skills_mode)` 到 tools
- 来源：`veadk/agent.py:453-600`

### F-036 `_validate_tool_dependencies` 方法
- 检查 `video_generate` 和 `video_task_query` 工具的成对存在性
- 缺少任一工具时自动补全另一个
- 来源：`veadk/agent.py:614-643`

### F-037 `_prepare_tracers` 方法
- 通过环境变量 `ENABLE_APMPLUS`、`ENABLE_COZELOOP`、`ENABLE_TLS` 启用对应 exporter
- 无 tracer 时创建 `OpentelemetryTracer`
- 支持 `APMPlusExporter`、`CozeloopExporter`、`TLSExporter`
- 初始化全局 `meter_uploader`
- 来源：`veadk/agent.py:645-696`

### F-038 `_llm_flow` 属性
- `@property def _llm_flow(self) -> BaseLlmFlow`
- 无子代理且禁止转移时返回 `SingleFlow`（或 `SupervisorSingleFlow`）
- 否则返回 `AutoFlow`（或 `SupervisorAutoFlow`）
- `enable_supervisor=True` 时使用监督者流程
- 来源：`veadk/agent.py:698-721`

### F-039 `_run_async_impl` 方法
- `async def _run_async_impl(self, ctx: "InvocationContext") -> AsyncGenerator["Event", None]`
- `runtime == "adk"` 时委托给 `super()._run_async_impl(ctx)`
- 其他运行时通过 `veadk.runtime.get_runtime(self.runtime).run_async(self, ctx)` 调度
- 来源：`veadk/agent.py:723-741`

### F-040 ADK 1.x 兼容的 `run` 方法
- 仅当 `not is_adk_gte("2.0.0")` 时定义
- 抛出 `NotImplementedError`，提示使用 `runner.run_async`
- 来源：`veadk/agent.py:743-751`

---

## 四、AgentBuilder 构建器

### F-041 AgentBuilder 类定义
- `class AgentBuilder:`（无继承）
- 来源：`veadk/agent_builder.py:38`

### F-042 AGENT_TYPES 映射表
- `"Agent"` → `Agent`
- `"SequentialAgent"` → `SequentialAgent`
- `"ParallelAgent"` → `ParallelAgent`
- `"LoopAgent"` → `LoopAgent`
- `"RemoteVeAgent"` → `RemoteVeAgent`
- 来源：`veadk/agent_builder.py:29-35`

### F-043 AgentBuilder._build 方法
- `def _build(self, agent_config: dict) -> BaseAgent`
- 递归构建 `sub_agents`
- 工具通过 `importlib.import_module` 动态导入，格式为 `"module.path.function_name"`
- 根据 `agent_config["type"]` 从 `AGENT_TYPES` 获取类并实例化
- 来源：`veadk/agent_builder.py:42-68`

### F-044 AgentBuilder._read_config 方法
- `def _read_config(self, path: str) -> dict`
- 断言文件以 `.yaml` 结尾
- 使用 `OmegaConf.load` 加载，`OmegaConf.to_container(resolve=True)` 转换为 dict
- 来源：`veadk/agent_builder.py:70-81`

### F-045 AgentBuilder.build 方法
- `def build(self, path: str, root_agent_identifier: str = "root_agent") -> BaseAgent`
- 从 YAML 配置中读取 `root_agent_identifier` 指定的配置段并构建 Agent
- 来源：`veadk/agent_builder.py:83-92`

---

## 五、Agent 类型

### F-046 LoopAgent 类
- `class LoopAgent(GoogleADKLoopAgent)`：继承自 `google.adk.agents.LoopAgent`
- `model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")`
- `name: str = "veLoopAgent"`
- `description: str = DEFAULT_DESCRIPTION`
- `instruction: str = DEFAULT_INSTRUCTION`
- `sub_agents: list[BaseAgent] = Field(default_factory=list, exclude=True)`
- `tracers: list[BaseTracer] = []`
- `model_post_init` 调用父类初始化并记录日志
- 来源：`veadk/agents/loop_agent.py:31-67`

### F-047 ParallelAgent 类
- `class ParallelAgent(GoogleADKParallelAgent)`：继承自 `google.adk.agents.ParallelAgent`
- `name: str = "veParallelAgent"`
- 字段与 LoopAgent 相同（description、instruction、sub_agents、tracers）
- `model_post_init` 中若 tracers 非空，记录 OpenTelemetry 上下文错误警告
- 来源：`veadk/agents/parallel_agent.py:31-72`

### F-048 SequentialAgent 类
- `class SequentialAgent(GoogleADKSequentialAgent)`：继承自 `google.adk.agents.SequentialAgent`
- `name: str = "veSequentialAgent"`
- 字段与 LoopAgent 相同
- `model_post_init` 调用父类初始化并记录日志
- 来源：`veadk/agents/sequential_agent.py:31-63`

### F-049 SuperviseAgent 模块
- `Advice` Pydantic 模型：`advice: str`、`reason: str`
- `instruction` 为 Jinja2 `Template`，指导监督者输出 JSON 格式建议
- `build_supervisor(supervised_agent: Agent) -> Agent`：构建名为 `"supervisor"` 的 Agent，使用 `response_format=Advice`
- `async def generate_advice(agent: Agent, llm_request: LlmRequest) -> str`：创建临时 Runner，将 LLM 请求历史序列化为文本，运行监督者 Agent 获取建议
- 来源：`veadk/agents/supervise_agent.py:25-79`

### F-050 SupervisorAutoFlow 类
- `class SupervisorAutoFlow(SupervisorSingleFlow)`
- `__init__(self, supervised_agent: Agent)`
- 重写 `_call_llm_async`：先调用 `generate_advice` 获取监督建议，将建议作为 user 角色 Content 追加到 `llm_request.contents`，再委托父类方法
- 建议 JSON 包含 `advice` 和 `reason` 字段
- 来源：`veadk/flows/supervise_auto_flow.py:32-70`

---

## 六、配置系统

### F-051 配置加载流程
- 模块加载时自动查找当前工作目录的 `.env` 文件并通过 `load_dotenv` 加载
- 通过 `find_dotenv(filename="config.yaml", usecwd=True)` 查找 `config.yaml`
- 使用 `set_envs` 处理 config.yaml 中的环境变量
- 最终实例化全局 `settings = VeADKConfig()`
- 来源：`veadk/config.py:45-52,133-146`

### F-052 CLOUD_PROVIDER 适配
- 环境变量 `CLOUD_PROVIDER=byteplus` 时，将 `BYTEPLUS_ACCESS_KEY`/`BYTEPLUS_SECRET_KEY` 映射到 `VOLCENGINE_ACCESS_KEY`/`VOLCENGINE_SECRET_KEY`
- 来源：`veadk/config.py:54-61`

### F-053 VeADKConfig 类
- `class VeADKConfig(BaseModel)`
- 字段：
  - `model: ModelConfig`
  - `tool: BuiltinToolConfigs`
  - `prompt_pilot: PromptPilotConfig`
  - `opentelemetry_config: OpenTelemetryConfig`
  - `apmplus_config: APMPlusConfig`
  - `cozeloop_config: CozeloopConfig`
  - `tls_config: TLSConfig`
  - `prometheus_config: PrometheusConfig`
  - `tos: TOSConfig`
  - `opensearch: OpensearchConfig`
  - `mysql: MysqlConfig`
  - `redis: RedisConfig`
  - `milvus: MilvusConfig`
  - `viking_knowledgebase: VikingKnowledgebaseConfig`
  - `veidentity: VeIdentityConfig`
  - `realtime_model: RealtimeModelConfig`
- 来源：`veadk/config.py:64-89`

### F-054 ModelConfig 类
- `class ModelConfig(BaseSettings)`，环境变量前缀 `MODEL_AGENT_`
- `name: str = DEFAULT_MODEL_AGENT_NAME`（`"doubao-seed-2-1-pro-260628"`）
- `provider: str = DEFAULT_MODEL_AGENT_PROVIDER`（`"openai"`）
- `api_base: str = DEFAULT_MODEL_AGENT_API_BASE`（`"https://ark.cn-beijing.volces.com/api/v3/"`）
- `api_key_name: str = ""`
- `api_key` 为 `@cached_property`，优先级：`MODEL_AGENT_API_KEY` 环境变量 > `get_ark_token(api_key_name=...)` > `get_ark_token()`
- 来源：`veadk/configs/model_configs.py:31-54`

### F-055 EmbeddingModelConfig 类
- 环境变量前缀 `MODEL_EMBEDDING_`
- `name: str = "doubao-embedding-vision-250615"`
- `dim: int = 2048`
- `api_base` 同 Agent 模型
- `api_key` 优先级：`MODEL_EMBEDDING_API_KEY` > `MODEL_AGENT_API_KEY` > `get_ark_token()`
- 来源：`veadk/configs/model_configs.py:57-75`

### F-056 RealtimeModelConfig 类
- 环境变量前缀 `MODEL_REALTIME_`
- `name: str = "doubao_realtime_voice_model"`
- `api_base: str = "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"`
- `api_key` 为 `MODEL_REALTIME_API_KEY` 或 `get_speech_token()`
- 来源：`veadk/configs/model_configs.py:93-104`

### F-057 getenv 函数
- `def getenv(env_name: str, default_value: Any = "", allow_false_values: bool = False) -> str`
- BytePlus 提供商下自动映射 AK/SK 环境变量
- 非 `allow_false_values` 模式下，值为空时抛出 `ValueError`
- 来源：`veadk/config.py:92-130`

### F-058 config.yaml.simple 结构
```yaml
model:
  agent:
    provider: openai
    name: doubao-seed-1-6-250615
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:
    encrypted: true
    caching: enabled
    max_llm_calls: 100
```
- 来源：`config.yaml.simple:1-9`

### F-059 config.yaml.full 顶层结构
- `model`：包含 agent、judge、embedding、video、image、edit 子配置
- `volcengine`：access_key、secret_key
- `agentkit`：tool_id、tool_id_script、tool_id_skills、tool_id_opencode、tool_host、tool_service_code、tool_region、tool_scheme、top_scheme
- `tool`：vesearch、web_scraper、text_to_speech、lark、feishu_channel、mobile_use、vod、las、mcp_router、code_sandbox、browser_sandbox、computer_sandbox、llm_shield
- `observability`：opentelemetry（apmplus、cozeloop、tls）、prometheus
- `database`：opensearch、mysql、postgresql、redis、milvus、viking、tos、mem0、openviking、tos_vector、tos_context
- `nacos`：endpoint、password
- `prompt_pilot`：api_key
- `logging`：level
- `veadk`：tracer（apmplus、cozeloop、tls）
- 来源：`config.yaml.full:1-238`

---

## 七、常量定义

### F-060 默认 Agent 名称
- `DEFAULT_AGENT_NAME = "veAgent"`
- 来源：`veadk/consts.py:20`

### F-061 默认模型常量（火山引擎）
- `DEFAULT_MODEL_AGENT_NAME = "doubao-seed-2-1-pro-260628"`
- `DEFAULT_MODEL_AGENT_PROVIDER = "openai"`
- `DEFAULT_MODEL_AGENT_API_BASE = "https://ark.cn-beijing.volces.com/api/v3/"`
- 来源：`veadk/consts.py:22-24`

### F-062 BytePlus 提供商模型常量
- 当 `CLOUD_PROVIDER=byteplus` 时覆盖：
  - Agent 模型：`"dola-seed-2-1-turbo-260628"`，API base 为 `https://ark.ap-southeast.bytepluses.com/api/v3`
  - 图像编辑：`"seededit-3-0-i2i-250628"`
  - 视频：`"dreamina-seedance-2-0-260128"`
  - 图像生成：`"dola-seedream-5-0-pro-260628"`
- 来源：`veadk/consts.py:79-91`

### F-063 多模态模型默认值
- 图像编辑：`doubao-seededit-3-0-i2i-250628`
- 视频生成：`doubao-seedance-2-0-260128`
- 图像生成：`doubao-seedream-5-0-260128`
- Embedding：`doubao-embedding-vision-250615`，维度 2048
- 来源：`veadk/consts.py:65-94`

### F-064 Tracing 默认端点
- APMPlus：`http://apmplus-cn-beijing.volces.com:4317`
- CozeLoop：`https://api.coze.cn/v1/loop/opentelemetry/v1/traces`
- TLS：`https://tls-cn-beijing.volces.com:4318/v1/traces`
- 来源：`veadk/consts.py:44-52`

---

## 八、Runner 运行器

### F-065 Runner 类定义与继承
- `class Runner(ADKRunner)`：继承自 `google.adk.runners.Runner`
- 来源：`veadk/runner.py:329`

### F-066 RunnerMessage 类型别名
```python
RunnerMessage = Union[
    str,                    # 单轮文本
    list[str],              # 多轮文本
    MediaMessage,           # 单轮多模态
    list[MediaMessage],     # 多轮多模态
    list[MediaMessage | str],  # 混合
]
```
- 来源：`veadk/runner.py:46-52`

### F-067 Runner.__init__ 参数
- `agent: BaseAgent | Agent | None = None`
- `short_term_memory: ShortTermMemory | None = None`
- `app_name: str | None = None`
- `user_id: str = "veadk_default_user"`
- `upload_inline_data_to_tos: bool = False`
- `run_processor: BaseRunProcessor | None = None`
- `*args, **kwargs`（可传入 `session_service`、`memory_service`、`credential_service`）
- 来源：`veadk/runner.py:355-365`

### F-068 Runner 初始化逻辑
- run_processor 优先级：Runner 参数 > agent.run_processor > NoOpRunProcessor
- 无 short_term_memory 时从 agent 获取；均无则创建内存版 ShortTermMemory
- 无 memory_service 时从 agent.long_term_memory 获取
- app_name 默认为 `"veadk_default_app"`
- 使用 `MethodType` 将 `intercept_new_message(_upload_image_to_tos)(super().run_async)` 绑定为实例方法
- 来源：`veadk/runner.py:396-466`

### F-069 Runner.run 方法签名
```python
async def run(
    self,
    messages: RunnerMessage,
    user_id: str = "",
    session_id: str = f"tmp-session-{formatted_timestamp()}",
    run_config: RunConfig | None = None,
    save_tracing_data: bool = False,
    upload_inline_data_to_tos: bool = False,
    run_processor: "BaseRunProcessor | None" = None,
) -> str
```
- 来源：`veadk/runner.py:468-477`

### F-070 Runner.run 执行流程
- 默认 `RunConfig(max_llm_calls=int(getenv("MODEL_AGENT_MAX_LLM_CALLS", 100)))`
- 通过 `_convert_messages` 转换消息格式
- 若 short_term_memory 存在，自动创建/获取会话
- 通过 run_processor 的 `process_run` 装饰器包装事件生成器
- 遍历事件，提取最后一条非 thought 的文本作为 `final_output`
- 捕获 `LlmCallsLimitExceededError`
- 可选保存 tracing 文件
- 来源：`veadk/runner.py:504-576`

### F-071 Runner 其他方法
- `get_trace_id() -> str`：从 agent.tracers[0].trace_id 获取
- `save_tracing_file(session_id: str) -> str`：仅支持 Agent/SequentialAgent/ParallelAgent/LoopAgent
- `async save_eval_set(session_id: str, eval_set_id: str = "default") -> str`
- `async save_session_to_long_term_memory(session_id, user_id="", app_name="") -> None`
- 来源：`veadk/runner.py:578-789`

### F-072 intercept_new_message 装饰器
- `def intercept_new_message(process_func)`：装饰器工厂
- 在 `run_async` 前调用 `pre_run_process` 处理 inline_data（上传到 TOS）
- 流式遍历事件，累积 thought 部分并批量日志
- 记录 function call / function response / 文本输出
- 结束后调用 `post_run_process`（当前为空操作）
- 来源：`veadk/runner.py:107-198`

### F-073 _convert_messages 函数
- `def _convert_messages(messages, app_name, user_id, session_id) -> list`
- 支持 str、MediaMessage、list 三种输入
- 多模态消息使用 `filetype` 库检测 MIME 类型，仅支持 `image/*` 和 `video/*`
- 来源：`veadk/runner.py:201-277`

---

## 九、CLI 命令系统

### F-074 CLI 主入口
- `@click.group()` 定义 `veadk` 命令组
- 版本选项：`--version`，prog_name 为 `"Volcengine Agent Development Kit (VeADK)"`
- 来源：`veadk/cli/cli.py:64-74`

### F-075 CLI 注册的子命令
- `deploy`、`init`、`create`、`prompt`、`web`、`frontend`、`studio`
- `pipeline`、`eval`、`kb`、`uploadevalset`、`update`、`clean`
- `rl_group`、`agentkit`、`harness`
- 来源：`veadk/cli/cli.py:77-92`

### F-076 _bootstrap_serve_provider 函数
- 在命令模块加载前执行，检测 `frontend`/`studio` 命令的 `--provider` 参数
- 设置 `AGENTKIT_CLOUD_PROVIDER` 和 `CLOUD_PROVIDER` 环境变量
- 支持 `volcengine` 和 `byteplus`
- 来源：`veadk/cli/cli.py:24-44`

### F-077 create 命令
- 生成 Agent 项目文件：`.env`、`__init__.py`、`agent.py`
- `.env` 模板包含 `MODEL_AGENT_API_KEY={ark_api_key}`
- `agent.py` 模板创建名为 `root_agent` 的 Agent
- 提示用户输入 ARK API Key 或稍后配置
- 来源：`veadk/cli/cli_create.py:20-72`

### F-078 init 命令
- 交互式收集配置：FaaS 应用名、API Gateway 实例/服务/上游名
- 部署模式选择：1=A2A/MCP Server，2=VeADK Web/Google ADK Web
- ADK Web 模式下认证方式：None 或 OAuth2
- A2A 模式下认证方式：None 或 API key
- 来源：`veadk/cli/cli_init.py:27-80`

### F-079 deploy 命令参数
- `--volcengine-access-key`、`--volcengine-secret-key`
- `--vefaas-app-name`（必填）
- `--veapig-instance-name`、`--veapig-service-name`、`--veapig-upstream-name`
- `--short-term-memory-backend`（`local` 或 `mysql`）
- `--use-adk-web`（flag）
- `--auth-method`（`none`/`api-key`/`oauth2`）
- `--user-pool-name`、`--client-name`
- `--path`（默认 `.`）
- `--iam-role`
- 来源：`veadk/cli/cli_deploy.py:23-80`

### F-080 eval 命令参数
- `--agent-dir`（默认 `.`，须导出 `root_agent`）
- `--agent-a2a-url`（远程 A2A 部署 URL）
- `--evalset-file`（必填，Google ADK 格式）
- `--evaluator`（`adk` 或 `deepeval`）
- `--judge-model-name`（默认 `doubao-1-5-pro-256k-250115`）
- `--volcengine-access-key`、`--volcengine-secret-key`
- 来源：`veadk/cli/cli_eval.py:22-66`

### F-081 web 命令功能
- `_patch_adkwebserver_oauth2`：猴子补丁 AdkWebServer，添加 OAuth2 认证中间件（VeIdentity User Pool）
- `patch_adkwebserver_disable_openapi`：禁用 OpenAPI 文档端点（`/openapi.json`、`/docs`、`/redoc`）
- 来源：`veadk/cli/cli_web.py:25-80`

---

## 十、记忆系统

### F-082 ShortTermMemory 类
- `class ShortTermMemory(BaseModel)`
- `backend: Literal["local", "mysql", "sqlite", "postgresql", "database"] = "local"`
- `backend_configs: dict = Field(default_factory=dict)`
- `db_kwargs: dict = Field(default_factory=dict)`
- `db_url: str = ""`（设置后覆盖 backend）
- `local_database_path: str = "/tmp/veadk_local_database.db"`
- `after_load_memory_callback: Callable | None = None`
- `_session_service: BaseSessionService = PrivateAttr()`
- 来源：`veadk/memory/short_term_memory.py:57-91`

### F-083 ShortTermMemory 后端初始化
- `db_url` 设置时使用 `DatabaseSessionService`
- `backend="local"` → `InMemorySessionService`
- `backend="mysql"` → `MysqlSTMBackend`
- `backend="sqlite"` → `SQLiteSTMBackend`
- `backend="postgresql"` → `PostgreSqlSTMBackend`
- `backend="database"` 已弃用，映射到 `sqlite`
- URL 中多个 `@` 或 `:` 时警告需 URL 编码
- 来源：`veadk/memory/short_term_memory.py:93-130`

### F-084 ShortTermMemory 核心方法
- `session_service` 属性返回 `_session_service`
- `async create_session(app_name, user_id, session_id) -> Session | None`：已存在则返回，否则创建
- `async generate_profile(app_name, user_id, session_id, events) -> list[str]`：使用 LLM 将事件分组为 profile，写入 `./profiles/memory/<app>/<user>/<session>/`
- `async compact_history_events(app_name, user_id, session_id, compact_limit, agent)`：压缩历史事件，追加 `load_history_events` 工具
- 来源：`veadk/memory/short_term_memory.py:132-290`

### F-085 MemoryProfile 数据模型
- `class MemoryProfile(BaseModel)`
- `name: str`
- `event_ids: list[str]`
- 来源：`veadk/memory/types.py:18-20`

### F-086 LongTermMemory 类
- `class LongTermMemory(BaseMemoryService, BaseModel)`
- 继承自 Google ADK 的 `BaseMemoryService`
- `backend` 支持：`"local"`、`"opensearch"`、`"redis"`、`"viking"`、`"viking_mem"`（已弃用）、`"mem0"`、`"openviking"`、`"tos_context"`，或 `BaseLongTermMemoryBackend` 实例
- 默认后端：`"opensearch"`
- `backend_config: dict = Field(default_factory=dict)`
- `top_k: int = 5`
- `index: str = ""`
- `app_name: str = ""`
- `user_id: str = ""`（已弃用，保留向后兼容）
- 来源：`veadk/memory/long_term_memory.py:98-149`

### F-087 LongTermMemory 后端工厂
- `_get_backend_cls(backend: str) -> type[BaseLongTermMemoryBackend]`
- 各后端懒加载：
  - `"local"` → `InMemoryLTMBackend`
  - `"opensearch"` → `OpensearchLTMBackend`
  - `"viking"` → `VikingDBLTMBackend`
  - `"redis"` → `RedisLTMBackend`
  - `"mem0"` → `Mem0LTMBackend`
  - `"openviking"` → `OpenVikingLTMBackend`
  - `"tos_context"` → `TosContextBucketLTMBackend`
- llama_index 导入失败时提示安装 `veadk-python[extensions]`
- 来源：`veadk/memory/long_term_memory.py:42-95`

### F-088 LongTermMemory 初始化逻辑
- 传入 backend 实例时直接使用
- `backend_config` 非空时用其初始化（自动补充 `index`）
- 否则使用 `index` 或 `app_name`，均无则使用 `"default_app"`
- `"viking_mem"` 自动映射为 `"viking"`
- 来源：`veadk/memory/long_term_memory.py:151-194`

### F-089 LongTermMemory 核心方法
- `async add_session_to_memory(session: Session, **kwargs)`：过滤并转换事件为 JSON 字符串后存储；`openviking` 后端包含 assistant 事件，其他仅存 user 事件
- `async search_memory(*, app_name, user_id, query) -> SearchMemoryResponse`：检索相关记忆
- `_filter_and_convert_events(events, include_assistant=False)`：过滤无效事件、函数调用，序列化为 JSON
- 来源：`veadk/memory/long_term_memory.py:196-318`

---

## 十一、LLM 模型

### F-090 ArkLlm 类
- `class ArkLlm(Gemini)`：继承自 Google ADK 的 `Gemini`
- `model: str`
- `fallbacks: Optional[List[str]] = None`
- `llm_client: ArkLlmClient = Field(default_factory=ArkLlmClient)`
- `use_interactions_api: bool = True`
- `enable_responses_cache: bool = True`
- 构造时检查 `google-adk>=1.34.0`（需 `previous_interaction_id` 字段）
- 来源：`veadk/models/ark_llm.py:703-730`

### F-091 ArkLlm.generate_content_async 方法
- `async def generate_content_async(self, llm_request: LlmRequest, stream: bool = False) -> AsyncGenerator[LlmResponse, None]`
- 从 LlmRequest 提取 instructions、input_param、tools、text_format、generation_params
- 若 `enable_responses_cache`，从 `get_previous_interaction_id` 获取 `previous_response_id`
- 调用 `_generate_content_with_fallbacks`
- 来源：`veadk/models/ark_llm.py:732-775`

### F-092 ArkLlm 回退机制
- `_generate_content_with_fallbacks` 按顺序尝试主模型和 fallback 模型
- 已 yield 输出后发生错误不进行 fallback（避免混合两个响应的 chunk）
- `PreviousResponseNotFound` 错误时移除 `previous_response_id` 重试
- 来源：`veadk/models/ark_llm.py:777-842`

### F-093 ArkLlm.generate_content_via_responses 方法
- 调用 `request_reorganization_by_ark` 重组请求参数
- 流式模式通过 `llm_client.aresponses(stream=True)` 获取事件流，使用 `event_to_generate_content_response` 转换
- 非流式模式通过 `aresponses` 获取完整响应，使用 `ark_response_to_generate_content_response` 转换
- 来源：`veadk/models/ark_llm.py:852-870`

### F-094 ArkLlm.supported_models
- `@classmethod def supported_models(cls) -> list[str]`
- 返回 `[r"openai/.*"]`
- 来源：`veadk/models/ark_llm.py:872-878`

### F-095 ArkEmbedding 类
- `class ArkEmbedding(BaseEmbedding)`：继承自 llama_index 的 `BaseEmbedding`
- `additional_kwargs: Dict[str, Any]`
- `api_key: str`（必填）
- `api_base: Optional[str] = None`
- `max_retries: int = 10`
- `timeout: float = 60.0`
- `reuse_client: bool = True`
- `dimensions: Optional[int] = None`
- 私有属性：`_client: Ark`、`_aclient: AsyncArk`、`_http_client`、`_async_http_client`
- 来源：`veadk/models/ark_embedding.py:34-66`

### F-096 ArkEmbedding 构造参数
- `model_name: str = DEFAULT_MODEL_EMBEDDING_NAME`（`"doubao-embedding-vision-250615"`）
- `embed_batch_size: int = 100`
- `dimensions: Optional[int] = None`
- `api_key`、`api_base`、`max_retries`、`timeout`、`reuse_client`
- `callback_manager`、`default_headers`、`http_client`、`async_http_client`、`num_workers`
- 来源：`veadk/models/ark_embedding.py:68-85`

### F-097 ArkEmbeddingModel 枚举
- `DOUBAO_EMBEDDING_VISION_251215 = "doubao-embedding-vision-251215"`
- `DOUBAO_EMBEDDING_VISION_250615 = "doubao-embedding-vision-250615"`
- 来源：`veadk/models/ark_embedding.py:29-31`

---

## 十二、评估系统

### F-098 评估数据模型
- `ToolInvocation`：`tool_name: str`、`tool_args: dict`、`tool_result: Any`
- `Invocation`：`invocation_id`、`input`、`actual_output`、`expected_output`、`actual_tool`、`expected_tool`、`latency`
- `EvalTestCase`：`invocations: list[Invocation]`
- `MetricResult`：`metric_type: str`、`success: bool`、`score: float`、`reason: str`
- 来源：`veadk/evaluation/base_evaluator.py:32-115`

### F-099 EvalResultData 类
- `class EvalResultData(BaseModel)`
- `metric_results: list[MetricResult]`
- `average_score: float = 0.0`
- `total_reason: str = ""`
- `calculate_average_score()`：计算平均分
- `generate_total_reason()`：拼接 `"metric_type:reason"`
- `call_before_append()`：调用上述两个方法
- 来源：`veadk/evaluation/base_evaluator.py:118-180`

### F-100 BaseEvaluator 类
- `class BaseEvaluator:`（无继承）
- `__init__(self, agent, name: str)`
- 属性：`name`、`agent`、`invocation_list: list[EvalTestCase]`、`result_list: list[EvalResultData]`、`agent_information_list: list[dict]`
- `_build_eval_set_from_eval_json(eval_json_path)`：通过 `load_eval_set_from_file` 加载
- `_build_eval_set_from_tracing_json(tracing_json_path)`：从 tracing JSON span 构建评估集，按 trace_id 分组
- 子类须实现 `evaluate` 方法
- 来源：`veadk/evaluation/base_evaluator.py:183-267`

### F-101 EvalResultCaseData 与 EvalResultMetadata
- `EvalResultCaseData`：`id`、`input`、`actual_output`、`expected_output`、`score`、`reason`、`status`（`PASSED`/`FAILURE`）、`latency`
- `EvalResultMetadata`：`tested_model: str`、`judge_model: str`
- score 和 latency 为字符串类型以兼容外部系统
- 来源：`veadk/evaluation/types.py:18-65`

---

## 十三、知识库

### F-102 KnowledgeBase 类
- `class KnowledgeBase(BaseModel)`
- `name: str = "user_knowledgebase"`
- `description: str = "This knowledgebase stores some user-related information."`
- `backend` 支持：`"local"`、`"opensearch"`、`"viking"`、`"redis"`、`"milvus"`、`"tos_vector"`、`"context_search"`、`"openviking"`，或 `BaseKnowledgebaseBackend` 实例
- 默认后端：`"local"`
- `backend_config: dict = Field(default_factory=dict)`
- `top_k: int = 10`
- `app_name: str = ""`
- `index: str = ""`
- `enable_profile: bool = False`
- `query_with_user_profile: bool = False`
- 来源：`veadk/knowledgebase/knowledgebase.py:92-154`

### F-103 KnowledgeBase 后端工厂
- `_get_backend_cls(backend: str) -> type[BaseKnowledgebaseBackend]`
- 各后端懒加载：
  - `"local"` → `InMemoryKnowledgeBackend`
  - `"opensearch"` → `OpensearchKnowledgeBackend`
  - `"redis"` → `RedisKnowledgeBackend`
  - `"milvus"` → `MilvusKnowledgeBackend`
  - `"tos_vector"` → `TosVectorKnowledgeBackend`
  - `"viking"` → `VikingDBKnowledgeBackend`
  - `"context_search"` → `ContextSearchBackend`
  - `"openviking"` → `OpenVikingKnowledgeBackend`
- llama_index 导入失败时提示安装 `veadk-python[extensions]`
- 来源：`veadk/knowledgebase/knowledgebase.py:30-89`

### F-104 KnowledgeBase 初始化逻辑
- 传入 backend 实例时直接使用并设置 index
- `backend_config` 非空时用其初始化
- 否则 `index` 取 `self.index or self.app_name`，均无则抛出 `ValueError`
- `query_with_user_profile=True` 时记录提示需使用 Viking Memory 后端
- 来源：`veadk/knowledgebase/knowledgebase.py:156-185`

### F-105 KnowledgeBase 核心方法
- `add_from_directory(directory: str, **kwargs) -> bool`：从目录添加
- `add_from_files(files: list[str], **kwargs) -> bool`：从文件列表添加
- `add_from_text(text: str | list[str], **kwargs) -> bool`：从文本添加
- `search(query: str, top_k: int = 0, **kwargs) -> list[KnowledgebaseEntry]`：搜索，top_k 为 0 时使用 self.top_k
- `close() -> None`：释放后端资源
- `__getattr__(name)`：代理到后端的其他方法（如 delete、list_chunks）
- 来源：`veadk/knowledgebase/knowledgebase.py:187-295`

### F-106 KnowledgeBase.generate_profiles 方法
- `async def generate_profiles(files: list[str], profile_path: str = "")`
- 使用 LLM（默认 `deepseek-v3-2-251201`）为每个文件生成 JSON 格式 profile
- Profile 包含 name、description、tags（3-5个）、keywords（3-5个）
- 写入 `./profiles/knowledgebase/profiles_<index>/`
- 来源：`veadk/knowledgebase/knowledgebase.py:297-357`

### F-107 KnowledgebaseEntry 数据模型
- `class KnowledgebaseEntry(BaseModel)`
- `content: str`
- `metadata: dict | None = None`
- 来源：`veadk/knowledgebase/entry.py:18-25`

### F-108 KnowledgebaseProfile 数据模型
- `class KnowledgebaseProfile(BaseModel)`
- `name: str`、`description: str`
- `tags: list[str]`（3-5 个分类标签）
- `keywords: list[str]`（3-5 个推荐查询关键词）
- 来源：`veadk/knowledgebase/types.py:18-29`

---

## 十四、Prompt 管理

### F-109 BasePromptManager 抽象类
- `class BasePromptManager(ABC)`
- `@abstractmethod def get_prompt(self, context: ReadonlyContext, **kwargs) -> str`
- 来源：`veadk/prompts/prompt_manager.py:26-30`

### F-110 CozeloopPromptManager 类
- `class CozeloopPromptManager(BasePromptManager)`
- 构造参数：`cozeloop_workspace_id: str`、`cozeloop_token: str`、`prompt_key: str`、`version: str = ""`、`label: str = ""`
- 通过 `cozeloop.new_client(workspace_id=..., api_token=...)` 创建客户端
- `get_prompt` 调用 `client.get_prompt(prompt_key, version, label)`，返回第一条消息内容
- 获取失败时返回 `DEFAULT_INSTRUCTION`
- 来源：`veadk/prompts/prompt_manager.py:33-79`

### F-111 默认 Prompt 常量
- `DEFAULT_INSTRUCTION`：定义 Agent 擅长数据科学、文档编写、编程、工具使用
- `DEFAULT_DESCRIPTION`：`"An AI agent developed by the VeADK team, specialized in data science, documentation, and software development."`
- 来源：`veadk/prompts/agent_default_prompt.py:15-30`

---

## 十五、认证体系

### F-112 BaseAuth 抽象基类
- `class BaseAuth:`
- `def __init__(self) -> None: ...`
- `def _fetch_token(self) -> str | dict: ...`
- `@property def token(self) -> str | dict: ...`
- 来源：`veadk/auth/base_auth.py:16-22`

---

## 十六、A2A（Agent-to-Agent）协议

### F-113 get_agent_card 函数
- `def get_agent_card(agent: Agent, url: str, version: str = VERSION, provider: str = "veadk") -> AgentCard`
- 使用 `a2a.types` 中的 `AgentCapabilities`、`AgentCard`、`AgentProvider`、`AgentSkill`
- 创建默认 skill：id="0"、name="chat"、description="Basically chat with user."、tags=["chat", "talk"]
- AgentCard 设置：defaultInputModes=["text"]、defaultOutputModes=["text"]
- 来源：`veadk/a2a/agent_card.py:15-45`

### F-114 Agent 元数据提取函数
- `agent_search_sources(agent) -> list[str]`：返回智能搜索来源（"web"、"knowledge"、"memory"）
- `agent_skill_summaries(agent) -> list[dict[str, str]]`：返回去重后的技能摘要
- `agent_component_summaries(agent) -> list[dict[str, str]]`：返回挂载组件（knowledgebase、memory、prompt_manager、example_store、run_processor、tracer、toolset、plugin）
- 来源：`veadk/agent_metadata.py:30-107`

### F-115 search_agent_component 函数
- `async def search_agent_component(agent, source, query, *, app_name, user_id) -> dict[str, Any]`
- 支持 source：`"knowledge"`（知识库搜索）、`"memory"`（长期记忆搜索，需要 user_id）
- 知识库搜索通过 `asyncio.to_thread(knowledgebase.search, query)` 异步执行
- 长期记忆搜索调用 `memory.search_memory(app_name, user_id, query)`
- 返回结构包含 `mounted`、`sourceName`、`sourceType`、`results`
- 来源：`veadk/agent_search.py:22-101`

---

## 十七、多模态系统

### F-116 MediaRef 数据类
- `@dataclass(frozen=True) class MediaRef`
- 字段：`app_name: str`、`user_id: str`、`session_id: str`、`media_id: str`
- `uri` 属性生成格式：`veadk-media://apps/<app>/users/<user>/sessions/<session>/media/<id>`（各段 URL 编码）
- `from_uri(uri: str) -> MediaRef | None`：解析 URI，scheme 不匹配返回 None
- URI scheme 常量：`MEDIA_URI_SCHEME = "veadk-media"`
- 来源：`veadk/multimodal/models.py:26-70`

### F-117 MediaRecord 数据类
- `@dataclass(frozen=True) class MediaRecord`
- 字段：`ref: MediaRef`、`file_name: str`、`mime_type: str`、`size_bytes: int`、`sha256: str`、`origin: str`、`created_at: str`
- `create()` 类方法自动生成 UTC ISO 时间戳
- `to_dict()`：序列化为存储格式（包含 uri）
- `to_api_dict()`：前端 camelCase 格式（id、uri、name、mimeType、sizeBytes、sha256、origin、createdAt）
- `from_dict(data)`：反序列化
- 来源：`veadk/multimodal/models.py:73-149`

### F-118 mount_media_routes 函数
- `def mount_media_routes(app: FastAPI, service: MediaService) -> None`
- 挂载的端点：
  - `GET /web/media/capabilities`：返回 maxFileBytes、mimeTypes、storage 类型
  - `POST /web/media`：上传媒体（Form 参数：app_name、user_id、session_id、file）
  - `GET /web/media/{app_name}/{user_id}/{session_id}/{media_id}`：获取元数据
  - `GET /web/media/{app_name}/{user_id}/{session_id}/{media_id}/content`：获取内容（本地文件返回 FileResponse，否则 307 重定向到签名 URL）
  - `DELETE /web/media/.../{media_id}` 和 `POST .../delete`：删除单个媒体
  - `DELETE /web/media/.../{session_id}` 和 `POST .../delete`：删除会话所有媒体
- 上传大小限制通过 `service.max_file_bytes`，超限返回 413
- 存储类型由环境变量 `VEADK_MEDIA_STORAGE` 控制（默认 `"local"`）
- 来源：`veadk/multimodal/api.py:36-135`

---

## 十八、运行时抽象

### F-119 BaseRuntime 抽象类
- `class BaseRuntime(ABC)`
- 类属性：`name: str = "base"`
- 抽象方法：`async def run_async(self, agent: "Agent", ctx: "InvocationContext") -> AsyncGenerator["Event", None]`
- 运行时替换 Agent 的内部推理+工具循环，Runner 仍负责多租户、会话、记忆和 tracing
- 默认 `"adk"` 运行时使用 Google ADK 的 `BaseLlmFlow`
- 替代运行时（如 `"codex"` 基于 Claude Code SDK、`"piagent"`）桥接外部 Agent harness 到 ADK Event 流
- 来源：`veadk/runtime/base_runtime.py:142-174`

### F-120 build_system_append 函数
- `def build_system_append(agent: "Agent") -> str`
- 将 agent 的 name、description、instruction（仅字符串类型）组合为追加到运行时系统提示词的文本块
- `InstructionProvider` 可调用对象被跳过
- 来源：`veadk/runtime/base_runtime.py:37-59`

### F-121 resolve_system_append 函数
- `async def resolve_system_append(agent: "Agent", ctx: "InvocationContext") -> tuple[str, str]`
- 返回 `(base_parts, developer_parts)` 两个字符串
- 处理 ADK 的 `InstructionProvider` 可调用对象和状态注入
- 支持 `global_instruction`、`static_instruction`、`instruction` 三层指令解析
- 使用 `inject_session_state` 进行会话状态注入
- 来源：`veadk/runtime/base_runtime.py:62-139`

---

## 十九、Harness 扩展

### F-122 HarnessExtensionConfig 类
- `class HarnessExtensionConfig(HarnessBaseModel)`
- `enabled: bool = True`
- `components: list[str]`：默认 `["invocation_context", "compactor", "response_verification"]`
- `profile: str = "default"`
- 来源：`veadk/extensions/harness/extension.py:43-54`

### F-123 HarnessExtension 类
- `class HarnessExtension:`
- 构造参数：`enabled`、`components`（Iterable/str/None）、`profile`、`store`、`context_config`、`compaction_config`、`verifier_config`、`env`
- `from_env(cls, env=None) -> HarnessExtension`：类方法，从环境变量创建
- `plugins() -> list[BasePlugin]`：构建插件列表，供 `Runner(..., plugins=...)` 使用
- env 非空时通过 `build_harness_plugins_from_env` 构建；enabled=False 时返回空列表
- 来源：`veadk/extensions/harness/extension.py:57-119`

### F-124 build_harness_plugins 函数（harness.py）
- `def build_harness_plugins(*, components=None, profile="default") -> list[BasePlugin]`
- 委托给 `veadk.extensions.harness.plugins.build_harness_plugins`
- 来源：`veadk/harness.py:24-33`

---

## 二十、示例代码

### F-125 快速开始示例
- 导入：`from veadk import Agent, Runner`
- 创建 Agent：name="quickstart_agent"，含 description 和 instruction
- 创建 Runner：`Runner(agent=agent, app_name="quickstart")`
- 运行：`await runner.run(messages="用一句话介绍火山引擎（Volcengine）。", session_id="demo-session")`
- 使用 `asyncio.run(main())` 启动
- 来源：`examples/01_quickstart/main.py:21-43`

### F-126 自定义工具示例
- 工具为带类型注解和 docstring 的普通 Python 函数
- `get_city_weather(city: str) -> dict[str, str]`：查询城市天气
- `recommend_clothing(temperature_celsius: int) -> dict[str, str]`：根据温度推荐穿着
- Agent 通过 `tools=[get_city_weather, recommend_clothing]` 挂载工具
- instruction 指导 Agent 先查天气再推荐穿着
- 来源：`examples/02_custom_tools/main.py:27-84`

---

## 二十一、模块导入与补丁

### F-127 agent.py 模块级补丁
- 导入时设置 `LITELLM_LOCAL_MODEL_COST_MAP=True`（减少约 10 秒导入延迟）
- 调用 `patch_tracer()`、`patch_asyncio()`、`patch_mcp_session_retry()`
- 来源：`veadk/agent.py:27-28,66-68`

### F-128 各 Agent 类型模块级补丁
- LoopAgent、ParallelAgent、SequentialAgent 模块均调用 `patch_asyncio()`
- 来源：
  - `veadk/agents/loop_agent.py:27`
  - `veadk/agents/parallel_agent.py:27`
  - `veadk/agents/sequential_agent.py:27`

---

## 二十二、环境变量汇总

### F-129 核心环境变量
- `MODEL_AGENT_API_KEY`：Agent 模型 API Key
- `MODEL_AGENT_API_KEY_NAME`：ARK API Key 名称
- `MODEL_AGENT_MAX_LLM_CALLS`：最大 LLM 调用次数（默认 100）
- `MODEL_AGENT_ENCRYPTED`：请求加密（默认 `"true"`）
- `MODEL_AGENT_CACHING`：缓存开关（默认 `"enabled"`）
- `MODEL_AGENT_CLIENT_REQ_ID`：客户端请求 ID
- `CLOUD_PROVIDER`：云提供商（`volcengine`/`byteplus`）
- `LITELLM_LOCAL_MODEL_COST_MAP`：LiteLLM 本地模型成本图
- 来源：`veadk/agent.py:27-28,224`；`veadk/consts.py:27-35`；`veadk/runner.py:511`

### F-130 Tracing 环境变量
- `ENABLE_APMPLUS`：启用 APMPlus exporter（`"true"`）
- `ENABLE_COZELOOP`：启用 CozeLoop exporter
- `ENABLE_TLS`：启用 TLS exporter
- 来源：`veadk/agent.py:646-648`

### F-131 技能与工具环境变量
- `AGENTKIT_TOOL_ID`：AgentKit 工具 ID
- `AGENTKIT_TOOL_SERVICE_CODE`：服务代码（默认 `"agentkit"`）
- `AGENTKIT_TOOL_REGION`：区域（默认 `"cn-beijing"`）
- `AGENTKIT_SKILL_HOST`：技能主机
- `VOLCENGINE_ACCESS_KEY`、`VOLCENGINE_SECRET_KEY`：火山引擎 AK/SK
- `VEADK_MEDIA_STORAGE`：多媒体存储类型（默认 `"local"`）
- 来源：`veadk/agent.py:468-505`；`veadk/multimodal/api.py:44`
