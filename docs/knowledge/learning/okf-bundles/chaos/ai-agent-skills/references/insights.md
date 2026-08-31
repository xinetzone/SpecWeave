---
type: Insights
title: "ai-agent-skills 架构洞察"
---

# ai-agent-skills 架构洞察

> I阶段分析。基于 R 阶段 292 条事实（agency-agents 63 + awesun-mcp 32 + awesun-skill 29 + awesun-ui-locator 30 + jira-skill 57 + retro-skill 81）。
> 分析日期：2026-08-23

---

## 洞察一：SKILL.md 渐进式披露——三层知识装载的开放标准

**陈述**：Agent Skills 开放标准（agentskills.io）以 `SKILL.md` 为核心入口，采用三层渐进式披露（progressive disclosure）模式组织知识：第一层是 SKILL.md 的 YAML frontmatter（name/description/version/allowed-tools 等元数据），AI 仅在匹配意图时才加载全文；第二层是 SKILL.md 正文的工作流程、工具清单和参数说明；第三层是 `references/` 子目录的深度参考文档和 `scripts/` 子目录的可执行脚本。这种分层使得技能在未激活时仅消耗极少 Token（frontmatter 的 description 字段），激活后按需展开完整知识。awesun-ui-locator 是典型范例：SKILL.md 包含 5 步工作流和坐标公式，`scripts/coordinate_utils.py` 提供可执行计算，`references/ui_patterns.md` 提供 UI 元素视觉特征对照表。jira-communication 更进一步，References 表引用了 16 个参考文档，scripts 按 core/workflow/utility 三层组织 21 个脚本。

**证据**：
- F-006~F-008（awesun-skill）：SKILL.md frontmatter 含 name/description/version，正文按 Device/Control/Desktop 三类列出 22 个工具
- F-028~F-030（awesun-ui-locator）：三层结构明确——SKILL.md 主入口、scripts/ 可执行函数、references/ 扩展知识
- F-012~F-022（jira-skill）：jira-communication 的 SKILL.md 声明 allowed-tools、脚本意图映射、References 目录引用 16 个文档
- F-024~F-029（jira-skill）：jira-syntax 的 SKILL.md 无 allowed-tools（纯知识技能），含语法参考表、模板、验证清单
- F-005~F-010（retro-skill）：retro 的 SKILL.md frontmatter 含完整字段，References 表引用 8 个参考文档

**反常识**：传统 AI 插件/扩展往往将所有能力描述和系统提示词一次性注入上下文，导致 Token 浪费。Skills 标准反其道而行：description 是"广告文案"，正文是"操作手册"，references 是"百科全书"——AI 像人类专家一样，先看标题判断是否相关，再翻阅手册，最后查阅百科。这种设计将 Token 消耗与任务相关性挂钩，而非与安装数量挂钩。

**行动**：
- 编写 SKILL.md 时，description 必须包含触发关键词和使用场景，这是 AI 是否加载技能的唯一判据。
- 重型知识放入 references/ 而非 SKILL.md 正文，保持主入口精简。
- 可执行逻辑放入 scripts/，SKILL.md 只描述何时调用、如何传参，不重复脚本内部实现。

---

## 洞察二：agency-agents 的部门化人格体系——200+ 专家的组织架构

**陈述**：agency-agents（The Agency）不是简单的提示词集合，而是一个模拟专业服务公司的部门化人格体系。它以 `divisions.json` 为部门集合的唯一真相来源，定义了 17 个部门（academic、design、engineering、finance、game-development、gis、healthcare、marketing、paid-media、product、project-management、sales、security、spatial-computing、specialized、support、testing），每个部门映射到显示标签、Lucide 图标名和品牌色。部门目录下存放 200+ 个 Agent 人格文件，每个文件使用 YAML frontmatter（必需 name/description/color）和结构化正文（Identity & Memory、Core Mission、Critical Rules、Technical Deliverables、Workflow Process 等 9 个章节）。`tools.json` 定义 16 个目标工具的安装契约（claude-code、cursor、codex、gemini-cli 等），支持三种安装类型：per-agent（每代理一个文件）、roster（合并为一个文件）、plugin（构建产物）。CI 通过 check-divisions.sh 验证 5 个位置的一致性（磁盘目录、divisions.json、convert.sh、lint-agents.sh、lint-agents.yml），确保部门集合不漂移。

