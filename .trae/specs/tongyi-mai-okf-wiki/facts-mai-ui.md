# Facts: MAI-UI
> 信源根：external/libs/tools/Tongyi-MAI/MAI-UI/MAI-UI（下述路径均相对此根）
> 采集日期：2026-08-29 ｜ 采集模式：源码逐行精读，零推测

## F-001 仓库定位为 GUI agent 基础模型家族仓库
- 位置: `README.md`
- 内容: README 标题为 MAI-UI，声明提供 2B/8B/32B/235B-A22B 四个尺寸的 GUI agent 基础模型；HuggingFace 已发布 MAI-UI-2B 与 MAI-UI-8B 权重链接（Tongyi-MAI 组织）。技术报告 arXiv:2512.22047。

## F-002 许可证为 Apache-2.0，附第三方组件 NOTICE
- 位置: `LICENSE`、`NOTICE`
- 内容: LICENSE 为 Apache License Version 2.0 全文；NOTICE 声明产品版权归 "Alibaba Cloud and its affiliates"，并列出第三方组件：Jinja2（BSD-3-Clause）、NumPy（BSD-3-Clause）、OpenAI Python Client（Apache-2.0）、Pillow（HPND）。

## F-003 顶层依赖仅 4 个包
- 位置: `requirements.txt`
- 内容: `Jinja2==3.1.6`、`numpy==2.3.5`、`openai==2.13.0`、`Pillow==12.0.0`。无 torch/transformers（src 通过 OpenAI 兼容 API 调用模型）。

## F-004 Quick Start 指定 vLLM 0.11.0 部署 API 服务
- 位置: `README.md`
- 内容: 安装章节指定 `pip install vllm==0.11.0`（注明需 transformers>=4.57.0），启动命令 `python -m vllm.entrypoints.openai.api_server --served-model-name MAI-UI-8B --port 8000`，服务地址 `http://localhost:8000/v1`。README 强调 "Must use VLLM=0.11.0"。

## F-005 README 示例给出两个 Agent 的初始化方式
- 位置: `README.md`
- 内容: Quick Start 展示 `MAIGroundingAgent(llm_base_url="http://localhost:8000/v1", model_name="MAI-UI-8B", runtime_conf={"history_n": 3, "temperature": 0.0, "top_k": -1, "top_p": 1.0, "max_tokens": 2048})` 与 `MAIUINaivigationAgent(...)` 同参数调用（类名拼写 Naivigation 在 README 即如此）。

## F-006 仓库目录结构：src 6 文件 + evaluation/grounding + cookbook + tests
- 位置: 仓库根
- 内容: `src/`（base.py、mai_grounding_agent.py、mai_naivigation_agent.py、prompt.py、unified_memory.py、utils.py）、`evaluation/grounding/`、`cookbook/`（grounding.ipynb、run_agent.ipynb）、`tests/`（test_mai_navigation_agent.py + output_messages/ 8 个 JSON 基线文件）、`resources/example_img/`（figure1~5.png）。

## F-007 unified_memory 定义两个 dataclass：TrajStep 与 TrajMemory
- 位置: `src/unified_memory.py`
- 内容: `@dataclass class TrajStep` 与 `@dataclass class TrajMemory`。TrajStep 必填字段：`screenshot: Image.Image`、`accessibility_tree: Optional[Dict[str, Any]]`、`prediction: str`、`action: Dict[str, Any]`、`conclusion: str`、`thought: str`、`step_index: int`、`agent_type: str`、`model_name: str`；默认字段：`screenshot_bytes: Optional[bytes] = None`、`structured_action: Optional[Dict[str, Any]] = None`、`ask_user_response: Optional[str] = None`、`mcp_response: Optional[str] = None`。

## F-008 TrajMemory 结构为 task_goal + task_id + steps 列表
- 位置: `src/unified_memory.py`
- 内容: `TrajMemory(task_goal: str, task_id: str, steps: List[TrajStep] = field(default_factory=list))`。文件 docstring 为 "Unified memory structures for trajectory tracking"。

## F-009 BaseAgent 为 ABC，内嵌 TrajMemory 并定义 predict 抽象方法
- 位置: `src/base.py`
- 内容: `class BaseAgent(ABC)`，`__init__(self) -> None` 初始化 `self.traj_memory = TrajMemory(task_goal="", task_id="", steps=[])`。抽象方法签名：`def predict(self, instruction: str, obs: Dict[str, Any], **kwargs: Any) -> Tuple[str, Dict[str, Any]]`。文件 docstring "Base agent class for mobile GUI automation agents"。

