---
title: SpecWeave复赛作品技术支持资源指南 - 实施计划
date: 2026-07-22
---

# SpecWeave复赛作品技术支持资源指南 - The Implementation Plan

## [/] Task 1: 创建文档骨架与资源全景图
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `playground/semi-final-support/` 目录
  - 创建主文档 `README.md`，包含frontmatter、目录结构、Mermaid资源全景图
  - 定义8大资源类别和6个开发阶段的章节框架
  - 资源全景图使用Mermaid flowchart展示代码/工具/文档/模板/容器/案例之间的关系
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-7, AC-9]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 目录结构清晰，8大类别+6个阶段+快速参考卡片的框架完整
  - `programmatic` TR-1.2: Mermaid全景图通过check-mermaid.py检查0错误
  - `human-judgement` TR-1.3: frontmatter包含content_sensitivity: "private"
  - `human-judgement` TR-1.4: 文档开头有简明的"如何使用本指南"说明
- **Notes**: 全景图参考优秀作品库的分类体系图风格，按类别用subgraph分组

## [ ] Task 2: 编写可复用代码模块章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 详细说明9个核心Python库模块：frontmatter.py, markdown.py, cli.py, patterns.py, atomic_write.py, io_safety.py, rules.py, spec_loader.py, process.py
  - 说明多智能体冲突解决模块（collaboration/conflict_resolution.py）的ConflictResolver类
  - 说明测试场景生成器（lib/testing/）的generate_agents, edge_scenarios等函数
  - 说明MDI Mermaid生成器（mdi/generator.py）的调用方式
  - 每个模块提供：功能概述、核心API表格、导入方式、代码示例、适用场景
  - 标注第三方依赖（如pandas用于prompt_extraction）
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每个模块至少1个可运行的Python代码片段（import示例+核心调用）
  - `programmatic` TR-2.2: 代码示例通过Python语法检查（python -m py_compile）
  - `human-judgement` TR-2.3: API表格列出函数名、参数、返回值、用途4列
  - `human-judgement` TR-2.4: 有第三方依赖的模块明确标注"需要安装xxx"
- **Notes**: 代码示例必须使用正确的相对导入路径（from .agents.scripts.lib import xxx 的形式需说明sys.path处理方式，或建议复制到项目中使用）

## [ ] Task 3: 编写API接口与服务章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 说明AI代码助手Flask API（apps/ai-code-assistant/app.py）：/api/explain, /api/ask, /api/learning-path
  - 说明提示词萃取系统Pipeline API（apps/prompt_extraction/pipeline.py）：run_single, run_batch, export_results
  - 说明MDI MCP服务器端点（mdi/mcp_server.py）：GET/POST /generate
  - 说明Home Assistant API封装（ha_api.py）：get_entities, set_state等
  - 说明论坛Bot API（forum_bot/）：auth, content, browser, reply模块
  - 每个API提供：端点/函数签名、请求参数说明、响应格式、curl/Python调用示例
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每个API有完整的请求参数表格（参数名/类型/必填/说明）
  - `human-judgement` TR-3.2: 每个API至少1个调用示例（curl或Python requests）
  - `human-judgement` TR-3.3: 标注API的运行前置条件（如需要启动Flask服务、需要.env配置等）
  - `human-judgement` TR-3.4: 响应示例使用JSON格式，字段说明清晰
- **Notes**: Flask API需要说明如何启动服务（python app.py）；提示词萃取系统需要标注pandas依赖

## [ ] Task 4: 编写开发工具链与Skill章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 说明18个Skill门面的使用方式：ci-check, docgen, insight, mermaid, retrospective, atomic-commit, atomization, link-check, export-report, extraction, seven-concepts, forum-posting等
  - 说明35+脚本工具的分类和用法：
    - 质量检查类：check-mermaid, check-links, check-duplication, check-hardcode, check-frontmatter, check-spec-format等
    - 生成构建类：docgen, generate-nav, generate-readme, generate-graph, generate-dashboard, generate-tests等
    - 自动化类：forum-bot, ha_api, backup-knowledge, spec-loader等
    - CI集成类：ci-check.sh/ps1
  - 每个工具提供：命令格式、核心参数、典型使用场景、输出示例
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-4.1: 抽样5个脚本运行--help，命令格式与文档描述一致
  - `human-judgement` TR-4.2: 工具按功能分类（检查/生成/分析/自动化），每组有使用场景总述
  - `human-judgement` TR-4.3: Skill使用说明包含触发关键词（如输入"/commit"触发原子提交）
  - `human-judgement` TR-4.4: CI检查脚本说明包含10项检查的执行顺序
- **Notes**: 脚本路径使用相对于项目根目录的写法；Skill部分说明在Trae IDE中如何触发

