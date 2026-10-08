---
type: Reference
id: "openkylin-ai-subsystem-source-architecture"
title: "openKylin 3 AI 子系统源码架构剖析：两代 SDK、运行时 D-Bus 与引擎插件层（huanghe 本机核验）"
category: "tech"
tags:
  - openkylin
  - ai-sdk
  - kylin-ai-subsystem
  - kytensor
  - triton
  - dbus
  - source-analysis
date: "2026-10-08"
last_updated: "2026-10-08"
status: "verified"
author: "SpecWeave Agent（方法论编排 session sc-20261008-openkylin-source-deepdive）"
summary: "在 openKylin-3.0-desktop WSL（huanghe）上以 dpkg/apt 只读核验结合 Gitee 上游源码（kylin-ai-subsystem、kylin-ai-engine、kysdk-ai-common、libkysdk-genai-*、kylin-ondevice-nlp-engine、libkylin-ai-base），还原 openKylin 3 AI 子系统的真实分层：Gen1 libkylin-ai-base2 与 Gen2 kysdk 1.1 两套 SDK 同机并存、SDK 全部是 D-Bus/IPC 代理不含推理、Gen2 走 per-uid 私有 unix socket 接 kylin-ai-runtime、引擎以 C++ AbstractAiEngine 插件方式接入、本地文本生成链路终点是预装的 kytensor(Triton)+llama.cpp，并给出 huanghe 官方源组件可用性矩阵与源码分支错位的证据边界。"
security_level: "public"
knowledge_type: "conditional"
validation_status: "verified"
source: "一手信源：① openKylin-3.0-desktop WSL（huanghe，WSL 3.0.2.0）本机 dpkg/apt/dbus/头文件只读核验（2026-10-08）；② Gitee openKylin 组织源码仓库浅克隆审阅：kylin-ai-subsystem（openkylin/huanghe 与 upstream 分支）、kylin-ai-engine、kysdk-ai-common、libkysdk-genai-nlp、libkysdk-genai-vision、kylin-ondevice-nlp-engine（默认分支 openkylin/nile）、libkylin-ai-base（upstream 分支）。采集于 2026-10-08。范围严格限定 openKylin 3（huanghe）；nile/nile-sp2 世代内容仅在与 huanghe 已发组件重合时作旁证。"
---

# openKylin 3 AI 子系统源码架构剖析

> 本文是 [OCR 落机 POC](ai-sdk-ocr-poc.md) 的源码层续作：POC 回答了"libkylin-ai-base2 的 OCR 能不能跑"，本文回答"openKylin 3 的 AI 子系统整体由哪些层、哪些包、哪些进程构成，Gen1/Gen2 两套 SDK 是什么关系，本地文本生成的完整链路终点在哪里"。
>
> **范围声明**：只覆盖 **openKylin 3（huanghe）**——一切结论以本机 huanghe 软件源（`archive.build.openkylin.top/openkylin huanghe`）的已装/候选包与本机文件为准；上游仓库 `openkylin/nile*` 分支代表下一代（nile）形态，仅在其源码被 huanghe 二进制实际采用时作旁证，不据其推断 openKylin 3 的行为。

## 1. 结论先行（TL;DR）

