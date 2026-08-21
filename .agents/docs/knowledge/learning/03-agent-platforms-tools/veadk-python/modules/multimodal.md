---
id: multimodal-module
title: 多模态能力
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 多模态能力

## 概述

VeADK 提供了丰富的多模态能力支持，包括图片输入输出、视频生成、文本转语音（TTS）、PPT 生成等功能。这些能力通过内置工具（Built-in Tools）的形式提供，Agent 可以像调用普通工具一样调用多模态生成能力。同时，ArkLLM 原生支持图片、视频、文件等多模态输入。

> 相关源码位置：[veadk/tools/builtin_tools/](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/)

---

## 多模态能力概览

| 能力 | 工具名称 | 说明 | 默认模型 |
|------|---------|------|---------|
| 图片生成 | `image_generate` | 文生图，支持批量生成 | `doubao-seedream-5-0-260128` |
| 图片编辑 | `image_edit` | 图生图/图片编辑 | `doubao-seededit-3-0-i2i-250628` |
| 视频生成 | `video_generate` | 文生视频/图生视频，异步任务 | `doubao-seedance-2-0-260128` |
| 视频任务查询 | `video_task_query` | 查询视频生成任务状态 | - |
| 文本转语音 | `text_to_speech` | TTS 文字转语音 | Seed TTS 2.0 |
| PPT 生成 | `ppt_generate` | 根据 Markdown 大纲生成 PPTX | - (Node.js 本地生成) |
| VOD 视频点播 | `vod` | 视频点播服务工具 | - |
| 多模态输入 | ArkLLM 原生 | 图片/视频/文件输入理解 | doubao-seed 系列 |

---

## 图片输入/输出

### 多模态输入（ArkLLM 原生支持）

ArkLLM 通过火山引擎方舟 Responses API 原生支持多模态输入，包括图片、视频、文件。

