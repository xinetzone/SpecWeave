---
version: "1.0"
---

# DeepSeek Harness Wiki 教程 Tasks

## 任务概览

| 任务ID | 任务名称 | 依赖 | 预估文件 | 验收标准 |
|--------|---------|------|---------|---------|
| T1 | 创建wiki目录与总览导航 | 无 | 00-overview.md | 导航表完整，学习路径清晰，核心概念速览准确 |
| T2 | 项目介绍与背景 | T1 | 01-introduction-background.md | 定位准确，时间线完整，对比Claude Code/Codex差异清晰 |
| T3 | 环境准备与安装 | T2 | 02-installation-setup.md | Node版本要求明确，启动命令可复现，配置目录说明准确 |
| T4 | 快速上手：第一个任务 | T3 | 03-quickstart-first-task.md | Web UI步骤清晰，第一个任务示例完整可执行 |
| T5 | 四种运行模式详解 | T4 | 04-four-modes.md | 四种模式对比表完整，各模式适用场景说明清晰 |
| T6 | 核心架构：一切皆插件 | T5 | 05-architecture-everything-plugin.md | Cordis框架解释清晰，无特权内核原则阐述准确，Profile/Bundle机制说明完整 |
| T7 | Agent循环与事件模型 | T6 | 06-agent-loop-events.md | Turn/Step定义准确，三类事件分类清晰，瀑布型事件机制说明正确 |
| T8 | 会话日志与可观测性 | T7 | 07-session-log-observability.md | append-only日志原则阐述清晰，Trajectory使用说明完整，分叉/回放机制说明准确 |
| T9 | 模型配置与多模型支持 | T4 | 08-model-configuration.md | 默认模型参数准确，多Provider配置步骤完整，自定义Provider说明清晰 |
| T10 | 工具系统与Capability Seam | T8 | 09-tools-capability-seam.md | 内置工具清单完整，Capability Seam三角色解释清晰，示例恰当 |
| T11 | 插件开发入门 | T10 | 10-plugin-development.md | 插件结构说明清晰，包含可运行的简单插件示例 |
| T12 | 与Claude Code/Codex/MCP生态互操作 | T11 | 11-ecosystem-interop.md | hooks/MCP/AGENTS.md兼容说明完整，委托机制说明准确 |
| T13 | 无头模式与SDK使用 | T4 | 12-headless-sdk.md | headless命令示例正确，Python SDK使用说明完整 |
| T14 | 常见问题与故障排查 | T3, T9, T13 | 13-faq-troubleshooting.md | 不少于10个常见问题，每个问题有明确解决方案 |
| T15 | 适用场景与风险提示 | T2, T14 | 14-use-cases-limitations.md | 适用/不适用场景表完整，风险提示清晰醒目 |
| T16 | 生态与资源链接 | T1-T15 | 15-ecosystem-resources.md | 资源链接完整且可访问，分类清晰 |
| T17 | 更新ai目录README导航 | T16 | docs/knowledge/ai/README.md | 追加deepseek-harness条目，导航链接正确 |

## 任务详述

### T1: 创建wiki目录与总览导航

**文件**: `docs/knowledge/ai/deepseek-harness/00-overview.md`

**内容要求**:
- YAML frontmatter（id/title/source/date/tags/maturity）
- 教程简介：本教程是什么、覆盖范围、基于哪些来源
- 目标读者：Agent框架研究者/插件开发者/需要可控Harness的团队/模型评测人员等
- 16章导航表（章节/文件/内容摘要/建议学习顺序）
- 学习路径建议：快速上手路径（T1-T4）→ 使用者路径（+T5,T8,T9,T12-T15）→ 架构理解路径（+T6,T7,T10）→ 插件开发路径（+T11）
- 核心概念速览：Cordis/Plugin/Profile/Bundle/Turn/Step/Session Log/Capability Seam等术语快速定义
- 版本说明：基于v0.1开发者预览版（0.1.0-rc.6），数据截止2026-08-15

---

### T2: 项目介绍与背景

**文件**: `docs/knowledge/ai/deepseek-harness/01-introduction-background.md`

**内容要求**:
- 核心公式：Agent = Model + Harness（模型是灵魂，Harness是手脚）
- Harness定义：工作区/工具/权限/会话记忆/驱动循环
- 发布时间线：2026-08-13晚发布，12小时star破5万，两天超10万
- 为什么Harness重要：同模型不同Harness完成率差30%（Composio测试数据）
- 与Claude Code/Codex的本质区别对比表（形态/界面/扩展/模型/源码/成熟度）
- "Agent界的Android"战略解读：开源vs闭源、框架vs成品、生态vs产品
- 开源协议：MIT，商业使用自由度
- 同期V4 Pro发布与API涨价背景（战略组合拳：开源抢生态+涨价造血）
- 上一章/下一章导航链接

