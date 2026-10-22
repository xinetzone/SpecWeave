# 05 AI 三层体系：使用、配置、开发

> 文档站里 AI 内容不是一篇"AI 功能介绍"，而是分成**用户使用、模型接入配置、开发者 SDK** 三层独立文档，外加一层贡献治理。这种"四层成文"结构本身就是判断系统 AI 能力是否进入可复用阶段的强证据（见[主教程 I-3](../index.md)；证据强度边界见该节末尾）。本文按层导读。

## 5.1 第一层：用户使用（开箱即跑）

### 5.1.1 麒麟模型管理工具（本地模型一键下载）

- 包名：`kylin-ai-model-manager`（新系统默认集成；缺包时 `sudo apt install kylin-ai-model-manager`）；
- 入口：开始菜单打开"麒麟模型管理工具"；
- 模型分三类：**nlp** 自然语言处理 1 个、**speech** 语音识别 5 个、**搜索** 语义搜索 2 个；支持一键下载与按类型高级下载；
- 完整性：下载后点"检查本地模型文件"校验，失败项重下；
- 网络要求：需能访问 **modelscope.cn（魔搭社区）**，初次下载还要拉依赖、耗时较长；
- 文档自述"功能非常不完善，之后会有全新设计"——属于可用但演进中的工具。

### 5.1.2 ollama 本地运行 DeepSeek-R1

《基于openKylin本地部署并运行DeepSeek-R1开源模型》给出的三步法：

```bash
# 1. 安装 ollama（三选一）
curl -fsSL https://ollama.com/install.sh | sh          # 方式一：官方脚本
# 方式二：GitHub release（文档对应 v0.5.7）手动解压到 /usr
# 方式三：关注 openKylin 公众号回复 ollama 获取网盘链接

# 2. 启动服务
ollama serve

# 3. 拉取并运行模型（新终端窗口）
ollama run deepseek-r1:1.5b
```

六档可选规格（均为蒸馏版）：1.5b（Qwen）、7b（Qwen）、8b（Llama）、14b（Qwen）、32b（Qwen）、70b（Llama）。文档演示机以 1.5b 为例，按显存/内存选档。

> 与本机技能栈的衔接：DeepSeek-R1 本地部署的硬件门槛、模型选型与 ollama 用法属于通用 Linux 技能，openKylin 文档只负责"在此发行版上可跑通"的确认。

### 5.1.3 AI 编程助手

1_4 另有《基于 KylinCode+DeepSeek 实现 AI 编程助手》——KylinCode 是社区自有的 IDE/编程入口，该文给出与 DeepSeek 组合的配置路径；IDE 侧还有《安装 Visual_Studio_Code》通用篇。

## 5.2 第二层：模型接入配置（AI 子系统管理）

1_5 下"AI模型配置指南"系列 7 篇，**按 AI 子系统版本分线**，查阅时先确认自己系统的 AI 子系统版本：

| 文档 | 适用子系统版本 | 场景 |
|---|---|---|
| 01 自选模型_公有云模型账号接入指南 | 1.3.0.0 系列 | 用公有云 API（自带 Key） |
| 02 自选模型_局域网文本类模型账号接入指南 | 1.3.0.0 系列 | 局域网内部署的推理服务 |
| 03 自选模型_本地文本类模型包构建指南 | 1.3.0.0 系列 | 自己构建本地模型包 |
| 04 云端模型账号接入指南 | 1.0.0.0–1.2.0.0 | 旧版子系统云端接入 |
| 05 自选模型账号接入指南 | 1.1.0.0–1.2.0.0 | 旧版子系统自选接入 |
| 06 openKylin 免费 token 接入指南 | 通用 | 社区发放的免费额度（含中英文档） |
| 07 Qwen2.5-3B 上架说明 | — | 本地模型商店上架记录 |

《AI模型账号获取及配置指南.md》是这个系列的导航页。配置侧的核心概念：**云端模型（API Key）/ 局域网模型（自建端点）/ 本地模型包（离线）三类来源**，对应"自选模型"能力——3.0 时代的统一封装 AI SDK（一套接口适配多家模型）是这一能力的延续（发布稿口径见[同包项目调研 F-047](../references/project-overview.md)）。

安全提示：API Key 属于敏感凭据，社区 AI 贡献守则明确禁止把 API Key/Token 上传到外部 AI 服务或提交进仓库；个人配置也应走系统凭据通道而非写死在脚本里。

## 5.3 第三层：开发者 SDK（接口手册）

> **两代 SDK 消歧（2026-10-08 源码核验，F-067～F-077）**：openKylin 3 上应用侧 SDK 实际有**两代互不从属的供给线**——本文 5.3.1 的《OpenKylin AI SDK 开发手册》对应 **Gen1 `libkylin-ai-base2 2.0`**（OCR 已落机实测）；出厂还预装了**第二代 kysdk 1.1 运行库**（genai/coreai/advanced-ai/mcp），它没有对应中文长手册、全面 IPC 异步化。读到"Kylin AI SDK / openKylin AI SDK"时先按包名与头文件根区分世代，详见 5.3.4。

