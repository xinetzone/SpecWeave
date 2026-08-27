# Anthropic Python SDK - I阶段架构洞察

> 洞察时间：2026-08-27
> 基于：facts.md（90条事实 F-001~F-090）

## 核心架构洞察

### 洞察1: 同步/异步双轨完全对称架构
- **陈述**：SDK采用Stainless代码生成模式，构建了`Anthropic`/`AsyncAnthropic`两套完全对称的客户端体系，从客户端类到资源类再到流处理类都一一对应，通过`X-Stainless-Async`头标识请求类型，而非用单一客户端通过参数切换同步异步。
- **证据**：F-003, F-004, F-006, F-008, F-009, F-026, F-027, F-083, F-084
- **反常识**：初看会觉得大量代码重复（同步异步各写一遍），但这种设计保证了类型安全和IDE体验——同步用户不会看到异步方法，异步用户也不会被同步方法干扰；`Client`/`AsyncClient`只是别名而非真正的不同实现。
- **文档影响**：概念文档必须成对讲解同步/异步用法，但避免重复内容——在入门篇说明对称模式后，后续文档可先讲同步再用一句话说明异步等价用法；特别强调`X-Stainless-Async`头是自动设置的，用户无需手动处理。

### 洞察2: @cached_property资源懒加载代理模式
- **陈述**：所有API资源（messages, models, files, beta等）都通过`@cached_property`懒加载，客户端初始化时不创建任何资源实例，首次访问`client.messages`时才实例化对应资源类，且实例被缓存复用；`with_raw_response`/`with_streaming_response`同样采用此模式。
- **证据**：F-007, F-019, F-024, F-025, F-049, F-050, F-051, F-052, F-053
- **反常识**：用户可能以为`client.messages`是一个普通实例属性在`__init__`中创建，实际是访问时才动态生成的缓存属性；这意味着不能在初始化后轻易替换资源类，也解释了为什么资源类总是接收客户端引用作为构造参数。
- **文档影响**：客户端初始化文档需要解释懒加载机制，避免用户尝试在`__init__`前访问资源；强调资源是线程安全的（因为只创建一次）；说明这是Stainless生成SDK的标准模式，不是Anthropic特有的设计。

### 洞察3: 多云后端通过继承式复用核心客户端
- **陈述**：`AnthropicBedrock`/`AnthropicVertex`/`AnthropicAWS`等多云客户端通过继承（而非组合）复用核心`Anthropic`客户端，只重写认证相关逻辑（`_prepare_request`、`base_url`、默认头等），直接继承所有messages/beta等资源，无需重新实现任何API方法。
- **证据**：F-059, F-060, F-062, F-063, F-064, F-065, F-067, F-068, F-070, F-071, F-072, F-073
- **反常识**：直觉上多云适配应该用组合模式（核心客户端+认证策略），但实际用继承更简洁——Bedrock客户端就是一个Anthropic客户端，只是"换了个入口和签名方式"，所有上层API（messages.create等）用法完全一致，用户学习成本为零。
- **文档影响**：多云文档要强调"API用法100%兼容"，只需要讲解认证参数差异和base_url选择逻辑；提醒用户Bedrock/Vertex的默认超时、重试等配置继承自核心客户端；说明Google Cloud和AWS客户端的导入路径。

### 洞察4: Beta API通过独立命名空间+请求头版本化
- **陈述**：实验性API不通过URL路径前缀（如`/v2/`）或客户端版本号区分，而是统一挂在`client.beta`独立命名空间下，每个Beta子资源在请求时自动添加对应的`anthropic-beta`头（如`managed-agents-2026-04-01`），Agents/Memory/Sessions等新能力都在beta命名空间下迭代。
- **证据**：F-049, F-050, F-051, F-052, F-053, F-054, F-057, F-058
- **反常识**：其他SDK常把beta功能放在单独的导入路径（如`from anthropic.beta import ...`），但Anthropic把它作为客户端的一个属性访问，且自动添加版本头，用户不需要手动管理beta标记；这意味着beta API的破坏性变更只影响显式访问`client.beta`的用户。
- **文档影响**：Beta文档必须明确标注"实验性，可能变更"；讲解Agents/Memory等高级能力时，先说明beta命名空间的访问方式和版本头机制；工具调用（tool use）虽然也在beta工具链中，但要区分哪些是稳定API哪些是实验API。

### 洞察5: 中间件管线严格分离同步/异步 + 装饰器式响应包装
- **陈述**：中间件系统定义了独立的同步/异步handle方法，通过`validate_sync_middleware`/`validate_async_middleware`严格校验中间件类型，不允许混用；响应增强（原始响应/流式响应）通过独立的包装类（`AnthropicWithRawResponse`/`WithStreamingResponse`）实现，而非在方法参数中加开关。
- **证据**：F-010, F-011, F-074, F-075, F-076, F-077, F-078, F-079, F-080
- **反常识**：很多HTTP客户端用`raw=True`参数控制返回原始响应，但Anthropic用`client.with_raw_response.messages.create()`这种装饰式访问，优点是返回类型可以精确标记（IDE能正确推断类型），缺点是API调用链稍长；中间件不能同时支持同步异步，必须为两种模式分别实现。
- **文档影响**：中间件文档要给出同步/异步两个版本的示例；解释WithRawResponse模式的类型安全优势；说明内置中间件（如BetaRefusalFallbackMiddleware）的作用；错误处理文档要讲清楚哪些异常是可重试的（RetryableError标记）。

## 知识地图

### 学习路径
入门篇（建立认知） → 核心篇（掌握常用API） → 高级篇（扩展能力与定制）