## [ ] Task 5: 编写模板、容器化与部署章节
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 容器化模板：
    - PyTorch基础镜像（apps/pytorch-base/）：Dockerfile + environment.yml + build.sh，适合AI/ML项目
    - Docker SSH DIND（apps/docker-ssh-dind/）：Containerfile + entrypoint.sh，适合CI/CD环境
    - XMNN运行时（apps/xmnn-runtime/docker/）：轻量模型部署方案
  - 文档模板：
    - 任务交接模板（templates/handoff-template.md）
    - 任务模板（templates/task-template.md）
    - Pattern文档模板（参考.agents/templates/下的模板和patterns目录现有文件）
  - vendor参考：
    - flexloop Agent框架（vendor/flexloop/）：AGENTS.md注册体系
    - ark-cli工具（vendor/ark-cli/）：CLI工具参考
    - Chaos混沌工程（vendor/flexloop/apps/chaos/）：tasks.py + 故障注入
  - 部署文档：参考vendor/flexloop/docs/tech/deploy.md
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 每个容器模板包含Dockerfile路径、构建命令、适用场景说明
  - `human-judgement` TR-5.2: 文档模板提供使用步骤（复制→填写→保存）
  - `human-judgement` TR-5.3: vendor资源标注"参考/学习用"与"可直接复用"的区别
  - `human-judgement` TR-5.4: 每个模板/容器有可点击的源文件链接
- **Notes**: 容器化部分说明docker build命令和端口映射；模板部分给出填写示例

## [ ] Task 6: 编写测试质量保障与性能优化章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 测试框架：
    - pytest配置（pytest.ini）和测试目录结构（.agents/scripts/tests/）
    - 测试场景生成器（lib/testing/）：边界场景、边缘案例、参数化用法
    - 多智能体冲突解决模块的测试用例参考
  - 质量保障10项CI检查：
    - 仓库合规→链接检查→Spec一致性→模式成熟度→文档生成→重复代码→阶段守卫→SG仪表盘→文件放置→.temp生命周期
    - 执行命令：ci-check.sh（Linux/Mac）或 ci-check.ps1（Windows）
  - 兼容性解决方案：
    - Mermaid跨环境渲染：check-mermaid.py + 安全编码六规则
    - Python跨平台：零依赖原则（标准库优先）、sitecustomize.py编码处理
    - Git跨平台：setup-cmd-utf8.ps1、.gitattributes、.editorconfig
  - 性能优化支持：
    - 原子写入（atomic_write.py）：避免并发写入损坏
    - IO安全封装（io_safety.py）：安全文件读写
    - 进程管理（process.py）：跨平台进程启动/停止/监控
    - 预提交钩子（githooks/）：阻止临时依赖和大文件提交
