---
id: "establish-four-region-routing-system-tasks"
version: "1.0"
---
# 建立四大区域路由体系 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建 apps/.agents/ 元数据容器
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `apps/.agents/` 目录
  - 创建 `apps/.agents/README.md` 作为 apps 区域元数据容器说明文档
  - 参照 projects/.agents/README.md 和 vendor/.agents/README.md 的模式
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: apps/.agents/ 目录存在
  - `programmatic` TR-1.2: apps/.agents/README.md 文件存在且包含 YAML frontmatter
- **Notes**: 先创建目录结构，后续再完善内容

## [x] Task 2: 创建 apps/AGENTS.md 区域入口文档
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 参照 projects/AGENTS.md 和 vendor/AGENTS.md 的结构创建 apps/AGENTS.md
  - 包含以下章节：
    1. 区域性质（明确 apps 是主仓库内应用，可直接修改，区别于 projects 的 submodule 模式）
    2. 应用路由表（列出所有现有应用）
    3. 嵌套优先级（根 AGENTS → apps/AGENTS → 应用自身 AGENTS）
    4. 路由流程图（Mermaid 格式）
    5. 可用资产索引（如有）
    6. 边界声明表格
    7. 跨应用调用规范
    8. 异常处理分支
    9. 新增应用说明
  - 添加正确的 YAML frontmatter（id, version, source）
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: apps/AGENTS.md 文件存在
  - `programmatic` TR-2.2: 包含所有必需章节（区域性质、路由表、嵌套优先级、流程图、资产索引、边界声明、调用规范、异常处理）
  - `human-judgement` TR-2.3: 章节结构与 projects/AGENTS.md、vendor/AGENTS.md 对称一致
  - `human-judgement` TR-2.4: 明确区分了 apps 与 projects/vendor 的本质差异
  - `programmatic` TR-2.5: 应用路由表包含所有现有 apps 子目录
- **Notes**: 路由表应包含：ai-code-assistant、camera-power-controller、docker-ssh-dind、jupyter-ssh-base、prompt_extraction、pytorch-base、shared、tests、xmnn-runtime、zhujian-wudao

## [x] Task 3: 更新 apps/README.md 添加智能体入口引用
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 在 apps/README.md 顶部（标题之后、"一、用途与定位"之前）添加智能体入口说明
  - 添加指向 AGENTS.md 的引用，类似于 projects/README.md 和 vendor/README.md 的模式
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: apps/README.md 顶部包含 AGENTS.md 入口引用
  - `human-judgement` TR-3.2: 引用位置和格式与 projects/README.md 风格一致

## [x] Task 4: 更新根 AGENTS.md - 添加四大区域对比表
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在根 AGENTS.md 中添加「四大顶层区域」章节或表格
  - 位置建议：在「核心规范入口」表格之前，或在「开发规范」之前
  - 表格包含：目录、用途、维护方式、版本控制、是否可直接修改、AGENTS.md 入口
  - 对比 .agents/（规范容器）、apps/（应用区）、projects/（第一方子项目）、vendor/（第三方依赖）
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 根 AGENTS.md 中存在四大区域对比表
  - `human-judgement` TR-4.2: 表格内容清晰，新人 30 秒内能理解区域区别
  - `programmatic` TR-4.3: 表格中包含三个区域的 AGENTS.md 链接

## [x] Task 5: 更新根 AGENTS.md - 重构启动协议步骤 2.1
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 重构根 AGENTS.md 启动协议的步骤 2.1，从仅判断 vendor/ 扩展为通用区域路由判断
  - 判断顺序：先检查 apps/，再检查 projects/，最后检查 vendor/
  - 添加统一的区域路由流程图（Mermaid 格式），展示三层路由体系：
    - 根 AGENTS.md（主权区）
    - 子区域 AGENTS.md（apps/projects/vendor）
    - 子应用/子项目 AGENTS.md（如有）
  - 更新步骤 3.5 自检清单，添加对 apps/projects 区域的检查项
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `human-judgement` TR-5.1: 启动协议步骤 2.1 完整覆盖三个子区域
  - `programmatic` TR-5.2: 步骤中包含 apps/AGENTS.md、projects/AGENTS.md、vendor/AGENTS.md 的引用
  - `human-judgement` TR-5.3: 路由流程图清晰展示三层嵌套结构
  - `programmatic` TR-5.4: 自检清单包含对 apps/projects 的检查项

## [x] Task 6: 更新根 AGENTS.md - 在核心规范入口表添加区域入口
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**: 
  - 在核心规范入口表格中添加三个区域入口条目：
    - 📱 应用区入口（apps/AGENTS.md）
    - 📦 第一方子项目入口（projects/AGENTS.md）
    - 📦 第三方依赖入口（vendor/AGENTS.md）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 核心规范入口表包含三个区域 AGENTS.md 的链接

## [x] Task 7: 更新 .agents/context-routing.md 添加 apps 入口
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 在常规任务路由表中添加 apps 区域相关条目：
    - apps 区域入口路由 → apps/AGENTS.md
    - 应用开发生命周期 → protocols/app-development-workflow.md
  - 位置：在 projects 区域入口条目附近
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: .agents/context-routing.md 中包含 apps/AGENTS.md 条目
  - `programmatic` TR-7.2: 条目中包含 app-development-workflow.md 的引用

## [x] Task 8: 链接验证与一致性检查
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 5, Task 6, Task 7
- **Description**: 
  - 运行链接检查脚本验证所有新增和修改的链接
  - 检查所有相对路径引用是否正确
  - 检查三个区域 AGENTS.md 的结构对称性
  - 验证 Mermaid 图表语法正确
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-8.1: 运行 `python .agents/scripts/check-links.py --path AGENTS.md --path apps/ --path .agents/context-routing.md` 无断链错误
  - `human-judgement` TR-8.2: 三个区域 AGENTS.md 的章节结构对称一致
  - `programmatic` TR-8.3: Mermaid 图表可正常渲染（无语法错误）
- **Notes**: 如发现断链，修复后重新验证

## [x] Task 9: 原子提交
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 使用 atomic-commit-cmd 进行原子提交
  - 提交信息遵循 Conventional Commits 规范：`feat(governance): 建立四大区域路由体系，补全 apps/AGENTS.md 入口`
- **Acceptance Criteria Addressed**: 所有 AC
- **Test Requirements**:
  - `programmatic` TR-9.1: 提交成功，单一职责（commit db3848d5，8 files changed, 630 insertions, 19 deletions）
  - `programmatic` TR-9.2: git status 显示我们提交的文件已提交（其他未暂存文件属于历史遗留，不在本次范围）
