# 事实登记：OpenViking 博文 → OKF 知识包

> F-001~F-032 为博文事实；F-033~F-048 为官方源核验补充。
> 核验状态：✅ 官方一致 ｜ ⚠️ 口径差异/单源 ｜ 📌 作者观点（非客观事实）
> 博文：《字节又开源了一个顶级 Agent 项目！》，公众号 macrozheng，作者梦想de星空，2026-09-09 14:10。

## A. 博文元信息与定位

| 编号 | 事实 | 核验 |
|------|------|------|
| F-001 | 标题《字节又开源了一个顶级 Agent 项目！》；公众号 macrozheng；作者署名"梦想de星空"；原创标记；2026-09-09 14:10 发布于江苏 | ✅ 页面元数据 |
| F-002 | 项目地址：https://github.com/volcengine/OpenViking | ✅ |
| F-003 | 博文称该项目 GitHub 35K+ star，"冲着 Agent 记不住事这个老毛病来" | ✅ F-033 |
| F-004 | 定位：面向 AI Agent 的开源上下文数据库；记忆、资源、技能统一存放在 viking:// 协议下的虚拟文件系统 | ✅ README |
| F-005 | 与查黑盒向量库不同，Agent 用 ls、tree、find 等熟悉操作浏览自己的上下文 | ✅ README |
| F-006 | 内容写入时被处理成 L0 摘要、L1 概览、L2 详情三层，按需加载省 token | ✅ F-037 |
| F-007 | 每次检索留下目录浏览轨迹，结果不对能回溯到具体路径 | ✅（目录感知检索，F-045） |

## B. 博文事实：三大特性

| 编号 | 事实 | 核验 |
|------|------|------|
| F-008 | 特性①目录递归检索：先定位得分最高的目录，再逐层下探，结果连同周边上下文一起返回 | ✅ README/FAQ |
| F-009 | 特性②会话沉淀记忆：会话结束后异步把用户偏好和 Agent 经验写成长期记忆，下次对话自动召回，跨会话不失忆 | ✅ F-038 |
| F-010 | 特性③多 Agent 共用：同一份记忆通过插件、MCP、SDK 接给 Claude Code、Codex、Cursor 等外部 Agent，跨项目共用 | ✅ F-040（口径细化） |

## C. 博文事实：部署配置

| 编号 | 事实 | 核验 |
|------|------|------|
| F-011 | 以一台 Linux 服务器（192.168.3.101）为例完整部署 | — 博文环境 |
| F-012 | 创建配置文件 ov.conf 并复制到 /mydata/openviking 目录 | ✅（配置路径机制 F-035） |
| F-013 | server 块：host 0.0.0.0、port 1933、root_api_key "abc123456efg"、public_base_url "http://192.168.3.101:1933" | ✅ 字段存在（F-035） |
| F-014 | storage 块：workspace "./data"；agfs.backend "local"；vectordb.backend "local" | ✅ |
| F-015 | embedding.dense：api_base 为阿里云百炼 OpenAI 兼容接口 https://dashscope.aliyuncs.com/compatible-mode/v1 ，provider "openai"，dimension 1024，model "text-embedding-v4" | ✅ F-042/F-046 |
| F-016 | vlm：同走百炼 OpenAI 兼容接口，model "qwen3-vl-plus"；embedding 与 vlm 一个 API Key 够用 | ✅ F-046 |
| F-017 | 四块配置职责：server=监听地址/端口/管理密钥（public_base_url 让服务端上传文件时回客户端可达地址）；storage=记忆与向量数据落盘位置；embedding=文本转向量；vlm=生成摘要、理解内容，兼作 VikingBot 思考模型 | ✅ 配置文档 |
| F-018 | 拉取镜像：`docker pull ghcr.io/volcengine/openviking:latest` | ✅ F-035 |
| F-019 | 运行容器：`docker run --name openviking -p 1933:1933 -v /mydata/openviking:/app/.openviking -d ghcr.io/volcengine/openviking:latest` | ✅ F-035 |
| F-020 | `curl http://192.168.3.101:1933/health` 验证；博文称返回 status:ok、healthy:true，并带出服务版本和 auth_mode | ⚠️ F-036 |

## D. 博文事实：Web Studio 配置

