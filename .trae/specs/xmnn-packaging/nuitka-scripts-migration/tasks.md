# Nuitka 脚本函数迁移 - 实现计划

## [x] Task 1: 创建 xmpack 模块结构
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `xmpack/models.py` 文件，作为数据模型模块
  - 创建 `xmpack/nuitka_compiler.py` 文件，作为 Nuitka 编译脚本生成器模块（避免与 nuitka 包命名冲突）
  - 创建 `xmpack/wheel.py` 文件，作为 Wheel 打包脚本生成器模块
  - 更新 `xmpack/__init__.py` 导出迁移的函数和模型
  - 代码风格使用 typer+dataclass 简化逻辑
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 新文件存在且路径正确 ✅
  - `programmatic` TR-1.2: `__init__.py` 正确导出所有公共 API ✅

## [x] Task 2: 迁移 NuitkaConfig 数据模型
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 将 `NuitkaConfig` 类迁移到 `xmpack/models.py`，作为纯 @dataclass（不继承 DictCompatibleDataclass，共享库不需要字典兼容层）
  - `DictCompatibleDataclass` 保留在 xmnn_pkg_utils/models.py 本地（xmnn-packager 内部便利层，非共享职责）
  - 添加完整的文档注释（类用途、属性说明、方法说明）
  - 更新 `xmpack/__init__.py` 导出
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: `NuitkaConfig` 可以从 `xmpack.models` 正确导入 ✅
  - `programmatic` TR-2.2: 类功能与原实现一致（默认值、字段访问）✅
  - `human-judgment` TR-2.3: 类有完整的 docstring ✅

## [x] Task 3: 迁移 Nuitka 编译脚本生成函数
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 将 `verify_compile_artifacts`、`build_tvm_package_script`、`build_vta_package_script`、`build_xmnn_package_script` 迁移到 `xmpack/nuitka_compiler.py`
  - 修改导入使用 `from .models import NuitkaConfig`
  - 添加完整的文档注释（函数用途、参数说明、返回值说明、异常说明）
  - 代码保持逻辑与原实现完全一致
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 所有函数可以从新位置正确导入 ✅
  - `programmatic` TR-3.2: 函数生成的脚本内容与原实现一致 ✅
  - `human-judgment` TR-3.3: 每个函数都有完整的 docstring ✅

## [x] Task 4: 迁移 Wheel 打包脚本生成函数
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 将 `package_xmnn_wheel_script` 迁移到 `xmpack/wheel.py`
  - 添加完整的文档注释
  - 保持函数签名和行为与原实现完全一致
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 函数可以从新位置正确导入 ✅
  - `programmatic` TR-4.2: 函数生成的脚本内容与原实现一致（包括 no_llvm 变体）✅
  - `human-judgment` TR-4.3: 函数有完整的 docstring ✅

## [x] Task 5: 更新原文件导入引用
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 修改 `xmnn_pkg_utils/nuitka_scripts.py`，从 `xmpack` 导入函数后重新导出
  - 保持原文件函数名和签名不变，确保向后兼容性
  - 在原文件添加注释说明函数已迁移到 xmpack
  - 添加 `_ensure_xmpack_importable()` 路径自动发现
  - 更新 `xmnn_pkg_utils/models.py`，从 `xmpack.models` 导入 `NuitkaConfig` 并重新导出；DictCompatibleDataclass 保留本地定义
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: 从 `xmnn_pkg_utils.nuitka_scripts` 导入的函数仍然可用 ✅
  - `programmatic` TR-5.2: 从 `xmnn_pkg_utils.models` 导入的 `NuitkaConfig` 仍然可用 ✅
  - `programmatic` TR-5.3: 函数行为与迁移前完全一致 ✅

## [x] Task 6: 更新 xmnn_pkg_utils/__init__.py 导入路径
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 更新 `__init__.py` 中的导入语句，确保导出的函数仍然可用
  - 保持 `__all__` 列表不变
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 从 `xmnn_pkg_utils` 顶层导入的函数仍然可用 ✅

## [x] Task 6b: xmpack 包构建配置
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 为 xmnn/ 创建 pyproject.toml，使用 scikit-build-core+cmake+ninja 构建系统
  - 创建最小 CMakeLists.txt（LANGUAGES NONE，纯 Python 包）
  - 添加自动路径发现机制 `_ensure_xmpack_importable()`
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-6b.1: xmpack 包可以通过 pip install -e 安装 ✅
  - `programmatic` TR-6b.2: 自动路径发现在开发环境中正常工作 ✅

## [x] Task 7: 运行单元测试验证
- **Priority**: high
- **Depends On**: Task 6b
- **Description**: 
  - 验证所有导入正常（直接从 xmpack 导入、从 xmnn_pkg_utils 向后兼容导入）
  - 验证函数行为与原实现一致
  - 验证 DictCompatibleDataclass 本地功能正常（其他 Config 类继承后字典访问正常）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 直接从 xmpack 导入所有函数和模型成功 ✅
  - `programmatic` TR-7.2: 向后兼容导入（从 xmnn_pkg_utils）成功 ✅
  - `programmatic` TR-7.3: 函数行为与原实现一致 ✅
  - `programmatic` TR-7.4: 本地 DictCompatibleDataclass 字典访问方法正常 ✅

## [x] Task 8: 验证 CLI 与依赖模块导入
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 验证 `xmnn_pkg_cli/nuitka.py` CLI 模块可以正常导入
  - 验证 `xmnn_pkg_utils/__init__.py` 所有导出正常
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: CLI 模块可以正常导入无 ImportError ✅
  - `programmatic` TR-8.2: 所有引用模块无循环导入问题 ✅
