# PyCaffe pyproject.toml Python 3.14+ 兼容性更新 - Implementation Plan

## [x] Task 1: 更新 pyproject.toml 中 requires-python 和 build-system 依赖
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 确认 `requires-python = ">=3.14"` 设置正确
  - 更新 `[build-system].requires` 中 `scikit-build-core` 版本下限为 `>=0.10`，添加 `setuptools-scm>=8.0`、`ninja>=1.11`、`cmake>=3.26`
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: `requires-python` 字段值为 `">=3.14"` ✅
  - `programmatic` TR-1.2: build-system.requires 中 scikit-build-core 版本约束为 `>=0.10` ✅
  - `programmatic` TR-1.3: TOML 语法正确，可用 tomllib 解析 ✅
- **Notes**: 已移除错误出现在 build-system.requires 中的 numpy（仅为运行时依赖）

## [x] Task 2: 更新运行时依赖 (dependencies) 版本下限
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 将 `[project].dependencies` 中所有包的版本下限提升到兼容 Python 3.14 的版本
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: 每个 dependencies 条目的版本下限 >= 目标最低版本 ✅
  - `programmatic` TR-2.2: 依赖列表中不包含对 Python 3.14 不兼容的旧版本约束 ✅
  - `programmatic` TR-2.3: typing-extensions 被添加到 dependencies ✅
  - `programmatic` TR-2.4: TOML 语法正确 ✅
- **Notes**: numpy 更新为 >=2.3（首个正式支持 Python 3.14 的版本系列）

## [x] Task 3: 更新可选依赖 (optional-dependencies) 版本下限
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 更新 test 组为 pytest/jupyter/ipython/notebook
  - 更新 full 组，保留原有 python-gflags/leveldb 并添加新工具包
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: test 组包含 pytest/jupyter/ipython/notebook ✅
  - `programmatic` TR-3.2: full 组包含 pycaffe[test] + pandas/black/isort/mypy/graphviz/python-gflags/leveldb ✅
  - `programmatic` TR-3.3: TOML 语法正确 ✅

## [x] Task 4: 检查并更新 scikit-build 配置
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 添加 minimum-version = "0.10"
  - 保留 wheel.py-api = "py3" 等原有配置
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: wheel.py-api 配置不阻止 Python 3.14+ 构建 ✅
  - `programmatic` TR-4.2: cmake 配置正确指向 pycaffe 目录 ✅

## [x] Task 5: 更新 build.sh 注释
- **Priority**: low
- **Depends On**: Task 2
- **Description**: 
  - 将 build.sh 第6行注释更新为 "Python 3.14+"
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgment` TR-5.1: build.sh 注释反映 Python 3.14+ 要求 ✅
  - `programmatic` TR-5.2: build.sh 脚本本身无语法错误 ✅

## [x] Task 6: TOML 格式验证和配置完整性检查
- **Priority**: high
- **Depends On**: Task 1, 2, 3, 4, 5
- **Description**: 
  - 使用 Python tomllib 解析修改后的 pyproject.toml
  - 验证所有字段存在且格式正确
  - 使用 packaging.requirements 验证版本约束
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: Python tomllib 成功解析 pyproject.toml 无错误 ✅
  - `programmatic` TR-6.2: 所有28个版本约束字符串可被 packaging.requirements.Requirement 成功解析 ✅
  - `programmatic` TR-6.3: requires-python 约束为 ">=3.14" ✅
  - `programmatic` TR-6.4: build-system、project、tool.scikit-build 各节完整 ✅
- **Verification Result**: 44/44 项检查全部通过
