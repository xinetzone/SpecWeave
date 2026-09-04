# XMNN 项目结构优化 - Implementation Plan

## [x] Task 1: 分析重复文档并制定合并策略
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 分析 `docs/` 目录下的所有文档，识别重复或重叠内容
  - 对比 `DEPLOYMENT_GUIDE.md` 和 `deployment-guide.md`，确定哪一个作为权威版本
  - 检查 `client/docs/` 与 `docs/` 的文档关系
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgment` TR-1.1: 生成重复文档分析报告，列出重复对和合并建议
  - `human-judgment` TR-1.2: 报告中每个重复对都有明确的保留/删除/合并决策

## [x] Task 2: 合并重复文档
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 按分析报告执行文档合并
  - 更新所有交叉引用指向合并后的文档
  - 删除冗余文档（通过 git 移动保留历史）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgment` TR-2.1: 每个主题只保留一份权威文档
  - `human-judgment` TR-2.2: 所有交叉引用正确指向新位置

## [x] Task 3: 整合重复脚本
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 分析 `scripts/` 和 `client/scripts/` 中的脚本，识别功能重复
  - 将重复脚本合并到统一位置（优先保留 `scripts/` 下的版本）
  - 更新引用这些脚本的其他文件
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgment` TR-3.1: 功能相同的脚本已合并为一个
  - `human-judgment` TR-3.2: 所有脚本调用路径更新正确

## [x] Task 4: 分离构建产物
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 将 `docker/runtime-build/` 中的二进制产物移至 `build/output/` 目录
  - 更新 `.gitignore` 排除新的输出目录
  - 更新相关脚本中的路径引用
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: `docker/runtime-build/` 目录下无 .so/.bin/.tar.gz 等二进制文件
  - `programmatic` TR-4.2: 新输出目录已正确添加到 `.gitignore`

## [x] Task 5: 清理临时文件
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 更新 `client/.gitignore` 排除 `.temp/` 和 `sdk/temp/`
  - 清理已提交的临时文件
  - 更新 `client/sdk/.gitignore`（如存在）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: `.gitignore` 正确包含临时文件模式
  - `programmatic` TR-5.2: `git status` 显示无未跟踪的临时文件

## [x] Task 6: 整理调试脚本
- **Priority**: medium
- **Depends On**: None
- **Description**: 
  - 将 `.agents/` 中的调试脚本（`debug_tvm.py`, `test_tvm_fix.py` 等）移至 `tools/` 目录
  - 更新 `.agents/` 索引文档移除对这些脚本的引用
  - 更新引用这些脚本的其他文件
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgment` TR-6.1: `.agents/` 目录只包含 AI Agent 配置文档（.md 文件）
  - `human-judgment` TR-6.2: 调试脚本已移至 `tools/` 目录并可正常运行

## [x] Task 7: 更新项目入口文档
- **Priority**: high
- **Depends On**: Tasks 1-6
- **Description**: 
  - 更新 `README.md` 反映新的目录结构
  - 更新 `AGENTS.md` 的目录导航表
  - 更新 `.agents/architecture.md` 的架构图和目录描述
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `human-judgment` TR-7.1: 入口文档中的目录结构与实际文件系统一致
  - `human-judgment` TR-7.2: 所有导航链接正确指向新位置

## [x] Task 8: 验证与测试
- **Priority**: high
- **Depends On**: Tasks 1-7
- **Description**: 
  - 运行链接检查器验证所有交叉引用
  - 运行构建脚本验证功能等价性
  - 执行回归测试用例
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 链接检查无错误
  - `programmatic` TR-8.2: 核心构建流程正常运行
  - `programmatic` TR-8.3: 回归测试用例全部通过