## F-010 BaseAgent 提供 6 个只读 property 派生轨迹数据
- 位置: `src/base.py`
- 内容: `thoughts -> List[str]`（各 step.thought）、`actions -> List[Dict[str, Any]]`（各 step.action）、`conclusions -> List[str]`、`observations -> List[Dict[str, Any]]`（每项为 `{"screenshot": step.screenshot_bytes, "accessibility_tree": step.accessibility_tree}`）、`history_images -> List[bytes]`（各 step.screenshot_bytes）、`history_responses -> List[str]`（各 step.prediction）。

## F-011 BaseAgent 提供 reset/load_traj/save_traj 三个轨迹管理方法
- 位置: `src/base.py`
- 内容: `reset(self) -> None` 重建空 TrajMemory；`load_traj(self, traj_memory: TrajMemory) -> None` 直接替换 self.traj_memory；`save_traj(self) -> Dict[str, Any]` 返回 `{"task_goal", "task_id", "steps": [每个 step 的 9 字段 dict（screenshot_bytes/accessibility_tree/prediction/action/conclusion/thought/step_index/agent_type/model_name）]}`。

## F-012 utils 提供 5 个图像/坐标工具函数
- 位置: `src/utils.py`
- 内容: `safe_pil_to_bytes(image: Union[Image.Image, bytes]) -> bytes`（PIL 转 PNG bytes）；`pil_to_base64(image: Image.Image) -> str`（PNG base64 字符串）；`save_screenshot(screenshot: Image.Image, path: str) -> None`；`extract_click_coordinates(action: Dict[str, Any]) -> Optional[Tuple[float, float]]`（读 `action['coordinate']`）；`draw_clicks_on_image(image_path: str, click_coords: Tuple[float, float], output_path: Optional[str] = None) -> Image.Image`（画半径 20 的红色圆）。

## F-013 prompt.py 定义 4 个 prompt 模板
- 位置: `src/prompt.py`
- 内容: `MAI_MOBILE_SYS_PROMPT`（str）、`MAI_MOBILE_SYS_PROMPT_NO_THINKING`（str）、`MAI_MOBILE_SYS_PROMPT_ASK_USER_MCP`（jinja2.Template）、`MAI_MOBILE_SYS_PROMPT_GROUNDING`（str）。前两者为纯字符串，第三个带 `{{ tools }}` 占位与 `{% if tools -%}` 条件块，第四个为 grounding 专用。

## F-014 导航 Action Space 共 10 种动作
- 位置: `src/prompt.py`
- 内容: `MAI_MOBILE_SYS_PROMPT` 的 Action Space：`click`（coordinate）、`long_press`（coordinate）、`type`（text）、`swipe`（direction: up/down/left/right + 可选 coordinate）、`open`（text: app_name）、`drag`（start_coordinate + end_coordinate）、`system_button`（button: back/home/menu/enter）、`wait`、`terminate`（status: success/fail）、`answer`（text）。ASK_USER_MCP 版本额外含 `ask_user`（text）与 `double_click`（coordinate），共 12 种。

## F-015 输出格式约定为 thinking + tool_call XML 标签
- 位置: `src/prompt.py`
- 内容: 系统提示要求输出 `<thinking>...</thinking>` 与 `<tool_call>{"name": "mobile_use", "arguments": <args-json-object>}</tool_call>`；NO_THINKING 版本仅要求 `<tool_call>`；grounding 版本要求 `<grounding_think>...</grounding_think>` 与 `<answer>{"coordinate": [x,y]}</answer>`。

## F-016 两个 prompt 版本内嵌两套可用 App 列表
- 位置: `src/prompt.py`
- 内容: MAI_MOBILE_SYS_PROMPT / NO_THINKING 列出 21 个 App（Camera、Chrome、Clock、Contacts、Dialer、Files、Settings、Markor、Tasks、Simple Draw Pro、Simple Gallery Pro、Simple SMS Messenger、Audio Recorder、Pro Expense、Broccoli APP、OSMand、VLC、Joplin、Retro Music、OpenTracks、Simple Calendar Pro）；ASK_USER_MCP 模板列出 14 个 App（Contacts、Settings、Clock、Maps、Chrome、Calendar、files、Gallery、Taodian、Mattermost、Mastodon、Mail、SMS、Camera）。

## F-017 grounding agent 常量 SCALE_FACTOR = 999
- 位置: `src/mai_grounding_agent.py`
- 内容: 模块级常量 `SCALE_FACTOR = 999`；`parse_grounding_response` 将 answer 中坐标除以 999 归一化到 [0,1]。

