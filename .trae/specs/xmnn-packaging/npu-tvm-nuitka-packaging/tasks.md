# NPU TVM Nuitka 打包功能 - 实现计划

## [x] Task 1: 创建 Nuitka 打包配置目录结构（自包含）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `docker/local/` 下创建 `nuitka/` 目录
  - 在 `nuitka/` 下创建 `tvm/` 和 `vta/` 子目录（独立打包）
  - 每个子目录包含 `pyproject.toml` 和 `CMakeLists.txt`（全部自包含创建）
  - `tvm/` 目录额外包含 `_tvm_nuitka_init.py` 和 `tvm_nuitka_init.pth`
  - VTA 的 `pyproject.toml` 通过 `dependencies` 声明对 TVM 的依赖
  - **所有文件均独立创建，不引用或复制 notebook 目录中的内容**
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 检查 `docker/local/nuitka/tvm/pyproject.toml`、`docker/local/nuitka/tvm/CMakeLists.txt`、`docker/local/nuitka/tvm/_tvm_nuitka_init.py`、`docker/local/nuitka/tvm/tvm_nuitka_init.pth` 文件存在
  - `programmatic` TR-1.2: 检查 `docker/local/nuitka/vta/pyproject.toml`、`docker/local/nuitka/vta/CMakeLists.txt` 文件存在
  - `programmatic` TR-1.3: 检查 VTA 的 `pyproject.toml` 包含 `dependencies = ["tvm>=0.19.0"]`
  - `programmatic` TR-1.4: 检查所有文件不包含对 `external/xmhub/notebook` 的任何引用

## [x] Task 2: 更新 Dockerfile 安装 Nuitka 和 scikit-build-core
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在 `docker/local/conda/Dockerfile` 中添加 Nuitka 和 scikit-build-core 的 pip 安装命令
  - 确保安装在 tvm-build conda 环境中
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 检查 Dockerfile 中包含 `nuitka` 和 `scikit-build-core` 的安装命令
  - `programmatic` TR-2.2: 构建镜像后进入容器，执行 `python -c "import nuitka; print(nuitka.__version__)"` 成功

## [x] Task 3: 创建 Nuitka 编译脚本（支持独立编译）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建 `docker/local/nuitka/compile.sh` 脚本（自包含）
  - 支持独立编译 TVM 和 VTA 模块（可单独编译任一组件）
  - VTA 编译时设置 `PYTHONPATH` 指向已编译的 TVM
  - 包含增量编译检查（检测 .so 已存在时跳过）
  - 编译产物输出到 `build/nuitka/` 目录
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 在容器内执行编译脚本后，检查 `build/nuitka/tvm/tvm.cpython-*.so` 文件存在
  - `programmatic` TR-3.2: 在容器内执行编译脚本后，检查 `build/nuitka/vta/vta.cpython-*.so` 文件存在
  - `programmatic` TR-3.3: VTA 编译成功且可导入 TVM 模块

## [x] Task 4: 创建独立 Wheel 打包脚本
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 创建 `docker/local/nuitka/package.sh` 脚本（自包含）
  - 分别打包 TVM 和 VTA 为独立的 wheel 文件
  - 使用 scikit-build-core 组装 wheel 包
  - 包含产物完整性验证
  - wheel 输出到 `docker/local/nuitka/dist/` 目录
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 执行打包脚本后，检查 `docker/local/nuitka/dist/tvm-*.whl` 文件存在
  - `programmatic` TR-4.2: 执行打包脚本后，检查 `docker/local/nuitka/dist/vta-*.whl` 文件存在
  - `programmatic` TR-4.3: VTA wheel 的 METADATA 包含对 TVM 的依赖声明

## [x] Task 5: 创建打包入口脚本
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 创建 `docker/local/nuitka/build.sh` 入口脚本（自包含）
  - 串联编译和打包两个阶段（TVM 先编译和打包，然后 VTA）
  - 支持在现有 docker-compose 环境中执行
  - 支持单独编译/打包 TVM 或 VTA
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 安装 TVM wheel 后，执行 `python -c "import tvm; print(tvm.__version__)"` 成功
  - `programmatic` TR-5.2: 安装 TVM wheel 和 VTA wheel 后，执行 `python -c "import vta; print('VTA imported OK')"` 成功
  - `programmatic` TR-5.3: 仅安装 TVM wheel 时不依赖 VTA，可独立使用
  - `programmatic` TR-5.4: 所有脚本不包含对 `external/xmhub/notebook` 的任何引用