# XMNN 项目结构优化 - Product Requirement Document

## Overview
- **Summary**: 对 xmnn 项目进行全面复盘和结构优化，识别并消除重复内容，重新规划目录层次以提高可维护性和可扩展性
- **Purpose**: 解决当前项目中存在的文档冗余、脚本分散、构建产物混杂等问题，使项目结构符合行业最佳实践
- **Target Users**: 开发团队、AI Agent、运维人员

## Goals
- 消除重复的文档和配置文件
- 统一脚本管理，避免功能重复
- 分离构建产物与源代码
- 建立清晰的目录层次和职责边界
- 提高项目可维护性和可扩展性

## Non-Goals (Out of Scope)
- 修改核心业务逻辑代码
- 变更构建流水线
- 修改第三方依赖版本
- 创建新功能

## Background & Context
当前 xmnn 项目结构存在以下问题：
1. **文档冗余**: `docs/` 目录下存在多个重复的部署指南（如 `DEPLOYMENT_GUIDE.md` 和 `deployment-guide.md`）
2. **脚本分散**: `scripts/` 和 `client/scripts/` 中存在功能重复的验证脚本
3. **构建产物混杂**: `docker/runtime-build/` 包含大量二进制文件和 .so 库，与源代码混杂
4. **临时文件未清理**: `client/.temp/` 和 `client/sdk/temp/` 包含不应提交的临时文件
5. **调试脚本位置不当**: `.agents/` 目录中混入了调试脚本

## Functional Requirements
- **FR-1**: 识别并合并重复文档，保留一份权威版本
- **FR-2**: 统一脚本管理，消除功能重复的脚本
- **FR-3**: 将构建产物移至独立的输出目录，与源代码分离
- **FR-4**: 清理不应提交的临时文件
- **FR-5**: 将调试脚本移至合适位置

## Non-Functional Requirements
- **NFR-1**: 优化后的结构符合行业最佳实践（如标准 Python 项目布局）
- **NFR-2**: 目录层次清晰，职责明确
- **NFR-3**: 所有变更必须保持功能等价，无回归风险
- **NFR-4**: 更新后的文档和脚本必须可验证

## Constraints
- **Technical**: 不能破坏现有的构建流程和脚本调用关系
- **Business**: 保持与父项目 xmhub 的目录约定兼容性
- **Dependencies**: 所有变更需经过测试验证

## Assumptions
- 当前项目的核心功能正常运行
- Git 历史记录需要保留（使用移动而非删除）

## Acceptance Criteria

### AC-1: 文档冗余消除
- **Given**: `docs/` 目录存在重复文档
- **When**: 执行文档合并和清理
- **Then**: 每个主题只保留一份权威文档，所有交叉引用更新为指向新位置
- **Verification**: `human-judgment`

### AC-2: 脚本统一管理
- **Given**: `scripts/` 和 `client/scripts/` 存在功能重复的脚本
- **When**: 执行脚本整合
- **Then**: 功能相同的脚本合并为一个，消除重复实现
- **Verification**: `human-judgment`

### AC-3: 构建产物分离
- **Given**: `docker/runtime-build/` 包含构建产物
- **When**: 将构建产物移至独立输出目录
- **Then**: 源代码目录不包含二进制构建产物
- **Verification**: `programmatic`

### AC-4: 临时文件清理
- **Given**: `client/.temp/` 和 `client/sdk/temp/` 存在临时文件
- **When**: 更新 `.gitignore` 并清理临时文件
- **Then**: 临时文件不再提交到版本控制
- **Verification**: `programmatic`

### AC-5: 调试脚本整理
- **Given**: `.agents/` 目录包含调试脚本
- **When**: 将调试脚本移至专用工具目录
- **Then**: `.agents/` 目录只包含 AI Agent 配置文档
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要保留 `docker/runtime-build/` 中的旧版本构建产物？
- [ ] `client/sdk/temp/` 中的模型编译产物是否为必需的测试数据？