| 编号 | 事实 | 核验 |
|------|------|------|
| F-021 | Studio 是自带 Web 控制台，地址 http://192.168.3.101:1933/studio；首页仪表盘展示上下文数据量、Token 用量、检索次数；左侧导航分工作区、活动、设置、资源四个区 | ✅ /studio 同源 |
| F-022 | 「连接设置」填入 ov.conf 的 root_api_key（Root 或管理员 API 密钥）后"控制台权限"显示正常；页面提示还缺用户 API 密钥；管理密钥只管管理操作，工作台和数据接口需用户密钥 | ✅ F-035（root_api_key 强制） |
| F-023 | 「用户管理」新增用户（用户名 macro、角色 user），生成用户 API 密钥并保存，回填连接设置后数据访问打通 | ✅ 多租户机制 |
| F-024 | 工作台三栏：左侧上下文树（user 下放个性化记忆、resources 放 Agent 可引用外部资源）、中间浏览 viking:// 目录、右侧会话区（"终端"/"Agent"两种模式）；Agent 工具调用与左侧目录联动，可定位打开对应 viking:// 文件 | ✅ README Studio |

## E. 博文事实：VikingBot 跨会话记忆实测

| 编号 | 事实 | 核验 |
|------|------|------|
| F-025 | 输入"记住我的职业：Java开发工程师"，Agent 调用 openviking_memory_commit 把偏好写进记忆，回复给出记忆的 Memory URI | ⚠️ 工具名 F-039 |
| F-026 | 新会话问"我的职业是什么"，Agent 先调 openviking_search 检索再回答"你的职业是 Java 开发工程师"；信息不在会话历史里，来自 OpenViking 召回 | ⚠️ 工具名 F-039；机制 ✅ |
| F-027 | 终端模式执行 `/search 职业`，列出命中的资源、记忆、技能，每条带 .abstract.md、.overview.md、profile.md 文件名与 L0/L1/L2 层级、相似度 score | ✅ 文件名 F-037；/search 为 VikingBot 终端命令（博文单源） |
| F-028 | 上下文树可展开到 user/macro/peers/macro/memories/profile.md，预览为明文"职业：Java开发工程师"；记忆以明文文件落盘，看得见摸得着 | ✅ user 树 F-038 |

## F. 博文事实：外部 Agent 支持与总结

| 编号 | 事实 | 核验 |
|------|------|------|
| F-029 | 官方接入页列出 Claude Code、Codex、OpenClaw 等，加通用 MCP 方式（TRAE、Cursor 等）和 SDK（Python、LangChain 等） | ✅ F-040（口径细化：TRAE/Cursor 有专用 Hooks+MCP 集成；SDK 语言为 Python/Go/TypeScript，LangChain 属框架集成） |
| F-030 | 接入三步：先启动自部署 OpenViking Server，再跑一条安装脚本把 Claude Code 接进来，重启后可用 | ✅ F-041 |
| F-031 | 📌 作者观点：OpenViking"把上下文当工程对象对待"；部署很轻，一条 docker run 把服务、控制台、VikingBot 一起带起；召回了什么、存到哪，控制台一目了然 | 观点（与官方机制相容） |
| F-032 | 📌 作者建议：受够 Agent 换会话失忆、或想给 Coding Agent 补可观察可管理长期记忆，值得花半小时部署 | 观点 |