**证据**：
- F-005~F-010：divisions.json 定义 17 部门，含 label/icon/color；NON_DIVISION_DIRS 排除 integrations/strategy/examples/scripts
- F-011~F-020：tools.json 定义 16 工具，三种 installKind，每工具有 scope/detect/format/dest 等字段
- F-021~F-029：Agent 文件 frontmatter 必需 name/description/color，正文分 Persona 和 Operations 两组语义部分
- F-044~F-052：check-divisions.sh 验证 5 位置一致性，使用 git ls-files 而非 glob，无 jq 依赖
- F-057~F-060：NEXUS 策略将代理编排为 7 阶段流水线（Phase 0-6），支持 Full/Sprint/Micro 三种模式

**反常识**：常识认为 AI 人格是"一个全能助手换不同语气"。agency-agents 揭示了另一种范式：人格是"岗位说明书"——每个 Agent 有明确的使命、可交付成果、工作流程和成功指标，而非仅个性差异。部门化使得 200+ 人格可组织、可检索、可按专业领域批量安装。更关键的是，format 字段保证"字节相同的输出"——两个工具只有在渲染文件完全相同时才能共享 format，这是一种比"兼容性"更严格的工程约束。

**行动**：
- 设计多 Agent 系统时，先用 divisions.json 式的分类法组织人格，再逐个填充。
- Agent 文件的 frontmatter 必需字段应由 lint 脚本强制校验，而非靠文档约定。
- 多工具适配时，用 installKind 区分 per-agent/roster/plugin 三种产物形态，避免为每个工具写独立转换逻辑。

---

## 洞察三：MCP vs Skill——工具协议与知识包的范式分野

**陈述**：本 bundle 中的项目揭示了两种根本不同的 AI 集成范式。MCP（Model Context Protocol）是**工具协议**——awesun-mcp 通过 stdio 或 HTTP 暴露 22 个结构化工具（device_add、control_connect、desktop_click_mouse 等），每个工具有 JSON Schema 定义的参数，AI 通过协议动态发现和调用工具，无需预读任何说明文档。Skill 是**知识包**——awesun-skill 不重新实现工具，而是通过 `executor.py`（MCPExecutor 类）连接已有的 MCP 服务器，SKILL.md 告诉 AI"有哪些工具、何时用、参数怎么填"，executor.py 处理实际的 MCP 通信。jira-skill 则代表第三种混合路径：它不使用 MCP，而是通过 PEP 723 内联依赖的 Python 脚本（uv run --script）直接调用 atlassian-python-api，SKILL.md 按意图映射脚本（triage→jira-issue.py work、QA→jira-issue.py qa），零 MCP 开销。retro-skill 同样走脚本路线，但脚本是自有的机械信号检测器（detect-mechanical.py），而非第三方 API 封装。

**证据**：
- F-001~F-008（awesun-mcp）：MCP Server 内置于向日葵客户端，22 个工具分三类，双模式通信（Stdio/HTTP）
- F-014~F-020（awesun-skill）：MCPExecutor 类通过 StdioServerParameters 和 stdio_client 连接 MCP，使用 AsyncExitStack 管理生命周期
- F-021~F-023（awesun-skill）：mcp-config.json 定义 command/env，AWESUN_API_URL 默认为 http://127.0.0.1:8908
- F-004（jira-skill）：核心特性"零 MCP 开销"，通过 Bash 调用脚本，无 Docker 容器启动
- F-031~F-035（jira-skill）：PEP 723 内联依赖，shebang 为 `#!/usr/bin/env -S uv run --script`，通过 PYTHONPATH 导入共享 lib
- F-055~F-057（jira-skill）：PRD 记录从 mcp-atlassian Docker 迁移到轻量脚本的原因——25 工具消耗 8000-12000 Token/会话

