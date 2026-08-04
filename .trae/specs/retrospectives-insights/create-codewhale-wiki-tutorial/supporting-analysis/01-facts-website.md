# CodeWhale 官网事实清单

> 采集日期：2026-08-04
> 来源页面：codewhale.net 官网（首页、安装、文档、产品名词、新手指引、提供商与模型、Fleet、运行时共 8 个页面）

## 产品定位与基本信息

- F-WEB-001: 官网域名为 codewhale.net，中文页面路径为 /zh
- F-WEB-002: 项目采用 MIT 开源协议
- F-WEB-003: 官网标语为"潜入深海，你不必亲自下潜。"
- F-WEB-004: 产品定位描述为"把大模型的杠杆交给普通人——在你的终端里读取仓库、修改文件、运行检查、留下收据。"
- F-WEB-005: 当前发布版本为 v0.9.3
- F-WEB-006: 当前源码候选版为 v0.9.4
- F-WEB-007: 项目仓库位于 GitHub 的 Hmbown/CodeWhale
- F-WEB-008: 官网部署在 Cloudflare 上，网站源码位于仓库的 web/ 目录下
- F-WEB-009: 官网同时提供 codewhale.net 和 www.codewhale.net 两个域名
- F-WEB-010: 所有正式发布和 SHA-256 校验文件仅通过 GitHub Releases 分发

## 安装与部署

- F-WEB-011: 安装命令为 `npm install -g codewhale`，npm wrapper 从 GitHub Releases 下载经 SHA-256 校验的二进制
- F-WEB-012: npm 安装需要 Node 18 及以上版本
- F-WEB-013: 安装后提供三个命令：codewhale、codew（短别名）和 codewhale-tui
- F-WEB-014: 提供一键安装脚本：`curl -fsSL https://codewhale.net/install.sh | sh`
- F-WEB-015: macOS/Linux 安装脚本默认安装到 `~/.local/bin`
- F-WEB-016: 支持 Cargo 安装，需要 Rust 1.88+，两个 crate 包分别为 codewhale-cli 和 codewhale-tui
- F-WEB-017: 支持 Docker 安装，发布镜像位于 GHCR（ghcr.io/hmbown/codewhale）
- F-WEB-018: 提供预编译二进制，支持 macOS (Apple Silicon/Intel)、Linux (x64/arm64)、Windows (x64/arm64) 共 6 个平台
- F-WEB-019: 支持 Homebrew 安装，旧版 tap 为 `Hmbown/deepseek-tui`（formula 重命名为 codewhale 期间保留兼容）
- F-WEB-020: 面向中国大陆用户提供 CNB 镜像和清华大学 TUNA 镜像加速
- F-WEB-021: npm 安装时设置 `CODEWHALE_USE_CNB_MIRROR=1` 环境变量可从 CNB 镜像下载二进制
- F-WEB-022: 支持从源码编译，执行 `cargo build --release --locked` 后分别安装 cli 和 tui 两个 crate

## 核心功能与模式

- F-WEB-023: 三种运行模式：Plan（始终只读）、Act（默认模式，多步骤工具调用，shell 有审批提示）、Operate（多任务调度，自动派发后台 worker）
- F-WEB-024: 三种权限姿态：Ask（默认，有未决选择时询问）、Auto-Review（完全自主，不弹出提问）、Full Access（普通工具调用不显示审批提示，安全拦截仍生效）
- F-WEB-025: 模式和权限姿态正交，Tab 键循环切换模式，Shift+Tab 循环切换权限姿态
- F-WEB-026: 核心工作流程为四步：检查→执行→验证→报告
- F-WEB-027: 产品定位为"终端原生的水下壳"，强调模型与提供商中立、本地优先
- F-WEB-028: 首次运行时无需任何 API 密钥即可启动，经历宪法优先设置（语言、提供商就绪情况、运行姿态、用户宪法）后进入完整界面
- F-WEB-029: 内置 36 条提供商路由

## 运行时与界面

