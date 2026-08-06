---
id: awesome-okf-vendor-migration
---
# awesome-okf 迁移到 vendor/ 作为 Git 子模块 - Product Requirement Document

## Overview
- **Summary**: 将当前位于根目录 `awesome-okf/` 的第三方开源项目（来自 https://github.com/yzfly/awesome-okf.git）正确迁移到 `vendor/awesome-okf/` 路径下，作为 **third_party** 类型的 Git 子模块进行管理。同步更新 vendor 区域元数据（AGENTS.md 路由表、README.md 依赖清单、VERSION.md 版本记录），并修复主权区文档中所有指向旧路径 `d:/AI/awesome-okf/` 的 `file:///` 绝对链接。
- **Purpose**: 修复架构边界违反问题——awesome-okf 是第三方外部依赖，不应直接放在根目录下（违反四区域架构规范）。通过 git submodule 管理可固定版本、明确所有权边界（第三方只读）、符合 vendor 区域治理规范、通过 `check-vendor.py` 合规检测。
- **Target Users**: SpecWeave 项目开发者、IDE Agent 智能体。

## Goals
- 将根目录 `awesome-okf/` 迁移到 `vendor/awesome-okf/`，正确配置为 Git 子模块
- `.gitmodules` 中正确配置 awesome-okf 条目（path、url、branch）
- 子模块正确初始化并固定到当前 commit（730e6ff 或相近版本，保持与现有分析文档一致）
- 更新 `vendor/AGENTS.md` 子模块路由表，登记 awesome-okf 为 third_party
- 更新 `vendor/README.md` 依赖清单，添加 awesome-okf 条目
- 更新 `vendor/VERSION.md` 版本记录，添加 awesome-okf 引入信息
- 修复主权区文档中所有 `file:///d:/AI/awesome-okf/` 绝对路径引用为 `file:///d:/AI/vendor/awesome-okf/`
- 所有变更正确暂存，不执行最终 commit（提交由用户确认后执行）

## Non-Goals (Out of Scope)
- 不修改 awesome-okf 源码内的任何文件（third_party 只读依赖）
- 不更新 awesome-okf 到最新版本（固定当前 shallow clone 的 commit）
- 不创建 vendor/awesome-okf/AGENTS.md（第三方项目无需自有路由体系）
- 不执行最终的 git commit（提交由用户确认后执行）
- 不重新进行 awesome-okf 的七概念分析（现有分析文档保留，仅更新路径引用）
- 不将 awesome-okf 从 shallow clone 转换为完整 clone（保持 depth=1）

## Background & Context
- SpecWeave 项目遵循四区域架构：`.agents/`（规范容器）、`apps/`（内置应用）、`projects/`（第一方子项目）、`vendor/`（第三方依赖）
- vendor 区域已有成熟规范：`.agents/VENDOR-INTEGRATION.md`、`vendor/AGENTS.md`、`vendor/README.md`、`vendor/VERSION.md`
- vendor 目录下已有两个子模块：`vendor/flexloop`（owned_collab 类型）、`vendor/ark-cli`（third_party 类型）
- awesome-okf 是云中江树（yzfly）维护的中文 OKF（Open Knowledge Format）生态项目，包含 7 个零依赖 Python 插件、7 个 Claude Code Skill、3 份扩展提案
- 当前 awesome-okf 直接克隆在根目录 `awesome-okf/`，为 shallow clone（depth=1），当前 commit 约为 730e6ff
- awesome-okf 在根目录 git 中状态为 untracked files（未被追踪），这是错误的放置方式
- 主权区已有对 awesome-okf 的深度案例分析文档（位于 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/awesome-okf-analysis/`），其中包含大量 `file:///d:/AI/awesome-okf/` 绝对路径引用，迁移后需批量更新
- 参考先例：`ark-cli-git-submodule` spec 已完成类似的第三方子模块集成，但本次是**迁移**而非从零添加，需额外处理路径更新和旧目录清理