## F-018 parse_grounding_response 解析 grounding_think 与 answer 标签
- 位置: `src/mai_grounding_agent.py`
- 内容: 签名 `def parse_grounding_response(text: str) -> Dict[str, Any]`；用正则 `<grounding_think>(.*?)</grounding_think>` 提取 thinking，`<answer>(.*?)</answer>` 提取 JSON 并取 `coordinate` 字段；坐标非 2 个值时 raise ValueError；返回 `{"thinking": ..., "coordinate": [x_norm, y_norm]}`。

## F-019 MAIGroundingAgent 不继承 BaseAgent
- 位置: `src/mai_grounding_agent.py`
- 内容: `class MAIGroundingAgent:`（无基类），`__init__(self, llm_base_url: str, model_name: str, runtime_conf: Optional[Dict[str, Any]] = None)`。default_conf 为 `{"temperature": 0.0, "top_k": -1, "top_p": 1.0, "max_tokens": 2048}`，与传入 runtime_conf 字典合并（`{**default_conf, **(runtime_conf or {})}`）。创建 `OpenAI(base_url=..., api_key="empty")` 客户端。

## F-020 MAIGroundingAgent.predict 签名与返回值
- 位置: `src/mai_grounding_agent.py`
- 内容: `def predict(self, instruction: str, image: Union[Image.Image, bytes], **kwargs: Any) -> Tuple[str, Dict[str, Any]]`。bytes 输入经 `Image.open(BytesIO(image))` 转 PIL，非 RGB 模式转 RGB；返回 `(prediction_text, {"thinking", "coordinate"})`；3 次重试后仍失败返回 `("llm client error", {"thinking": None, "coordinate": None})`。

## F-021 grounding 推理固定 seed=42 且请求参数含 extra_body
- 位置: `src/mai_grounding_agent.py`
- 内容: `self.llm.chat.completions.create(model=..., messages=..., max_tokens=..., temperature=..., top_p=..., frequency_penalty=0.0, presence_penalty=0.0, extra_body={"repetition_penalty": 1.0, "top_k": self.top_k}, seed=42)`。

## F-022 grounding 消息结构为 system prompt + 单条 user（文本+单图）
- 位置: `src/mai_grounding_agent.py`
- 内容: `_build_messages(self, instruction: str, image: Image.Image) -> list` 生成 2 条消息：system（`MAI_MOBILE_SYS_PROMPT_GROUNDING`）与 user（`instruction + "\n"` 文本 + base64 PNG image_url）。无历史图像逻辑。system_prompt 为 @property，直接返回 `MAI_MOBILE_SYS_PROMPT_GROUNDING`。

## F-023 导航 agent 常量同样为 SCALE_FACTOR = 999
- 位置: `src/mai_naivigation_agent.py`
- 内容: 模块级常量 `SCALE_FACTOR = 999`，用于坐标归一化/反归一化（乘除 999）。

## F-024 mai_naivigation_agent 定义 3 个模块级解析函数
- 位置: `src/mai_naivigation_agent.py`
- 内容: `mask_image_urls_for_logging(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]`（深拷贝并将 image_url 替换为 "[IMAGE_DATA]"）；`parse_tagged_text(text: str) -> Dict[str, Any]`（正则 `<thinking>(.*?)</thinking>.*?<tool_call>(.*?)</tool_call>`，兼容 thinking 模型把 `</think>` 替换为 `</thinking>` 并补前置 `<thinking>`，tool_call 需为合法 JSON）；`parse_action_to_structure_output(text: str) -> Dict[str, Any]`（返回 `{"thinking", "action_json"}`）。

## F-025 坐标解析支持 2 值与 4 值两种格式
- 位置: `src/mai_naivigation_agent.py`
- 内容: `parse_action_to_structure_output` 中 `coordinate`/`start_coordinate`/`end_coordinate` 均支持长度 2（x,y 直接用）或长度 4（x1,y1,x2,y2 取中点），除以 SCALE_FACTOR 归一化；长度不为 2 或 4 时 raise ValueError。

## F-026 MAIUINaivigationAgent 继承 BaseAgent
- 位置: `src/mai_naivigation_agent.py`
- 内容: `class MAIUINaivigationAgent(BaseAgent)`，`__init__(self, llm_base_url: str, model_name: str, runtime_conf: Optional[Dict[str, Any]] = None, mcp_tools: Optional[List[Dict[str, Any]]] = None)`；先 `super().__init__()`，`self.mcp_tools = mcp_tools or []`；default_conf 为 `{"history_n": 3, "temperature": 0.0, "top_k": -1, "top_p": 1.0, "max_tokens": 2048}`。类 docstring 名为 "MAIMobileAgent"（docstring 与类名不一致，属代码现状）。