- F-WEB-030: 提供五种运行时界面：TUI（交互式终端）、codewhale exec（脚本与 CI）、Web 客户端（仅限本机回环 127.0.0.1）、运行时 API + MCP、Fleet（持久化多智能体）
- F-WEB-031: Runtime API 默认监听 127.0.0.1:7878，提供 HTTP + Server-Sent Events 接口
- F-WEB-032: 所有 Runtime API 路由（/v1/*）需要 Bearer Token 认证，通过 CODEWHALE_RUNTIME_TOKEN 或 config.toml 中的 auth_token 配置
- F-WEB-033: 支持 ACP (Agent Client Protocol)，面向 Zed 等编辑器客户端的 JSON-RPC stdio 适配器
- F-WEB-034: 支持 MCP (Model Context Protocol)，通过 stdio 或 HTTP/SSE 消费和暴露工具
- F-WEB-035: 提供 VS Code 扩展（Phase 0），可在终端中打开 Codewhale、启动并检查 Runtime API、显示只读线程摘要和还原点
- F-WEB-036: 提供官方 Telegram 桥接机器人，可在 Telegram 客户端中与无头 Codewhale 会话对话
- F-WEB-037: 提供官方飞书/Lark 桥接机器人，支持审批卡片、会话关联和审计日志
- F-WEB-038: 提供实验性微信桥接，可在微信中接收 Agent 完成通知和审批
- F-WEB-039: 项目不依赖 Codewhale 账户或托管中继，本地运行时无需联网账户

## 配置文件与数据

- F-WEB-040: 配置文件默认位于 `~/.codewhale/`（可通过 CODEWHALE_HOME 环境变量自定义）
- F-WEB-041: 配置目录包含 config.toml（API 密钥、模型、钩子、配置集）、mcp.json（MCP 服务器定义）、skills/（用户技能）、sessions/（检查点与离线队列）、tasks/（后台任务存储）、audit.log（凭证/审批/提权事件日志）
- F-WEB-042: 支持项目级配置目录 `./.codewhale/`，每个仓库可有独立的 MCP 服务器、钩子、技能和配置覆盖
- F-WEB-043: 旧版 `~/.deepseek` 和 `./.deepseek` 路径仍作为兼容回退读取
- F-WEB-044: 沙箱支持：macOS 使用 Seatbelt，Linux 使用 bubblewrap（需显式启用）

## 提供商与模型

- F-WEB-045: 内置 36 个提供商路由，提供商和模型分别独立选择
- F-WEB-046: 内置提供商包括 DeepSeek、Anthropic、OpenAI、OpenRouter、NVIDIA NIM、vLLM、Ollama、SGLang、Hugging Face、Together AI、xAI、Moonshot/Kimi、SiliconFlow、Fireworks AI、Novita AI、Baidu Qianfan、MiniMax、StepFun、DeepInfra、Volcengine Ark、Meta Model API 等
- F-WEB-047: 本地运行时（vLLM、SGLang、Ollama）可以直连 localhost，通常不需要 API 密钥
- F-WEB-048: 每条路由的身份由四个字段组成：Provider（推理提供方）、Model（具体模型）、Requested reasoning（请求思考档位，取值 inherit/off/low/medium/high/max/auto）、Effective reasoning（实际采用的思考档位）
- F-WEB-049: 官网不发布基准排行榜，任何数字发布必须同时给出确切的提供商、模型、请求与实际思考档位和测量工具链
- F-WEB-050: 模型名称不会隐式改变提供商，不发生静默切换
- F-WEB-051: 无法确认的值（如实际思考档位、token 用量、成本、进度）保持"暂不可用"状态，不显示为零或成功

## Fleet 与 Workflow

- F-WEB-052: Fleet 是面向持久多 worker 运行的本地优先控制平面，一个 Fleet worker 就是一次 codewhale exec 无头运行
- F-WEB-053: Fleet 状态存放在工作区 `.codewhale/fleet.jsonl` 台账中，worker 日志在 `.codewhale/fleet/` 下
- F-WEB-054: Fleet 命令包括 init、run、status、inspect、logs、interrupt、resume、stop
- F-WEB-055: `/fleet setup` 命令启动渐进式向导，编写可复用的 agent 团队档案（角色、模型、思考档位、权限、工具、范围、审查策略）
- F-WEB-056: Agent 档案可存储在项目级（.codewhale/agents/<role>.toml）或个人级（$CODEWHALE_HOME/agents/<role>.toml），同名项目档案优先
- F-WEB-057: Workflow 脚本以编译专用的声明式 JS 子集编写，降低到类型化的 WorkflowSpec 后由 Rust 校验与执行
- F-WEB-058: Workflow 默认校验边界：每次运行最多 100 个 worker Agent、最多 5 层递归 Fleet 环、循环必须声明 max_iterations、动态 expand 节点必须声明 max_children 和模板
- F-WEB-059: Workflow JS 沙箱内单 run 最多 16 个并发存活 Agent、整个 VM 生命周期最多 1,000 次启动

## 产品名词体系

- F-WEB-060: Fleet 定义为"谁来做工作：配置好的 worker、角色、模型、主机和信任边界"
- F-WEB-061: Workflow 定义为"工作按什么顺序进行：阶段、门禁、预算、回放和汇总"
- F-WEB-062: Lane 定义为"一个正在运行的 Workflow 实例及其实时进度"
- F-WEB-063: Runtime 定义为"Lane 在哪里、如何执行：本地或远程进程、提供商路由、沙箱和 API 边界"
- F-WEB-064: Consultant 是面向用户的只读 Fleet 咨询角色，"oracle"与"advisor"作为兼容别名保留
- F-WEB-065: Routing source 字段说明为何选择某条已配置路由，缺失的来源保持"暂不可用"

## 文档与社区

- F-WEB-066: 文档站点包含入门（安装、使用指南、配置）、核心概念（产品名词、嵌套宪法、模式、工具、工作面板、子 Agent、沙箱与审批）、参考（提供商与模型）、扩展（MCP、钩子、运行时 API、浏览器客户端）、运维与社区（Fleet/Workflow、排障、贡献）五大板块
- F-WEB-067: 每篇文档页面均链接到 GitHub 仓库中的对应源文档
- F-WEB-068: 文档索引由仓库中的 docs-map.ts 注册表维护
- F-WEB-069: 新手指引页面中标注了真实会话媒体位"当前处于待录制状态"，在 v0.9.2 候选版 dogfood 录制完成前不展示任何占位或摆拍影像
- F-WEB-070: 提供商注册表由仓库生成并随发布更新，如需新增提供商可提交 issue 或 pull request