1. **openKylin 3 上同时存在两代、互不从属的应用侧 SDK**：Gen1 `libkylin-ai-base2 2.0`（《OpenKylin AI SDK 开发手册》对应的 C ABI，OCR 直连 tesseract）与 Gen2 `libkysdk-* 1.1`（genai/coreai/advanced-ai/mcp 一组运行库）同机安装；二者头文件根、命名空间、IPC 形态都不同。
2. **两代 SDK 都不做推理，都是 IPC 代理**：Gen2 经 **per-uid 私有 unix domain socket 上的 D-Bus**（`/tmp/.kylin-ai-runtime-unix/<uid>/genai-nlp.sock`）连到 `kylin-ai-runtime`；Gen1 源码同样由 text/vision/speech/datamanagement 的 D-Bus proxy 构成，**OCR 直连 libtesseract 是唯一的进程内例外**（POC 已实测）。
3. **真正的能力层是"引擎 + 插件"**：`kylin-ai-engine` 源码仓定义 C++ `AbstractAiEngine` 插件 ABI（7 个能力引擎头文件），云厂商（百度/讯飞/百川/DeepSeek/通义/商汤）与 ondevice 本地引擎都是该 ABI 的实现插件；ondevice NLP 引擎本体只是一个 **Triton 客户端**（localhost:8000/8001），推理落在预装的 kytensor（Triton 2.49）+ llm-backend(llama.cpp)。
4. **huanghe 源是"客户端齐备、引擎与模型缺省"的半成品形态**：Gen2 客户端库与文档问答/向量库运行时出厂已装，但引擎插件元包 `kylin-ai-subsystem 1.3.0.0`、`kylin-ai-engine-plugins`、`kylin-ondevice-nlp-engine` **未安装且需手动拉取**，6 家云厂商引擎包在 huanghe 源中**不可见**，无任何 AI 守护进程默认运行（唯一 enabled 的 AI 单元是 `kytensor.service`）。
5. **源码公开度落后于发行版二进制**：Gen1 源仓只有 upstream/nile 分支、无 huanghe 分支，且 upstream 头文件与源码树都不包含本机 2.0.0.0 实际携带的 OCR 会话 API 与 tesseract 实现——公开源码与发行版二进制存在可证实的分叉（见 §7）。

## 2. 取证方法

| 通道 | 手段 | 性质 |
|---|---|---|
| 本机包数据库 | `dpkg -l` / `dpkg -s` / `dpkg -L` / `apt-cache policy\|show` | huanghe 权威事实 |
| 本机文件 | `/usr/include/kylin-ai/`、`/usr/share/wayland-sessions/`、systemd 单元、`ldd` | huanghe 权威事实 |
| 上游源码 | Gitee 浅克隆 7 个仓库（默认 HEAD 与指定分支），只读审阅头文件/源码/打包文件 | 架构形态旁证 |
| 排除项 | 不安装任何新包、不启动服务、不下载模型 | 只读核验 |

源码探针仓库（2026-10-08，探针副本不入库）：`kylin-ai-subsystem`（分支 `openkylin/huanghe` 与 `upstream`）、`kylin-ai-engine`（upstream）、`kysdk-ai-common`（upstream）、`libkysdk-genai-nlp`（upstream）、`libkysdk-genai-vision`（upstream）、`kylin-ondevice-nlp-engine`（默认分支 `openkylin/nile`）、`libkylin-ai-base`（upstream）。

## 3. 本机 AI 组件现状：按层清点（huanghe）

### 3.1 出厂已安装

| 层 | 包（版本） | 作用 |
|---|---|---|
| Gen1 SDK | `libkylin-ai-base2 2.0.0.0-ok1.0` + `-dev`（POC 时装入） | 手册 API；OCR 进程内直连 tesseract，其余能力为 D-Bus proxy |
| Gen1 运行时 | `kylin-ai-runtime 1.1.0.1-ok0.21`（提供 `/usr/bin/kylin-ai-runtime`） | Gen2 D-Bus 服务端载体 |
| Gen2 公共库 | `libkysdk-ai-common 1.1.0.1-ok0.5` | 枚举/错误码/宏（`kylin-ai/common/*.h`） |
| Gen2 生成式 | `libkysdk-genai-nlp0 1.1.0.1-ok1.6`、`libkysdk-genai-vision0 1.1.0.1-ok1.5` | 文本/图像生成 D-Bus 代理 |
| Gen2 核心能力 | `libkysdk-coreai-speech0 1.1.0.1-ok1.5`、`libkysdk-coreai-vision0 1.1.0.1-ok1.3` | 语音/视觉（OCR 等）代理 |
| Gen2 高级/MCP | `libkysdk-advanced-ai0 1.0.0.1-ok0.10`、`libkysdk-mcp 1.0.0.0-ok0.1`（含 `libkysdk-mcp-client.so`/`-server.so`） | 高级能力聚合；MCP 客户端/服务端**库级**底座 |
| 业务框架 | `libkyai-assistant0 1.0.0.1-ok2.5`、`libkyai-config0 1.1.0.1-ok2.6`、`libkyai-business-framework 1.2.0.0-ok0.5`、`libkyai-data-management-client 1.2.0.0-ok0.5` | 助手/配置/业务编排/数据管理客户端 |
| 文档问答/RAG | `libkylin-ai-document-qa-service 1.2.0.0-ok0.7`、`libkysdk-vector-engine-client 1.2.0.0-ok0.7` | 文档问答服务与向量库客户端（另见 F-059 的 runtime 内含组件） |
| 推理底座 | `kytensor-server/client/python 2.49.0.6-0ok11`（即 Triton 2.49 定制）、`kytensor-llm 1.0.0-ok0.7~1`（llama.cpp）、`llm-backend 1.0.1-0ok3`、`onnxruntime-backend 1.0.0-0ok3`、`libonnxruntime 1.20.1` | Triton 服务 + llama.cpp/ONNX Runtime 两类后端 |