## F-027 system_prompt 属性按 mcp_tools 切换模板
- 位置: `src/mai_naivigation_agent.py`
- 内容: `@property def system_prompt(self) -> str`：若 `self.mcp_tools` 非空，将每个 tool dict 以 `json.dumps(tool, ensure_ascii=False)` 逐行 join 后传入 `MAI_MOBILE_SYS_PROMPT_ASK_USER_MCP.render(tools=mcp_tools_str)`；否则返回 `MAI_MOBILE_SYS_PROMPT`。

## F-028 history_responses 属性重写：坐标反归一化后重组 tool_call 文本
- 位置: `src/mai_naivigation_agent.py`
- 内容: `@property def history_responses(self) -> List[str]` 遍历 traj_memory.steps，跳过无 structured_action 的 step；将 action_json 的 normalized 坐标乘以 SCALE_FACTOR 取 int 还原；组装 `{"name": "mobile_use", "arguments": action_json}`（`json.dumps(..., separators=(",", ":"))`），输出 `f"<thinking>\n{thinking}\n</thinking>\n<tool_call>\n{tool_call_json}\n</tool_call>"`。

## F-029 三个 mem2 系列方法
- 位置: `src/mai_naivigation_agent.py`
- 内容: `mem2response(self, step: TrajStep) -> str`（同 F-028 格式化单步；无 structured_action 时 raise ValueError）、`mem2ask_user_response(self, step: TrajStep) -> str`（返回 `step.ask_user_response`）、`mem2mcp_response(self, step: TrajStep) -> str`（返回 `step.mcp_response`）。

## F-030 _prepare_images 拼接 history_n-1 张历史图与当前图
- 位置: `src/mai_naivigation_agent.py`
- 内容: `def _prepare_images(self, screenshot_bytes: bytes) -> List[Image.Image]`；取 `min(len(history_images), history_n - 1)` 张最近历史截图 bytes，追加当前 screenshot_bytes，逐张转 PIL、非 RGB 转 RGB 后返回列表。兼容 bytes / PIL Image 输入，其他类型 raise TypeError。

## F-031 _build_messages 历史完整回放但图像只挂最后 history_n-1 张
- 位置: `src/mai_naivigation_agent.py`
- 内容: `def _build_messages(self, instruction: str, images: List[Image.Image]) -> List[Dict[str, Any]]`。结构：system → user(instruction) → 对每个历史 step 依次追加 [可选 user 图像消息] + [assistant(mem2response(step))] + [ask_user_response 存在时追加 user 文本] + [mcp_response 存在时追加 user 文本] → 最后追加当前图像 user 消息。图像消息仅给 `history_idx >= len(steps) - (history_n - 1)` 的历史 step（`start_image_idx = max(0, len(steps) - (history_n - 1))`）。无历史时为 system → user(instruction) → user(当前图像)。

## F-032 MAIUINaivigationAgent.predict 签名与 obs 字段
- 位置: `src/mai_naivigation_agent.py`
- 内容: `def predict(self, instruction: str, obs: Dict[str, Any], **kwargs: Any) -> Tuple[str, Dict[str, Any]]`。obs 读取 `obs["screenshot"]`（PIL 或 bytes）与 `obs.get("accessibility_tree")`、可选 `ask_user_response`/`mcp_response` 键（docstring 声明，代码实际仅使用 screenshot 与 accessibility_tree）。首次调用时 `if not self.traj_memory.task_goal: self.traj_memory.task_goal = instruction`。

## F-033 predict 成功后将 TrajStep 追加进 traj_memory
- 位置: `src/mai_naivigation_agent.py`
- 内容: 构造 `TrajStep(screenshot=screenshot_pil, accessibility_tree=obs.get("accessibility_tree"), prediction=prediction, action=action_json, conclusion="", thought=thinking, step_index=len(self.traj_memory.steps), agent_type="MAIMobileAgent", model_name=self.model_name, screenshot_bytes=screenshot_bytes, structured_action={"action_json": action_json})` 并 `self.traj_memory.steps.append(traj_step)`；返回 `(prediction, action_json)`。3 次重试失败返回 `("llm client error", {"action": None})`。注意 ask_user_response/mcp_response 字段未被 predict 写入（保持默认 None，由外部赋值）。

## F-034 reset 方法覆写接受 runtime_logger 参数
- 位置: `src/mai_naivigation_agent.py`
- 内容: `def reset(self, runtime_logger: Any = None) -> None`，调用 `super().reset()`，runtime_logger 未使用（docstring 注明 "unused, kept for API compatibility"）。

