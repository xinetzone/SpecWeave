# 构建 TVM/VTA 纯净运行时 Docker 镜像 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建预配置 wheel 包的运行时 Dockerfile
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 基于现有的 [Dockerfile.runtime](../../../../../external/xmhub/npu_tvm/docker/local/conda/Dockerfile.runtime) 进行扩展
  - 添加 `PYTHON_VERSION` build-arg，默认值 3.14
  - 添加 `TVM_VERSION` build-arg，默认值 0.19.0
  - 在 Conda 环境创建完成后，复制 TVM 和 VTA 的 wheel 包到镜像中
  - 使用 pip 安装 wheel 包（先安装 tvm，再安装 vta，因为 vta 依赖 tvm）
  - 将 test_wheel.py 复制到镜像中的 /opt/ 目录
  - 在构建末尾运行验证命令：检查 python 版本、tvm 导入、vta 导入
  - 清理所有缓存：conda clean -a -y, pip cache purge, rm -rf /tmp/*, rm -rf /var/lib/apt/lists/*
  - 文件位置：`docker/local/conda/Dockerfile.runtime_wheels`（新建文件，不覆盖原 Dockerfile.runtime）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: Dockerfile 语法正确，可通过 `docker build` 命令构建
  - `programmatic` TR-1.2: 构建过程中 wheel 包被正确复制和安装
  - `programmatic` TR-1.3: 构建结束时验证命令成功执行（tvm/vta 可导入）
  - `programmatic` TR-1.4: 镜像中无 apt 缓存、conda 缓存、pip 缓存残留
- **Notes**: 
  - Dockerfile 构建上下文应为 npu_tvm 根目录，以便能复制 nuitka/dist/ 下的 wheel 包
  - wheel 包路径为 docker/local/nuitka/tvm/dist/ 和 docker/local/nuitka/vta/dist/
  - 使用 `--no-cache-dir` 安装 pip 包避免缓存
  - 确保 LD_LIBRARY_PATH 包含 tvm/_libs 目录

## [x] Task 2: 创建镜像构建脚本 build_runtime_image.sh
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在 `docker/local/conda/` 目录下创建 `build_runtime_image.sh` 脚本
  - 脚本支持参数：`--python-version` 指定 Python 版本，`--tvm-version` 指定 TVM 版本，`--tag` 指定镜像标签
  - 脚本自动检测 wheel 包是否存在，不存在则提示先运行打包
  - 脚本执行 docker build 命令，传递 build-arg 参数
  - 构建完成后打印镜像信息（大小、标签、ID）
  - 构建完成后自动运行容器内验证（可选，通过 --verify 参数）
  - 提供 --help 输出使用说明
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: 脚本可执行，--help 输出完整使用说明
  - `programmatic` TR-2.2: 无参数时使用默认值（Python 3.14, TVM 0.19.0）成功构建镜像
  - `programmatic` TR-2.3: 指定 --python-version 和 --tvm-version 参数可正确传递给 docker build
  - `human-judgement` TR-2.4: 脚本日志输出清晰，关键步骤有提示信息
- **Notes**:
  - 脚本应在 WSL/Linux 环境下运行
  - 需先检查 wheel 包文件存在性
  - 镜像标签格式：tvm-runtime:${TVM_VERSION}-py${PYTHON_VERSION}

## [x] Task 3: 创建镜像导出脚本 export_runtime_image.sh
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 在 `docker/local/conda/` 目录下创建 `export_runtime_image.sh` 脚本
  - 脚本支持参数：`--tag` 指定要导出的镜像标签，`--output` 指定输出 tar 文件路径
  - 使用 `docker save` 命令将镜像保存为 tar 文件
  - 导出完成后打印文件大小和路径
  - 可选：使用 gzip 压缩以减小文件大小（--compress 参数）
  - 提供导入命令的提示说明
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 脚本可执行，成功导出 tar 文件
  - `programmatic` TR-3.2: 导出的 tar 文件可通过 `docker load -i` 正确导入
  - `programmatic` TR-3.3: --compress 参数可生成 .tar.gz 文件
- **Notes**:
  - 默认输出路径：`docker/local/dist/tvm-runtime-<version>-py<version>.tar`
  - 确保输出目录存在

## [ ] Task 4: 构建镜像并验证功能
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 使用构建脚本实际构建镜像
  - 检查镜像大小是否在预期范围内（< 1GB）
  - 启动容器验证 Python 版本正确
  - 在容器内运行 test_wheel.py，确认所有测试通过
  - 验证 TVM 基本功能：创建张量、简单计算、TE 表达式
  - 验证 VTA 基本功能：加载环境配置
  - 验证 Conda 环境自动激活
  - 验证无 PYTHONPATH 干扰（干净环境）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 镜像构建成功，退出码为 0
  - `programmatic` TR-4.2: docker images 显示镜像大小 < 1GB
  - `programmatic` TR-4.3: 容器内 python --version 输出 3.14.x
  - `programmatic` TR-4.4: 容器内 import tvm 成功，版本为 0.19.0
  - `programmatic` TR-4.5: 容器内 import vta 成功
  - `programmatic` TR-4.6: 容器内 python /opt/test_wheel.py 输出 "All tests passed"
  - `programmatic` TR-4.7: TVM 张量创建和基本计算正常工作
- **Notes**:
  - 构建前先确认 wheel 包存在且是最新的
  - 使用 `unset PYTHONPATH` 确保环境干净

## [ ] Task 5: 导出镜像为 tar 文件并验证导入
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 使用导出脚本将镜像保存为 tar 文件
  - 可选：使用 gzip 压缩
  - 在本地测试 docker load 导入（可先删除原镜像再导入）
  - 验证导入后的镜像可正常启动和使用
  - 记录 tar 文件大小
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: tar 文件成功生成
  - `programmatic` TR-5.2: docker load -i 成功导入镜像
  - `programmatic` TR-5.3: 导入的镜像可启动容器，tvm/vta 可正常导入
- **Notes**:
  - 如果磁盘空间有限，可以在验证后删除 tar 文件

## [ ] Task 6: 编写使用说明文档 RUNTIME_IMAGE_USAGE.md
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 在 `docker/local/conda/` 目录下创建 `RUNTIME_IMAGE_USAGE.md`
  - 文档包含以下章节：
    1. 镜像简介：包含内容、用途、版本信息
    2. 构建镜像：如何使用 build_runtime_image.sh 构建
    3. 导出/导入镜像：如何导出 tar 文件和在其他机器导入
    4. 启动容器：基本启动命令、挂载目录、端口映射示例
    5. 验证安装：如何运行测试脚本验证 TVM/VTA 正常工作
    6. 基本用法示例：简单的 TVM 张量操作、TE 计算示例代码
    7. 环境变量说明：LD_LIBRARY_PATH、CONDA_ENV_NAME 等
    8. 故障排查：常见问题及解决方案（如动态库找不到、导入失败等）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-6.1: 文档结构清晰，章节完整
  - `human-judgement` TR-6.2: 构建/导出/导入/启动命令可直接复制执行
  - `human-judgement` TR-6.3: 示例代码正确可运行
  - `human-judgement` TR-6.4: 故障排查部分覆盖常见问题
- **Notes**:
  - 文档使用中文编写
  - 所有命令示例基于实际测试过的命令