## G. 核验补充事实（官方源）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-033 | GitHub API 2026-09-09/10 快照：stargazers_count **36,276**、forks 2,772、watchers 105、open_issues 703；仓库创建于 **2026-01-05**；主语言 Python；许可证 AGPL-3.0；topics：agent-memory/agent-plugins/agentic-rag/context-database/dsh-plugin/self-evolving；官方描述 "Self-evolving Context Database for AI Agents. Unify Agent Memory, Knowledge RAG and Skills."；homepage https://openviking.ai/ | GitHub REST API |
| F-034 | 官方文档站 https://docs.openviking.ai；在线免安装 Studio https://openviking.ai/studio；README 基准节版本 **0.3.22**；pip 安装 `pip install openviking --upgrade`，要求 Python 3.10+，另需 embedding 模型与 VLM（云端或本地）；`openviking-server init/doctor` 向导写 `~/.openviking/ov.conf`；`pip install "openviking[bot]"` + `openviking-server --with-bot` 起 VikingBot，`ov chat` 对话 | README/官方文档 |
| F-035 | Docker 官方文档：镜像 ghcr.io/volcengine/openviking:latest；容器内 HTTP 服务绑 0.0.0.0:1933，Web Studio 同源 /studio，默认同时启动 vikingbot 网关；ov.conf/ovcli.conf/workspace 全部持久态位于容器内 /app/.openviking，单挂载即可；因绑 0.0.0.0 **必须在 ov.conf 设 root_api_key，否则拒绝启动**；`--without-bot` 或环境变量 OPENVIKING_WITH_BOT=0 可关 bot；无挂载时可用 OPENVIKING_CONF_CONTENT 传配置或 docker exec 跑 init；旧入口 1934（Caddy 反代）保留；另提供 docker-compose.yml 与 Helm chart | docs/guides/03-deployment |
| F-036 | 健康探针：`GET /health` 无鉴权，文档示例仅返回 `{"status":"ok"}`（liveness）；另有 `GET /ready`（readiness）检查 AGFS/VectorDB/APIKeyManager/Embedding/Ollama。博文所述 healthy:true/服务版本/auth_mode 字段**未见于现行官方文档示例**（可能为实测版本的扩展返回，⚠️ 口径差异，不影响"可用于验证服务存活"的操作结论） | docs/guides/03-deployment |
| F-037 | 三层加载：L0（Abstract）= .abstract.md 一句话摘要做快速相关性判断；L1（Overview）= .overview.md 核心信息与使用场景供规划；L2（Details）= 完整原始数据，按需读取。经语义处理的目录携带 L0/L1 摘要 | README |
| F-038 | viking:// 布局：resources/ 放项目文档、仓库、网页等；user/{user_id}/ 下分 memories/（偏好与经验，含 preferences/）、resources/（私有资源）、skills/、peers/（外部访问者，如 web-visitor-alice）。提交会话（commit）会归档对话并启动后台抽取，记忆策略控制保留内容，候选记忆与既有记忆比对后执行 create/merge/skip；启用 VikingBot 时 `ov compile` 可把素材组织成 wiki、知识图谱或报告 | README |
| F-039 | MCP 端点 `http://<server>:1933/mcp`，与 REST API 同进程同端口；鉴权用 X-Api-Key 或 Authorization: Bearer（绑 localhost 本地开发模式可免鉴权）。MCP 暴露 **15 个工具**：find、search、read、list、tree、remember、write、edit、add_resource、list_watches、cancel_watch、grep、glob、forget、health；find=不带会话上下文的快速语义检索，search=深检索且 mode="context" 组装注入级上下文（替代旧 recall 工具）。**博文工具名 openviking_memory_commit/openviking_search 不见于官方工具集**：官方对应"主动固化"为 remember、会话后台沉淀为 commit 机制、检索为 search/find（⚠️ 疑为 VikingBot 早期/界面化名称或作者转述，2026-09 文档口径以官方 15 工具为准） | docs MCP 指南/集成文档 |
| F-040 | 官方集成矩阵：Claude Code / Codex / Cursor / TRAE（含 TRAE CN、TraeCode CLI 2.0）均为 **Hooks + MCP**；OpenClaw 为 Context engine；Hermes built-in；OpenCode / DeerFlow / DSH 为 Plugin + MCP；pi 为 Native extension；Doubao Work 为 Connector；LangChain 为 Tools + store；SDK 提供 Python / Go / TypeScript 及 HTTP API。MCP 已验证平台：Claude Code、Trae、Cursor、ChatGPT/Codex、OpenCode、Manus、Claude Desktop（OAuth 2.1） | README 集成表/MCP 指南 |
| F-041 | Coding Agent 接入：统一安装脚本 `examples/memory-plugin-shared/install.sh --harness <claude-code\|codex\|cursor\|trae\|trae-cn\|trae-cli\|...>`，国内可用 TOS 镜像 ovrelease.tos-cn-beijing.volces.com（--dist tos）；前置 macOS/Linux + Node.js 18+；安装后需完全退出并重启客户端。Hooks 四事件：SessionStart 加载 profile 与项目记忆、UserPromptSubmit 召回注入、PreToolUse 把误访本地 viking:// 路径重定向到 MCP 工具、Stop 捕获并立即提交当轮用于记忆抽取 | TRAE/Cursor 集成文档 |
| F-042 | embedding 官方 provider 支持 openai/azure/volcengine/vikingdb/jina/ollama/voyage/minimax/cohere/gemini/dashscope/litellm/local；DashScope 原生 provider 示例即 text-embedding-v4、dimension 1024、input text；博文用 provider "openai" + /compatible-mode/v1 属官方文档同时给出的"OpenAI 兼容端点"合法接法。VLM 配置示例含豆包 doubao-seed-2-0-lite、GPT-5.4、Kimi、GLM-4.6V/GLM-5V-Turbo（图像理解需视觉模型）等；openviking-server init 单独引导配置 embedding 与 VLM | docs/guides/01-configuration |
| F-043 | 许可证分层：主项目 AGPLv3、crates/ov_cli 与 examples 为 Apache-2.0、third_party 随各自许可。商业形态：火山引擎托管 SaaS（个人版/企业版，含开源部署迁移工具，海外计划由 BytePlus 提供）；自管版 BYOC（自有云账号/VPC/离线环境，增加分布式部署与官方支持，需 license key）。桌面端 OpenViking Helper 0.0.19 beta（macOS arm64/x64、Windows x64），配置本地 Agent 集成、查看召回/捕获事件、同步记忆与技能。服务端支持多租户账号隔离与可选资源 ACL | README/LICENSE |
| F-044 | **厂商自述基准**（官方 README/benchmark 报告，复现脚本在仓库 ./benchmark；评测版本 0.3.22）：LoCoMo 长对话用户记忆准确率：OpenClaw 原生 24.20%→接 OpenViking 82.08%；Hermes 33.38%→82.86%；Claude Code 57.21%→80.32%；输入 token 降低 34.3%~91.0%，查询延迟降低 58.45%~66.10%。tau2-bench 任务成功率：Retail 70.94%→77.81%（+6.87pp），Airline 54.38%→66.25%（+11.87pp）。评测模型：VLM 用 Doubao 2.0 Pro，embedding 用 doubao-embedding-vision-251215。属厂商自测数据，引用需标注口径 | README/benchmark blog |
| F-045 | 研究背景（均为火山团队论文）：VikingMem（arXiv:2605.29640，VLDB 2026，事件驱动的长期记忆抽取/更新/合并，OpenViking 开源其子集）；目录感知向量检索（arXiv:2606.16903，ICDE 收录，TrieHI 在向量排序前解析目录范围，OpenViking 已集成）；VikingRAG（arXiv:2609.11390，已投稿，结构化文档 token 高效检索，复用检索轨迹） | README Research 段 |
| F-046 | 阿里云百炼侧核验：qwen3-vl-plus 为百炼在售 Qwen3 视觉模型（输入文/图/视频、输出文本，256K 上下文，现版本等同快照 qwen3-vl-plus-2025-12-19，2026-01-20 自动升级）；华北2（北京）原价输入 ¥1/百万 token、输出 ¥10/百万 token（≤32k 档，2026-09 时点）；百炼提供 dashscope.aliyuncs.com/compatible-mode/v1 OpenAI 兼容接口，text-embedding-v4 为 1024 维中文优化 embedding 模型 | help.aliyun.com |
| F-047 | ov CLI：`ov status`、`ov add-resource <url>`（异步任务，`ov task status <TASK_ID>` 轮询至 completed）、`ov ls viking://resources/`、`ov tree viking://resources/volcengine -L 2`、`ov find "..."`、`ov grep "openviking" --uri viking://resources/volcengine/OpenViking/docs/en`（tree/grep 示例取自官方 README quick start，导入后的实际 URI 以 add-resource 返回为准）；CLI 连接配置在 ~/.openviking/ovcli.conf（url + api_key，可用 OPENVIKING_CLI_CONFIG_FILE 覆盖）；Python SDK 示例 `ov.SyncHTTPClient(url, api_key).initialize()/find()/close()` | README/deployment |
| F-048 | 其他部署形态：systemd 服务单元（官方推荐生产方式）、docker compose up -d、Helm（examples/k8s-helm，helm install 时传 api_key）、多实例配置（temp_upload shared 模式、skip_process_lock 仅多实例共享 workspace 时开启、QueueFS/审计 SQLite 按实例独立路径）；构建自定义镜像可 `docker build --build-arg OPENVIKING_VERSION=0.3.12` | docs/guides/03-deployment |

## 核验总览

- 事实总数：48（博文 32：含 2 条作者观点 + 核验补充 16）
- P0 关键声明：10 项 —— ✅ 通过 10（其中 3 项含口径细化）、⚠️ 2（/health 响应字段、MCP 工具名）、❌ 0
- 无厂商自宣成效数字污染：博文本身无提效倍数；官方基准 F-044 已标"厂商自述"
