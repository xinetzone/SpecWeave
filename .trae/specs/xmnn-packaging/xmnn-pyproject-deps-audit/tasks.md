# XMNN pyproject.toml 依赖审计与补全 - The Implementation Plan

## [x] Task 1: 补全 pyproject.toml 核心依赖列表
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 pyproject.toml 第10行的 `dependencies` 从 7 个包扩展为 21 个核心依赖
  - 移除 pytest（移至 dev 可选组）
  - 为每个包添加合理的最低版本约束
  - 核心依赖包含：numpy, scipy, pandas, matplotlib, Pillow, onnx, protobuf, openpyxl, tabulate, rich, tqdm, tomlkit, decorator, attrs, psutil, cloudpickle, typing_extensions, torch, torchvision, onnx2pytorch, telnetlib3
  - torch/torchvision 声明通用版本，CPU 版在 Dockerfile 中用 `--index-url` 处理
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: pyproject.toml 是合法 TOML 文件
  - `programmatic` TR-1.2: dependencies 列表包含 21 个核心包
  - `programmatic` TR-1.3: pytest 出现在 dev 组
  - `human-judgement` TR-1.4: 版本约束合理，均为 `>=X.Y` 格式
- **Notes**: 已完成。telnetlib3 从 full 组移至核心依赖。

## [x] Task 2: 添加可选依赖组（optional-dependencies）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 添加 `[project.optional-dependencies]` 段
  - `dev` 组：pytest, build, scikit-build-core
  - `examples` 组：opencv-python-headless（yolov5s show_result.py）
  - `full` 组：组合 dev + examples
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: optional-dependencies 包含 dev/examples/full 三组
  - `programmatic` TR-2.2: pip 可正确解析依赖组
- **Notes**: 已完成。telnetlib3 移至核心依赖后，full 组仅组合 dev+examples。

## [x] Task 3: 同步更新 docker/runtime/Dockerfile
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 简化 pip 安装：Step 4 仅安装 torch CPU 版和 opencv-python-headless，其余依赖由 wheel 自动解析
  - 更新验证脚本（Step 7），import 所有 21 个核心依赖并打印版本号
  - 添加 telnetlib3 import 和版本验证
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: Dockerfile 构建成功
  - `programmatic` TR-3.2: 镜像中所有依赖 import 成功
  - `human-judgement` TR-3.3: Dockerfile 不再重复维护核心依赖列表
- **Notes**: 已完成。runtime Dockerfile 验证脚本已包含 telnetlib3。

## [x] Task 4: 同步更新 docker/dev-llvm22 构建环境
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 更新 dev-llvm22/Dockerfile conda 依赖列表，添加 pandas/matplotlib/openpyxl/tabulate/tqdm/rich/onnx/protobuf/tomlkit/pillow
  - 更新 pip 安装：配置清华镜像、单独安装 torch CPU 版、安装其余包（含 onnx2pytorch/telnetlib3）
  - 更新 run-build.sh pip 依赖列表，添加 telnetlib3 和缺失的包
  - 更新验证脚本，添加所有新增包的 import 和版本检查
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: dev Docker 镜像构建成功
  - `programmatic` TR-4.2: run-build.sh 中 pip install 包含所有核心依赖
- **Notes**: 已完成。dev Dockerfile 和 run-build.sh 均已同步更新。

## [x] Task 5: 全面扫描确认无遗漏依赖
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 扫描 sdk/tools/、npuusertools/xmnn/、sdk/models/ 下所有 .py 文件的 import 语句
  - 过滤标准库和项目内部模块
  - 对比 pyproject.toml 声明，确认无遗漏
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有第三方 import 均已在 pyproject.toml 中声明
  - `programmatic` TR-5.2: pandas.to_markdown() 所需的 tabulate 已在核心依赖中
- **Notes**: 已完成。扫描确认 15 个直接 import 的第三方包全部已声明，间接依赖（scipy/decorator/attrs/psutil/cloudpickle/typing_extensions）也已包含。

## [x] Task 6: 端到端验证 - 依赖可解析性检查
- **Priority**: high
- **Depends On**: Task 1-5
- **Description**:
  - 使用 Python packaging 库验证所有依赖声明格式正确
  - 验证 TOML 语法正确性
  - 静态扫描确认无遗漏 import
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: pyproject.toml TOML 语法正确，tomllib 可解析 ✅
  - `programmatic` TR-6.2: packaging.requirements.Requirement 解析所有 21+3 依赖声明成功 ✅
  - `programmatic` TR-6.3: 全量 import 扫描确认无遗漏第三方包 ✅
- **Notes**: 静态验证全部通过。Docker 构建时验证（wheel METADATA 检查）需在下次完整构建时执行。
