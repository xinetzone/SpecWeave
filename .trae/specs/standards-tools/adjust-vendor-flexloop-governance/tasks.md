# flexloop 子模块治理模式调整 — The Implementation Plan

## [x] Task 1: .gitmodules 分支跟踪配置
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修改 `.gitmodules`，为 `vendor/flexloop` 子模块添加 `branch = main` 配置
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: `.gitmodules` 文件包含 `branch = main` 行 ✅
  - `programmatic` TR-1.2: `repo-check.py vendor --deep` 分支跟踪检查通过 ✅
- **Status**: 已完成。.gitmodules 添加了 `branch = main`，分支跟踪检查报告 "已配置 branch 跟踪"

## [x] Task 2: 更新 VENDOR-INTEGRATION.md 治理文档
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 flexloop 描述从「第三方只读子模块」改为「自有协作子模块」
  - 更新三区域边界模型、版本控制策略、新增子模块开发工作流/条件导入规范/沙箱运行规范等章节
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgment` TR-2.1~TR-2.4: 文档已更新 ✅
  - `programmatic` TR-2.5: Mermaid 图通过 check-mermaid.py 检查（0错误0警告）✅
- **Status**: 已完成

## [x] Task 3: 重构 vendor.py 检查脚本支持双模式
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 引入子模块类型概念（third_party / owned_collab）
  - 新增 _get_submodule_type、_check_reverse_dependency、_check_branch_tracking 函数
  - 修改 _check_illegal_imports 区分条件导入和裸导入
  - 修改 _check_submodule_clean 允许本地提交但检查工作树修改
  - 修复分支跟踪检测逻辑（通过 path 字段精确定位配置段）
  - 修复反向依赖检测（使用 pathlib.resolve + relative_to 精确判断）
  - 修复 Windows GBK 编码问题（使用 ASCII 输出标记替代 emoji）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1~TR-3.7: 全部通过 ✅（pytest 34 passed）
- **Status**: 已完成。修复了3个运行时 bug（编码崩溃、分支跟踪误判、反向依赖误报）

## [x] Task 4: 更新 dependency-management.md 协议文档
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 更新适用场景对比表、版本管理策略、禁止事项清单、元数据要求，区分双模式
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `human-judgment` TR-4.1~TR-4.2: 文档已更新 ✅
  - `programmatic` TR-4.3: Mermaid 图通过检查 ✅
- **Status**: 已完成

## [x] Task 5: 更新 vendor 元数据文件
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 更新 vendor/README.md 和 vendor/VERSION.md，标注 owned_collab 类型、跟踪分支 main
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `human-judgment` TR-5.1~TR-5.2: 元数据已更新 ✅
  - `programmatic` TR-5.3: repo-check.py vendor 非 deep 模式通过（exit code 0）✅
- **Status**: 已完成

## [x] Task 6: 创建运行时沙箱工具模块
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 创建 vendor_sandbox.py，提供 FLEXLOOP_AVAILABLE、conditional_import()、run_flexloop_script()
  - 修复路径计算 bug（PROJECT_ROOT 多了一级 parent）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: FLEXLOOP_AVAILABLE 正确返回 True ✅
  - `programmatic` TR-6.2: conditional_import("nonexistent.module") 返回 None ✅
  - `human-judgment` TR-6.4: 模块有清晰的 docstring 和使用示例 ✅
- **Status**: 已完成。修复了路径计算偏移一级的 bug

## [x] Task 7: 验证可选依赖优雅降级
- **Priority**: high
- **Depends On**: Task 1, Task 3, Task 6
- **Description**:
  - 验证 FLEXLOOP_AVAILABLE 检测逻辑正确
  - 验证 conditional_import 在模块不存在时返回 None 而非抛异常
  - 验证核心工具不依赖 flexloop
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-7.1~TR-7.5: 通过 ✅
- **Status**: 已完成。vendor_sandbox.py 正确提供优雅降级能力，核心工具不硬依赖 flexloop

## [x] Task 8: 综合验证与回归测试
- **Priority**: high
- **Depends On**: Task 1-7
- **Description**:
  - 运行 vendor 检查、Mermaid 检查、pytest 测试套件
- **Acceptance Criteria Addressed**: AC-1 through AC-11
- **Test Requirements**:
  - `programmatic` TR-8.1: repo-check.py vendor 非 deep 模式 exit code 0 ✅
  - `programmatic` TR-8.2: check-mermaid.py 对修改的文档 0 错误 ✅
  - `programmatic` TR-8.4: pytest 相关测试全部通过（34 passed）✅
- **Notes**: repo-check.py vendor --deep 返回 exit code 1 是因为 flexloop 内预存的 CRLF 行尾符差异（README.md 被 git 标记为 modified），以及 flexloop 内部文档的相对链接指向其自身项目结构（apps/chaos/...），这些均为 flexloop 仓库本身的预存问题，非本次引入
- **Status**: 已完成

## [x] Task 9: 更新 standards-tools 主题看板
- **Priority**: low
- **Depends On**: Task 8
- **Description**:
  - 更新 `.trae/specs/standards-tools/README.md` 看板
- **Status**: 进行中