## F-035 评估脚本模型封装类 CustomQwen3_VL_VLLM_Model
- 位置: `evaluation/grounding/models/MAI_UI.py`
- 内容: `class CustomQwen3_VL_VLLM_Model():`（无基类）。`load_model(self, model_name_or_path="Qwen/Qwen3-VL-30B-A3B-Instruct", max_pixels=99999999)` 用 vllm.LLM 加载（`tensor_parallel_size=torch.cuda.device_count()`、`gpu_memory_utilization=0.90`、`max_model_len=32768`、`limit_mm_per_prompt={"image": 1}`、mm_processor_kwargs 的 min_pixels=16*16*4）。`set_generation_config(self, **kwargs)` 为空实现。模块顶部设置 `mp.set_start_method('spawn', force=True)` 与 `os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "spawn"`。

## F-036 评估模型提供单样本与批量两个推理方法
- 位置: `evaluation/grounding/models/MAI_UI.py`
- 内容: `ground_only_positive(self, instruction, image, use_guide_text=False)`（单样本，SamplingParams(temperature=0.0, max_tokens=256)，smart_resize factor=16*2，point 归一化用 `point_x / resized_width`）；`batch_ground_only_positive(self, instructions, images, use_guide_text=False)`（批量，SamplingParams(temperature=0.01, max_tokens=256)，smart_resize factor=14*2 / min_pixels=28*28，point 归一化固定除以 1000）。两者均返回 `{"result": "positive", "format": "x1y1x2y2", "raw_response", "bbox": None, "point": None-or-[x,y]}`。use_guide_text=True 时在 prompt 后追加 guide_text `"<tool_call>\n{\"name\": \"grounding\", \"arguments\": {\"action\": \"click\", \"coordinate\": ["`。

## F-037 评估 prompt 与 src grounding prompt 同源但追加 "## Input instruction" 尾行
- 位置: `evaluation/grounding/models/MAI_UI.py`（`get_qwen3_vl_prompt_msg`）、`evaluation/grounding/eval_server.py`（SYSTEM_PROMPT）
- 内容: 评估脚本将 grounding 系统 prompt（与 `src/prompt.py` 的 MAI_MOBILE_SYS_PROMPT_GROUNDING 文本一致）末尾追加一行 `## Input instruction`。消息为 system(text) + user(instruction + "\n" + image)。

## F-038 eval_local.py 命令行参数清单
- 位置: `evaluation/grounding/eval_local.py`
- 内容: `--model_type`（required，build_model 仅支持 "MAI_UI"）、`--model_name_or_path`、`--screenspot_imgs`（required）、`--screenspot_test`（required）、`--task`（默认 "all"）、`--inst_style`（choices: instruction/action/description/all，默认 "instruction"）、`--language`（choices: en/cn/all，默认 "en"）、`--gt_type`（choices: positive/negative/all，默认 "positive"）、`--log_path`（required）、`--use_guide_text`（str_to_bool，默认 True）、`--max_pixels`（默认 2116800）。模块常量 `GT_TYPES = ['positive', 'negative']`、`INSTRUCTION_STYLES = ['instruction', 'action', 'description']`、`LANGUAGES = ['en', 'cn']`、`torch.manual_seed(114514)`。

## F-039 eval_local.py 中文指令仅支持 positive + instruction 样式
- 位置: `evaluation/grounding/eval_local.py`
- 内容: 语言分发处 `if lang == "cn": if inst_style != 'instruction' or gt_type != 'positive': raise AttributeError(...)`，prompt 取 `task_instance["instruction_cn"]`；英文取 `task_instance["instruction"]`。批量推理 batch_size=100，批量失败时降级为单样本循环，单样本仍失败则填入 `{"result": "positive", "format": "x1y1x2y2", "raw_response": "ERROR", "bbox": None, "point": None}`。

## F-040 判分逻辑：bbox 归一化后点包含判定
- 位置: `evaluation/grounding/eval_local.py`（`eval_sample_positive_gt`、`eval_sample_negative_gt`）、`evaluation/grounding/eval_server.py`（process_case）
- 内容: 正样本判分 `eval_sample_positive_gt`：bbox 除以 `sample["img_size"]` 归一化为 [x1,y1,x2,y2]，`response["point"]` 为 None 记 "wrong_format"，点落在 bbox 矩形内记 "correct" 否则 "wrong"。负样本 `eval_sample_negative_gt`：`response["result"] == "negative"` 记 "correct"，"positive" 记 "wrong"，其余 "wrong_format"。eval_server.py 中同逻辑但错误标签写作 'incorrect'（bbox 用 `case.get('img_size', [ori_width, ori_height])`），坐标按 `related / 1000.0` 归一化再乘原图宽高得到绝对 pred。

