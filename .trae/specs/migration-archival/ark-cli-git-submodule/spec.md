# ark-cli Git 子模块集成 - Product Requirement Document

## Overview
- **Summary**: 将火山引擎 ark-cli 仓库 (`git@github.com:volcengine/ark-cli.git`) 作为 Git 子模块集成到 SpecWeave 项目的 `vendor/ark-cli` 目录，遵循项目现有的 vendor 子模块管理规范，完成子模块添加、元数据更新、配置提交和验证全流程。
- **Purpose**: 将 ark-cli 源码纳入项目版本控制体系，便于团队统一管理依赖版本、离线查阅源码、在 IDE Agent 环境中可靠调用 CLI 工具，替代全局 npm 安装方式带来的版本不一致问题。
- **Target Users**: SpecWeave 项目开发者、IDE Agent 智能体、需要使用 ark-cli 的团队成员。

## Goals
- 在 `vendor/ark-cli` 路径下正确添加 ark-cli 作为 Git 子模块
- 子模块配置正确写入 `.gitmodules`，包含 path、url、branch 信息
- ark-cli 子模块正确初始化并可通过标准 git submodule 命令更新
- 更新 vendor 区域元数据文件（AGENTS.md 路由表、README.md 依赖清单、VERSION.md 版本记录）
- 子模块相关变更（.gitmodules、gitlink、元数据）已暂存，可提交

## Non-Goals (Out of Scope)
- 不在本任务中修改 ark-cli 源码（ark-cli 为 third_party 只读依赖）
- 不在本任务中构建或编译 ark-cli
- 不在本任务中配置 ark-cli 的认证凭据（SSO 登录为运行时配置，不入库）
- 不创建 vendor/ark-cli/AGENTS.md（第三方依赖无需自有路由体系）
- 不执行最终的 git commit（提交由用户确认后执行）

## Background & Context
- SpecWeave 项目已有 vendor 目录管理外部依赖，现有一个 owned_collab 类型子模块 flexloop
- vendor 区域已有成熟的管理规范：`.agents/VENDOR-INTEGRATION.md`、`vendor/AGENTS.md`、`vendor/README.md`、`vendor/VERSION.md`
- ark-cli 是火山引擎方舟大模型平台的官方 CLI 工具，托管在 GitHub，通过 SSH 协议访问
- ark-cli 为第三方开源项目，SpecWeave 不直接参与其开发，故分类为 **third_party**（第三方只读），而非 owned_collab
- 注意：用户原始描述中"确保 vendor 目录已存在且为空"为表述歧义——vendor 目录已存在且包含 flexloop 子模块和元数据文件，**不能清空**。实际目标是确保 `vendor/ark-cli` 目标路径不存在（为空）。

## Functional Requirements
- **FR-1**: 执行 `git submodule add` 将 ark-cli 仓库添加到 `vendor/ark-cli` 路径
- **FR-2**: `.gitmodules` 文件自动/手动配置正确的 path、url、branch 字段
- **FR-3**: 子模块正确初始化，工作区包含完整的 ark-cli 源码
- **FR-4**: 更新 `vendor/AGENTS.md` 子模块路由表，登记 ark-cli 条目
- **FR-5**: 更新 `vendor/README.md` 依赖清单，添加 ark-cli 行
- **FR-6**: 更新 `vendor/VERSION.md` 版本清单，添加 ark-cli 版本记录和引入日期
- **FR-7**: 验证子模块状态正常（`git submodule status` 显示正确 commit）
- **FR-8**: 暂存所有子模块相关变更（.gitmodules、vendor/ark-cli gitlink、元数据文件）

## Non-Functional Requirements
- **NFR-1**: 子模块添加过程不影响现有 flexloop 子模块的状态
- **NFR-2**: 元数据更新遵循现有文件的 TOML frontmatter 和 Markdown 表格格式
- **NFR-3**: 所有路径引用使用正确的相对路径格式，与现有风格一致
- **NFR-4**: 操作可复现，其他开发者克隆仓库后通过 `git submodule update --init` 即可获取完整依赖

