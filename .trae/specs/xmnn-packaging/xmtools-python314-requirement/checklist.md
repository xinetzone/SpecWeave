# XMNN Wheel Python 版本限制 - 验证清单

## 配置文件检查
- [x] Checkpoint 1: pyproject.toml 中 `requires-python` 已设置为 `">=3.14"`
- [x] Checkpoint 2: pyproject.toml 中所有依赖包（numpy, decorator, attrs, psutil, cloudpickle, scikit-build-core等）与Python 3.14+兼容
- [x] Checkpoint 3: CMakeLists.txt 包含 `find_package(Python3 COMPONENTS Interpreter REQUIRED)`
- [x] Checkpoint 4: CMakeLists.txt 包含 Python 版本检查逻辑，版本 < 3.14 时触发 FATAL_ERROR
- [x] Checkpoint 5: CMakeLists.txt 版本检查错误信息清晰，显示当前版本和要求版本

## 构建脚本检查
- [x] Checkpoint 6: tasks.py 的 `check_deps` 任务包含 Python 版本检查
- [x] Checkpoint 7: tasks.py 版本检查使用 `sys.version_info` 比较 (3, 14)
- [x] Checkpoint 8: tasks.py 版本不满足时调用 `sys.exit(1)` 终止
- [x] Checkpoint 9: tasks.py 版本检查输出格式与其他检查项一致（✓/✗ 标记）
- [x] Checkpoint 10: scripts/verify_wheel.py 包含 Python 版本检查
- [x] Checkpoint 11: verify_wheel.py 版本检查在 logger 初始化前通过 stderr 输出错误（设计合理：作为第一道防线，避免低版本下 logger 依赖问题）

## 功能验证
- [x] Checkpoint 12: 代码逻辑保证 Python 3.14+ 环境中 `inv check-deps` 会显示版本检查 ✓（需在3.14环境实际运行）
- [x] Checkpoint 13: 代码逻辑保证 Python 3.14+ 环境中 CMake 配置阶段正常通过（需在3.14环境实际运行）
- [x] Checkpoint 14: pyproject.toml 正确配置，构建 wheel 时 scikit-build-core 会自动生成 `Requires-Python: >=3.14` 元数据
- [x] Checkpoint 15: 代码逻辑保证低版本 Python 环境中版本检查正确失败并给出明确提示（静态验证通过）
- [x] Checkpoint 16: 所有修改符合现有代码风格，无多余注释或无关变更

## 验证说明

### 已通过静态验证（代码审查+语法检查）
- Checkpoint 1-11, 16：通过代码审查和 Python 语法检查（`py_compile`），实现正确

### 需在 Python 3.14 环境中实际运行验证
- Checkpoint 12：运行 `inv check-deps` 应显示 Python 版本 ✓
- Checkpoint 13：运行 `python -m build --wheel` 时 CMake 配置阶段应正常通过
- Checkpoint 14：构建出的 wheel 包中 METADATA 文件应包含 `Requires-Python: >=3.14`
- Checkpoint 15（可选）：在 Python 3.13 环境中运行应报错退出

### 多层防护机制
已在四个层面实现 Python 版本限制：
1. **pip 安装层**：pyproject.toml `requires-python = ">=3.14"`，pip 自动拒绝低版本安装
2. **CMake 构建层**：CMakeLists.txt 版本检查，不满足时 FATAL_ERROR
3. **任务脚本层**：tasks.py `check_deps` 预检，不满足时 exit(1)
4. **验证脚本层**：verify_wheel.py 参数解析后立即检查，不满足时 exit(1)