### 3.2 huanghe 源可装但未安装

| 包（候选版本） | 角色 |
|---|---|
| `kylin-ai-subsystem 1.3.0.0-ok0.4` | 元包，一条 Depends 拉齐全栈（见 §6） |
| `kylin-ai-engine-plugins 1.1.0.1-ok1.5` | 引擎插件集合（元包依赖项） |
| `kylin-ai-subsystem-plugin 1.0.0.2-ok1.13` | 子系统插件管理 |
| `kylin-ai-subsystem-modelconfig 1.0.0.1-ok1.11` | 模型配置（对应 POC 中 gsettings model-config 的后端） |
| `kylin-ondevice-nlp-engine 1.0.0.0-ok0.2` | 本地 NLP 引擎插件（Triton 客户端，见 §5） |

### 3.3 huanghe 源中不可见（apt-cache policy 无候选）

`kylin-ai-engine`（同名守护包）、`kylin-ondevice-vision-engine`、`kylin-ondevice-embedding-engine`、`kylin-coreai-embedding`，以及 6 家云厂商引擎包（`kylin-{baidu,deepseek,qwen,sensetime,baichuan,xunfei}-*-engine`）。它们出现在 nile 世代的 `repos.md`/元包依赖里，但**在本机此刻的 huanghe 源取不到**——不解读为"永久不发布"，只登记为 openKylin 3 huanghe 当前仓库状态。

### 3.4 进程与服务面

- `systemctl list-unit-files` 中 AI 相关**仅 `kytensor.service` enabled**；但 POC 阶段已核验无模型仓库、无监听、无推理进程（[F-058](ai-sdk-ocr-poc.md)）。
- 不存在运行中的 `kylin-ai-runtime` 守护：它是 Gen2 SDK 首次调用时经私有 socket 对接的服务端载体（会话式/按需），桌面镜像默认不跑 AI 业务。

## 4. 两代 SDK 对照（Gen1 vs Gen2）

