# Hermes 深度集成 SpecWeave 工作区规范 - 实施计划

## [ ] Task 1: 创建插件骨架与清单文件
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在用户 Hermes 插件目录（Windows 下 `C:\Users\admin\.hermes\plugins\specweave-bridge\`）创建插件目录
  - 创建 `plugin.yaml`：name=specweave-bridge, version=0.1.0, description="SpecWeave工作区规范集成", kind=standalone, manifest_version=1
  - 创建 `__init__.py`：包含 `register(ctx)` 入口函数骨架
  - 创建 `detector.py`：实现 SpecWeave 工作区检测逻辑（向上查找 AGENTS.md，检查"启动协议"关键词，缓存 git root 路径）
  - 创建 `_constants.py`：插件名称、版本、SpecWeave 特征关键词、子区域列表（apps/projects/vendor）、Skill 列表
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: plugin.yaml 存在且包含必填字段（name/version/description/manifest_version）
  - `programmatic` TR-1.2: detector.py 的 `is_specweave_workspace(path)` 函数对 SpecWeave 根目录返回 True，对其他目录返回 False
  - `programmatic` TR-1.3: detector.py 的 `find_specweave_root(start_path)` 能从子目录向上查找到根目录
  - `human-judgement` TR-1.4: 插件目录结构符合 Hermes 插件规范（plugin.yaml + __init__.py）

## [ ] Task 2: 实现工作区检测与启动协议注入 hook
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `__init__.py` 的 `register(ctx)` 中注册 `on_session_start` hook
  - hook 中：检测当前 cwd 是否为 SpecWeave 工作区（调用 detector），如果是则：
    - 缓存 specweave_root 路径到插件状态
    - 构建精简版启动协议指导文本（中文，步骤1-4，不超过 500 字）
    - 将指导文本通过 ctx 的方式注入到 volatile 层提示词（通过 hook 的 prompt 增强机制或 register 到系统提示词构建钩子）
  - 实现 `_build_startup_protocol_guidance(root_path)` 函数返回指导文本
  - 非 SpecWeave 工作区时 hook 立即返回，不做任何操作
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: 在 SpecWeave 目录启动 hermes oneshot 测试，系统提示词包含启动协议指导文本
  - `programmatic` TR-2.2: 在非 SpecWeave 目录启动，系统提示词不含 SpecWeave 相关内容
  - `human-judgement` TR-2.3: 启动协议指导文本为中文，步骤清晰简洁，不超过 500 字
  - `human-judgement` TR-2.4: 指导文本指引模型使用 specweave_route 工具而非直接硬编码路径

## [ ] Task 3: 实现 specweave_route 路由工具
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `router.py`：实现上下文路由逻辑，基于 `.agents/context-routing.md` 的映射表
  - 构建路由表数据结构（硬编码核心路由项，覆盖 vendor 预检和常规任务类型）：
    - vendor 预检：Skill 创建/优化/调试 → vendor/flexloop skill-creator + rules/skill-development.md
    - 内容敏感度预检 → rules/content-sensitivity-precheck.md
    - 角色定义 → roles/README.md
    - 复盘/洞察/七概念 → commands/ 对应规范
    - CI 检查 → skills/ci-check-cmd/SKILL.md
    - 链接检查 → skills/link-check-cmd/SKILL.md
    - 等等（至少覆盖 15 个常用路由项）
  - 实现 `resolve_route(task_type: str, cwd: str, specweave_root: str) -> list[str]`：返回需要读取的文件相对路径列表
  - 实现子区域检测：检查 cwd 是否在 apps/projects/vendor 下，如果是则附加对应区域 AGENTS.md 路径
  - 注册 `specweave_route` 工具：参数 `task_type`（字符串，描述任务类型），返回 JSON 格式的路径列表+简要说明
  - 工具 check_fn：仅在检测到 SpecWeave 工作区时可用
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: specweave_route 工具在 SpecWeave 工作区会话中可用，非工作区不可用
  - `programmatic` TR-3.2: 调用 specweave_route(task_type="skill 创建") 返回路径列表包含 vendor flexloop 相关文件
  - `programmatic` TR-3.3: 调用 specweave_route(task_type="复盘") 返回 commands/ 相关路径
  - `programmatic` TR-3.4: cwd 在 apps/ 下时返回路径包含 apps/AGENTS.md
  - `human-judgement` TR-3.5: 路由表覆盖 context-routing.md 中最常用的 15+ 项任务类型

## [ ] Task 4: 封装验证脚本工具（服务门控）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 创建 `script_tools.py`：将 SpecWeave 核心验证脚本桥接为 Hermes 工具
  - 每个工具使用 subprocess 调用对应 Python 脚本，设置正确的 cwd（specweave_root），使用 Hermes conda 环境的 Python
  - 注册以下工具（check_fn：在 SpecWeave 工作区且文件存在时可用）：
    - `specweave_check_links`：调用 `.agents/scripts/check-links.py`，参数可选 `fix: bool`、`check_external: bool`
    - `specweave_check_duplication`：调用 `.agents/scripts/check-duplication.py`
    - `specweave_check_vendor`：调用 `.agents/scripts/check-vendor.py`，参数可选 `deep: bool`
    - `specweave_ci_check`：调用 `.agents/scripts/ci-check.ps1`（Windows）或 `.agents/scripts/ci-check.sh`（跨平台）
    - `specweave_docgen`：调用 `.agents/scripts/docgen.py`，参数 `target: str`（nav/dashboard/apps/all）
    - `specweave_check_stage_guardrails`：调用 `.agents/scripts/check-stage-guardrails.py`，参数可选 `log_file: str`
  - 每个工具的 schema 包含清晰的中文描述和参数说明
  - 工具返回 stdout/stderr 的最后 4000 字符（避免输出过大）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 在 SpecWeave 工作区会话中工具列表包含上述 6 个工具
  - `programmatic` TR-4.2: 非 SpecWeave 工作区这些工具不可见
  - `programmatic` TR-4.3: 调用 specweave_check_links() 返回脚本执行输出（0 退出码或错误信息）
  - `human-judgement` TR-4.4: 每个工具的 schema 描述清晰，参数有中文说明

## [ ] Task 5: 创建 SpecWeave 技能包（Hermes Skills）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建技能包安装目录：`C:\Users\admin\.hermes\skills\specweave\`
  - 为每个核心 Skill 门面创建对应的 Hermes SKILL.md（适配 Hermes frontmatter 格式）：
    - 必需 frontmatter 字段：name（小写连字符，前缀 specweave-）、description（≤60字符中文）、author（"SpecWeave"）、category（"specweave"）、platforms（全平台）
    - 正文章节适配：When to Use → 何时使用；Prerequisites → 前置条件；How to Run → 使用方式（调用对应工具或执行脚本）；Quick Reference → 快速参考；Notes → 注意事项
  - 封装的核心技能列表（10个高频）：
    1. specweave-seven-concepts：七概念方法论编排
    2. specweave-ci-check：CI综合检查
    3. specweave-docgen：文档导航/看板生成
    4. specweave-link-check：链接有效性检查修复
    5. specweave-atomization：原子化操作收尾
    6. specweave-atomic-commit：原子化提交
    7. specweave-mermaid：Mermaid图表管理
    8. specweave-insight：洞察分析
    9. specweave-retrospective：复盘
    10. specweave-check-duplication：重复代码检测
  - 创建 `_skill_index.md` 或由 Hermes 自动索引
  - 技能中"使用方式"章节引用 Task 4 注册的对应工具
- **Acceptance Criteria Addressed**: AC-5, AC-9
- **Test Requirements**:
  - `programmatic` TR-5.1: 技能目录存在，包含至少 10 个 SKILL.md 文件
  - `programmatic` TR-5.2: 每个 SKILL.md frontmatter 包含 name/description/author/category 且格式正确
  - `programmatic` TR-5.3: 重启 Hermes 后 `/skills` 或技能索引显示 specweave 分类下的技能
  - `human-judgement` TR-5.4: 技能内容清晰说明如何调用对应工具/脚本，遵循 Hermes 技能章节结构

## [ ] Task 6: 实现 CLI 子命令和斜杠命令
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 创建 `cli_commands.py`：注册 `hermes specweave` CLI 子命令
  - 子命令结构：
    - `hermes specweave status`：显示当前工作区状态（是否在 SpecWeave、根路径、检测到的子区域、已注册工具数、技能包状态）
    - `hermes specweave route <task-type>`：命令行直接查询路由，输出需要读取的文件列表
    - `hermes specweave doctor`：检查集成健康状态（插件是否启用、技能包是否安装、脚本路径是否存在）
  - 注册会话内斜杠命令 `/specweave-load`：参数 `<规范名>`，调用 specweave_route 获取路径并读取文件内容注入对话上下文
  - 斜杠命令通过 ctx.register_command() 注册，handler 调用路由工具+文件读取
- **Acceptance Criteria Addressed**: AC-8, AC-10
- **Test Requirements**:
  - `programmatic` TR-6.1: `hermes specweave status` 在 SpecWeave 目录执行输出检测信息
  - `programmatic` TR-6.2: `hermes specweave status` 在非 SpecWeave 目录提示"非SpecWeave工作区"
  - `programmatic` TR-6.3: `hermes specweave route "skill 创建"` 输出路由路径列表
  - `human-judgement` TR-6.4: `/specweave-load context-routing` 在会话中能加载并显示规范内容

## [ ] Task 7: 插件注册与集成测试
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 在 `__init__.py` 的 `register(ctx)` 中完整注册所有组件：
    - on_session_start hook（Task 2）
    - specweave_route tool（Task 3）
    - 6个脚本工具（Task 4）
    - CLI 子命令（Task 6）
    - 斜杠命令（Task 6）
  - 更新 `~/.hermes/config.yaml` 启用插件：在 `plugins.enabled` 列表中添加 `specweave-bridge`
  - 创建插件安装说明：如何手动安装（复制到 plugins 目录、启用、重启 Hermes）
  - 执行冒烟测试：
    1. 在 SpecWeave 根目录启动 `hermes oneshot "你现在在哪个工作区？应该先做什么？"` 验证启动协议被注入
    2. 调用 `hermes specweave status` 验证状态命令
    3. 在会话中调用 specweave_route 工具验证路由
    4. 调用 specweave_check_links 验证脚本工具
    5. 在非 SpecWeave 目录启动验证零影响
- **Acceptance Criteria Addressed**: AC-1 ~ AC-10
- **Test Requirements**:
  - `programmatic` TR-7.1: config.yaml plugins.enabled 包含 specweave-bridge
  - `programmatic` TR-7.2: 启动 Hermes 不报错，插件成功加载
  - `programmatic` TR-7.3: SpecWeave 目录 oneshot 测试返回包含启动协议指引的响应
  - `programmatic` TR-7.4: 非 SpecWeave 目录 oneshot 测试无 SpecWeave 内容
  - `human-judgement` TR-7.5: 完整端到端流程可走通（检测→路由→工具调用→技能发现）

## [ ] Task 8: 子区域路由完善与边界处理
- **Priority**: medium
- **Depends On**: Task 3, Task 7
- **Description**:
  - 测试 cwd 在 `apps/`、`projects/`、`vendor/` 下时的路由行为
  - 为 apps/ 区域实现子路由：读取 apps/AGENTS.md 后识别当前应用（如 prompt_extraction），追加对应应用的 AGENTS.md
  - 处理边界情况：
    - cwd 在 .chaos/ 或 .trae/ 等非路由目录时的行为
    - 从子目录启动时的路径向上查找正确停止在 git root
    - Windows 长路径、中文路径、空格路径处理
    - AGENTS.md 不存在时的优雅降级
  - 添加 `specweave doctor` 的健康检查项：子区域检测、路径可读性、Python 环境可用性
- **Acceptance Criteria Addressed**: AC-7, AC-2
- **Test Requirements**:
  - `programmatic` TR-8.1: 在 apps/prompt_extraction/ 启动 specweave_route 返回包含 apps/AGENTS.md
  - `programmatic` TR-8.2: Windows 路径（含空格、中文）不报错
  - `human-judgement` TR-8.3: 边界情况处理优雅，不崩溃，给出友好提示

# Task Dependencies
```
Task 1 (插件骨架) ──┬── Task 2 (启动协议hook) ──┐
                     ├── Task 3 (路由工具) ─────┤
                     └── Task 5 (技能包) ───────┤
                                                  ├── Task 7 (集成测试) ── Task 8 (边界完善)
                     ├── Task 4 (脚本工具) ───────┤
                     └── Task 6 (CLI/斜杠命令) ──┘