### 5.3.1 麒麟 AI SDK（Gen1，4_10，137K 字符 / 4929 行）

文档站最大单篇《OpenKylin AI SDK 开发手册》，8 个能力域：

| # | 能力域 | 接口轮廓 |
|---|---|---|
| 1 | 文字识别（OCR）✅ 已落机实测 | 会话创建/初始化/销毁、结果回调、模型配置（名称+部署类型）、图片路径/图片数据两种入参、带 request_id 变体、内部事件循环开关；结果可解析整行文本、行四角点坐标、整体文本 |
| 2 | 音频处理 | 语音类会话接口 |
| 3 | 向量化 | embedding 接口（语义搜索/知识库的基础） |
| 4 | 文本生成 | 对话/补全类接口 |
| 5 | 图像生成 | 文生图类接口 |
| 6 | 主体分割 | 图像前景/主体分割 |
| 7 | 通用分割 | 通用图像分割 |
| 8 | 通用错误码 | 全 SDK 错误码对照表 |

接口设计的共同模式：**会话生命周期（create→init→set callback→set model config→invoke→destroy）+ 异步回调取结果 + 模型部署类型可配（本地/云端）**。文字识别章节作为最完整的范例，开发其他能力时可先照它的结构理解。

> **2026-10-08 落机实测补充**（详见 [Kylin AI SDK 文字识别 OCR 落机 POC](../references/ai-sdk-ocr-poc.md)，F-058～F-066/S34）：表中第 1 项 OCR 已在 openKylin-3.0-desktop WSL 经官方源 `libkylin-ai-base-dev 2.0.0.0` 实测调通。实测对本节文档口径有三点细化：① 实际头文件 `ai-base/ocr.h` 比手册描述更简，为**同步**三函数（`ocr_create_session`→`ocr_get_text_from_image_file`→`ocr_destroy_session`），手册所述 init/结果回调/request_id 变体在该版本头文件中未见（异步回调形态主要见于 `nlp.h` 文本生成）；② 默认部署策略经 `ldd` 直链 libtesseract + `gsettings` 权威值 + tesseract CLI 三源钉死为**本地 tesseract 5.3.4（chi_sim+eng）CPU 离线**，无云密钥、不依赖网络/GPU/大模型，识别可用但精度中等（有形近误识）；③ 头文件仅 C++ 友好（裸 enum 类型名无 typedef，`gcc .c` 失败、`g++ .cpp` 通过）。第 2～8 项（音频/向量化/文本生成/图像生成/两类分割/错误码）仍为**成文未验证**。

### 5.3.2 openKylin SDK 与系统维护接口（4_11 / 4_8）

- 《openkylin SDK开发指南》（2026-09-15/20 经 !517 新增）：系统能力 SDK，新文档；
- 《openKylin+SDK开发指南》（1_5）：早期系统能力开发入口；
- 《维护模式手册》的 `mm-cli`：面向系统管理的命令接口；
- 《语音助手适配说明》：应用接入语音助手的适配指引。

### 5.3.3 与 3.0 智能体底座的关系

文档站 SDK 手册描述的是**应用调用 AI 能力**的接口层；3.0 发布的智能体开放底座（模型/记忆/工具/系统权限/桌面能力统一架构、智能体经 MCP 调桌面能力、openkylin-skills 技能仓库）属于更新的平台层，其权威事实以 3.0 发布新闻与后续更新的 SDK 文档为准。读到两代接口并存时，按文档日期与子系统版本区分。

### 5.3.4 源码层补充：Gen2 kysdk 栈与引擎插件层（2026-10-08，huanghe 只读核验）

> 详见 [openKylin 3 AI 子系统源码架构剖析](../references/ai-subsystem-source-architecture.md)（F-067～F-077/S35）。本节是导读，证据以该文为准；本轮为只读核验，**未装包、未启服务、未跑端到端推理**。

