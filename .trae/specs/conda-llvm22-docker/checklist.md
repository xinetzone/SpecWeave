# Conda + LLVM 22.1 Docker 开发环境 - Verification Checklist

## Dockerfile 结构与语法
- [ ] Dockerfile 位于正确目录 `external/chaos/xmtools/docker/dev-llvm22/Dockerfile`
- [ ] Dockerfile 语法正确，可通过 docker build 解析
- [ ] 基础镜像选择合理（Ubuntu 24.04 或官方 Conda 镜像）
- [ ] 每个构建步骤有清晰的注释说明
- [ ] 使用多阶段构建或适当的缓存清理减小镜像大小

## Conda 安装配置
- [ ] Miniconda 正确安装到 `/opt/conda`
- [ ] `/opt/conda/bin` 已添加到 PATH 环境变量
- [ ] conda-forge channel 已配置
- [ ] Conda 安装后清理了包缓存（conda clean -ya）
- [ ] `conda --version` 可正常执行
- [ ] `which conda` 输出 `/opt/conda/bin/conda`

## LLVM 22.1 安装
- [ ] LLVM 版本精确为 22.1.x（通过 `llvm-config --version` 验证）
- [ ] llvm-config 在 PATH 中可用
- [ ] clang 编译器在 PATH 中可用（`clang --version`）
- [ ] opt、llc、llvm-dis 等核心工具在 PATH 中可用
- [ ] LLVM_CONFIG 环境变量正确设置指向 llvm-config
- [ ] LLVM 库路径已添加到 LD_LIBRARY_PATH（如需要）
- [ ] 构建过程中有验证 LLVM 版本的 RUN 命令

## 基础构建工具
- [ ] build-essential（gcc/g++/make）已安装
- [ ] cmake 已安装且版本 >= 3.18
- [ ] ninja-build 已安装且版本 >= 1.10
- [ ] git、wget、python3 等基础工具已安装
- [ ] ccache 已安装（可选但推荐）

## 环境配置
- [ ] 工作目录设置为 `/workspace`
- [ ] 默认 CMD 为 bash 或其他合理的入口
- [ ] apt 缓存已清理（rm -rf /var/lib/apt/lists/*）
- [ ] 临时文件已清理（/tmp 下的安装包等）
- [ ] 环境变量设置正确（PATH、LLVM_CONFIG、LD_LIBRARY_PATH）

## 构建脚本
- [ ] build-docker.sh 脚本存在
- [ ] 脚本具有可执行权限
- [ ] 脚本正确设置镜像标签为 `xmnn-dev:llvm22`
- [ ] 脚本有使用说明输出

## 镜像验证
- [ ] Docker 镜像构建成功无错误（exit code 0）
- [ ] 镜像大小不超过 2GB
- [ ] 容器启动后 pwd 显示 `/workspace`
- [ ] 容器内可执行 `llvm-config --version` 并显示 22.1
- [ ] 容器内可执行 `clang --version`
- [ ] 容器内可执行 `cmake --version && ninja --version`
- [ ] 容器内可执行 `python3 --version`
- [ ] `echo $LLVM_CONFIG` 显示正确路径
- [ ] `echo $PATH` 包含 `/opt/conda/bin`

## 文档
- [ ] 如有必要，创建简单的 README 说明如何使用镜像（可选，用户未明确要求）
