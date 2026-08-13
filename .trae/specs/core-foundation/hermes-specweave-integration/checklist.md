# Hermes 深度集成 SpecWeave 工作区规范 - 验证检查清单

> 依据 spec.md 的 10 个验收标准（AC-1 ~ AC-10）逐项核对。

## 插件基础结构
- [ ] CP-1: 插件目录 `~/.hermes/plugins/specweave-bridge/` 存在，包含 `plugin.yaml` 和 `__init__.py`
- [ ] CP-2: `plugin.yaml` 字段完整（name=specweave-bridge, version=0.1.0, description, kind=standalone, manifest_version=1）
- [ ] CP-3: `__init__.py` 的 `register(ctx)` 函数可正常导入，无语法错误
- [ ] CP-4: 工作区检测器（detector.py）正确识别 SpecWeave 根目录（AGENTS.md + "启动协议"关键词）
- [ ] CP-5: 工作区检测器从子目录向上查找能正确找到 git root
- [ ] CP-6: 非 SpecWeave 目录检测器返回 False

## 工作区检测与启动协议
- [ ] AC-1: SpecWeave 根目录启动 Hermes，系统提示词 volatile 层包含启动协议指导
- [ ] AC-2: 非 SpecWeave 目录启动 Hermes，系统提示词无 SpecWeave 内容，工具列表无 specweave 工具
- [ ] AC-3: 启动协议指导为中文，包含步骤概览，指引使用 specweave_route 工具，长度≤500字
- [ ] AC-9: 多轮对话中 stable 层前缀保持字节稳定，SpecWeave 内容不破坏前缀缓存

## 路由工具
- [ ] AC-4: `specweave_route` 工具在 SpecWeave 工作区可用
- [ ] AC-4: 调用 specweave_route(task_type="skill 创建") 返回 vendor flexloop skill-creator 相关路径
- [ ] AC-4: 调用 specweave_route(task_type="复盘") 返回 commands/retrospective 相关路径
- [ ] AC-4: 路由表覆盖至少 15 个常用任务类型
- [ ] AC-7: cwd 在 apps/prompt_extraction/ 下时路由结果包含 apps/AGENTS.md
- [ ] AC-7: cwd 在 vendor/ 下时路由结果包含 vendor/AGENTS.md

## 脚本桥接工具
- [ ] AC-6: `specweave_check_links` 工具在 SpecWeave 工作区可用
- [ ] AC-6: `specweave_check_duplication` 工具可用
- [ ] AC-6: `specweave_check_vendor` 工具可用
- [ ] AC-6: `specweave_ci_check` 工具可用
- [ ] AC-6: `specweave_docgen` 工具可用
- [ ] AC-6: `specweave_check_stage_guardrails` 工具可用
- [ ] AC-6: 调用 specweave_check_links() 返回脚本执行输出（非错误堆栈）
- [ ] AC-6: 每个工具的 schema 描述为中文，参数有说明
- [ ] AC-6: 非工作区时这 6 个工具不可见

## 技能包
- [ ] AC-5: `~/.hermes/skills/specweave/` 目录存在
- [ ] AC-5: 包含至少 10 个核心技能的 SKILL.md（seven-concepts, ci-check, docgen, link-check, atomization, atomic-commit, mermaid, insight, retrospective, check-duplication）
- [ ] AC-5: 每个 SKILL.md frontmatter 格式正确（name/description/author/category），name 使用 specweave- 前缀
- [ ] AC-5: 重启 Hermes 后技能索引中可见 specweave 分类的技能
- [ ] AC-5: 技能内容包含"使用方式"章节，引用对应的桥接工具
- [ ] AC-5: 技能描述为中文，≤60字符

## CLI 子命令与斜杠命令
- [ ] AC-8: `hermes specweave status` 在 SpecWeave 目录输出检测信息（根路径、子区域、工具数、技能状态）
- [ ] AC-8: `hermes specweave status` 在非 SpecWeave 目录提示"非SpecWeave工作区"
- [ ] AC-8: `hermes specweave route "skill 创建"` 命令行输出路由路径列表
- [ ] AC-8: `hermes specweave doctor` 输出健康检查结果
- [ ] AC-10: 会话内 `/specweave-load context-routing` 能加载并显示规范内容
- [ ] AC-10: `/specweave-load` 不存在的规范名给出错误提示

## 集成与端到端测试
- [ ] CP-7: `~/.hermes/config.yaml` 的 plugins.enabled 列表包含 specweave-bridge
- [ ] CP-8: 启动 Hermes 无报错，插件加载成功
- [ ] CP-9: `hermes oneshot "你现在在哪个工作区？遵循什么启动协议？"`（在 SpecWeave 根目录执行）返回包含启动协议步骤的响应
- [ ] CP-10: 非 SpecWeave 目录 oneshot 测试响应不含 SpecWeave 相关内容
- [ ] CP-11: 在会话中可正常调用 specweave_route 并获取路径列表
- [ ] CP-12: 在会话中可正常调用 specweave_check_links 并获取执行结果
- [ ] CP-13: 插件禁用（从 plugins.enabled 移除）后重启，所有 specweave 工具/技能消失

## 边界与健壮性
- [ ] CP-14: Windows 路径（含空格、中文目录名）不导致插件崩溃
- [ ] CP-15: cwd 在 .chaos/、.trae/、.git/ 等特殊目录时行为优雅（降级或正确识别根）
- [ ] CP-16: AGENTS.md 被删除时检测器优雅降级（返回 False 或提示）
- [ ] CP-17: 脚本执行超时或出错时工具返回友好错误信息而非崩溃
- [ ] CP-18: 不引入新的第三方 Python 包依赖（仅使用标准库 + Hermes 已有依赖）

## 缓存与性能
- [ ] CP-19: 插件初始化时间 < 500ms（不显著拖慢 Hermes 启动）
- [ ] CP-20: 非 SpecWeave 工作区插件初始化开销 < 50ms（快速路径退出）
- [ ] AC-9: 注入的提示词内容位于 volatile 层，不影响 stable 层缓存键