- **Gen2 客户端出厂已装但只是薄代理**：`libkysdk-genai-nlp0/-vision0`、`libkysdk-coreai-speech0/-vision0`、`libkysdk-advanced-ai0`、`libkysdk-mcp` 等运行库随系统安装，但包 Depends/`ldd` 不含任何推理库；调用经 **per-uid 私有 unix socket 上的 D-Bus**（`/tmp/.kylin-ai-runtime-unix/<uid>/genai-nlp.sock`，源码常量、运行时未验证）转发给 `kylin-ai-runtime`，全异步、信号回传（如 `ChatNlpResult`）。
- **能力在引擎插件层**：上游 `kylin-ai-engine` 仓定义 C++ `AbstractAiEngine` 插件 ABI（7 个能力引擎头，与手册 8 域对应；区分云引擎/内置引擎/OpenAI 兼容自定义引擎）；云厂商引擎与 ondevice 本地引擎都是该 ABI 的实现插件。
- **本地文本生成 = Triton 客户端链路**：`kylin-ondevice-nlp-engine` 本身只连本机 Triton（HTTP :8000/gRPC :8001，llama.cpp 采样参数）；完整链路为 genai-nlp0 → kylin-ai-runtime → engine-plugins → ondevice-nlp-engine → kytensor-server(Triton 2.49) → llm-backend/libllama → GGUF。镜像**预装的只是最后三行推理底座**，打通还需引擎插件 2 包（huanghe 源可装未装）＋ 模型仓库 ＋ 自备 GGUF——5.3.1 表中第 4 项"文本生成"的本地路径由此从 F-066 的粗略登记升级为包级精确链路。
- **不要据包名过度宣称**：`libkysdk-mcp` 仅提供 client/server **共享库**，镜像里没有可调用的 MCP 服务或技能市场；"源中无候选"（6 家云厂商引擎、ondevice-vision/embedding 等）仅是 2026-10-08 huanghe 源快照。
- **源码引用纪律**：一切以 `openkylin/huanghe` 分支的 `debian/control` 与本机二进制为准；47 仓 `repos.md` 只存在于 nile/nile-sp2 分支；Gen1 源仓无 huanghe 分支且公开源码与 2.0.0.0 二进制存在已证实的分叉——引用上游代码前先核分支与代号。

## 5.4 治理层：AI 辅助贡献守则（使用者也应了解）

2026-08-01 发布的 9 节守则，核心规则：

- **人类负全责**：AI 只做辅助，贡献者必须能解释、调试、维护提交内容；
- **披露模板**（实质性 AI 内容时）：

  ```
  AI usage:
  Tool/model: <工具或模型名称>
  Usage: <代码理解/初稿/测试/润色/翻译/调试/其他>
  Human review: 我已审阅并测试，确认理解其内容。
  ```

  或提交信息加 `Assisted-by: <模型>` + 人类的 `Signed-off-by`（AI 不能代签 CLA）。
- **无需披露**：拼写检查、语法润色、普通 IDE 补全等轻微辅助；
- **明令禁止**：不验证直接贴 AI 输出、批量低质 PR/Issue、编造测试结果/性能数据/漏洞影响、把评审意见原样丢给 AI 改、未经批准的 AI Bot 自动提 PR/评论；
- **数据红线**：不得向外部 AI 上传未公开代码、内部资料、用户隐私、漏洞细节、API Key、Token、密码、证书、私钥。

这份守则同时是使用者评估社区 AI 内容可信度的依据：带规范披露与人工验证声明的提交可信度高于无披露内容。

## 5.5 学习者路径建议

1. **只想体验**：5.1 节工具装上，ollama 跑 1.5b；
2. **要接自己的模型/Key**：先查 AI 子系统版本，再进 5.2 对应分版文档；
3. **要开发 AI 应用**：精读 5.3.1 文字识别章节掌握会话模式，再套用到其他能力域，配合第 8 章错误码；
4. **要贡献**：先读 5.4 守则，再按[07 社区治理](07-community-and-contribution.md)签 CLA、走 PR。

> **实测状态声明（2026-10-08 更新）**：本节内容原为纯文档导读，现 **OCR 一域已完成落机 POC**（装官方源 `libkylin-ai-base-dev 2.0.0.0` → g++ 调通 → 三源钉死本地 tesseract CPU 离线，见 [OCR POC](../references/ai-sdk-ocr-poc.md)）；仍**未**在本机安装 `kylin-ai-model-manager`、**未**跑通 ollama 六档模型、**未**调用音频/向量化/文本生成/图像生成/两类分割任一接口（镜像虽预装 Triton+llama.cpp 引擎骨架，但需自备 GGUF 模型或云端密钥）。模型规格的硬件门槛（尤其 32b/70b 档）以 ollama 与模型卡说明为准；其余能力生产采用前仍须按主教程 I-3"证据边界"各自做最小 POC——OCR 实测同时证明了该 POC 的必要性：手册可得不等于接口一致性/识别精度可直接放心采用。同日另完成 **AI 子系统源码级架构核验**（F-067～F-077，只读未装包）：两代 SDK 均为 IPC 薄代理、Gen2 客户端出厂齐备而引擎插件/模型缺省、本地 NLP 包级链路已精确到 Triton+GGUF（见 5.3.4 与[源码架构剖析](../references/ai-subsystem-source-architecture.md)），但端到端 NLP 仍属下一阶段 POC。

> 上一篇：[04 桌面使用](04-desktop-usage.md) ｜ 下一篇：[06 开发者基础设施](06-developer-infrastructure.md)