## Functional Requirements
- **FR-1**: 记录当前 awesome-okf 的 commit hash 和 git 状态，作为迁移基线
- **FR-2**: 删除根目录下的 `awesome-okf/` 目录（因其是 untracked 且不是子模块）
- **FR-3**: 在 `vendor/awesome-okf` 路径下正确执行 `git submodule add` 添加 awesome-okf 子模块
- **FR-4**: 检出子模块到与原来一致的 commit hash（保持分析文档引用的代码版本不变）
- **FR-5**: `.gitmodules` 文件包含正确的 awesome-okf 配置（path=vendor/awesome-okf、url=https://github.com/yzfly/awesome-okf.git、branch=main）
- **FR-6**: 更新 `vendor/AGENTS.md` 子模块路由表，添加 awesome-okf 条目（third_party 类型）
- **FR-7**: 更新 `vendor/README.md` 依赖清单，添加 awesome-okf 行
- **FR-8**: 更新 `vendor/VERSION.md` 版本表格和更新记录
- **FR-9**: 批量修复主权区 Markdown 文档中所有 `file:///d:/AI/awesome-okf/` 为 `file:///d:/AI/vendor/awesome-okf/`
- **FR-10**: 验证子模块状态正常、现有子模块（flexloop、ark-cli、xuanspace）未受影响
- **FR-11**: 暂存所有相关变更

## Non-Functional Requirements
- **NFR-1**: 迁移过程不影响现有三个子模块（vendor/flexloop、vendor/ark-cli、projects/xuanspace）的状态
- **NFR-2**: 子模块保持 shallow clone（depth=1），不获取完整历史
- **NFR-3**: 子模块检出的 commit 与原根目录版本一致，确保分析文档中的代码行号引用仍然有效
- **NFR-4**: 路径更新使用精确字符串替换，不破坏其他内容
- **NFR-5**: 元数据更新遵循现有文件格式，保持表格列数一致
- **NFR-6**: 操作可回滚（迁移前记录状态，出现问题可恢复）

## Constraints
- **Technical**: 
  - awesome-okf 远程 URL 使用 HTTPS 协议（`https://github.com/yzfly/awesome-okf.git`），与现有配置一致
  - 子模块路径固定为 `vendor/awesome-okf`
  - 分类为 **third_party**（第三方只读依赖，来自 yzfly/awesome-okf）
  - Windows 环境，注意路径分隔符和 Git for Windows 兼容性
  - 当前 awesome-okf 是 shallow clone（depth=1），子模块添加后保持 shallow
- **Business**: 
  - 不修改 vendor 内已有 flexloop、ark-cli 相关内容
  - 不直接修改 vendor/awesome-okf/ 内的任何文件
  - 不修改 awesome-okf-analysis 目录下的分析内容本身，仅更新路径引用
- **Dependencies**:
  - Git 已安装且可访问 GitHub（HTTPS 协议，无需 SSH 密钥）
  - 现有 `.gitmodules` 和 vendor 元数据文件已存在
  - 根目录 awesome-okf 当前为 untracked 状态

## Assumptions
- awesome-okf 仓库公开可访问（公共仓库）
- 当前根目录 awesome-okf 的 HEAD commit 为 730e6ff（或相近 SHA），能成功检出
- 主权区文档中所有对 awesome-okf 的文件引用均使用 `file:///d:/AI/awesome-okf/` 格式的绝对路径
- 分析文档中引用的行号在相同 commit 下保持准确
- 删除根目录 awesome-okf/ 是安全的，因为所有分析产出都已存放在主权区 `.agents/` 目录下

## Acceptance Criteria

### AC-1: 旧目录已清理，子模块成功添加到 vendor/awesome-okf
- **Given**: 根目录存在 untracked 的 awesome-okf/ 目录，vendor/ 下无 awesome-okf 子目录
- **When**: 执行迁移流程（记录状态→删除旧目录→git submodule add→检出正确 commit）
- **Then**: (1) 根目录无 awesome-okf/；(2) vendor/awesome-okf/ 存在且为 gitlink（mode 160000）；(3) vendor/awesome-okf/ 内包含 awesome-okf 源码
- **Verification**: `programmatic`
- **Notes**: 如 vendor/awesome-okf 意外存在需先清理