## F-041 结果聚合产出 5 类指标视图
- 位置: `evaluation/grounding/eval_local.py`（`evaluate`、`calc_metric_for_result_list`、`make_combinations`、`collect_results_to_eval`）
- 内容: `evaluate(results)` 返回 `{"details": results, "metrics": {"fine_grained", "seeclick_style", "leaderboard_simple_style", "leaderboard_detailed_style", "overall"}}`。fine_grained 按 platform × application × instruction_style × gt_type 组合；seeclick_style 按 platform × instruction_style × gt_type；leaderboard_simple_style 按 group；leaderboard_detailed_style 按 application。`calc_metric_for_result_list` 输出 `num_correct_action / num_total / wrong_format_num / action_acc / text_acc / icon_acc`（text/icon 按 ui_type=="text"/"icon" 分桶）。

## F-042 output_local JSON 顶层结构：details + metrics 五子键
- 位置: `evaluation/grounding/output_local/OS_G.json`、`SSV2.json`（同目录还有 MMBench.json、OS_G_Refine.json、SSPro.json、UI_Vision.json）
- 内容: 顶层 `{"details": [...], "metrics": {"fine_grained", "seeclick_style", "leaderboard_simple_style", "leaderboard_detailed_style", "overall"}}`。details 每条含字段：id、img_path、group、platform、application、lang、instruction_style、prompt_to_evaluate、gt_type、ui_type（OS_G 中为列表如 ["Label","Button","Icon"]，SSV2 中为字符串如 "icon"）、task_filename、pred、raw_response、bbox、correctness。OS_G.json 的 group 值为 "os_g_refine"、platform 为 "linux"、task_filename 为 "OSWorld-G_sspro"；SSV2.json 的 platform 为 "v2"、application 为 "screenspot_desktop_v2"、task_filename 为 "screenspot_desktop_v2_convert"。

## F-043 eval_server.py 走 OpenAI 兼容客户端 + 多线程
- 位置: `evaluation/grounding/eval_server.py`
- 内容: 参数 `--dataset_dir`(required)、`--image_root`(required)、`--output_file`（默认 ./results.jsonl）、`--server_ip`（默认 localhost）、`--server_port`（默认 8001）、`--model_name`（默认 "MAI-UI-8B"）、`--api_key`（默认 "EMPTY"）、`--num_workers`（默认 16）。用 `ThreadPoolExecutor(max_workers=num_workers)` 并发调用 `client.chat.completions.create`，逐条 JSONL 追加写入（`file_write_lock = threading.Lock()` 保护）；smart_resize max_pixels=6553600、factor=16*2。跑完按 `dataset_source`（数据集文件名）聚合打印 accuracy。

## F-044 extract_metrics.py 读取 metrics.overall.action_acc 字段
- 位置: `evaluation/grounding/extract_metrics.py`
- 内容: `extract_action_acc_from_json(json_file_path)` 读取 `data['metrics']['overall']` 下的 `action_acc`、`num_correct_action`、`num_total`、`wrong_format_num`。目录中存在以 "checkpoint" 开头的文件夹时走多 checkpoint 对比（输出 metrics_comparison.xlsx，openpyxl 给每行最高分单元格加红色填充），否则输出 metrics_summary.csv。参数：位置参数 input_directory / `--input -i` / `--output -o` / `--format -f`（xlsx/csv/auto）/ `--verbose -v`；无参数时进入交互模式。

## F-045 评估 requirements 锁定 vllm 0.11.0 与 transformers 4.57.0
- 位置: `evaluation/grounding/requirements.txt`
- 内容: `vllm==0.11.0`、`transformers==4.57.0`、`accelerate==1.3.0`、`qwen-vl-utils==0.0.14`、`dashscope==1.23.6`、`openai==2.2.0`、`torch==2.8.0`、`torchvision==0.23.0`、`pillow==10.4.0`、`numpy==1.26.4`、`pandas==2.2.2`，并指定 `--extra-index-url https://pypi.nvidia.com` 与 `https://download.pytorch.org/whl/cu12`。与根 requirements.txt（仅 4 包、openai==2.13.0、Pillow==12.0.0）版本不一致。

## F-046 评估 README 声明训练范式沿用 UI-Ins
- 位置: `evaluation/grounding/README.md`
- 内容: "Our training paradigm follows UI-Ins (arXiv:2510.20286, Code: github.com/alibaba/UI-Ins), with specific adaptations tailored for MAI-UI"。环境要求 conda python=3.12、VLLM==0.11.0。MAI-UI 评测显式 `--use_guide_text False`（README：guide text 特性对 MAI-UI 禁用以对齐标准推理模式）。示例命令 `--model_name_or_path Tongyi-MAI/MAI-UI-8B --max_pixels 6553600`。

