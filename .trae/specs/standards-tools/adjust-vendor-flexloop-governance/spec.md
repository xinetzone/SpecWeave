# flexloop 子模块治理模式调整 — Product Requirement Document

## Overview

- **Summary**: 将 vendor/flexloop 从「第三方只读子模块」治理模式调整为「自有协作子模块」模式：跟踪 main 分支、开放子模块内代码编辑权限、支持条件导入+萃取双模式使用、建立单向访问控制机制（代码级约束+运行时沙箱）。

- **Purpose**: flexloop（AgentForge）是 SpecWeave 团队拥有完全控制权的项目，当前的「禁止本地修改、固定 commit、禁止直接 import」第三方治理模式过于保守，阻碍了对 flexloop 的迭代开发和按需使用。需要调整为适合自有项目的协作模式，同时保持两个项目的独立性和安全边界。

- **Target Users**: SpecWeave 项目开发者、维护者，以及使用 vendor check 工具的 AI 智能体。

## Goals

1. 配置 `.gitmodules` 跟踪 flexloop 的 main 分支，支持通过 `git submodule update --remote` 拉取最新代码
2. 明确 flexloop 的「自有项目」属性，允许在 vendor/flexloop/ 内按标准子模块开发流程编辑代码、提交到 flexloop 远程仓库
3. 确认 flexloop 作为独立项目不依赖 SpecWeave，维护严格的单向依赖（SpecWeave→flexloop）
4. 实现 flexloop 的可选依赖特性：未初始化时 SpecWeave 核心功能正常工作，涉及 flexloop 的功能优雅降级
5. 建立双层访问控制：代码级自动化检测（反向依赖检测、非法写入检测）+ 运行时沙箱（flexloop 脚本运行时路径白名单）

## Non-Goals (Out of Scope)

- 不改变 flexloop 自身的代码结构、构建系统或发布流程
- 不将 flexloop 改为普通目录纳入 SpecWeave 主仓库（保留 submodule 独立版本历史）
- 不修改 flexloop 的 CI/CD 或远程仓库配置
- 不实现 flexloop 的自动同步/定时更新机制（保持按需更新策略）
- 不在 SpecWeave 核心功能中强依赖 flexloop（保持核心独立性）

## Background & Context

### 当前状态

- `.gitmodules` 未配置 `branch` 字段，submodule 处于 detached HEAD 状态，固定在 commit `d618849a`（v0.7.1-270-gd618849）
- VENDOR-INTEGRATION.md 定义的治理模式为「第三方只读子模块」：
  - 三区域边界模型中 flexloop 主权区标注为「禁止本地修改」
  - 外部依赖四不原则：不侵入、不直引、不跟版、不裸考
  - 禁止行为清单包含「在 vendor/flexloop/ 内创建/修改/删除文件」「直接 import vendor/ 模块」
- vendor.py 检查脚本的 `_check_illegal_imports` 会将所有 `import vendor.` 或 `from vendor.` 标记为违规
- dependency-management.md 中 git submodule 行的「本地修改」列为「禁止」

### 治理模式变更对照

| 维度 | 当前模式（第三方只读） | 新模式（自有协作） |
|---|---|---|
| 版本策略 | 固定 commit，不跟踪分支 | 跟踪 main 分支，按需更新 |
| 本地修改 | 绝对禁止 | 允许子模块开发（commit 到 flexloop 仓库） |
| 代码引用 | 禁止直接 import，仅萃取 | 条件导入（try/except）+ 萃取双模式 |
| 依赖性质 | 参考实现，非运行时依赖 | 可选运行时依赖，按需加载 |
| 访问控制 | 靠规范约束 | 规范+自动化检测+运行时沙箱三层 |

### 关键约束

- flexloop 远程仓库地址不变（`git@gitcode.com:flexloop/flexloop.git`）
- 子模块路径不变（`vendor/flexloop`）
- 两个项目仍保持独立 Git 仓库，不合并
- SpecWeave 核心功能（不依赖 flexloop 的部分）必须在 flexloop 未初始化时正常工作

## Functional Requirements

