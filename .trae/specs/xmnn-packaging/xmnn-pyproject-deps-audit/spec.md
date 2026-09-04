# XMNN pyproject.toml 依赖审计与补全 - Product Requirement Document

## Overview
- **Summary**: 审计并补全 [pyproject.toml](file:///d:/spaces/SpecWeave/external/chaos/xmtools/pyproject.toml) 中的 `dependencies` 列表，确保 `sdk/tools/` 目录下所有 CLI 脚本（compile.py、accuracy.py、infer.py、performance.py、bandwidth.py、excelreport.py）及其调用的 xmnn API 模块所需的第三方 Python 包全部声明，版本兼容 Python 3.14，且可通过 conda/pip 正确安装。
- **Purpose**: 当前 pyproject.toml 的依赖列表严重不足（仅 7 个包），缺少 pandas、matplotlib、onnx、torch、torchvision、Pillow、protobuf、openpyxl、rich、tqdm、tomlkit、tabulate、onnx2pytorch 等关键依赖。用户在纯净环境中 `pip install xmnn-*.whl` 后运行 SDK 工具会因 `ModuleNotFoundError` 崩溃。本任务确保 wheel 包自带完整依赖元数据，实现"安装即用"。
- **Target Users**: XMNN 最终用户（通过 pip install xmnn-*.whl 安装后直接使用 sdk/tools/ CLI 脚本的开发者）

## Goals
- 补全 pyproject.toml `[project].dependencies` 列表，覆盖 xmnn 包内所有模块和 sdk/tools/ 脚本的第三方 import
- 为每个依赖指定合理的最低版本约束，确保与 Python 3.14 兼容
- 同步更新 Docker 构建环境（dev 和 runtime Dockerfile）使其与 pyproject.toml 依赖一致
- 验证：在全新虚拟环境中仅安装 wheel 包后，6 个 CLI 脚本的 `--help` 均能正常执行，accuracy.py/compile.py 端到端流程无 ImportError

## Non-Goals (Out of Scope)
- 不修复 xmnn 代码本身的 bug（仅补全依赖声明）
- 不处理 caffe Python 包（代码中仅使用 caffe_pb2（protobuf 生成的文件），无 `import caffe`）
- 不添加 telnetlib3 到核心依赖（该模块仅在 telnet 远程连接功能中延迟导入，属于可选功能）
- 不锁定精确版本（仅指定最低兼容版本，如 `pandas>=2.0`）
- 不修改 xmnn 源码的 import 逻辑

## Background & Context
- xmnn 通过 Nuitka 编译为 `.so` 后使用 scikit-build-core 打包为 wheel
- wheel 包已包含 tvm/vta/xmnn 三个 Nuitka 编译模块和 _libs/ 原生库目录
- 之前的修复（fix-xmnn-whl-data-dirs）已确保 autolibs/tools_cpp/fonts 数据目录正确打包
- 但 pyproject.toml 中的 Python 依赖列表自项目初始化以来未更新，遗漏了大量第三方包
- Docker 运行时镜像（docker/runtime/Dockerfile）通过 pip install 手动安装了一批包，但与 pyproject.toml 不同步
- Python 版本要求：>=3.14

### 依赖分析结果

通过扫描 `npuusertools/xmnn/` 下 42 个 .py 文件的 import 语句，识别出以下第三方依赖：

| pip 包名 | import 名 | 是否当前pyproject已有 | 使用场景 | 必要性 |
|---------|-----------|---------------------|---------|--------|
| numpy | numpy | ✅ 已有 | 核心数组运算 | 必须 |
| scipy | scipy | ✅ 已有 | 科学计算（TVM依赖） | 必须 |
| decorator | decorator | ✅ 已有 | TVM装饰器 | 必须 |
| attrs | attrs | ✅ 已有 | 数据类 | 必须 |
| psutil | psutil | ✅ 已有 | 系统监控 | 必须 |
| cloudpickle | cloudpickle | ✅ 已有 | 序列化 | 必须 |
| typing_extensions | typing_extensions | ✅ 已有 | 类型注解兼容 | 必须 |
| pytest | pytest | ✅ 已有（但属于dev依赖） | 测试框架 | 应移至dev |
| pandas | pandas | ❌ 缺失 | 精度指标汇总、Excel报告 | 必须 |
| matplotlib | matplotlib | ❌ 缺失 | 图表生成 | 必须 |
| Pillow (PIL) | PIL | ❌ 缺失 | 图像加载（data.py延迟导入） | 必须 |
| onnx | onnx | ❌ 缺失 | ONNX模型前端 | 必须 |
| protobuf | google.protobuf | ❌ 缺失 | caffe_pb2、ONNX proto | 必须 |
| openpyxl | openpyxl | ❌ 缺失 | Excel报告生成 | 必须 |
| tabulate | tabulate | ❌ 缺失 | pandas to_markdown() | 必须 |
| rich | rich | ❌ 缺失 | 日志美化输出（logger_config.py） | 必须 |
| tqdm | tqdm | ❌ 缺失 | 进度条 | 必须 |
| tomlkit | tomlkit | ❌ 缺失 | config.toml解析 | 必须 |
| torch | torch | ❌ 缺失 | PyTorch模型前端、adaround量化 | 必须（CPU版） |
| torchvision | torchvision | ❌ 缺失 | PyTorch模型示例（resnet等） | 必须（CPU版） |
| onnx2pytorch | onnx2pytorch | ❌ 缺失 | ONNX→PyTorch转换（adaround） | 必须 |
| opencv-python-headless | cv2 | ❌ 缺失 | yolov5s示例show_result.py | 可选* |

*注：opencv-python-headless 仅在 `sdk/models/onnx/yolov5s/show_result.py` 示例脚本中使用，非工具链核心依赖，可放入可选依赖组。

## Functional Requirements
- **FR-1**: pyproject.toml 的 `[project].dependencies` 必须包含 xmnn 包所有直接 import 的第三方包（17个缺失包 + 已有7个包，pytest移至dev）
- **FR-2**: 每个依赖必须指定与 Python 3.14 兼容的最低版本约束
- **FR-3**: 必须定义 `[project.optional-dependencies]` 可选依赖组，将 opencv 等非核心依赖归入
- **FR-4**: docker/runtime/Dockerfile 必须与 pyproject.toml 依赖保持一致，从 pip 安装列表改为直接安装 wheel（wheel 会自动拉取依赖）
- **FR-5**: docker/dev-llvm22/Dockerfile 中的 conda/pip 依赖列表必须同步更新
- **FR-6**: 保留 pytest 在开发依赖组中（如 `[project.optional-dependencies].dev`）

## Non-Functional Requirements
- **NFR-1**: 所有声明的依赖必须能在 linux-x86_64 + Python 3.14 环境下通过 pip 成功安装
- **NFR-2**: torch 必须使用 CPU 版本（通过 `--index-url https://download.pytorch.org/whl/cpu` 或使用 `torch; platform_system != "..."` 标记），避免引入 CUDA 依赖
- **NFR-3**: 依赖列表保持精简，不引入传递依赖中已包含的冗余包
- **NFR-4**: 版本约束使用 `>=` 最低版本形式，不使用上限锁定（除非存在已知不兼容版本）

## Constraints
- **Technical**: Python >=3.14，wheel 包使用 scikit-build-core 构建
- **Business**: 必须保证 Docker 构建环境（国内镜像源）可顺利安装所有依赖
- **Dependencies**: torch CPU 版需从 PyTorch 官方 index 安装；其余包从 PyPI 安装

## Assumptions
- onnx2pytorch 已有兼容 Python 3.14 的版本（或可从源码安装）
- torch CPU 版对 Python 3.14 提供 wheel 支持（PyTorch 2.5+ 已支持）
- 用户会在 x86_64 Linux 环境中使用（Docker 容器），Windows/macOS 兼容性不在本次保证范围内
- telnetlib3 为可选功能，不需要强制安装

## Acceptance Criteria

### AC-1: pyproject.toml 依赖列表完整
- **Given**: 修改后的 pyproject.toml
- **When**: 检查 `[project].dependencies` 列表
- **Then**: 包含 numpy, scipy, pandas, matplotlib, Pillow, onnx, protobuf, openpyxl, tabulate, rich, tqdm, tomlkit, torch, torchvision, onnx2pytorch, decorator, attrs, psutil, cloudpickle, typing_extensions（共20个核心依赖）
- **Verification**: `programmatic`

### AC-2: pytest 移至可选 dev 依赖组
- **Given**: 修改后的 pyproject.toml
- **When**: 检查 dependencies 和 optional-dependencies
- **Then**: pytest 不在核心 dependencies 中，而是在 `[project.optional-dependencies].dev` 组内
- **Verification**: `programmatic`

### AC-3: 版本约束合理且兼容 Python 3.14
- **Given**: 修改后的 pyproject.toml
- **When**: 审查每个依赖的版本约束
- **Then**: 所有依赖使用 `>=X.Y` 最低版本格式，版本号不超过当前已知兼容 Python 3.14 的最新版本
- **Verification**: `human-judgment`

### AC-4: Wheel 包在纯净环境中可安装且所有 CLI --help 正常
- **Given**: 从修改后的源码构建的 xmnn wheel 包
- **When**: 在一个全新的 Python 3.14 虚拟环境中 `pip install xmnn-*.whl`（不额外安装任何包）
- **Then**: 安装成功，且以下 6 个命令均能正常输出 help 信息（无 ModuleNotFoundError）：
  - `python -m xmnn` 或 `python tools/compile.py --help`
  - `python tools/accuracy.py --help`
  - `python tools/infer.py --help`
  - `python tools/performance.py --help`
  - `python tools/bandwidth.py --help`
  - `python tools/excelreport.py --help`
- **Verification**: `programmatic`

### AC-5: Docker 运行时镜像依赖同步
- **Given**: 更新后的 docker/runtime/Dockerfile
- **When**: 构建 xmnn:1.2.1-alpha 运行时镜像
- **Then**: 镜像构建成功，在容器中运行 `python tools/accuracy.py -n pytorch/resnet18` 无 ImportError
- **Verification**: `programmatic`

### AC-6: Docker 开发镜像依赖同步
- **Given**: 更新后的 docker/dev-llvm22/Dockerfile（或环境安装脚本）
- **When**: 构建开发镜像
- **Then**: 镜像构建成功，conda/pip 环境包含所有必要依赖
- **Verification**: `programmatic`

## Open Questions
- [ ] onnx2pytorch 是否有兼容 Python 3.14 的正式版本？如无，是否需要使用 git 源码安装或寻找替代方案？
- [ ] torch CPU 版是否应在 pyproject.toml 中通过 environment marker 指定 CPU 源？还是仅在 Dockerfile 中处理？（wheel 本身无法强制 pip 使用特定 index-url）
- [ ] telnetlib3 是否需要加入可选依赖组？