> 源码位置：[models/ark_llm.py#L165-L200](file:///d:/AI/.chaos/libs/veadk-python/veadk/models/ark_llm.py#L165-L200)

**支持的输入类型：**

| 类型 | Content Type | 说明 |
|------|-------------|------|
| 图片 | `input_image` | 支持 `image_url` 或 `file_id`，可设置 `detail` 参数 |
| 视频 | `input_video` | 支持 `video_url` 或 `file_id`，可设置 `fps` 帧率 |
| 文件 | `input_file` | 支持 `file_url` 或 `file_id` |

**URI 格式：**
- 公网 URL：`https://example.com/image.jpg`
- 方舟文件 ID：`file_id://<file-id>`

```python
# 图片输入参数
ResponseInputImageParam(
    type="input_image",
    detail="auto",  # auto/low/high
    image_url="https://example.com/image.jpg",  # URL 方式
    # 或 file_id="file-xxx"  # 文件ID方式
)

# 视频输入参数
ResponseInputVideoParam(
    type="input_video",
    video_url="https://example.com/video.mp4",
    fps=1.0,
)
```

### 图片生成工具（image_generate）

`image_generate` 工具封装了火山引擎方舟的文生图 API，支持文本生成图片。

> 源码位置：[tools/builtin_tools/image_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/image_generate.py)

**默认配置：**
- 默认模型：`doubao-seedream-5-0-260128`
- API Base：`https://ark.cn-beijing.volces.com/api/v3/`
- API Key：遵循四级优先级（`MODEL_IMAGE_API_KEY` → `MODEL_AGENT_API_KEY` → settings）

**API 端点：**
```
POST {API_BASE}/images/generations
```

**支持参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | str | 图片描述提示词（必填） |
| `size` | str | 图片尺寸（如 "1024x1024", "1024x1792"） |
| `response_format` | str | 响应格式（url/b64_json） |
| `watermark` | bool | 是否添加水印 |
| `image` | str | 参考图片（图生图模式） |
| `sequential_image_generation` | str | 顺序生成模式 |
| `max_images` | int | 最大生成图片数 |
| `output_format` | str | 输出格式 |
| `tools` | list | 工具配置（如联网搜索） |

**请求示例：**
```python
async def _call_image_api(item: dict, model_name: str, timeout: int) -> dict:
    url = f"{API_BASE}/images/generations"
    body = {
        "model": model_name,
        "prompt": item.get("prompt", ""),
        "size": item.get("size"),
        "response_format": item.get("response_format"),
        "watermark": item.get("watermark"),
        # ... 其他参数
    }
    async with httpx.AsyncClient(timeout=float(timeout)) as client:
        response = await client.post(url, headers=_get_headers(), json=body)
        return response.json()
```

**认证 Headers：**
```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "veadk-source": "veadk",
    "veadk-version": VERSION,
    "User-Agent": f"VeADK/{VERSION}",
}
```

### 图片编辑工具（image_edit）

VeADK 还提供了 `image_edit` 工具用于图片编辑（图生图），默认模型为 `doubao-seededit-3-0-i2i-250628`。

> 源码位置：[tools/builtin_tools/image_edit.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/image_edit.py)
> 默认配置：[consts.py#L65-L66](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L65-L66)

---

## 视频生成与查询

### 视频生成工具（video_generate）

`video_generate` 工具封装了火山引擎方舟的视频生成 API，支持文生视频和图生视频等多种模式。视频生成是异步任务，需要轮询查询结果。

> 源码位置：[tools/builtin_tools/video_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/video_generate.py)

**默认配置：**
- 默认模型：`doubao-seedance-2-0-260128`
- API Base：`https://ark.cn-beijing.volces.com/api/v3/`
- API Key：`MODEL_VIDEO_API_KEY` → `MODEL_AGENT_API_KEY` → settings

**视频生成配置（VideoGenerationConfig）：**

```python
@dataclass
class VideoGenerationConfig:
    first_frame: Optional[str] = None           # 首帧图片 URL
    last_frame: Optional[str] = None            # 尾帧图片 URL
    reference_images: List[str] = None          # 参考图片列表
    reference_videos: List[str] = None          # 参考视频列表
    reference_audios: List[str] = None          # 参考音频列表
    generate_audio: Optional[bool] = None       # 是否生成音频
    ratio: Optional[str] = None                 # 画面比例
    duration: Optional[int] = None              # 视频时长（秒）
    resolution: Optional[str] = None            # 分辨率
    frames: Optional[int] = None                # 帧数
    camera_fixed: Optional[bool] = None         # 固定镜头
    seed: Optional[int] = None                  # 随机种子
    watermark: Optional[bool] = None            # 水印
    tools: Optional[List[Dict]] = None          # 工具（如联网搜索，仅文生视频支持）
```

> 源码位置：[video_generate.py#L53-L68](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/video_generate.py#L53-L68)

**支持的生成模式：**

| 模式 | 条件 | 说明 |
|------|------|------|
| 文生视频 | 无 first_frame/参考素材 | 纯文本生成视频，可启用 tools（联网搜索） |
| 首帧生成 | 设置 first_frame | 根据首帧图片生成后续视频 |
| 首尾帧生成 | 设置 first_frame + last_frame | 根据首尾帧生成中间视频 |
| 参考图/视频 | 设置 reference_images/reference_videos | 参考素材生成 |

**版本兼容性提示：**
```python
def _should_disable_audio(model_name: str, generate_audio: Optional[bool]) -> Optional[bool]:
    if model_name.startswith("doubao-seedance-1-0") and generate_audio is not None:
        logger.warning(
            "The `doubao-seedance-1-0` series models do not support enabling the audio field. "
            "Please upgrade to the doubao-seedance-1-5 series or higher if you want to generate video with audio."
        )
        return None
    return generate_audio
```
- Seedance 1.0 系列不支持音频生成
- Seedance 1.5+ 系列支持 `generate_audio` 参数

**API 流程：**
```
1. 创建任务：POST {API_BASE}/contents/generations/tasks
   ↓
2. 返回 task_id
   ↓
3. 轮询查询（或由 Agent 轮询）：video_task_query(task_id)
   ↓
4. 任务完成 → 返回 video_url
   （超时则返回 task_id，提示后续使用 video_task_query 查询）
```

### 视频任务查询工具（video_task_query）

`video_task_query` 工具用于查询异步视频生成任务的状态。

> 源码位置：[video_generate.py#L224-L...](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/video_generate.py#L224)

**使用场景：**
1. `video_generate` 调用超时（任务仍在运行）
2. 需要稍后再次查询任务状态
3. 批量任务状态轮询

**返回结果（VideoTaskResult）：**

```python
@dataclass
class VideoTaskResult:
    video_name: str                          # 视频名称
    task_id: Optional[str] = None            # 任务 ID
    video_url: Optional[str] = None          # 视频 URL（完成后）
    error: Optional[str] = None              # 错误信息
    error_detail: Optional[dict] = None      # 错误详情
    status: str = "pending"                  # 状态：pending/running/completed/failed
    execution_expires_after: Optional[int] = None  # 执行过期时间
```

> 源码位置：[video_generate.py#L42-L50](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/video_generate.py#L42-L50)

**Content 构建逻辑：**
```python
def _build_content(prompt: str, config: VideoGenerationConfig) -> list:
    content = [{"type": "text", "text": prompt}]
    if config.first_frame:
        content.append({"type": "image_url", "image_url": {"url": config.first_frame}, "role": "first_frame"})
    if config.last_frame:
        content.append({"type": "image_url", "image_url": {"url": config.last_frame}, "role": "last_frame"})
    for ref_image in config.reference_images:
        content.append({"type": "image_url", "image_url": {"url": ref_image}, "role": "reference_image"})
    for ref_video in config.reference_videos:
        content.append({"type": "video_url", "video_url": {"url": ref_video}, "role": "reference_video"})
    for ref_audio in config.reference_audios:
        content.append({"type": "audio_url", "audio_url": {"url": ref_audio}, "role": "reference_audio"})
    return content
```

> 源码位置：[video_generate.py#L71-L119](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/video_generate.py#L71-L119)

---

## 音频处理

### 文本转语音工具（text_to_speech / TTS）

`text_to_speech` 工具封装了火山引擎语音服务（VeSpeech），支持将文本转换为自然语音，输出 PCM 格式音频。

> 源码位置：[tools/builtin_tools/tts.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/tts.py)

**API 端点：**
```
POST https://openspeech.bytedance.com/api/v3/tts/unidirectional
```

**必需配置（环境变量）：**

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `TOOL_VESPEECH_APP_ID` | 语音服务 App ID | **（必填）** |
| `TOOL_VESPEECH_API_KEY` | 语音服务 API Key | **（必填）** |
| `TOOL_VESPEECH_SPEAKER` | 音色 ID | `zh_female_vv_uranus_bigtts` |
| `TOOL_VESPEECH_AUDIO_OUTPUT_PATH` | 音频输出目录 | 系统临时目录 |

**API 配置：**
```python
headers = {
    "X-Api-App-Id": app_id,
    "X-Api-Key": api_key,
    "X-Api-Resource-Id": "seed-tts-2.0",  # seed-tts-1.0 or seed-tts-2.0
    "Content-Type": "application/json",
}
payload = {
    "user": {"uid": user_id},
    "req_params": {
        "text": text,
        "speaker": speaker,
        "audio_params": {
            "format": "pcm",
            "bit_rate": 16000,
            "sample_rate": 24000,
            "enable_timestamp": True,
        },
        "additions": json.dumps({
            "explicit_language": "zh",
            "disable_markdown_filter": True,
            "enable_timestamp": True,
        }),
    },
}
```

**输出格式：**
- 音频格式：PCM（原始音频数据）
- 采样率：24000 Hz
- 比特率：16000 bps
- 支持时间戳输出（`enable_timestamp=True`）
- 输出路径：临时文件或指定目录，后缀 `.pcm`

### 实时语音对话

VeADK 还提供了实时语音对话能力（Realtime Voice），支持全双工语音交互，基于 WebSocket 协议。

> 源码位置：[veadk/realtime/](file:///d:/AI/.chaos/libs/veadk-python/veadk/realtime/)
> 默认配置：[consts.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py)（RealtimeModelConfig）

**相关模块：**
- `realtime/live.py` - 实时对话核心
- `realtime/doubao_realtime_voice_llm.py` - 豆包实时语音 LLM
- `realtime/protocol.py` - WebSocket 协议定义
- `toolkits/audio/tts/` - TTS 客户端
- `toolkits/audio/asr/` - ASR 语音识别客户端

> **说明**：实时语音模块主要用于低延迟语音对话场景，TTS 工具用于独立的文本转语音任务。

---

## PPT 生成工具（ppt_generate）

`ppt_generate` 工具可以根据 Markdown 格式的大纲生成 PowerPoint（.pptx）文件，并生成 WebP 预览图。该工具通过 Node.js 子进程调用 `ppt_generate.mjs` 脚本完成 PPT 文件的生成。

> 源码位置：
> - Python 工具：[tools/builtin_tools/ppt_generate.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/ppt_generate.py)
> - Node.js 生成脚本：[tools/builtin_tools/ppt_generate.mjs](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/ppt_generate.mjs)

### 依赖要求

- **Node.js 运行时**：PPT 生成需要 Node.js 环境
- **环境变量**：`VEADK_PRESENTATION_NODE` 可指定 Node.js 路径，默认使用 `node` 命令

```python
node = os.getenv("VEADK_PRESENTATION_NODE") or shutil.which("node")
if not node:
    raise RuntimeError(
        "PPT generation requires Node.js. Configure VEADK_PRESENTATION_NODE."
    )
```

### 输入格式

PPT 大纲使用 Markdown 格式，每节用 `##` 开头表示一页幻灯片：

```markdown
## 第一页标题
这是页面摘要内容。
- 要点一
- 要点二
- 要点三
来源：https://example.com

## 第二页标题
页面摘要...
- 要点 A
- 要点 B
```

**支持的字段：**
- `## 标题`：每页标题（必填）
- 第一行非列表文本：页面摘要（summary）
- `- /* `：要点列表（bullets）
- `Sources:` 或 `来源：`：参考来源，用 `|` 分隔

### 限制配置

```python
_MAX_SLIDES = 20      # 最多 20 页
_MAX_BULLETS = 7      # 每页最多 7 个要点
_MAX_SOURCES = 12     # 每页最多 12 个来源
```

### 输出文件

- **PPTX 文件**：标准 PowerPoint 格式，MIME 类型 `application/vnd.openxmlformats-officedocument.presentationml.presentation`
- **WebP 预览图**：封面预览，MIME 类型 `image/webp`
- **超时**：120 秒超时

```python
process = await asyncio.create_subprocess_exec(
    node, str(runner),
    str(input_path),    # JSON 输入
    str(output_path),   # PPTX 输出
    str(preview_path),  # WebP 预览输出
)
stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
```

### 文件名处理

```python
def _safe_filename(filename: str, title: str) -> str:
    value = Path(filename.strip()).name if filename.strip() else ""
    if not value:
        value = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", title).strip("-")
    value = value[:100] or "presentation"
    if not value.lower().endswith(".pptx"):
        value += ".pptx"
    return value
```
- 支持中文文件名
- 自动清理特殊字符
- 默认添加 `.pptx` 后缀
- 文件名最长 100 字符

---

## 其他多模态工具

### VOD 视频点播工具

`vod` 工具提供火山引擎视频点播（VOD）服务集成，支持视频上传、管理等操作。

> 源码位置：[tools/builtin_tools/vod.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/vod.py)

---

## OpenTelemetry 追踪

所有多模态工具都集成了 OpenTelemetry 追踪，自动记录调用 Span：

```python
tracer = trace.get_tracer("veadk.video_generate")
# 或
tracer = trace.get_tracer("veadk")

def add_span_attributes(span: Span, tool_context: ToolContext, ...):
    span.set_attribute("gen_ai.agent.name", agent_name)
    span.set_attribute("gen_ai.app.name", app_name)
    span.set_attribute("gen_ai.user.id", user_id)
    span.set_attribute("gen_ai.session.id", session_id)
    span.set_attribute("gen_ai.system", "Ark")
    # Token 使用量等属性
```

> 源码位置：[image_generate.py#L121-L150](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/image_generate.py#L121-L150)

---

## 使用示例

### 图片生成

```python
from veadk import Agent
from veadk.tools.builtin_tools.image_generate import image_generate

agent = Agent(
    name="image-creator",
    model_name="doubao-seed-2-1-pro-260628",
    tools=[image_generate],
)

# Agent 会自动调用 image_generate 工具
# 示例 prompt: "帮我生成一张未来城市的图片，赛博朋克风格"
```

### 视频生成

```python
from veadk import Agent
from veadk.tools.builtin_tools.video_generate import video_generate, video_task_query

agent = Agent(
    name="video-creator",
    model_name="doubao-seed-2-1-pro-260628",
    tools=[video_generate, video_task_query],
)

# 文生视频示例
# "生成一只小猫在草地上奔跑的视频"
# Agent 会调用 video_generate，若超时则使用 video_task_query 轮询
```

### 图生视频（首帧控制）

```python
# 视频生成配置示例（概念示例，实际由 Agent 调度）
config = VideoGenerationConfig(
    first_frame="https://example.com/first-frame.jpg",
    duration=5,
    ratio="16:9",
    generate_audio=True,
)
```

### 文本转语音

```python
from veadk import Agent
from veadk.tools.builtin_tools.tts import text_to_speech

# .env 配置
# TOOL_VESPEECH_APP_ID=your-app-id
# TOOL_VESPEECH_API_KEY=your-api-key
# TOOL_VESPEECH_SPEAKER=zh_female_vv_uranus_bigtts

agent = Agent(
    name="tts-agent",
    model_name="doubao-seed-2-1-pro-260628",
    tools=[text_to_speech],
)

# Agent 调用 text_to_speech("你好，欢迎使用VeADK")
# 返回 PCM 音频文件路径
```

### PPT 生成

```python
from veadk import Agent
from veadk.tools.builtin_tools.ppt_generate import ppt_generate

agent = Agent(
    name="ppt-creator",
    model_name="doubao-seed-2-1-pro-260628",
    tools=[ppt_generate],
)

# Agent 先生成 Markdown 大纲，再调用 ppt_generate
# 输出 .pptx 文件和 WebP 预览图
```

---

## 环境变量配置汇总

| 环境变量 | 模块 | 说明 | 必填 |
|---------|------|------|------|
| `MODEL_IMAGE_API_KEY` | 图片生成 | 图片模型 API Key | 否（回退到 MODEL_AGENT_API_KEY） |
| `MODEL_IMAGE_API_BASE` | 图片生成 | 图片 API Base | 否 |
| `MODEL_VIDEO_API_KEY` | 视频生成 | 视频模型 API Key | 否（回退到 MODEL_AGENT_API_KEY） |
| `MODEL_VIDEO_API_BASE` | 视频生成 | 视频 API Base | 否 |
| `TOOL_VESPEECH_APP_ID` | TTS | 语音服务 App ID | **是** |
| `TOOL_VESPEECH_API_KEY` | TTS | 语音服务 API Key | **是** |
| `TOOL_VESPEECH_SPEAKER` | TTS | 音色 ID | 否（默认女声） |
| `TOOL_VESPEECH_AUDIO_OUTPUT_PATH` | TTS | 音频输出目录 | 否（默认临时目录） |
| `VEADK_PRESENTATION_NODE` | PPT | Node.js 路径 | 否（默认 `node`） |

---

## 功能状态说明

| 功能 | 状态 | 备注 |
|------|------|------|
| 图片输入理解 | ✅ 完整支持 | ArkLLM Responses API 原生 |
| 图片生成 | ✅ 完整支持 | 豆包 Seedream 模型 |
| 图片编辑 | ✅ 完整支持 | 豆包 SeedEdit 模型 |
| 视频生成（文生视频） | ✅ 完整支持 | 豆包 Seedance 模型，异步任务 |
| 视频生成（图生视频） | ✅ 完整支持 | 首帧/首尾帧/参考图模式 |
| 视频任务查询 | ✅ 完整支持 | 轮询异步任务状态 |
| 视频音频生成 | ⚠️ 部分支持 | Seedance 1.5+ 支持，1.0 不支持 |
| 文本转语音（TTS） | ✅ 完整支持 | PCM 格式输出，需配置 App ID/Key |
| 语音识别（ASR） | ✅ 存在 | 在 toolkits/audio/asr/ 中 |
| 实时语音对话 | ✅ 存在 | realtime 模块，WebSocket |
| PPT 生成 | ✅ 完整支持 | 需 Node.js 环境 |
| 音频输入理解 | ⚠️ 部分支持 | 通过 video_generate 的 reference_audios 间接支持 |