- **FR-1**: `.gitmodules` 添加 `branch = main` 配置，使 `git submodule update --remote vendor/flexloop` 能拉取 main 分支最新代码
- **FR-2**: 更新 VENDOR-INTEGRATION.md，将 flexloop 标记为「自有协作子模块」，调整三区域边界模型中的 flexloop 主权区描述为「允许子模块内开发，提交至 flexloop 仓库」
- **FR-3**: 更新「外部依赖四不原则」为适用于自有子模块的「协作四原则」：可编辑（在子模块内开发并推送上游）、条件引（try/except 条件导入）、跟踪分支（跟踪 main 分支但不自动更新）、沙箱护（脚本运行时路径隔离）
- **FR-4**: 更新 vendor.py 检查脚本：
  - `_check_illegal_imports` 区分「条件导入」（try/except ImportError 包裹）和「强制导入」（裸 import），前者为允许，后者为警告
  - 新增 `_check_reverse_dependency` 检查：扫描 vendor/flexloop/ 内代码是否引用了 SpecWeave 主权区路径
  - 新增 `_check_branch_tracking` 检查：验证 .gitmodules 是否配置了 branch 字段
  - 调整 `_check_submodule_clean`：允许子模块内有本地提交（ahead of remote），但不允许未提交的工作树修改
- **FR-5**: 更新 dependency-management.md 中 git submodule 相关描述，区分「第三方只读子模块」和「自有协作子模块」两种模式
- **FR-6**: 创建 vendor/flexloop/ 运行时沙箱工具模块，提供 `run_flexloop_script()` 函数，在子进程中运行 flexloop 脚本并限制文件系统写入范围（仅限 vendor/flexloop/ 和 .temp/ 目录）
- **FR-7**: 更新 vendor/README.md 和 vendor/VERSION.md 元数据，标注 flexloop 为「自有协作子模块」，记录当前跟踪分支和最新同步 commit
- **FR-8**: 更新 pytest.ini 测试隔离配置，保持 flexloop 测试目录排除
- **FR-9**: 创建条件导入的规范文档和示例代码，说明如何在 SpecWeave 中安全地可选导入 flexloop 模块

## Non-Functional Requirements

- **NFR-1（向后兼容）**: 未初始化 flexloop 子模块时，`python .agents/scripts/repo-check.py vendor --deep` 不应报错，应给出提示信息
- **NFR-2（性能）**: vendor check 新增的反向依赖扫描不应使 `--deep` 检查总耗时增加超过 50%
- **NFR-3（可维护性）**: 新旧两种子模块模式（第三方只读 vs 自有协作）应在检查脚本中通过配置明确区分，便于未来新增子模块时选择模式
- **NFR-4（安全）**: 运行时沙箱必须确保 flexloop 脚本无法写入 vendor/flexloop/ 和 .temp/ 以外的路径
- **NFR-5（可发现性）**: 条件导入规范和沙箱使用方式应在 VENDOR-INTEGRATION.md 中有明确文档和示例

## Constraints

- **Technical**:
  - 保留 git submodule 机制，不迁移到其他依赖管理方式
  - Python 3.12+ 兼容，不引入新的第三方运行时依赖（沙箱使用 subprocess + cwd 限制，不使用容器技术）
  - Windows 兼容性：所有路径处理和脚本调用必须支持 Windows 环境
- **Business**:
  - flexloop 保持独立项目定位和 Apache-2.0 许可证
  - 不破坏现有 SpecWeave 功能和 CI 流水线
- **Dependencies**:
  - 依赖现有的 `.agents/scripts/lib/checks/vendor.py` 检查框架
  - 依赖现有的 `lib/cli.py` 输出规范
  - 依赖现有的 `pytest.ini` 配置

## Assumptions

- flexloop 远程仓库的 main 分支可正常访问和拉取
- 团队对 flexloop 仓库拥有 push 权限（自有项目前提）
- SpecWeave 当前没有直接 import vendor/flexloop/ 模块的代码（需验证）
- 现有 CI 流程中 `repo-check.py vendor --deep` 不会因模式调整而失败

## Acceptance Criteria

### AC-1: .gitmodules 分支跟踪配置
- **Given**: `.gitmodules` 文件存在
- **When**: 读取 `vendor/flexloop` 子模块配置
- **Then**: 包含 `branch = main` 配置项
- **Verification**: `programmatic`
- **Notes**: 可通过 `git config -f .gitmodules submodule.vendor/flexloop.branch` 验证