**反常识**：MCP 常被宣传为 AI 工具集成的"万能协议"，但 jira-skill 的迁移数据揭示了其成本：MCP 服务器的工具 Schema 会持续占用上下文窗口，25 个工具消耗 8000-12000 Token/会话，而实际使用中 5 个工具占 80% 调用量。Skill + 脚本的方式将"工具发现"外包给 SKILL.md 的意图映射（AI 按需读取），而非全量注入 Schema。MCP 适合"工具数量多、参数结构稳定、需跨客户端通用"的场景；Skill 脚本适合"高频工具集中、需自定义工作流、追求最低延迟"的场景。

**行动**：
- 评估集成方案时，先统计工具使用频率分布——若符合二八定律，Skill 脚本可能比 MCP 更高效。
- MCP 与 Skill 不互斥：awesun-skill 是"MCP 工具 + Skill 知识"的组合模式，executor.py 桥接两者。
- PEP 723 内联依赖使脚本可移植（无需 requirements.txt 或虚拟环境），是 Skill 脚本的理想分发格式。

---

## 洞察四：Jira Skill 的工程化——双技能拆分、PEP 723、21 脚本分层

**陈述**：jira-skill 将 Jira 集成为两个专业化技能而非单体技能：jira-communication（API 操作，含 21 个 Python 脚本）和 jira-syntax（Wiki 标记语法、模板、验证，纯知识技能）。这种拆分遵循"操作与知识分离"原则——语法参考不需要 Bash 执行权限，API 操作不需要语法表污染上下文。jira-communication 的 21 个脚本按三层组织：core（6 个：issue/search/worklog/attachment/setup/validate）、workflow（8 个：create/transition/comment/move/sprint/board/version/tempo-account）、utility（7 个：user/fields/link/weblink/worklog-query/watchers/qa-gather）。每个脚本使用 PEP 723 内联依赖声明（`atlassian-python-api>=3.41.0,<4` 和 `click>=8.1.0,<9`），shebang 为 `#!/usr/bin/env -S uv run --script`，通过 PYTHONPATH 操作导入共享 lib/ 库（LazyJiraClient、config、errors、input、output、users、jql、markup、changelog）。所有脚本支持 `--json/--quiet/--debug` 三种输出格式和 `--dry-run` 破坏性操作保护。版本一致性由 pre-commit 和 CI 强制：plugin.json 和两个 SKILL.md 的 metadata.version 必须匹配。

**证据**：
- F-002：双技能拆分——jira-communication（API 操作）和 jira-syntax（语法/模板/验证）
- F-017~F-020：21 脚本分 core(6)/workflow(8)/utility(7) 三层
- F-021：所有脚本支持 --help/--json/--quiet/--debug，破坏性操作支持 --dry-run
- F-031~F-035：PEP 723 头，依赖固定版本，PYTHONPATH 导入 lib，click 框架 CLI
- F-037~F-042：lib/client.py 提供 LazyJiraClient，默认超时 30 秒，is_account_id 支持新旧格式，resolve_assignee 处理 me/Cloud ID/用户名模糊匹配
- F-043~F-047：lib/config.py 配置加载优先级（explicit→~/.env.jira→环境变量），normalize_netloc 剥离默认端口
- F-050~F-054：版本一致性由 pre-commit/CI 强制，每脚本必须三种输出格式，写操作必须 --dry-run
- F-057：使用分析显示 5 个工具占 80% 调用量（add_worklog 22.8%、get_issue 18.6%、search 10.7%、update 8.1%、create 7.3%）

**反常识**：常识认为"一个插件应该做所有事"。jira-skill 证明了按"操作/知识"边界拆分技能的价值：jira-syntax 无 allowed-tools（纯参考），不会触发脚本执行权限；jira-communication 专注 API，其 SKILL.md 的意图映射表使 AI 能快速定位正确脚本而非浏览全部 21 个。更深层的反常识是依赖固定：atlassian-python-api 故意固定在 >=3.41,<4，因为 v4 有 Jira Cloud 变更和 DC 回归——这不是技术债，而是面向 Jira Server/DC 9.12 的兼容性承诺。

