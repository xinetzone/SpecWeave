# Nuitka 脚本函数迁移 - 产品需求文档

## Overview
- **Summary**: 对 `nuitka_scripts.py` 文件进行全面代码分析，识别具有通用性的函数模块，迁移至 `xmpack` 目录，并保持原有功能不受影响。
- **Purpose**: 提取可复用的 Nuitka 编译与打包脚本生成功能，建立共享库，避免代码重复，提升代码可维护性。
- **Target Users**: XMNN 项目开发者、打包工具使用者

## Goals
- 识别并提取 `nuitka_scripts.py` 中具有通用性的函数模块
- 将提取的函数按功能逻辑分类整理后迁移至 `xmpack` 目录
- 添加完整的文档注释说明函数用途、参数及返回值
- 在原文件中通过导入方式引用新位置的函数
- 确保所有单元测试通过，验证功能未受影响

## Non-Goals (Out of Scope)
- 修改函数的核心逻辑或行为
- 重构 `models.py` 或其他依赖模块
- 修改 CLI 命令实现
- 添加新功能或优化现有功能性能

## Background & Context
- `nuitka_scripts.py` 位于 `dev-env/xmnn-packager/xmnn_pkg_utils/` 目录
- 目标目录 `xmnn/src/xmpack/` 当前仅包含空的 `__init__.py`
- 函数依赖 `xmnn_pkg_utils.models.NuitkaConfig` 数据模型
- 已有完整的单元测试覆盖

## Functional Requirements
- **FR-1**: 分析 `nuitka_scripts.py` 中所有函数，识别可复用的通用模块
- **FR-2**: 将可复用函数按功能分类迁移至 `xmpack` 目录
- **FR-3**: 为迁移的函数添加完整的文档注释
- **FR-4**: 修改原文件，通过导入方式引用新位置的函数
- **FR-5**: 运行单元测试验证功能完整性

## Non-Functional Requirements
- **NFR-1**: 代码风格与原项目保持一致，尽可能使用 `typer+dataclass` 简化逻辑
- **NFR-2**: 迁移后的函数保持向后兼容性
- **NFR-3**: 单元测试覆盖率不低于原水平

## Constraints
- **Technical**: 需维护对 `NuitkaConfig` 的依赖
- **Dependencies**: `nuitka_scripts.py` 被多个模块引用（`__init__.py`、`nuitka.py`、`test_nuitka_scripts.py`）

## Assumptions
- 目标目录 `xmpack` 已存在且为空
- Python 环境已配置好必要的依赖
- 现有测试可以正常运行

## Acceptance Criteria

### AC-1: 函数分析完成
- **Given**: 已读取 `nuitka_scripts.py` 文件
- **When**: 完成函数分析并分类
- **Then**: 输出可复用函数列表及分类方案
- **Verification**: `human-judgment`

### AC-2: 函数迁移完成
- **Given**: 可复用函数列表已确定
- **When**: 创建新文件并迁移函数
- **Then**: `xmpack` 目录下包含迁移后的函数文件
- **Verification**: `programmatic`

### AC-3: 文档注释完整
- **Given**: 函数已迁移
- **When**: 添加文档注释
- **Then**: 每个函数都有完整的 docstring（用途、参数、返回值）
- **Verification**: `human-judgment`

### AC-4: 原文件导入引用更新
- **Given**: 函数已迁移到新位置
- **When**: 修改原文件的导入语句
- **Then**: 原文件通过导入方式使用新位置的函数
- **Verification**: `programmatic`

### AC-5: 单元测试通过
- **Given**: 所有代码修改完成
- **When**: 运行单元测试
- **Then**: 所有测试用例通过，无回归问题
- **Verification**: `programmatic`

## Open Questions
- [x] 是否需要创建多个文件来分类不同功能？→ 是，创建 `nuitka_compiler.py`、`wheel.py` 和 `models.py`
- [x] 如何处理 `NuitkaConfig` 的依赖路径？→ 将 `NuitkaConfig` 迁移到 `xmpack/models.py`，由 `xmnn_pkg_utils` 反向引用

## 架构决策
- **依赖方向**：`xmpack` 作为共享库，不应依赖 `xmnn_pkg_utils`（开发工具包）
- **方案**：将 `NuitkaConfig` 迁移到 `xmpack/models.py`，`xmnn_pkg_utils` 反向引用 `xmpack`
- **文件结构**：
  - `xmpack/models.py`: 数据模型（NuitkaConfig）
  - `xmpack/nuitka_compiler.py`: Nuitka 编译脚本生成器
  - `xmpack/wheel.py`: Wheel 打包脚本生成器
  - `xmpack/__init__.py`: 导出所有公共 API