### AC-2: 子模块分支跟踪功能可用
- **Given**: `.gitmodules` 已配置 `branch = main`
- **When**: 执行 `git submodule update --remote vendor/flexloop`
- **Then**: 子模块切换到 main 分支的最新 commit，不产生错误
- **Verification**: `programmatic`

### AC-3: VENDOR-INTEGRATION.md 治理模式更新
- **Given**: VENDOR-INTEGRATION.md 文档
- **When**: 阅读文档
- **Then**: 明确标注 flexloop 为「自有协作子模块」；三区域边界模型更新 flexloop 区描述；四不原则更新为协作四原则；包含子模块开发流程（编辑→commit→push→更新指针）；包含条件导入示例和沙箱使用说明
- **Verification**: `human-judgment`

### AC-4: vendor.py 检查脚本区分条件导入和强制导入
- **Given**: 项目中有使用 `try: import vendor.flexloop... except ImportError:` 模式的代码
- **When**: 运行 `repo-check.py vendor --deep`
- **Then**: 条件导入不被标记为违规；裸 `import vendor.xxx` 被标记为警告（非错误）
- **Verification**: `programmatic`

### AC-5: vendor.py 反向依赖检测
- **Given**: vendor/flexloop/ 内有代码引用了 SpecWeave 主权区文件（如 `../../.agents/` 路径）
- **When**: 运行 `repo-check.py vendor --deep`
- **Then**: 检测到反向依赖引用并报告为错误
- **Verification**: `programmatic`

### AC-6: vendor.py 分支跟踪检查
- **Given**: `.gitmodules` 缺少 flexloop 的 branch 配置
- **When**: 运行 `repo-check.py vendor --deep`
- **Then**: 报告分支跟踪未配置的警告
- **Verification**: `programmatic`

### AC-7: vendor.py 子模块清洁检查调整
- **Given**: 子模块内有本地提交（ahead of remote）但工作树清洁
- **When**: 运行 `repo-check.py vendor --deep`
- **Then**: 不报告错误（本地提交允许）；若工作树有未提交修改则报告错误
- **Verification**: `programmatic`

### AC-8: 运行时沙箱限制写入范围
- **Given**: 通过沙箱工具运行一个尝试写入 SpecWeave 主权区文件的 flexloop 脚本
- **When**: 脚本尝试写入 vendor/flexloop/ 或 .temp/ 以外的路径
- **Then**: 沙箱阻止写入操作并抛出异常/返回错误
- **Verification**: `programmatic`

### AC-9: 可选依赖优雅降级
- **Given**: flexloop 子模块未初始化（目录为空或不存在）
- **When**: 运行 SpecWeave 核心工具（如 repo-check.py、check-links.py 等不依赖 flexloop 的脚本）
- **Then**: 所有核心功能正常运行，不出现 ImportError 或文件找不到错误
- **Verification**: `programmatic`

### AC-10: 元数据更新
- **Given**: vendor/README.md 和 vendor/VERSION.md
- **When**: 阅读这两个文件
- **Then**: flexloop 标注为「自有协作子模块」，记录跟踪分支为 main
- **Verification**: `human-judgment`

### AC-11: dependency-management.md 更新
- **Given**: `.agents/protocols/dependency-management.md`
- **When**: 阅读 Git 子模块依赖管理章节
- **Then**: 区分「第三方只读子模块」和「自有协作子模块」两种模式，各自有适用场景对比表和操作规范
- **Verification**: `human-judgment`

## Open Questions（已解决）

1. **条件导入路径方案**：通过 `vendor_sandbox.py` 的 `conditional_import()` 辅助函数动态导入，内部临时添加 vendor/flexloop 路径到 sys.path（导入后恢复），不在全局永久修改 sys.path。调用方式：`flexloop_mod = conditional_import("apps.chaos.src.taolib.cli")`，失败返回 None。
2. **沙箱网络访问**：初期仅限制文件系统写入（通过 cwd 和环境变量），不做网络访问限制。后续若有安全需求再升级。
3. **Pre-commit hook 隔离**：flexloop 子模块有独立 `.git` 目录，在子模块内 commit 时 SpecWeave 的 hooks 不会触发，无需特殊配置。在 SpecWeave 主仓库提交时，vendor check 会检查子模块状态。
