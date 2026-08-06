---
id: okf-libs-vendor-migration
---
# 将 .chaos/libs 下三个 OKF 目录迁移为 vendor git 子模块 - Product Requirement Document

## Overview
- **Summary**: 将 `d:\AI\.chaos\libs\` 下的三个 OKF 相关第三方开源仓库（`awesome-okf`、`awesome-okf-kit`、`okf-bundle-template`）迁移到 `d:\AI\vendor\` 路径下，作为 **third_party** 类型的 Git 子模块管理。同步更新 vendor 区域元数据（AGENTS.md 路由表、README.md 依赖清单、VERSION.md 版本记录），并修复主权区文档中指向上游目录的失效相对链接。
- **Purpose**: 修复架构边界问题——这三个目录是第三方外部开源依赖（各自拥有独立 `.git`），不应存放在 `.chaos/libs/` 未纳入主仓库版本控制的区域。通过 `git submodule` 管理可固定版本、明确所有权边界（第三方只读）、符合 vendor 区域治理规范、通过 `check-vendor.py` 合规检测。
- **Target Users**: SpecWeave 项目开发者、IDE Agent 智能体。

## 上游来源与命名映射
由于 `vendor/awesome-okf` 已存在且指向**不同仓库**（`git@github.com:yzfly/awesome-okf.git`），本次迁移三个源仓库时，首个 `awesome-okf` 采用**独立路径**避免命名冲突（用户已确认）：

| 源路径（.chaos/libs/） | 上游仓库 | 目标子模块路径 | HEAD commit | 主分支 | 许可证 |
|---|---|---|---|---|---|
| `awesome-okf` | `git@github.com:linyiru/awesome-okf.git` | `vendor/awesome-okf-bundle` | `ebe906b71fbf68b0b1ecbba58bdad1b4605b297f` | main | CC0-1.0 |
| `awesome-okf-kit` | `git@github.com:vinodborole/awesome-okf-kit.git` | `vendor/awesome-okf-kit` | `5e862eeb8af32595884fe4147faee0deb86fb52b` | main | MIT |
| `okf-bundle-template` | `git@github.com:vinodborole/okf-bundle-template.git` | `vendor/okf-bundle-template` | `a0883c7bb125efe79b0efaeb8cbd0484abfbd7f5` | main | 待确认（无 LICENSE，含 NOTICE.md） |

## Goals
- 将三个源目录从 `.chaos/libs/` 迁移到 `vendor/` 对应路径，正确配置为 Git 子模块
- `.gitmodules` 中正确配置三条新子模块条目（path、url、branch）
- 三个子模块正确初始化并固定到各自记录的 HEAD commit（保持与现有分析文档一致的代码版本）
- 更新 `vendor/AGENTS.md` 子模块路由表与边界声明，登记三个新子模块为 third_party
- 更新 `vendor/README.md` 依赖清单，添加三个条目
- 更新 `vendor/VERSION.md` 版本记录与更新记录，添加三个条目
- 修复主权区文档中失效的 `.chaos/libs/awesome-okf/` 相对链接（`01-ecosystem-map.md` 中 3 处文件链接）
- **保留现有 `vendor/awesome-okf`（yzfly）子模块不变**
- 所有变更正确暂存，不执行最终 commit（提交由用户确认后执行）

## Non-Goals (Out of Scope)
- 不修改三个源仓库内的任何文件（third_party 只读依赖）
- 不更新三个仓库到最新版本（固定 HEAD commit）
- 不创建 `vendor/<name>/AGENTS.md`（第三方项目无需自有路由体系）
- 不执行最终的 git commit（提交由用户确认后执行）
- 不重新进行三个仓库的七概念分析（现有分析文档保留，仅更新失效路径引用）
- 不删除 `.chaos/libs/` 下除这三个目录以外的其他内容
- 不修改现有 `vendor/awesome-okf`（yzfly）子模块的配置与内容

## Background & Context
- SpecWeave 项目遵循四区域架构：`.agents/`（规范容器）、`apps/`（内置应用）、`projects/`（第一方子项目）、`vendor/`（第三方依赖）
- vendor 区域已有成熟规范与既有子模块：`vendor/flexloop`（owned_collab）、`vendor/ark-cli`（third_party）、`vendor/awesome-okf`（third_party，yzfly）、`vendor/knowledge-catalog`（third_party）
- 三个源目录各自是独立 git 仓库（含 `.git`），但 `.chaos/` 整体**未被主仓库 git 跟踪**（`git ls-files .chaos` 为空），属于游离的外部依赖
- `vendor/awesome-okf`（yzfly/awesome-okf）与 `.chaos/libs/awesome-okf`（linyiru/awesome-okf）是**两个不同项目**——前者是中文 OKF 生态工具链（docs/plugins/skills），后者是含 `bundle/` 构建器与 Awesome 列表的汇总项目，故采用 `vendor/awesome-okf-bundle` 独立路径
- 主权区已有对三者的分析文档位于 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/okf-ecosystem-wiki/`，其中 `01-ecosystem-map.md` 含 3 处对 `.chaos/libs/awesome-okf/` 的相对文件链接，迁移后需更新
- 参考先例：`awesome-okf-vendor-migration` spec 已完成类似的第三方子模块迁移流程，本次迁移类似但源位置不同（`.chaos/libs/` 而非根目录），且为批量三个目录