```

- Task 1 无前置
- Task 2/3/5 依赖 Task 1，可并行开发
- Task 4 依赖 Task 1+2（需要 hook 提供 root 路径），可与 Task 3/5/6 并行
- Task 6 依赖 Task 1+3
- Task 7 依赖 Task 2-6 全部完成
- Task 8 依赖 Task 7 测试反馈

# 实施策略
1. **最小可用先行**：Task 1+2+3 先完成（检测+启动协议+路由工具），即可获得核心价值
2. **工具和技能增量添加**：Task 4（脚本工具）和 Task 5（技能包）可独立迭代，每个工具/技能单独验证
3. **CLI 和命令最后加**：Task 6 是便利性增强，核心功能通过工具调用已可用
4. **测试驱动**：每个 Task 完成后立即用 `hermes oneshot` 或简单脚本验证，不等到最后
5. **遵循 Hermes Footprint Ladder**：所有能力通过 Plugin API 实现，不触碰核心源码

# 安装路径说明
- 插件目录：`C:\Users\admin\.hermes\plugins\specweave-bridge\`（用户级插件）
- 技能包目录：`C:\Users\admin\.hermes\skills\specweave\`
- 配置位置：`C:\Users\admin\.hermes\config.yaml` 的 `plugins.enabled` 列表