- **Acceptance Criteria Addressed**: [AC-1, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-6.1: CI检查流程有清晰的10步执行顺序说明
  - `human-judgement` TR-6.2: 每个兼容性方案说明"问题→方案→工具/命令"三要素
  - `human-judgement` TR-6.3: 性能优化模块有代码示例
  - `human-judgement` TR-6.4: 测试场景生成器提供pytest参数化示例代码
- **Notes**: 引用check-mermaid.py的安全编码规则，这是跨平台Mermaid渲染的关键经验

## [ ] Task 7: 编写技术文档与知识库导航章节
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 技术文档索引：
    - 入门指南：ONBOARDING.md（L0，<100行速查）
    - 能力注册中心：capability-registry.md（L1，全量能力索引）
    - 开发规范：docs/development-standards.md
    - 技术栈说明：docs/tech-stack.md
    - API文档：docs/code-wiki/key-apis.md
    - 模块说明：docs/code-wiki/modules.md
    - 调试指南：docs/code-wiki/debugging.md
    - 运行时说明：docs/code-wiki/runtime.md
  - 角色定义：roles/目录下7个角色（architect/developer/reviewer/tester/orchestrator/co-founder/thesis-advisor）
  - 命令集：commands/目录下13个命令（复盘/洞察/萃取/原子提交/原子化/Mermaid/导出报告/第一性原理/七概念/文件创建/论坛/Home Assistant/对抗性评审）
  - 知识库标签体系：docs/knowledge/tags/下的标签索引
  - 优秀作品库入口：playground/excellent-works-catalog/README.md（563件案例）
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 文档索引按"入门→进阶→专项"三层组织
  - `programmatic` TR-7.2: 每个文档链接使用正确的相对路径
  - `human-judgement` TR-7.3: 对每个文档提供"读了能解决什么问题"的一句话说明
- **Notes**: 重点突出"选手遇到X问题应该读哪个文档"的导航逻辑

## [ ] Task 8: 编写按开发阶段的资源工作流章节
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 阶段1-项目初始化：推荐AGENTS.md启动协议、Spec-driven开发（spec-loader）、项目模板选择、容器化环境搭建、pre-commit hooks配置
  - 阶段2-核心开发：推荐可复用代码库模块、Mermaid图表（MDI/Mermaid-cmd）、提示词萃取Pipeline、API接口参考
  - 阶段3-质量保障：推荐CI全量检查（ci-check）、Mermaid语法检查、链接检查、重复代码检测、硬编码检测、pytest测试框架
  - 阶段4-性能优化：推荐原子写入、IO安全、进程管理、场景生成器做边界测试、Chaos混沌工程
  - 阶段5-部署交付：推荐容器化模板（PyTorch/DIND）、文档生成（docgen）、导航自动生成
  - 阶段6-文档撰写：推荐文档模板、Mermaid图表规范、frontmatter规范、原子化文档命令
  - 每个阶段包含：核心任务→推荐资源（3-5项）→快速操作步骤→注意事项
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 6个阶段每个都有≥3项推荐资源和可执行步骤
  - `human-judgement` TR-8.2: 阶段之间有逻辑递进关系，无循环依赖
  - `human-judgement` TR-8.3: 每个阶段的快速步骤≤5步，可操作性强
- **Notes**: 这是选手最常查阅的章节，要突出"到了这个阶段该做什么、用什么工具"

## [ ] Task 9: 编写作品类型定制资源包章节
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - AI Agent类作品推荐：
    - 必选：多智能体冲突解决库、AGENTS.md规范、角色定义、Spec-driven开发
    - 推荐：提示词萃取系统、MDI MCP服务器、Chaos混沌测试、edge_scenarios测试
    - 参考案例：flexloop Agent框架、提示词萃取系统Pipeline
  - 工具CLI类作品推荐：
    - 必选：cli.py框架、原子写入、IO安全、argbest practices
    - 推荐：process.py进程管理、check-hardcode硬编码检测、ci-check集成
    - 参考案例：ark-cli、check-mermaid.py、docgen.py
  - Web应用类作品推荐：
    - 必选：Flask API模板（ai-code-assistant）、容器化部署
    - 推荐：SG Dashboard静态分析仪表盘、ECharts可视化（参考excellent-works-catalog/dashboard）
    - 参考案例：ai-code-assistant、prompt_extraction UI
  - 文档/知识库类作品推荐：
    - 必选：frontmatter元数据、Markdown处理库、docgen文档生成、generate-nav导航
    - 推荐：Mermaid图表、generate-graph知识图谱、link-check链接维护
    - 参考案例：优秀作品库、knowledge Wiki体系
  - 每类作品包含：推荐资源清单（必选+推荐）、快速启动步骤（5步内）、参考案例链接
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 4类作品每类有≥5项推荐资源
  - `human-judgement` TR-9.2: 每类快速启动步骤≤5步
  - `human-judgement` TR-9.3: 参考案例链接指向真实存在的文件
  - `human-judgement` TR-9.4: 必选资源和推荐资源有明确区分
- **Notes**: 可以用表格形式对比4类作品的资源需求差异

## [ ] Task 10: 编写快速参考卡片与FAQ
- **Priority**: medium
- **Depends On**: Task 8, Task 9
- **Description**:
  - 一页式快速参考卡片：
    - 最常用10+命令（ci-check, check-mermaid, docgen, mermaid-cmd等）
    - 5+关键路径（scripts/lib/, skills/, templates/, apps/等）
    - 3+常见问题（如何添加新脚本？如何写AGENTS.md？如何运行CI检查？）
  - FAQ常见问题：
    - Q: 如何让我的脚本也能被CI检查覆盖？
    - Q: Python模块如何正确导入.agents/scripts/lib/下的库？
    - Q: Mermaid图表在某些平台不显示怎么办？
    - Q: 如何提交新的pattern/best-practice到作品库？
    - Q: 容器化构建失败如何排查？
    - Q: pre-commit hooks如何安装？
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 快速参考卡片可在一屏内显示（不超过80行）
  - `human-judgement` TR-10.2: 常用命令可直接复制执行
  - `human-judgement` TR-10.3: FAQ回答简洁（≤5行），有明确的操作步骤
  - `human-judgement` TR-10.4: 关键路径使用可点击的相对路径链接
- **Notes**: 快速参考卡片放在文档最末尾或作为独立的QUICKREF.md

## [ ] Task 11: 最终验证与链接检查
- **Priority**: high
- **Depends On**: Task 7, Task 8, Task 9, Task 10
- **Description**:
  - 运行check-mermaid.py验证所有Mermaid图表
  - 运行check-links.py验证所有内部链接
  - 通读全文检查术语一致性、路径准确性
  - 检查代码示例的语法正确性
  - 验证所有文件位于playground/semi-final-support/下
  - 确认git status仅新增目标目录文件
- **Acceptance Criteria Addressed**: [AC-6, AC-7, AC-9]
- **Test Requirements**:
  - `programmatic` TR-11.1: check-mermaid.py结果0错误0警告
  - `programmatic` TR-11.2: check-links.py结果0死链（内部路径）
  - `programmatic` TR-11.3: Python代码示例通过语法检查
  - `programmatic` TR-11.4: git diff显示仅新增playground/semi-final-support/目录文件
  - `human-judgement` TR-11.5: 通读全文语言通顺、结构清晰、术语一致
- **Notes**: 这是质量门禁任务，所有其他任务完成后执行