| 维度 | Gen1：libkylin-ai-base 2.0 | Gen2：kysdk 1.1 |
|---|---|---|
| 手册/包名 | 《OpenKylin AI SDK 开发手册》；`libkylin-ai-base2`/`-dev`，Source 名 `libkylin-ai-base` | 无对应中文长手册；`libkysdk-genai-*`/`coreai-*`/`advanced-ai`/`mcp` 多包 |
| 头文件根 | `/usr/include/kylin-ai/{base,common,config}.h` + `ai-base/{ocr,nlp,speech,vision,modelconfig}.h` | 源码形态 `kylin-ai/genai/text/*.h`、`kylin-ai/genai/vision/*.h`、`kylin-ai/common/*.h`（本机仅装运行库，无头文件） |
| ABI/语言 | `extern "C"` C ABI；但 enum 无 typedef，纯 C 不可编译（[F-062](ai-sdk-ocr-poc.md)） | C ABI 导出（`AISDK_EXTERN`）+ C++ 内部实现（proxy 类位于 `kyai::genai::nlp` 命名空间） |
| 调用形态 | OCR 同步三函数；NLP 异步回调；speech/vision 经 D-Bus proxy | 全异步：`*_create_session`→`init_session`→`result_set_callback`→`*_async`，信号回传（如 `ChatNlpResult`），超时 1 小时 |
| IPC | 源码内 `*processorglue.c`（gdbus 骨架）+ `*processorproxy.cpp` 连后端服务；**OCR 例外走进程内 libtesseract** | **per-uid 私有 unix socket 上的 D-Bus**：`unix:path=/tmp/.kylin-ai-runtime-unix/<uid>/genai-nlp.sock`（gdbus `new_for_address_sync` 直连，不经 system/session bus），对象路径 `/com/kylin/AiRuntime/GenAiNlp`，接口 `com.kylin.AiRuntime.GenAiNlp` |
| 配置 | dconf/gsettings `org.openkylin.aisdk.*`（POC 实测读取错位，[F-065](ai-sdk-ocr-poc.md)） | 经 modelconfig 服务/包；`ChatModelConfig` 结构体随会话下发 |
| 出厂状态 | 运行库随系统（POC 时装 -dev） | genai/coreai/advanced/mcp 运行库**全部预装**，但服务端引擎缺省 |

> 关键架构判断：**两代都是薄代理**。Gen2 客户端包的 Depends 只有 glibc/gcc/libstdc++/glib2/jsoncpp，`ldd` 无任何推理库；源码 `genainlpserviceproxy.cpp` 的全部职责是组 GVariant 参数、发 D-Bus 调用、解析 `ChatNlpResult` 信号。推理发生在 socket 另一端的 runtime + engine plugin 中。

## 5. 引擎插件层与本地 NLP 的完整链路

### 5.1 引擎插件 ABI（kylin-ai-engine 源码）

`include/kylin-ai/ai-engine/aiengine.h` 定义 C++ 抽象基类 `ai_engine::AbstractAiEngine`，插件必须实现：

- `engineName()`、`isCloud()`（云端引擎）、`isBuiltInEngine()`（**内置模型、调用者不可切换，注释明确点名"向量化模型、OCR 等"**）、`isCustomModelEngine()`（兼容 OpenAI chat API 的自定义端点，默认 false）；
- `modelInfo()`/`setCurrentModel()`/`currentModel()`/`setConfig(json)`。

同目录 7 个能力引擎头文件与手册 8 能力域一一对应：`textrecognitionengine`（OCR）、`textgenerationengine`、`imagegenerationengine`、`imageprocessengine`（分割）、`speechengine`、`embeddingengine`，加 `aienginepluginfactory`（插件工厂）与 result/error。本机 `-dev` 头文件目录 `/usr/include/kylin-ai/plugins/ai-engines/` 只露出 `baiduspeechengine.h`、`xunfeispeechengine.h` 两个语音云引擎插件头。

### 5.2 ondevice NLP 引擎 = Triton(llama.cpp) 客户端

`kylin-ondevice-nlp-engine`（源码默认分支 `openkylin/nile`，二进制 1.0.0.0-ok0.2 在 huanghe 源）实现极小：二进制 Depends 仅 libc/libgcc/libstdc++/libjsoncpp；其 `nlp/llm.h` 直接 `#include <triton/client/grpc_client.h>`，内置：

- HTTP 端点 `http://localhost:8000`、gRPC 端点 `localhost:8001`（Triton 标准端口）；
- llama.cpp 风格采样参数：`n_predict=512`、`top_k=40`、`top_p=0.95`、`temperature`、`lora_scale`、`cache_prompt`、停止词 `<|im_end|>`、流式回调。

由此，**openKylin 3 本地文本生成的完整链路**（包级精确版，修正 [F-066](ai-sdk-ocr-poc.md) 的粗略登记）：