---

### T3: 环境准备与安装

**文件**: `docs/knowledge/ai/deepseek-harness/02-installation-setup.md`

**内容要求**:
- 前置条件：Node.js版本要求（^22.19 || >=24，奇数版本如23不支持），版本检查命令`node -v`
- Node.js安装：各平台安装方法（macOS Homebrew/Windows/Linux）
- DeepSeek API Key准备：platform.deepseek.com申请步骤，余额提醒
- 一键启动：在项目目录执行`npx @deepseek-ai/dsh web`，访问http://127.0.0.1:3080
- 源码构建步骤：git clone → pnpm install → pnpm run build → pnpm dsh web
- 配置目录结构：~/.dsh/ 下profiles/.credentials.yaml/settings.yaml/cordis.patch.yml说明
- 端口说明：默认3080，自定义端口`--port 8080`
- 本地服务限制：CLI拒绝--host 0.0.0.0，仅设计为本地使用
- Windows兼容性说明：Web UI可运行但PTY持久终端能力受限，官方自带运行时仅发Linux/macOS
- 常见安装问题预检
- 上一章/下一章导航链接

---

### T4: 快速上手：第一个任务

**文件**: `docs/knowledge/ai/deepseek-harness/03-quickstart-first-task.md`

**内容要求**:
- Web UI界面概览：会话列表/输入区/Trajectory按钮/统计面板/Settings
- 第一步：选择工作区（Choose workspace），未选时输入框灰色不可用
- 第二步：配置模型（Settings → Models），填入DeepSeek API Key，保存立即生效
- API Key安全：真实密钥存~/.dsh/.credentials.yaml，设置文件只保留引用，页面显示脱敏
- 默认模型选择：deepseek-v4-pro（旗舰Agent优化）vs deepseek-v4-flash（快速省成本）
- 第一个任务示例："总结一下这个仓库，指出它的主要模块"
- 权限审批：危险操作弹窗确认机制
- 实时统计面板解读：步数/模型耗时/输入输出token/缓存命中率/成本估算
- Trajectory按钮入口提示（详见第7章）
- 上一章/下一章导航链接

---

### T5: 四种运行模式详解

**文件**: `docs/knowledge/ai/deepseek-harness/04-four-modes.md`

**内容要求**:
- 模式总览对比表（模式/能力集合/适用场景/启动方式）
- **Standard模式**：完整编程Agent能力清单（文件编辑/shell/文件网页搜索/skills/计划/目标/子Agent/工作流），默认日常使用
- **Code模式（PTC-程序化工具调用）**：模型写TypeScript编排多步操作，减少轮次往返，适用多步操作密集场景
- **Minimal模式**：仅保留持久bash + str_replace_editor两个工具，适用模型基准评测需要极简可控环境
- **Creator模式**：Standard全部能力 + 运行时自省 + 内存中试插件 + preset编写指导，适用定制Agent形态
- 模式切换方法：Web UI中选择或命令行--profile参数
- 上一章/下一章导航链接

---

### T6: 核心架构：一切皆插件

**文件**: `docs/knowledge/ai/deepseek-harness/05-architecture-everything-plugin.md`

**内容要求**:
- "一切皆插件"设计哲学深度解读
- Cordis元框架：源自论文《A Programming Paradigm for Spatiotemporal Composability》，核心思想
- 无特权内核原则：模型适配器/工具注册表/会话日志/Agent循环本身都是插件，不需要修改源码扩展
- 可逆效应（Reversible Effects）：插件卸载时注册的一切自动撤销
- Bundle（能力捆绑包）：分发格式，打包Cordis配置行+代码，支持上层继续打补丁
- Profile（配置档案）：~/.dsh/profiles/下的命名组合清单，内置web/headless模板
- 分层叠加机制：profile内bundle顺序加载 → profile级补丁 → 用户主目录补丁 → 命令行--patch补丁
- 补丁机制：按id定位配置行，整体替换或插入新行
- 查看实际插件树：`dsh --profile web --dump-config`，任意行可被替换
- 架构价值：换模型/换工具/换沙箱从"改代码"变成"改配置"
- 上一章/下一章导航链接