**行动**：
- 大型技能按"操作/知识"或"高频/低频"边界拆分为多个 SKILL.md，减少单次加载的上下文量。
- 脚本分层（core/workflow/utility）使 AI 能按意图快速定位，SKILL.md 的意图映射表是关键导航。
- 统一 CLI 契约（--json/--quiet/--debug/--dry-run）降低 AI 调用脚本的认知负担。
- 版本号必须在 plugin.json 和所有 SKILL.md 中同步，用 CI 门控而非人工保证。

---

## 洞察五：Retro Skill 的自省与演进——机械信号、五层流水线、七目标路由

**陈述**：retro-skill 是一个 LLM 驱动的会话复盘技能，其核心设计是"让 AI 审查自己的工作过程并将学习成果路由到正确的位置"。它定义了六种运行模式：Sweep（全会话分析）、Spotlight（单问题聚焦）、Outcome（事后输出复盘）、Audit（跨会话架构审查）、Promote（本地记忆库存迁移）、Auto（SessionEnd 钩子自动触发）。流水线分五层（Schicht A-E）：A 层机械预检由 `detect-mechanical.py` 实现，检测 A1-A20 和 C6 共 21 个确定性信号（工具错误、用户纠正、工具误用、主分支提交、权限重审批、重复命令等），不依赖 LLM；B 层 LLM 增强添加 14 个推断信号并过滤误报；C 层跨会话增强由 `scan-cross-session.py` 实现；D 层 Outcome 信号检测；E 层评估咨询。分类阶段按"权威优先"三轴（Axis 0 权威性、Axis 1 可执行性、Axis 2 覆盖面）将发现路由到七个目标位置：canonical-source、personal-rule、project-rule、skill-update、new-skill、checkpoint、harness-artefact。核心原则是"No silent writes"——每次物化都需逐提案审批，补丁始终指向源仓库而非插件缓存。

**证据**：
- F-008：六种模式 Sweep/Spotlight/Outcome/Audit/Promote/Auto
- F-017~F-022：七个目标位置，personal-rule 追加到 ~/.claude/CLAUDE.md，skill-update 对源仓库开 PR
- F-023~F-028：10 阶段流水线，Schicht A 检测 18 个确定性信号（实际 21 个含 C6），效率目标每次 /retro 仅 1 次 LLM 传递
- F-029~F-034：分类三轴，Axis 0 技能仅作为自身流程规范来源，Axis 1 机械门控最强，Axis 2 升级顺序 skill-update→project-rule→personal-rule
- F-041~F-052：detect-mechanical.py 实现 A1-A20+C6 信号，SIGNAL_FUNCS 字典注册，支持 --transcript-file/--output-format/--signals 参数
- F-044：A6 检测用户纠正短语，支持英语和德语
- F-045：A11 检测结构化文件上的工具误用（grep/sed/awk 操作 json/yaml，cat/head/tail 代替 Read）
- F-048：A19 检测重复命令形状（≥8 次），提示包装为脚本
- F-059~F-066：scan-memory-inventory.py 是 Promote 模式前端，drain 子命令移动到 .promoted/ 墓碑目录（从不删除）
- F-074~F-076：安全边界——补丁指向源仓库、禁止自动合并/机器人署名/--no-verify、PR 需要 DCO 签名

**反常识**：大多数 AI 工具的"改进"依赖用户手动反馈或事后日志分析。retro-skill 的反常识在于：它用确定性正则和 shell 解析（A 层）做第一道摩擦检测，只在机械层无法判定时才调用 LLM（B 层），且每次复盘仅 1 次 LLM 传递。这种"机械优先、LLM 兜底"的设计与"AI 万能"的直觉相反，但它带来了三个优势：可预测（正则不会幻觉）、低成本（21 个信号本地计算）、可审计（每个信号有 ID 和函数名）。A11 检测"用 grep/sed/awk 操作 JSON/YAML"和"用 cat/head/tail 代替 Read"尤其精妙——它在检测 AI 是否违反了工具使用规范，而非检测代码 bug。