```
应用
 └─ libkysdk-genai-nlp0（D-Bus over 私有 unix socket）
     └─ kylin-ai-runtime（/usr/bin/kylin-ai-runtime）
         └─ kylin-ai-engine-plugins（引擎框架/工厂）
             └─ kylin-ondevice-nlp-engine（Triton 客户端插件）  ← huanghe 可装未装
                 └─ kytensor-server :8000/:8001（Triton 2.49，预装未配模型）
                     └─ llm-backend → libllama.so / libggml-cpu（kytensor-llm，预装）
                         └─ Triton 模型仓库中的 GGUF 模型（镜像不附带，需自备）
```

已预装的只是最后三行的推理底座；缺 `kylin-ai-engine-plugins` + `kylin-ondevice-nlp-engine` + 模型仓库配置 + GGUF 四件，链路不通。云端路径则把引擎插件换成云厂商包 + 账号配置（huanghe 源未见厂商包）。

### 5.3 RAG/文档问答支线

`libkylin-ai-document-qa-service 1.2.0.0` + `libkysdk-vector-engine-client 1.2.0.0` + `libkyai-business-framework` + data-management 客户端已装，与元包依赖中的 `kylin-ai-vector-engine 1.2.0.1`（**未装**）、`kylin-ai-python-env`（未装）构成文档问答子系统；客户端先行、服务端缺省的形态与 NLP 一致。

## 6. 元包即架构图：kylin-ai-subsystem 的 huanghe 依赖清单

huanghe 分支 `debian/control`（候选 1.3.0.0-ok0.4）的 Depends 就是 openKylin 3 官方认定的全栈清单（均限定 `[amd64 arm64]]`，摘录分组）：

- 数据/知识：`kyai-data-management-service`、`libkyai-data-management-client`、`libkyai-business-framework`、`kylin-ai-document-qa-service`、`kylin-ai-knowledge-base-service`、`libkylin-ai-document-qa-service`、`kylin-ai-document-service`(+lib)、`kylin-ai-python-env`、`libkysdk-vector-engine-client`、`kylin-ai-vector-engine`；
- 核心运行时：`kylin-ai-runtime >= 1.1.0.1`、`kylin-ai-engine-plugins`、`kylin-ai-subsystem-modelconfig`、`kylin-ai-abstract-models`、`libkysdk-ai-common`；
- 两代能力 SDK：`libkyai-assistant0`、`libkyai-config0`、`libkysdk-coreai-speech0/-vision0`、`libkysdk-genai-nlp0/-vision0`、`libkysdk-advanced-ai0`、`libkylin-coreai-embedding`；
- 推理底座：`kytensor-client/server/python >= 2.49.0.6-0ok9`、`onnxruntime-backend`、`llm-backend`、`kytensor-llm`。

注意元包**不依赖 Gen1 `libkylin-ai-base2`**——POC 所用手册 SDK 与这套 kysdk 全栈在打包层是两条独立供给线。

> 分支纪律：该仓库 `upstream`/`openkylin/nile-sp2` 分支的 `repos.md`（47 个仓库 + `build-deploy.sh` 一键构建）是**下一代源码总装图**；huanghe 分支只有 `debian/` + 一行 README，没有 repos.md。谈 openKylin 3 时以 control 为准，勿把 nile 的 47 仓清单安到 3.0 上。

## 7. V 对抗审查：证据边界与已排除的误判