---

### T7: Agent循环与事件模型

**文件**: `docs/knowledge/ai/deepseek-harness/06-agent-loop-events.md`

**内容要求**:
- 为什么Agent循环设计是Harness核心
- Step定义：一次模型请求加上它调用的工具
- Turn定义：零到多个Step组成，从认领输入开始到无"欠账"结束
- 典型回合流程图解：认领输入 → 组装提示词与工具schema → agent/pre-step → 追加日志 → 模型请求 → 流式接收 → 调用工具 → 决定是否下一步
- 三类事件系统：
  - 会话事件（session/event）：写入日志持久存在，重启后还在的事实
  - Agent事件（agent/*）：携带活的Agent对象（收件箱/步骤/状态/请求/校验/续跑）
  - 能力事件（Capability events）：文件系统/工具/遥测等能力接口的策略与适配器
- 瀑布型事件（Waterfall）：agent/pre-step/agent/request/llm/stream/tools/*，必须显式调用next()传递控制权，可拦截/重写/拒绝
- 串行事件：agent/turn-stopping无next()，专门用于终止回合
- Loop本身也是插件（core/agent-loop包），可完整替换调度逻辑
- 上一章/下一章导航链接

---

### T8: 会话日志与可观测性

**文件**: `docs/knowledge/ai/deepseek-harness/07-session-log-observability.md`

**内容要求**:
- 硬性规则："模型看到的一切，都必须能从日志里还原出来"
- SessionEvent流：append-only仅追加设计
- deriveMessages()函数：从事件流投射模型实际看到的历史
- 保真度：保留原始assistant/chunk流式事件支持回放与UI还原
- Trajectory（轨迹）视图使用：
  - 如何打开：会话界面Trajectory按钮
  - 能看到什么：系统提示词/思维链/工具调用与结果/子Agent调度/每次上下文注入，按来源摊开展示
  - 能做什么：从任意节点恢复/分叉/检视/回放
- 分叉（fork）机制：基于事件流在任意点创建新会话分支
- 恢复（resume）机制：断点续做
- 完整回放：复现Agent完整决策路径
- 遥测与持久化：同一条事件流派生，无需额外状态快照
- 调试价值：长任务debug、决策路径复盘、失败案例分析
- Hacker News好评：开发者称为killer feature，对比美国厂商API隐藏数据的做法
- 上一章/下一章导航链接

---

### T9: 模型配置与多模型支持

**文件**: `docs/knowledge/ai/deepseek-harness/08-model-configuration.md`

**内容要求**:
- 默认DeepSeek模型配置：
  - deepseek-v4-pro：旗舰，面向Agent任务优化
  - deepseek-v4-flash：更快更省，日常任务
  - 默认参数：100万上下文窗口、单次输出上限256k、推理档位high
- 三档思考强度：low（简单任务）/high（日常Agent）/max（高度复杂）
- API Key配置：Settings → Models页面操作，脱敏显示，密钥存.credentials.yaml
- 内置多Provider支持：Add provider内置目录包含Anthropic/OpenAI/Bedrock/Azure/Vertex等
- 自定义Provider配置：
  - Add a custom provider
  - 填写：小写Provider ID、Base URL、协议类型、API Key、至少一个模型
  - Fetch available models自动拉取模型列表
- 视觉模型注意事项：手填模型默认纯文本，图片请求前被拒绝；需在settings.yaml补`input: [text, image]`
- V4 Pro与Harness协同：公开基准Code Agent任务使用Harness Minimal模式测试
- OpenAI Responses API格式原生支持，Codex适配一键配置
- 上一章/下一章导航链接

---

### T10: 工具系统与Capability Seam

**文件**: `docs/knowledge/ai/deepseek-harness/09-tools-capability-seam.md`

**内容要求**:
- Standard模式内置工具清单：
  - 文件读写编辑
  - Shell命令执行（bash/PTY）
  - 文件与网页搜索
  - Skills技能系统
  - 计划（planning）与目标（goals）管理
  - 子Agent委派（subagent seam）
  - 工作流编排
- Capability Seam抽象设计：为什么需要Seam
- 三角色定义：
  - Service Definition：声明接口
  - Service Provider：实现接口
  - Consumer：使用接口（通常是面向模型的工具）
- "一次替换，处处生效"机制：
  - 示例1：文件系统+子进程provider共享同一执行世界，指向远程沙箱则Bash/PTY/LSP一起迁移，无需每个工具适配分支
  - 示例2：子Agent provider切换（拉起新子Agent vs 委托给其他产品处理），同一接口
- ctx.goals扩展点：同一会话内目标管理能力
- subagent seam扩展点：多Agent协作场景
- 上一章/下一章导航链接

---

### T11: 插件开发入门

**文件**: `docs/knowledge/ai/deepseek-harness/10-plugin-development.md`

**内容要求**:
- 插件开发前提：理解Cordis基本概念（第6章）
- 插件基本结构概述（基于官方文档和社区示例）
- 如何注册插件到插件树
- 事件监听示例：监听agent/pre-step修改提示词
- 自定义工具插件示例：注册一个新工具给模型调用
- 可逆效应实现：插件卸载时清理注册内容
- UI主题插件示例：修改Web UI样式
- Creator模式运行时试验：内存中试插件无需重启
- 社区插件生态：dsh-plugin GitHub标签，发布当天300+插件示例（XP皮肤/表情包/DSH-OpenPencil设计工具等）
- 官方PR政策：暂不接受外部PR到主仓库，建议开发独立插件
- 插件开发资源链接
- 上一章/下一章导航链接

---

### T12: 与Claude Code/Codex/MCP生态互操作

**文件**: `docs/knowledge/ai/deepseek-harness/11-ecosystem-interop.md`

**内容要求**:
- 生态兼容策略：降低迁移成本，避免冷启动
- Claude Code hooks桥接：内置桥接器，直接复用现成的hooks.json配置
- Codex兼容：DeepSeek API原生支持OpenAI Responses API格式，一键配置脚本
- MCP（Model Context Protocol）支持：作为客户端支持MCP服务器
- AGENTS.md / CLAUDE.md读取：自动识别并读取项目中的这些文件作为上下文
- 任务委托机制：可将任务委托给本机已安装的Claude Code/Codex处理（默认关闭，需配置开启）
- 与Claude Code/Codex共存策略：不是替代而是互补，可组合使用
- 迁移路径：从Claude Code/Codex迁移到dsh的注意事项
- 上一章/下一章导航链接

---

### T13: 无头模式与SDK使用

**文件**: `docs/knowledge/ai/deepseek-harness/12-headless-sdk.md`

**内容要求**:
- 无头（Headless）模式使用场景：自动化脚本、CI/CD集成、批量任务
- Headless模式启动：`npx @deepseek-ai/dsh --profile headless "把失败的测试修好"`
- Headless模式特点：一次性执行任务、打印结果、退出，无Web UI
- Python SDK：
  - 安装：`pip install deepseek-harness-sdk`
  - 特点：自带Node运行时，目标机器无需单独安装Node
  - 使用示例：在Python代码中调用dsh执行任务
- JSON-RPC SDK：适合其他语言集成
- ACP（Agent Communication Protocol）服务端：便于嵌入自己的程序
- 嵌入应用场景：内部工具平台、自动化工作流、IDE插件
- 与Web模式配置共享：使用同一套~/.dsh配置
- 上一章/下一章导航链接

---

### T14: 常见问题与故障排查

**文件**: `docs/knowledge/ai/deepseek-harness/13-faq-troubleshooting.md`

**内容要求**:
- 至少包含以下10个常见问题，每个有明确症状+原因+解决方案：
  1. Node版本错误（ERR_UNSUPPORTED_ENGINE，要求^22.19 || >=24）
  2. 3080端口被占用（EADDRINUSE，用--port换端口）
  3. MISSING_CREDENTIAL错误（没配置API Key，去Settings→Models填入）
  4. UNKNOWN_MODEL错误（选了未配置的模型，补全模型ID或切换模型）
  5. 输入框是灰色无法输入（没选工作区，点Choose workspace；或模型下拉显示Select model需重新选择）
  6. 想让局域网同事访问（CLI拒绝--host 0.0.0.0，设计为本地服务，不支持远程共享）
  7. Windows上PTY/持久终端不可用（Windows仅支持Web UI，PTY依赖POSIX环境，建议WSL2或Linux/macOS）
  8. 图片/视觉输入不工作（自定义模型默认纯文本，需在settings.yaml配置input: [text, image]）
  9. 升级后旧会话无法读取（预览版不承诺会话格式兼容，这是预期行为）
  10. Token消耗看起来比其他Harness高（v0.1预览版优化不足，等待后续版本优化；可切换Minimal模式评测基线）
- 配置文件位置速查：~/.dsh/各文件用途
- 获取帮助渠道：GitHub Discussions、社区插件标签
- 上一章/下一章导航链接

---

### T15: 适用场景与风险提示

**文件**: `docs/knowledge/ai/deepseek-harness/14-use-cases-limitations.md`

**内容要求**:
- 适用场景决策表：

| 你的情况 | 建议 | 理由 |
|---------|------|------|
| 想用DeepSeek官方出品的编程Agent | 直接用dsh | 默认DeepSeek优先，官方出品 |
| 想自己掌控Agent运行时，不用封闭产品 | 首选dsh | 核心设计目标就是可扩展 |
| 需要干净稳定工具面做模型评测 | 用Minimal模式 | 仅两个工具，极简可控环境 |
| 给团队搭内部Agent平台 | 可行 | 用插件和profile组合需要的形态 |
| 研究Agent架构和Harness工程 | 强烈推荐 | 架构清晰，源码MIT开放 |
| 开发Agent插件生态 | 推荐 | 插件机制完善，生态正在爆发 |

- 不适用场景决策表：

| 你的情况 | 建议 | 理由 |
|---------|------|------|
| 需要立即上生产、要求API稳定 | 暂缓 | 开发者预览版，官方声明会有破坏兼容变更 |
| 只想让Claude Code用上更便宜模型 | 不必用dsh | 用CC Switch等方案更简单 |
| 非技术终端用户开箱即用 | 不适合 | 界面对非开发者不友好，需要技术背景 |
| 需要团队协作SaaS托管服务 | 不支持 | 设计为本地服务，无多用户/远程访问 |
| 生产环境核心流程依赖 | 不推荐 | 会话格式不兼容升级，稳定性未经验证 |

- ⚠️ **风险提示**（醒目格式）：
  - v0.1是开发者预览版，核心插件与基础接口会快速演化
  - 不承诺会话格式向后兼容，升级可能导致旧会话无法读取
  - 目前只建议用于：评估、内部试验、Harness研究、插件开发
  - 主仓库暂不接受外部PR
  - 本地优先设计，无官方远程托管方案

- Windows平台特殊限制：PTY能力受限，建议优先使用WSL2/Linux/macOS获得完整体验

- 版本跟踪建议：关注GitHub Releases，升级前查看CHANGELOG注意破坏性变更

- 上一章/下一章导航链接

---

### T16: 生态与资源链接

**文件**: `docs/knowledge/ai/deepseek-harness/15-ecosystem-resources.md`

**内容要求**:
- 官方资源分类：
  - 源码仓库：https://github.com/deepseek-ai/deepseek-harness
  - 官方产品页：https://deepseek.com/harness
  - DeepSeek API平台：https://platform.deepseek.com
  - API文档：https://platform.deepseek.com/api-docs
  - Cordis元框架：https://github.com/cordiverse/cordis
  - Cordis论文：https://github.com/cordiverse/paper/blob/main/paper.pdf
- 社区与第三方资源：
  - deepseekagent.io指南：https://deepseekagent.io/zh/guides/deepseek-harness
  - GitHub Discussions：问题反馈与讨论
  - dsh-plugin标签：社区插件发现
- 推荐深度阅读：
  - Tony Bai《DeepSeek Harness终于来了：开源，一切皆插件》（架构深度分析）
  - 极客公园《DeepSeek开源毛坯零件，会催生哪些意想不到的Agent玩法？》（产品评测）
  - 新浪财经/华夏时报商业分析（战略解读）
- 同类Harness框架参考对比：
  - Claude Code（Anthropic，闭源成品）
  - Codex CLI（OpenAI，闭源成品）
  - 其他开源Harness（如OpenClaw等）
- 生态动态新闻：
  - 腾讯QQ Bot官宣支持接入DeepSeek Harness（单聊/群聊）
  - DeepSeek V4 Pro上线国家超算互联网
- 本教程来源说明与数据截止日期（2026-08-15）
- 上一章导航链接

---

### T17: 更新ai目录README导航

**文件**: `docs/knowledge/ai/README.md`

**内容要求**:
- 在AI主题wiki目录的README中追加deepseek-harness子目录条目
- 条目包含：目录名、简介、教程状态
- 保持现有README格式风格一致
- 链接路径正确使用相对路径

## 执行顺序建议

1. 按T1→T2→...→T16顺序依次创建各章节文档，保证前置引用准确
2. T17在所有章节完成后最后执行
3. 每个文档完成后立即检查内部导航链接（上一章/下一章）正确性
4. 所有文档完成后运行链接检查验证
