# book-to-skill Wiki 教程 - 实施计划

## [x] Task 1: 生成 00-overview.md 总览章节
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 介绍book-to-skill是什么、解决什么问题
  - 核心价值主张（24×-51× token节省）
  - wiki导航结构
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于正确路径 ✓
  - `human-judgement` TR-1.2: 清晰说明项目定位和价值 ✓

## [x] Task 2: 生成 01-core-architecture.md 架构解析章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 双层架构图（Python提取器 + SKILL.md规范驱动生成器）
  - 组件职责表
  - 数据流：文档 → 提取 → 分析 → 生成Skill
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在 ✓
  - `human-judgement` TR-2.2: 架构描述与代码一致，引用正确文件路径 ✓

## [x] Task 3: 生成 02-extractor-deep-dive.md 提取器深度解析
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 格式支持矩阵和提取器优先级链
  - 多语言章节检测机制（7种语言+罗马数字）
  - 依赖探测和优雅降级策略
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在 ✓
  - `human-judgement` TR-3.2: 提取器逻辑描述与utils.py/dependencies.py一致 ✓

## [x] Task 4: 生成 03-skill-md-spec.md SKILL.md生成规范
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 4种操作模式详解
  - 10步生成流程
  - Token预算矩阵（BOOK_TYPE × DEPTH）
  - 文件结构和模板（SKILL.md/章节/glossary/patterns/cheatsheet）
  - 更新/折叠工作流
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在 ✓
  - `human-judgement` TR-4.2: 生成规范与SKILL.md定义一致 ✓

## [x] Task 5: 生成 04-token-economics.md Token经济学与性能
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - Discovery Loop Tax原理
  - 性能基准数据
  - 与上下文dump、RAG的对比
  - 大书REPL式访问策略
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在 ✓
  - `human-judgement` TR-5.2: 性能数据与README一致 ✓

## [x] Task 6: 生成 05-security-model.md 安全模型
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 文档→Agent供应链攻击面分析
  - 5层防御体系详细解析
  - 每层对应的代码实现
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在，覆盖5层防御 ✓
  - `human-judgement` TR-6.2: 安全机制与代码一致 ✓

## [x] Task 7: 生成 06-installation-usage.md 安装与使用
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 两种安装方式（作为Agent Skill git clone / 作为独立CLI pip install）
  - Skill位置优先级表
  - 基本使用示例
  - --check环境预检
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在 ✓
  - `human-judgement` TR-7.2: 安装步骤准确可执行 ✓（已修复git URL占位符）

## [x] Task 8: 生成 07-extending-development.md 扩展开发
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 新增格式支持步骤
  - 新增生成行为步骤
  - 工具脚本说明（discovery_tax.py、validate_skill.py、scan_generated_skill.py）
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在 ✓
  - `human-judgement` TR-8.2: 扩展指南与ARCHITECTURE.md一致 ✓

## [x] Task 9: 生成 08-transferable-patterns.md 可复用模式
- **Priority**: high
- **Depends On**: Task 2, Task 5, Task 6
- **Description**:
  - 模式1：编译时付费架构（Compile-time Payment Architecture）
  - 模式2：规范驱动生成（Spec-driven Generation）
  - 模式3：文档供应链安全分层防御
  - 模式4：优雅降级与依赖探测
  - 模式5：Token预算自适应矩阵
  - 每个模式包含：触发场景、核心步骤、反模式、迁移示例
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在，每个模式包含要求的4个部分 ✓
  - `human-judgement` TR-9.2: 至少3个模式可直接迁移到SpecWeave ✓（5个模式均可迁移）

## [x] Task 10: 生成 09-summary-faq.md 总结与FAQ
- **Priority**: medium
- **Depends On**: Task 1-9
- **Description**:
  - 核心要点总结
  - 常见问题解答
  - 延伸阅读资源
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在 ✓
  - `human-judgement` TR-10.2: FAQ覆盖常见疑问 ✓

## [x] Task 11: 验证所有代码引用链接可访问
- **Priority**: high
- **Depends On**: Task 1-10
- **Description**:
  - 检查所有file:///链接指向正确文件
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-11.1: 所有链接有效 ✓（修复了09-summary-faq.md中6个路径错误链接）