## Functional Requirements
- **FR-1**: 记录三个源仓库的 HEAD commit、主分支、许可证作为迁移基线
- **FR-2**: 确认三个源目录未被主仓库 git 跟踪，且工作树干净（无本地未提交变更）
- **FR-3**: 删除 `.chaos/libs/` 下三个源目录（因未跟踪）
- **FR-4**: 在 `vendor/` 对应路径执行 `git submodule add -b main <url> vendor/<name>` 添加三个子模块
- **FR-5**: 将每个子模块检出到各自记录的 HEAD commit（保持分析文档引用的代码版本不变）
- **FR-6**: `.gitmodules` 包含三条正确配置（path、url、branch）
- **FR-7**: 更新 `vendor/AGENTS.md` 子模块路由表，添加三个条目（third_party 类型）
- **FR-8**: 更新 `vendor/README.md` 依赖清单，添加三行
- **FR-9**: 更新 `vendor/VERSION.md` 版本表格与更新记录
- **FR-10**: 修复 `01-ecosystem-map.md` 中 3 处 `.chaos/libs/awesome-okf/` 相对文件链接为 `vendor/awesome-okf-bundle/`
- **FR-11**: 验证子模块状态正常、现有子模块（flexloop、ark-cli、awesome-okf、knowledge-catalog、xuanspace）未受影响
- **FR-12**: 暂存所有相关变更

## Non-Functional Requirements
- **NFR-1**: 迁移过程不影响现有五个子模块（vendor/flexloop、vendor/ark-cli、vendor/awesome-okf、vendor/knowledge-catalog、projects/xuanspace）的状态
- **NFR-2**: 三个子模块检出的 commit 与原 `.chaos/libs/` 版本一致，确保分析文档引用有效
- **NFR-3**: 路径更新使用精确字符串替换，不破坏其他内容；`../` 前缀层级保持不变
- **NFR-4**: 元数据更新遵循现有文件格式，保持表格列数一致
- **NFR-5**: 操作可回滚（迁移前记录状态，出现问题可恢复）
- **NFR-6**: 使用 SSH 远程 URL（与现有 `.gitmodules` 中多数条目一致）

## Constraints
- **Technical**:
  - 三个源仓库远程 URL 使用 SSH 协议（`git@github.com:...`），与现有 `.gitmodules` 多数条目一致
  - 子模块路径固定为 `vendor/awesome-okf-bundle`、`vendor/awesome-okf-kit`、`vendor/okf-bundle-template`
  - 分类均为 **third_party**（第三方只读依赖）
  - Windows 环境，注意路径分隔符和 Git for Windows 兼容性
- **Business**:
  - 不修改 vendor 内已有 flexloop、ark-cli、awesome-okf(yzfly)、knowledge-catalog 相关内容
  - 不直接修改三个新子模块内的任何文件
  - 不修改 okf-ecosystem-wiki 分析内容本身，仅更新失效文件链接
- **Dependencies**:
  - Git 已安装且可通过 SSH 访问 GitHub
  - 现有 `.gitmodules` 和 vendor 元数据文件已存在
  - 三个源目录当前为未跟踪状态且工作树干净

## Assumptions
- 三个源仓库公开可访问（公共仓库）
- 记录的 HEAD commit（ebe906b7、5e862eeb、a0883c7b）能成功检出
- 主权区中仅 `01-ecosystem-map.md` 含指向 `.chaos/libs/awesome-okf/` 的文件链接（已确认，其余两个文件仅 frontmatter `source:` 文本描述，无文件链接）
- 删除 `.chaos/libs/` 下三个源目录是安全的，因为相关分析产出已存放在主权区 `.agents/` 目录下
- 现有 `vendor/awesome-okf`（yzfly）与 `vendor/awesome-okf-bundle`（linyiru）可共存，无路径冲突