## Constraints
- **Technical**: 
  - 必须使用 SSH 协议 URL (`git@github.com:volcengine/ark-cli.git`)
  - 子模块路径固定为 `vendor/ark-cli`
  - 遵循现有 vendor 规范，ark-cli 分类为 third_party（第三方只读）
  - Windows 环境，注意路径分隔符和 Git for Windows 兼容性
- **Business**: 
  - 不修改 vendor 内已有 flexloop 相关内容
  - 不直接修改 ark-cli 子模块内的任何文件
- **Dependencies**:
  - Git 已安装且配置了 GitHub SSH 密钥（用于克隆）
  - 现有 `.gitmodules` 和 vendor 元数据文件已存在

## Assumptions
- 用户已配置 GitHub SSH 访问权限，可克隆 `git@github.com:volcengine/ark-cli.git`
- ark-cli 仓库公开可访问（公共仓库）
- 当前工作区干净（除了已知的 docs/knowledge 未跟踪文件，不影响 vendor 操作）
- ark-cli 默认分支为 main 或 master，`git submodule add` 会自动检出默认分支

## Acceptance Criteria

### AC-1: 子模块成功添加到 vendor/ark-cli
- **Given**: SpecWeave 仓库根目录，vendor 目录已存在且无 ark-cli 子目录
- **When**: 执行 `git submodule add git@github.com:volcengine/ark-cli.git vendor/ark-cli`
- **Then**: vendor/ark-cli 目录存在且包含 ark-cli 源码，.gitmodules 包含 ark-cli 条目
- **Verification**: `programmatic`
- **Notes**: 如目录已存在需先清理

### AC-2: .gitmodules 配置正确
- **Given**: 子模块已添加
- **When**: 检查 .gitmodules 文件内容
- **Then**: 包含 path=vendor/ark-cli、url=git@github.com:volcengine/ark-cli.git 的正确配置
- **Verification**: `programmatic`

### AC-3: 子模块状态正常
- **Given**: 子模块已添加并初始化
- **When**: 执行 `git submodule status vendor/ark-cli`
- **Then**: 输出以 commit hash 开头（无前缀 `-` 或 `+` 表示未初始化/有修改），状态正常
- **Verification**: `programmatic`

### AC-4: vendor/AGENTS.md 路由表已更新
- **Given**: 子模块添加完成
- **When**: 检查 vendor/AGENTS.md 子模块路由表
- **Then**: 路由表包含 ark-cli 条目，标注为 third_party 类型，说明为火山引擎方舟 CLI 工具
- **Verification**: `human-judgment`

### AC-5: vendor/README.md 依赖清单已更新
- **Given**: 子模块添加完成
- **When**: 检查 vendor/README.md 依赖清单表格
- **Then**: 表格包含 ark-cli 行，字段正确（版本、类型 third_party、引入日期 2026-07-07、用途说明）
- **Verification**: `human-judgment`

### AC-6: vendor/VERSION.md 版本记录已更新
- **Given**: 子模块添加完成
- **When**: 检查 vendor/VERSION.md 版本表格和更新记录
- **Then**: 版本表格包含 ark-cli 行（commit hash、来源、日期、许可证待确认、类型 third_party、跟踪分支），更新记录有 2026-07-07 引入条目
- **Verification**: `human-judgment`

### AC-7: 所有变更已正确暂存
- **Given**: 所有元数据更新完成
- **When**: 执行 `git status` 和 `git diff --cached`
- **Then**: .gitmodules、vendor/ark-cli gitlink、vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md 均已暂存，无意外修改
- **Verification**: `programmatic`

### AC-8: 不影响现有 flexloop 子模块
- **Given**: 操作前后
- **When**: 对比 vendor/flexloop 状态
- **Then**: vendor/flexloop 的 gitlink 未变化，.gitmodules 中 flexloop 条目保持不变
- **Verification**: `programmatic`

## Open Questions
- [ ] ark-cli 的默认分支是 main 还是 master？（执行时自动检测）
- [ ] ark-cli 的开源许可证是什么？（集成时通过源码 LICENSE 文件确认，初始标注"待确认"）
