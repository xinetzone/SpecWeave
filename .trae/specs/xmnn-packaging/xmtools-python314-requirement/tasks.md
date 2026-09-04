# XMNN Wheel Python 版本限制 - 实现计划

## [x] Task 1: 更新 pyproject.toml 声明 Python 3.14+ 版本要求
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 修改 `external/chaos/xmtools/pyproject.toml`
  - 将 `requires-python` 从 `">=3.8"` 更新为 `">=3.14"`
  - 确认 build-system 和 dependencies 中的包都支持 Python 3.14+
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: 检查 `pyproject.toml` 中 `requires-python = ">=3.14"`
  - `programmatic` TR-1.2: 确认所有依赖包在 Python 3.14 环境中可正常安装

## [x] Task 2: 在 CMakeLists.txt 中添加 Python 版本检查
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 修改 `external/chaos/xmtools/CMakeLists.txt`
  - 在 `project()` 命令后添加 `find_package(Python3 COMPONENTS Interpreter REQUIRED)`
  - 添加版本检查逻辑：如果 `Python3_VERSION` 小于 3.14，触发 `message(FATAL_ERROR ...)`
  - 错误信息需明确显示当前版本和要求版本
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: CMakeLists.txt 包含 `find_package(Python3 COMPONENTS Interpreter REQUIRED)`
  - `programmatic` TR-2.2: CMakeLists.txt 包含版本检查和 `FATAL_ERROR`
  - `human-judgement` TR-2.3: 错误信息清晰可读，包含当前版本号和要求版本号

## [x] Task 3: 在 tasks.py 的 check_deps 中添加 Python 版本验证
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 修改 `external/chaos/xmtools/tasks.py`
  - 在 `check_deps` 任务开头添加 Python 版本检查
  - 使用 `sys.version_info` 检查版本是否 >= (3, 14)
  - 如果版本不满足，打印错误信息并调用 `sys.exit(1)`
  - 版本满足时显示 ✓ 标记和当前版本号
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: tasks.py 中 `check_deps` 函数包含 Python 版本检查逻辑
  - `programmatic` TR-3.2: 使用 Python 3.14+ 运行 `inv check-deps` 时版本检查通过
  - `human-judgement` TR-3.3: 输出格式与现有检查项风格一致（使用 ✓/✗ 标记）

## [x] Task 4: 在 verify_wheel.py 中添加 Python 版本检查
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 修改 `external/chaos/xmtools/scripts/verify_wheel.py`
  - 在脚本开头（main 函数或入口点）添加 Python 版本检查
  - 版本不满足时记录错误日志并退出
  - 使用已有的 logger 记录版本信息
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: verify_wheel.py 包含 Python 版本检查
  - `programmatic` TR-4.2: 版本不满足时脚本以非零退出码退出
  - `human-judgement` TR-4.3: 错误信息通过 logger 输出，符合现有日志格式

## [x] Task 5: 验证整体版本限制功能
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 
  - 在 Python 3.14+ 环境中运行完整检查流程
  - 验证 `inv check-deps` 通过
  - 验证 CMake 配置阶段版本检查通过（dry-run 或实际测试）
  - （可选）在低版本 Python 环境中验证检查正确失败（如果环境可用）
  - 确认 pip 会根据 requires-python 拒绝低版本安装（可通过 `pip install --dry-run` 或wheel元数据验证）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: Python 3.14+ 环境中 `inv check-deps` 成功，版本检查项显示 ✓
  - `programmatic` TR-5.2: wheel 包 METADATA 中包含 `Requires-Python: >=3.14`
  - `human-judgement` TR-5.3: 所有错误信息清晰、友好，包含明确的版本要求说明
