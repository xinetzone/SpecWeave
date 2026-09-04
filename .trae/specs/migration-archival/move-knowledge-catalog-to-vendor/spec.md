# 将 knowledge-catalog 移动到 vendor 作为 git 子模块 - 产品需求文档

## Overview
- **Summary**: 将当前位于 `d:\AI\.chaos\libs\knowledge-catalog` 的 Google Cloud Knowledge Catalog 仓库移动到 `d:\AI\vendor\knowledge-catalog`，并将其配置为 SpecWeave 项目的第三方 git 子模块（third_party 类型），同时更新相关路由配置和索引文件。
- **Purpose**: 遵循 SpecWeave 项目目录结构规范，将第三方依赖统一放置在 vendor/ 目录下管理，与现有的 flexloop、ark-cli 等子模块保持一致的管理方式。
- **Target Users**: SpecWeave 项目开发者、维护者，需要引用 knowledge-catalog 的 AI 智能体和脚本。

## Goals
- 将 `d:\AI\.chaos\libs\knowledge-catalog` 移动到 `d:\AI\vendor\knowledge-catalog`
- 将 knowledge-catalog 配置为 git 子模块，远程地址为 `git@github.com:GoogleCloudPlatform/knowledge-catalog.git`
- 更新 vendor/AGENTS.md 的子模块路由表，添加 knowledge-catalog 条目
- 更新 vendor/README.md 依赖清单（如需）
- 确保移动后所有现有引用路径正确更新（如有）
- 验证子模块正常工作，能够正常拉取和更新

## Non-Goals (Out of Scope)
- 不修改 knowledge-catalog 仓库内部的任何文件（作为第三方依赖，禁止本地修改）
- 不将 knowledge-catalog 升级到新版本（保持当前 commit 930b65f 不变）
- 不修改 knowledge-catalog 的远程仓库配置
- 不进行任何功能开发或代码修改（仅目录移动和配置）
- 不删除原始目录 `.chaos/libs/knowledge-catalog` 直到验证完成（安全回滚考虑）

## Background & Context
- 当前 knowledge-catalog 位于 `.chaos/libs/` 目录下，该目录是临时/混沌开发区域，不符合 SpecWeave 第三方依赖的管理规范
- SpecWeave 项目使用 vendor/ 目录统一管理 git 子模块形式的第三方依赖，已有 flexloop（owned_collab）和 ark-cli（third_party）作为先例
- knowledge-catalog 是 Google 官方的开源项目，采用 Apache 2.0 许可证，属于第三方只读依赖
- 项目已有成熟的子模块引入流程，参考 vendor/AGENTS.md 和 .agents/VENDOR-INTEGRATION.md
- 当前 knowledge-catalog 工作区干净，在 main 分支，与 origin/main 同步，最新 commit 为 930b65f

## Functional Requirements
- **FR-1**: 将 knowledge-catalog 作为 third_party 类型的 git 子模块添加到 vendor/knowledge-catalog
- **FR-2**: 子模块固定在当前 commit 930b65f，不跟踪分支（与 ark-cli 一致）
- **FR-3**: 更新 .gitmodules 文件，添加 knowledge-catalog 子模块配置
- **FR-4**: 更新 vendor/AGENTS.md 的子模块路由表，登记 knowledge-catalog 条目
- **FR-5**: 验证子模块初始化正常，能够通过 `git submodule update --init` 正确拉取
- **FR-6**: 检查代码库中是否有对旧路径 `.chaos/libs/knowledge-catalog` 的引用，如有则更新（注：根据最近记忆，knowledge-catalog-wiki 是文档引用，不直接引用本地路径，需验证）

## Non-Functional Requirements
- **NFR-1**: 操作过程必须安全可回滚，在验证通过前保留原始目录
- **NFR-2**: 所有配置文件更新必须遵循现有格式和风格
- **NFR-3**: 子模块添加后不影响现有其他子模块的正常使用
- **NFR-4**: 整个过程不修改 knowledge-catalog 内部的任何文件，保持第三方依赖只读原则

## Constraints
- **Technical**: 必须使用标准 git submodule 命令；Windows 平台环境；遵循项目已有的子模块管理规范
- **Business**: 无特殊时间要求，需保证质量；不引入新的依赖
- **Dependencies**: 依赖 git 命令可用；依赖 GitHub 仓库可访问（已有访问权限，当前已克隆）

## Assumptions
- knowledge-catalog 作为第三方依赖，类型为 third_party（只读，不跟踪分支），与 ark-cli 一致
- 当前 `.chaos/libs/knowledge-catalog` 目录中的内容与远程 origin/main 在 commit 930b65f 完全一致，无本地修改
- 代码库中对 knowledge-catalog 的引用主要是文档链接，不直接引用本地文件路径
- 移动完成后，原始目录可以在验证通过后删除
- 用户希望遵循 vendor 区域规范，禁止修改 vendor 内子模块内容

## Acceptance Criteria

### AC-1: 子模块正确添加到 vendor/knowledge-catalog
- **Given**: 项目根目录为 d:\AI，knowledge-catalog 已从 GitHub 克隆
- **When**: 执行 git submodule add 并完成配置
- **Then**: vendor/knowledge-catalog 目录存在，是有效的 git 子模块，.gitmodules 包含正确条目
- **Verification**: `programmatic`
- **Notes**: 验证方法：运行 `git submodule status` 显示 knowledge-catalog，.gitmodules 中 path=vendor/knowledge-catalog，url=git@github.com:GoogleCloudPlatform/knowledge-catalog.git

### AC-2: vendor/AGENTS.md 路由表更新
- **Given**: vendor/AGENTS.md 现有子模块路由表
- **When**: 添加 knowledge-catalog 条目
- **Then**: 子模块路由表包含 knowledge-catalog 条目，类型标记为 third_party，AGENTS.md 入口标注"无（第三方项目）"
- **Verification**: `human-judgment`
- **Notes**: 条目格式与 ark-cli 保持一致

### AC-3: 子模块可正常初始化和更新
- **Given**: 子模块已添加
- **When**: 运行 `git submodule update --init vendor/knowledge-catalog`
- **Then**: 命令成功执行，vendor/knowledge-catalog 目录内容完整，HEAD 指向 930b65f
- **Verification**: `programmatic`

### AC-4: 不修改 knowledge-catalog 内部文件
- **Given**: 原始 knowledge-catalog 仓库
- **When**: 完成移动和子模块添加
- **Then**: vendor/knowledge-catalog 内的文件与原始目录完全一致，git status 在子模块内显示 clean
- **Verification**: `programmatic`
- **Notes**: 使用目录比较或 git diff 验证

### AC-5: 现有功能不受影响
- **Given**: 添加子模块前项目状态正常
- **When**: 完成子模块添加
- **Then**: 现有子模块（flexloop、ark-cli、xuanspace）状态正常，git status 在主仓库显示预期变更
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在添加子模块后立即删除原始目录 `.chaos/libs/knowledge-catalog`，还是保留一段时间？（建议保留直到验证通过，由用户确认后删除）
- [ ] knowledge-catalog 是否需要跟踪特定分支（类似 flexloop 跟踪 main），还是固定 commit（类似 ark-cli）？（根据第三方依赖性质，建议固定 commit，等待用户确认）