## Acceptance Criteria

### AC-1: 旧目录已清理，子模块成功添加到 vendor 对应路径
- **Given**: `.chaos/libs/` 下存在三个未跟踪的源目录，vendor/ 下无对应目标目录
- **When**: 执行迁移流程（记录状态→删除源目录→git submodule add→检出正确 commit）
- **Then**: (1) `.chaos/libs/` 下三个源目录已移除；(2) vendor/awesome-okf-bundle、vendor/awesome-okf-kit、vendor/okf-bundle-template 存在且为 gitlink（mode 160000）；(3) 各目录内含对应上游源码
- **Verification**: `programmatic`

### AC-2: .gitmodules 配置正确
- **Given**: 三个子模块已添加
- **When**: 检查 .gitmodules 文件内容
- **Then**: 包含 `[submodule "vendor/awesome-okf-bundle"]`、`[submodule "vendor/awesome-okf-kit"]`、`[submodule "vendor/okf-bundle-template"]` 三个条目，path、url、branch 正确
- **Verification**: `programmatic`

### AC-3: 子模块固定到正确 commit，状态正常
- **Given**: 三个子模块已添加并检出
- **When**: 执行 `git submodule status`
- **Then**: (1) 三个新子模块输出以各自 commit hash 开头（无前缀 `-`/`+`）；(2) commit hash 与迁移前记录的基线一致（ebe906b7、5e862eeb、a0883c7b）
- **Verification**: `programmatic`

### AC-4: vendor/AGENTS.md 路由表与边界声明已更新
- **Given**: 三个子模块添加完成
- **When**: 检查 vendor/AGENTS.md
- **Then**: 子模块路由表包含三个新条目，类型均标注为 third_party；边界声明表包含对应三行，标注为不可修改
- **Verification**: `human-judgment`

### AC-5: vendor/README.md 依赖清单已更新
- **Given**: 三个子模块添加完成
- **When**: 检查 vendor/README.md 依赖清单表格
- **Then**: 表格包含三个新行，字段正确（版本 main@<short-commit> (子模块)、类型 third_party、引入日期 2026-08-06、用途说明）
- **Verification**: `human-judgment`

### AC-6: vendor/VERSION.md 版本记录已更新
- **Given**: 三个子模块添加完成
- **When**: 检查 vendor/VERSION.md
- **Then**: (1) 版本表格包含三个新行（完整 commit hash、来源 URL、日期、许可证、类型、跟踪分支）；(2) 更新记录有 2026-08-06 引入三个子模块的条目
- **Verification**: `human-judgment`

### AC-7: 主权区文档中的失效相对链接已更新
- **Given**: 子模块迁移完成
- **When**: 检查 `okf-ecosystem-wiki/01-ecosystem-map.md`
- **Then**: 原 `.chaos/libs/awesome-okf/` 的 3 处文件链接已替换为 `vendor/awesome-okf-bundle/`，`../` 前缀保持不变，Markdown 链接格式未被破坏
- **Verification**: `programmatic`

### AC-8: 现有子模块未受影响
- **Given**: 迁移前后
- **When**: 对比 vendor/flexloop、vendor/ark-cli、vendor/awesome-okf、vendor/knowledge-catalog、projects/xuanspace 的 gitlink 状态
- **Then**: 五个现有子模块的 gitlink 未变化，.gitmodules 中对应条目保持不变
- **Verification**: `programmatic`

### AC-9: 所有变更已正确暂存
- **Given**: 所有更新完成
- **When**: 执行 `git status` 和 `git diff --cached --name-only`
- **Then**: (1) .gitmodules 已暂存；(2) 三个新子模块 gitlink 已暂存；(3) vendor/AGENTS.md、vendor/README.md、vendor/VERSION.md 元数据更新已暂存；(4) 路径更新的主权区文档已暂存；(5) 无意外暂存内容
- **Verification**: `programmatic`

### AC-10: check-vendor.py 合规检测通过
- **Given**: 所有变更暂存后
- **When**: 运行 `python .agents/scripts/check-vendor.py --deep`
- **Then**: 脚本执行无错误，三个新子模块被正确识别为合规的 third_party 子模块
- **Verification**: `programmatic`

## Open Questions
- [ ] `okf-bundle-template` 无 LICENSE 文件，其许可证类型需确认（含 NOTICE.md，可能为 MIT 或模板自有声明），VERSION.md 中许可证字段如何填写
- [ ] 三个新子模块是否需要配置 `shallow = true`（保持浅克隆），还是完整克隆