## F-047 评估 README 附 MAI-UI-8B 三种评测方式结果表
- 位置: `evaluation/grounding/README.md`
- 内容: 表格列（6 数据集）：UI-Vision / MMBench-GUI L2 / ScreenSpot-Pro / ScreenSpot-V2 / OSWorld-G / OSWorld-G Refine。三行结果：Tech Report（40.7 / 88.8 / 65.8 / 95.2 / 60.1 / 68.6）、eval locally（40.9 / 88.9 / 66.1 / 95.1 / 60.9 / 68.7）、eval by vllm api（40.3 / 88.7 / 67.0 / 94.9 / 61.7 / 69.5）。

## F-048 评测数据目录将 6 个基准统一为 ScreenSpot-Pro 格式
- 位置: `evaluation/grounding/data/`（目录清单）、`evaluation/grounding/README.md`
- 内容: data/ 下 6 个数据目录：`ScreenSpot_Pro_data/`（28 个 json：android_studio_macos、autocad_windows、blender_windows、davinci_macos、eviews_windows、excel_macos、fruitloops_windows、illustrator_windows、inventor_windows、linux_common_linux、macos_common_macos、matlab_macos、origin_windows、photoshop_windows、powerpoint_windows、premiere_windows、pycharm_macos、quartus_windows、solidworks_windows、stata_windows、unreal_engine_windows、vivado_windows、vmware_macos、vscode_macos、windows_common_windows、word_macos）、`ScreenSpot_V2_data/`（desktop/mobile/web 3 个 convert json）、`OS_G_data/`（OSWorld-G_sspro_format.json）、`OS_G_Refine_data/`（OSWorld-G_refined_sspro_format.json）、`MMbench_data/`（MMbench_GUI_sspro_format.json）、`UI_Vision_data/`（element_grounding_basic/functional/spatial.json）。README 声明 OSWorld-G、MMBench 已重排为 ScreenSpot-Pro 格式。

## F-049 cookbook/grounding.ipynb 流程：加载图 → 建 agent → predict → 可视化
- 位置: `cookbook/grounding.ipynb`
- 内容: 步骤（共 6 cell）：`sys.path.insert(0, "../src")` 后导入 `MAIGroundingAgent`、`draw_clicks_on_image`、`extract_click_coordinates`；打开 `../resources/example_img/figure1.png`；instruction 为 "click the email icon"；创建 agent（llm_base_url="http://localhost:8000/v1"，model_name="MAI-UI-8B"，runtime_conf 同 README）；`prediction, action = agent.predict(instruction, test_image)`（第二参数直接传 PIL 图）；`extract_click_coordinates(action)` 取归一化坐标乘图像宽高得绝对坐标，`draw_clicks_on_image` 画红圈并 display。

## F-050 cookbook/run_agent.ipynb 流程：5 张连续截图循环预测
- 位置: `cookbook/run_agent.ipynb`
- 内容: 标题 "# Run Naivagation"（notebook 内即此拼写）。加载 `../resources/example_img/figure1.png` 至 `figure5.png` 共 5 张图；instruction 为 "open the settings and turn on the wifi"；循环对 5 张图执行 `obs = {"screenshot": test_image}`、`prediction, action = agent.predict(instruction, obs)`（同一 agent 实例连续调用，轨迹累积），结果收集到 results 列表；随后对每个结果做与 grounding notebook 相同的坐标可视化。

## F-051 tests 覆盖 _build_messages 的 10 个用例
- 位置: `tests/test_mai_navigation_agent.py`
- 内容: 文件 docstring "Unit tests for MAIUINaivigationAgent._build_messages functionality"。`class TestBuildMessages` 下用例：test_build_messages_no_history（断言 3 条消息）、test_build_messages_with_single_history（5 条消息：system/user/history图/assistant/current图）、test_build_messages_with_multiple_history（3 history 时 image_count==3）、test_build_messages_with_5_history_steps（5 assistant + 3 image）、test_build_messages_with_5_steps_ask_user_and_mcp（验证 ask_user_response 与 mcp_response 进入消息、MCP 工具名进入 system prompt）、test_build_messages_with_ask_user_response、test_build_messages_with_mcp_response、test_build_messages_system_prompt、test_build_messages_with_mcp_tools、test_build_messages_image_encoding（base64 前缀 `data:image/png;base64,` 校验）。

## F-052 测试通过 mock OpenAI 并将消息 dump 为 JSON 基线文件
- 位置: `tests/test_mai_navigation_agent.py`
- 内容: fixture 用 `with patch('mai_naivigation_agent.OpenAI')` 构造 agent（llm_base_url="http://test.com"、model_name="test-model"、runtime_conf={"history_n": 3}）；`dump_messages_to_file` 用 `mask_image_urls_for_logging` 屏蔽图像后写入 `tests/output_messages/<test_name>.json`（8 个基线文件与用例对应）。agent.traj_memory 被 `TrajMemory(task_goal="", task_id="test_task")` 重新赋值。测试导入方式为 `sys.path.insert(0, str(Path(__file__).parent.parent / "src"))`。