### AC-2: .gitmodules 配置正确
- **Given**: 子模块已添加
- **When**: 检查 .gitmodules 文件内容
- **Then**: 包含 `[submodule "vendor/awesome-okf"]` 条目，path=vendor/awesome-okf、url=https://github.com/yzfly/awesome-okf.git、branch=main
- **Verification**: `programmatic`

### AC-3: 子模块固定到正确 commit，状态正常
- **Given**: 子模块已添加并检出
- **When**: 执行 `git submodule status vendor/awesome-okf`
- **Then**: (1) 输出以 commit hash 开头（无前缀 `-` 或 `+`）；(2) commit hash 与迁移前记录的基线一致
- **Verification**: `programmatic`

### AC-4: vendor/AGENTS.md 路由表已更新
- **Given**: 子模块添加完成
- **When**: 检查 vendor/AGENTS.md 子模块路由表
- **Then**: 路由表包含 awesome-okf 条目，标注为 third_party 类型，AGENTS.md 入口标注"无（第三方项目）"，说明为"中文 OKF 生态项目（开源知识格式工具链与插件集）"
- **Verification**: `human-judgment`

### AC-5: vendor/README.md 依赖清单已更新
- **Given**: 子模块添加完成
- **When**: 检查 vendor/README.md 依赖清单表格
- **Then**: 表格包含 awesome-okf 行，字段正确（版本 main@<short-commit> (子模块)、类型 third_party、引入日期 2026-08-06、用途说明）
- **Verification**: `human-judgment`

### AC-6: vendor/VERSION.md 版本记录已更新
- **Given**: 子模块添加完成
- **When**: 检查 vendor/VERSION.md 版本表格和更新记录
- **Then**: (1) 版本表格包含 awesome-okf 行（完整 commit hash、来源 https://github.com/yzfly/awesome-okf.git、日期 2026-08-06、许可证 MIT、类型 third_party、跟踪分支 main）；(2) 更新记录有 2026-08-06 引入 awesome-okf 子模块的条目
- **Verification**: `human-judgment`

### AC-7: 主权区文档中的 file:/// 路径引用已全部更新
- **Given**: 子模块迁移完成
- **When**: 在主权区（.agents/、.trae/specs/ 等，排除 vendor/ 目录）搜索 `file:///d:/AI/awesome-okf/`
- **Then**: (1) 无任何文件包含旧路径 `file:///d:/AI/awesome-okf/`；(2) 所有原引用已替换为 `file:///d:/AI/vendor/awesome-okf/`；(3) Markdown 链接格式未被破坏
- **Verification**: `programmatic`

### AC-8: 现有子模块未受影响
- **Given**: 迁移前后
- **When**: 对比 vendor/flexloop、vendor/ark-cli、projects/xuanspace 的 gitlink 状态
- **Then**: 三个现有子模块的 gitlink 未变化，.gitmodules 中对应条目保持不变
- **Verification**: `programmatic`

### AC-9: 所有变更已正确暂存
- **Given**: 所有更新完成
- **When**: 执行 `git status` 和 `git diff --cached --name-only`
- **Then**: (1) .gitmodules 已暂存；(2) vendor/awesome-okf gitlink 已暂存；(3) vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md 元数据更新已暂存；(4) 路径更新的主权区文档已暂存；(5) 无意外暂存内容
- **Verification**: `programmatic`

### AC-10: check-vendor.py 合规检测通过
- **Given**: 所有变更暂存后
- **When**: 运行 `python .agents/scripts/check-vendor.py --deep`
- **Then**: 脚本执行无错误，awesome-okf 被正确识别为合规的 third_party 子模块
- **Verification**: `programmatic`

## Open Questions
- [ ] 当前 awesome-okf 的 LICENSE 是否为 MIT？（从源码确认，初始推测为 MIT）
- [ ] awesome-okf 是否需要配置 `shallow = true` 在 .gitmodules 中以保持浅克隆？