**行动**：
- 设计自省系统时，先用确定性规则覆盖可量化的摩擦信号，LLM 仅用于模糊判断。
- 学习成果的路由目标必须有权威层级——最广泛有用的目标优先（skill-update > project-rule > personal-rule），避免知识被困在个人记忆中。
- "No silent writes"原则应作为所有 AI 自动化的底线——提案可以自动生成，但物化必须人工审批。
- 信号函数通过字典注册（SIGNAL_FUNCS）便于选择性运行和测试，每个信号有独立 ID 便于追踪。

---

## 知识地图

### 概念文档规划

| 编号 | 文件名 | 标题 | 覆盖事实 | 前置依赖 |
|------|--------|------|---------|---------|
| 00 | 00-overview.md | AI Agent Skills 生态概览 | 各项目 F-001~F-005 | 无 |
| 01 | 01-skill-md-standard.md | SKILL.md 标准与渐进式披露 | awesun-skill F-006~F-013、jira F-012~F-022、retro F-005~F-010 | 00 |
| 02 | 02-agency-agents-division.md | agency-agents 部门化人格体系 | agency F-005~F-063 | 00 |
| 03 | 03-agent-persona-format.md | Agent 人格文件格式与 frontmatter | agency F-021~F-029 | 02 |
| 04 | 04-mcp-protocol.md | MCP 协议与工具集成 | awesun-mcp F-001~F-032、awesun-skill F-014~F-023 | 01 |
| 05 | 05-plugin-architecture.md | 插件架构（plugin.json/hooks/commands） | jira F-006~F-011、retro F-067~F-081 | 01 |
| 06 | 06-awesun-remote-control.md | Awesun 远程控制 Skill 实战 | awesun-skill F-001~F-029、awesun-mcp F-005~F-027 | 04 |
| 07 | 07-ui-locator-pattern.md | UI 定位器模式（坐标归一化、视觉定位） | awesun-ui-locator F-001~F-030 | 01 |
| 08 | 08-jira-skill-engineering.md | Jira Skill 工程化实践 | jira F-001~F-057 | 05 |
| 09 | 09-retro-skill-introspection.md | Retro Skill 自省与演进模式 | retro F-001~F-081 | 05 |
| 10 | 10-skill-tooling-scripts.md | Skill 脚本工具模式（Python/Shell） | jira F-031~F-047、retro F-041~F-066、awesun F-014~F-020 | 01 |
| 11 | 11-integration-patterns.md | 多工具兼容与集成模式 | agency F-011~F-020、jira F-003、retro F-077 | 02,05 |

### 学习路径

1. **入门（理解标准）**：00 → 01
   - 先建立 AI Agent Skills 生态的全局视图（6 个项目定位、两种集成范式），再深入 SKILL.md 标准（frontmatter、渐进式披露、三层结构）。
2. **核心（理解组织与协议）**：02 → 03 → 04 → 05
   - 掌握 agency-agents 的部门化人格体系和人格文件格式，理解 MCP 工具协议，再学习插件架构（plugin.json/hooks/commands）。
3. **实战（理解具体实现）**：06 → 07 → 08 → 09
   - Awesun 远程控制实战（MCP+Skill 桥接）、UI 定位器模式（视觉+坐标）、Jira 工程化（双技能+PEP 723）、Retro 自省（机械信号+流水线）。
4. **进阶（理解模式）**：10 → 11
   - 脚本工具模式（Python/Shell 最佳实践）和多工具兼容集成模式。

### 示例文档规划

| 文件名 | 标题 | 内容要点 |
|--------|------|---------|
| skill-authoring.md | SKILL.md 编写示例 | ① 最小可用 SKILL.md（frontmatter+正文）；② 添加 references/ 扩展文档；③ 添加 scripts/ 可执行脚本；④ allowed-tools 声明；⑤ 渐进式披露三层结构；⑥ 常见错误与最佳实践 |