## F-053 伞仓 README 表明 MAI-UI 是 Qwen-UI-Agent 的前代项目
- 位置: `../README.md`（external/libs/tools/Tongyi-MAI/MAI-UI/README.md）
- 内容: 伞仓标题 "MAI-UI × Qwen-UI-Agent"，Projects 章节列出 `Qwen-UI-Agent/`（"continuation work of MAI-UI"，arXiv:2607.28227）与 `MAI-UI 1.0/`（"original MAI-UI repository content"）。License 章节引用 `./MAI-UI/NOTICE`。

## F-054 GitHub Pages 部署 workflow 存在
- 位置: `.github/workflows/deploy-pages.yml`
- 内容: 仓库含 deploy-pages.yml workflow 文件（仅记录存在；本次未展开内容）。

## 模块覆盖核对表

| 模块 | 路径 | 覆盖情况 | 对应事实 |
|---|---|---|---|
| README（Quick Start/安装/用法） | `README.md` | ✅ 已读全文 | F-001, F-004, F-005 |
| requirements | `requirements.txt` | ✅ 已读全文 | F-003 |
| LICENSE / NOTICE | `LICENSE`、`NOTICE` | ✅ 类型已记录 | F-002 |
| 伞仓 README | `../README.md` | ✅ 已读全文 | F-053 |
| src/base.py | `src/base.py` | ✅ 逐行精读（137 行） | F-009~F-011 |
| src/mai_grounding_agent.py | `src/mai_grounding_agent.py` | ✅ 逐行精读（265 行） | F-017~F-022 |
| src/mai_naivigation_agent.py | `src/mai_naivigation_agent.py` | ✅ 逐行精读（593 行） | F-023~F-034 |
| src/prompt.py | `src/prompt.py` | ✅ 逐行精读（148 行） | F-013~F-016 |
| src/unified_memory.py | `src/unified_memory.py` | ✅ 逐行精读（69 行） | F-007~F-008 |
| src/utils.py | `src/utils.py` | ✅ 逐行精读（66 行） | F-012 |
| evaluation models | `evaluation/grounding/models/MAI_UI.py` | ✅ 逐行精读（240 行） | F-035~F-037 |
| eval_local.py | `evaluation/grounding/eval_local.py` | ✅ 逐行精读（466 行） | F-038~F-041 |
| eval_server.py | `evaluation/grounding/eval_server.py` | ✅ 逐行精读（268 行） | F-037, F-040, F-043 |
| extract_metrics.py | `evaluation/grounding/extract_metrics.py` | ✅ 逐行精读（354 行） | F-044 |
| evaluation requirements | `evaluation/grounding/requirements.txt` | ✅ 已读全文 | F-045 |
| evaluation README | `evaluation/grounding/README.md` | ✅ 已读全文 | F-046~F-047 |
| output_local/OS_G.json | `evaluation/grounding/output_local/OS_G.json` | ✅ 顶层结构与样例字段已记录 | F-042 |
| output_local/SSV2.json | `evaluation/grounding/output_local/SSV2.json` | ✅ 顶层结构与样例字段已记录（metrics 五子键经检索确认） | F-042 |
| data/ 目录清单 | `evaluation/grounding/data/` | ✅ 目录级记录（未展开数据内容） | F-048 |
| cookbook/grounding.ipynb | `cookbook/grounding.ipynb` | ✅ 全部 6 cell 已读 | F-049 |
| cookbook/run_agent.ipynb | `cookbook/run_agent.ipynb` | ✅ 全部 7 cell 源码已提取（文件 6MB 因含图像输出，仅读 source） | F-050 |
| tests/test_mai_navigation_agent.py | `tests/test_mai_navigation_agent.py` | ✅ 逐行精读（577 行） | F-051~F-052 |
| tests/__init__.py | `tests/__init__.py` | ✅ 已读（空文件） | — |
| output_messages 基线 | `tests/output_messages/*.json` | ✅ 目录级记录（8 个 JSON，与用例对应） | F-052 |
| CI workflow | `.github/workflows/deploy-pages.yml` | ⚠️ 仅确认存在，未展开 | F-054 |
| 跳过项 | `.git/`、`assets/`、`resources/example_img/`、`output_server/*.jsonl`、data JSON 内容体 | 按任务要求跳过/不展开 | — |