1. **源码-二进制分叉（已证实，不强行解释）**：Gen1 源仓 `libkylin-ai-base` 仅有 `upstream/openkylin/nile(-sp2)/ubuntu/noble/debian/unstable` 分支，无 huanghe；其 `upstream` 的 `ocr.h` 只声明 `const char* ocr_get_text(const char*)`，全树无 `ocr_create_session`、无任何 tesseract 实现文件。而本机 `libkylin-ai-base2 2.0.0.0` 携带会话式 OCR API 且 `ldd` 直链 libtesseract（[F-064](ai-sdk-ocr-poc.md)）。可下结论：**公开 upstream 源码落后/分叉于 huanghe 发行版二进制**；不可下结论：分叉的具体提交在哪（打包分支未公开）。同类现象：ondevice 引擎源码 HEAD 在 `openkylin/nile`，二进制却进了 huanghe 源——openKylin 的"发行版分支 ↔ 源码分支"不是一一映射。
2. **"无候选"≠"不支持"**：§3.3 的缺失项只代表 2026-10-08 huanghe main/proposed 源的快照；元包 control 已为云厂商/embedding 等留位，后续 SRU 可能补入。
3. **socket 路径是源码常量、非本机抓包**：§4 的 `/tmp/.kylin-ai-runtime-unix/<uid>/genai-nlp.sock` 来自 Gen2 源码字符串；本机未装引擎端、没有实际 socket 可供 `ls` 佐证，故标注为"源码级事实"，运行时连通性未验证。
4. **未把 nile 架构当 3.0 事实**：`AbstractAiEngine` 插件 ABI 来自 upstream 头文件，属源码旁证；huanghe 二进制 `kylin-ai-engine-plugins`（未安装）是否逐字一致未做字节比对，但本机已露出的插件头（`plugins/ai-engines/*.h`）与元包依赖结构与该 ABI 相容。
5. **MCP 仅是库**：`libkysdk-mcp` 提供 client/server 共享库，不等于有可调用的 MCP 服务/技能市场——勿据此宣称"3.0 已带智能体运行时"。

## 8. 与 OCR POC 事实的对账

| POC 事实 | 源码层结论 |
|---|---|
| F-058 预装 kytensor/llm-backend 骨架无模型无服务 | 与元包 control 一致：推理底座是全栈依赖，但模型与引擎插件默认不装、服务不启 |
| F-059 SDK 未预装可装 | 精确化：**Gen1** 未预装；**Gen2 kysdk 客户端库反而是预装的**，缺的是引擎/模型侧 |
| F-061 OCR 同步三函数、NLP 异步 | 源码解释：OCR 是 `isBuiltInEngine` 式本地内置能力的进程内特例；Gen2 全面 IPC 化故全部异步 |
| F-064 ldd 直链 tesseract | Gen1 源码树其余能力均为 D-Bus proxy，反衬 OCR 直连是架构特例而非"SDK 整体本地" |
| F-065 gsettings 权威/查询错位 | model-config 有独立子系统包（modelconfig 1.0.0.1 未装），配置通道跨 Gen1 settings 与 Gen2 服务，错位有了结构性解释，但具体 Bug 归属仍待官方确认 |
| F-066 NLP 需自备 GGUF | 升级为包级精确链路（§5.2）：还差引擎插件包 2 个 + 模型仓库 + GGUF |

## 9. 未闭环事项

- 未安装 `kylin-ai-subsystem` 元包做端到端 NLP（本轮只读；属下一阶段 POC，预计下载量百 MB 级 + GGUF 1–5 GB）。
- Gen2 coreai-vision（含 OCR）与 Gen1 OCR 的结果是否同源、精度差异，未实测。
- `kylin-ai-runtime` 的会话拉起方式（systemd user? socket activation?）未在运行时验证。
- 云厂商引擎在 huanghe 的正式发布时点未知。

## 10. 相关文档

- [Kylin AI SDK 文字识别 OCR 落机 POC](ai-sdk-ocr-poc.md)——Gen1 OCR 运行时实测（F-058～F-066）
- [openKylin 3 显示服务器双栈：kywc 与 KWin 源码剖析](kylin-wayland-compositor-architecture.md)——同批源码核验的显示栈姊妹篇
- [05 AI 三层体系](../concepts/05-ai-stack.md)——文档站导读视角的 AI 栈
- [信源台账](source-inventory.md)——S35（本机只读核验 + 上游源码）

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R2 | event=CONCEPT_COMPLETED | session=sc-20261008-openkylin-source-deepdive | msg=AI子系统R完成：两代SDK/IPC/引擎插件/本地NLP链路/可用性矩阵 | ctx={"facts":"F-067~F-077"}
```
