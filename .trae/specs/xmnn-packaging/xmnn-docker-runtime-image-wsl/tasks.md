# XMNN Docker 运行时镜像（WSL 构建） - The Implementation Plan

## [x] Task 1: WSL Docker 环境检查与 wheel 文件就位
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 验证 WSL2 Ubuntu 中 Docker 服务正常运行（docker info）
  - 将 wheel 文件从 `dist/` 复制到 Dockerfile.runtime 期望的构建上下文位置（`packaging/dist/`），或调整 Dockerfile 中的 COPY 路径
  - 确认构建上下文目录结构正确（environment.yml、entrypoint-runtime.sh 等文件在正确位置）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker --version` 在 WSL 中返回版本信息
  - `programmatic` TR-1.2: `docker info` 无错误，Server 版本正确
  - `programmatic` TR-1.3: wheel 文件存在于 Docker 构建上下文中可访问的位置
  - `programmatic` TR-1.4: environment.yml 和 docker/entrypoint-runtime.sh 存在于构建上下文中
- **Notes**: wheel 当前在 `dist/` 目录，Dockerfile.runtime 期望在 `packaging/dist/`

## [x] Task 2: 适配 Dockerfile.runtime 与最新 wheel
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 审查现有 Dockerfile.runtime 是否需要修改以适配新 wheel（Python 3.14、scipy 已在核心依赖、库捆绑等）
  - 检查 environment.yml 与 pyproject.toml 依赖一致性（scipy 是否已包含）
  - 确保 builder 阶段正确安装 wheel（pip install 应自动拉取所有依赖）
  - 确保 runtime 阶段安装必要的系统库（libgomp1 等 OpenMP 运行时，可能需要 libgomp1 给 scipy/numpy）
  - 检查 conda 环境创建是否能正确获取 Python 3.14
  - 修复任何路径、版本或配置不匹配问题
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: Dockerfile 构建过程无 COPY 错误（文件都能找到）
  - `programmatic` TR-2.2: conda 环境创建成功，Python 版本为 3.14.x
  - `programmatic` TR-2.3: pip install wheel 成功，自动解决所有依赖
  - `human-judgement` TR-2.4: Dockerfile 结构清晰，保持多阶段构建，无冗余层
- **Notes**: environment.yml 中已有 scipy，但 Dockerfile.runtime 中 builder 阶段通过 `conda env create -f environment.yml` + `pip install wheel` 安装，可能存在重复安装但不会出错

## [ ] Task 3: 构建 Docker 镜像
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 WSL 中执行 docker build 命令，使用 Dockerfile.runtime 构建镜像
  - 镜像标签：`xmnn-runtime:1.2.2`
  - 默认安装 infer + report extras（pandas, tqdm, tomlkit, matplotlib, openpyxl）
  - 记录构建时间和镜像大小
  - 如果构建失败，分析错误日志并修复 Dockerfile 或相关文件
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: `docker build` 退出码为 0
  - `programmatic` TR-3.2: `docker images xmnn-runtime:1.2.2` 显示镜像存在
  - `programmatic` TR-3.3: 镜像大小 < 2GB（含 infer+report extras）
  - `programmatic` TR-3.4: 构建过程中 builder 阶段的验证步骤（import tvm/vta/xmnn）通过
- **Notes**: 如果 conda 安装 Python 3.14 有问题，考虑在 conda 环境中用 pip 安装 Python 或直接使用 pip 基础镜像

## [ ] Task 4: 镜像功能验证（容器内测试）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 运行容器并验证核心导入：import tvm, import vta, import xmnn
  - 验证 TVM 核心功能：TE compute、Relay 表达式构建、NDArray 操作
  - 验证 VTA 环境：VTA_HW_PATH 正确设置，vta_hw 配置文件可访问
  - 验证 XMNN API 可用性：compile_api, infer_api 等可导入
  - 检查共享库依赖：ldd 验证 tvm/_libs 下所有 .so 无 "not found"
  - 检查环境变量：TVM_LIBRARY_PATH、LD_LIBRARY_PATH 等
  - 检查 .pth 初始化脚本是否正常执行
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-4.1: `docker run --rm xmnn-runtime:1.2.2 python -c "import tvm; print(tvm.__version__)"` 输出 0.19.0
  - `programmatic` TR-4.2: `docker run --rm xmnn-runtime:1.2.2 python -c "import vta; print('VTA OK')"` 成功
  - `programmatic` TR-4.3: `docker run --rm xmnn-runtime:1.2.2 python -c "import xmnn; print('XMNN OK')"` 成功
  - `programmatic` TR-4.4: 容器内 TE compute（placeholder + compute + create_schedule）执行成功
  - `programmatic` TR-4.5: 容器内 Relay var + nn.dense 创建成功
  - `programmatic` TR-4.6: 容器内 NDArray 创建和 numpy 互操作成功
  - `programmatic` TR-4.7: ldd 检查 tvm/_libs 下所有 .so 文件无 "not found"
  - `programmatic` TR-4.8: TVM_LIBRARY_PATH 指向 tvm/_libs 目录
- **Notes**: 使用 `docker run --rm` 而非进入交互 shell，每次测试后自动清理容器

## [ ] Task 5: 交互式 shell 和 entrypoint 验证
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 验证 `docker run -it --rm xmnn-runtime:1.2.2 bash` 可进入交互式 shell
  - 验证 entrypoint 脚本正确处理 UID/GID 映射（挂载卷权限正确）
  - 验证默认 CMD（python）可启动 Python 解释器
  - 验证工作目录 /workspace 存在且可写
  - 验证容器内非 root 用户 (ai) 权限正确
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: `docker run --rm xmnn-runtime:1.2.2 python -c "import os; print(os.getcwd())"` 输出 /workspace
  - `programmatic` TR-5.2: 容器内当前用户不是 root（uid != 0），或通过 gosu 正确降权
  - `human-judgement` TR-5.3: entrypoint 输出清晰的日志信息，UID/GID 检测正常
- **Notes**: 交互式测试需要通过子代理 browser_use 或 docker exec 方式验证

## [ ] Task 6: 可选依赖镜像变体构建与验证
- **Priority**: low
- **Depends On**: Task 4
- **Description**:
  - 构建包含 ONNX 支持的镜像变体（--build-arg INSTALL_ONNX=1）
  - 验证 onnx/onnxruntime 可导入
  - 如时间允许，构建 all-in-one 镜像（INSTALL_ALL=1）
  - 记录各变体镜像大小
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: ONNX 变体镜像构建成功
  - `programmatic` TR-6.2: ONNX 变体中 `import onnx; import onnxruntime` 成功
- **Notes**: 此任务为低优先级，如果时间不够可以只构建基础镜像