### 入门篇（3个概念）
| 文档 | 核心覆盖事实 | 预期字数 |
|------|------------|---------|
| 00-overview.md | F-001~F-015, F-059~F-073, F-085~F-090 | 1500-2000 |
| 01-client-init.md | F-005, F-006, F-007, F-012~F-015, F-061, F-065, F-070 | 1000-1500 |
| 02-messages-basics.md | F-016~F-023, F-085~F-090 | 1200-1800 |

### 核心篇（4个概念）
| 文档 | 核心覆盖事实 | 预期字数 |
|------|------------|---------|
| 03-streaming.md | F-026~F-037 | 1500-2000 |
| 04-tool-use.md | F-038~F-048 | 1800-2500 |
| 05-vision-files.md | F-018（system/tool相关）, F-007（files属性） | 1000-1500 |
| 06-pagination-models.md | F-007（models属性）, F-021~F-023 | 800-1200 |

### 高级篇（3个概念）
| 文档 | 核心覆盖事实 | 预期字数 |
|------|------------|---------|
| 07-multi-cloud.md | F-059~F-073 | 1500-2000 |
| 08-beta-agents-memory.md | F-049~F-058 | 1500-2000 |
| 09-middleware-errors.md | F-010~F-011, F-074~F-084, F-085~F-090 | 1500-2000 |

## E阶段文档清单

共24个文档（6 references + 10 concepts + 6 examples + 2 根文档）

### references/（信源先行）
| # | 文件名 | 主题 | 覆盖事实 |
|---|--------|------|---------|
| 1 | sdk-client.md | 客户端入口与基础设施 | F-001~F-015, F-074~F-084 |
| 2 | messages-api.md | 消息API与流式处理 | F-016~F-037 |
| 3 | tools-beta.md | 工具系统与Beta API | F-038~F-058 |
| 4 | multi-cloud.md | 多云后端认证 | F-059~F-073 |
| 5 | types-errors.md | 类型系统与异常体系 | F-085~F-090 |
| 6 | source.md | 源码版本与目录结构 | 源码目录信息 |

### concepts/
| # | 文件名 | 主题 | 前置概念 | 对应信源 |
|---|--------|------|---------|---------|
| 1 | 00-overview.md | SDK整体架构与设计理念 | 无 | sdk-client.md |
| 2 | 01-client-init.md | 客户端初始化与配置 | 00-overview | sdk-client.md, multi-cloud.md |
| 3 | 02-messages-basics.md | Messages API基础用法 | 01-client-init | messages-api.md, types-errors.md |
| 4 | 03-streaming.md | 流式响应处理 | 02-messages-basics | messages-api.md |
| 5 | 04-tool-use.md | 工具调用（Function Calling） | 02-messages-basics | tools-beta.md |
| 6 | 05-vision-files.md | 视觉理解与文件上传 | 02-messages-basics | messages-api.md, sdk-client.md |
| 7 | 06-pagination-models.md | 分页与模型管理 | 02-messages-basics | sdk-client.md, messages-api.md |
| 8 | 07-multi-cloud.md | Bedrock/Vertex/AWS多云后端 | 01-client-init | multi-cloud.md |
| 9 | 08-beta-agents-memory.md | Beta Agents与Memory | 04-tool-use | tools-beta.md |
| 10 | 09-middleware-errors.md | 中间件扩展与错误处理 | 01-client-init, 02-messages-basics | sdk-client.md, types-errors.md |

### examples/
| # | 文件名 | 场景 | 核心API |
|---|--------|------|---------|
| 1 | 01-basic-chat.md | 基础多轮对话 | client.messages.create |
| 2 | 02-streaming-chat.md | 流式对话输出 | client.messages.create(stream=True), MessageStream |
| 3 | 03-tool-use.md | 工具调用实战 | beta_tools, ToolRunner |
| 4 | 04-vision.md | 图片理解 | messages.create（image内容块） |
| 5 | 05-bedrock-vertex.md | Bedrock/Vertex后端 | AnthropicBedrock, AnthropicVertex |
| 6 | 06-thinking-extended.md | Extended Thinking思考模式 | messages.create（thinking参数） |

### 根文档
| # | 文件名 | 说明 |
|---|--------|------|
| 1 | index.md | Bundle根索引（含okf_version frontmatter） |
| 2 | log.md | 生成与变更日志 |

## 分批生成计划
- **第一批**：references/（6个信源文档）——建立信源基础，所有后续文档的sources字段指向这些文件
- **第二批**：concepts/入门篇（3个：00-overview, 01-client-init, 02-messages-basics）——建立基础认知
- **第三批**：concepts/核心篇（4个：03-streaming, 04-tool-use, 05-vision-files, 06-pagination-models）——覆盖常用场景
- **第四批**：concepts/高级篇（3个：07-multi-cloud, 08-beta-agents-memory, 09-middleware-errors）——扩展能力
- **第五批**：examples/（6个示例文档）——对应各概念的可运行代码
- **最后**：根index.md和log.md——所有内容完成后统一写索引和日志

## 关键写作约定
1. **同步异步对称**：所有概念文档先讲同步用法，再用"AsyncAnthropic的用法完全一致，只需将客户端替换为AsyncAnthropic并使用await"一句话带过异步
2. **事实溯源**：文档中所有API声明、参数列表必须可追溯到references/信源文档，最终溯源到F-xxx事实
3. **术语统一**：Anthropic（官方客户端）、Bedrock（AWS Bedrock）、Vertex（GCP Vertex AI）三个术语首次出现时标注
4. **代码示例**：所有代码示例必须是可运行的，包含import语句和完整的client初始化
5. **Beta标注**：所有访问client.beta的API必须在文档开头标注"实验性API，可能在未来版本中变更"
