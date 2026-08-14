---
id: "caffe-ffi-cross-dockerfile-rules"
title: "Dockerfile 交叉编译规范"
source: "Dockerfile.macos-cross + Dockerfile.win-cross"
---
# Dockerfile 交叉编译规范（caffe-ffi-cross）

<a id="基础约定"></a>
## 基础约定

- **项目类型**：纯构建镜像（无SSH/Jupyter/supervisord/entrypoint），仅用于conda包交叉编译
- **基础镜像**：`continuumio/miniconda3:latest`（非ubuntu基础镜像，不继承ubuntu规范）
- **构建文件**：两个Dockerfile分别对应macOS和Windows交叉编译
  - `Dockerfile.macos-cross`：Linux→macOS（osx-64）交叉编译
  - `Dockerfile.win-cross`：Linux→Windows（win-64）交叉编译 + Wine L3冒烟测试
- **SHELL**：`SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`（必须启用pipefail）
- **Locale**：`C.UTF-8`（构建镜像不需要中文locale，避免多余locale包）
- **无ENTRYPOINT/CMD**：纯工具镜像，运行时由用户指定命令（默认为conda-build）

<a id="构建参数"></a>
## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| APT_MIRROR | official | apt镜像源（tuna/aliyun/official） |
| CONDA_MIRROR | official | conda镜像源 |
| PYTHON_VERSION | 3.14 | Python版本 |
| SKIP_SDK_DOWNLOAD | 0 (macOS) / SKIP_WINE=0 (Windows) | 跳过SDK/Wine下载（运行时挂载） |

## macOS交叉编译（Dockerfile.macos-cross）

### 单阶段构建

直接基于miniconda3，单阶段完成（无runtime分离，因为这是纯构建工具镜像）：

1. **conda环境创建**：创建名为`cross-build`的conda环境
2. **交叉编译器安装**：通过conda-forge安装`clang_osx-64`、`clangxx_osx-64`、`cctools_osx-64`、`ld64_osx-64`
3. **macOS SDK**：下载MacOSX11.3.sdk到`/opt/MacOSX11.3.sdk`，设置`CONDA_BUILD_SYSROOT`
   - SDK下载失败时可通过`SKIP_SDK_DOWNLOAD=1`跳过，运行时挂载
4. **conda-build配置**：配置`~/.condarc`使用cross-compilation频道
5. **环境变量**：
   - `MACOSX_DEPLOYMENT_TARGET=10.15`
   - `CONDA_BUILD_SYSROOT=/opt/MacOSX11.3.sdk`
   - `CONDA_BUILD_OUTPUT_DIR=/opt/conda/conda-bld`

### 反模式

- ❌ 不要在构建镜像中安装SSH/Jupyter/supervisord（纯构建工具）
- ❌ 不要创建非root用户（构建容器以root运行，简化权限）
- ❌ 不要使用ubuntu基础镜像（miniconda3已基于Debian，conda环境是核心）

## Windows交叉编译（Dockerfile.win-cross）

### 两阶段构建

1. **Stage 1 (cross-builder)**：
   - 基于continuumio/miniconda3:latest
   - 安装`clang_win-64`（MSVC ABI交叉编译器）
   - 安装`m2w64-sysroot_win-64`（Windows头文件windows.h、CRT）
   - 配置conda-build for win-64

2. **Stage 2 (wine-runtime)**：
   - 继承cross-builder
   - 安装Wine（可选L3冒烟测试）
   - 安装Windows Miniconda到Wine环境
   - L3测试是best-effort（失败不阻断构建）
   - 通过`SKIP_WINE=1`可跳过Wine安装

<a id="输出目录"></a>
## 输出目录

- **构建输出**：`/opt/conda/conda-bld/`（conda-build默认输出目录）
- **用户输出**：`/output`（VOLUME，用户挂载获取构建产物）
- **工作空间**：`/workspace`（VOLUME，挂载caffe-ffi源码）
- WORKDIR设置为`/workspace`

## 镜像源切换

- 通过`APT_MIRROR`和`CONDA_MIRROR`构建参数控制
- 默认official，国内使用`tuna`或`aliyun`
- conda镜像配置写入`~/.condarc`

## 验证清单

- [ ] Dockerfile.macos-cross构建成功，cross-build conda环境存在
- [ ] osx-64交叉编译器可调用（`x86_64-apple-darwin13.4.0-clang --version`）
- [ ] macOS SDK存在于`/opt/MacOSX11.3.sdk`（或SKIP_SDK_DOWNLOAD=1时跳过）
- [ ] Dockerfile.win-cross构建成功，win-64交叉编译器可调用
- [ ] Wine阶段可选，SKIP_WINE=1时正常跳过
- [ ] conda-build可执行（`conda build --version`）
- [ ] 镜像内不包含SSH/Jupyter/supervisord
